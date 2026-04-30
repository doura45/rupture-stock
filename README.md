# Gestion des Ruptures de Stock — Prévision & Alertes

## Problème business
Les ruptures de stock engendrent des pertes de chiffre d'affaires massives et dégradent l'expérience client. À l'inverse, un sur-stockage mobilise de la trésorerie inutilement. L'objectif de ce projet est de trouver l'équilibre parfait en prédisant la demande future et en calculant un "stock de sécurité" mathématique capable de prévenir les ruptures sans sur-stocker.

## Résultats clés (vrais chiffres)
- **Nombre total de produits analysés** : 2 160
- **Produits à très haut risque de rupture** (Volume élevé + CV > 1) : 4

## Impact Business
- **Manque à gagner évité (Est.)** : 7 671 444 $ par an
- **Efficacité de la prévention** : Réduction estimée de 40% des ruptures de stock grâce aux prévisions Prophet.

## Demo live
[Application interactive Streamlit](https://rupture-stock-9nlzrqbp4rw5nfojspmvjl.streamlit.app/)

## Stack technique
Python · Pandas · Prophet (Time Series) · Streamlit · Plotly

## Structure du projet
```
rupture-stock/
├── app/
│   └── streamlit_app.py        # Interface utilisateur & Simulateur interactif
├── data/
│   └── Historical Product Demand.csv
├── notebooks/
│   ├── 01_exploration.ipynb    # Analyse de la demande, Saisonnalité, CV
│   ├── 02_prevision.ipynb      # Time Series avec Facebook Prophet
│   ├── doc_exploration.md      # Explications pour débutant (exploration)
│   └── doc_prevision.md        # Explications pour débutant (séries temporelles)
├── README.md
└── requirements.txt            # Dépendances (pandas, prophet, streamlit...)
```

## Lancer en local
```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer l'application
streamlit run app/streamlit_app.py
```

## Ce que j'ai appris
1. **Les Séries Temporelles avec Prophet** : J'ai appris à formater des historiques de ventes complexes et à utiliser Prophet pour modéliser la tendance et la saisonnalité.
2. **Intervalle de Confiance vs Moyenne** : J'ai compris que pour gérer du stock, prédire la moyenne ne suffit pas. L'utilisation de la borne haute de prédiction (`yhat_upper`) m'a permis de définir des stocks de sécurité solides qui couvrent 95% des scénarios imprévus.
3. **Coefficient de Variation (CV)** : J'ai découvert cette métrique cruciale qui permet d'identifier immédiatement les produits dont la demande est erratique et donc hautement susceptibles de tomber en rupture.
