// SPDX-License-Identifier: GPL-3.0-or-later
using global::Android.Runtime;
using System.Text.Json;

namespace EarthBoundCompanion.Android;
internal static class AndroidRomSetup {
 internal static async Task Install(string rom,bool redux,IProgress<string> progress){
  string target=redux?ReduxProfileService.DirectoryPath:Path.Combine(Settings.BaseGame,"assets.pak");
  if(redux&&Directory.Exists(target)){
   if(!ReduxProfileService.Ready||ReduxProfileService.UpdateNeeded)throw new IOException("An existing Redux profile was preserved. Import a current pack in a separate data folder to replace another version.");
   progress.Report("Redux is already set up.");return;
  }
  string parent=Path.Combine(Settings.User,"ROMSetup");Directory.CreateDirectory(parent);
  string work=Path.Combine(parent,Guid.NewGuid().ToString("N"));Directory.CreateDirectory(work);
  string output=Path.Combine(work,"result"),marker=Path.Combine(work,"progress.txt");
  MainActivity.Current?.Window?.AddFlags(global::Android.Views.WindowManagerFlags.KeepScreenOn);
  try {
   progress.Report("Starting ROM setup on this device…");
   var build=Task.Run(()=>Invoke(rom,output,redux,marker));
   string previous="";
   while(!build.IsCompleted){
    try{if(File.Exists(marker)){string detail=await File.ReadAllTextAsync(marker);if(detail!=previous){previous=detail;progress.Report(detail);}}}catch(IOException){/* Progress is advisory while its file is being replaced. */}
    await Task.WhenAny(build,Task.Delay(400));
   }
   string error=await build;
   if(error.Length!=0)throw new InvalidDataException(error+" See UserData/rom-setup.log.");
   var data=await File.ReadAllBytesAsync(Path.Combine(output,"assets.pak"));
   var policy=ProgressionGuard.CheckBase(data);string hash=StoryShuffle.Hash(data);
   if(redux){
    using var metadata=JsonDocument.Parse(await File.ReadAllTextAsync(Path.Combine(output,"profile.json")));
    if(policy.ContentId!=ReduxProfileService.ContentId||!ReduxStoryUpgrade.IsCurrent(hash)||
       metadata.RootElement.GetProperty("contentId").GetString()!=policy.ContentId||
       !hash.Equals(metadata.RootElement.GetProperty("assetPackSha256").GetString(),StringComparison.OrdinalIgnoreCase))
     throw new InvalidDataException("Generated Redux data differs from the supported version. Existing games were preserved.");
    string original=Path.Combine(Settings.BaseGame,"assets.pak"),builtOriginal=Path.Combine(output,"original-assets.pak");
    if(ProgressionGuard.CheckBase(await File.ReadAllBytesAsync(builtOriginal)).ContentId!="earthbound-usa")throw new InvalidDataException("Generated Original data differs from the supported version.");
    if(File.Exists(original)){
     if(ProgressionGuard.CheckBase(await File.ReadAllBytesAsync(original)).ContentId!="earthbound-usa")throw new InvalidDataException("Existing Original data was preserved; it is outside the supported versions.");
     File.Delete(builtOriginal);
    }else{Directory.CreateDirectory(Settings.BaseGame);File.Move(builtOriginal,original);}
    Directory.CreateDirectory(Path.GetDirectoryName(target)!);Directory.Move(output,target);
   }else{
    if(policy.ContentId!="earthbound-usa")throw new InvalidDataException("Generated data isn't the supported Original version.");
    Directory.CreateDirectory(Settings.BaseGame);
    if(File.Exists(target)){
     if(StoryShuffle.HashFile(target)!=hash)throw new IOException("An existing Original pack differs and was preserved.");
    }else File.Move(Path.Combine(output,"assets.pak"),target);
   }
  }finally{
   MainActivity.Current?.Window?.ClearFlags(global::Android.Views.WindowManagerFlags.KeepScreenOn);
   if(File.Exists(Path.ChangeExtension(marker,".log")))File.Copy(Path.ChangeExtension(marker,".log"),Path.Combine(Settings.User,"rom-setup.log"),true);
   // This GUID directory was created above; it contains only setup output.
   if(Path.GetDirectoryName(work)==parent)Directory.Delete(work,true);
  }
 }
 internal static string Invoke(string rom,string output,bool redux,string progress){
  // FindClass returns a global class reference in .NET Android.
  IntPtr clazz=JNIEnv.FindClass("org/earthbound/companion/romsetup/RomSetup");
  IntPtr method=JNIEnv.GetStaticMethodID(clazz,"run","(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;)Ljava/lang/String;");
  IntPtr a=JNIEnv.NewString(rom),b=JNIEnv.NewString(output),c=JNIEnv.NewString(progress);
  try {
   IntPtr result=JNIEnv.CallStaticObjectMethod(clazz,method,[new JValue(global::Android.App.Application.Context),new JValue(a),new JValue(b),new JValue(redux),new JValue(c)]);
   return JNIEnv.GetString(result,JniHandleOwnership.TransferLocalRef)??"Setup returned no result.";
  }finally{JNIEnv.DeleteLocalRef(a);JNIEnv.DeleteLocalRef(b);JNIEnv.DeleteLocalRef(c);JNIEnv.DeleteGlobalRef(clazz);}
 }
}
