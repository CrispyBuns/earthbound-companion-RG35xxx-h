using System.Net.Http;
namespace EarthBoundCompanion;

internal sealed record SetupResult(int MsuTracks,long MsuBytes,bool CreatedStarterSeed,string? SoundtrackWarning=null);

internal static class SetupWorkflow {
 internal static async Task<SetupResult> RunAsync(Func<Task<SetupResult>> buildGame,Func<Task<(int Tracks,long Bytes)>>? installMusic,CancellationToken cancel){
  var result=await buildGame();
  cancel.ThrowIfCancellationRequested();
  if(installMusic==null)return result;
  try {
   var (tracks,bytes)=await installMusic();
   return result with {MsuTracks=tracks,MsuBytes=bytes};
  }catch(Exception e)when(e is IOException or HttpRequestException or InvalidDataException or UnauthorizedAccessException){
   cancel.ThrowIfCancellationRequested();
   return result with {SoundtrackWarning="Game ready; soundtrack incomplete. Original music still works.\nRetry from Music & volume. Details: UserData/msu-setup.log."};
  }
 }
}
