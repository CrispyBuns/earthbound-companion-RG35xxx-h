// SPDX-License-Identifier: GPL-3.0-or-later
import org.earthbound.companion.TouchStick;

/** Run with javac/java; no Android SDK, ROM or assets required. */
public final class TouchStickTest {
 private static final int[] held=new int[21];
 private static int transitions;
 private static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
 private static void clean(){for(int value:held)check(value==0,"stuck native action");}
 public static void main(String[] arguments){
  TouchStick stick=new TouchStick((action,down)->{
   held[action]+=down?1:-1;transitions++;
   check(held[action]>=0&&held[action]<=1,"unbalanced native reference count");
  });
  check(stick.begin(42,80,0,100),"nonzero pointer ID");check(held[11]==1,"right");
  int before=transitions;for(int i=0;i<100;i++)stick.move(42,80,0,100);
  check(transitions==before,"repeated move must not increment native hold count");
  stick.move(42,0,-80,100);check(held[8]==1&&held[11]==0,"slide right to up without lifting");
  stick.move(42,-80,-80,100);check(held[8]==1&&held[10]==1,"diagonal");
  check(!stick.begin(7,0,80,100),"second finger cannot steal movement");
  stick.move(7,80,0,100);stick.end(7);check(held[8]==1&&held[10]==1,"ignore other pointer");
  stick.move(42,0,0,100);clean();check(stick.pointer()==42,"neutral keeps owning finger");
  stick.move(42,20,0,100);clean();
  stick.move(42,23,0,100);check(held[11]==1,"leave dead zone");
  stick.move(42,18,0,100);check(held[11]==1,"dead zone hysteresis");
  stick.move(42,15,0,100);clean();
  int[] masks={8,10,2,6,4,5,1,9};
  for(int i=0;i<8;i++){
   stick.release();stick.begin(42,(float)Math.cos(i*Math.PI/4)*300,(float)Math.sin(i*Math.PI/4)*300,100);
   check(stick.mask()==masks[i],"sector "+i);
   check(Math.hypot(stick.x(),stick.y())<=1.00001,"clamped thumb");
  }
  stick.release();clean();stick.release();clean();
  check(!stick.begin(1,Float.NaN,0,100),"reject invalid input");
  check(!stick.begin(1,0,0,0),"reject zero radius");
  stick.begin(1,80,0,100);stick.release();clean();check(stick.pointer()==-1,"cancel resets owner");
  System.out.println("PASS: continuous swipe, eight directions, multitouch ownership, dead zone, cancellation and balanced native holds");
 }
}
