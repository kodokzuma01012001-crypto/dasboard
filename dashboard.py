import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Americano Sosial - BPS Kepri",
    page_icon="📊",
    layout="wide"
)

# --- ID DATABASE GOOGLE SHEETS ---
ID_DUKNAKER = "1aUSp4yJYQRBDlb0WDURTgAUFdn45uJWdwUKfUhpeq74"
ID_KESRA = "14Wvgg69DVCLSau0veZ-9nHIHOoyiUaRatE6fWtYw-sY"
ID_HANSOS = "1dlnIhrplo2nL-4tq9VJmwTKn38cN_W6WMiWygSjG_f0"

# --- PENGELOMPOKAN INDIKATOR BERDASARKAN TIM ---
TIM_DUKNAKER = {
    "Tingkat Pengangguran Terbuka (TPT)": {"sheet_id": ID_DUKNAKER, "sheet": "TPT_TPAK", "kolom": "Nilai_TPT", "satuan": "%", "tipe": "line_periode"},
    "Tingkat Partisipasi Angkatan Kerja (TPAK)": {"sheet_id": ID_DUKNAKER, "sheet": "TPT_TPAK", "kolom": "Nilai_TPAK", "satuan": "%", "tipe": "line_periode"},
    "Jumlah Angkatan Kerja": {"sheet_id": ID_DUKNAKER, "sheet": "Level_Provinsi", "kolom": "Jumlah_angkatan_kerja", "satuan": "Ribu Orang", "tipe": "line_periode"},
    "Jumlah Bekerja": {"sheet_id": ID_DUKNAKER, "sheet": "Level_Provinsi", "kolom": "Jumlah_bekerja", "satuan": "Ribu Orang", "tipe": "line_periode"},
    "Jumlah Pengangguran": {"sheet_id": ID_DUKNAKER, "sheet": "Level_Provinsi", "kolom": "Jumlah_pengangguran", "satuan": "Ribu Orang", "tipe": "line_periode"},
    "Penduduk Bekerja Menurut Pendidikan": {"sheet_id": ID_DUKNAKER, "sheet": "Pendidikan_Tertinggi", "kolom": "Persentase", "satuan": "%", "tipe": "bar_kategori", "label_kategori": "Tingkat_pendidikan"},
    "Distribusi Menurut Lapus": {"sheet_id": ID_DUKNAKER, "sheet": "Lapus", "kolom": "Persentase_Distribusi", "satuan": "%", "tipe": "bar_kategori", "label_kategori": "Lapangan_Usaha"}
}

TIM_KESRA = {
    "Angka Partisipasi Sekolah (APS)": {"sheet_id": ID_KESRA, "sheet": "APS", "kolom": "Nilai_APS", "satuan": "%", "tipe": "line_kategori", "label_kategori": "Kelompok_Umur"},
    "Rata-rata Lama Sekolah (RLS) 15+": {"sheet_id": ID_KESRA, "sheet": "Kesra", "kolom": "rls_15+", "satuan": "Tahun", "tipe": "line_tahunan"},
    "Akses Sanitasi Layak": {"sheet_id": ID_KESRA, "sheet": "Kesra", "kolom": "akses_terhadap_sanitasi Layak", "satuan": "%", "tipe": "line_tahunan"},
    "Akses Air Minum Bersih": {"sheet_id": ID_KESRA, "sheet": "Kesra", "kolom": "akses_terhadap_air_minum_bersih", "satuan": "%", "tipe": "line_tahunan"},
    "Akses Air Minum Layak": {"sheet_id": ID_KESRA, "sheet": "Kesra", "kolom": "akses_terhadap_air_minum_layak", "satuan": "%", "tipe": "line_tahunan"},
    "Prevalensi Ketidakcukupan Konsumsi Pangan (PoU)": {"sheet_id": ID_KESRA, "sheet": "Kesra", "kolom": "prevalence_of_undernourishment", "satuan": "%", "tipe": "line_tahunan"}
}

TIM_HANSOS = {
    "Persentase Penduduk Miskin": {"sheet_id": ID_HANSOS, "sheet": "Levelkako", "kolom": "Persentase_penduduk_miskin", "satuan": "%", "tipe": "line_periode"},
    "Jumlah Penduduk Miskin": {"sheet_id": ID_HANSOS, "sheet": "Levelkako", "kolom": "Jumlah_penduduk_miskin", "satuan": "Ribu Jiwa", "tipe": "line_periode"},
    "Indeks Kedalaman Kemiskinan (P1)": {"sheet_id": ID_HANSOS, "sheet": "Levelkako", "kolom": "Kedalaman_kemiskinan", "satuan": "Indeks", "tipe": "line_periode"},
    "Indeks Keparahan Kemiskinan (P2)": {"sheet_id": ID_HANSOS, "sheet": "Levelkako", "kolom": "Keparahan_kemiskinan", "satuan": "Indeks", "tipe": "line_periode"},
    "Garis Kemiskinan": {"sheet_id": ID_HANSOS, "sheet": "Levelkako", "kolom": "GK", "satuan": "Rp/Kapita/Bulan", "tipe": "line_periode"},
    "Gini Ratio": {"sheet_id": ID_HANSOS, "sheet": "Levelkako", "kolom": "Gini_ratio", "satuan": "Indeks", "tipe": "line_periode"},
    "Indeks Demokrasi Indonesia (IDI)": {"sheet_id": ID_HANSOS, "sheet": "IDI", "kolom": "IDI_menurut_aspek", "satuan": "Indeks", "tipe": "line_kategori", "label_kategori": "aspek_IDI"}
}

