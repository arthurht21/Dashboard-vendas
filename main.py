import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="🚀 Sistema de IA para Vendas",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .demo-warning {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🚀 Sistema de IA para Análise de Vendas</h1>
    <p>Dashboard Inteligente para E-commerce</p>
    <p><strong>Versão Demo - Dados Fictícios</strong></p>
</div>
""", unsafe_allow_html=True)

# Aviso de demo
st.markdown("""
<div class="demo-warning">
    <h4>🎭 Versão Demonstrativa</h4>
    <p>Este é um dashboard de demonstração com dados fictícios para mostrar as funcionalidades do sistema.</p>
    <p><strong>Para usar com seus dados reais:</strong> Execute localmente com seus arquivos Excel.</p>
</div>
""", unsafe_allow_html=True)

# Gerar dados fictícios para demo
@st.cache_data
def generate_demo_data():
    """Gerar dados fictícios para demonstração"""
    np.random.seed(42)
    
    # Dados de vendas fictícios
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    data = []
    for date in dates:
        # Simular sazonalidade
        base_orders = 50 + 30 * np.sin(2 * np.pi * date.dayofyear / 365)
        daily_orders = max(1, int(base_orders + np.random.normal(0, 10)))
        
        for _ in range(daily_orders):
            data.append({
                'date': date,
                'store_name': np.random.choice(['Loja Principal', 'Filial SP', 'Filial RJ', 'Online Store']),
                'platform': np.random.choice(['SHEIN', 'Mercado Livre', 'Shopee', 'Amazon', 'Site Próprio']),
                'product_name': np.random.choice([
                    'Smartphone Galaxy', 'Fone Bluetooth', 'Carregador Wireless',
                    'Capa de Celular', 'Película Protetora', 'Power Bank',
                    'Cabo USB-C', 'Suporte Veicular', 'Fone de Ouvido', 'Smartwatch'
                ]),
                'customer_name': f'Cliente {np.random.randint(1, 1000):03d}',
                'total_value': np.random.uniform(25, 500),
                'quantity': np.random.randint(1, 5),
                'city': np.random.choice(['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Brasília', 'Salvador']),
                'state': np.random.choice(['SP', 'RJ', 'MG', 'DF', 'BA'])
            })
    
    return pd.DataFrame(data)

# Carregar dados demo
df = generate_demo_data()

# Sidebar
st.sidebar.markdown("### 📊 Filtros")
date_range = st.sidebar.date_input(
    "📅 Período",
    value=[df['date'].min().date(), df['date'].max().date()],
    min_value=df['date'].min().date(),
    max_value=df['date'].max().date()
)

selected_platform = st.sidebar.selectbox(
    "🌐 Plataforma",
    ['Todas'] + list(df['platform'].unique())
)

# Filtrar dados
filtered_df = df.copy()
if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['date'].dt.date >= date_range[0]) & 
        (filtered_df['date'].dt.date <= date_range[1])
    ]

if selected_platform != 'Todas':
    filtered_df = filtered_df[filtered_df['platform'] == selected_platform]

# Métricas principais
st.subheader("📊 Métricas Principais")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_orders = len(filtered_df)
    st.metric("📦 Total de Pedidos", f"{total_orders:,}")

with col2:
    total_revenue = filtered_df['total_value'].sum()
    st.metric("💰 Receita Total", f"R$ {total_revenue:,.2f}")

with col3:
    avg_ticket = filtered_df['total_value'].mean()
    st.metric("🎯 Ticket Médio", f"R$ {avg_ticket:.2f}")

with col4:
    unique_customers = filtered_df['customer_name'].nunique()
    st.metric("👥 Clientes Únicos", f"{unique_customers:,}")

# Gráficos
st.subheader("📈 Análises Visuais")

col1, col2 = st.columns(2)

with col1:
    # Vendas por dia
    daily_sales = filtered_df.groupby(filtered_df['date'].dt.date)['total_value'].sum().reset_index()
    fig = px.line(daily_sales, x='date', y='total_value', 
                  title='Vendas Diárias',
                  labels={'total_value': 'Receita (R$)', 'date': 'Data'})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Vendas por plataforma
    platform_sales = filtered_df.groupby('platform')['total_value'].sum().reset_index()
    fig = px.pie(platform_sales, values='total_value', names='platform',
                 title='Receita por Plataforma')
    st.plotly_chart(fig, use_container_width=True)

# Top produtos
st.subheader("🏆 Top Produtos")
top_products = filtered_df.groupby('product_name').agg({
    'total_value': 'sum',
    'quantity': 'sum',
    'customer_name': 'nunique'
}).round(2).sort_values('total_value', ascending=False).head(10)

top_products.columns = ['Receita (R$)', 'Quantidade', 'Clientes']
st.dataframe(top_products, use_container_width=True)

# Análise geográfica
st.subheader("🗺️ Análise Geográfica")
geo_data = filtered_df.groupby(['state', 'city'])['total_value'].sum().reset_index()
geo_data = geo_data.sort_values('total_value', ascending=False).head(10)

fig = px.bar(geo_data, x='city', y='total_value', color='state',
             title='Top Cidades por Receita',
             labels={'total_value': 'Receita (R$)', 'city': 'Cidade'})
st.plotly_chart(fig, use_container_width=True)

# Informações do sistema
st.markdown("---")
st.markdown("""
### 🎯 Sobre este Dashboard

Este é um **sistema completo de análise de vendas** com inteligência artificial, desenvolvido para e-commerce.

**🚀 Funcionalidades Principais:**
- 📊 Dashboard executivo com KPIs
- 📈 Análises temporais avançadas
- 🏪 Performance por loja
- 👥 Segmentação de clientes
- 🤖 Insights com IA
- 📱 Marketing WhatsApp automatizado
- 🕷️ Monitoramento competitivo

**💡 Como usar com seus dados:**
1. Execute o sistema localmente
2. Importe seus arquivos Excel do UpSeller
3. Configure as integrações (OpenAI, WhatsApp)
4. Automatize relatórios e campanhas

---
*Desenvolvido com Python, Streamlit e ❤️*
""")
