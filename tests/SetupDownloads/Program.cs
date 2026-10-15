using System.Net;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using EarthBoundCompanion;

string root=Path.GetFullPath(args.Single());
if(Directory.Exists(root))throw new IOException("Choose a fresh test directory.");
Directory.CreateDirectory(root);
byte[] expected=Encoding.ASCII.GetBytes("MSU1synthetic-track");
var entry=new MsuEntry("eb_msu1-1.pcm",expected.Length.ToString(),Convert.ToHexString(MD5.HashData(expected)),Convert.ToHexString(SHA1.HashData(expected)));
Uri[] sources=[new("https://primary.invalid/pcm/"),new("https://mirror.invalid/pcm/")];
void Check(bool value,string message){if(!value)throw new Exception(message);}
HttpResponseMessage Good(byte[]? bytes=null)=>new(HttpStatusCode.OK){Content=new ByteArrayContent(bytes??expected)};
string Target(string name){string dir=Path.Combine(root,name);Directory.CreateDirectory(dir);return Path.Combine(dir,entry.Name);}

// A real HTTP 500 must advance to the next source, retaining the identical pinned track.
var fallback=new FakeHandler((request,index,token)=>index==0?new(HttpStatusCode.InternalServerError):Good());
string target=Target("fallback");
await new MsuDownloader(new HttpClient(fallback),sources).DownloadAsync(entry,target,null,default);
Check(File.ReadAllBytes(target).SequenceEqual(expected)&&fallback.Hosts.SequenceEqual(new[]{"primary.invalid","mirror.invalid"}),"HTTP500 failover");

// Invalid bytes from a live mirror are rejected, not installed as a finished PCM.
var corrupt=new FakeHandler((request,index,token)=>Good(index==0?new byte[expected.Length]:expected));
target=Target("corrupt");await new MsuDownloader(new HttpClient(corrupt),sources).DownloadAsync(entry,target,null,default);
Check(corrupt.Hosts.Count==2&&File.ReadAllBytes(target).SequenceEqual(expected),"checksum failover");

var unavailable=new FakeHandler((request,index,token)=>new(HttpStatusCode.ServiceUnavailable));
target=Target("unavailable");byte[] sentinel=[9,8,7];File.WriteAllBytes(target,sentinel);
try{await new MsuDownloader(new HttpClient(unavailable),sources).DownloadAsync(entry,target,null,default);throw new Exception("expected download error");}
catch(IOException error){Check(error.Message.Contains("503")&&error.Message.Contains(entry.Name)&&error.Message.Contains("primary.invalid"),"actionable exhausted-source error");}
Check(File.ReadAllBytes(target).SequenceEqual(sentinel),"failed downloads preserve existing file");

// A chunked body cannot write more bytes than the pinned manifest permits.
var oversized=new FakeHandler((request,index,token)=>index==0?new(HttpStatusCode.OK){Content=new UnknownLengthContent(new byte[expected.Length+1])}:Good());
target=Target("oversized");await new MsuDownloader(new HttpClient(oversized),sources).DownloadAsync(entry,target,null,default);
Check(oversized.Hosts.Count==2&&File.ReadAllBytes(target).SequenceEqual(expected),"oversized body rejected");

using(var canceled=new CancellationTokenSource()){
 var handler=new FakeHandler((request,index,token)=>{canceled.Cancel();token.ThrowIfCancellationRequested();return Good();});
 target=Target("cancel");
 try{await new MsuDownloader(new HttpClient(handler),sources).DownloadAsync(entry,target,null,canceled.Token);throw new Exception("expected cancellation");}
 catch(OperationCanceledException){}
 Check(!File.Exists(target)&&handler.Hosts.Count==1,"cancel must stop without mirror retries");
}
Check(!Directory.EnumerateFiles(root,"*.part-*",SearchOption.AllDirectories).Any(),"temporary files cleaned");

string config=Path.Combine(root,"msu-sources.json");File.WriteAllText(config,"{\"sources\":[\"https://music.example.org/eb/v1/\"]}");
Check(MsuDownloader.LoadSources(config)[0].Host=="music.example.org","custom mirror precedes fallback sources");
File.WriteAllText(config,"{\"sources\":[\"http://insecure.invalid/\"]}");
try{MsuDownloader.LoadSources(config);throw new Exception("expected HTTPS validation");}catch(InvalidDataException){}

var order=new List<string>();
var completed=await SetupWorkflow.RunAsync(()=>{order.Add("game");return Task.FromResult(new SetupResult(0,0,true));},()=>{order.Add("music");throw new HttpRequestException("HTTP500");},default);
Check(order.SequenceEqual(new[]{"game","music"})&&completed.CreatedStarterSeed&&completed.SoundtrackWarning!=null,"optional outage must retain successful game setup");
bool musicCalled=false;
try{await SetupWorkflow.RunAsync(()=>throw new InvalidDataException("bad ROM"),()=>{musicCalled=true;return Task.FromResult((1,1L));},default);throw new Exception("expected ROM error");}catch(InvalidDataException){}
Check(!musicCalled,"game failure must propagate before music");
var successful=await SetupWorkflow.RunAsync(()=>Task.FromResult(new SetupResult(0,0,false)),()=>Task.FromResult((164,1234L)),default);
Check(successful.MsuTracks==164&&successful.MsuBytes==1234&&successful.SoundtrackWarning==null,"music success counts");
using(var canceled=new CancellationTokenSource()){
 try{await SetupWorkflow.RunAsync(()=>Task.FromResult(new SetupResult(0,0,false)),()=>{canceled.Cancel();throw new OperationCanceledException(canceled.Token);},canceled.Token);throw new Exception("expected workflow cancellation");}catch(OperationCanceledException){}
}
Console.WriteLine("PASS: HTTP500/503 fallback, checksum/oversize rejection, cancellation, atomic preservation, source configuration, game-first workflow and optional outage handling");
File.WriteAllText(Path.Combine(root,"results.json"),JsonSerializer.Serialize(new{Passed=true,NetworkUsed=false,OwnerDataUsed=false,Checks=13},new JsonSerializerOptions{WriteIndented=true}));

sealed class FakeHandler(Func<HttpRequestMessage,int,CancellationToken,HttpResponseMessage> respond):HttpMessageHandler {
 internal List<string> Hosts {get;}=[];
 protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request,CancellationToken token){int i=Hosts.Count;Hosts.Add(request.RequestUri!.Host);return Task.FromResult(respond(request,i,token));}
}
sealed class UnknownLengthContent(byte[] bytes):HttpContent {
 protected override Task SerializeToStreamAsync(Stream stream,TransportContext? context)=>stream.WriteAsync(bytes).AsTask();
 protected override bool TryComputeLength(out long length){length=0;return false;}
}
