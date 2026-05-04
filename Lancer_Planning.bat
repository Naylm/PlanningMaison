@echo on
chcp 65001
echo.
echo ==========================================
echo    LANCEMENT DE PLANNING MAISON
echo ==========================================
echo.

:: 1. Detection de Python
echo [1/4] Verification de Python...
python --version
if %errorlevel% neq 0 (
    echo Python non trouve, essai avec 'py'...
    py --version
    if %errorlevel% neq 0 (
        echo ERREUR : Python n'est pas installe.
        pause
        exit /b
    )
)

:: 2. Environnement virtuel
echo [2/4] Verification de venv...
if not exist "venv" (
    echo Creation de venv...
    python -m venv venv
)

:: 3. Dependances
echo [3/4] Installation des composants...
.\venv\Scripts\python.exe -m pip install -r requirements.txt

:: 4. Lancement
echo [4/4] Lancement...
start "" http://127.0.0.1:5000
.\venv\Scripts\python.exe app.py

pause
