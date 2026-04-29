import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from prophet import Prophet
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Gestion des Stocks — Fofana Abdou",
    layout="wide"
)

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data
def charger_donnees():
    # Définition du chemin vers le dataset de demande historique
    dossier_actuel = os.path.dirname(__file__)
    chemin_data = os.path.join(dossier_actuel, "..", "data", "Historical Product Demand.csv")
    
    df = pd.read_csv(chemin_data)
    
    # Nettoyage des données (essentiel en Data Analysis)
    # On retire les parenthèses souvent présentes dans les chiffres de ce dataset
    df['Order_Demand'] = df['Order_Demand'].astype(str).str.replace('(', '').str.replace(')', '')
    df['Order_Demand'] = pd.to_numeric(df['Order_Demand'], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # On supprime les lignes vides
    return df.dropna()

# --- FONCTION DE PRÉVISION (Utilisation de Prophet) ---
def calculer_prevision(df_produit, jours_futurs=30):
    # Prophet nécessite deux colonnes spécifiques : 'ds' (date) et 'y' (valeur)
    df_prep = df_produit.groupby('Date')['Order_Demand'].sum().reset_index()
    df_prep.columns = ['ds', 'y']
    
    # On vérifie s'il y a assez de données pour une prédiction fiable
    if len(df_prep) < 30:
        return None
        
    # Initialisation du modèle Prophet (très efficace pour capturer la saisonnalité)
    model = Prophet(yearly_seasonality=True, daily_seasonality=False, weekly_seasonality=True)
    model.fit(df_prep)
    
    # Création du futur et prédiction
    futur = model.make_future_dataframe(periods=jours_futurs)
    prediction = model.predict(futur)
    
    return prediction

# Exécution du chargement
try:
    df = charger_donnees()
except Exception as e:
    st.error(f"Erreur de chargement des données : {e}")
    st.stop()

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("Fofana Abdou")
    st.write("Analyste Supply Chain")
    st.markdown("---")
    st.write("Ce projet vise à prédire la demande de produits pour optimiser les niveaux de stock.")

# --- TITRE PRINCIPAL ---
st.title("Supply Chain — Prévision des Ruptures de Stock")
st.markdown("---")

# --- ONGLETS ---
tab1, tab2, tab3 = st.tabs(["État du Stock", "Prévisions de Demande", "Simulateur de Réapprovisionnement"])

# --- ONGLET 1 : ÉTAT DU STOCK ---
with tab1:
    # --- SECTION IMPACT FINANCIER (Ajoutée par mes soins) ---
    st.markdown("---")
    st.subheader("Impact Financier de la Prévention")
    
    # Hypothèses business pour l'analyse
    total_unites = df['Order_Demand'].sum()
    prix_moyen_unite = 25  # Estimation
    manque_a_gagner_sans_modele = total_unites * 0.10 * prix_moyen_unite # 10% de rupture sans prévision
    reduction_rupture = 0.40 # Le modèle permet de réduire les ruptures de 40%
    gain_financier = manque_a_gagner_sans_modele * reduction_rupture

    col1, col2, col3 = st.columns(3)
    col1.metric("Volume Total Annuel", f"{total_unites:,.0f}")
    col2.metric("Manque à gagner évité (Est.)", f"${gain_financier:,.0f}", delta=f"+{reduction_rupture*100:.0f}% d'efficacité")
    col3.write(f"**Analyse :** En anticipant mieux la demande, j'estime que nous pouvons éviter une perte de **${gain_financier:,.0f}** par an en réduisant les ruptures de stock de 40%.")
    st.markdown("---")

    col_a, col_b = st.columns(2)
    
    # Top 10 des produits les plus demandés (en volume)
    top_produits = df.groupby('Product_Code')['Order_Demand'].sum().sort_values(ascending=False).head(10).reset_index()
    
    with col_a:
        st.subheader("Top 10 Produits (Volume Total)")
        fig1 = px.bar(top_produits, x='Order_Demand', y='Product_Code', 
                     orientation='h', color='Order_Demand',
                     labels={'Order_Demand': 'Demande Totale', 'Product_Code': 'Code Produit'})
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_b:
        st.subheader("Tendance Globale de la Demande")
        # Groupement par mois pour voir l'évolution
        evol_mensuelle = df.groupby(df['Date'].dt.to_period('M'))['Order_Demand'].sum().reset_index()
        evol_mensuelle['Date'] = evol_mensuelle['Date'].dt.to_timestamp()
        
        fig2 = px.line(evol_mensuelle, x='Date', y='Order_Demand',
                      title="Évolution de la demande au fil du temps")
        st.plotly_chart(fig2, use_container_width=True)

# --- ONGLET 2 : PRÉVISIONS DE DEMANDE ---
with tab2:
    st.subheader("Anticiper les ventes futures")
    st.write("Sélectionnez un produit pour lancer l'algorithme de prédiction Prophet.")
    
    liste_top_produits = top_produits['Product_Code'].tolist()
    produit_selectionne = st.selectbox("Produit à analyser :", liste_top_produits)
    
    if st.button("Lancer l'analyse prédictive"):
        df_p = df[df['Product_Code'] == produit_selectionne]
        
        with st.spinner("Analyse des tendances historiques..."):
            pred = calculer_prevision(df_p)
            
            if pred is not None:
                # Affichage du graphique de prédiction (Prophet)
                # 'yhat' est la valeur prédite par le modèle
                fig3 = px.line(pred, x='ds', y='yhat', 
                              title=f"Prévision de la demande pour {produit_selectionne} (30 prochains jours)",
                              labels={'ds': 'Date', 'yhat': 'Demande Estimée'})
                st.plotly_chart(fig3, use_container_width=True)
                
                # Calcul du volume total prévu sur le prochain mois
                volume_prevu = pred.iloc[-30:]['yhat'].sum()
                st.info(f"### Résultat : Demande totale estimée sur 30 jours = **{int(volume_prevu)} unités**")
            else:
                st.warning("Données insuffisantes pour générer une prédiction fiable sur ce produit.")

# --- ONGLET 3 : SIMULATEUR DE RÉAPPROVISIONNEMENT ---
with tab3:
    st.subheader("Calculer mon Point de Commande")
    st.write("Utilisez cet outil pour savoir quand passer votre prochaine commande fournisseur.")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        v_jour = st.number_input("Ventes moyennes journalières", 1, 5000, 100)
    with c2:
        d_livraison = st.number_input("Délai de livraison (en jours)", 1, 90, 7)
    with c3:
        s_securite = st.number_input("Stock de sécurité souhaité", 0, 10000, 200)
        
    # --- FORMULE DE SUPPLY CHAIN (Simple et explicite) ---
    # Point de Commande = (Ventes par jour * Délai de livraison) + Stock de sécurité
    point_de_commande = (v_jour * d_livraison) + s_securite
    
    st.markdown("---")
    st.markdown(f"### Seuil d'alerte : **{point_de_commande} unités**")
    st.write(f"""
    **Explication :** 
    - Vous vendez {v_jour} unités par jour.
    - Votre fournisseur met {d_livraison} jours à livrer (soit {v_jour * d_livraison} unités vendues pendant l'attente).
    - Avec un stock de sécurité de {s_securite} unités, vous devez commander dès que votre stock descend à **{point_de_commande}**.
    """)
    
    if point_de_commande > 1000:
        st.warning("Attention : Le seuil est élevé, assurez-vous d'avoir la capacité de stockage nécessaire.")

# --- FOOTER ---
st.markdown("---")
st.caption("Projet Supply Chain & Forecasting — Fofana Abdou")
