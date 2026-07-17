# PredictIQ — Auto Setup & Launch
# Run this in PowerShell:  .\setup_and_run.ps1

Write-Host ""
Write-Host " =====================================================" -ForegroundColor Cyan
Write-Host "  PredictIQ - Predictive Maintenance System Setup" -ForegroundColor Cyan
Write-Host " =====================================================" -ForegroundColor Cyan
Write-Host ""

# ── Detect Python ─────────────────────────────────────────────────────────
$pythonExe = $null

$candidates = @(
    "C:\Users\whoca\AppData\Local\Python\pythoncore-3.14-64\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Python\pythoncore-3.14-64\python.exe"
)

# Also probe python / py on PATH (PS5-compatible, no ?. operator)
try { $p = Get-Command python -ErrorAction Stop; $candidates += $p.Source } catch {}
try { $p = Get-Command py    -ErrorAction Stop; $candidates += $p.Source } catch {}

foreach ($candidate in $candidates) {
    if ($candidate -and (Test-Path $candidate)) {
        $pythonExe = $candidate
        Write-Host " [OK] Using Python: $pythonExe" -ForegroundColor Green
        break
    }
}

if (-not $pythonExe) {
    Write-Host " [ERROR] No Python found! Install Python 3.9+ from https://python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# ── Install packages ──────────────────────────────────────────────────────
Write-Host ""
Write-Host " Installing packages (may take 2-5 minutes)..." -ForegroundColor Yellow
Write-Host ""

& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install streamlit pandas numpy scikit-learn imbalanced-learn xgboost lightgbm plotly joblib

Write-Host ""
Write-Host " Trying catboost (optional)..." -ForegroundColor Yellow
try {
    & $pythonExe -m pip install catboost 2>$null
    Write-Host " [OK] catboost installed" -ForegroundColor Green
} catch {
    Write-Host " [WARN] catboost skipped - app works without it" -ForegroundColor Yellow
}

# ── Launch ─────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host " =====================================================" -ForegroundColor Cyan
Write-Host "  Setup complete! Launching PredictIQ..." -ForegroundColor Cyan
Write-Host " =====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " NOTE: First launch trains AI models (~60-90 sec)" -ForegroundColor Yellow
Write-Host " App opens at: http://localhost:8501" -ForegroundColor Green
Write-Host ""

Set-Location $PSScriptRoot
& $pythonExe -m streamlit run app.py
