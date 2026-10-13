"""Compare native portrait pixels with the upstream ROM's padded sprite layout.

Uses private ROM/assets and the unchanged production library. Outputs remain
private. Covers normal/Magicant/robot variants, party counts and raising frames.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import battle_action_catalog_qa as helper
from maternalbound_graphics import asm_pointer, slice_rom

DRIVER = helper.DRIVER[:helper.DRIVER.index('static unsigned pump(void)')] + r'''
#include "game/maternalbound_battle_sprites.h"
#include "entity/sprite.h"
int main(int argc,char **argv) {
 if(eb_platform_main(argc,argv))return 2;
 load_sprite_data();
 FILE *out=fopen("portrait-pixels.bin","wb");if(!out)return 3;
 for(unsigned count=1;count<=4;count++)for(unsigned mode=0;mode<3;mode++)
 for(unsigned selected=0;selected<count;selected++) {
  game_state.player_controlled_party_count=count;
  game_state.character_mode=mode==0?CHARACTER_MODE_NORMAL:mode==1?CHARACTER_MODE_GHOST:CHARACTER_MODE_ROBOT;
  memset(&bt,0,sizeof(bt));bt.battle_mode_flag=1;
  for(unsigned i=0;i<count;i++){bt.battlers_table[i].id=i+1;bt.battlers_table[i].consciousness=1;}
  win.battle_menu_current_character_id=selected;maternalbound_battle_sprites_reset();
  for(unsigned phase=1;phase<=8;phase++) {
   maternalbound_battle_sprites_tick();
   static const unsigned positions[]={45,78,101,133,157,189,213};
   int left=positions[4-count+selected*2]+EB_VIEWPORT_PAD_LEFT+(HPPP_CENTER_TILE-16)*8-8;
   unsigned meta[]={count,mode,selected,phase,(unsigned)maternalbound_battle_sprites.anchor_y[selected],(unsigned)left};
   fwrite(meta,sizeof(unsigned),6,out);
   for(int y=120;y<176;y++) {
    uint16_t colours[EB_VIEWPORT_WIDTH]={0};uint8_t priorities[EB_VIEWPORT_WIDTH]={0};
    maternalbound_battle_sprites_line(y+EB_VIEWPORT_PAD_TOP,colours,priorities,EB_VIEWPORT_WIDTH);
    for(int x=left;x<left+16;x++){uint32_t rgb=pixel_to_rgb888(colours[x]);fwrite(&rgb,4,1,out);fwrite(&priorities[x],1,1,out);}
   }
  }
 }
 fclose(out);return 0;
}
'''


def source_sprite(rom, group):
    pointer = int.from_bytes(slice_rom(rom, asm_pointer(rom, 0x1df9)+group*4, 4), 'little')
    header = slice_rom(rom, pointer, 25)
    assert header[0] == 3 and header[1] >> 4 == 2 and header[2] == 5
    frame = int.from_bytes(header[17:19], 'little')
    data = slice_rom(rom, (header[8] << 16) | (frame & 0xfffc), 16*24//2)
    # 4bpp occupies 32 bytes per 8x8 tile: 2*3 tiles, 192 bytes.
    palette = slice_rom(rom, 0xc30000+((header[3] >> 1) & 7)*32, 32)
    result = []
    for y in range(24):
        row = []
        for x in range(16):
            sx = 15-x if frame & 1 else x
            tile = data[((y//8)*2+sx//8)*32:]
            bit, off = 7-(sx & 7), (y & 7)*2
            pixel = ((tile[off] >> bit)&1) | (((tile[off+1] >> bit)&1)<<1) | (((tile[off+16] >> bit)&1)<<2) | (((tile[off+17] >> bit)&1)<<3)
            colour = int.from_bytes(palette[pixel*2:pixel*2+2], 'little')
            r, g, b = colour & 31, (colour >> 5)&31, (colour >> 10)&31
            row.append((pixel, r, g, b))
        result.append(row)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('native-source','build','runtime','assets','rom','scratch','output'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--expect-mismatch', action='store_true')
    parser.add_argument('--reference-source', type=Path, help='Optional older portrait C file for an explicit negative control')
    args = parser.parse_args()
    args.build = args.build.resolve()
    args.native_source = args.native_source.resolve()
    args.runtime = args.runtime.resolve()
    args.scratch = args.scratch.resolve()
    args.scratch.mkdir(parents=True, exist_ok=False)
    helper.DRIVER = DRIVER
    exe, proof = helper.private_build(args)
    if args.reference_source:
        assert args.expect_mismatch, 'A reference source is only for the known-bad control'
        commands=json.loads((args.build/'compile_commands.json').read_text())
        entry=next(row for row in commands if row['file'].endswith('/src/game/maternalbound_battle_sprites.c'))
        flags=entry['command'].split();object_path=args.scratch/'reference-portrait.obj'
        flags[flags.index('-o')+1]=str(object_path);flags[flags.index('-c')+1]=str(args.reference_source.resolve())
        subprocess.run(flags,cwd=args.build,check=True,capture_output=True)
        ninja=(args.build/'build.ninja').read_text()
        match=re.search(r'^build earthbound.exe: C_EXECUTABLE_LINKER__earthbound_Release (.*?)\n(.*?)(?=\n\n)',ninja,re.M|re.S)
        objects=match[1].split(' | ',1)[0].split()
        objects=[str(args.scratch/'platform_main.c.obj') if path.replace('\\','/').endswith('/main.c.obj') else str(args.build/path) for path in objects]
        libraries=re.search(r'^  LINK_LIBRARIES = (.*)$',match[2],re.M)[1].split()
        subprocess.run([flags[0],'-O3','-DNDEBUG',str(args.scratch/'battle_action_driver.c.obj'),str(object_path),*objects,'-o',str(exe),'-Wl,--major-image-version,0,--minor-image-version,0',*libraries],cwd=args.build,check=True,capture_output=True)
        proof.update(referencePortraitSourceSha256=helper.digest(args.reference_source),executableSha256=helper.digest(exe),referenceOverridesPortraitObject=True)
    command = [str(exe),'--assets',str(args.assets.resolve()),'--session-dir',str(args.scratch),'--allow-redux-development','--no-achievements','--inspect-shuffle']
    run = subprocess.run(command,cwd=args.scratch,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'),capture_output=True,timeout=60)
    (args.scratch/'run.log').write_bytes(run.stdout+run.stderr)
    if run.returncode:
        raise RuntimeError((run.stdout+run.stderr).decode(errors='replace')[-1600:])
    rom = args.rom.read_bytes()
    source = {group: source_sprite(rom,group) for group in (1,2,3,4,5,6,343,355,457)}
    raw = (args.scratch/'portrait-pixels.bin').read_bytes()
    cursor = errors = checks = cases = 0
    samples = []
    while cursor < len(raw):
        count, mode, slot, phase, anchor, left = struct.unpack_from('<6I',raw,cursor);cursor+=24
        group = (5,343,355,457)[slot] if mode == 2 else 6 if mode == 1 and slot == 0 else slot+1
        assert anchor == 168-phase*2
        # Source type 5: two 16x16 cells at -24/-8, with the first graphics
        # row blanked by Bowspr. The image starts at anchor-16, not anchor-24.
        pixels = [[(0,0)]*16 for _ in range(56)]
        for sy, row in enumerate(source[group]):
            y = anchor-16+sy
            for x, (index,r,g,b) in enumerate(row):
                if index and 120 <= y < 176:
                    # Native RGB565 retains the source's five green bits.
                    rgb = (((r*255+15)//31)<<16) | ((((g<<1)*255+31)//63)<<8) | ((b*255+15)//31)
                    pixels[y-120][x] = (rgb,3) # upstream OBJ priority 2
        case_errors = 0
        for y in range(56):
            for x in range(16):
                rgb = struct.unpack_from('<I',raw,cursor)[0];priority=raw[cursor+4];cursor+=5
                expected_rgb, expected_priority = pixels[y][x]
                bad = priority != expected_priority or (priority and rgb != expected_rgb)
                case_errors += bool(bad);checks += 1
        if case_errors and len(samples)<4:
            samples.append(dict(count=count,mode=mode,slot=slot,phase=phase,errors=case_errors))
        errors += case_errors;cases += 1
    assert cases == 240 and cursor == len(raw)
    result = dict(cases=cases,pixelChecks=checks,pixelErrors=errors,passed=errors==0,expectedMismatch=args.expect_mismatch,negativeControlDetected=args.expect_mismatch and errors>0,examples=samples,privateBuild=proof,sourceRomSha256=hashlib.sha256(rom).hexdigest(),limits=['Source-derived pixel/priority and raising-layout comparison; not a SNES emulator campaign.','Final HP/PP-box occlusion is checked separately with the production renderer.'])
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('cases','pixelChecks','pixelErrors','passed','negativeControlDetected')}))
    if bool(errors) != args.expect_mismatch:
        raise SystemExit('Unexpected portrait comparison result')


if __name__ == '__main__':
    main()
