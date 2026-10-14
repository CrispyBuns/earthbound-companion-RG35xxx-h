// SPDX-License-Identifier: GPL-3.0-or-later
package org.earthbound.companion;
import android.os.Bundle;
import android.content.Intent;
import android.view.Gravity;
import android.view.InputDevice;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import org.libsdl.app.SDLActivity;

public final class GameActivity extends SDLActivity {
 private static final int ACTION_SETTINGS=19;
 private static native void setTouch(int action, boolean down);
 private static native void clearTouch();
 private static native void requestQuit();
 private FrameLayout touchOverlay;
 private boolean showTouchControls=true;
 @Override protected String[] getLibraries() { return new String[]{"SDL2", "earthbound"}; }
 @Override protected String getMainSharedObject() {return getApplicationInfo().nativeLibraryDir + "/libearthbound.so";}
 @Override protected String[] getArguments() {return getIntent().getStringArrayExtra("arguments");}
 @Override protected void onCreate(Bundle saved) {
  super.onCreate(saved);
  if (mBrokenLibraries) return;
  if(android.os.Build.VERSION.SDK_INT>=33)getOnBackInvokedDispatcher().registerOnBackInvokedCallback(android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT,()->handleBack());
  FrameLayout overlay=new FrameLayout(this);
  touchOverlay=overlay;
  addContentView(overlay,new FrameLayout.LayoutParams(-1,-1));
  LinearLayout left=new LinearLayout(this);left.setOrientation(LinearLayout.VERTICAL);
  left.addView(row(new String[]{"↖","↑","↗"},new int[][]{{8,10},{8},{8,11}}));
  left.addView(row(new String[]{"←","Y","→"},new int[][]{{10},{3},{11}}));
  left.addView(row(new String[]{"↙","↓","↘"},new int[][]{{9,10},{9},{9,11}}));
  FrameLayout.LayoutParams lp=new FrameLayout.LayoutParams(-2,-2,Gravity.BOTTOM|Gravity.LEFT);lp.setMargins(12,0,0,12);overlay.addView(left,lp);
  LinearLayout right=new LinearLayout(this);right.setOrientation(LinearLayout.VERTICAL);
  right.addView(row(new String[]{"X","A"},new int[][]{{2},{0}}));right.addView(row(new String[]{"L","B"},new int[][]{{4},{1}}));right.addView(row(new String[]{"R","Settings"},new int[][]{{5},{ACTION_SETTINGS}}));
  FrameLayout.LayoutParams rp=new FrameLayout.LayoutParams(-2,-2,Gravity.BOTTOM|Gravity.RIGHT);rp.setMargins(0,0,12,12);overlay.addView(right,rp);
  LinearLayout top=row(new String[]{"Start","Select","Save","Load","Fast"},new int[][]{{6},{7},{13},{14},{12}});
  FrameLayout.LayoutParams tp=new FrameLayout.LayoutParams(-2,-2,Gravity.TOP|Gravity.CENTER_HORIZONTAL);overlay.addView(top,tp);
  applyTouchControls();
 }
 private void applyTouchControls(){
  showTouchControls=getIntent().getBooleanExtra("showTouchControls",true);
  if(touchOverlay==null)return;
  if(!showTouchControls)clearTouch();
  touchOverlay.setVisibility(showTouchControls?View.VISIBLE:View.GONE);
 }
 @Override protected void onNewIntent(Intent intent){
  super.onNewIntent(intent);
  if(intent.hasExtra("showTouchControls"))getIntent().putExtra("showTouchControls",intent.getBooleanExtra("showTouchControls",true));
  applyTouchControls();
 }
 @Override protected void onResume(){super.onResume();if(!mBrokenLibraries)applyTouchControls();}
 private void handleBack(){
  if(mBrokenLibraries){super.onBackPressed();return;}
  if(!showTouchControls&&touchOverlay!=null&&touchOverlay.getVisibility()!=View.VISIBLE){touchOverlay.setVisibility(View.VISIBLE);return;}
  requestQuit();
 }
 @Override public boolean dispatchKeyEvent(KeyEvent event){
  InputDevice device=event.getDevice();
  boolean gamepad=event.isFromSource(InputDevice.SOURCE_GAMEPAD)||event.isFromSource(InputDevice.SOURCE_JOYSTICK)||(device!=null&&(device.supportsSource(InputDevice.SOURCE_GAMEPAD)||device.supportsSource(InputDevice.SOURCE_JOYSTICK)));
  if(event.getKeyCode()==KeyEvent.KEYCODE_BACK&&!gamepad&&!mBrokenLibraries){
   if(event.getAction()==KeyEvent.ACTION_UP&&!event.isCanceled())handleBack();
   return true;
  }
  return super.dispatchKeyEvent(event);
 }
 public void openSettings(){runOnUiThread(()->{Intent intent=new Intent();intent.setClassName(this,"org.earthbound.companion.ManagedLauncher");intent.addFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);startActivity(intent);});}
 private LinearLayout row(String[] labels,int[][] actions) {
  LinearLayout row=new LinearLayout(this);
  for(int i=0;i<labels.length;i++) {
   Button b=new Button(this);b.setText(labels[i]);b.setAlpha(0.55f);b.setMinWidth(0);b.setMinimumWidth(0);
   int[] mapped=actions[i];
   b.setOnTouchListener((v,event)->{int a=event.getActionMasked();if(a==MotionEvent.ACTION_DOWN){for(int id:mapped)setTouch(id,true);return true;}if(a==MotionEvent.ACTION_UP||a==MotionEvent.ACTION_CANCEL){for(int id:mapped)setTouch(id,false);if(a==MotionEvent.ACTION_UP)v.performClick();return true;}return true;});
   int size=(int)(58*getResources().getDisplayMetrics().density);row.addView(b,new LinearLayout.LayoutParams(size,size));
  }
  return row;
 }
 @Override protected void onPause(){if(!mBrokenLibraries)clearTouch();super.onPause();}
 @Override public void onBackPressed(){handleBack();}
}
