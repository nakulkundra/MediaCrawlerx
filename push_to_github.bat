@echo off
setlocal enabledelayedexpansion

echo =======================================================
echo   MediaCrawlerx - Push Translated Code to GitHub
echo =======================================================
echo.

cd /d "C:\Users\NAKUL.KUNDRA\MediaCrawlerx"
if %errorlevel% neq 0 (
    echo [ERROR] Could not find folder C:\Users\NAKUL.KUNDRA\MediaCrawlerx
    pause
    exit /b 1
)

echo [1/4] Checking Git repository...
if not exist ".git" (
    echo Initializing new Git repository...
    git init
    git branch -M main
    git remote add origin https://github.com/nakulkundra/MediaCrawlerx.git
) else (
    echo Existing Git repository found.
    git remote set-url origin https://github.com/nakulkundra/MediaCrawlerx.git >nul 2>&1 || git remote add origin https://github.com/nakulkundra/MediaCrawlerx.git
)

echo.
echo [2/4] Staging all files...
git add -A

echo.
echo [3/4] Creating commit...
git commit -m "feat: translate entire codebase, docstrings, logs, and documentation to 100% English"

echo.
echo [4/4] Pushing to GitHub (main branch)...
git push -u origin main --force

if %errorlevel% equ 0 (
    echo.
    echo =======================================================
    echo   SUCCESS! All changes pushed to https://github.com/nakulkundra/MediaCrawlerx
    echo =======================================================
) else (
    echo.
    echo =======================================================
    echo   [ERROR] Push failed. Please check your GitHub credentials or network.
    echo =======================================================
)

echo.
pause
