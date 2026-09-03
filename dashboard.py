import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Americano Sosial - BPS Kepri",
    page_icon="📊",
    layout="wide"
)

# 1. PETA INDIKATOR: Menghubungkan nama indikator dengan Sheet dan Kolomnya di Google Sheet
INDIKATOR_MAP = {
    "Tingkat Pengangguran Terbuka (TPT)": {"sheet": "TPT_TPAK", "kolom": "Nilai_TPT", "satuan": "%"},
    "Tingkat Partisipasi Angkatan Kerja (TPAK)": {"sheet": "TPT_TPAK", "kolom": "Nilai_TPAK", "satuan": "%"},
    "Jumlah Angkatan Kerja": {"sheet": "Level_Provinsi", "kolom": "Jumlah_angkatan_kerja", "satuan": "Ribu Orang"},
    "Jumlah Bekerja": {"sheet": "Level_Provinsi", "kolom": "Jumlah_bekerja", "satuan": "Ribu Orang"},
    "Jumlah Pengangguran": {"sheet": "Level_Provinsi", "kolom": "Jumlah_pengangguran", "satuan": "Ribu Orang"}
}

@st.cache_data(ttl=3600)
def load_fast_data(sheet_id, sheet_name):
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(csv_url)
    
    # [SMART CLEANSER] Membersihkan format angka (ribuan dengan koma atau desimal dengan koma)
    for col in df.columns:
        if col not in ['Tahun', 'Periode', 'Kabupaten_kota']:
            if df[col].dtype == 'object':
                # Jika ada koma DAN titik (misal 1,057.92), hilangkan koma ribuan
                # Jika hanya koma (misal 6,94), ubah koma menjadi titik desimal
                df[col] = df[col].apply(lambda x: str(x).replace(',', '') if '.' in str(x) else str(x).replace(',', '.'))
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
    def get_month_order(month_str):
        month_str = str(month_str).lower()
        if month_str == 'februari': return 1
        elif month_str == 'mei': return 2
        elif month_str == 'agustus': return 3
        elif month_str == 'november': return 4
        return 5
            
    if 'Periode' in df.columns and 'Tahun' in df.columns:
        df['Urutan_Bulan'] = df['Periode'].apply(get_month_order)
        if 'Kabupaten_kota' in df.columns:
            df = df.sort_values(by=['Tahun', 'Urutan_Bulan', 'Kabupaten_kota']).reset_index(drop=True)
        else:
            df = df.sort_values(by=['Tahun', 'Urutan_Bulan']).reset_index(drop=True)
        
        df['Label_Waktu'] = df['Periode'].astype(str).str[:3] + " " + df['Tahun'].astype(str)
    
    return df

SHEET_ID = "1aUSp4yJYQRBDlb0WDURTgAUFdn45uJWdwUKfUhpeq74"

# --- SIDEBAR ---
st.sidebar.title("🦅 Kopasus Tim Sosial")
st.sidebar.markdown("**BPS Provinsi Kepulauan Riau**")

if st.sidebar.button("🔄 Segarkan Data Terbaru", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.divider()
st.sidebar.header("🎯 Filter Visualisasi")

# Pilihan Indikator ditarik otomatis dari PETA INDIKATOR di atas
indikator_pilihan = st.sidebar.selectbox(
    "1. Pilih Indikator Sakernas:",
    options=list(INDIKATOR_MAP.keys())
)

# Konfigurasi aktif berdasarkan indikator yang dipilih
konfig = INDIKATOR_MAP[indikator_pilihan]
nama_sheet = konfig["sheet"]
kolom_target = konfig["kolom"]
satuan = konfig["satuan"]

try:
    with st.spinner(f'Menarik data {nama_sheet}...'):
        data = load_fast_data(SHEET_ID, nama_sheet)
    
    periode_pilihan = st.sidebar.selectbox(
        "2. Pilih Periode Rilis:",
        options=["Semua Periode", "Agustus saja", "Februari saja", "November saja", "Mei saja"]
    )
    
    # [LOGIKA SMART FILTER WILAYAH]
    if 'Kabupaten_kota' in data.columns:
        daftar_wilayah = data['Kabupaten_kota'].unique().tolist()
        wilayah_pilihan = st.sidebar.multiselect(
            "3. Bandingkan Wilayah:",
            options=daftar_wilayah,
            default=["Kepulauan Riau"] if "Kepulauan Riau" in daftar_wilayah else daftar_wilayah[0]
        )
        filtered_df = data[data['Kabupaten_kota'].isin(wilayah_pilihan)]
    else:
        filtered_df = data.copy()
        # Memberikan informasi visual kepada pengguna mengapa filter wilayah hilang
        st.sidebar.info("💡 Filter wilayah disembunyikan (Indikator ini khusus level Provinsi).")
        
    if periode_pilihan == "Agustus saja":
        filtered_df = filtered_df[filtered_df['Periode'].str.lower() == 'agustus']
    elif periode_pilihan == "Februari saja":
        filtered_df = filtered_df[filtered_df['Periode'].str.lower() == 'februari']
    elif periode_pilihan == "November saja":
        filtered_df = filtered_df[filtered_df['Periode'].str.lower() == 'november']
    elif periode_pilihan == "Mei saja":
        filtered_df = filtered_df[filtered_df['Periode'].str.lower() == 'mei']
    
    st.title(f"📈 Grafik {indikator_pilihan}")
    
    if not filtered_df.empty and kolom_target in filtered_df.columns:
        sumbu_x = 'Label_Waktu' if periode_pilihan == "Semua Periode" else 'Tahun'
        
        fig = px.line(
            filtered_df,
            x=sumbu_x, 
            y=kolom_target,
            color='Kabupaten_kota' if 'Kabupaten_kota' in filtered_df.columns else None,
            markers=True,
            text=kolom_target,
            labels={
                sumbu_x: 'Periode Rilis' if periode_pilihan == "Semua Periode" else 'Tahun',
                kolom_target: f'Nilai ({satuan})',
                'Kabupaten_kota': 'Wilayah'
            }
        )
        
        fig.update_traces(textposition="top center")
        fig.update_layout(
            xaxis_type='category', 
            hovermode="x unified",
            yaxis_title=f"Nilai ({satuan})"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander(f"📄 Lihat Tabel Data {nama_sheet}"):
            kolom_tampil = ['Tahun', 'Periode']
            if 'Kabupaten_kota' in filtered_df.columns:
                kolom_tampil.append('Kabupaten_kota')
            kolom_tampil.append(kolom_target)
            
            st.dataframe(filtered_df[kolom_tampil].reset_index(drop=True), use_container_width=True)
    else:
        st.warning("Data untuk indikator atau periode ini tidak tersedia.")

except Exception as e:
    st.error(f"Gagal menarik data dari sheet {nama_sheet}.")
    st.code(str(e))