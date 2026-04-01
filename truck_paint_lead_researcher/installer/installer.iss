#define MyAppName "Truck Paint Lead Researcher"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Local Research Tools"
#define MyAppExeName "TruckPaintLeadResearcher.exe"

[Setup]
AppId={{E4F1BA2D-7A7B-4A99-9241-122A909F4E18}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist_installer
OutputBaseFilename=TruckPaintLeadResearcherSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Tasks]
Name: "desktopicon"; Description: "デスクトップアイコンを作成する"; GroupDescription: "追加タスク:"; Flags: unchecked

[Files]
Source: "..\dist\TruckPaintLeadResearcher.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\data\config.json"; DestDir: "{app}\data"; Flags: ignoreversion
Source: "..\data\url_seed_sample.csv"; DestDir: "{app}\data"; Flags: ignoreversion
Source: "..\data\output\sample_output.csv"; DestDir: "{app}\data\output"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{#MyAppName} を起動"; Flags: nowait postinstall skipifsilent
