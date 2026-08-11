# Library
import os
from collections import Counter

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Komparatif Sentimen E-Wallet",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Konfigurasi utama
APP_ORDER = ["DANA", "GoPay", "ShopeePay"]

warnaApp = {
    "DANA": "#2377ca",
    "GoPay": "#01aed6",
    "ShopeePay": "#ff773c"
}

MODEL_CONFIG = {
    "Model NBC": {
        "short": "NBC",
        "title": "Multinomial Naïve Bayes Classifier",
        "description": "TF-IDF + Multinomial Naïve Bayes Classifier",
        "sentimentFile": "hasilSentimenNBC.csv",
        "evaluationFile": "hasilEvaluasiNBC.csv",
        "predictColumn": "predictLabel"
    },
    "Model SVM": {
        "short": "SVM",
        "title": "Linear Support Vector Machine",
        "description": "TF-IDF + LinearSVC (C=1.0)",
        "sentimentFile": "hasilSentimenSVM.csv",
        "evaluationFile": "hasilEvaluasiSVM.csv",
        "predictColumn": "predictLabelSVM"
    }
}

PLOTLY_CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "scrollZoom": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"]
}


# Style dashboard
st.markdown(
    """
    <style>
        :root {
            --text: #172033;
            --muted: #667085;
            --border: #e6eaf0;
            --surface: #ffffff;
            --background: #f7f9fc;
        }

        html, body, [class*="css"] {
            font-family: Inter, "Segoe UI", Arial, sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 0% 0%, rgba(35,119,202,.08), transparent 24%),
                radial-gradient(circle at 100% 0%, rgba(1,174,214,.07), transparent 24%),
                radial-gradient(circle at 50% 100%, rgba(255,119,60,.06), transparent 26%),
                var(--background);
        }

        .block-container {
            max-width: 1500px;
            padding-top: 1.35rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] .block-container {
            padding-top: 1rem;
        }

        .brand-strip {
            width: 100%;
            height: 5px;
            border-radius: 999px;
            background: linear-gradient(90deg, #2377ca 0 33.33%, #01aed6 33.33% 66.66%, #ff773c 66.66% 100%);
            margin-bottom: 18px;
        }

        .dashboard-header {
            background: rgba(255,255,255,.94);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 22px 24px;
            box-shadow: 0 8px 28px rgba(16,24,40,.06);
            margin-bottom: 14px;
        }

        .dashboard-header h1 {
            color: var(--text);
            font-size: clamp(26px, 3vw, 42px);
            line-height: 1.1;
            margin: 0 0 8px 0;
            letter-spacing: -0.8px;
        }

        .dashboard-header p {
            color: var(--muted);
            margin: 0;
            font-size: 14px;
            line-height: 1.55;
        }

        .model-badge {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            border: 1px solid #d9e2ef;
            border-radius: 999px;
            padding: 7px 11px;
            margin-bottom: 10px;
            background: #f8fbff;
            color: #344054;
            font-size: 12px;
            font-weight: 700;
        }

        .legend-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 14px;
        }

        .legend-chip {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 6px 9px;
            border: 1px solid var(--border);
            border-radius: 999px;
            background: #ffffff;
            color: #475467;
            font-size: 12px;
            font-weight: 600;
        }

        .legend-dot {
            width: 9px;
            height: 9px;
            border-radius: 50%;
            display: inline-block;
        }

        .filter-box {
            background: rgba(255,255,255,.92);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 13px 15px 4px 15px;
            box-shadow: 0 5px 20px rgba(16,24,40,.04);
            margin-bottom: 14px;
        }

        .section-title {
            color: var(--text);
            font-size: 21px;
            font-weight: 800;
            letter-spacing: -0.2px;
            margin: 18px 0 4px 0;
        }

        .section-subtitle {
            color: var(--muted);
            font-size: 13px;
            line-height: 1.55;
            margin: 0 0 12px 0;
        }

        .kpi-card {
            background: rgba(255,255,255,.96);
            border: 1px solid var(--border);
            border-radius: 15px;
            padding: 16px 16px 14px 16px;
            min-height: 112px;
            box-shadow: 0 6px 22px rgba(16,24,40,.05);
            transition: transform .16s ease, box-shadow .16s ease;
        }

        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 28px rgba(16,24,40,.08);
        }

        .kpi-label {
            color: #667085;
            font-size: 12px;
            font-weight: 650;
            margin-bottom: 7px;
        }

        .kpi-value {
            color: var(--text);
            font-size: clamp(24px, 2.4vw, 36px);
            font-weight: 800;
            line-height: 1;
            letter-spacing: -0.6px;
        }

        .kpi-note {
            color: #98a2b3;
            font-size: 11px;
            margin-top: 8px;
            line-height: 1.35;
        }

        .insight-box {
            background: linear-gradient(90deg, rgba(35,119,202,.08), rgba(1,174,214,.06), rgba(255,119,60,.07));
            border: 1px solid #dfe7f1;
            border-left: 5px solid #2377ca;
            border-radius: 14px;
            padding: 13px 15px;
            color: #344054;
            font-size: 13px;
            line-height: 1.55;
            margin: 12px 0 8px 0;
        }

        .info-note {
            background: #ffffff;
            border: 1px dashed #d0d5dd;
            border-radius: 12px;
            padding: 10px 12px;
            color: #667085;
            font-size: 12px;
            line-height: 1.5;
            margin: 8px 0 12px 0;
        }

        [data-testid="stPlotlyChart"] {
            background: rgba(255,255,255,.96);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 4px;
            box-shadow: 0 6px 22px rgba(16,24,40,.05);
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--border);
            border-radius: 14px;
            overflow: hidden;
        }

        hr {
            border: none;
            border-top: 1px solid #e7ebf0;
            margin: 1.4rem 0;
        }

        .sidebar-title {
            color: #172033;
            font-size: 20px;
            font-weight: 800;
            margin: 2px 0 4px 0;
        }

        .sidebar-caption {
            color: #667085;
            font-size: 12px;
            line-height: 1.5;
            margin-bottom: 14px;
        }

        .sidebar-model-card {
            border: 1px solid #e3e8ef;
            border-radius: 13px;
            padding: 11px 12px;
            background: #f8fafc;
            margin: 10px 0 14px 0;
            color: #344054;
            font-size: 12px;
            line-height: 1.5;
        }

        @media (max-width: 900px) {
            .block-container {
                padding-left: .8rem;
                padding-right: .8rem;
            }

            .dashboard-header {
                padding: 18px;
            }

            .kpi-card {
                min-height: 98px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True
)


# Fungsi data
@st.cache_data
def load_model_data(sentiment_file, evaluation_file, predict_column):
    df_sentiment = pd.read_csv(sentiment_file)
    df_evaluation = pd.read_csv(evaluation_file)

    df_sentiment.columns = df_sentiment.columns.str.strip()
    df_evaluation.columns = df_evaluation.columns.str.strip()

    required_sentiment = {
        "reviewId", "appName", "content", "score", "date",
        "actualLabel", predict_column
    }
    required_evaluation = {
        "appName", "dataTrain", "dataTest", "TN", "FP", "FN", "TP",
        "Accuracy", "Precision", "Recall", "Specificity", "F1-Score"
    }

    missing_sentiment = required_sentiment.difference(df_sentiment.columns)
    missing_evaluation = required_evaluation.difference(df_evaluation.columns)

    if missing_sentiment:
        raise ValueError(
            f"Kolom pada {sentiment_file} belum lengkap: {sorted(missing_sentiment)}"
        )

    if missing_evaluation:
        raise ValueError(
            f"Kolom pada {evaluation_file} belum lengkap: {sorted(missing_evaluation)}"
        )

    df_sentiment["appName"] = df_sentiment["appName"].astype(str).str.strip()
    df_sentiment["actualLabel"] = (
        df_sentiment["actualLabel"].astype(str).str.strip().str.lower()
    )
    df_sentiment["sentimen"] = (
        df_sentiment[predict_column].astype(str).str.strip().str.lower().str.capitalize()
    )
    df_sentiment["date"] = pd.to_datetime(df_sentiment["date"], errors="coerce")
    df_sentiment["score"] = pd.to_numeric(df_sentiment["score"], errors="coerce")
    df_sentiment = df_sentiment.dropna(subset=["date", "appName", "sentimen"])

    df_evaluation["appName"] = df_evaluation["appName"].astype(str).str.strip()
    if "algorithm" not in df_evaluation.columns:
        df_evaluation["algorithm"] = "NBC"

    metric_columns = [
        "Accuracy", "Precision", "Recall", "Specificity", "F1-Score"
    ]
    for column in metric_columns:
        df_evaluation[column] = pd.to_numeric(
            df_evaluation[column], errors="coerce"
        )

    for column in ["dataTrain", "dataTest", "TN", "FP", "FN", "TP"]:
        df_evaluation[column] = pd.to_numeric(
            df_evaluation[column], errors="coerce"
        )

    return df_sentiment, df_evaluation


@st.cache_data
def load_original_reviews():
    raw_files = {
        "DANA": "rawDana.csv",
        "GoPay": "rawGopay.csv",
        "ShopeePay": "rawShopeepay.csv"
    }

    frames = []
    for app_name, file_name in raw_files.items():
        if not os.path.exists(file_name):
            continue

        raw = pd.read_csv(file_name)
        if not {"reviewId", "content"}.issubset(raw.columns):
            continue

        raw = raw[["reviewId", "content"]].copy()
        raw["appName"] = app_name
        raw = raw.rename(columns={"content": "originalContent"})
        frames.append(raw)

    if not frames:
        return pd.DataFrame(columns=["reviewId", "appName", "originalContent"])

    return pd.concat(frames, ignore_index=True).drop_duplicates(
        subset=["reviewId", "appName"]
    )


def rgba(hex_color, alpha=1.0):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def weighted_metric(df_eval, metric_name):
    if df_eval.empty:
        return 0.0

    weights = pd.to_numeric(df_eval["dataTest"], errors="coerce").fillna(0)
    values = pd.to_numeric(df_eval[metric_name], errors="coerce").fillna(0)

    if weights.sum() == 0:
        return float(values.mean()) if len(values) else 0.0

    return float((values * weights).sum() / weights.sum())


def render_kpi(label, value, note="", accent="#172033"):
    st.markdown(
        f"""
        <div class="kpi-card" style="border-top: 4px solid {accent};">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value" style="color:{accent};">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_section(title, subtitle=""):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(
            f'<div class="section-subtitle">{subtitle}</div>',
            unsafe_allow_html=True
        )


