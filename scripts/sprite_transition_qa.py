# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused native renderer regressions in a private prepared Onett session.

Sparse OAM checks use synthetic tiles. Door/teleport checks drive production
mode handlers after staging a fresh scene; they do not alter an owner save.
"""
import argparse, hashlib, importlib.util, json, os, re, shutil, subprocess
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('motion', ROOT / 'scripts/motion_qa_dev33.py')
motion = importlib.util.module_from_spec(spec)
spec.loader.exec_module(motion)

HELPERS = r'''
#include "include/pad.h"
static void qa_ignore_line(int y, const pixel_t *pixels) {(void)y;(void)pixels;}
static pixel_t qa_outline_colors[8][12];
static void qa_outline_line(int y,const pixel_t *pixels) {
    if(y>=40 && y<48)memcpy(qa_outline_colors[y-40],pixels+40,sizeof(qa_outline_colors[0]));
}
static void qa_sparse_oam(void) {
    PPUState *saved=malloc(sizeof(ppu)); if(!saved)exit(2); *saved=ppu;
    unsigned errors=0,checks=0;
    for(unsigned front=0;front<2;front++) for(unsigned same=0;same<2;same++) {
        memset(&ppu,0,sizeof(ppu));ppu.inidisp=15;ppu.bgmode=1;ppu.tm=17;
        ppu.bg_viewport_fill[0]=BG_VIEWPORT_FILL;
        for(unsigned at=0;at<128;at++)ppu.oam_full_y[at]=EB_VIEWPORT_HEIGHT;
        for(unsigned row=0;row<8;row++) {
            ppu.vram[32+row*2]=255; // tile 1: index 1
            ppu.vram[64+row*2+(same?0:1)]=255; // tile 2: index 1 or 2
        }
        ppu.cgram[129]=0x001f;ppu.cgram[130]=0x7c00;
        unsigned party=front?3:47,npc=front?47:3;
        ppu.oam[party].tile=1;ppu.oam[party].attr=0x30;
        ppu.oam_full_x[party]=40;ppu.oam_full_y[party]=40;
        ppu.oam[npc].tile=2;ppu.oam[npc].attr=0x30;
        ppu.oam_full_x[npc]=44;ppu.oam_full_y[npc]=40;
        memset(ppu_party_oam,0,sizeof(ppu_party_oam));ppu_party_oam[party]=true;
        ppu_track_party_pixels=true;ppu_track_window_pixels=false;
        ppu_render_frame(qa_ignore_line);
        for(unsigned y=40;y<48;y++)for(unsigned x=40;x<52;x++) {
            unsigned expected=x<44 || (front && x<48) ? 1 :
                (!front && x<48 ? 3 : 0);
            errors+=(ppu_party_pixels[y][x]!=expected);checks++;
        }
    }
    ppu=*saved;free(saved);ppu_track_party_pixels=ppu_track_window_pixels=false;
    fprintf(stderr,"SPARSE_OAM checks=%u errors=%u\n",checks,errors);
}
static void qa_black_outline(void) {
    PPUState *saved=malloc(sizeof(ppu));if(!saved)exit(2);*saved=ppu;
    unsigned errors=0,checks=0,color_errors=0,color_checks=0;
    for(unsigned front=0;front<2;front++)for(unsigned b=0;b<3;b++) {
        memset(&ppu,0,sizeof(ppu));ppu.inidisp=b==0?15:b==1?7:1;
        ppu.bgmode=1;ppu.tm=17;ppu.bg_viewport_fill[0]=BG_VIEWPORT_FILL;
        for(unsigned at=0;at<128;at++)ppu.oam_full_y[at]=EB_VIEWPORT_HEIGHT;
        for(unsigned row=0;row<8;row++) {
            /* Index 1 is opaque black, with colored index 2 interiors.
             * Both sprites share the black outline palette entry. */
            unsigned edge=row==0||row==7?255:129;
            ppu.vram[32+row*2]=edge;ppu.vram[32+row*2+1]=255^edge;
            ppu.vram[64+row*2]=edge;ppu.vram[64+row*2+1]=255^edge;
        }
        ppu.cgram[129]=ppu.cgram[145]=0;ppu.cgram[130]=0x001f;ppu.cgram[146]=0x7c00;
        unsigned party=front?3:47,npc=front?47:3;
        ppu.oam[party].tile=1;ppu.oam[party].attr=0x30;
        ppu.oam_full_x[party]=40;ppu.oam_full_y[party]=40;
        ppu.oam[npc].tile=2;ppu.oam[npc].attr=0x32;
        ppu.oam_full_x[npc]=44;ppu.oam_full_y[npc]=40;
        memset(ppu_party_oam,0,sizeof(ppu_party_oam));ppu_party_oam[party]=true;
        ppu_track_party_pixels=true;ppu_track_window_pixels=false;
        ppu_render_frame(qa_outline_line);
        for(unsigned y=40;y<48;y++)for(unsigned x=40;x<48;x++) {
            /* Coverage is independent of RGB equality and sprite order:
             * the winning NPC pixels must also cover the party cutout. */
            errors+=ppu_party_pixels[y][x]!=(front||x<44?1:3);checks++;
        }
        for(unsigned x=0;x<12;x++) {
            color_errors+=qa_outline_colors[0][x]!=0;
            color_errors+=qa_outline_colors[7][x]!=0;color_checks+=2;
        }
        if(b==0) {
            color_errors+=qa_outline_colors[2][6]!=(front?PIXEL_RGB(255,0,0):PIXEL_RGB(0,0,255));
            color_checks++;
        }
    }
    ppu=*saved;free(saved);ppu_track_party_pixels=ppu_track_window_pixels=false;
    fprintf(stderr,"BLACK_OUTLINE checks=%u errors=%u\n",checks,errors);
    fprintf(stderr,"OUTLINE_COLORS checks=%u errors=%u\n",color_checks,color_errors);
}
static void qa_start_door(void) {
    for(unsigned y=0;y<1280;y++)for(unsigned x=0;x<1024;x++) {
        if(find_door_at_position(x,y)!=2)continue;
        const uint8_t *door=get_door_data_entry(dr.door_found&0x7fff);
        if(!door || read_u32_le(door) || read_u16_le(door+4))continue;
        ModeState child={0};child.door_transition.phase=DTR_BEGIN;
        child.door_transition.door_ptr=0xcf0000u|(dr.door_found&0x7fff);
        mode_push(GAME_MODE_DOOR_TRANSITION,&child);
        fprintf(stderr,"QA_DOOR start tile=%u,%u ptr=%06x transition=%u\n",x,y,(unsigned)child.door_transition.door_ptr,door[10]);return;
    }
    fprintf(stderr,"QA_DOOR no ordinary door found\n");exit(2);
}
static void qa_party_overlap(int frame) {
    if(!getenv("EB_QA_PARTY"))return;
    unsigned drawn=0;
    for(unsigned member=0;member<game_state.party_count;member++) {
        unsigned ent=read_u16_le(&game_state.party_entity_slots[member*2]);
        int min_x=32767,min_y=32767;
        for(unsigned at=0;at<128;at++)if(presentation_oam_entity[at]==(int)ent) {
            if(ppu.oam_full_x[at]<min_x)min_x=ppu.oam_full_x[at];
            if(ppu.oam_full_y[at]<min_y)min_y=ppu.oam_full_y[at];
        }
        if(min_x==32767)continue;drawn++;
        int target_x=EB_VIEWPORT_CENTER_X-8+(member>=2?30+(member-2)*20:0);
        int target_y=EB_VIEWPORT_CENTER_Y-28+(member==1?4:0);
        for(unsigned at=0;at<128;at++)if(presentation_oam_entity[at]==(int)ent) {
            ppu.oam_full_x[at]+=target_x-min_x;ppu.oam_full_y[at]+=target_y-min_y;
            /* Reclassify Ness as a foreground non-party actor only for this
             * private pixel fixture; actual sprite art and OAM order stay. */
            if(getenv("EB_QA_NPC") && member==0)presentation_oam_entity[at]=-1;
        }
    }
    if(frame==55) {
        fprintf(stderr,"PARTY_OVERLAP members=%u rendered=%u\n",game_state.party_count,drawn);
        if(drawn!=4)exit(2);
    }
}
'''

HOOK = r'''
        if(probe_staged && frame_num==30) {
            qa_sparse_oam();
            qa_black_outline();
            game_state.leader_x_frac=32768;game_state.leader_y_frac=49152;
            if(getenv("EB_QA_ZOOM"))ow.zoom_mode=EB_ZOOM_IN;
        }
        if(probe_staged && frame_num==60) {
            if(!strcmp(getenv("EB_QA_KIND"),"door"))qa_start_door();
            if(!strcmp(getenv("EB_QA_KIND"),"teleport")) {
                ModeState child={0};child.teleport_to.dest_id=1;
                mode_push(GAME_MODE_TELEPORT_TO,&child);
            }
            if(!strcmp(getenv("EB_QA_KIND"),"fade"))fade_out(1,1);
            if(!strcmp(getenv("EB_QA_KIND"),"event-fade")) {
                ModeState child={0};child.mosaic_fade.kind=MF_OUT;
                child.mosaic_fade.step=1;child.mosaic_fade.delay=2;
                mode_push(GAME_MODE_MOSAIC_FADE,&child);
            }
            if(!strcmp(getenv("EB_QA_KIND"),"event-window-fade")) {
                fade_out(1,1);ModeState child={0};
                child.fade_wait.tick_kind=FADE_TICK_WINDOW;
                mode_push(GAME_MODE_FADE_WAIT,&child);
            }
            if(!strcmp(getenv("EB_QA_KIND"),"coffee-fade")) {
                ModeState child={0};child.special_event.event_id=1;
                mode_push(GAME_MODE_SPECIAL_EVENT,&child);
            }
            if(!strcmp(getenv("EB_QA_KIND"),"achievements")) {
                ModeState child={0};child.settings_menu.phase=SET_RESULT;
                child.settings_menu.result_ready=1;child.settings_menu.result=14;
                mode_push(GAME_MODE_SETTINGS_MENU,&child);
            }
        }
        if(probe_staged && !strcmp(getenv("EB_QA_KIND"),"achievements")) {
            if(frame_num==90)eb_achievements_browser_input(PAD_RIGHT);
            if(frame_num==120)eb_achievements_browser_input(PAD_CANCEL);
            if(frame_num==70 && !eb_achievements_browser_active())exit(2);
            if(frame_num==150 && eb_achievements_browser_active())exit(2);
        }
        if(probe_staged && frame_num==90 && !strcmp(getenv("EB_QA_KIND"),"fade"))fade_in(1,1);
        if(probe_staged && frame_num==110 && !strcmp(getenv("EB_QA_KIND"),"event-fade")) {
            ppu.inidisp=0;ModeState child={0};child.mosaic_fade.kind=MF_IN;
            child.mosaic_fade.step=1;child.mosaic_fade.delay=2;
            mode_push(GAME_MODE_MOSAIC_FADE,&child);
        }
        if(probe_staged && frame_num==100 && !strcmp(getenv("EB_QA_KIND"),"event-window-fade"))fade_in(1,1);
        if(probe_staged && frame_num>=35 && frame_num<155) {
            fprintf(stderr,"RENDER_QA frame=%d bright=%u camera=%u,%u leader=%u,%u frac=%u,%u off=%.6f,%.6f age=%u modes=",
                frame_num,ppu.inidisp,ppu.bg_hofs[0],ppu.bg_vofs[0],game_state.leader_x_coord,game_state.leader_y_coord,
                game_state.leader_x_frac,game_state.leader_y_frac,platform_video_motion_offset(0),platform_video_motion_offset(1),
                (unsigned)(core.frame_counter-presentation_oam_frame));
            for(unsigned at=0;at<g_mode_stack.depth;at++)fprintf(stderr,"%u/",g_mode_stack.mode[at]);fprintf(stderr,"\n");
        }
        if(probe_staged && (frame_num==55 || frame_num==62 || frame_num==70 || frame_num==95 || frame_num==110 || frame_num==150)) {
            char capture[60];snprintf(capture,sizeof(capture),"render-%03d.bmp",frame_num);platform_video_request_screenshot(capture);
        }
'''

def build_host(a):
    exe = motion.build(SimpleNamespace(out=a.out, source=a.source, build=a.build, enhanced=True, sdl_dll=a.build/'SDL2.dll'))
    main = a.out/'host/main.c'
    code = main.read_text()
    code = '#include "game/door.h"\n#include "core/memory.h"\n' + code
    code = code.replace('int main(int argc', HELPERS + '\nint main(int argc', 1)
    assert code.count('        float offset_x=0,offset_y=0;') == 1
    code = code.replace('        float offset_x=0,offset_y=0;', HOOK + '\n        float offset_x=0,offset_y=0;')
    code = code.replace('!probe_staged && host_capture_status() == HOST_CAPTURE_COMMITTED', '!probe_staged && (host_capture_status()==HOST_CAPTURE_COMMITTED || getenv("EB_SHOWCASE_FRESH"))')
    code = code.replace('ow.redux_secondary_timer=143;', 'ow.redux_secondary_timer=143;ow.enemy_spawns_enabled=0;')
    code = code.replace('            initialize_overworld_state();', '''
            if(getenv("EB_QA_PARTY")) {
                memset(game_state.party_members,0,sizeof(game_state.party_members));
                for(unsigned member=0;member<4;member++)game_state.party_members[member]=member+1;
                game_state.character_mode=CHARACTER_MODE_NORMAL;
            }
            ppu.window_hdma_active=ppu.window2_hdma_active=ppu.tm_hdma_active=false;
            initialize_overworld_state();''')
    code = code.replace('        game_loop_step();\n        host_process_frame();', '        game_loop_step();\n        if(probe_staged)qa_party_overlap(frame_num);\n        host_process_frame();')
    main.write_text(code)
    commands = json.loads((a.build/'compile_commands.json').read_text())
    flags = next(row['command'].split() for row in commands if row['file'].endswith('/port/unix/main.c'))
    obj = a.out/'host/main.obj'
    flags[flags.index('-o')+1] = str(obj)
    flags[flags.index('-c')+1] = str(main)
    result=subprocess.run(flags, cwd=a.build, capture_output=True)
    if result.returncode:raise RuntimeError(result.stderr.decode(errors='replace'))
    ninja = (a.build/'build.ninja').read_text()
    match = re.search(r'^build earthbound.exe: C_EXECUTABLE_LINKER__earthbound_Release (.*?)\n(.*?)(?=\n\n)', ninja, re.M|re.S)
    replacements={'/main.c.obj':obj}
    if a.reference_renderer:
        for suffix,filename in [('ppu_render.c','dev36-ppu.c'),('sdl2_video.c','dev36-video.c')]:
            original_path=a.reference_renderer/filename
            entry=next(row for row in commands if row['file'].endswith('/'+suffix))
            reference_flags=entry['command'].split();reference_obj=a.out/'host'/('reference-'+suffix+'.obj')
            reference_flags[reference_flags.index('-o')+1]=str(reference_obj)
            reference_flags[reference_flags.index('-c')+1]=str(original_path.resolve())
            reference_flags+=['-I'+str(Path(entry['file']).parent)]
            subprocess.run(reference_flags,cwd=a.build,check=True,capture_output=True)
            replacements['/'+suffix+'.obj']=reference_obj
    if a.baseline_mask:
        original=subprocess.check_output(['git','-C',str(a.source),'show','HEAD:src/snes/ppu_render.c'])
        original_path=a.out/'host/ppu_render_baseline.c';original_path.write_bytes(original)
        entry=next(row for row in commands if row['file'].endswith('/src/snes/ppu_render.c'))
        ppu_flags=entry['command'].split();ppu_obj=a.out/'host/ppu_render_baseline.obj'
        ppu_flags[ppu_flags.index('-o')+1]=str(ppu_obj);ppu_flags[ppu_flags.index('-c')+1]=str(original_path)
        subprocess.run(ppu_flags,cwd=a.build,check=True,capture_output=True)
        replacements['/ppu_render.c.obj']=ppu_obj
    objects=[]
    for item in match[1].split(' | ',1)[0].split():
        replacement=next((v for k,v in replacements.items() if item.replace('\\','/').endswith(k)),None)
        objects.append(str(replacement or a.build/item))
    if a.baseline_mask:objects.insert(0,str(ppu_obj)) # override the renderer in the static game library
    if a.reference_renderer:objects.insert(0,str(replacements['/ppu_render.c.obj']))
    libs = re.search(r'^  LINK_LIBRARIES = (.*)$', match[2], re.M)[1].split()
    subprocess.run([flags[0], '-O3', '-DNDEBUG', *objects, '-o', str(exe), *libs], cwd=a.build, check=True, capture_output=True)
    return exe

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('source','build','assets','out'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--kind',choices=['door','teleport','fade','event-fade','event-window-fade','coffee-fade','mask','achievements'],default='door')
    p.add_argument('--filter',type=int,choices=[0,1,2],default=0)
    p.add_argument('--baseline',action='store_true')
    p.add_argument('--baseline-mask',action='store_true',help='Use the committed pre-fix PPU object to demonstrate the regression')
    p.add_argument('--reference-renderer',type=Path,help='Use private dev36-ppu.c/dev36-video.c snapshots for a before/after comparison')
    p.add_argument('--checkpoint',type=Path,help='Cold-load a copied full-party save before staging the test scene')
    p.add_argument('--party-overlap',action='store_true',help='Arrange all four real party sprites in an overlap fixture after copied restore')
    p.add_argument('--npc-overlap',action='store_true',help='Classify the foreground real sprite as non-party in the private overlap fixture')
    p.add_argument('--achievement-profile',type=Path,help='Copy an existing progress profile into the private browser fixture')
    p.add_argument('--zoom-in',action='store_true',help='Render the tightest 179-row crop')
    a=p.parse_args()
    assert not (a.reference_renderer and a.baseline_mask)
    for name in ('source','build','assets','out'):setattr(a,name,getattr(a,name).resolve())
    a.out.mkdir(parents=True,exist_ok=False)
    exe=build_host(a)
    session=a.out/'session';session.mkdir()
    checkpoint_hash=None
    if a.checkpoint:
        a.checkpoint=a.checkpoint.resolve();checkpoint_hash=hashlib.sha256(a.checkpoint.read_bytes()).hexdigest()
        (session/'saves').mkdir();shutil.copy2(a.checkpoint,session/'saves/quicksave_1.bin.0')
    (session/'settings.dat').write_bytes(b'EBST'+bytes([5,0,0,0,0,0,a.filter==1,0,0,0,0,0]))
    (session/'earthbound.ini').write_text(f'companion=1\nwidth=1280\nheight=720\nfullscreen=0\nfilter={a.filter}\nvolume=0\nno_homesickness=1\nno_dad_calls=1\n')
    (session/'input.txt').write_text('0 0\n')
    env={k:v for k,v in os.environ.items() if not k.startswith(('EB_SHOWCASE_','EB_PROBE_','EB_QA_'))}
    env.update(EB_SHOWCASE_X='2024',EB_SHOWCASE_Y='1488',EB_SHOWCASE_FRESH='1',EB_QA_KIND=a.kind,SDL_AUDIODRIVER='dummy')
    if a.checkpoint:env.pop('EB_SHOWCASE_FRESH')
    if a.party_overlap:env['EB_QA_PARTY']='1'
    if a.npc_overlap:
        assert a.party_overlap and a.checkpoint
        env['EB_QA_NPC']='1'
    if a.zoom_in:env['EB_QA_ZOOM']='1'
    cmd=[str(exe),'--session-dir',str(session),'--assets',str(a.assets),'--allow-redux-development','--no-achievements','--config',str(session/'earthbound.ini'),'--windowed','--skip-intro','--frames','170','--input-script',str(session/'input.txt')]
    if a.kind=='achievements':
        cmd.remove('--no-achievements');cmd.extend(['--achievements-dir',str(session/'progress')])
        if a.achievement_profile:
            (session/'progress').mkdir();shutil.copy2(a.achievement_profile,session/'progress'/a.achievement_profile.name)
    if a.checkpoint:cmd.append('--load-state')
    result=subprocess.run(cmd,cwd=session,env=env,capture_output=True,timeout=45)
    log=result.stdout+result.stderr;(session/'run.log').write_bytes(log)
    assert result.returncode==0,log[-2400:].decode(errors='replace')
    text=log.decode(errors='replace')
    match=re.search(r'SPARSE_OAM checks=(\d+) errors=(\d+)',text);assert match,text[-2400:]
    outline=re.search(r'BLACK_OUTLINE checks=(\d+) errors=(\d+)',text);assert outline,text[-2400:]
    colors=re.search(r'OUTLINE_COLORS checks=(\d+) errors=(\d+)',text);assert colors,text[-2400:]
    rows=re.findall(r'RENDER_QA frame=(\d+) bright=(\d+) camera=(\d+),(\d+) leader=(\d+),(\d+) frac=(\d+),(\d+) off=([\d.]+),([\d.]+).*?modes=([^\r\n]+)',text)
    phase_checks=phase_errors=0
    for f,b,cx,cy,lx,ly,xf,yf,ox,oy,modes in rows:
        if int(b)&128 or not int(b)&15:continue
        if int(cx)!=(int(lx)-256)&65535 or int(cy)!=(int(ly)-128)&65535:continue
        phase_checks+=1
        phase_errors+=abs(float(ox)-int(xf)/65536)>0.00001 or abs(float(oy)-int(yf)/65536)>0.00001
    if a.checkpoint:assert hashlib.sha256(a.checkpoint.read_bytes()).hexdigest()==checkpoint_hash
    report={'kind':a.kind,'filter':a.filter,'copiedCheckpointSha256':checkpoint_hash,'baselineMask':a.baseline_mask,'maskChecks':int(match[1]),'maskErrors':int(match[2]),'outlineChecks':int(outline[1]),'outlineErrors':int(outline[2]),'phaseChecks':phase_checks,'phaseErrors':phase_errors,'modeStacks':sorted(set(row[-1] for row in rows)),'nativeSha256':hashlib.sha256((a.build/'earthbound.exe').read_bytes()).hexdigest(),'limits':['Synthetic sparse/overlapping sprites and prepared Onett transition drivers; not a natural campaign or every map.']}
    report['referenceRenderer']=bool(a.reference_renderer)
    report['outlineColorChecks']=int(colors[1]);report['outlineColorErrors']=int(colors[2])
    dedicated=[row for row in rows if a.kind=='coffee-fade' and int(row[0])>=100]
    report['dedicatedSceneChecks']=len(dedicated)
    report['dedicatedSceneErrors']=sum(float(row[8])!=0 or float(row[9])!=0 for row in dedicated)
    report['qaHostSha256']=hashlib.sha256(exe.read_bytes()).hexdigest()
    if a.reference_renderer:report['referenceSourceSha256']={p:hashlib.sha256((a.reference_renderer/p).read_bytes()).hexdigest() for p in ('dev36-ppu.c','dev36-video.c')}
    (a.out/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
    if not a.baseline:assert report['maskErrors']==0 and report['outlineErrors']==0 and report['phaseErrors']==0 and report['outlineColorErrors']==0 and report['dedicatedSceneErrors']==0

if __name__=='__main__':main()
