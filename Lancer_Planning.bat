@echo off
chcp 65001 >nul
echo.
echo  ============================================
echo    Planning Maison  -  Lancement
echo  ============================================
echo.

:: Aller dans le dossier du script
cd /d "%~dp0"

:: ── 1. Python ──────────────────────────────────────
echo  [1/4] Verification de Python...
set PYTHON_CMD=
where python >nul 2>&1 && set PYTHON_CMD=python
if "%PYTHON_CMD%"=="" (
    where py >nul 2>&1 && set PYTHON_CMD=py
)
if "%PYTHON_CMD%"=="" (
    echo.
    echo  [!] Python n'est pas installe ou pas dans le PATH.
    echo.
    echo  ==> Telechargez-le sur : https://www.python.org/downloads/
    echo      Lors de l'installation, COCHEZ bien :
    echo      "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
%PYTHON_CMD% --version
echo  [OK] Python trouve.
echo.

:: ── 2. Environnement virtuel ───────────────────────
echo  [2/4] Preparation de l'environnement...
if not exist "venv\Scripts\activate.bat" (
    echo       Creation en cours, patience...
    %PYTHON_CMD% -m venv venv
    if %errorlevel% neq 0 (
        echo  [!] Echec de creation de venv.
        pause
        exit /b 1
    )
)
echo  [OK] Environnement pret.
echo.

:: ── 3. Dependances ─────────────────────────────────
echo  [3/4] Mise a jour des composants (peut prendre 1 minute)...
venv\Scripts\python.exe -m pip install --upgrade pip --quiet
venv\Scripts\python.exe -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo  [!] Echec d'installation. Verifiez votre connexion internet.
    pause
    exit /b 1
)
echo  [OK] Composants installes.
echo.

:: ── 4. Lancement ───────────────────────────────────
echo  [4/4] Lancement de l'application...
echo.
echo  ============================================
echo   Ouverture sur http://127.0.0.1:5000
echo   NE FERMEZ PAS cette fenetre !
echo   (fermez-la pour arreter l'application)
echo  ============================================
echo.

:: Ouvrir le navigateur apres 2 secondes
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:5000"

:: Lancer Flask
venv\Scripts\python.exe app.py

echo.
echo  Application arretee. Vos donnees sont sauvegardes dans fredo.db
pause
