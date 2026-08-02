#define AppName "BlakeLabs Multimedia"
#define AppVersion "0.1.0"
#define AppPublisher "Blake Labs"
#define AppExeName "BlakeLabsMultimedia.exe"

[Setup]
AppId={{B702F056-9B98-4D8C-BF4B-A6C10D0C6AF2}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\Blake Labs\BlakeLabs Multimedia
DefaultGroupName=BlakeLabs Multimedia
OutputDir=..\..\build\installer
OutputBaseFilename=BlakeLabsMultimedia-Setup-x64
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
WizardStyle=modern
UninstallDisplayIcon={app}\{#AppExeName}

[Files]
Source: "..\..\build\windows\BlakeLabsMultimedia\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\BlakeLabs Multimedia"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\BlakeLabs Multimedia"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch BlakeLabs Multimedia"; Flags: nowait postinstall skipifsilent
