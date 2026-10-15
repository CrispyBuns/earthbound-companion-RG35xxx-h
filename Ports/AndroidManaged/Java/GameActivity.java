// SPDX-License-Identifier: GPL-3.0-or-later
package org.earthbound.companion;
import android.os.Bundle;
import android.content.Intent;
import android.view.InputDevice;
import android.view.KeyEvent;
import android.view.View;
import org.libsdl.app.SDLActivity;

public final class GameActivity extends SDLActivity {
 private static native void setTouch(int action, boolean down);
 private static native void clearTouch();
 private static native void requestQuit();
 private TouchControls touchOverlay;
 private boolean showTouchControls=true;
 @Override protected String[] getLibraries() { return new String[]{"SDL2", "earthbound"}; }
 @Override protected String getMainSharedObject() {return getApplicationInfo().nativeLibraryDir + "/libearthbound.so";}
 @Override protected String[] getArguments() {return getIntent().getStringArrayExtra("arguments");}
 @Override protected void onCreate(Bundle saved) {
  super.onCreate(saved);
  if (mBrokenLibraries) return;
  if(android.os.Build.VERSION.SDK_INT>=33)getOnBackInvokedDispatcher().registerOnBackInvokedCallback(android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT,()->handleBack());
  touchOverlay=new TouchControls(this,GameActivity::setTouch);
  addContentView(touchOverlay,new android.widget.FrameLayout.LayoutParams(-1,-1));
  touchOverlay.requestApplyInsets();
  applyTouchControls();
 }
 private void applyTouchControls(){
  showTouchControls=getIntent().getBooleanExtra("showTouchControls",true);
  if(touchOverlay==null)return;
  if(!showTouchControls){touchOverlay.releaseAll();clearTouch();}
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
 @Override protected void onPause(){releaseTouch();super.onPause();}
 @Override public void onWindowFocusChanged(boolean focused){super.onWindowFocusChanged(focused);if(!focused)releaseTouch();}
 private void releaseTouch(){if(!mBrokenLibraries){if(touchOverlay!=null)touchOverlay.releaseAll();clearTouch();}}
 @Override public void onBackPressed(){handleBack();}
}
