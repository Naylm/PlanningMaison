# 🏡 Guide Utilisateur — Planning Maison

Bienvenue ! Ce guide vous explique tout ce dont vous avez besoin pour utiliser l'application, même si vous n'êtes pas expert en informatique.

---

## 🚀 1. Lancer l'application

### 🪟 Sur Windows

**Étape 1 — Installer Python (une seule fois)**

1. Allez sur [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Cliquez sur le gros bouton jaune « Download Python »
3. Lancez le fichier téléchargé
4. ⚠️ **IMPORTANT** : tout en bas de la fenêtre d'installation, cochez **« Add Python to PATH »** avant de cliquer Installer

**Étape 2 — Lancer l'application**

1. Ouvrez le dossier **PlanningMaison**
2. **Double-cliquez** sur **`Lancer_Planning.bat`**
3. Une fenêtre noire s'ouvre — c'est normal, laissez-la tourner
4. Après quelques secondes, votre navigateur (Chrome, Firefox…) s'ouvre automatiquement
5. L'application est prête !

> 🔁 La prochaine fois : re-double-cliquez simplement sur `Lancer_Planning.bat`. L'installation ne se refait pas.

> ⚠️ **Ne fermez pas la fenêtre noire** tant que vous utilisez l'application. La fermer arrête le planning.

---

### 🐧 Sur Linux

**Première fois uniquement :**

Ouvrez un terminal dans le dossier PlanningMaison et tapez :
```
chmod +x run.sh
```

**À chaque lancement :**
```
./run.sh
```

Le guide utilisateur s'ouvrira automatiquement, puis le navigateur.

**Ajouter au menu d'applications (optionnel) :**

Pour lancer depuis votre menu graphique :
```
cp PlanningMaison.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications/
```

---

## 💾 2. Vos données sont-elles sauvegardées ?

**Oui, automatiquement.** Chaque action que vous faites (ajouter un événement, cocher un article, créer une tâche…) est **enregistrée immédiatement** dans un fichier appelé **`fredo.db`** dans le dossier de l'application.

- ✅ Fermer et relancer l'application : **rien n'est perdu**
- ✅ Redémarrer l'ordinateur : **rien n'est perdu**
- ✅ Déplacer tout le dossier : **les données suivent**

**Faire une copie de sécurité :**

Dans l'application, barre de gauche tout en bas → cliquez **« Sauvegarder les données »**.  
Cela télécharge une copie du fichier `fredo.db`. Conservez-la sur une clé USB ou dans un dossier cloud.

> ⚠️ Ne supprimez jamais le fichier `fredo.db` — c'est votre base de données.

---

## 📱 3. Utiliser sur téléphone ou tablette

L'application fonctionne aussi sur mobile, depuis le même réseau Wi-Fi :

1. Lancez l'application sur le PC comme d'habitude
2. Sur le PC, trouvez votre adresse IP locale :
   - **Windows** : ouvrez un terminal, tapez `ipconfig`, notez l'adresse `192.168.x.x`
   - **Linux** : tapez `ip a` ou `hostname -I`
3. Sur votre téléphone (connecté au même Wi-Fi), ouvrez le navigateur et tapez :
   `http://192.168.x.x:5000` (remplacez par votre IP)

---

## � 4. Toutes les fonctionnalités

### 📊 Tableau de bord
La page d'accueil. D'un coup d'œil vous voyez :
- Les prochains événements du calendrier
- Les tâches à faire
- Le classement du mois
- La liste de courses en attente
- Les dernières notes

### 📅 Calendrier
- Voir tous les événements de la famille
- **Cliquer sur un jour** pour ajouter un événement directement
- Cliquer sur un événement pour le modifier ou le supprimer
- Vue mois ou semaine (boutons en haut à droite)

### ✅ Tâches ménagères
Le système de tâches avec **points et classement** :

1. **Créer une tâche** : cliquez **« + Nouvelle tâche »**, donnez un nom et une valeur en ⭐ (1 à 5 points)
2. **Accomplir une tâche** : choisissez qui l'a faite dans le menu déroulant, puis cliquez ✅
3. **Classement** : les points s'accumulent pour chaque membre du foyer — le classement du mois est visible ici et sur le tableau de bord
4. Les tâches accomplies apparaissent en bas avec la possibilité de les réactiver (↔️)

> 🏆 Le classement se remet à zéro chaque mois — de quoi motiver tout le monde !

### 🛒 Liste de courses
- Ajoutez des articles en bas de la liste
- Cochez ce qui est acheté
- Cliquez **« Vider les cochés 🧹 »** pour faire le ménage d'un coup
- Le compteur d'articles restants se met à jour automatiquement

### 📝 Notes
- Créez des post-its colorés pour les infos importantes
- Modifiez ou supprimez-les à tout moment

### 👥 Membres
- Ajoutez chaque personne du foyer avec un prénom, une couleur et un emoji
- Les couleurs apparaissent dans le calendrier et le classement

### 🌙 Mode sombre
Bouton en haut à droite (🌙 / ☀️). La préférence est mémorisée.

---

## ❓ 5. Problèmes fréquents

### « Python n'est pas reconnu » (Windows)
- Téléchargez Python sur [python.org/downloads](https://www.python.org/downloads/)
- **Cochez « Add Python to PATH »** pendant l'installation
- Relancez `Lancer_Planning.bat`

### La fenêtre noire se ferme toute seule (Windows)
- Un message d'erreur a dû s'afficher. Relancez et lisez le message en rouge.
- Vérifiez votre connexion internet (nécessaire pour la 1ère installation)

### « Module venv manquant » (Linux)
```
sudo apt install python3-venv
```

### Le navigateur ne s'ouvre pas
- Ouvrez manuellement votre navigateur
- Tapez dans la barre d'adresse : **`http://127.0.0.1:5000`**

### J'ai fermé la fenêtre noire par accident
- Relancez simplement `Lancer_Planning.bat` (Windows) ou `./run.sh` (Linux)
- Vos données sont intégralement préservées dans `fredo.db`

### Je veux déplacer l'application sur un autre PC
1. Copiez **tout le dossier** `PlanningMaison` sur l'autre PC (incluant `fredo.db`)
2. Relancez le script de lancement sur le nouveau PC
3. Toutes vos données sont là

---

*Bonne organisation à toute la famille !* 🏡
