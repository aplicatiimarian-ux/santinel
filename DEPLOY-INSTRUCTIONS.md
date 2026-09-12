# SANTINEL Deployment: Automated All-Phases

**Status:** Ready to deploy (single command)  
**Time:** ~5-10 minutes total (including Render rebuild)  
**Files:** 3 service files + git push + Render auto-deploy

---

## Quick Start (Copy-Paste One Command)

### **Step 1: Download Files**
Download these from outputs folder to `F:\Proiecte AI\santinel\` root:

- `DEPLOY-ALL-PHASES.py` (main automation script)
- `RUN-DEPLOY.bat` (Windows batch wrapper)

### **Step 2: Run Deployment**

**Option A: Windows Batch (Easiest)**
```
F:\Proiecte AI\santinel> RUN-DEPLOY.bat
```

**Option B: PowerShell**
```powershell
cd F:\Proiecte AI\santinel
python DEPLOY-ALL-PHASES.py
```

**Option C: Direct Python**
```cmd
cd F:\Proiecte AI\santinel
python DEPLOY-ALL-PHASES.py
```

---

## What Happens Automatically

| Phase | What | Time |
|-------|------|------|
| **1** | Creates 3 service files in `backend/services/` | 1s |
| **2** | Alerts you to manually update `start_api.py` (if needed) | - |
| **3** | Git commit all changes | 2s |
| **4** | Git push → Render webhook triggers | 1s |
| - | **Render rebuilds** (you monitor this) | 3-5 min |

---

## Manual Step: Update start_api.py

If `start_api.py` doesn't already have the imports, add them:

**File:** `backend/start_api.py`

```python
# AT TOP - Add imports:
from backend.services.stt_cascade_service import setup_stt_routes
from backend.services.coach_output_service import setup_coach_routes
from backend.services.evaluation_service import setup_evaluation_routes

# IN @app.on_event("startup") - Add:
@app.on_event("startup")
async def startup():
    await setup_stt_routes(app)
    await setup_coach_routes(app, framework_service, tts_service)
    await setup_evaluation_routes(app)
```

---

## Monitor Deployment

After running the script:

1. **Check Render Logs** (3-5 min):
   ```
   https://dashboard.render.com/services/santinel-backend
   → Logs tab
   → Look for: [STT], [COACH], [EVAL] messages
   ```

2. **Test Backend Health**:
   ```
   https://santinel-backend-xyz.onrender.com/health
   → Should return: {"status": "OK"}
   ```

---

## Q3: Microphone Test (On Android)

Once Render is deployed:

1. Open: `https://santinel-8a53.vercel.app`
2. Click "Start Recording"
3. Speak: "I'm feeling stressed"
4. **Verify:**
   - ✅ Lock icon 🔒 visible (HTTPS)
   - ✅ Microphone permission popup appears
   - ✅ Transcription shows (STT worked)
   - ✅ Coach text appears below (Coach output worked)
   - ✅ Audio button shows (TTS available)
   - ✅ Audio plays when clicked

---

## Troubleshooting

### Script fails: "Python not found"
→ Install Python 3.8+ or add to PATH

### Git push fails: "Not a git repository"
→ Make sure you're in `F:\Proiecte AI\santinel\` root

### Coach text still not appearing
→ Check Render logs for `[COACH]` messages
→ Verify `start_api.py` has `setup_coach_routes()` call

### All STT providers failed
→ Check `.env` for valid `DEEPGRAM_API_KEY`
→ Verify Deepgram account has quota remaining

---

## Success Indicators

✅ Script completes without errors  
✅ Git push shows "Render webhook triggered"  
✅ Render logs show build starting  
✅ Backend endpoints responding after 5 min  
✅ Microphone permission works on Android  
✅ Coach advice appears in UI  

---

## Files Deployed

```
backend/services/
├── stt_cascade_service.py    (NEW)
├── coach_output_service.py   (NEW)
└── evaluation_service.py     (NEW)

backend/
└── start_api.py              (MODIFIED - manual update)

.env                          (needs DEEPGRAM_API_KEY)

.git/
└── New commit with all 3 services
```

---

## Next: Code Automation Complete ✅

All three phases (STT + Coach + Evaluation) deployed automatically.  
Ready for live testing on Android.  
Render monitoring shows deployment status in real-time.

