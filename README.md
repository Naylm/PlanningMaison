# 🏡 Planning Maison

**Planning Maison** est une application web moderne et intuitive conçue pour simplifier l'organisation quotidienne de la famille. Gérez vos membres, votre calendrier partagé, votre liste de courses et vos notes importantes en un seul endroit.

![Aperçu de l'application](static/logo.png)

## ✨ Fonctionnalités

- **📊 Tableau de Bord** : Une vue d'ensemble des événements à venir, des notes récentes et des articles à acheter.
- **👥 Gestion des Membres** : Ajoutez chaque membre de la famille avec une couleur et un avatar personnalisés.
- **📅 Calendrier Interactif** : Un planning complet (FullCalendar) pour suivre les activités de chacun avec modification en temps réel.
- **🛒 Liste de Courses** : Une liste partagée et interactive pour ne rien oublier au supermarché.
- **📝 Notes & Post-its** : Un système de notes colorées pour les informations importantes ou les petits rappels.
- **🛡️ Sauvegarde Automatique** : Toutes vos données sont enregistrées en temps réel dans une base SQLite locale.
- **💾 Export de Sécurité** : Un bouton de backup intégré pour télécharger une copie de vos données à tout moment.

## 🚀 Installation Rapide

L'application est conçue pour être **"Zero-Configuration"** pour l'utilisateur final.

### Sur Windows 🪟
Double-cliquez sur : 👉 **`Lancer_Planning.bat`**
*Le script s'occupe de tout : vérification de Python, création de l'environnement virtuel et installation des dépendances.*

### Sur Linux 🐧
```bash
chmod +x run.sh
./run.sh
```

## 🛠️ Stack Technique

- **Backend** : Python, Flask, Flask-SQLAlchemy (SQLite)
- **Frontend** : HTML5, CSS3 (Glassmorphism), JavaScript Vanilla
- **Librairies** : FullCalendar 6, FontAwesome 6, Google Fonts (Inter)

## 📦 Structure du Projet

```text
├── app.py              # Serveur Flask & API
├── Lancer_Planning.bat # Launcher Windows
├── run.sh              # Launcher Linux
├── fredo.db           # Base de données (générée automatiquement)
├── static/             # Assets (CSS, JS, Images)
└── templates/          # Vues HTML
```

---
*Développé avec ❤️ pour une organisation familiale optimale.*
