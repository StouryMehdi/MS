@echo off
title WiFi Password Extractor
echo WiFi Password Extractor
echo ======================
echo.

setlocal enabledelayedexpansion

set "outputfile=WiFi_Passwords_Only_%DATE:~-4%-%DATE:~-10,2%-%DATE:~-7,2%.txt"
set "tempfile=temp_passwords.txt"
set "fullfile=%~dp0%outputfile%"
set "fulltemp=%~dp0%tempfile%"


echo Extracting WiFi passwords to: %outputfile%
echo.

for /f "skip=9 tokens=2 delims=:" %%i in ('netsh wlan show profiles') do (
    set "ssid=%%i"
    set "ssid=!ssid:~1!"
    if not "!ssid!"=="" (
        echo Extracting: !ssid!
        for /f "tokens=2 delims=:" %%j in ('netsh wlan show profile name^="!ssid!" key^=clear ^| findstr "Key Content"') do (
            set "pass=%%j"
            set "pass=!pass:~1!"
            echo !pass! >> "%fulltemp%"
        )
    )
)

:: Remove duplicates and create final file
echo WiFi Passwords (unique) > "%fullfile%"
echo ===================== >> "%fullfile%"
echo. >> "%fullfile%"

set "prev_pass="
for /f "tokens=*" %%p in ('sort "%fulltemp%"') do (
    set "current_pass=%%p"
    if "!current_pass!" neq "!prev_pass!" (
        echo !current_pass! >> "%fullfile%"
    )
    set "prev_pass=!current_pass!"
)

del "%fulltemp%"

echo.
echo All passwords saved to: %fullfile%
echo.
pause