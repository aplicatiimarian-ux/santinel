@echo off
cd /d "F:\Proiecte AI\santinel"
powershell -ExecutionPolicy Bypass -File .\RENDER-DEPLOY-AUTO.ps1 -neonURL "postgresql://neondb_owner:npg_Q2E9UyOdIzWA@ep-weathered-grass-aeezrkeq-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
pause
