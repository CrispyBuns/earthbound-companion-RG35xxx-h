# SPDX-License-Identifier: GPL-3.0-or-later
"""Windows rendered dialogue regression fixture. Uses an isolated output directory.

Loads a COPIED checkpoint or a fresh prepared sandbox, invokes the production
window/text interpreter, and captures before/during/after frames. No owner save,
installation or achievement profile is written. This is not a natural NPC route.
"""
from pathlib import Path
from types import SimpleNamespace
import argparse, csv, hashlib, importlib.util, json, os, re, shutil, subprocess
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('motion_qa',ROOT/'scripts/motion_qa_dev33.py')
motion=importlib.util.module_from_spec(spec);spec.loader.exec_module(motion)
def build_host(label,source,build):
    out=scratch/label;out.mkdir(exist_ok=False)
    args=SimpleNamespace(out=out,source=source,build=build,enhanced=True,sdl_dll=build/'SDL2.dll')
    exe=motion.build(args)
    path=out/'host/main.c';code=path.read_text()
    code='#include "data/text_refs.h"\n'+code
    anchor='        float offset_x=0,offset_y=0;'
    hook=r'''
        if(probe_staged && frame_num==35 && !getenv("EB_DIALOGUE_NATURAL")) {
            if(getenv("EB_DIALOGUE_MENU")) {
                ModeState child={0};mode_push(GAME_MODE_PAUSE_MENU,&child);
            } else {
                create_window(WINDOW_TEXT_STANDARD);
                set_window_focus(WINDOW_TEXT_STANDARD);
                queue_interaction(0,MSG_SYS_TALK_NO_TARGET);
            }
            fprintf(stderr,"DIALOGUE queued at fraction %u,%u\n",game_state.leader_x_frac,game_state.leader_y_frac);
        }
        if(probe_staged && frame_num==185 && !getenv("EB_DIALOGUE_NATURAL")) {
            close_all_windows();
            if(getenv("EB_DIALOGUE_MENU")) {
                g_mode_stack.depth=1;g_mode_stack.state[0].overworld.phase=OWP_RENDER;enable_all_entities();
            }
        }
        if(probe_staged && frame_num>=25 && frame_num<220) {
            unsigned fixed_pixels=0;
            for(unsigned yy=0;yy<EB_VIEWPORT_HEIGHT;yy++)
                for(unsigned xx=0;xx<EB_VIEWPORT_WIDTH;xx++)fixed_pixels+=ppu_party_pixels[yy][xx]!=0;
            fprintf(stderr,"DIALOGUE frame=%d window=%d depth=%u camera=%u,%u frac=%u,%u offset=%.6f,%.6f mask=%u modes=",
                frame_num,any_window_open(),g_mode_stack.depth,ppu.bg_hofs[0],ppu.bg_vofs[0],
                game_state.leader_x_frac,game_state.leader_y_frac,platform_video_motion_offset(0),platform_video_motion_offset(1),fixed_pixels);
            for(unsigned mm=0;mm<g_mode_stack.depth;mm++)fprintf(stderr,"%u/",g_mode_stack.mode[mm]);
            fprintf(stderr,"\n");
        }
        if(probe_staged && (frame_num==33 || frame_num==65 || frame_num==195)) {
            char capture[80];snprintf(capture,sizeof(capture),"dialogue-%03d.bmp",frame_num);
            platform_video_request_screenshot(capture);
        }
'''
    assert code.count(anchor)==1
    code=code.replace(anchor,hook+anchor)
    code=code.replace('!probe_staged && host_capture_status() == HOST_CAPTURE_COMMITTED', '!probe_staged && (host_capture_status() == HOST_CAPTURE_COMMITTED || getenv("EB_DIALOGUE_FRESH"))')
    # Do not let prepared fixtures enter unrelated battles.
    code=code.replace('ow.redux_secondary_timer=143;','ow.redux_secondary_timer=143; ow.enemy_spawns_enabled=0; platform_input_shutdown(); platform_input_init();')
    path.write_text(code)
    entries=json.loads((build/'compile_commands.json').read_text())
    entry=next(row for row in entries if row['file'].endswith('/port/unix/main.c'))
    flags=entry['command'].split();obj=out/'host/main.obj'
    flags[flags.index('-o')+1]=str(obj);flags[flags.index('-c')+1]=str(path)
    subprocess.run(flags,cwd=build,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    ninja=(build/'build.ninja').read_text()
    match=re.search(r'^build earthbound.exe: C_EXECUTABLE_LINKER__earthbound_Release (.*?)\n(.*?)(?=\n\n)',ninja,re.M|re.S)
    objects=[str(obj) if item.replace('\\','/').endswith('/main.c.obj') else str(build/item) for item in match[1].split(' | ',1)[0].split()]
    libraries=re.search(r'^  LINK_LIBRARIES = (.*)$',match[2],re.M)[1].split()
    subprocess.run([flags[0],'-O3','-DNDEBUG',*objects,'-o',str(exe),*libraries],cwd=build,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    return exe

def main():
    global scratch
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--build',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--assets',type=Path,required=True)
    parser.add_argument('--checkpoint',type=Path)
    parser.add_argument('--fresh',action='store_true')
    parser.add_argument('--menu',action='store_true',help='Exercise the production pause-menu cascade')
    parser.add_argument('--filter',type=int,choices=[0,1,2],default=0)
    parser.add_argument('--aspect',type=int,choices=[0,1,2],default=0)
    a=parser.parse_args()
    if not a.fresh and not a.checkpoint:parser.error('--checkpoint is required unless --fresh is selected')
    a.out=a.out.resolve();a.build=a.build.resolve();a.source=a.source.resolve();a.assets=a.assets.resolve()
    if a.out.exists():parser.error('Choose a new output directory; existing outputs are never overwritten')
    a.out.parent.mkdir(parents=True,exist_ok=True);scratch=a.out.parent
    exe=build_host(a.out.name,a.source,a.build)
    session=a.out/'session';(session/'saves').mkdir(parents=True)
    before=hashlib.sha256(a.checkpoint.read_bytes()).hexdigest() if a.checkpoint else None
    if not a.fresh:shutil.copy2(a.checkpoint,session/'saves/quicksave_1.bin.0')
    (session/'settings.dat').write_bytes(b'EBST'+bytes([5,0,0,0,0,0,a.filter==1,0,0,0,a.aspect,0]))
    (session/'earthbound.ini').write_text(f'companion=1\nwidth=1280\nheight=720\nfullscreen=0\ninteger_scale=0\nfilter={a.filter}\nvolume=0\nno_homesickness=1\nno_dad_calls=1\n')
    (session/'input.txt').write_text('0 0\n20 100\n25 0\n100 80\n103 0\n')
    env={key:value for key,value in os.environ.items() if not key.startswith(('EB_DIALOGUE_','EB_SHOWCASE_','EB_PROBE_'))}
    env.update(EB_SHOWCASE_X='2024',EB_SHOWCASE_Y='1488',EB_SHOWCASE_FRESH='1',SDL_AUDIODRIVER='dummy')
    if a.fresh:env['EB_DIALOGUE_FRESH']='1'
    if a.menu:env['EB_DIALOGUE_MENU']='1'
    command=[str(exe),'--session-dir',str(session),'--assets',str(a.assets),'--allow-redux-development','--no-achievements','--config',str(session/'earthbound.ini'),'--windowed','--skip-intro','--frames','225','--input-script',str(session/'input.txt')]
    if not a.fresh:command.append('--load-state')
    result=subprocess.run(command,cwd=session,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=45)
    (session/'run.log').write_bytes(result.stdout)
    assert result.returncode==0,result.stdout[-1600:]
    text=result.stdout.decode(errors='replace')
    rows=[(int(f),int(win),int(cx),int(cy),int(xf),int(yf),float(ox),float(oy)) for f,win,cx,cy,xf,yf,ox,oy in re.findall(r'frame=(\d+) window=(\d).*?camera=(\d+),(\d+) frac=(\d+),(\d+) offset=([\d.]+),([\d.]+)',text)]
    assert len(rows)>100 and any(row[1] for row in rows),'Fixture did not reach a rendered textbox'
    stable=[row for row in rows if 30<=row[0]<=190]
    unchanged=len({row[2:] for row in stable})==1
    if a.checkpoint:assert hashlib.sha256(a.checkpoint.read_bytes()).hexdigest()==before
    report=dict(cameraPhaseUnchanged=unchanged,fixture='pause-menu' if a.menu else 'queued-text',filter=a.filter,aspect=a.aspect,preparedScene=True,copiedColdRestore=not a.fresh,sourceCheckpointSha256=before,productionNativeSha256=hashlib.sha256((a.build/'earthbound.exe').read_bytes()).hexdigest(),observerSha256=hashlib.sha256(exe.read_bytes()).hexdigest(),limits=['Prepared Onett window/text fixture; not every NPC/map or physical monitor scanout.'])
    (a.out/'report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    if not unchanged:raise SystemExit('Camera phase changed across the dialogue boundary')

if __name__=='__main__':main()