@st.cache_data(ttl=3600)
def load_fast_data(sheet_id, sheet_name):
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(csv_url)
    
    kolom_teks = ['Tahun', 'Periode', 'Kabupaten_kota', 'Tingkat_pendidikan', 'Lapangan_Usaha', 'Kelompok_Umur', 'aspek_IDI']
    
    for col in df.columns:
        if col not in kolom_teks:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(lambda x: str(x).replace(',', '') if '.' in str(x) else str(x).replace(',', '.'))
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
    def urutan_bulan(bulan_str):
        mapping = {'februari': 1, 'maret': 2, 'mei': 3, 'agustus': 4, 'september': 5, 'november': 6}
        return mapping.get(str(bulan_str).lower(), 99)
            
    if 'Periode' in df.columns and 'Tahun' in df.columns:
        df['Urutan_Bulan'] = df['Periode'].apply(urutan_bulan)
        df = df.sort_values(by=['Tahun', 'Urutan_Bulan', 'Kabupaten_kota'] if 'Kabupaten_kota' in df.columns else ['Tahun', 'Urutan_Bulan']).reset_index(drop=True)
        df['Label_Waktu'] = df['Periode'].astype(str) + " " + df['Tahun'].astype(str)
    elif 'Tahun' in df.columns:
        df = df.sort_values(by=['Tahun', 'Kabupaten_kota'] if 'Kabupaten_kota' in df.columns else ['Tahun']).reset_index(drop=True)
    
    return df

# --- SIDEBAR NAVIGASI UTAMA ---
st.sidebar.title("📊 Dasboard Americano Tim Sosial")
st.sidebar.markdown("**BPS Provinsi Kepulauan Riau**")

