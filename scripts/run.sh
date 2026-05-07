#!/bin/bash
set -e

# ── Couleurs ─────────────────────────────────────────────
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ── Se placer à la RACINE du projet (parent de scripts/) ─
cd "$(dirname "$0")/.."

echo
echo -e "${BLUE} ============================================${NC}"
echo -e "${BLUE}   Planning Maison  -  Lancement             ${NC}"
echo -e "${BLUE} ============================================${NC}"
echo

# ── 1. Python ────────────────────────────────────────────
echo -e " [1/4] Vérification de Python..."
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
else
    echo -e "${RED} [!] ERREUR : Python 3 n'est pas installé.${NC}"
    echo -e "     Installez-le avec :"
    echo -e "       Ubuntu/Debian : ${YELLOW}sudo apt install python3 python3-venv${NC}"
    echo -e "       Fedora        : ${YELLOW}sudo dnf install python3${NC}"
    echo -e "       Arch          : ${YELLOW}sudo pacman -S python${NC}"
    exit 1
fi
echo -e " [OK] $($PYTHON_CMD --version)"
echo

# ── 2. Module venv ───────────────────────────────────────
if ! $PYTHON_CMD -m venv --help &>/dev/null; then
    echo -e "${RED} [!] ERREUR : Module 'venv' manquant.${NC}"
    echo -e "     Installez-le avec : ${YELLOW}sudo apt install python3-venv${NC}"
    exit 1
fi

# ── 3. Environnement virtuel ─────────────────────────────
echo -e " [2/4] Préparation de l'environnement..."
if [ ! -f "venv/bin/python" ]; then
    echo -e "       Création en cours, patience (1ère fois seulement)..."
    $PYTHON_CMD -m venv venv
fi
echo -e " [OK] Environnement prêt."
echo

# ── 4. Dépendances ───────────────────────────────────────
echo -e " [3/4] Mise à jour des composants..."
venv/bin/pip install --upgrade pip --quiet
venv/bin/pip install -r requirements.txt --quiet
echo -e " [OK] Composants à jour."
echo

# ── 5. Lancement ─────────────────────────────────────────
echo -e " [4/4] Lancement de l'application..."

# Ouvrir le navigateur après 2 secondes
if command -v xdg-open &>/dev/null; then
    (sleep 2 && xdg-open http://127.0.0.1:5000 2>/dev/null) &
elif command -v open &>/dev/null; then
    (sleep 2 && open http://127.0.0.1:5000) &
fi

# Récupérer l'IP locale
LAN_IP=$(ip route get 1.1.1.1 2>/dev/null | awk '{print $7; exit}')
if [ -z "$LAN_IP" ]; then
    LAN_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
fi

echo
echo -e "${GREEN} ============================================${NC}"
echo -e "${GREEN}  Ce laptop   : http://127.0.0.1:5000       ${NC}"
if [ -n "$LAN_IP" ]; then
echo -e "${GREEN}                                             ${NC}"
echo -e "${GREEN}  Téléphone / tablette (même Wi-Fi) :       ${NC}"
echo -e "${GREEN}  📡 http://${LAN_IP}:5000          ${NC}"
fi
echo -e "${GREEN}                                             ${NC}"
echo -e "${GREEN}  NE FERMEZ PAS CE TERMINAL                 ${NC}"
echo -e "${GREEN}  (Ctrl+C pour arrêter)                     ${NC}"
echo -e "${GREEN} ============================================${NC}"
echo

venv/bin/python app.py

echo
echo -e "${YELLOW} Application arrêtée. Données sauvegardées dans fredo.db${NC}"
echo
