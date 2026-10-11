// SPDX-License-Identifier: GPL-3.0-or-later
using System.Text.Json;

namespace EarthBoundCompanion;

public sealed record AchievementEntry(string Id,string Title,string Description,int Target,int Progress=0,long UnlockedAt=0) {
 public bool Unlocked=>UnlockedAt>0;
 public string Status=>Unlocked?$"Unlocked · {DateTimeOffset.FromUnixTimeSeconds(UnlockedAt).LocalDateTime:g}":$"{Progress} / {Target}";
}
public sealed record AchievementView(IReadOnlyList<AchievementEntry> Entries,string Message);

public static class AchievementProfiles {
 public static string Root=>Environment.GetEnvironmentVariable("COMPANION_ACHIEVEMENTS_DIR") is {Length:>0} testRoot?Path.GetFullPath(testRoot):
  Path.Combine(Settings.User,"Achievements");
 public static readonly string[] Editions=["original","redux","shuffle-original","shuffle-redux"];
 public static readonly string[] EditionLabels=["Original EarthBound","MaternalBound Redux","Story Shuffle · Original","Story Shuffle · Redux"];
 static readonly AchievementEntry[] Pilot=[
  new("morning-onett","Morning, Onett","See Onett wake up after the meteor adventure.",1),
  new("meteor-patrol","Meteor Patrol","Win the battle against Starman Junior.",1),
  new("arcade-peacekeeper","Arcade Peacekeeper","Finish Frank's challenge at the arcade.",1),
  new("first-fight","First Fight, First Win","Win a battle, including an instant victory.",1),
  new("getting-the-hang","Getting the Hang of It","Win five battles. Replayed battles count too.",5)
 ];
 public static AchievementView Read(string edition) {
  if(!Editions.Contains(edition))throw new ArgumentException("Unknown achievement edition.",nameof(edition));
  var entries=Pilot.ToArray();string file=Path.Combine(Root,$"earthbound-{edition}.json");
  if(!File.Exists(file))return new(entries,"No progress recorded yet. Play with achievement tracking enabled to get started.");
  try {
   using var stream=new FileStream(file,FileMode.Open,FileAccess.Read,FileShare.ReadWrite|FileShare.Delete);
   if(stream.Length>16384)throw new InvalidDataException("Profile is too large.");
   using var document=JsonDocument.Parse(stream);var root=document.RootElement;
   if(root.GetProperty("schema").GetInt32()!=1 || root.GetProperty("gameId").GetString()!="earthbound" || root.GetProperty("edition").GetString()!=edition)
    throw new InvalidDataException("Unsupported achievement profile.");
   var seen=new HashSet<string>(StringComparer.Ordinal);
   foreach(var item in root.GetProperty("achievements").EnumerateArray()) {
    string id=item.GetProperty("id").GetString()??"";int index=Array.FindIndex(entries,e=>e.Id==id);
    int progress=item.GetProperty("progress").GetInt32();long when=item.GetProperty("unlockedAt").GetInt64();
    if(index<0 || !seen.Add(id) || progress<0 || progress>entries[index].Target || when<0 || when>253402300799L || (progress==entries[index].Target)!=(when>0))
     throw new InvalidDataException("Invalid achievement record.");
    entries[index]=entries[index] with {Progress=progress,UnlockedAt=when};
   }
   return new(entries,$"{entries.Count(e=>e.Unlocked)} of {entries.Length} unlocked · Local profile");
  }catch(Exception e)when(e is IOException or InvalidDataException or UnauthorizedAccessException or JsonException or InvalidOperationException or KeyNotFoundException or FormatException or OverflowException) {
   return new(Pilot.ToArray(),$"Could not read this profile: {e.Message} The file has been left untouched.");
  }
 }
}