if st.sidebar.button("🔄 Segarkan Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.divider()
st.sidebar.header("🏢 Pilih Domain Kerja")

pilar_pilihan = st.sidebar.radio("Navigasi Tim:", options=["Tim Duknaker", "Tim Kesra", "Tim Hansos"], label_visibility="collapsed")

if pilar_pilihan == "Tim Duknaker": kamus_aktif = TIM_DUKNAKER
elif pilar_pilihan == "Tim Kesra": kamus_aktif = TIM_KESRA
else: kamus_aktif = TIM_HANSOS

st.sidebar.divider()
st.sidebar.header("🎯 Filter Visualisasi")

indikator_pilihan = st.sidebar.selectbox("1. Pilih Indikator:", options=list(kamus_aktif.keys()))
konfig = kamus_aktif[indikator_pilihan]
nama_sheet = konfig["sheet"]
sheet_id = konfig["sheet_id"]

kolom_target = konfig["kolom"]
satuan = konfig["satuan"]
tipe_grafik = konfig["tipe"]

try:
    with st.spinner(f'Menarik data...'):
        data = load_fast_data(sheet_id, nama_sheet)
    
    # KONDISI 1: GRAFIK GARIS (ADA PERIODE BULAN)
    if tipe_grafik == "line_periode":
        unik_periode = data['Periode'].drop_duplicates().tolist() if 'Periode' in data.columns else []
        opsi_periode = ["Semua Periode"] + unik_periode
        
        periode_pilihan = st.sidebar.selectbox("2. Periode:", options=opsi_periode)
        
        if 'Kabupaten_kota' in data.columns:
            daftar_wilayah = data['Kabupaten_kota'].unique().tolist()
            wilayah_pilihan = st.sidebar.multiselect("3. Wilayah:", options=daftar_wilayah, default=["Kepulauan Riau"] if "Kepulauan Riau" in daftar_wilayah else daftar_wilayah[0])
            filtered_df = data[data['Kabupaten_kota'].isin(wilayah_pilihan)]
        else:
            filtered_df = data.copy()
            st.sidebar.info("💡 Filter wilayah disembunyikan (Khusus level Provinsi).")
            
        if periode_pilihan != "Semua Periode":
            target_periode = periode_pilihan.lower()
            filtered_df = filtered_df[filtered_df['Periode'].str.lower() == target_periode]
        
        st.title(f"📈 {indikator_pilihan}")
        
        if not filtered_df.empty:
            sumbu_x = 'Label_Waktu' if periode_pilihan == "Semua Periode" else 'Tahun'
            fig = px.line(filtered_df, x=sumbu_x, y=kolom_target, color='Kabupaten_kota' if 'Kabupaten_kota' in filtered_df.columns else None, markers=True, text=kolom_target)
            fig.update_traces(textposition="top center")
            fig.update_layout(xaxis_type='category', hovermode="x unified", yaxis_title=f"Nilai ({satuan})")
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("📄 Tabel Data"):
                csv = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 Unduh Data di Sini (CSV)", data=csv, file_name=f"Data_{indikator_pilihan}.csv", mime="text/csv", use_container_width=True)
                st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)

    # KONDISI 2: GRAFIK GARIS TAHUNAN (TANPA BULAN)
    elif tipe_grafik == "line_tahunan":
        if 'Kabupaten_kota' in data.columns:
            daftar_wilayah = data['Kabupaten_kota'].unique().tolist()
            wilayah_pilihan = st.sidebar.multiselect("2. Wilayah:", options=daftar_wilayah, default=["Kepulauan Riau"] if "Kepulauan Riau" in daftar_wilayah else daftar_wilayah[0])
            filtered_df = data[data['Kabupaten_kota'].isin(wilayah_pilihan)]
        else:
            filtered_df = data.copy()
        
        st.title(f"📈 {indikator_pilihan}")
        
        if not filtered_df.empty:
            fig = px.line(filtered_df, x='Tahun', y=kolom_target, color='Kabupaten_kota' if 'Kabupaten_kota' in filtered_df.columns else None, markers=True, text=kolom_target)
            fig.update_traces(textposition="top center")
            fig.update_layout(xaxis_type='category', hovermode="x unified", yaxis_title=f"Nilai ({satuan})")
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("📄 Tabel Data"):
                csv = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 Unduh Data di Sini (CSV)", data=csv, file_name=f"Data_{indikator_pilihan}.csv", mime="text/csv", use_container_width=True)
                st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)

    # KONDISI 3: GRAFIK GARIS DENGAN KATEGORI (APS, IDI)
    elif tipe_grafik == "line_kategori":
        kolom_kategori = konfig["label_kategori"]
        if 'Kabupaten_kota' in data.columns:
            daftar_wilayah = data['Kabupaten_kota'].unique().tolist()
            wilayah_pilihan = st.sidebar.selectbox("2. Pilih Wilayah:", options=daftar_wilayah, index=daftar_wilayah.index("Kepulauan Riau") if "Kepulauan Riau" in daftar_wilayah else 0)
            filtered_df = data[data['Kabupaten_kota'] == wilayah_pilihan]
        else:
            filtered_df = data.copy()
            st.sidebar.info("💡 Filter wilayah disembunyikan (Khusus level Provinsi).")
        
        st.title(f"📈 {indikator_pilihan}")
        
        if not filtered_df.empty:
            fig = px.line(filtered_df, x='Tahun', y=kolom_target, color=kolom_kategori, markers=True, text=kolom_target)
            fig.update_traces(textposition="top center")
            fig.update_layout(xaxis_type='category', hovermode="x unified", yaxis_title=f"Nilai ({satuan})")
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("📄 Tabel Data"):
                csv = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 Unduh Data di Sini (CSV)", data=csv, file_name=f"Data_{indikator_pilihan}.csv", mime="text/csv", use_container_width=True)
                st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)

    # KONDISI 4: GRAFIK BATANG HORIZONTAL
    elif tipe_grafik == "bar_kategori":
        st.sidebar.info("💡 Filter wilayah dinonaktifkan.")
        kolom_kategori = konfig["label_kategori"]
        daftar_tahun = sorted(data['Tahun'].unique().tolist(), reverse=True)
        tahun_pilihan = st.sidebar.multiselect("2. Tahun:", options=daftar_tahun, default=daftar_tahun[:2] if len(daftar_tahun) >= 2 else daftar_tahun)
        
        filtered_df = data[data['Tahun'].isin(tahun_pilihan)]
        st.title(f"📊 {indikator_pilihan}")
        
        if not filtered_df.empty:
            fig = px.bar(filtered_df, x=kolom_target, y=kolom_kategori, color='Label_Waktu', barmode='group', text=kolom_target, orientation='h')
            fig.update_traces(textposition='outside')
            fig.update_layout(xaxis_title=f"Nilai ({satuan})", yaxis_title="Kategori", yaxis={'categoryorder':'total ascending'}, height=600)
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("📄 Tabel Data"):
                csv = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 Unduh Data di Sini (CSV)", data=csv, file_name=f"Data_{indikator_pilihan}.csv", mime="text/csv", use_container_width=True)
                st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)

except Exception as e:
    st.error(f"Gagal menarik data dari sheet {nama_sheet}. Pastikan nama sheet dan kolom sesuai.")
    st.code(str(e))
