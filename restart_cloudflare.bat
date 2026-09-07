@echo off
REM Kill existing cloudflared process
taskkill /F /IM cloudflared.exe 2>nul

REM Create .cloudflared config directory
cd /d "%USERPROFILE%"
if not exist .cloudflared mkdir .cloudflared

REM Create config.yml with HTTPS origin
(
echo tunnel: certification-evaluations-eastern-lines
echo credentials-file: %USERPROFILE%\.cloudflared\cert.pem
echo protocol: quic
echo.
echo ingress:
echo   - hostname: certification-evaluations-eastern-lines.trycloudflare.com
echo     service: https://192.168.1.50:5173
echo     originRequest:
echo       originServerName: localhost
echo   - service: http_status:404
) > "%USERPROFILE%\.cloudflared\config.yml"

echo Config created at "%USERPROFILE%\.cloudflared\config.yml"
echo.
echo Now run:
echo   cloudflared tunnel run
pause
