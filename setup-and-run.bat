@echo off
echo ============================================
echo   Setting up Arivazhagan's Portfolio
echo ============================================

echo.
echo [1/3] Copying profile photo...
if exist "C:\Users\whoca\Downloads\20260425_110611.jpg" (
    copy "C:\Users\whoca\Downloads\20260425_110611.jpg" "C:\Users\whoca\Downloads\Portfolio\src\assets\profile.jpg" /Y
    echo Profile photo copied successfully!
) else (
    echo Profile photo not found, using placeholder.
)

echo.
echo [2/3] Installing dependencies...
cd /d "C:\Users\whoca\Downloads\Portfolio"
npm install

echo.
echo [3/3] Starting development server...
npm run dev

echo.
echo ============================================
echo   Portfolio is running at http://localhost:5173
echo ============================================
pause
