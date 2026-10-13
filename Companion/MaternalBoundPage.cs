namespace EarthBoundCompanion;

sealed partial class MainForm {
 void MaternalBoundPage(){
  Header("Choose your game mode.","Select original EarthBound or MaternalBound Redux, then continue from Play. Each edition keeps separate saves. Redux setup and conversion details are below.");

  Section("Game edition");
  var build=Theme.Button(ReduxProfileService.UpdateNeeded?"Update Redux game data":ReduxProfileService.Ready?"Use MaternalBound Redux":"Build MaternalBound Redux",()=>Try(()=>{
   if(Running||generating)return;
   if(!ReduxProfileService.Ready||ReduxProfileService.UpdateNeeded){OpenReduxSetup();return;}
   ReduxProfileService.Select(settings);ShowPage("Play");Notify("MaternalBound Redux selected. Its story saves and seeds stay separate.");
  }),true);build.Enabled=!Running&&!generating;build.Width=240;
  var original=Theme.Button("Use original EarthBound",()=>Try(()=>{if(Running||generating)return;settings.AssetPack="";settings.ReduxDevelopmentEnabled=false;settings.Save();ShowPage("Play");Notify("Original EarthBound selected. Its existing saves are preserved.");}));original.Enabled=!Running&&!generating;original.Width=240;Actions(build,original);

  Section("Title screen");
  Check("Original EarthBound title screen","Use the original logo and animation while keeping Redux gameplay. Apply settings, then relaunch the game. Original mode already uses this title screen.",settings.OriginalTitleScreen,v=>settings.OriginalTitleScreen=v);

  Section("Redux release status");
  var statusCard=new TableLayoutPanel(){Height=88,ColumnCount=2,RowCount=1,BackColor=Theme.Surface,Padding=new Padding(18,13,18,13),Margin=new Padding(0,4,0,14)};
  statusCard.ColumnStyles.Add(new ColumnStyle(SizeType.Percent,72));statusCard.ColumnStyles.Add(new ColumnStyle(SizeType.Percent,28));
  var statusText=new FlowLayoutPanel(){Dock=DockStyle.Fill,FlowDirection=FlowDirection.TopDown,WrapContents=false,Margin=Padding.Empty};
  var statusTitle=Theme.Text("Native Redux conversion",15);statusTitle.Font=Theme.Font(15,FontStyle.Bold);statusTitle.Margin=new Padding(0,0,0,3);
  statusText.Controls.Add(statusTitle);statusText.Controls.Add(Theme.Text("Official release · v1.0.0",10,Theme.Muted));statusCard.Controls.Add(statusText,0,0);
  var badge=Theme.Text("RELEASED",10,Theme.Gold);badge.Font=Theme.Font(10,FontStyle.Bold);badge.Dock=DockStyle.Fill;badge.TextAlign=ContentAlignment.MiddleRight;badge.AutoSize=false;statusCard.Controls.Add(badge,1,0);page.Controls.Add(statusCard);

  Section("Included edition");
  page.Controls.Add(Theme.Text("MaternalBound Redux's restored writing, presentation and fixes · Native x64 gameplay · HD and ultrawide output · MSU music · PC controls and settings · QoL profiles · Story Shuffle adventures",11));

  var stages=new TableLayoutPanel(){Height=210,ColumnCount=2,RowCount=1,Margin=new Padding(0,4,0,8)};
  stages.ColumnStyles.Add(new ColumnStyle(SizeType.Percent,50));stages.ColumnStyles.Add(new ColumnStyle(SizeType.Percent,50));
  stages.Controls.Add(PortCard("PLAYED AND TESTED",Theme.Green,"Completed Original/Redux playthrough reports\nNative shops, equipment and Jeff's Tools\nWidescreen and smooth scrolling\n46 offline achievements\nStory Shuffle v4 preservation checks\nSeparate story and seed saves"),0,0);
  stages.Controls.Add(PortCard("TESTING LIMITS",Theme.Gold,"Every optional story branch\nFull randomized progression\nEvery music transition and combat effect\nBroader hardware/controller testing\nNewer upstream changes are separate\nReport bugs for focused fixes"),1,0);
  page.Controls.Add(stages);

  Section("Story Shuffle v4");
  page.Controls.Add(Theme.Text("Story Shuffle mixes ordinary gifts, shop stock, drops and wild enemy lineups. Required story items, trade supplies and scripted boss lineups stay intact. Each seed has its own saves; full randomized progression remains unverified.",11,Theme.Muted));
  page.Controls.Add(Theme.Text("This release uses the tested Redux version supported by Companion. Newer upstream changes are handled as separate updates.",10,Theme.Muted));
  Section("Continue an earlier Redux story");
  page.Controls.Add(Theme.Text("The game-data update rebuilds from your ROM, checks the exact reviewed art changes and copies compatible phone/F6 saves unchanged. A backup of the earlier profile remains on disk. To move saves from a separate dev.2–17 installation, use Import below; destination saves must be empty. Earlier randomizer seeds retain their original base data and saves.",10,Theme.Muted));
  page.Controls.Add(Theme.Text("A quick save made during combat retains that scene's cached art until the next battle loads. Updating never rewrites the contents of your saved scene.",10,Theme.Muted));
  var import=Theme.Button("Import earlier story saves",()=>Try(()=>{
   if(Running||generating)return;
   using var picker=new FolderBrowserDialog{Description="Select your previous Redux EarthBound Companion installation folder (dev.2–17)."};
   if(picker.ShowDialog(this)!=DialogResult.OK)return;
   int count=ReduxStoryUpgrade.Import(picker.SelectedPath);ReduxProfileService.Select(settings);ShowPage("Play");Notify($"Imported {count} story save files. Use Resume quick save to continue your F6 checkpoint.");
  }));import.Enabled=ReduxProfileService.Ready&&!Running&&!generating;import.Width=260;Actions(import);
 }

 static Panel PortCard(string title,Color color,string body){
  var card=new Panel(){Dock=DockStyle.Fill,BackColor=Theme.Rail,Padding=new Padding(18,16,18,12),Margin=new Padding(0,0,10,0)};
  var stack=new FlowLayoutPanel(){Dock=DockStyle.Fill,FlowDirection=FlowDirection.TopDown,WrapContents=false,Margin=Padding.Empty};
  var heading=Theme.Text(title,10,color);heading.Font=Theme.Font(10,FontStyle.Bold);heading.Margin=new Padding(0,0,0,10);stack.Controls.Add(heading);
  var copy=Theme.Text(body,10,Theme.Muted);copy.MaximumSize=new Size(330,0);copy.Margin=Padding.Empty;stack.Controls.Add(copy);card.Controls.Add(stack);return card;
 }
}
