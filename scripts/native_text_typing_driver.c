/* SPDX-License-Identifier: GPL-3.0-or-later
 * Isolated text fixtures; include the production interpreter to substitute a
 * tiny in-memory script and observe letters without modifying owner assets.
 * Link via check_native_text_typing.py against the matching native build.
 */
#define print_eb_string fixture_print_eb_string
#include "game/display_text.c"
#undef print_eb_string
#include "platform/pc_options.h"
#include "core/state_dump.h"
#include "game/map_loader.h"
#include <stddef.h>

void print_eb_string(const uint8_t *, int);
static uint8_t output[1024];
static unsigned count, checks;
static int tick, last_tick, spacing, minimum_gap, maximum_burst, burst;
#define CHECK(x) do { ++checks; if (!(x)) { fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x); exit(2); } } while (0)
void fixture_print_eb_string(const uint8_t *s, int length) {
    for (int i=0; i<length && s[i]; ++i) {
        CHECK(count < sizeof(output));
        output[count++] = s[i];
        if (last_tick == tick) ++burst;
        else { if (last_tick >= 0 && tick-last_tick < minimum_gap) minimum_gap=tick-last_tick; burst=1; }
        if (burst > maximum_burst) maximum_burst=burst;
        if (last_tick >= 0 && spacing) CHECK(tick-last_tick == spacing);
        last_tick=tick;
    }
    print_eb_string(s,length);
}

static void reset(uint8_t speed, bool instant) {
    close_all_windows(); window_system_init();
    CHECK(create_window(1)); set_window_focus(1); vwf_init();
    dt.instant_printing=0; dt.enable_word_wrap=1; dt.upcoming_word_length=0;
    dt.text_sound_mode=3; dt.g_cc18_attrs_saved=0;
    game_state.text_speed=speed; pc_options.instant_text=instant;
    count=0; tick=0; last_tick=-1; minimum_gap=10000; maximum_burst=burst=0; spacing=0;
    g_mode_stack.depth=0;
}

static void run(const uint8_t *script, size_t length, bool save_mid_name) {
    const uint8_t *old=dialogue_blob; size_t old_size=dialogue_blob_size;
    dialogue_blob=script; dialogue_blob_size=length;
    ModeState init; dt_setup_init(&init,script,length); mode_push(GAME_MODE_DISPLAY_TEXT,&init);
    bool saved=false;
    while (g_mode_stack.depth) {
        CHECK(tick < 1200);
        uint8_t top=g_mode_stack.depth-1;
        StepResult r=mode_dispatch_step(g_mode_stack.mode[top],&g_mode_stack.state[top]);
        if (r.kind==STEP_PUSH) mode_push(r.push_mode,r.push_init);
        else if (r.kind==STEP_POP) mode_pop(r.pop_result);
        else { ++tick; ++core.frame_counter; }
        if (save_mid_name && !saved && g_mode_stack.depth &&
            g_mode_stack.state[0].display_text.substitution_position==2) {
            ModeStack before=g_mode_stack;
            CHECK(state_dump_save_slots());
            memset(&g_mode_stack,0,sizeof(g_mode_stack));
            CHECK(state_dump_load_slots());
            CHECK(!memcmp(&before,&g_mode_stack,sizeof(before)));
            saved=true;
        }
    }
    CHECK(!save_mid_name || saved);
    dialogue_blob=old; dialogue_blob_size=old_size;
}

