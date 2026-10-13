// SPDX-License-Identifier: GPL-3.0-or-later
package org.earthbound.companion.romsetup;
import android.content.Context;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

public final class RomSetup {
    public static synchronized String run(Context context, String rom, String output,
                                           boolean redux, String progress) {
        try {
            if (!Python.isStarted()) Python.start(new AndroidPlatform(context.getApplicationContext()));
            if (rom.isEmpty()) return Python.getInstance().getModule("android_setup").callAttr("selftest").toString();
            return Python.getInstance().getModule("android_setup").callAttr(
                "build", rom, output, redux, progress).toString();
        } catch (Throwable error) {
            return "Setup failed: " + error.toString();
        }
    }
}
