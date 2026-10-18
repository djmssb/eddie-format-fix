@echo off
chcp 65001 >nul
cd /d "%~dp0"

set BASE=Eddie-format-0.6.4-win-x64

echo ========================================
echo   Eddie format 分卷合并与解压
echo ========================================
echo.

if not exist "%BASE%.zip.001" (
    echo [错误] 没找到 %BASE%.zip.001
    echo 请把本文件和全部 5 个分卷放在同一个文件夹里。
    pause
    exit /b 1
)

echo 正在合并 5 个分卷...
copy /b "%BASE%.zip.001"+"%BASE%.zip.002"+"%BASE%.zip.003"+"%BASE%.zip.004"+"%BASE%.zip.005" "%BASE%.zip"
if errorlevel 1 (
    echo [错误] 合并失败，请确认 5 个分卷都在。
    pause
    exit /b 1
)

echo.
echo 正在解压...
if not exist "Eddie-format" mkdir "Eddie-format"
tar -xf "%BASE%.zip" -C .
if errorlevel 1 (
    echo [提示] tar 解压失败，改用 PowerShell 解压...
    powershell -NoProfile -Command "Expand-Archive -Path '%BASE%.zip' -DestinationPath '.' -Force"
)

echo.
echo 完成。程序在 Eddie-format 文件夹里，双击 Eddie format.exe 运行。
echo 合并出来的 zip 可以删掉。
pause
