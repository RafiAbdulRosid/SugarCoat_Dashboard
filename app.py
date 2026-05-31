import pandas as pd
import plotly.express as px
import streamlit as st

# ==========================================
# 1. KONFIGURASI TEMA & HALAMAN UTAMA
# ==========================================
st.set_page_config(
    page_title="SugarCoat - Diabetes Risk Dashboard",
    page_icon="🏥",
    layout="wide"
)

# Definisi Palet Warna (2 kategori: Tidak Diabetes & Diabetes)
COLOR_MAP = {
    'Tidak Diabetes': '#1ABC9C',
    'Diabetes': '#E74C3C'
}

# ==========================================
# 2. LOAD DATA
# ==========================================
@st.cache_data
def load_data():
    df = pd.read_csv("Data Diabetes Lifestyle Cleaned.csv")
    # Mapping diagnosed_diabetes ke label teks untuk tampilan
    df['status_diabetes'] = df['diagnosed_diabetes'].map({
        0: 'Tidak Diabetes',
        1: 'Diabetes'
    })
    return df

try:
    df_lifestyle = load_data()
except FileNotFoundError:
    st.error("⚠️ File 'Data Diabetes Lifestyle Cleaned.csv' tidak ditemukan.")
    st.stop()

# ==========================================
# 3. SIDEBAR & FILTER GLOBAL
# ==========================================
st.sidebar.title("🏥 SugarCoat Analytics")
st.sidebar.markdown("Dashboard Pemantauan Risiko Diabetes & Gaya Hidup")

