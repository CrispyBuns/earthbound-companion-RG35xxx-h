// SPDX-License-Identifier: GPL-3.0-or-later
namespace EarthBoundCompanion;

sealed partial class MainForm {
 int achievementEdition;
 int achievementCategory;
 void AchievementsPage() {
  Header("A journey worth remembering.","46 achievements from Onett to the ending. Earned achievements stay unlocked when you reload a save.");
  Check("Track achievements","Local progress and in-game notifications. Changes apply the next time you launch the game.",settings.AchievementsEnabled,v=>settings.AchievementsEnabled=v);
  Choice("Game edition","Each edition has its own progress. Story Shuffle progress is shared across seeds.",AchievementProfiles.EditionLabels,achievementEdition,i=>{achievementEdition=i;ShowPage("Achievements");});
  Choice("Show","Browse the full set or choose a category.",AchievementProfiles.Categories,achievementCategory,i=>{achievementCategory=i;ShowPage("Achievements");});
  var view=AchievementProfiles.Read(AchievementProfiles.Editions[achievementEdition]);
  page.Controls.Add(Theme.Text(view.Message,11,Theme.Gold));
  foreach(var entry in view.Entries.Where(e=>achievementCategory==0||e.Category==AchievementProfiles.Categories[achievementCategory])) {
   var card=new TableLayoutPanel{Height=94,ColumnCount=1,RowCount=3,Padding=new Padding(14,10,14,8),Margin=new Padding(0,6,0,6),BackColor=Theme.Surface};
   card.RowStyles.Add(new RowStyle(SizeType.Absolute,26));card.RowStyles.Add(new RowStyle(SizeType.Absolute,24));card.RowStyles.Add(new RowStyle(SizeType.Percent,100));
   var title=Theme.Text(entry.Title,12,entry.Unlocked?Theme.Gold:Theme.Ink);title.Font=Theme.Font(12,FontStyle.Bold);card.Controls.Add(title);
   card.Controls.Add(Theme.Text(entry.Description,10,Theme.Muted));card.Controls.Add(Theme.Text(entry.Status,10,entry.Unlocked?Theme.Green:Theme.Muted));page.Controls.Add(card);
  }
  Actions(Theme.Button("Refresh progress",()=>ShowPage("Achievements")));
  var location=Theme.Text($"Saved locally: {AchievementProfiles.Root}",9,Theme.Muted);location.MaximumSize=new Size(660,0);page.Controls.Add(location);
  page.Controls.Add(Theme.Text("Standalone achievements with original names. No account or server is needed. Cheats and replayed battles are allowed.",10,Theme.Muted));
 }
}
