// SPDX-License-Identifier: GPL-3.0-or-later
using Avalonia.Controls;
namespace EarthBoundCompanion;

public sealed partial class MainView {
 Control Achievements() {
  var panel=Page();panel.Children.Add(Text("Achievements · 46 across the full journey"));
  Check(panel,"Track achievements (applies next launch)",()=>settings.AchievementsEnabled,v=>settings.AchievementsEnabled=v);
  panel.Children.Add(Text("Earned achievements stay unlocked when you reload a save. Each edition has separate progress; Story Shuffle progress is shared across seeds."));
  var edition=new ComboBox{ItemsSource=AchievementProfiles.EditionLabels,SelectedIndex=0};panel.Children.Add(edition);
  var category=new ComboBox{ItemsSource=AchievementProfiles.Categories,SelectedIndex=0};panel.Children.Add(category);
  var list=new StackPanel{Spacing=12};panel.Children.Add(list);
  void Update() {
   list.Children.Clear();var view=AchievementProfiles.Read(AchievementProfiles.Editions[Math.Max(0,edition.SelectedIndex)]);
   list.Children.Add(Text(view.Message));
   foreach(var entry in view.Entries.Where(e=>category.SelectedIndex<=0||e.Category==AchievementProfiles.Categories[category.SelectedIndex])) {
    var card=new StackPanel{Spacing=4};card.Children.Add(new TextBlock{Text=entry.Title,FontWeight=Avalonia.Media.FontWeight.Bold});
    card.Children.Add(Text(entry.Description));card.Children.Add(Text(entry.Status));list.Children.Add(card);
   }
  }
  edition.SelectionChanged+=(_,_)=>Update();category.SelectionChanged+=(_,_)=>Update();Update();
  panel.Children.Add(Action("Refresh progress",()=>{Update();return Task.CompletedTask;}));
  panel.Children.Add(Text($"Saved locally: {AchievementProfiles.Root}"));
  panel.Children.Add(Text("Standalone achievements for this game. No account or server is needed."));return panel;
 }
}
