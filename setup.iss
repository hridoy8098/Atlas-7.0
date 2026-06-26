; Atlas 7.0 — Inno Setup Installer Script
; 1. Download Inno Setup: https://jrsoftware.org/isdl.php
; 2. Right-click this file → Compile (or run: iscc setup.iss)
; 3. Output: Output\Atlas_7.0_Setup.exe

#define MyAppName "Atlas 7.0"
#define MyAppVersion "7.0.0"
#define MyAppPublisher "Atlas AI"
#define MyAppURL "http://localhost:8000"
#define MyAppExeName "Atlas.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Atlas
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=Atlas_7.0_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
; Python embeddable (user must download separately)
; Source: "C:\path\to\python-3.13.3-embed-amd64.zip"; DestDir: "{app}\python"; Flags: ignoreversion
; Main app files
Source: "main.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "server.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "command_handler.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "or_client.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env.example"; DestDir: "{app}"; DestName: ".env"; Flags: ignoreversion
; Backend modules
Source: "backend\*"; DestDir: "{app}\backend"; Flags: ignoreversion recursesubdirs createallsubdirs
; Frontend build
Source: "frontend\dist\*"; DestDir: "{app}\frontend\dist"; Flags: ignoreversion recursesubdirs createallsubdirs
; Tools (if any)
Source: "tools\*"; DestDir: "{app}\tools"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
Name: "{app}\data"; Permissions: users-modify
Name: "{app}\logs"; Permissions: users-modify

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; WorkingDir: "{app}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: postinstall nowait skipifsilent shellexec

[Code]
{ Helper to install Python packages on first run }
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    if MsgBox('Install Python dependencies now? (requires internet)', mbConfirmation, MB_YESNO) = IDYES then
    begin
      Exec('python', ExpandConstant('-m pip install -r "{app}\requirements.txt"'), '', SW_SHOW, ewWaitUntilTerminated, ResultCode);
    end;
  end;
end;
