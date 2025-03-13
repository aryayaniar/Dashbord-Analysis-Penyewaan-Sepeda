import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import streamlit as st
import os

sns.set(style='darkgrid')

# ==============================
# KONFIGURASI DASAR
# ==============================
st.set_page_config(page_title="🚲 Bike Share Insights", layout="wide", page_icon="🚴")

# Path handling
def file_path(filename):
    paths = [
        f"dashboard/{filename}",
        filename
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    st.error(f"File {filename} tidak ditemukan!")
    st.stop()

# Memuat data
@st.cache_data
def load_data():
    try:
        data = pd.read_csv(file_path('df_day.csv'))
        data['dteday'] = pd.to_datetime(data['dteday'])
        return data
    except Exception as e:
        st.error(f"Gagal memuat data: {str(e)}")
        st.stop()

# ==============================
# SIDEBAR
# ==============================
with st.sidebar:
    st.title("📌 Informasi Pengembang")
    st.markdown("**• 👤 Arya Yanimaharta**")
    st.markdown("**• 🆔 MC007D5Y0407**")
    st.markdown("**• 📧 [111202113744@mhs.dinus.ac.id](mailto:111202113744@mhs.dinus.ac.id)**")
    st.image(file_path('rent bike.jpg'), width=250, caption="Sistem Penyewaan Sepeda")
    
    # Date filter
    
    min_date = pd.to_datetime(load_data()['dteday'].min())
    max_date = pd.to_datetime(load_data()['dteday'].max())
    selected_dates = st.date_input(
        "🗓️ Pilih Rentang Waktu",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

# ==============================
# FUNGSI UTAMA
# ==============================
def main():
    # Memproses filter tanggal
    start_date, end_date = pd.to_datetime(selected_dates)
    filtered_data = load_data()[
        (load_data()['dteday'] >= start_date) & 
        (load_data()['dteday'] <= end_date)
    ]
    
    # Validasi data kosong
    if filtered_data.empty:
        st.warning("⚠️ Tidak ada data dalam rentang tanggal yang dipilih")
        return
    
    # ==============================
    # VISUALISASI INTERAKTIF
    # ==============================
    st.title("📊 Dashboard Analisis Penyewaan Sepeda")
    st.markdown("---")
    
    # Metrics cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Penyewaan", filtered_data['cnt'].sum())
    with col2:
        st.metric("Rata-rata Harian", f"{filtered_data['cnt'].mean():.0f}")
    with col3:
        st.metric("Puncak Penyewaan", filtered_data['cnt'].max())
    st.markdown("---")
    
    # Chart 1: Tren Bulanan
    monthly = filtered_data.resample('M', on='dteday').agg({'cnt':'sum'}).reset_index()
    fig1 = px.area(
        monthly,
        x='dteday',
        y='cnt',
        title="📈 Tren Penyewaan Bulanan",
        labels={'cnt': 'Total Penyewaan', 'dteday': 'Bulan'},
        color_discrete_sequence=['#1f77b4']
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Chart 2: Distribusi Musiman
    season_order = ['Spring', 'Summer', 'Fall', 'Winter']
    seasonal = filtered_data.groupby('season', observed=True)['cnt'].sum().reindex(season_order).reset_index()
    fig2 = px.bar(
        seasonal,
        x='season',
        y='cnt',
        title="🌦️ Distribusi Musiman",
        labels={'cnt': 'Total Penyewaan', 'season': 'Musim'},
        color='season',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # Chart 3: Perbandingan Hari
    day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    daily = filtered_data.groupby(filtered_data['dteday'].dt.day_name())['cnt'].sum().reindex(day_order).reset_index()
    fig3 = px.line(
        daily,
        x='dteday',
        y='cnt',
        title="📅 Pola Harian",
        labels={'cnt': 'Total Penyewaan', 'dteday': 'Hari'},
        markers=True
    )
    st.plotly_chart(fig3, use_container_width=True)

if __name__ == "__main__":
    main()