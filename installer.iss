#define AppName "두디오 다운로더"
#define AppVersion "1.0"
#define AppExeName "DodioDownloader.exe"

; ffmpeg.exe 경로 - 본인 환경에 맞게 수정하세요
; build_installer.bat을 먼저 실행했다면 build_temp\ffmpeg.exe가 자동으로 준비됩니다
#define FfmpegSource "build_temp\ffmpeg.exe"

[Setup]
AppId={{B7A3C2D1-E4F5-4321-ABCD-EF0123456789}
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={autopf}\DodioDownloader
DefaultGroupName={#AppName}
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=DodioDownloader_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; 관리자 권한 없이도 설치 가능 (사용자 폴더에 설치됨)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\DodioDownloader\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#FfmpegSource}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
