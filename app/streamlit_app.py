import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from prophet import Prophet
import os
import datetime

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Gestion des Ruptures de Stock — Prévision & Alertes",
    layout="wide"
)

# --- CACHE DATA ---
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(BASE_DIR, "..", "data", "Historical Product Demand.csv")
    
    df = pd.read_csv(DATA_PATH)
    
    # Nettoyage
    df['Order_Demand'] = df['Order_Demand'].astype(str).str.replace(r'[^0-9-]', '', regex=True)
    df['Order_Demand'] = pd.to_numeric(df['Order_Demand'], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date', 'Order_Demand'])
    
    return df

@st.cache_data
def compute_stats(df):
    total_products = df['Product_Code'].nunique()
    
    # Top 10 produits
    top_products = df.groupby('Product_Code')['Order_Demand'].sum().sort_values(ascending=False).head(10).reset_index()
    
    # Risque de rupture (CV method)
    monthly = df.groupby([df['Date'].dt.to_period('M'), 'Product_Code'])['Order_Demand'].sum().reset_index()
    stats = monthly.groupby('Product_Code')['Order_Demand'].agg(['mean', 'std', 'sum']).dropna()
    stats['CV'] = stats['std'] / stats['mean']
    
    vol_thresh = stats['sum'].quantile(0.95)
    risky = stats[(stats['sum'] >= vol_thresh) & (stats['CV'] > 1.0)]
    nb_risky = len(risky)
    
    # Évolution globale
    timeline = df.groupby(df['Date'].dt.to_period('M'))['Order_Demand'].sum().reset_index()
    timeline['Date'] = timeline['Date'].dt.to_timestamp()
    
    return total_products, nb_risky, top_products, timeline

@st.cache_data
def run_prophet(df, product_code, periods=30):
    df_prod = df[df['Product_Code'] == product_code]
    df_daily = df_prod.groupby('Date')['Order_Demand'].sum().reset_index()
    df_prophet = df_daily.rename(columns={'Date': 'ds', 'Order_Demand': 'y'})
    
    if len(df_prophet) < 10:
        return None
        
    model = Prophet(interval_width=0.95, daily_seasonality=False, yearly_seasonality=True)
    model.fit(df_prophet)
    
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    
    return forecast

# --- SIDEBAR ---
with st.sidebar:
    st.title("Fofana Abdou")
    st.markdown("""
    Analyste Supply Chain.
    Prévision des ruptures de stock avec Prophet.
    """)
    st.divider()

st.title("Gestion des Ruptures de Stock — Prévision & Alertes")
st.markdown("---")

df = load_data()
total_products, nb_risky, top_products, timeline = compute_stats(df)

tab1, tab2, tab3 = st.tabs(["Vue Globale", "Prévisions & Alertes", "Simulateur de Stock"])

# --- ONGLET 1 : VUE GLOBALE ---
with tab1:
    col1, col2 = st.columns(2)
    col1.metric("Total de Produits Analysés", f"{total_products:,}")
    col2.metric("Produits à Haut Risque de Rupture (Alerte)", f"{nb_risky:,}")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Top 10 Produits (Volume de Demande)")
        fig1 = px.bar(top_products, x='Order_Demand', y='Product_Code', orientation='h', color='Order_Demand', color_continuous_scale='Blues')
        fig1.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig1, use_container_width=True)
        
    with c2:
        st.subheader("Évolution Mensuelle Globale")
        fig2 = px.line(timeline, x='Date', y='Order_Demand')
        st.plotly_chart(fig2, use_container_width=True)

# --- ONGLET 2 : PREVISIONS & ALERTES ---
with tab2:
    st.subheader("Prévisions Météo des Ventes (Prophet)")
    
    # On propose seulement le top 20 pour éviter de tout recalculer
    top_20 = df.groupby('Product_Code')['Order_Demand'].sum().sort_values(ascending=False).head(20).index.tolist()
    selected_prod = st.selectbox("Choisissez un produit à analyser :", top_20)
    
    forecast = run_prophet(df, selected_prod, periods=30)
    
    if forecast is not None:
        last_historical_date = df['Date'].max()
        future_forecast = forecast[forecast['ds'] > last_historical_date].head(30)
        
        expected_demand = future_forecast['yhat'].sum()
        max_demand = future_forecast['yhat_upper'].sum()
        safety_stock = max_demand - expected_demand
        
        c_a, c_b, c_c = st.columns(3)
        c_a.metric("Demande Prévue (30j)", f"{expected_demand:,.0f}")
        c_b.metric("Stock de Sécurité", f"{safety_stock:,.0f}")
        c_c.metric("Stock Minimum Recommandé", f"{(expected_demand + safety_stock):,.0f}")
        
        # Graphique Prophet
        fig_proph = go.Figure()
        
        # Intervalle de confiance
        fig_proph.add_trace(go.Scatter(
            x=forecast['ds'].tolist() + forecast['ds'].tolist()[::-1],
            y=forecast['yhat_upper'].tolist() + forecast['yhat_lower'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(52, 152, 219, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Intervalle de Confiance 95%'
        ))
        
        # Prévision moyenne
        fig_proph.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat'],
            mode='lines',
            line=dict(color='#2980b9', width=2),
            name='Prévision Moyenne'
        ))
        
        fig_proph.update_layout(title=f"Prévisions pour {selected_prod}", hovermode="x")
        st.plotly_chart(fig_proph, use_container_width=True)

# --- ONGLET 3 : SIMULATEUR ---
with tab3:
    st.subheader("Simulateur de Rupture & Réapprovisionnement")
    st.write(f"Basé sur les 30 prochains jours du produit **{selected_prod}**.")
    
    if forecast is not None:
        c1, c2, c3 = st.columns(3)
        with c1:
            stock_actuel = st.slider("Niveau de Stock Actuel (unités)", 0, int(max_demand * 1.5), int(expected_demand))
        with c2:
            lead_time = st.slider("Délai de Réapprovisionnement (Jours)", 1, 30, 7)
        with c3:
            service_level = st.slider("Niveau de Service Cible (%)", 50, 99, 95)
            
        # Simulation basique
        # On extrait la demande journalière moyenne sur le futur proche
        daily_demand = expected_demand / 30
        daily_std = (safety_stock / 30) / 1.645 # Approximation de l'écart-type
        
        # Z-score simple
        z_score_dict = {50: 0.0, 80: 0.84, 90: 1.28, 95: 1.645, 99: 2.33}
        # Interpolation simple du z_score
        z = z_score_dict.get(service_level, 1.645) 
        
        # Nouveau stock de sécurité basé sur le lead time
        sim_safety_stock = z * daily_std * np.sqrt(lead_time)
        reorder_point = (daily_demand * lead_time) + sim_safety_stock
        
        days_until_empty = stock_actuel / daily_demand if daily_demand > 0 else 999
        
        st.divider()
        col_res1, col_res2, col_res3 = st.columns(3)
        
        col_res1.metric("Point de Commande (Reorder Point)", f"{reorder_point:,.0f} unités", help="Déclencher une commande si le stock tombe sous ce seuil")
        col_res2.metric("Stock de Sécurité Requis", f"{sim_safety_stock:,.0f} unités")
        
        if stock_actuel <= reorder_point:
            col_res3.error(f"🚨 ALERTE : COMMANDER IMMÉDIATEMENT")
        else:
            col_res3.success(f"✅ STOCK SAIN")
            
        st.info(f"Si vous ne commandez rien, rupture estimée dans **{days_until_empty:.1f} jours**.")
