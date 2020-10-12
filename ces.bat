@echo off
echo StartNox 
start /d "D:\Program Files\Nox\" nox.lnk
echo starting Nox.
choice /t 1 /d y /n >nul
echo ..
choice /t 1 /d y /n >nul
echo ...
choice /t 1 /d y /n >nul
echo .....
choice /t 1 /d y /n >nul
echo ......
choice /t 1 /d y /n >nul
echo .......
choice /t 1 /d y /n >nul
echo ........
choice /t 1 /d y /n >nul
echo .........
echo Start Learning Program
::start /d "D:\AutoXue-multiuser-master\" start.cmd

start Services
appium -a 0.0.0.0 -p 4723


if "%1" == "h" goto begin
mshta vbscript:createobject("wscript.shell").run("%~nx0 h",0)(window.close)&&exit
begin
cd /d %~dp0
echo %cd%

tasklist /nh|find /i "Appium.exe"
if errorlevel 1 (
    echo Appium not running
) else (
    REM echo Appium is running
)

tasklist /nh|find /i "Nox.exe"
if errorlevel 1 (
    echo could not start while Nox not running
    goto breakout
) else (
    REM echo Nox is running
    goto run
)


:run
REM echo venv\scripts\python -m xuexi
python -m xuexi
pause
exit

:breakout
echo please start Appium and Nox
pause
exit

