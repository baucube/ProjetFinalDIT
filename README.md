# Prédiction de la Réussite Scolaire – Application Flask

## Description
Cette application web permet de prédire la note finale (G3) d’un élève à partir de plusieurs facteurs scolaires et socio-économiques. Elle fournit également une interprétation détaillée de la prédiction et des suggestions personnalisées pour améliorer la réussite scolaire. L’application propose des visualisations statistiques et conserve l’historique des prédictions dans une base de données SQLite.

## Fonctionnalités principales
- **Prédiction individuelle ou par lot (CSV/XLSX)**
- **Interprétation détaillée et suggestions d’amélioration**
- **Historique des prédictions**
- **Tableau de bord de reporting avec graphiques**
- **API REST pour intégration externe**

## Structure du projet
```
projet/
│   app.py                  # Application principale Flask
│   best_model.pkl          # Modèle de machine learning entraîné (pickle)
│   requirements.txt        # Dépendances Python
│   predictions.db          # Base de données SQLite
│   predictions_history.json# Historique (optionnel)
│   eleves_liste1.csv       # Exemple de fichier d’entrée CSV
│   eleves_liste2.xlsx      # Exemple de fichier d’entrée Excel
│   Presentation.pdf        # Présentation du projet
│
├── static/
│   ├── css/style.css       # Feuilles de style
│   ├── js/script.js        # Scripts JS
│   ├── education.jpg       # Images
│   └── plots/              # Graphiques générés
│
├── templates/
│   ├── base.html           # Template de base
│   ├── home.html           # Page d’accueil
│   ├── predict.html        # Formulaire de prédiction
│   ├── about.html          # À propos
│   ├── history.html        # Historique
│   └── reporting.html      # Tableau de bord
└── env/                    # Environnement virtuel Python
```

## Installation
1. **Cloner le dépôt**
2. **Créer un environnement virtuel (optionnel mais recommandé)**
   ```powershell
   python -m venv env
   .\env\Scripts\activate
   ```
3. **Installer les dépendances**
   ```powershell
   pip install -r requirements.txt
   ```
4. **Vérifier la présence du modèle**
   - Le fichier `best_model.pkl` doit être présent à la racine. Sinon, entraîner un modèle et le sauvegarder sous ce nom.

## Lancement de l’application
```powershell
python app.py
```
L’application sera accessible sur [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Utilisation
### 1. Prédiction via l’interface web
- Accéder à `/prediction` pour remplir le formulaire ou importer un fichier CSV/XLSX.
- Les résultats s’affichent avec interprétation et suggestions.

### 2. Historique
- Accéder à `/history` pour consulter toutes les prédictions passées.

### 3. Reporting
- Accéder à `/reporting` pour visualiser des graphiques statistiques :
  - Pourcentage d’élèves à risque
  - Distribution des notes
  - Analyse par sexe, temps d’étude, etc.

### 4. API REST
- Endpoint : `/predict_api` (méthode POST)
- Exemple de payload JSON :
  ```json
  {
    "sex": "F",
    "studytime": 2,
    "higher": "yes",
    "internet": "no",
    "Medu": 3,
    "G1": 12,
    "G2": 13
  }
  ```
- Réponse :
  ```json
  {
    "prediction": 13.5,
    "detailed_interpretation": "...",
    "improvement_suggestions": ["...", "..."]
  }
  ```

## Schéma de la base de données
Table `predictions` :
- `id` (int, PK)
- `timestamp` (str)
- `sex` (str)
- `studytime` (int)
- `higher` (str)
- `internet` (str)
- `medu` (int)
- `g1` (int)
- `g2` (int)
- `predicted_g3` (float)
- `detailed_interpretation` (text)
- `improvement_suggestions` (text, JSON)

## Dépendances principales
- Flask
- pandas
- numpy
- matplotlib
- seaborn
- SQLAlchemy
- scikit-learn (pour le modèle)
- openpyxl (pour lecture Excel)

## Personnalisation & extension
- **Modèle** : Remplacer `best_model.pkl` par un modèle plus performant si besoin.
- **Variables d’entrée** : Adapter le formulaire ou l’API selon les besoins.
- **Visualisations** : Ajouter de nouveaux graphiques dans `reporting`.

## Sécurité & bonnes pratiques
- Ne pas exposer l’application en mode debug en production.
- Protéger la base de données si déploiement public.
- Valider les entrées utilisateurs.

## Auteurs & contact
- Réalisé dans le cadre du module « Practical Machine Learning »
- Pour toute question, contacter l’équipe projet.
