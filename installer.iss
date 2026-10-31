; Inno Setup Script for SmartCatalog Hub
; Compiles dist\SmartCatalogHub into SmartCatalog-Setup-v1.0.2.exe

#define MyAppName "SmartCatalog Hub"
#define MyAppVersion "1.2.1"
#define MyAppPublisher "SmartCatalog Hub Team"
#define MyAppURL "https://github.com/Pipetosik/SmartCatalog-Hub"
#define MyAppExeName "SmartCatalog.exe"
#define MyServiceExeName "SmartCatalogHub.exe"

[Setup]
AppId={{8B13F155-B043-4DF2-8703-9FE47C4927BC}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE
OutputDir=dist_installer
OutputBaseFilename=SmartCatalog-Setup-v1.2.1
SetupIconFile=assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startupentry"; Description: "Запускать SmartCatalog Hub при старте Windows"; GroupDescription: "Автозапуск:"

[Files]
Source: "assets\icon.ico"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "assets\icon.ico"; DestDir: "{app}"; DestName: "icon.ico"; Flags: ignoreversion
Source: "dist\SmartCatalogHub\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icon.ico"; IconIndex: 0
Name: "{group}\Деинсталлировать {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\assets\icon.ico"; IconIndex: 0
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyServiceExeName}"; Tasks: startupentry; IconFilename: "{app}\assets\icon.ico"; IconIndex: 0

[Run]
Filename: "{app}\{#MyServiceExeName}"; Description: "Запустить фоновую службу SmartCatalog"; Flags: nowait postinstall skipifsilent
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
