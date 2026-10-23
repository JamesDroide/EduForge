Write-Host "Creando regla de firewall para PostgreSQL..." -ForegroundColor Yellow

try {
    New-NetFirewallRule -DisplayName "PostgreSQL Server" `
                        -Direction Inbound `
                        -Protocol TCP `
                        -LocalPort 5432 `
                        -Action Allow `
                        -Profile Any `
                        -Enabled True

    Write-Host "Regla de firewall creada exitosamente." -ForegroundColor Green
    Write-Host ""
    Write-Host "PostgreSQL ahora esta accesible desde otras maquinas." -ForegroundColor Green
    Write-Host ""
    Write-Host "Verificando reglas de firewall para PostgreSQL..." -ForegroundColor Yellow
    Get-NetFirewallRule -DisplayName "*PostgreSQL*" | Select-Object DisplayName, Enabled, Direction, Action

} catch {
    Write-Host "Error al crear la regla de firewall: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Asegurate de ejecutar este script como ADMINISTRADOR" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Presiona cualquier tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