extern int eb_platform_main(int,char**);
int main(int argc,char **argv) {
    CHECK(argc==3);
    char *boot[]={"typing","--assets",argv[1],"--session-dir",argv[2],"--allow-redux-development",
                  "--headless","--frames","300","--redux-battle-fixture","452","--no-achievements"};
    CHECK(!eb_platform_main(sizeof(boot)/sizeof(boot[0]),boot));
    platform_max_frames=0; platform_input_shutdown(); CHECK(platform_input_init());
    game_set_fast_forward(true); entity_system_init();
    bt.battle_mode_flag=0; core.pad1_held=core.pad1_pressed=0;
    CHECK(sizeof(ModeState)==160);
    CHECK(offsetof(DisplayTextModeState,reader)==20);
    const uint8_t plain[]={0x91,0x92,0x93,0x94,2};
    for (int instant=0; instant<2; ++instant) for (int speed=1; speed<=3; ++speed) {
        reset(speed,instant); spacing=instant?0:speed+1; run(plain,sizeof(plain),false);
        CHECK(count==4); CHECK(tick==(instant?0:4*(speed+1)));
        CHECK(maximum_burst==(instant?4:1));
    }
    /* The name opcode must have the same cadence as adjacent literal text. */
    const uint8_t name[]={0x91,0x1c,2,1,0x92,2};
    unsigned name_length=0;
    while(name_length<maternalbound_name_capacity() && maternalbound_character_name(0)[name_length]) ++name_length;
    CHECK(name_length>=3);
    for (int instant=0; instant<2; ++instant) for (int speed=1; speed<=3; ++speed) {
        reset(speed,instant); spacing=instant?0:speed+1; run(name,sizeof(name),!instant && speed==1);
        CHECK(count==name_length+2);
        CHECK(!memcmp(output+1,maternalbound_character_name(0),name_length));
        CHECK(maximum_burst==(instant?(int)count:1));
    }
    /* Battle user/target, item, teleport, stat names and PSI names all type. */
    const uint8_t substitutions[][5]={{0x1c,0x0d,2},{0x1c,0x0e,2},{0x1c,1,8,2},
        {0x1c,5,1,2},{0x1c,6,1,2},{0x1c,0x12,1,2}};
    const uint8_t battle_name[]={0x91,0x92,0x93,0x94,0};
    memcpy(return_battle_attacker_address(),battle_name,sizeof(battle_name));
    memcpy(return_battle_target_address(),battle_name,sizeof(battle_name));
    dt.attacker_enemy_id=dt.target_enemy_id=-1;
    for(unsigned i=0;i<sizeof(substitutions)/sizeof(substitutions[0]);++i) {
        reset(1,false); spacing=2; run(substitutions[i],sizeof(substitutions[i]),false);
        CHECK(count>0); CHECK(maximum_burst==1);
    }
    /* Whole-name wrapping happens before the first letter, not per fragment. */
    reset(1,false); set_text_pixel_position(0,(get_window(1)->width-2)*8-2);
    const uint8_t wrap[]={0x1c,2,1,2}; run(wrap,sizeof(wrap),false);
    CHECK(get_window(1)->text_y==1); CHECK(count==name_length);
    /* Script instant-print commands still win with Companion Instant text off. */
    reset(1,false); dt.instant_printing=1; run(name,sizeof(name),false); CHECK(tick==0);
    /* Instant text must not erase a deliberate scripted pause. */
    reset(1,true); const uint8_t pause[]={0x91,0x10,9,0x92,2};
    run(pause,sizeof(pause),false); CHECK(count==2); CHECK(minimum_gap>=9);
    /* Preserve the windowless-padding fix used by Tessie and other events. */
    reset(1,false); win.current_focus_window=WINDOW_ID_NONE; run(name,sizeof(name),false);
    CHECK(count==0); CHECK(tick==0);
    /* Quick dialogue must not auto-cancel scripted timing/music waits. */
    reset(1,true); ModeState wait={0}; wait.text_delay.remaining=9;
    wait.text_delay.cancelable=1; wait.text_delay.primed=1;
    CHECK(mode_step_text_delay(&wait).kind==STEP_CONTINUE);
    CHECK(wait.text_delay.remaining==8);
    core.pad1_pressed=PAD_A; CHECK(mode_step_text_delay(&wait).kind==STEP_POP);
    core.pad1_pressed=0;
    if (maternalbound_enabled()) {
        bt.battle_mode_flag=0; pc_options.disable_cinematic_letterbox=1;
        maternalbound_letterbox_start(11);
        for(int i=0;i<14;i++){maternalbound_effects_tick();CHECK(!ppu.tm_hdma_active);}
        CHECK(ow.redux_letterbox_active && !ow.redux_letterbox_direction);
        pc_options.disable_cinematic_letterbox=0; maternalbound_effects_tick();CHECK(ppu.tm_hdma_active);
        pc_options.disable_cinematic_letterbox=1; maternalbound_effects_tick();CHECK(!ppu.tm_hdma_active);
        bt.battle_mode_flag=1; ppu.tm_hdma_active=true;
        maternalbound_effects_tick();CHECK(ppu.tm_hdma_active); /* Battle still owns its masks. */
        bt.battle_mode_flag=0; maternalbound_letterbox_start(13);
        for(int i=0;i<14;i++)maternalbound_effects_tick();
        CHECK(!ow.redux_letterbox_active && !ppu.tm_hdma_active);
        pc_options.disable_cinematic_letterbox=0;
    }
    /* Saved favourite names include the original four-byte PSI prefix.
     * Check both immediate menu printing and queued battle/dialogue names. */
    uint8_t saved_thing[sizeof(game_state.favourite_thing)];
    memcpy(saved_thing,game_state.favourite_thing,sizeof(saved_thing));
    memset(game_state.favourite_thing,0,sizeof(game_state.favourite_thing));
    const char *named="PSI Test";
    for(unsigned i=0;named[i];i++)game_state.favourite_thing[i]=ascii_to_eb_char(named[i]);
    uint8_t expected[16]={0}; const char *label=maternalbound_enabled()?"PK Test":"PSI Test";
    unsigned size=strlen(label);
    for(unsigned i=0;i<size;i++)expected[i]=ascii_to_eb_char(label[i]);
    reset(1,true); print_psi_name(1); CHECK(count==size);CHECK(!memcmp(output,expected,size));
    unsigned tested=0;
    for(unsigned i=0;i<PSI_MAX_ENTRIES;i++)if(psi_ability_data[i].name==1){
        ModeState queued={0};dt_queue_psi_name(&queued,i);
        CHECK(queued.display_text.substitution_length>=size);
        CHECK(!memcmp(queued.display_text.substitution,expected,size));tested++;
    }
    CHECK(tested>0); CHECK(!memcmp(game_state.favourite_thing,(uint8_t[]){0x80,0x83,0x79,0x50,0x84,0x95,0xa3,0xa4},8));
    memcpy(game_state.favourite_thing,saved_thing,sizeof(saved_thing));
    /* Receipt must identify the awarded item even in a hole or slot 14. */
    uint8_t saved_inventory[sizeof(party_characters[0].items)];
    memcpy(saved_inventory,party_characters[0].items,sizeof(saved_inventory));
    const uint8_t *old_blob=dialogue_blob; size_t old_blob_size=dialogue_blob_size;
    for(unsigned slot=0;slot<ITEM_INVENTORY_SIZE;slot++) {
        memset(party_characters[0].items,42,sizeof(saved_inventory));
        party_characters[0].items[slot]=0;
        uint8_t give[]={0x0e,1,1}; dialogue_blob=give; dialogue_blob_size=sizeof(give);
        ScriptReader r={TEXT_SRC_DIALOGUE,0,sizeof(give),-1};
        cc_1d_dispatch(&r);
        CHECK(get_working_memory()==1); CHECK(get_argument_memory()==slot+1);
        CHECK(party_characters[0].items[slot]==1);
        CHECK(get_character_item(1,(uint16_t)get_argument_memory())==1);
        for(unsigned other=0;other<ITEM_INVENTORY_SIZE;other++)
            CHECK(party_characters[0].items[other]==(other==slot?1:42));
    }
    dialogue_blob=old_blob;dialogue_blob_size=old_blob_size;
    memcpy(party_characters[0].items,saved_inventory,sizeof(saved_inventory));
    CHECK(map_loader_tile_in_bounds(0,0));CHECK(map_loader_tile_in_bounds(1023,1279));
    CHECK(!map_loader_tile_in_bounds(-1,0));CHECK(!map_loader_tile_in_bounds(0,-1));
    CHECK(!map_loader_tile_in_bounds(1024,10));CHECK(!map_loader_tile_in_bounds(0,1280));
    printf("TEXT_TYPING %s %u checks PASS; ModeState=%zu; literal Fast/Medium/Slow=2/3/4 frames; Instant=0\n",
           maternalbound_enabled()?"Redux":"Original",checks,sizeof(ModeState));
    return 0;
}