halaman = st.sidebar.radio(
    "📌 Navigasi Menu:",
    [
        "Ringkasan & Demografi",
        "Analisis Gaya Hidup & Konsumsi",
        "Faktor Medis & Keturunan",
        "Analisis Sosio-Ekonomi (EDA)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Filter Data Global")

gender_options = df_lifestyle['gender'].unique()
gender_filter = st.sidebar.multiselect("Jenis Kelamin:", options=gender_options, default=gender_options)

smoke_options = df_lifestyle['smoking_status'].unique()
smoke_filter = st.sidebar.multiselect("Status Merokok:", options=smoke_options, default=smoke_options)

df_filtered = df_lifestyle[
    (df_lifestyle['gender'].isin(gender_filter)) &
    (df_lifestyle['smoking_status'].isin(smoke_filter))
]

# ==========================================
# 4. IMPLEMENTASI HALAMAN & GRAFIK
# ==========================================

# ------------------------------------------
# HALAMAN 1: RINGKASAN & DEMOGRAFI
# ------------------------------------------
if halaman == "Ringkasan & Demografi":
    st.title("📊 Ringkasan Dataset & Profil Demografi")
    st.markdown("Menampilkan metrik utama data serta sebaran demografi awal dari populasi pasien.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Pasien dalam Analisis", f"{len(df_filtered):,}")
    with col2:
        avg_age = df_filtered['age'].mean() if len(df_filtered) > 0 else 0
        st.metric("Rata-rata Usia Pasien", f"{avg_age:.1f} Tahun")
    with col3:
        avg_bmi = df_filtered['bmi'].mean() if len(df_filtered) > 0 else 0
        st.metric("Rata-rata BMI", f"{avg_bmi:.1f} kg/m²")

    st.markdown("---")

    col_demo1, col_demo2 = st.columns(2)

    with col_demo1:
        st.subheader("1. Distribusi Kelompok Usia Pasien")
        fig_age = px.histogram(
            df_filtered, x="age", color="status_diabetes",
            color_discrete_map=COLOR_MAP, barmode="overlay",
            title="Kepadatan Umur Berdasarkan Status Diabetes",
            template="plotly_white"
        )
        st.plotly_chart(fig_age, use_container_width=True)

    with col_demo2:
        st.subheader("2. Proporsi Kasus Berdasarkan Jenis Kelamin")
        fig_gender = px.histogram(
            df_filtered, x="gender", color="status_diabetes",
            color_discrete_map=COLOR_MAP, barmode="group",
            title="Jumlah Pasien per Gender & Status Diabetes",
            template="plotly_white"
        )
        st.plotly_chart(fig_gender, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Cuplikan Data Pasien (10 Baris Pertama)")
    st.dataframe(df_filtered.head(10), use_container_width=True)

# ------------------------------------------
# HALAMAN 2: ANALISIS GAYA HIDUP & KONSUMSI
# ------------------------------------------
elif halaman == "Analisis Gaya Hidup & Konsumsi":
    st.title("🏃‍♂️ Analisis Perilaku, Aktivitas Fisik & Konsumsi")
    st.markdown("Menganalisis indikator gaya hidup harian serta pola konsumsi zat yang memicu risiko diabetes.")

    col_lf1, col_lf2 = st.columns(2)

    with col_lf1:
        st.subheader("1. Pola Hubungan Aktivitas Fisik (Olahraga)")
        df_avg_act = df_filtered.groupby('status_diabetes')['physical_activity_minutes_per_week'].mean().reset_index()
        fig_act = px.line(
            df_avg_act, x='status_diabetes', y='physical_activity_minutes_per_week', markers=True,
            title="Rata-rata Olahraga Mingguan (Menit)", template="plotly_white"
        )
        fig_act.update_traces(line=dict(color='#2980B9', width=4), marker=dict(size=10, color='#2C3E50'))
        st.plotly_chart(fig_act, use_container_width=True)

    with col_lf2:
        st.subheader("2. Durasi Tidur Harian Pasien")
        df_avg_slp = df_filtered.groupby('status_diabetes')['sleep_hours_per_day'].mean().reset_index()
        fig_slp = px.bar(
            df_avg_slp, x='status_diabetes', y='sleep_hours_per_day', color='status_diabetes',
            color_discrete_map=COLOR_MAP, text='sleep_hours_per_day',
            title="Rata-rata Jam Tidur Pasien", template="plotly_white"
        )
        fig_slp.update_traces(texttemplate='%{text:.2f} jam', textposition='outside')
        st.plotly_chart(fig_slp, use_container_width=True)

    st.markdown("---")

    col_lf3, col_lf4 = st.columns(2)

    with col_lf3:
        st.subheader("3. Distribusi Screen Time (Box Plot)")
        fig_box_screen = px.box(
            df_filtered, x='status_diabetes', y='screen_time_hours_per_day', color='status_diabetes',
            color_discrete_map=COLOR_MAP, points="outliers",
            title="Sebaran Jam Menatap Layar per Hari", template="plotly_white"
        )
        st.plotly_chart(fig_box_screen, use_container_width=True)

    with col_lf4:
        st.subheader("4. Rata-rata Konsumsi Minuman Manis")
        df_avg_bev = df_filtered.groupby('status_diabetes')['sweet_beverages_per_week'].mean().reset_index()
        fig_bev = px.bar(
            df_avg_bev, x='status_diabetes', y='sweet_beverages_per_week', color='status_diabetes',
            color_discrete_map=COLOR_MAP, text='sweet_beverages_per_week',
            title="Konsumsi Minuman Manis (Gelas/Minggu)", template="plotly_white"
        )
        fig_bev.update_traces(texttemplate='%{text:.1f} gelas', textposition='inside')
        st.plotly_chart(fig_bev, use_container_width=True)

    st.markdown("---")
    st.subheader("5. Intensitas Konsumsi Alkohol Berdasarkan Perilaku Merokok Pasien")
    fig_alc = px.box(
        df_filtered, x='smoking_status', y='alcohol_consumption_per_week', color='status_diabetes',
        color_discrete_map=COLOR_MAP, title="Pola Konsumsi Alkohol Mingguan vs Status Merokok",
        template="plotly_white"
    )
    st.plotly_chart(fig_alc, use_container_width=True)

# ------------------------------------------
# HALAMAN 3: FAKTOR MEDIS & KETURUNAN
# ------------------------------------------
elif halaman == "Faktor Medis & Keturunan":
    st.title("🩺 Analisis Kondisi Klinis & Riwayat Medis")
    st.markdown("Mengeksplorasi keterkaitan parameter biologis, riwayat penyakit penyerta, dan faktor genetik.")

    st.subheader("1. Sebaran Karakteristik Fisik Pasien (Age vs BMI Scatter)")
    fig_scatter = px.scatter(
        df_filtered.sample(min(5000, len(df_filtered))),
        x="age", y="bmi", color="status_diabetes", color_discrete_map=COLOR_MAP,
        title="Korelasi Umur dan BMI Pasien (Sampel Data)",
        labels={"age": "Usia (Tahun)", "bmi": "Body Mass Index (BMI)"},
        template="plotly_white", opacity=0.6
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")
    col_med1, col_med2 = st.columns(2)

    with col_med1:
        st.subheader("2. Dampak Riwayat Keturunan Keluarga")
        df_fam = df_filtered.copy()
        df_fam['Family History'] = df_fam['family_history_diabetes'].map({
            0: 'Tidak Ada Riwayat Keluarga',
            1: 'Ada Riwayat Keluarga'
        })
        fig_fam = px.histogram(
            df_fam, x="Family History", color="status_diabetes", color_discrete_map=COLOR_MAP,
            barmode="group", title="Rasio Diabetes Berdasarkan Garis Keturunan", template="plotly_white"
        )
        st.plotly_chart(fig_fam, use_container_width=True)

    with col_med2:
        st.subheader("3. Korelasi Riwayat Penyakit Hipertensi")
        df_hyp = df_filtered.copy()
        df_hyp['Hypertension'] = df_hyp['hypertension_history'].map({
            0: 'Normal / Tanpa Hipertensi',
            1: 'Memiliki Hipertensi'
        })
        fig_hyp = px.histogram(
            df_hyp, x="status_diabetes", color="Hypertension",
            color_discrete_sequence=['#34495E', '#E67E22'], barmode="stack",
            title="Distribusi Pengidap Hipertensi di Tiap Status Diabetes",
            template="plotly_white"
        )
        st.plotly_chart(fig_hyp, use_container_width=True)

    st.markdown("---")
    st.subheader("4. Komplikasi Mutlak Penyakit Kardiovaskular (Jantung)")
    df_cv = df_filtered.copy()
    df_cv['Cardiovascular Disease'] = df_cv['cardiovascular_history'].map({
        0: 'Sehat / Normal',
        1: 'Ada Riwayat Jantung'
    })
    df_pie = df_cv.groupby(['status_diabetes', 'Cardiovascular Disease']).size().reset_index(name='count')
    fig_donut = px.pie(
        df_pie, names='Cardiovascular Disease', values='count', facet_col='status_diabetes', hole=0.4,
        color='Cardiovascular Disease',
        color_discrete_map={'Sehat / Normal': '#34495E', 'Ada Riwayat Jantung': '#E74C3C'},
        template="plotly_white"
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# ------------------------------------------
# HALAMAN 4: ANALISIS SOSIO-EKONOMI (EDA)
# ------------------------------------------
elif halaman == "Analisis Sosio-Ekonomi (EDA)":
    st.title("💼 Analisis Faktor Sosio-Ekonomi Pasien")
    st.markdown("Halaman khusus analisis eksploratif (EDA) untuk meninjau profil latar belakang sosial dan ekonomi pasien.")

    col_eco1, col_eco2 = st.columns(2)

    with col_eco1:
        st.subheader("1. Distribusi Tingkat Pendapatan (Income Level)")
        fig_inc = px.histogram(
            df_filtered, x="income_level", color="status_diabetes", color_discrete_map=COLOR_MAP,
            category_orders={"income_level": ["Low", "Medium", "High"]}, barmode="group",
            title="Tingkat Risiko Diabetes Berdasarkan Strata Ekonomi", template="plotly_white"
        )
        st.plotly_chart(fig_inc, use_container_width=True)

    with col_eco2:
        st.subheader("2. Status Pekerjaan Pasien (Employment Status)")
        fig_emp = px.histogram(
            df_filtered, x="employment_status", color="status_diabetes", color_discrete_map=COLOR_MAP,
            barmode="stack", title="Proporsi Pekerjaan Terhadap Status Diabetes", template="plotly_white"
        )
        st.plotly_chart(fig_emp, use_container_width=True)

    st.markdown("---")
    st.subheader("3. Tingkat Pendidikan Terakhir Pasien (Education Level)")
    fig_edu = px.histogram(
        df_filtered, x="education_level", color="status_diabetes", color_discrete_map=COLOR_MAP,
        category_orders={"education_level": ["No formal", "Highschool", "Graduate", "Postgraduate"]},
        title="Distribusi Kelompok Pendidikan vs Status Diabetes", template="plotly_white"
    )
    st.plotly_chart(fig_edu, use_container_width=True)