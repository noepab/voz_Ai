# Script para configurar el inicio automático del asistente
$shortcutPath = [System.IO.Path]::Combine([Environment]::GetFolderPath('Startup'), 'AsistenteVoz.lnk')
$targetPath = [System.IO.Path]::Combine($PSScriptRoot, 'iniciar_asistente.bat')
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $targetPath
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.WindowStyle = 7  # Minimizado
$Shortcut.Save()

Write-Host "Configuración completada. El asistente se iniciará automáticamente al iniciar Windows." -ForegroundColor Green
