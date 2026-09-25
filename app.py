from __future__ import annotations

from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from config import LOG_DIR, PROCESSED_DIR
from ui_helpers import filter_catalog, has_real_values, is_rare, prepare_catalog, rarity_column, unique_values
from utils.io_utils import read_json

st.set_page_config(
    page_title="PlantMatch",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Visual layer only: no external assets, fonts or UI dependencies are required.
st.markdown(
    """
    <style>
      :root {
        --pm-bg: #f3f5ef;
        --pm-surface: #fbfcf8;
        --pm-surface-2: #eef2e8;
        --pm-forest: #20392b;
        --pm-olive: #687456;
        --pm-emerald: #2f7d5c;
        --pm-emerald-soft: #dfece4;
        --pm-text: #1f2a23;
        --pm-muted: #687168;
        --pm-line: #d7ddd2;
        --pm-warm: #f0ede5;
      }

      [data-testid="stAppViewContainer"] {
        background:
          radial-gradient(circle at 96% 3%, rgba(104, 116, 86, .10), transparent 28rem),
          radial-gradient(circle at 2% 24%, rgba(47, 125, 92, .055), transparent 24rem),
          var(--pm-bg);
        color: var(--pm-text);
      }
      [data-testid="stHeader"] { background: rgba(243,245,239,.88); }
      [data-testid="stSidebar"] {
        background: #e9eee5;
        border-right: 1px solid var(--pm-line);
      }
      [data-testid="stSidebar"] > div { padding-top: 1.35rem; }
      .block-container {
        padding-top: 1.9rem;
        padding-bottom: 4rem;
        max-width: 1240px;
      }
      h1, h2, h3 { color: var(--pm-forest); letter-spacing: -0.025em; }
      h1 { font-size: clamp(2rem, 4vw, 3.3rem) !important; line-height: 1.05 !important; }
      p, label, [data-testid="stCaptionContainer"] { color: var(--pm-muted); }

      .pm-brand {
        display:flex; align-items:center; gap:.7rem; margin-bottom:1.4rem;
        color:var(--pm-forest); font-weight:750; font-size:1.18rem;
      }
      .pm-brand-mark {
        width:2rem; height:2rem; display:grid; place-items:center;
        border-radius:10px; background:var(--pm-forest); color:#f4f7f1;
        font-size:1rem;
      }
      .pm-kicker {
        text-transform: uppercase; letter-spacing: .13em; font-size: .72rem;
        font-weight: 750; color: var(--pm-olive); margin-bottom:.45rem;
      }
      .pm-hero {
        border:1px solid var(--pm-line); border-radius:22px;
        background:linear-gradient(120deg, rgba(251,252,248,.97), rgba(238,242,232,.93));
        padding:1.6rem 1.7rem; margin-bottom:1.25rem;
        box-shadow:0 10px 30px rgba(32,57,43,.055);
      }
      .pm-hero-title { color:var(--pm-forest); font-size:1.25rem; font-weight:750; margin-bottom:.3rem; }
      .pm-hero-copy { color:var(--pm-muted); max-width:760px; line-height:1.55; }
      .pm-leafline { color:var(--pm-emerald); letter-spacing:.22rem; font-size:.9rem; margin-bottom:.75rem; }

      .pm-result-meta {
        display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between;
        gap:.7rem; margin:1.4rem 0 .8rem 0;
      }
      .pm-result-count { font-size:1.02rem; font-weight:700; color:var(--pm-forest); }
      .pm-result-sub { color:var(--pm-muted); font-size:.88rem; }

      .pm-title-row { display:flex; align-items:center; gap:.55rem; flex-wrap:wrap; }
      .pm-plant-title { font-size:1.35rem; font-weight:760; color:var(--pm-forest); line-height:1.1; }
      .pm-scientific { font-style:italic; color:var(--pm-muted); font-size:.92rem; margin-top:.24rem; }
      .pm-badge {
        display:inline-block; padding:.2rem .55rem; border-radius:999px;
        border:1px solid #cbd4c6; background:#eef3eb; color:#4e604f;
        font-size:.72rem; font-weight:700; letter-spacing:.015em;
      }
      .pm-badge-rare {
        border-color:#c4a971; background:#f5efe1; color:#765d2e;
      }
      .pm-care-grid {
        display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.48rem .65rem;
        margin:.55rem 0 .25rem 0;
      }
      .pm-care {
        padding:.5rem .6rem; border-radius:10px; background:#f2f4ee;
        border:1px solid #e0e4da; color:#435047; font-size:.82rem;
      }
      .pm-price { color:var(--pm-forest); font-size:1.45rem; font-weight:780; }
      .pm-small { color:var(--pm-muted); font-size:.82rem; }
      .pm-store-head { color:var(--pm-forest); font-weight:720; font-size:.9rem; }
      .pm-status-ok { color:#2f7456; font-weight:700; }
      .pm-status-off { color:#8c6657; font-weight:700; }
      .pm-status-partial { color:#8a6b32; font-weight:700; }
      .pm-code-note { color:var(--pm-muted); font-size:.82rem; }

      [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--pm-line) !important;
        border-radius: 18px !important;
        background: rgba(251,252,248,.88);
        box-shadow: 0 7px 22px rgba(32,57,43,.035);
      }
      [data-testid="stMetric"] {
        background: rgba(251,252,248,.92);
        border: 1px solid var(--pm-line);
        padding: 13px 15px;
        border-radius: 14px;
        box-shadow: 0 5px 18px rgba(32,57,43,.03);
      }
      [data-testid="stMetricLabel"] { color:var(--pm-muted); }
      [data-testid="stMetricValue"] { color:var(--pm-forest); }
      div[data-testid="stDataFrame"] {
        border:1px solid var(--pm-line); border-radius:14px; overflow:hidden;
      }
      div[data-baseweb="input"] > div,
      div[data-baseweb="select"] > div,
      div[data-baseweb="base-input"] > div {
        border-radius:10px !important;
      }
      .stButton > button, .stLinkButton > a {
        border-radius:10px !important;
        border:1px solid #b9c4b4 !important;
        font-weight:680 !important;
      }
      .stButton > button[kind="primary"] {
        background:var(--pm-forest) !important; color:white !important;
        border-color:var(--pm-forest) !important;
      }
      .stLinkButton > a:hover, .stButton > button:hover {
        border-color:var(--pm-emerald) !important;
        color:var(--pm-emerald) !important;
      }
      .stButton > button[kind="primary"]:hover { color:white !important; background:#294b39 !important; }
      hr { border-color:var(--pm-line) !important; }

      @media (max-width: 720px) {
        .block-container { padding-left:1rem; padding-right:1rem; padding-top:1rem; }
        .pm-hero { padding:1.2rem; border-radius:16px; }
        .pm-care-grid { grid-template-columns:1fr; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

CATALOG_PATH = PROCESSED_DIR / "plants_catalog.csv"
LATEST_RUN_PATH = PROCESSED_DIR / "latest_run.json"


def load_catalog() -> pd.DataFrame:
    if not CATALOG_PATH.exists():
        return pd.DataFrame()
    return prepare_catalog(pd.read_csv(CATALOG_PATH))


def pretty_status(value: str) -> str:
    return {"ok": "Correcto", "partial": "Parcial", "failed": "Fallido"}.get(value, value or "Sin datos")


def value_or_dash(value: object) -> str:
    if value is None or pd.isna(value):
        return "—"
    text = str(value).strip()
    return text if text else "—"


def money(value: object) -> str:
    try:
        return f"${float(value):,.0f} MXN"
    except (TypeError, ValueError):
        return "—"


def rarity_badge(row: pd.Series, rare_col: str | None) -> str:
    if not rare_col or rare_col not in row or not is_rare(row.get(rare_col)):
        return ""
    return '<span class="pm-badge pm-badge-rare">Colección especial</span>'


def render_store_offer(offer: pd.Series) -> None:
    left, mid, right = st.columns([2.2, 1.35, 1.25], vertical_alignment="center")
    with left:
        st.markdown(f"<div class='pm-store-head'>{escape(value_or_dash(offer.get('store')))}</div>", unsafe_allow_html=True)
        st.caption(value_or_dash(offer.get("size")))
    with mid:
        st.markdown(f"**{money(offer.get('price_mxn'))}**")
        if bool(offer.get("available", False)):
            st.markdown("<span class='pm-status-ok'>● Disponible</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span class='pm-status-off'>● Agotada</span>", unsafe_allow_html=True)
    with right:
        product_url = value_or_dash(offer.get("product_url"))
        source_url = value_or_dash(offer.get("source_url"))
        target = product_url if product_url != "—" else source_url
        if target != "—":
            st.link_button("Consultar producto", target, use_container_width=True)
        else:
            st.caption("Sin enlace disponible")


def render_plant_card(group: pd.DataFrame, rare_col: str | None) -> None:
    row = group.iloc[0]
    available_group = group[group["available"] == True]  # noqa: E712
    price_source = available_group if not available_group.empty else group
    min_price = price_source["price_mxn"].min()

    with st.container(border=True):
        intro, price = st.columns([3.2, 1], vertical_alignment="top")
        with intro:
            family = value_or_dash(row.get("family"))
            family_badge = f'<span class="pm-badge">{escape(family)}</span>' if family != "—" else ""
            rare_badge = rarity_badge(row, rare_col)
            badges = " ".join(x for x in (family_badge, rare_badge) if x)
            st.markdown(
                f"""
                <div class="pm-title-row">
                  <div class="pm-plant-title">{escape(value_or_dash(row.get('common_name') or row.get('product_name')))}</div>
                  {badges}
                </div>
                <div class="pm-scientific">{escape(value_or_dash(row.get('scientific_name')))}</div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div class="pm-care-grid">
                  <div class="pm-care">☀ &nbsp;<strong>Luz</strong><br>{escape(value_or_dash(row.get('sunlight')))}</div>
                  <div class="pm-care">◌ &nbsp;<strong>Riego</strong><br>{escape(value_or_dash(row.get('watering')))}</div>
                  <div class="pm-care">⌂ &nbsp;<strong>Ubicación</strong><br>{escape(value_or_dash(row.get('placement')))}</div>
                  <div class="pm-care">⌁ &nbsp;<strong>Tipo</strong><br>{escape(value_or_dash(row.get('plant_type')))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with price:
            st.markdown("<div class='pm-small'>Mejor precio observado</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='pm-price'>{money(min_price)}</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='pm-small'>★ {float(row.get('avg_rating', 0)):.1f} · {int(row.get('review_count', 0))} reseñas<br>{group['store'].nunique()} tienda(s)</div>",
                unsafe_allow_html=True,
            )

        st.divider()
        st.markdown("**Dónde comprar**")
        ordered = group.sort_values(["available", "price_mxn"], ascending=[False, True])
        for _, offer in ordered.iterrows():
            render_store_offer(offer)


def clear_explore_filters() -> None:
    keys = [
        "search_name", "filter_family", "filter_sunlight", "filter_watering",
        "filter_placement", "filter_type", "filter_store", "filter_max_price",
        "filter_min_rating", "filter_available", "filter_rare",
    ]
    for key in keys:
        st.session_state.pop(key, None)


df = load_catalog()
latest = read_json(LATEST_RUN_PATH, default={}) or {}
rare_col = rarity_column(df) if not df.empty else None

with st.sidebar:
    st.markdown('<div class="pm-brand"><span class="pm-brand-mark">⌁</span><span>PlantMatch</span></div>', unsafe_allow_html=True)
    page = st.radio(
        "Sección",
        ["Explorar plantas", "Comparar", "Pipeline"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("Arquitectura de ingesta híbrida")
    st.caption("Ingeniería de Datos · 2026")

if page == "Explorar plantas":
    st.markdown('<div class="pm-kicker">Catálogo botánico integrado</div>', unsafe_allow_html=True)
    st.title("Encuentra la planta que encaja contigo")
    st.markdown(
        """
        <div class="pm-hero">
          <div class="pm-leafline">⌁ · ⌁ · ⌁</div>
          <div class="pm-hero-title">Filtra por necesidades reales, después compara dónde comprar.</div>
          <div class="pm-hero-copy">PlantMatch cruza las ofertas recuperadas por scraping con los rasgos botánicos y las reseñas del pipeline. Los filtros operan sobre el catálogo procesado; no disparan scraping ni llamadas nuevas a la API.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty:
        st.warning("Todavía no hay catálogo procesado. Ejecuta primero `python -m pipeline.orchestrator`.")
        st.stop()

    max_catalog_price = float(df["price_mxn"].dropna().max()) if df["price_mxn"].notna().any() else 100.0
    slider_ceiling = max(100, int(max_catalog_price + 50))

    with st.container(border=True):
        st.markdown("#### Buscar y filtrar")
        top1, top2, top3 = st.columns([2.1, 1.25, 1.25])
        with top1:
            query = st.text_input(
                "Buscar por nombre",
                placeholder="Ej. Monstera, Aloe vera…",
                key="search_name",
                help="Busca en nombre común, nombre publicado por la tienda y nombre científico.",
            )
        with top2:
            families = st.multiselect("Familia", unique_values(df, "family"), key="filter_family")
        with top3:
            sunlight = st.multiselect("Luz", unique_values(df, "sunlight"), key="filter_sunlight")

        row2a, row2b, row2c = st.columns(3)
        with row2a:
            watering = st.multiselect("Riego", unique_values(df, "watering"), key="filter_watering")
        with row2b:
            placements = st.multiselect("Interior / exterior", unique_values(df, "placement"), key="filter_placement")
        with row2c:
            plant_types = st.multiselect("Tipo de planta", unique_values(df, "plant_type"), key="filter_type")

        with st.expander("Más filtros", expanded=False):
            a, b, c = st.columns(3)
            with a:
                stores = st.multiselect("Tienda", unique_values(df, "store"), key="filter_store")
            with b:
                max_price = st.slider(
                    "Precio máximo (MXN)",
                    min_value=50,
                    max_value=slider_ceiling,
                    value=min(int(max_catalog_price), slider_ceiling),
                    key="filter_max_price",
                )
            with c:
                min_rating = st.slider("Calificación mínima", 0.0, 5.0, 0.0, 0.1, key="filter_min_rating")

            d, e = st.columns(2)
            with d:
                available_only = st.checkbox("Solo disponibles", value=True, key="filter_available")
            with e:
                if rare_col:
                    rare_only = st.checkbox("Solo plantas raras / especiales", value=False, key="filter_rare")
                else:
                    rare_only = False
                    st.caption("Rareza: preparada para el campo `rareza`; el dataset actual no contiene clasificaciones de rareza.")

        controls_left, controls_right = st.columns([1, 4])
        with controls_left:
            st.button("Mostrar todas", use_container_width=True, on_click=clear_explore_filters)
        with controls_right:
            if not has_real_values(df["family"]):
                st.caption("La familia aparecerá al regenerar el catálogo con la versión actual de la API botánica del proyecto.")

    # Defaults when the advanced expander has not instantiated a value yet.
    stores = st.session_state.get("filter_store", [])
    max_price = st.session_state.get("filter_max_price", min(int(max_catalog_price), slider_ceiling))
    min_rating = st.session_state.get("filter_min_rating", 0.0)
    available_only = st.session_state.get("filter_available", True)
    rare_only = st.session_state.get("filter_rare", False) if rare_col else False

    filtered = filter_catalog(
        df,
        query=query,
        families=families,
        sunlight=sunlight,
        watering=watering,
        placements=placements,
        plant_types=plant_types,
        stores=stores,
        max_price=max_price,
        min_rating=min_rating,
        available_only=available_only,
        rare_only=rare_only,
    )

    species_count = filtered["product_id"].nunique() if not filtered.empty else 0
    st.markdown(
        f"""
        <div class="pm-result-meta">
          <div><span class="pm-result-count">{species_count} plantas</span><br><span class="pm-result-sub">{len(filtered)} opciones de compra después de aplicar filtros</span></div>
          <div class="pm-result-sub">Datos integrados por <code>product_id</code></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if filtered.empty:
        st.info("No hay resultados con esos filtros. Prueba ampliar precio, ubicación, luz o riego.")
    else:
        for _, group in filtered.groupby("product_id", sort=False):
            render_plant_card(group, rare_col)

elif page == "Comparar":
    st.markdown('<div class="pm-kicker">Comparación directa</div>', unsafe_allow_html=True)
    st.title("Compara plantas lado a lado")
    st.markdown(
        """
        <div class="pm-hero">
          <div class="pm-hero-title">Mismos datos, una lectura más rápida.</div>
          <div class="pm-hero-copy">Selecciona hasta tres especies para contrastar familia, cuidados, ubicación, precio y valoración sin perder la información de las tiendas.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty:
        st.warning("Ejecuta el pipeline antes de comparar.")
        st.stop()

    species = df.drop_duplicates("product_id").copy()
    labels = {
        row["product_id"]: f"{value_or_dash(row.get('common_name'))} · {value_or_dash(row.get('scientific_name'))}"
        for _, row in species.iterrows()
    }
    options = list(labels.keys())
    selected = st.multiselect(
        "Selecciona hasta 3 plantas",
        options,
        default=options[: min(3, len(options))],
        max_selections=3,
        format_func=lambda x: labels.get(x, x),
    )

    comparison: dict[str, dict[str, object]] = {}
    for pid in selected:
        group = df[df["product_id"] == pid]
        if group.empty:
            continue
        row = group.iloc[0]
        name = value_or_dash(row.get("common_name") or row.get("product_name"))
        available_group = group[group["available"] == True]  # noqa: E712
        price_source = available_group if not available_group.empty else group
        comparison[name] = {
            "Nombre científico": value_or_dash(row.get("scientific_name")),
            "Familia": value_or_dash(row.get("family")),
            "Tipo": value_or_dash(row.get("plant_type")),
            "Luz": value_or_dash(row.get("sunlight")),
            "Riego": value_or_dash(row.get("watering")),
            "Interior / Exterior": value_or_dash(row.get("placement")),
            "Precio mínimo": money(price_source["price_mxn"].min()),
            "Calificación": f"★ {float(row.get('avg_rating', 0)):.1f}",
            "Reseñas": int(row.get("review_count", 0)),
            "Tiendas": int(group["store"].nunique()),
        }
        if rare_col:
            comparison[name]["Rareza"] = value_or_dash(row.get(rare_col))

    if comparison:
        comparison_df = pd.DataFrame(comparison)
        st.dataframe(comparison_df, use_container_width=True)

        st.markdown("### Opciones de compra")
        for pid in selected:
            group = df[df["product_id"] == pid]
            if group.empty:
                continue
            row = group.iloc[0]
            with st.expander(value_or_dash(row.get("common_name") or row.get("product_name")), expanded=False):
                for _, offer in group.sort_values(["available", "price_mxn"], ascending=[False, True]).iterrows():
                    render_store_offer(offer)
    else:
        st.info("Selecciona al menos una planta para iniciar la comparación.")

else:
    st.markdown('<div class="pm-kicker">Operación y trazabilidad</div>', unsafe_allow_html=True)
    st.title("Estado del pipeline")
    st.markdown(
        """
        <div class="pm-hero">
          <div class="pm-hero-title">Vista técnica separada de la experiencia del catálogo.</div>
          <div class="pm-hero-copy">Aquí se conserva la evidencia operativa del proyecto: ingesta, calidad, errores, fuentes procesadas, tiempos y logs de la última ejecución.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not latest:
        st.warning("No hay una ejecución registrada todavía.")
        st.stop()

    status = latest.get("status", "unknown")
    status_class = "pm-status-ok" if status == "ok" else ("pm-status-partial" if status == "partial" else "pm-status-off")
    st.markdown(
        f"Estado actual: <span class='{status_class}'>● {escape(pretty_status(status))}</span>",
        unsafe_allow_html=True,
    )

    cols = st.columns(6)
    cols[0].metric("Productos", latest.get("products", 0))
    cols[1].metric("Reseñas", latest.get("reviews", 0))
    cols[2].metric("Rasgos", latest.get("traits", 0))
    cols[3].metric("Errores", latest.get("errors", 0))
    cols[4].metric("Calidad cruda", f"{latest.get('quality_pct', 0)}%")
    cols[5].metric("Duración", f"{latest.get('duration_seconds', 0)} s")

    left, right = st.columns([1.15, 1])
    with left:
        st.markdown("### Fuentes procesadas")
        counts = latest.get("store_counts", {})
        source_rows = [{"Fuente": k, "Registros": v, "Estado": "Procesada"} for k, v in counts.items()]
        source_rows.extend([
            {"Fuente": "API de reseñas", "Registros": latest.get("reviews", 0), "Estado": "Procesada" if latest.get("reviews", 0) else "Sin datos"},
            {"Fuente": "API botánica", "Registros": latest.get("traits", 0), "Estado": "Procesada" if latest.get("traits", 0) else "Sin datos"},
        ])
        st.dataframe(pd.DataFrame(source_rows), use_container_width=True, hide_index=True)

    with right:
        st.markdown("### Última ejecución")
        with st.container(border=True):
            st.markdown(f"**Run ID**  `{latest.get('run_id', '—')}`")
            st.markdown(f"**Inicio**  {latest.get('started_at', '—')}")
            st.markdown(f"**Fin**  {latest.get('finished_at', '—')}")
            st.markdown(f"**Landing**  `{latest.get('landing_path', '—')}`")

    st.markdown("### Log reciente")
    log_path = LOG_DIR / "pipeline.log"
    if log_path.exists():
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        recent_lines = lines[-24:]
        failed_attempts = sum("Petición fallida" in line for line in recent_lines)
        if failed_attempts:
            st.caption(f"Intentos de red fallidos visibles en el tramo reciente del log: {failed_attempts}. Los reintentos son gestionados por `request_with_retry`.")
        with st.expander("Ver últimas líneas del log", expanded=True):
            st.code("\n".join(recent_lines), language="text")
    else:
        st.caption("Sin log todavía.")
