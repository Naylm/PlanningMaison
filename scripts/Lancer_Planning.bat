@echo off
chcp 65001 >nul
title Planning Maison
echo.
echo  ============================================
echo    Planning Maison  -  Lancement
echo  ============================================
echo.

:: Aller a la RACINE du projet (dossier parent de scripts/)
cd /d "%~dp0.."

:: ── 1. Python ──────────────────────────────────────
echo  [1/4] Verification de Python...

set PYTHON_CMD=
where python >nul 2>&1
if %errorlevel% == 0 set PYTHON_CMD=python

if "%PYTHON_CMD%"=="" (
    where py >nul 2>&1
    if %errorlevel% == 0 set PYTHON_CMD=py
)

if "%PYTHON_CMD%"=="" (
    echo.
    echo  [!] ERREUR : Python n'est pas installe ou pas dans le PATH.
    echo.
    echo  ==> Telechargez-le sur : https://www.python.org/downloads/
    echo      Lors de l'installation, COCHEZ bien :
    echo      "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%V in ('%PYTHON_CMD% --version 2^>^&1') do echo  [OK] %%V
echo.

:: ── 2. Environnement virtuel ───────────────────────
echo  [2/4] Preparation de l'environnement...

if not exist "venv\Scripts\activate.bat" (
    echo       Creation en cours, patience...
    %PYTHON_CMD% -m venv venv
    if %errorlevel% neq 0 (
        echo  [!] Echec de creation du venv.
        pause
        exit /b 1
    )
)
echo  [OK] Environnement pret.
echo.

:: ── 3. Dependances ─────────────────────────────────
echo  [3/4] Mise a jour des composants (1ere fois = ~1 min)...
venv\Scripts\python.exe -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo  [!] Echec pip upgrade. Verifiez votre connexion internet.
    pause
    exit /b 1
)
venv\Scripts\python.exe -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo  [!] Echec installation des dependances.
    pause
    exit /b 1
)
echo  [OK] Composants installes.
echo.

:: ── 4. Lancement ───────────────────────────────────────
echo  [4/4] Lancement de l'application...
echo.

:: Recuperer l'IP locale (Wi-Fi ou Ethernet)
for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /C:"IPv4" ^| findstr /V "127.0.0.1"') do (
    set LAN_IP=%%A
    goto :found_ip
)
:found_ip
if defined LAN_IP set LAN_IP=%LAN_IP: =%

echo  ============================================
echo   Ouverture sur http://127.0.0.1:5000
echo.
if defined LAN_IP (
    echo   Depuis un telephone / tablette / autre PC
    echo   sur le MEME Wi-Fi, ouvrir :
    echo.
    echo     http://%LAN_IP%:5000
    echo.
)
echo   NE FERMEZ PAS cette fenetre !
echo   (fermez-la pour arreter l'application)
echo  ============================================
echo.

:: Generer version.txt si absent
if not exist "version.txt" (
    where git >nul 2>&1 && git rev-parse HEAD > version.txt 2>nul
    if not exist "version.txt" echo unknown > version.txt
)

:: Ouvrir le navigateur apres 2 secondes
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:5000"

:: Lancer Flask
venv\Scripts\python.exe app.py

echo.
echo  Application arretee. Vos donnees sont sauvegardes dans fredo.db
pause
