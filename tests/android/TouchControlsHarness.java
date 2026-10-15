// SPDX-License-Identifier: GPL-3.0-or-later
package org.earthbound.companion.test;

import android.app.Activity;
import android.os.Bundle;
import android.os.SystemClock;
import android.util.Log;
import android.view.InputDevice;
import android.view.MotionEvent;
import android.view.View;
import android.widget.FrameLayout;
import org.earthbound.companion.TouchControls;
import java.util.ArrayList;

/** ROM-free emulator test host. This activity is never included in the game APK. */
public final class TouchControlsHarness extends Activity {
 private TouchControls controls;
 private final int[] held=new int[21];
 private final boolean[] seen=new boolean[21];
 private int transitions;
 private long downTime;
 private static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
 @Override public void onCreate(Bundle state){
  super.onCreate(state);
  getWindow().getDecorView().setSystemUiVisibility(5894);
  controls=new TouchControls(this,(id,down)->{held[id]+=down?1:-1;seen[id]=true;transitions++;check(held[id]>=0&&held[id]<=1,"unbalanced hold "+id);});
  setContentView(controls,new FrameLayout.LayoutParams(-1,-1));
  controls.postDelayed(()->{
   try{runChecks();Log.i("TouchChecks","PASS: real MotionEvent sliding, diagonals, pointer reindexing, simultaneous Run, action cancel, hide, accessibility, layout and all action IDs");}
   catch(Throwable error){Log.e("TouchChecks","FAIL",error);}
  },700);
 }
 private void clean(){for(int value:held)check(value==0,"held input after release");}
 private View action(int id){return controls.findViewWithTag("touch-action-"+id);}
 private float[] point(View view,float x,float y){int[] a=new int[2],b=new int[2];view.getLocationOnScreen(a);controls.getLocationOnScreen(b);return new float[]{a[0]-b[0]+x*view.getWidth(),a[1]-b[1]+y*view.getHeight()};}
 private void event(int action,int[] ids,float[]... positions){
  if(action==MotionEvent.ACTION_DOWN)downTime=SystemClock.uptimeMillis();
  MotionEvent.PointerProperties[] properties=new MotionEvent.PointerProperties[ids.length];
  MotionEvent.PointerCoords[] coordinates=new MotionEvent.PointerCoords[ids.length];
  for(int i=0;i<ids.length;i++){properties[i]=new MotionEvent.PointerProperties();properties[i].id=ids[i];properties[i].toolType=MotionEvent.TOOL_TYPE_FINGER;coordinates[i]=new MotionEvent.PointerCoords();coordinates[i].x=positions[i][0];coordinates[i].y=positions[i][1];coordinates[i].pressure=1;coordinates[i].size=1;}
  MotionEvent value=MotionEvent.obtain(downTime,SystemClock.uptimeMillis(),action,ids.length,properties,coordinates,0,0,1,1,0,0,InputDevice.SOURCE_TOUCHSCREEN,0);
  controls.dispatchTouchEvent(value);value.recycle();
 }
 private void runChecks(){
  View stick=controls.findViewWithTag("touch-stick");check(stick!=null&&stick.getWidth()>0,"stick layout");
  float[] right=point(stick,.85f,.5f),up=point(stick,.5f,.15f),diagonal=point(stick,.2f,.2f),run=point(action(3),.5f,.5f);
  event(0,new int[]{17},right);check(held[11]==1,"stick right");
  event(5|(1<<8),new int[]{17,7},right,run);check(held[3]==1&&held[11]==1,"Run with movement");
  event(2,new int[]{17,7},up,run);check(held[8]==1&&held[11]==0&&held[3]==1,"continuous slide while running");
  event(2,new int[]{17,7},diagonal,run);check(held[8]==1&&held[10]==1,"diagonal");
  event(6,new int[]{7,17},run,diagonal);check(held[3]==0&&held[8]==1,"non-owner lifted at reordered index zero");
  event(2,new int[]{17},up);check(held[8]==1&&held[10]==0,"owner survives pointer index change");
  event(1,new int[]{17},up);clean();
  float[] a=point(action(0),.5f,.5f),outside=point(action(0),-1,.5f);
  event(0,new int[]{9},a);check(held[0]==1,"A down");event(2,new int[]{9},outside);clean();
  event(2,new int[]{9},a);check(held[0]==1,"A reenter");event(3,new int[]{9},a);clean();
  for(int id:new int[]{0,1,2,3,4,5,6,7,12,13,14,19}){
   float[] p=point(action(id),.5f,.5f);event(0,new int[]{3},p);check(held[id]==1,"action down "+id);event(1,new int[]{3},p);clean();
  }
  event(0,new int[]{17},right);controls.setVisibility(View.GONE);clean();controls.setVisibility(View.VISIBLE);
  action(0).performClick();check(held[0]==1,"accessible action click");controls.releaseAll();clean();
  check(!seen[20],"settings must never send Zoom");
  ArrayList<View> buttons=new ArrayList<>();for(int id:new int[]{0,1,2,3,4,5,6,7,12,13,14,19})buttons.add(action(id));
  float density=getResources().getDisplayMetrics().density;
  for(View b:buttons){check(b.getWidth()/density>=47.9&&b.getHeight()/density>=47.9,"48dp touch target "+b.getTag());float[] p=point(b,0,0);check(p[0]>=0&&p[1]>=0&&p[0]+b.getWidth()<=controls.getWidth()+1&&p[1]+b.getHeight()<=controls.getHeight()+1,"button outside screen "+b.getTag());}
  for(int i=0;i<buttons.size();i++)for(int j=i+1;j<buttons.size();j++){
   View aView=buttons.get(i),bView=buttons.get(j);float[] ap=point(aView,0,0),bp=point(bView,0,0);
   check(!(ap[0]<bp[0]+bView.getWidth()&&ap[0]+aView.getWidth()>bp[0]&&ap[1]<bp[1]+bView.getHeight()&&ap[1]+aView.getHeight()>bp[1]),"overlapping buttons");
  }
  check(transitions>20,"events exercised");
 }
}
