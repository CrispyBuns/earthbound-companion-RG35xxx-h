// SPDX-License-Identifier: GPL-3.0-or-later
package org.earthbound.companion;

/** Digital eight-way output from one stable Android pointer, independent of its array index. */
public final class TouchStick {
 public interface Actions { void set(int action, boolean down); }
 public static final int UP=1, DOWN=2, LEFT=4, RIGHT=8;
 private static final int NONE=-1;
 private static final int[] SECTORS={RIGHT,RIGHT|DOWN,DOWN,DOWN|LEFT,LEFT,LEFT|UP,UP,UP|RIGHT};
 private final Actions actions;
 private int pointer=NONE, mask, sector=-1;
 private float x,y;
 public TouchStick(Actions actions){this.actions=actions;}
 public int pointer(){return pointer;}
 public int mask(){return mask;}
 public float x(){return x;}
 public float y(){return y;}
 public boolean begin(int id,float dx,float dy,float radius){
  if(pointer!=NONE||id<0||!valid(dx,dy,radius))return false;
  pointer=id;move(id,dx,dy,radius);return true;
 }
 public void move(int id,float dx,float dy,float radius){
  if(id!=pointer||pointer==NONE||!valid(dx,dy,radius))return;
  float length=(float)Math.hypot(dx,dy),scale=Math.max(radius,length);
  x=dx/scale;y=dy/scale;
  if(length<radius*(mask==0?0.22f:0.16f)){sector=-1;setMask(0);return;}
  double angle=Math.atan2(dy,dx),step=Math.PI/4;
  int next=((int)Math.round(angle/step)+8)%8;
  if(sector>=0){
   double distance=Math.atan2(Math.sin(angle-sector*step),Math.cos(angle-sector*step));
   if(Math.abs(distance)<step/2+Math.toRadians(3))next=sector;
  }
  sector=next;setMask(SECTORS[next]);
 }
 public void end(int id){if(id==pointer)release();}
 public void release(){pointer=NONE;x=y=0;sector=-1;setMask(0);}
 private static boolean valid(float x,float y,float radius){return Float.isFinite(x)&&Float.isFinite(y)&&Float.isFinite(radius)&&radius>0;}
 private void setMask(int next){
  int before=mask;mask=next;
  for(int i=0;i<4;i++)if((before&(1<<i))!=0&&(next&(1<<i))==0)actions.set(8+i,false);
  for(int i=0;i<4;i++)if((before&(1<<i))==0&&(next&(1<<i))!=0)actions.set(8+i,true);
 }
}
