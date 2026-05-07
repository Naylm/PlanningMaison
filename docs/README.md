# 🏡 Planning Maison

Application web familiale simple et rapide pour organiser le quotidien : calendrier partagé, tâches ménagères avec classement gamifié, liste de courses, et notes.

---

## 🚀 Lancement rapide

### 🪟 Windows — double-clic

1. **Installez Python** si ce n'est pas déjà fait → [python.org/downloads](https://www.python.org/downloads/)  
   ⚠️ Lors de l'installation, cochez bien **« Add Python to PATH »**
2. **Double-cliquez** sur **`Lancer_Planning.bat`**
3. Une fenêtre noire s'ouvre, attendez que le navigateur se lance automatiquement
4. **Ne fermez pas la fenêtre noire** tant que vous utilisez l'appli

> Lancement suivants : il suffit de re-double-cliquer. L'installation est faite une seule fois.

---

### � Linux — terminal

**Première fois uniquement :**
```bash
chmod +x run.sh
```

**À chaque lancement :**
```bash
./run.sh
```

Le script ouvre automatiquement le guide utilisateur et le navigateur.

> Si Python est absent : `sudo apt install python3 python3-venv` (Ubuntu/Debian)

---

## 💾 Sauvegarde des données

Toutes les données (membres, événements, tâches, courses, notes) sont **automatiquement enregistrées** dans le fichier **`fredo.db`** situé dans ce dossier.

- ✅ Le fichier est créé dès le premier lancement
- ✅ Chaque action (ajout, modification, suppression) est sauvegardée immédiatement
- ✅ Relancer l'application n'efface rien
- ✅ Déplacer le dossier entier conserve toutes les données

**Faire une copie de sauvegarde :**  
Dans la barre latérale de l'appli → cliquez **« Sauvegarder les données »** pour télécharger une copie du fichier `fredo.db`.  
Gardez cette copie dans un endroit sûr (clé USB, cloud…).

> ⚠️ Ne supprimez pas `fredo.db` — c'est là que tout est stocké.

---

## ✨ Fonctionnalités

| Section | Ce que ça fait |
|---|---|
| 📊 Tableau de bord | Vue d'ensemble : événements, tâches, classement, courses |
| � Calendrier | Planning familial, cliquer sur un jour pour ajouter un événement |
| ✅ Tâches | Tâches ménagères avec points ⭐, classement mensuel gamifié 🏆 |
| 🛒 Courses | Liste partagée, cocher les articles, vider les cochés d'un clic |
| 📝 Notes | Post-its colorés pour les infos importantes |
| 👥 Membres | Profils avec avatar emoji et couleur personnalisée |
| 🌙 Mode sombre | Bouton en haut à droite |

---

## 📱 Accès depuis un téléphone / tablette (même Wi-Fi)

### Prérequis : autoriser le pare-feu

Si l'appli ne s'ouvre pas depuis le téléphone, le pare-feu bloque l'accès. Voici comment l'autoriser :

#### 🪟 Windows

1. **Paramètres Windows** → **Sécurité** → **Pare-feu et protection réseau**
2. Cliquez sur **"Autoriser une application via le pare-feu"**
3. Cliquez sur **"Modifier les paramètres"** (en haut)
4. Cliquez sur **"Autoriser une autre application..."**
5. Cliquez sur **"Parcourir..."** et sélectionnez :

   ```text
   C:\Users\VOTRE_NOM\Desktop\PlanningMaison\venv\Scripts\python.exe
   ```

6. Cliquez sur **"Ajouter"**
7. Cochez les cases **"Réseau privé"** et **"Réseau public"** pour cette ligne
8. Cliquez sur **"OK"**

#### 🐧 Linux (Ubuntu / Debian)

```bash
# Autoriser le port 5000
sudo ufw allow 5000

# Vérifier que c'est actif
sudo ufw status
```

#### 🐧 Linux (Fedora / CentOS / RHEL)

```bash
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

#### 🍎 macOS

```bash
# Ouvrir les préférences du pare-feu
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Autoriser Python (si nécessaire)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3
```

Ou via l'interface graphique : **Préférences Système** → **Sécurité et confidentialité** → **Pare-feu** → **Options du pare-feu** → ajoutez Python.

---

### Connexion depuis le téléphone

1. **Lancez l'application** sur le PC avec `Lancer_Planning.bat` (Windows) ou `./run.sh` (Linux)

2. **Dans la fenêtre noire**, regardez la ligne affichée :

   ```text
   http://192.168.1.XX:5000
   ```

3. **Sur votre téléphone / tablette** (connecté au même Wi-Fi) :
   - Ouvrez Chrome ou Safari
   - Tapez cette adresse dans la barre en haut
   - ✅ L'appli s'ouvre !

> Astuce : Sur mobile, "Ajouter à l'écran d'accueil" pour avoir une icône comme une vraie app.
>
> ⚠️ Le PC doit rester allumé avec la fenêtre noire ouverte pour que l'appli soit accessible.

---

## � Ajouter l'icône sur l'écran d'accueil (Android & iOS)

Pour que Planning Maison ressemble à une vraie application sur votre téléphone :

### 🤖 Android (Chrome)

1. Ouvrez l'appli dans Chrome avec l'adresse affichée
2. Appuyez sur les **3 points** ⋮ (menu) en haut à droite
3. Sélectionnez **"Ajouter à l'écran d'accueil"**
4. Confirmez en tapant **"Ajouter"**
5. ✅ L'icône apparaît sur votre écran d'accueil !

###  iOS (iPhone / iPad - Safari)

1. Ouvrez l'appli dans Safari avec l'adresse affichée
2. Appuyez sur le bouton **Partager** ⎙ (carré avec flèche vers le haut) en bas de l'écran
3. Faites défiler et sélectionnez **"Sur l'écran d'accueil"**
4. Confirmez en tapant **"Ajouter"** en haut à droite
5. ✅ L'icône apparaît sur votre écran d'accueil !

> 💡 Une fois l'icône créée, vous n'avez plus besoin de retaper l'adresse — un clic suffit !

---

## �� Structure du projet

```text
PlanningMaison/
├── app.py                  → Serveur & API
├── fredo.db                → Base de données (NE PAS SUPPRIMER)
├── requirements.txt        → Dépendances Python
├── Lancer_Planning.bat     → Lancement Windows
├── run.sh                  → Lancement Linux
├── GUIDE_UTILISATEUR.md    → Guide complet
├── static/
│   ├── css/style.css
│   └── js/main.js
└── templates/              → Pages HTML
```

---

## 🛠️ Stack technique

- **Backend** : Python 3, Flask, Flask-SQLAlchemy, SQLite
- **Frontend** : HTML5, CSS3, JavaScript vanilla
- **Librairies** : FullCalendar 6, FontAwesome 6, Google Fonts (Inter)

---
*Développé pour une organisation familiale simple et efficace.* 🏡
