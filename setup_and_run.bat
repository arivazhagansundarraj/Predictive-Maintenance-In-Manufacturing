@echo off
title PredictIQ — Auto Setup
color 0B
echo.
echo  =====================================================
echo   PredictIQ - Predictive Maintenance System Setup
echo  =====================================================
echo.

REM ── Detect Python interpreter ─────────────────────────────────────────────
set PYTHON_EXE=

REM Try the Python 3.14 install the IDE uses
if exist "C:\Users\whoca\AppData\Local\Python\pythoncore-3.14-64\python.exe" (
    set PYTHON_EXE=C:\Users\whoca\AppData\Local\Python\pythoncore-3.14-64\python.exe
    echo [OK] Found Python 3.14 at: %PYTHON_EXE%
    goto :install
)

REM Try system python
where python >nul 2>&1
if %ERRORLEVEL% == 0 (
    set PYTHON_EXE=python
    echo [OK] Found system Python
    goto :install
)

REM Try py launcher
where py >nul 2>&1
if %ERRORLEVEL% == 0 (
    set PYTHON_EXE=py
    echo [OK] Found py launcher
    goto :install
)

echo [ERROR] No Python installation found!
echo Please install Python 3.9+ from https://python.org
pause
exit /b 1

:install
echo.
echo  Installing required packages...
echo  (This may take 2-5 minutes on first run)
echo.

"%PYTHON_EXE%" -m pip install --upgrade pip

"%PYTHON_EXE%" -m pip install streamlit pandas numpy scikit-learn imbalanced-learn xgboost lightgbm plotly joblib

REM Try catboost separately (may fail on Python 3.14)
echo.
echo  Trying catboost (optional)...
"%PYTHON_EXE%" -m pip install catboost 2>nul
if %ERRORLEVEL% == 0 (
    echo [OK] catboost installed
) else (
    echo [WARN] catboost skipped (not available for this Python version - app will still work)
)

echo.
echo  =====================================================
echo   All packages installed! Starting PredictIQ...
echo  =====================================================
echo.
echo  NOTE: First launch trains AI models (~60-90 seconds)
echo  The app will open in your browser at http://localhost:8501
echo.

cd /d "%~dp0"
"%PYTHON_EXE%" -m streamlit run app.py

pause
