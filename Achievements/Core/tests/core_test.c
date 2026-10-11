/* SPDX-License-Identifier: MIT */
#include "companion_achievements.h"
#include <stdio.h>
#include <string.h>
#define CHECK(x) do { if(!(x)){fprintf(stderr,"failed at line %d: %s\n",__LINE__,#x);return 1;} ++checks;} while(0)
static bool fail_commit;static unsigned notices,commits;static ca_state saved[CA_MAX_ACHIEVEMENTS];
static bool commit(void *ctx,const ca_state *states,size_t count) {
    (void)ctx;++commits;if(fail_commit)return false;memcpy(saved,states,count*sizeof(*states));return true;
}
static void notify(void *ctx,const ca_definition *d,const ca_state *s){(void)ctx;(void)d;(void)s;++notices;}
int main(void) {
    unsigned checks=0;ca_engine earthbound,other;
    const ca_definition defs[]={
        {"first","First","Win one battle","battle.won",1,CA_COUNTER},
        {"five","Five","Win five battles","battle.won",5,CA_COUNTER},
        {"town","Town","Reach a town","town.entered",1,CA_MILESTONE}};
    CHECK(ca_init(&earthbound,defs,3,commit,notify,NULL));
    CHECK(ca_event(&earthbound,"unknown",1,10));CHECK(commits==0&&notices==0);
    CHECK(ca_event(&earthbound,"battle.won",1,10));CHECK(notices==1&&saved[1].progress==1);
    fail_commit=true;CHECK(!ca_event(&earthbound,"town.entered",1,11));CHECK(notices==1&&earthbound.states[2].progress==0);
    fail_commit=false;CHECK(ca_event(&earthbound,"town.entered",1,12));CHECK(notices==2);
    CHECK(ca_event(&earthbound,"town.entered",1,13));CHECK(notices==2);
    CHECK(ca_init(&other,defs,3,commit,notify,NULL));
    CHECK(ca_restore(&other,"first",1,10));CHECK(ca_restore(&other,"five",1,0));CHECK(ca_restore(&other,"town",1,12));
    CHECK(ca_event(&other,"battle.won",UINT32_MAX,14));CHECK(other.states[1].progress==5&&ca_unlocked(&other)==3);
    CHECK(earthbound.states[1].progress==1); /* independent instances/games */
    CHECK(!ca_restore(&other,"first",1,0));CHECK(!ca_restore(&other,"five",6,0));CHECK(!ca_restore(&other,"first",0,1));
    CHECK(!ca_event(&other,"battle.won",1,0));
    ca_definition invalid[2]={defs[0],defs[0]};CHECK(!ca_init(&other,invalid,2,NULL,NULL,NULL));
    CHECK(!ca_init(&other,defs,CA_MAX_ACHIEVEMENTS+1,NULL,NULL,NULL));
    printf("Companion Achievements: %u checks passed\n",checks);return 0;
}