def top_words(data, top_n=15):
    counter = Counter()

    for text in data.dropna().astype(str):
        tokens = [
            token.strip().lower()
            for token in text.split()
            if len(token.strip()) > 1 and not token.strip().isdigit()
        ]
        counter.update(tokens)

    return pd.DataFrame(
        counter.most_common(top_n),
        columns=["Kata", "Frekuensi"]
    )


def format_date_range(start_date, end_date):
    month_id = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun",
        7: "Jul", 8: "Agu", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des"
    }
    return (
        f"{start_date.day} {month_id[start_date.month]} {start_date.year}"
        f" – {end_date.day} {month_id[end_date.month]} {end_date.year}"
    )


# Sidebar model
with st.sidebar:
    st.markdown('<div class="sidebar-title">Model Analisis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-caption">Pilih algoritma untuk membuka dashboard khusus dari hasil model tersebut.</div>',
        unsafe_allow_html=True
    )

    selected_model = st.radio(
        "Pilih model",
        options=["Model NBC", "Model SVM"],
        index=0,
        key="selected_model"
    )

    model_config = MODEL_CONFIG[selected_model]

    st.markdown(
        f"""
        <div class="sidebar-model-card">
            <strong>{model_config['title']}</strong><br>
            {model_config['description']}<br><br>
            <span style="color:#667085;">Sumber:</span><br>
            {model_config['sentimentFile']}<br>
            {model_config['evaluationFile']}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("**Identitas aplikasi**")
    for app_name in APP_ORDER:
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:8px;margin:7px 0;color:#475467;font-size:13px;">
                <span style="width:10px;height:10px;border-radius:50%;background:{warnaApp[app_name]};display:inline-block;"></span>
                <strong>{app_name}</strong>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()
    st.caption(
        "Metrik evaluasi selalu berasal dari data testing. Filter periode dan sentimen tidak mengubah hasil evaluasi model."
    )


# Load model aktif
try:
    df_sentimen, df_evaluasi = load_model_data(
        model_config["sentimentFile"],
        model_config["evaluationFile"],
        model_config["predictColumn"]
    )
except Exception as error:
    st.error(
        "Gagal memuat file model aktif. Pastikan file CSV berada satu folder "
        f"dengan dashboard.py. Detail: {error}"
    )
    st.stop()


# Header
min_date = df_sentimen["date"].min().date()
max_date = df_sentimen["date"].max().date()
full_period_text = format_date_range(min_date, max_date)

st.markdown('<div class="brand-strip"></div>', unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="dashboard-header">
        <div class="model-badge">● MODEL AKTIF · {model_config['short']}</div>
        <h1>Dashboard Komparatif Sentimen E-Wallet</h1>
        <p>
            Perbandingan hasil klasifikasi sentimen DANA, GoPay, dan ShopeePay
            menggunakan <strong>{model_config['title']}</strong>.
            Data visualisasi mencakup periode <strong>{full_period_text}</strong>.
        </p>
        <div class="legend-row">
            <span class="legend-chip"><span class="legend-dot" style="background:#2377ca"></span>DANA</span>
            <span class="legend-chip"><span class="legend-dot" style="background:#01aed6"></span>GoPay</span>
            <span class="legend-chip"><span class="legend-dot" style="background:#ff773c"></span>ShopeePay</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# Filter utama
with st.container(border=True):
    filter_col_1, filter_col_2, filter_col_3 = st.columns([1.35, 1.0, 1.35])

    with filter_col_1:
        selected_apps = st.multiselect(
            "E-Wallet",
            options=APP_ORDER,
            default=APP_ORDER,
            key="filter_apps"
        )

    with filter_col_2:
        selected_sentiments = st.multiselect(
            "Sentimen prediksi",
            options=["Positif", "Negatif"],
            default=["Positif", "Negatif"],
            key="filter_sentiments"
        )

    with filter_col_3:
        selected_dates = st.date_input(
            "Periode ulasan",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="filter_dates"
        )

if not selected_apps:
    st.warning("Pilih minimal satu aplikasi E-Wallet.")
    st.stop()

if not selected_sentiments:
    st.warning("Pilih minimal satu kategori sentimen.")
    st.stop()

if isinstance(selected_dates, (list, tuple)) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
elif isinstance(selected_dates, (list, tuple)) and len(selected_dates) == 1:
    start_date = end_date = selected_dates[0]
else:
    start_date = end_date = selected_dates

start_timestamp = pd.Timestamp(start_date)
end_timestamp = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

# Base data memakai aplikasi + periode agar KPI komposisi tetap utuh.
df_base = df_sentimen[
    (df_sentimen["appName"].isin(selected_apps))
    & (df_sentimen["date"] >= start_timestamp)
    & (df_sentimen["date"] <= end_timestamp)
].copy()

# Data visual mengikuti filter sentimen.
df_visual = df_base[df_base["sentimen"].isin(selected_sentiments)].copy()

df_eval_selected = df_evaluasi[
    df_evaluasi["appName"].isin(selected_apps)
].copy()

if df_base.empty:
    st.warning("Tidak ada data pada kombinasi aplikasi dan periode yang dipilih.")
    st.stop()


# Level 1 - KPI
render_section(
    "Ringkasan Utama",
    "Headline dashboard: angka yang paling penting ditampilkan terlebih dahulu sebelum grafik pendukung."
)

base_total = len(df_base)
positive_total = int((df_base["sentimen"] == "Positif").sum())
negative_total = int((df_base["sentimen"] == "Negatif").sum())
positive_pct = (positive_total / base_total * 100) if base_total else 0
negative_pct = (negative_total / base_total * 100) if base_total else 0
weighted_accuracy = weighted_metric(df_eval_selected, "Accuracy") * 100
weighted_f1 = weighted_metric(df_eval_selected, "F1-Score") * 100

kpi_1, kpi_2, kpi_3, kpi_4, kpi_5 = st.columns(5)

with kpi_1:
    render_kpi(
        "Total Ulasan",
        f"{base_total:,}",
        "Aplikasi & periode terpilih",
        "#172033"
    )

with kpi_2:
    render_kpi(
        "Sentimen Positif",
        f"{positive_pct:.1f}%",
        f"{positive_total:,} ulasan",
        "#16803b"
    )

with kpi_3:
    render_kpi(
        "Sentimen Negatif",
        f"{negative_pct:.1f}%",
        f"{negative_total:,} ulasan",
        "#c7372f"
    )

with kpi_4:
    render_kpi(
        "Accuracy Test",
        f"{weighted_accuracy:.2f}%",
        "Rata-rata tertimbang aplikasi terpilih",
        "#5b5bd6"
    )

with kpi_5:
    render_kpi(
        "F1-Score Test",
        f"{weighted_f1:.2f}%",
        "Rata-rata tertimbang aplikasi terpilih",
        "#7a4fb3"
    )

# Insight otomatis
app_summary = (
    df_base.groupby(["appName", "sentimen"])
    .size()
    .unstack(fill_value=0)
    .reindex(selected_apps)
)

for sentiment_name in ["Positif", "Negatif"]:
    if sentiment_name not in app_summary.columns:
        app_summary[sentiment_name] = 0

app_summary["Total"] = app_summary["Positif"] + app_summary["Negatif"]
app_summary["PositivePct"] = (
    app_summary["Positif"] / app_summary["Total"].replace(0, pd.NA) * 100
).fillna(0)

best_sentiment_app = app_summary["PositivePct"].idxmax()
best_sentiment_pct = app_summary.loc[best_sentiment_app, "PositivePct"]

if not df_eval_selected.empty:
    best_accuracy_row = df_eval_selected.loc[df_eval_selected["Accuracy"].idxmax()]
    best_accuracy_app = best_accuracy_row["appName"]
    best_accuracy_value = float(best_accuracy_row["Accuracy"]) * 100

    insight_text = (
        f"Pada periode terpilih, <strong>{best_sentiment_app}</strong> memiliki proporsi sentimen positif "
        f"tertinggi sebesar <strong>{best_sentiment_pct:.1f}%</strong>. "
        f"Pada evaluasi data testing model {model_config['short']}, Accuracy tertinggi terdapat pada "
        f"<strong>{best_accuracy_app}</strong> sebesar <strong>{best_accuracy_value:.2f}%</strong>."
    )
else:
    insight_text = (
        f"Pada periode terpilih, <strong>{best_sentiment_app}</strong> memiliki proporsi sentimen positif "
        f"tertinggi sebesar <strong>{best_sentiment_pct:.1f}%</strong>."
    )

st.markdown(
    f'<div class="insight-box"><strong>Insight cepat:</strong> {insight_text}</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="info-note">Filter sentimen digunakan pada grafik dan detail. KPI Positif/Negatif tetap menampilkan komposisi lengkap untuk aplikasi dan periode yang dipilih. Accuracy dan F1-Score berasal dari data testing, bukan dari prediksi seluruh Data Preparation.</div>',
    unsafe_allow_html=True
)


# Level 2 - Main chart
render_section(
    "Tren Sentimen Bulanan",
    "Grafik utama berukuran paling besar untuk melihat perubahan sentimen dari waktu ke waktu. Warna menunjukkan aplikasi; bentuk garis menunjukkan kategori sentimen."
)

trend_data = df_visual.copy()
trend_data["Bulan"] = trend_data["date"].dt.to_period("M").dt.to_timestamp()
trend_data = (
    trend_data.groupby(["Bulan", "appName", "sentimen"])
    .size()
    .reset_index(name="Jumlah")
)

if trend_data.empty:
    st.info("Tidak ada data untuk grafik tren pada filter saat ini.")
else:
    fig_trend = px.line(
        trend_data,
        x="Bulan",
        y="Jumlah",
        color="appName",
        line_dash="sentimen",
        symbol="sentimen",
        markers=True,
        color_discrete_map=warnaApp,
        category_orders={
            "appName": APP_ORDER,
            "sentimen": ["Positif", "Negatif"]
        },
        labels={
            "Bulan": "Periode",
            "Jumlah": "Jumlah Ulasan",
            "appName": "Aplikasi",
            "sentimen": "Sentimen"
        }
    )

    fig_trend.update_traces(
        line=dict(width=3),
        marker=dict(size=7),
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "Periode: %{x|%b %Y}<br>"
            "Jumlah: %{y:,}<extra></extra>"
        )
    )

    fig_trend.update_layout(
        height=470,
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=35, r=25, t=30, b=35),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="left",
            x=0
        ),
        font=dict(color="#344054", size=12),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="#edf0f4", zeroline=False)
    )

    st.plotly_chart(
        fig_trend,
        use_container_width=True,
        config=PLOTLY_CONFIG
    )


# Context charts
render_section(
    "Perbandingan Antar Aplikasi",
    "Grafik pendukung membantu menjelaskan komposisi sentimen dan pola rating pada aplikasi yang dipilih."
)

context_col_1, context_col_2 = st.columns([1.2, 1])

with context_col_1:
    sentiment_compare = (
        df_visual.groupby(["appName", "sentimen"])
        .size()
        .reset_index(name="Jumlah")
    )

    fig_sentiment = go.Figure()
    pattern_map = {"Positif": "", "Negatif": "/"}
    opacity_map = {"Positif": 1.0, "Negatif": 0.58}

    for app_name in APP_ORDER:
        if app_name not in selected_apps:
            continue
        for sentiment_name in ["Positif", "Negatif"]:
            if sentiment_name not in selected_sentiments:
                continue

            row = sentiment_compare[
                (sentiment_compare["appName"] == app_name)
                & (sentiment_compare["sentimen"] == sentiment_name)
            ]
            value = int(row["Jumlah"].iloc[0]) if not row.empty else 0

            fig_sentiment.add_trace(
                go.Bar(
                    x=[app_name],
                    y=[value],
                    name=f"{app_name} · {sentiment_name}",
                    marker=dict(
                        color=warnaApp[app_name],
                        opacity=opacity_map[sentiment_name],
                        pattern=dict(shape=pattern_map[sentiment_name])
                    ),
                    text=[f"{value:,}"],
                    textposition="outside",
                    cliponaxis=False,
                    hovertemplate=(
                        f"<b>{app_name}</b><br>"
                        f"Sentimen: {sentiment_name}<br>"
                        "Jumlah: %{y:,}<extra></extra>"
                    )
                )
            )

    fig_sentiment.update_layout(
        title=dict(text="Jumlah Sentimen per Aplikasi", x=0.02, xanchor="left"),
        height=390,
        barmode="group",
        bargap=0.28,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=20, t=65, b=35),
        xaxis_title="",
        yaxis_title="Jumlah Ulasan",
        yaxis=dict(gridcolor="#edf0f4", zeroline=False),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="center",
            x=0.5,
            font=dict(size=10)
        ),
        font=dict(color="#344054", size=12)
    )

    st.plotly_chart(
        fig_sentiment,
        use_container_width=True,
        config=PLOTLY_CONFIG
    )

with context_col_2:
    rating_data = (
        df_visual.dropna(subset=["score"])
        .groupby(["score", "appName"])
        .size()
        .reset_index(name="Jumlah")
    )

    fig_rating = px.bar(
        rating_data,
        x="score",
        y="Jumlah",
        color="appName",
        barmode="group",
        color_discrete_map=warnaApp,
        category_orders={"appName": APP_ORDER},
        labels={
            "score": "Rating Bintang",
            "Jumlah": "Jumlah Ulasan",
            "appName": "Aplikasi"
        }
    )

    fig_rating.update_traces(
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "Rating: %{x:.0f}<br>"
            "Jumlah: %{y:,}<extra></extra>"
        )
    )

    fig_rating.update_layout(
        title=dict(text="Distribusi Rating", x=0.02, xanchor="left"),
        height=390,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=20, t=65, b=35),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="center",
            x=0.5
        ),
        xaxis=dict(dtick=1, showgrid=False),
        yaxis=dict(gridcolor="#edf0f4", zeroline=False),
        font=dict(color="#344054", size=12)
    )

    st.plotly_chart(
        fig_rating,
        use_container_width=True,
        config=PLOTLY_CONFIG
    )


# Analisis kata interaktif
render_section(
    "Kata Dominan",
    "Pengganti Word Cloud statis: horizontal bar chart dapat di-hover dan difilter sehingga kata dominan lebih mudah dibandingkan."
)

word_filter_1, word_filter_2, word_filter_3 = st.columns([1, 1, 1])

with word_filter_1:
    word_app = st.selectbox(
        "Aplikasi untuk analisis kata",
        options=selected_apps,
        index=0,
        key="word_app"
    )

with word_filter_2:
    word_sentiment_options = [
        sentiment for sentiment in ["Positif", "Negatif"]
        if sentiment in selected_sentiments
    ]
    word_sentiment = st.selectbox(
        "Sentimen",
        options=word_sentiment_options,
        index=0,
        key="word_sentiment"
    )

with word_filter_3:
    top_n = st.slider(
        "Jumlah kata",
        min_value=8,
        max_value=25,
        value=15,
        step=1,
        key="top_n_words"
    )

word_source = df_visual[
    (df_visual["appName"] == word_app)
    & (df_visual["sentimen"] == word_sentiment)
]["content"]

word_data = top_words(word_source, top_n=top_n)

if word_data.empty:
    st.info("Kata dominan tidak tersedia pada filter saat ini.")
else:
    word_data = word_data.sort_values("Frekuensi", ascending=True)
    fig_words = go.Figure(
        go.Bar(
            x=word_data["Frekuensi"],
            y=word_data["Kata"],
            orientation="h",
            marker=dict(
                color=warnaApp[word_app],
                line=dict(color=rgba(warnaApp[word_app], 0.95), width=1)
            ),
            text=word_data["Frekuensi"],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>Frekuensi: %{x:,}<extra></extra>"
            )
        )
    )

    fig_words.update_layout(
        title=dict(
            text=f"Top {top_n} Kata · {word_app} · {word_sentiment}",
            x=0.02,
            xanchor="left"
        ),
        height=max(380, top_n * 27),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=35, r=60, t=65, b=35),
        xaxis_title="Frekuensi Kemunculan",
        yaxis_title="",
        xaxis=dict(gridcolor="#edf0f4", zeroline=False),
        font=dict(color="#344054", size=12)
    )

    st.plotly_chart(
        fig_words,
        use_container_width=True,
        config=PLOTLY_CONFIG
    )


# Evaluation
render_section(
    f"Evaluasi Kinerja {model_config['short']}",
    "Bagian evaluasi hanya menggunakan hasil data testing. Metrik tidak dihitung dari prediksi seluruh Data Preparation."
)

if df_eval_selected.empty:
    st.info("Data evaluasi untuk aplikasi terpilih tidak tersedia.")
else:
    metrics = ["Accuracy", "Precision", "Recall", "Specificity", "F1-Score"]

    eval_long = df_eval_selected[
        ["appName"] + metrics
    ].melt(
        id_vars="appName",
        var_name="Metrik",
        value_name="Nilai"
    )
    eval_long["Persen"] = eval_long["Nilai"] * 100

    fig_eval = px.bar(
        eval_long,
        x="Metrik",
        y="Persen",
        color="appName",
        barmode="group",
        color_discrete_map=warnaApp,
        category_orders={
            "appName": APP_ORDER,
            "Metrik": metrics
        },
        text="Persen",
        labels={
            "Persen": "Nilai (%)",
            "appName": "Aplikasi"
        }
    )

    fig_eval.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "%{x}: %{y:.2f}%<extra></extra>"
        )
    )

    fig_eval.update_layout(
        height=430,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=35, r=25, t=35, b=35),
        yaxis=dict(
            title="Nilai (%)",
            range=[0, 105],
            gridcolor="#edf0f4",
            zeroline=False
        ),
        xaxis=dict(title="", showgrid=False),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="left",
            x=0
        ),
        font=dict(color="#344054", size=12)
    )

    st.plotly_chart(
        fig_eval,
        use_container_width=True,
        config=PLOTLY_CONFIG
    )

    # Confusion matrix detail
    cm_col_1, cm_col_2 = st.columns([1.25, 0.75])

    with cm_col_2:
        cm_app = st.selectbox(
            "Detail Confusion Matrix",
            options=selected_apps,
            index=0,
            key="cm_app"
        )

        cm_row = df_eval_selected[
            df_eval_selected["appName"] == cm_app
        ]

        if not cm_row.empty:
            cm_row = cm_row.iloc[0]
            st.metric("Data Train", f"{int(cm_row['dataTrain']):,}")
            st.metric("Data Test", f"{int(cm_row['dataTest']):,}")
            st.metric("Accuracy", f"{float(cm_row['Accuracy']) * 100:.2f}%")
            st.metric("F1-Score", f"{float(cm_row['F1-Score']) * 100:.2f}%")

    with cm_col_1:
        cm_row = df_eval_selected[
            df_eval_selected["appName"] == cm_app
        ]

        if not cm_row.empty:
            cm_row = cm_row.iloc[0]
            tn = int(cm_row["TN"])
            fp = int(cm_row["FP"])
            fn = int(cm_row["FN"])
            tp = int(cm_row["TP"])

            matrix_values = [[tn, fp], [fn, tp]]
            matrix_text = [
                [f"TN<br><b>{tn}</b>", f"FP<br><b>{fp}</b>"],
                [f"FN<br><b>{fn}</b>", f"TP<br><b>{tp}</b>"]
            ]

            brand = warnaApp[cm_app]
            colorscale = [
                [0.0, rgba(brand, 0.08)],
                [0.35, rgba(brand, 0.25)],
                [0.70, rgba(brand, 0.60)],
                [1.0, rgba(brand, 0.95)]
            ]

            fig_cm = go.Figure(
                go.Heatmap(
                    z=matrix_values,
                    x=["Prediksi Negatif", "Prediksi Positif"],
                    y=["Aktual Negatif", "Aktual Positif"],
                    colorscale=colorscale,
                    showscale=False,
                    text=matrix_text,
                    texttemplate="%{text}",
                    textfont=dict(size=16, color="#172033"),
                    hovertemplate=(
                        "%{y}<br>%{x}<br>Jumlah: %{z:,}<extra></extra>"
                    ),
                    xgap=4,
                    ygap=4
                )
            )

            fig_cm.update_layout(
                title=dict(
                    text=f"Confusion Matrix · {cm_app}",
                    x=0.02,
                    xanchor="left"
                ),
                height=430,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=35, r=25, t=65, b=35),
                xaxis=dict(side="top", fixedrange=True),
                yaxis=dict(autorange="reversed", fixedrange=True),
                font=dict(color="#344054", size=12)
            )

            st.plotly_chart(
                fig_cm,
                use_container_width=True,
                config=PLOTLY_CONFIG
            )

    # Evaluation detail table
    with st.expander("Lihat tabel evaluasi lengkap", expanded=False):
        evaluation_table = df_eval_selected.copy()
        for metric in metrics:
            evaluation_table[metric] = (
                pd.to_numeric(evaluation_table[metric], errors="coerce") * 100
            ).round(2)

        columns_eval = [
            "appName", "algorithm", "dataTrain", "dataTest",
            "TN", "FP", "FN", "TP"
        ] + metrics

        columns_eval = [
            column for column in columns_eval
            if column in evaluation_table.columns
        ]

        st.dataframe(
            evaluation_table[columns_eval],
            use_container_width=True,
            hide_index=True
        )


# Level 3 - Details
render_section(
    "Detail Data Ulasan",
    "Detail ditempatkan di bagian bawah untuk investigasi. Prediksi pada tabel berasal dari seluruh Data Preparation dan tidak digunakan untuk menghitung metrik evaluasi."
)

original_reviews = load_original_reviews()
detail_data = df_visual.copy()

if not original_reviews.empty:
    detail_data = detail_data.merge(
        original_reviews,
        on=["reviewId", "appName"],
        how="left"
    )
    detail_data["Teks Ulasan"] = detail_data["originalContent"].fillna(
        detail_data["content"]
    )
else:
    detail_data["Teks Ulasan"] = detail_data["content"]

search_col, rating_col, rows_col = st.columns([1.5, 1, 0.8])

with search_col:
    search_text = st.text_input(
        "Cari kata pada ulasan",
        value="",
        placeholder="Contoh: transaksi, error, cepat...",
        key="review_search"
    )

with rating_col:
    available_scores = sorted(
        [int(score) for score in detail_data["score"].dropna().unique()]
    )
    selected_scores = st.multiselect(
        "Rating",
        options=available_scores,
        default=available_scores,
        key="review_rating"
    )

with rows_col:
    max_rows = st.selectbox(
        "Jumlah baris",
        options=[25, 50, 100, 250],
        index=1,
        key="review_rows"
    )

if selected_scores:
    detail_data = detail_data[detail_data["score"].isin(selected_scores)]

if search_text.strip():
    detail_data = detail_data[
        detail_data["Teks Ulasan"].astype(str).str.contains(
            search_text.strip(),
            case=False,
            na=False,
            regex=False
        )
    ]

show_columns = [
    "reviewId", "appName", "date", "score", "actualLabel",
    "sentimen", "Teks Ulasan"
]

detail_view = detail_data[show_columns].copy()
detail_view = detail_view.rename(columns={
    "reviewId": "Review ID",
    "appName": "Aplikasi",
    "date": "Tanggal",
    "score": "Rating",
    "actualLabel": "Label Aktual",
    "sentimen": "Prediksi Model"
})
detail_view["Label Aktual"] = detail_view["Label Aktual"].str.capitalize()
detail_view = detail_view.sort_values("Tanggal", ascending=False)

st.dataframe(
    detail_view.head(max_rows),
    use_container_width=True,
    hide_index=True
)

st.caption(
    f"Menampilkan {min(max_rows, len(detail_view)):,} dari {len(detail_view):,} ulasan yang sesuai filter detail."
)

csv_download = detail_view.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download data ulasan terfilter",
    data=csv_download,
    file_name=f"detail_{model_config['short'].lower()}_terfilter.csv",
    mime="text/csv",
    key="download_filtered_reviews"
)


# Footer metodologi singkat
st.divider()
st.markdown(
    f"""
    <div style="text-align:center;color:#667085;font-size:12px;line-height:1.6;padding:8px 0 4px 0;">
        Dashboard {model_config['short']} · DANA, GoPay, ShopeePay ·
        Hasil klasifikasi seluruh Data Preparation digunakan untuk visualisasi,
        sedangkan Confusion Matrix dan metrik evaluasi berasal khusus dari data testing.
    </div>
    """,
    unsafe_allow_html=True
)
