import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuración de la Página Web
st.set_page_config(page_title="La Quesera | BI & Analytics", page_icon="🧀", layout="wide")

# Estilo Personalizado CSS (Tema Artesanal / Ejecutivo)
st.markdown("""
    <style>
    .stApp {
        background-color: #F8F9FA;
    }
    h1, h2, h3 {
        color: #1E293B;
        font-family: 'Segoe UI', sans-serif;
    }
    /* Tarjetas de métricas */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border-left: 5px solid #D97706;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    div[data-testid="stMetricValue"] {
        color: #0F172A;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Carga de Datos Ampliada
@st.cache_data
def load_data():
    df_quesos = pd.DataFrame({
        'Variedad': ['Oaxaca', 'Manchego', 'Gouda', 'Panela', 'Brie', 'Cheddar'],
        'Categoria': ['Fresco', 'Madurado', 'Madurado', 'Fresco', 'Blando', 'Madurado'],
        'Precio_Kg': [160, 220, 250, 120, 340, 280],
        'Kg_Vendidos': [4200, 3100, 2400, 5100, 1100, 1800],
        'Margen': [0.35, 0.40, 0.42, 0.28, 0.48, 0.45]
    })
    df_quesos['Ingresos'] = df_quesos['Precio_Kg'] * df_quesos['Kg_Vendidos']
    df_quesos['Utilidad_Neta'] = df_quesos['Ingresos'] * df_quesos['Margen']
    
    df_tendencia = pd.DataFrame({
        'Mes': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio'],
        'Ventas': [185000, 192000, 210000, 205000, 230000, 250000],
        'IC_Inf': [172000, 180000, 195000, 190000, 215000, 232000],
        'IC_Sup': [198000, 204000, 225000, 220000, 245000, 268000]
    })
    return df_quesos, df_tendencia

df_quesos, df_tendencia = load_data()

# ==========================================
# BARRA LATERAL: FILTROS Y CONSULTAS
# ==========================================
st.sidebar.header("🔍 Panel de Filtros y Consultas")

# Filtro 1: Categoría
categorias_disp = df_quesos['Categoria'].unique().tolist()
cat_seleccionadas = st.sidebar.multiselect(
    "Filtrar por Categoría:",
    options=categorias_disp,
    default=categorias_disp
)

# Filtro 2: Variedad específica
variedades_disp = df_quesos[df_quesos['Categoria'].isin(cat_seleccionadas)]['Variedad'].tolist()
var_seleccionadas = st.sidebar.multiselect(
    "Filtrar por Variedad de Queso:",
    options=variedades_disp,
    default=variedades_disp
)

# Filtro 3: Rango de Precio
min_p, max_p = int(df_quesos['Precio_Kg'].min()), int(df_quesos['Precio_Kg'].max())
rango_precio = st.sidebar.slider(
    "Rango de Precio por Kg ($):",
    min_value=min_p, max_value=max_p, value=(min_p, max_p)
)

# Filtro 4: Meses para tendencia
meses_disp = df_tendencia['Mes'].tolist()
meses_seleccionados = st.sidebar.select_slider(
    "Periodo de Tendencia Mensual:",
    options=meses_disp,
    value=(meses_disp[0], meses_disp[-1])
)

# Aplicar filtros al DataFrame de Quesos
df_filtrado = df_quesos[
    (df_quesos['Categoria'].isin(cat_seleccionadas)) &
    (df_quesos['Variedad'].isin(var_seleccionadas)) &
    (df_quesos['Precio_Kg'].between(rango_precio[0], rango_precio[1]))
]

# Aplicar filtro de meses
idx_inicio = meses_disp.index(meses_seleccionados[0])
idx_fin = meses_disp.index(meses_seleccionados[1])
df_tendencia_filtrada = df_tendencia.iloc[idx_inicio:idx_fin+1]

# ==========================================
# CUERPO PRINCIPAL
# ==========================================
st.title("Quesos Artesanales 'La Quesera'")
st.caption("Panel Interactivo de Inteligencia de Negocios y Rendimiento Comercial")

# Validación por si los filtros dejan la tabla vacía
if df_filtrado.empty:
    st.warning("No hay productos que coincidan con los filtros seleccionados. Ajusta los parámetros en la barra lateral.")
    st.stop()

# 3. KPIs Dinámicos
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ingresos Seleccionados", f"${df_filtrado['Ingresos'].sum():,.2f}")
col2.metric("Utilidad Estimada", f"${df_filtrado['Utilidad_Neta'].sum():,.2f}")
col3.metric("Volumen Vendido", f"{df_filtrado['Kg_Vendidos'].sum():,} Kg")
col4.metric("Margen Promedio", f"{df_filtrado['Margen'].mean()*100:.1f}%")

st.write("") # Espaciado

# 4. Organización por Pestañas
tab_graficos, tab_tabla, tab_consulta = st.tabs([
    "📊 Análisis Visual", 
    "📋 Tabla de Datos y Exportación", 
    "🔎 Consulta Rápida por Producto"
])

# --- PESTAÑA 1: GRÁFICOS ---
with tab_graficos:
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Ingresos por Variedad ($)")
        fig_bar = px.bar(
            df_filtrado.sort_values('Ingresos'), 
            x='Ingresos', y='Variedad', 
            color='Categoria',
            orientation='h', text_auto='$.2s',
            color_discrete_map={'Fresco': '#0284C7', 'Madurado': '#D97706', 'Blando': '#10B981'}
        )
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            legend_title_text='Categoría'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.subheader("Evolución Mensual e Incertidumbre (IC 95%)")
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=df_tendencia_filtrada['Mes'].tolist() + df_tendencia_filtrada['Mes'].tolist()[::-1],
            y=df_tendencia_filtrada['IC_Sup'].tolist() + df_tendencia_filtrada['IC_Inf'].tolist()[::-1],
            fill='toself', fillcolor='rgba(217, 119, 6, 0.18)',
            line=dict(color='rgba(255,255,255,0)'), name='Banda de Confianza (95%)'
        ))
        fig_line.add_trace(go.Scatter(
            x=df_tendencia_filtrada['Mes'], y=df_tendencia_filtrada['Ventas'],
            mode='lines+markers', 
            line=dict(color='#B45309', width=3),
            marker=dict(size=8, color='#1E293B'),
            name='Ventas Reales'
        ))
        fig_line.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            hovermode="x unified"
        )
        st.plotly_chart(fig_line, use_container_width=True)

# --- PESTAÑA 2: TABLA INTERACTIVA ---
with tab_tabla:
    st.subheader("Detalle de Inventario y Rentabilidad")
    
    # Buscador de texto rápido
    busqueda = st.text_input("Buscar por nombre o categoría:", placeholder="Ej. Manchego, Madurado...")
    df_tabla = df_filtrado.copy()
    if busqueda:
        df_tabla = df_tabla[
            df_tabla['Variedad'].str.contains(busqueda, case=False) | 
            df_tabla['Categoria'].str.contains(busqueda, case=False)
        ]
    
    # Formato visual de tabla
    st.dataframe(
        df_tabla.style.format({
            'Precio_Kg': '${:,.2f}',
            'Kg_Vendidos': '{:,} Kg',
            'Margen': '{:.1%}',
            'Ingresos': '${:,.2f}',
            'Utilidad_Neta': '${:,.2f}'
        }),
        use_container_width=True
    )
    
    # Botón de descarga CSV
    csv = df_tabla.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Descargar consulta en CSV",
        data=csv,
        file_name='consulta_queseria.csv',
        mime='text/csv',
    )

# --- PESTAÑA 3: CONSULTA INDIVIDUAL Y SIMULADOR ---
with tab_consulta:
    st.subheader("Ficha Técnica y Simulador de Ventas")
    queso_sel = st.selectbox("Selecciona una variedad para inspeccionar:", df_quesos['Variedad'])
    datos_q = df_quesos[df_quesos['Variedad'] == queso_sel].iloc[0]
    
    c1, c2 = st.columns([1, 1])
    with c1:
        st.info(f"""
        **Ficha del Producto: Queso {datos_q['Variedad']}**
        * **Categoría:** {datos_q['Categoria']}
        * **Precio actual por Kg:** ${datos_q['Precio_Kg']:,.2f}
        * **Volumen histórico:** {datos_q['Kg_Vendidos']:,} Kg
        * **Margen de ganancia:** {datos_q['Margen']*100:.0f}%
        * **Utilidad total generada:** ${datos_q['Utilidad_Neta']:,.2f}
        """)
    with c2:
        st.write("**Simulador de Pedido / Proyección**")
        kg_sim = st.number_input("Ingresa cantidad de Kilogramos a cotizar:", min_value=1, value=100, step=10)
        total_venta = kg_sim * datos_q['Precio_Kg']
        ganancia_sim = total_venta * datos_q['Margen']
        st.success(f"**Total Cotización:** ${total_venta:,.2f} MXN  \n**Ganancia Neta Estimada:** ${ganancia_sim:,.2f} MXN")