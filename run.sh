#!/bin/bash

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}       LANCEMENT DE PLANNING MAISON       ${NC}"
echo -e "${BLUE}==========================================${NC}"
echo

# 1. Détection de Python
echo -e "[1/4] Vérification de Python..."
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
else
    echo -e "${RED}[!] ERREUR : Python n'est pas installé.${NC}"
    echo "Installez-le avec : sudo apt install python3"
    exit 1
fi
echo -e "      - Python détecté."

# 2. Vérification du module venv
$PYTHON_CMD -m venv --help &>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}[!] ERREUR : Le module Python 'venv' est manquant.${NC}"
    echo "Installez-le avec : sudo apt install python3-venv"
    exit 1
fi

# 3. Création de l'environnement virtuel si inexistant
echo -e "[2/4] Vérification de l'environnement virtuel..."
if [ ! -d "venv" ]; then
    echo -e "      - Création de l'environnement (patience)..."
    $PYTHON_CMD -m venv venv
fi
echo -e "      - Environnement prêt."

# 4. Installation des dépendances
echo -e "[3/4] Mise à jour des composants..."
./venv/bin/pip install --upgrade pip --quiet
./venv/bin/pip install -r requirements.txt --quiet
echo -e "      - Composants à jour."

# 5. Lancement
echo -e "[4/4] Lancement de l'application..."
if command -v xdg-open &>/dev/null; then
    (sleep 2 && xdg-open http://127.0.0.1:5000) &
fi

echo -e "\n${GREEN}------------------------------------------${NC}"
echo -e " L'application démarre sur http://127.0.0.1:5000"
echo -e " NE FERMEZ PAS CE TERMINAL"
echo -e "${GREEN}------------------------------------------${NC}\n"

./venv/bin/python app.py
