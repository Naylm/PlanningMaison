# 🏡 Guide d'utilisation - Planning Maison

Bienvenue dans votre outil de gestion familiale ! Ce guide vous explique comment installer et lancer l'application très simplement.

---

## 🚀 Installation et Lancement Rapide

L'application est conçue pour s'installer toute seule. Suivez simplement l'étape correspondant à votre ordinateur :

### 🪟 Sur Windows
1. Double-cliquez sur le fichier : **`Lancer_Planning.bat`**
2. Le script va vérifier si vous avez Python et installera tout le nécessaire automatiquement.
3. Votre navigateur s'ouvrira tout seul sur la page du planning.

### 🐧 Sur Linux
1. Ouvrez un terminal dans ce dossier.
2. Tapez `chmod +x run.sh` (à faire une seule fois pour donner l'autorisation).
3. Tapez `./run.sh` pour lancer l'application.
4. *Optionnel* : Vous pouvez utiliser le fichier `PlanningMaison.desktop` pour l'ajouter à votre menu d'applications.

---

## ❓ En cas de problème

### "Python n'est pas reconnu" (Windows)
Si le script vous dit que Python est absent :
1. Téléchargez-le ici : [python.org/downloads](https://www.python.org/downloads/)
2. Lors de l'installation, **cochez impérativement la case "Add Python to PATH"**.
3. Relancez le fichier `.bat`.

### Erreur "venv" ou "module manquant" (Linux)
Sur certaines versions de Linux (Ubuntu/Debian), il faut installer un composant supplémentaire. Tapez cette commande dans votre terminal :
`sudo apt install python3-venv`

---

## 📱 Utilisation sur Smartphone / Tablette
Vous pouvez accéder au planning depuis n'importe quel appareil connecté à votre Wi-Fi :
1. Lancez l'application sur votre PC.
2. Notez l'adresse IP de votre PC.
3. Sur votre téléphone, entrez l'adresse : `http://VOTRE_IP:5000`

---

## 🛠️ Fonctionnalités
- **Tableau de bord** : Vos prochains événements et notes.
- **Membres** : Gérez les profils de chaque membre de la famille.
- **Calendrier** : Planning complet et interactif.
- **Courses** : Liste partagée mise à jour en temps réel.
- **Notes** : Post-its de couleur pour ne rien oublier.

---
*Développé pour vous faciliter la vie quotidienne !* 🚀
