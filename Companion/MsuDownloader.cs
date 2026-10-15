using System.Net.Http;
using System.Security.Cryptography;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace EarthBoundCompanion;

internal sealed record MsuEntry(
 [property:JsonPropertyName("name")] string Name,
 [property:JsonPropertyName("size")] string SizeText,
 [property:JsonPropertyName("md5")] string Md5,
 [property:JsonPropertyName("sha1")] string Sha1) {
 public long Size=>long.Parse(SizeText,System.Globalization.CultureInfo.InvariantCulture);
}

/// <summary>Only verified PCM bytes reach a final filename; each attempt has its own temporary file.</summary>
internal sealed class MsuDownloader(HttpClient http,IReadOnlyList<Uri> sources) {
 internal static readonly string[] DefaultSources=[
  "https://archive.org/download/earthbound-msu-1-pack/",
  "https://ia601501.us.archive.org/1/items/earthbound-msu-1-pack/",
  "https://ia801501.us.archive.org/1/items/earthbound-msu-1-pack/"
 ];
 internal static Uri[] LoadSources(string overrideFile){
  var urls=new List<string>();
  if(File.Exists(overrideFile)){
   try{
    using var document=JsonDocument.Parse(File.ReadAllText(overrideFile));
    urls.AddRange(document.RootElement.GetProperty("sources").EnumerateArray().Select(v=>v.GetString()??""));
    if(urls.Count is 0 or >8)throw new InvalidDataException("Use between one and eight soundtrack sources.");
   }catch(Exception e)when(e is JsonException or InvalidOperationException or KeyNotFoundException){throw new InvalidDataException("Invalid msu-sources.json. Use the documented HTTPS source list.",e);}
  }
  urls.AddRange(DefaultSources);
  return urls.Distinct(StringComparer.Ordinal).Select(value=>{
   if(!Uri.TryCreate(value,UriKind.Absolute,out var uri)||uri.Scheme!=Uri.UriSchemeHttps||uri.UserInfo!=""||uri.Query!=""||uri.Fragment!=""||!uri.AbsolutePath.EndsWith('/'))throw new InvalidDataException("Soundtrack sources must be HTTPS folder URLs ending in /, without credentials or query strings.");
   return uri;
  }).ToArray();
 }

 internal async Task DownloadAsync(MsuEntry entry,string target,Action<string,long>? progress,CancellationToken cancel){
  if(sources.Count==0)throw new InvalidDataException("No soundtrack download sources are configured.");
  int attempts=Math.Max(3,sources.Count+1);Exception? last=null;
  for(int attempt=0;attempt<attempts;attempt++){
   cancel.ThrowIfCancellationRequested();
   var uri=new Uri(sources[attempt%sources.Count],Uri.EscapeDataString(entry.Name));
   string part=target+".part-"+Guid.NewGuid().ToString("N");
   progress?.Invoke($"{uri.Host}, attempt {attempt+1}/{attempts}",0);
   try {
    using var timeout=CancellationTokenSource.CreateLinkedTokenSource(cancel);timeout.CancelAfter(TimeSpan.FromSeconds(20));
    using var request=new HttpRequestMessage(HttpMethod.Get,uri);
    request.Headers.UserAgent.ParseAdd("EarthBoundCompanion/1.0");
    using var response=await http.SendAsync(request,HttpCompletionOption.ResponseHeadersRead,timeout.Token);
    if(!response.IsSuccessStatusCode)throw new HttpRequestException($"HTTP {(int)response.StatusCode} ({uri.Host}), {entry.Name}",null,response.StatusCode);
    if(response.Content.Headers.ContentLength is long length&&length!=entry.Size)throw new InvalidDataException($"Wrong download size from {uri.Host}: {entry.Name}");
    timeout.CancelAfter(TimeSpan.FromSeconds(90));
    await using var input=await response.Content.ReadAsStreamAsync(timeout.Token);
    using var md5=IncrementalHash.CreateHash(HashAlgorithmName.MD5);
    using var sha1=IncrementalHash.CreateHash(HashAlgorithmName.SHA1);
    long fileDone=0;
    await using(var output=new FileStream(part,FileMode.CreateNew,FileAccess.Write,FileShare.None,262144,true)){
     byte[] buffer=new byte[262144];int read;
     while((read=await input.ReadAsync(buffer,timeout.Token))>0){
      if(read>entry.Size-fileDone)throw new InvalidDataException($"Oversized soundtrack download: {entry.Name}");
      await output.WriteAsync(buffer.AsMemory(0,read),timeout.Token);md5.AppendData(buffer,0,read);sha1.AppendData(buffer,0,read);fileDone+=read;
      timeout.CancelAfter(TimeSpan.FromSeconds(90));progress?.Invoke($"Downloading from {uri.Host}",fileDone);
     }
     await output.FlushAsync(timeout.Token);
    }
    if(fileDone!=entry.Size||!Convert.ToHexString(md5.GetHashAndReset()).Equals(entry.Md5,StringComparison.OrdinalIgnoreCase)||!Convert.ToHexString(sha1.GetHashAndReset()).Equals(entry.Sha1,StringComparison.OrdinalIgnoreCase))throw new InvalidDataException($"Soundtrack checksum failed ({uri.Host}): {entry.Name}");
    cancel.ThrowIfCancellationRequested();File.Move(part,target,true);return;
   } catch(Exception e)when(e is HttpRequestException or IOException or InvalidDataException or OperationCanceledException){
    cancel.ThrowIfCancellationRequested();
    last=e is OperationCanceledException?new IOException($"Soundtrack host timed out: {uri.Host}",e):e;
   } finally {if(File.Exists(part))File.Delete(part);}
   if(attempt+1<attempts)await Task.Delay(TimeSpan.FromMilliseconds(500*Math.Min(attempt+1,3)),cancel);
  }
  throw new IOException($"Soundtrack download failed after {attempts} attempts. {last?.Message}. Retry later from Music & volume.",last);
 }
}
