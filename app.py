import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Superstore DS Portfolio",
    page_icon="📊",
    layout="wide"
)

# --- CUSTOM CSS UNTUK TAMPILAN MODERN ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border-left: 5px solid #636EFA;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .stPlotlyChart {
        background-color: #ffffff;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    # Gunakan r'' untuk menghindari unicode error pada path windows
    df = pd.read_excel(r"data\superstore_dataset.xlsx")
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df

df = load_data()

# --- SIDEBAR NAVIGASI ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/6821/6821005.png", width=100)
    st.title("Data Portfolio")
    halaman = st.radio("Pilih Menu:", ["👤 My Profile", "📈 Business Dashboard", "🔍 Deep Dive Data"])
    st.markdown("---")
    st.write("**Contact:**")
    st.write("📧 mellymarceliaaziza@gmail.com")

# --- HALAMAN 1: PROFIL ---
if halaman == "👤 My Profile":
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        # Gunakan path file foto kamu
        st.image(r"assets\20191003_blog_scoping_a_data_science_project_in_a_smarter_way_website.png", use_container_width=True)
    
    with col2:
        st.title("Hi, I'm MELLY MARCELIA AZIZA 👋")
        st.subheader("Data Science Bootcamp Student")
        st.write("""
        Selamat datang di portofolio saya! Project ini merupakan bukti kemampuan saya dalam 
        mengolah data mentah menjadi dashboard interaktif yang siap digunakan oleh bisnis 
        untuk pengambilan keputusan strategis berbasis data.
        """)
        
        st.info("**Main Skills:** Python, Streamlit, SQL, Machine Learning Analysis")
        
        st.markdown("### 🏆 Project Highlights")
        st.write("✅ **End-to-End Analysis:** Dari data mentah hingga visualisasi interaktif.")
        st.write("✅ **Business Insight:** Mengidentifikasi kategori produk paling menguntungkan.")
        st.write("✅ **Data Cleaning:** Menangani format tanggal dan pembersihan kolom.")

# --- HALAMAN 2: DASHBOARD ---
elif halaman == "📈 Business Dashboard":
    st.title("📊 Superstore Business Insight")
    
    # FILTER ROW
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_a:
        region_filter = st.multiselect("Filter Wilayah:", df['region'].unique(), default=df['region'].unique())
    with col_b:
        category_filter = st.multiselect("Filter Kategori:", df['category'].unique(), default=df['category'].unique())
    with col_c:
        # TAMBAHAN: Filter Segment agar lebih keren
        segment_filter = st.multiselect("Filter Segmen:", df['segment'].unique(), default=df['segment'].unique())

    # Filter Logic
    df_filtered = df[(df['region'].isin(region_filter)) & 
                     (df['category'].isin(category_filter)) & 
                     (df['segment'].isin(segment_filter))]

    # METRIC CARDS
    m1, m2, m3, m4 = st.columns(4)
    total_sales = df_filtered['sales'].sum()
    total_profit = df_filtered['profit'].sum()
    total_qty = df_filtered['quantity'].sum()
    avg_discount = df_filtered['discount'].mean()

    m1.metric("Total Sales", f"${total_sales:,.0f}")
    m2.metric("Total Profit", f"${total_profit:,.0f}", f"{ (total_profit/total_sales)*100:.1f}% Margin")
    m3.metric("Items Sold", f"{total_qty:,}")
    m4.metric("Avg Discount", f"{avg_discount:.1%}")

    st.markdown("---")

    # CHARTS ROW 1
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("📅 Sales Trend & Moving Average")
        df_time = df_filtered.set_index('order_date').resample('M')['sales'].sum().reset_index()
        # Tambahkan Moving Average untuk analisis tren
        df_time['moving_avg'] = df_time['sales'].rolling(window=3).mean()
        
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=df_time['order_date'], y=df_time['sales'], name='Bulanan', line=dict(color='#636EFA', width=2)))
        fig_line.add_trace(go.Scatter(x=df_time['order_date'], y=df_time['moving_avg'], name='Tren (3 bln)', line=dict(color='#EF553B', width=2, dash='dash')))
        
        fig_line.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_line, use_container_width=True)

    with c2:
        st.subheader("📦 Sales by Category")
        fig_pie = px.pie(df_filtered, values='sales', names='category', hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)

    # CHARTS ROW 2
    col_d, col_e = st.columns(2)
    
    with col_d:
        st.subheader("🗺️ Profitability Analysis per State")
        fig_bar = px.bar(df_filtered.groupby('state')['profit'].sum().reset_index().sort_values('profit', ascending=False).head(10), 
                         x='profit', y='state', orientation='h', color='profit',
                         color_continuous_scale='RdYlGn')
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_e:
        # TAMBAHAN: Analisis Sub-Kategori paling rugi (untuk insight bisnis)
        st.subheader("⚠️ Top 10 Sub-Categories by Loss")
        loss_data = df_filtered.groupby('subcategory')['profit'].sum().reset_index().sort_values('profit').head(10)
        fig_loss = px.bar(loss_data, x='profit', y='subcategory', orientation='h', color_discrete_sequence=['#EF553B'])
        st.plotly_chart(fig_loss, use_container_width=True)

# --- HALAMAN 3: DEEP DIVE ---
elif halaman == "🔍 Deep Dive Data":
    st.title("🔍 Data Exploration")
    
    # TAMBAHAN: Tab untuk memisahkan data mentah dan top customer
    tab1, tab2 = st.tabs(["📄 Raw Data", "🏆 Top Performance"])
    
    with tab1:
        st.write("Gunakan tabel ini untuk melihat detail setiap transaksi.")
        search = st.text_input("Cari Nama Produk:")
        df_display = df[df['product_name'].str.contains(search, case=False)] if search else df
        st.dataframe(df_display, use_container_width=True)
        
        csv = df_display.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Data", data=csv, file_name="superstore_filtered.csv", mime="text/csv")
        
    with tab2:
        col_x, col_y = st.columns(2)
        with col_x:
            st.subheader("👤 Top 10 Customers")
            top_cust = df.groupby('customer_name')['sales'].sum().reset_index().sort_values('sales', ascending=False).head(10)
            st.table(top_cust)
        with col_y:
            st.subheader("🔥 Top 10 Products")
            top_prod = df.groupby('product_name')['sales'].sum().reset_index().sort_values('sales', ascending=False).head(10)

            st.table(top_prod)
