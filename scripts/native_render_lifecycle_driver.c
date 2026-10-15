/* SPDX-License-Identifier: GPL-3.0-or-later
 * Prepared native regression fixtures. Link with a private platform main renamed
 * to eb_platform_main; Original fixtures relax only the private main guard.
 * Arguments: owner-supplied assets.pak, an EMPTY disposable session directory.
 * See check_native_render_lifecycle.py. No game data is embedded.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "game_main.h"
#include "core/memory.h"
#include "core/mode_stack.h"
#include "game/battle.h"
#include "game/battle_internal.h"
#include "game/battle_bg.h"
#include "game/game_state.h"
#include "game/maternalbound.h"
#include "game/overworld.h"
#include "game/position_buffer.h"
#include "game/settings.h"
#include "entity/entity.h"
#include "snes/ppu.h"
#include "platform/platform.h"
extern int eb_platform_main(int,char**);
static FILE*out;
static void discard(int y,const pixel_t*p){}
static void row(int y,const pixel_t*p){for(int x=0;x<EB_VIEWPORT_WIDTH;x++){unsigned rgb=pixel_to_rgb888(p[x]);fputc(rgb>>16,out);fputc(rgb>>8,out);fputc(rgb,out);}}
static void capture(const char*folder,const char*label){char path[4096];snprintf(path,sizeof(path),"%s/%s.ppm",folder,label);out=fopen(path,"wb");fprintf(out,"P6\n%d %d\n255\n",EB_VIEWPORT_WIDTH,EB_VIEWPORT_HEIGHT);memcpy(ppu.cgram,ert.palettes,sizeof(ppu.cgram));ppu.inidisp=15;ppu_render_frame(row);fclose(out);}

#include "core/state_dump.h"
#include "include/pad.h"
#include "game/window.h"
#include "game/oval_window.h"
#include "include/constants.h"
#include "data/assets.h"
static int checks=0;
static unsigned long long picture_hash;
static void hash_row(int y,const pixel_t*p){for(int x=0;x<EB_VIEWPORT_WIDTH;x++){picture_hash^=p[x];picture_hash*=1099511628211ULL;}}
static unsigned long long picture(void){picture_hash=1469598103934665603ULL;ppu_render_frame(hash_row);return picture_hash;}

#define CHECK(x) do{checks++;if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);return 12;}}while(0)
int main(int argc,char**argv){
 char *boot[]={"reports","--assets",argv[1],"--session-dir",argv[2],"--allow-redux-development","--headless","--frames","300","--redux-battle-fixture","452","--no-achievements"};
 if(eb_platform_main(sizeof(boot)/sizeof(boot[0]),boot))return 3;
 platform_max_frames=0;platform_input_shutdown();if(!platform_input_init())return 4;game_set_fast_forward(true);
 // Every physical target and every distortion type, isolated ownership and axis.
 for(int target=1;target<=4;target++)for(int style=1;style<=4;style++){
  LoadedBGData data={0};data.target_layer=target;data.distortion_type=style;data.distortion_ripple_amplitude=0x2000;data.distortion_ripple_frequency=0x180;data.distortion_speed=20;data.distortion_compression_rate=0x100;
  battle_bg_clear_rasters();ppu.bg_hofs[target-1]=31;ppu.bg_vofs[target-1]=7;distort_30fps=0;generate_battlebg_frame(&data,0);
  for(int i=0;i<4;i++)CHECK(battle_bg_raster_mode[i]==(i==target-1?(style<=2?1:2):0));
  int16_t saved[224];memcpy(saved,battle_bg_raster_offsets[target-1],sizeof(saved));
  LoadedBGData other=data;other.target_layer=target==4?1:target+1;generate_battlebg_frame(&other,1);CHECK(!memcmp(saved,battle_bg_raster_offsets[target-1],sizeof(saved)));
  data.distortion_type=0;generate_battlebg_frame(&data,0);CHECK(!battle_bg_raster_mode[target-1]);
 }
 // Rendered coordinate checks: raster offsets replace only the selected axis.
 psi_animation_state.time_until_next_frame=0;
 for(int target=0;target<4;target++)for(int axis=1;axis<=2;axis++){
  memset(&ppu,0,sizeof(ppu));battle_bg_clear_rasters();ppu.inidisp=15;ppu.bgmode=0;ppu.tm=1<<target;ppu.bg_sc[target]=0x60;
  for(int row=0;row<8;row++){ppu.vram[row*2]=0x55;ppu.vram[row*2+1]=(row&1)?0xff:0;}
  for(int i=0;i<256;i++)ppu.cgram[i]=(i%4)*0x145;
  ppu.bg_hofs[target]=11;ppu.bg_vofs[target]=8;
  unsigned long long expected;
  if(axis==1)ppu.bg_hofs[target]=4;else ppu.bg_vofs[target]=3;
  expected=picture();ppu.bg_hofs[target]=11;ppu.bg_vofs[target]=8;battle_bg_raster_mode[target]=axis;
  for(int i=0;i<224;i++)battle_bg_raster_offsets[target][i]=axis==1?4:3;
  CHECK(expected==picture());
 }
 // Selected real data configurations across the complete 2bpp/4bpp table.
 const unsigned char*cfg=ASSET_DATA(ASSET_DATA_BG_DATA_TABLE_BIN);unsigned count=ASSET_SIZE(ASSET_DATA_BG_DATA_TABLE_BIN)/17;
 int seen[2][4]={{0}},representatives=0;
 for(unsigned id=0;id<count;id++){
  int bits=cfg[id*17+2];if(bits!=2&&bits!=4)continue;
  load_battle_bg(id,0,0);core.frame_counter++;generate_battlebg_frame(&loaded_bg_data_layer1,0);
  int type=loaded_bg_data_layer1.distortion_type;if(type<1||type>4||seen[bits==4][type-1])continue;
  seen[bits==4][type-1]=1;representatives++;
  for(int dual=0;dual<2;dual++){
   load_battle_bg(id,dual?id:0,0);
   for(int tick=0;tick<60;tick++){core.frame_counter++;generate_battlebg_frame(&loaded_bg_data_layer1,0);generate_battlebg_frame(&loaded_bg_data_layer2,1);}
   int target=loaded_bg_data_layer1.target_layer-1;CHECK(target>=0&&target<4);CHECK(battle_bg_raster_mode[target]);
   if(bits==2){CHECK(!battle_bg_raster_mode[0]);CHECK(!battle_bg_raster_mode[1]);}
   LoadedBGData before=loaded_bg_data_layer1;CHECK(state_dump_save_slots());memset(&loaded_bg_data_layer1,0,sizeof(before));battle_bg_clear_rasters();CHECK(state_dump_load_slots());CHECK(!memcmp(&before,&loaded_bg_data_layer1,sizeof(before)));CHECK(battle_bg_raster_mode[target]);
   memcpy(ppu.cgram,ert.palettes,sizeof(ppu.cgram));ppu_render_frame(discard);ppu_clear_effects();for(int i=0;i<4;i++)CHECK(!battle_bg_raster_mode[i]);
  }
 }
 CHECK(representatives>=4);printf("REAL_BG_REPRESENTATIVES %d\n",representatives);
 // All packed effects exercise real wait continuations, both physical layouts.
 unsigned effects=maternalbound_enabled()?68:34;
 for(int bits=2;bits<=4;bits+=2)for(unsigned id=0;id<effects;id++){
  load_battle_bg(bits==2?184:1,bits==4?1:0,bits==4?4:0);show_psi_animation(id);ModeState wait={0};wait.battle_wait.kind=BW_PSI_ANIM;int ticks=0;
  while(++ticks<3000){core.frame_counter++;StepResult r=mode_step_battle_wait(&wait);if(r.kind==STEP_POP)break;CHECK(r.kind==STEP_CONTINUE);if(ticks%20==0){memcpy(ppu.cgram,ert.palettes,sizeof(ppu.cgram));
    if(bits==4){unsigned long long actual=picture();uint8_t mode=battle_bg_raster_mode[0];battle_bg_raster_mode[0]=0;CHECK(actual==picture());battle_bg_raster_mode[0]=mode;}else ppu_render_frame(discard);
   }if(bits==2)CHECK(!battle_bg_raster_mode[1]);
   if(ticks==40 && id%17==0){PsiAnimationState before=psi_animation_state;CHECK(state_dump_save_slots());memset(&psi_animation_state,0,sizeof(psi_animation_state));battle_bg_clear_rasters();CHECK(state_dump_load_slots());CHECK(psi_animation_state.frame_data==before.frame_data && psi_animation_state.time_until_next_frame==before.time_until_next_frame);}
}
  CHECK(ticks<3000);
 }
 printf("PSI_EFFECT_CASES %u\n",effects*2);
 // Nonbattle restore ownership, with intentionally stale loaded BG data.
 memset(&psi_animation_state,0,sizeof(psi_animation_state));load_battle_bg(184,183,0);
 core.frame_counter++;generate_battlebg_frame(&loaded_bg_data_layer1,0);generate_battlebg_frame(&loaded_bg_data_layer2,1);
 __typeof__(g_mode_stack) saved_stack=g_mode_stack;bt.battle_mode_flag=0;g_mode_stack.depth=1;g_mode_stack.mode[0]=GAME_MODE_OVERWORLD;
 bg2_distortion_active=true;battle_bg_rebuild_rasters();for(int i=0;i<4;i++)CHECK(!battle_bg_raster_mode[i]);CHECK(!bg2_distortion_active);
 g_mode_stack.mode[0]=GAME_MODE_GAS_STATION;g_mode_stack.state[0].gas_station.phase=GS_PH3;battle_bg_rebuild_rasters();CHECK(battle_bg_raster_mode[2]);
 g_mode_stack.mode[0]=GAME_MODE_SOUND_STONE;g_mode_stack.state[0].sound_stone.phase=SS_MAIN;battle_bg_rebuild_rasters();CHECK(battle_bg_raster_mode[2]);
 g_mode_stack.state[0].sound_stone.phase=SS_EXIT;battle_bg_rebuild_rasters();CHECK(!battle_bg_raster_mode[2]);
 g_mode_stack.mode[0]=GAME_MODE_FLYOVER;g_mode_stack.state[0].flyover.kind=FO_COFFEETEA;g_mode_stack.state[0].flyover.phase=FOP_CT_PARSE;battle_bg_rebuild_rasters();CHECK(battle_bg_raster_mode[2]);
 g_mode_stack.state[0].flyover.kind=FO_SCRIPT;battle_bg_rebuild_rasters();CHECK(!battle_bg_raster_mode[2]);
 g_mode_stack.mode[0]=GAME_MODE_GAME_OVER;bt.battle_mode_flag=1;battle_bg_rebuild_rasters();CHECK(!battle_bg_raster_mode[2]);CHECK(!bg2_distortion_active);
 g_mode_stack=saved_stack;bt.battle_mode_flag=1;
 // Held run must never pick a running pose while an escalator freezes animation.
 entity_system_init();game_state.party_status=0;game_state.character_mode=0;ow.pajama_flag=0;ow.disabled_transitions=0;maternalbound_stamina_reset();
 for(int ch=0;ch<4;ch++){
  memset(party_characters[ch].afflictions,0,sizeof(party_characters[ch].afflictions));
  core.pad1_held=0;int walk=get_party_member_sprite_id(ch,WALKING_STYLE_ESCALATOR,23,ch);int speed=entities.var[3][23];
  core.pad1_held=PAD_Y;int ride=get_party_member_sprite_id(ch,WALKING_STYLE_ESCALATOR,23,ch);CHECK(walk==ride);CHECK(speed==entities.var[3][23]);
  int stairs=get_party_member_sprite_id(ch,WALKING_STYLE_STAIRS,23,ch);int normal=get_party_member_sprite_id(ch,WALKING_STYLE_NORMAL,23,ch);CHECK(stairs==normal);if(maternalbound_enabled())CHECK(normal!=ride);
 }
 // Normal cinematic close and scripted battle interruption must retain behavior.
 if(maternalbound_enabled()){
  g_mode_stack.depth=0;bt.battle_mode_flag=0;maternalbound_letterbox_start(12);maternalbound_effects_tick();CHECK(ppu.tm_hdma_active);CHECK(ow.redux_letterbox_active);
  bt.battle_mode_flag=1;unsigned top=ow.redux_letterbox_top;maternalbound_effects_tick();CHECK(ow.redux_letterbox_top==top);CHECK(ow.redux_letterbox_active);
  bt.battle_mode_flag=0;maternalbound_letterbox_start(13);for(int i=0;i<20;i++)maternalbound_effects_tick();CHECK(!ow.redux_letterbox_active);CHECK(!ppu.tm_hdma_active);
 }
 // Death abandons the cinematic producer, for Continue and No Continue choices.
 for(int choice=0;choice<2;choice++){
  ow.redux_letterbox_active=1;ow.redux_letterbox_direction=1;ow.redux_letterbox_top=39;ppu.tm_hdma_active=true;bt.battle_mode_flag=0;
  ModeState over={0};mode_step_game_over(&over);CHECK(!ow.redux_letterbox_active&&!ow.redux_letterbox_direction&&!ow.redux_letterbox_top&&!ppu.tm_hdma_active);maternalbound_effects_tick();CHECK(!ppu.tm_hdma_active);
  if(choice)event_flag_set(475);else event_flag_clear(475);
  over.game_over.phase=GO_CB_DECIDE;StepResult decision=mode_step_game_over(&over);CHECK(decision.kind==STEP_PUSH);CHECK(over.game_over.phase==(choice?GO_NC_SEQ_CHECK:GO_CONT_FADE));CHECK(!ppu.tm_hdma_active);
 }
 printf("CHECKS %d PASS\n",checks);return 0;
}
