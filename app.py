from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st

from config import LOG_DIR, PROCESSED_DIR
from utils.io_utils import read_json

st.set_page_config(page_title="PlantMatch", page_icon="🌿", layout="wide")

st.markdown(
    """
    <style>
      .block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1180px;}
      h1, h2, h3 {letter-spacing: -0.02em;}
      [data-testid="stMetric"] {background: #efeee8; border: 1px solid #deddd5; padding: 12px 14px; border-radius: 8px;}
      .pm-card {border: 1px solid #d9d8d0; border-radius: 10px; padding: 16px 18px; margin: 10px 0 16px 0; background: #fbfaf6;}
      .pm-muted {color: #666b62; font-size: 0.92rem;}
      .pm-kicker {text-transform: uppercase; letter-spacing: .08em; font-size: .75rem; color:#6e7569;}
      .pm-status-ok {font-weight: 600; color:#40533e;}
      .pm-status-partial {font-weight: 600; color:#7a6238;}
      .pm-status-failed {font-weight: 600; color:#7a4343;}
      div[data-testid="stDataFrame"] {border: 1px solid #dfded7; border-radius: 8px;}
    </style>
    """,
    unsafe_allow_html=True,
)

CATALOG_PATH = PROCESSED_DIR / "plants_catalog.csv"
LATEST_RUN_PATH = PROCESSED_DIR / "latest_run.json"


def load_catalog() -> pd.DataFrame:
    if not CATALOG_PATH.exists():
        return pd.DataFrame()
    df = pd.read_csv(CATALOG_PATH)
    if "available" in df:
        df["available"] = df["available"].astype(str).str.lower().map({"true": True, "false": False}).fillna(df["available"])
    return df


def pretty_status(value: str) -> str:
    return {"ok": "Correcto", "partial": "Parcial", "failed": "Fallido"}.get(value, value)


df = load_catalog()
latest = read_json(LATEST_RUN_PATH, default={}) or {}

st.sidebar.markdown("### PlantMatch")
page = st.sidebar.radio("Sección", ["Explorar plantas", "Comparar", "Pipeline"], label_visibility="collapsed")
st.sidebar.caption("Proyecto de ingesta híbrida · Ingeniería de Datos")

if page == "Explorar plantas":
    st.markdown('<div class="pm-kicker">Catálogo integrado</div>', unsafe_allow_html=True)
    st.title("Encuentra plantas por condiciones reales")
    st.caption("Filtra necesidades de cuidado y compara en qué tienda está disponible cada especie.")

    if df.empty:
        st.warning("Todavía no hay catálogo procesado. Ejecuta primero `python -m pipeline.orchestrator`.")
        st.stop()

    c1, c2, c3 = st.columns(3)
    with c1:
        sunlight = st.multiselect("Luz", sorted(df["sunlight"].dropna().unique().tolist()))
        max_price = st.slider("Precio máximo (MXN)", 50, int(max(100, df["price_mxn"].max() + 50)), int(df["price_mxn"].max()))
    with c2:
        watering = st.multiselect("Riego", sorted(df["watering"].dropna().unique().tolist()))
        min_rating = st.slider("Calificación mínima", 0.0, 5.0, 0.0, 0.1)
    with c3:
        placement = st.multiselect("Ubicación", sorted(df["placement"].dropna().unique().tolist()))
        stores = st.multiselect("Tienda", sorted(df["store"].dropna().unique().tolist()))

    available_only = st.checkbox("Mostrar solo productos disponibles", value=True)

    filtered = df.copy()
    if sunlight:
        filtered = filtered[filtered["sunlight"].isin(sunlight)]
    if watering:
        filtered = filtered[filtered["watering"].isin(watering)]
    if placement:
        filtered = filtered[filtered["placement"].isin(placement)]
    if stores:
        filtered = filtered[filtered["store"].isin(stores)]
    filtered = filtered[filtered["price_mxn"] <= max_price]
    filtered = filtered[filtered["avg_rating"] >= min_rating]
    if available_only:
        filtered = filtered[filtered["available"] == True]  # noqa: E712

    species_count = filtered["product_id"].nunique()
    st.markdown(f"**{species_count} especies** · {len(filtered)} opciones de compra")

    if filtered.empty:
        st.info("No hay resultados con esos filtros. Prueba ampliar precio, luz o riego.")
    else:
        for product_id, group in filtered.groupby("product_id", sort=False):
            row = group.iloc[0]
            min_price = group.loc[group["available"] == True, "price_mxn"].min() if (group["available"] == True).any() else group["price_mxn"].min()  # noqa: E712
            st.markdown('<div class="pm-card">', unsafe_allow_html=True)
            left, right = st.columns([3, 1])
            with left:
                st.subheader(str(row.get("common_name") or row.get("product_name")))
                st.markdown(
                    f"<span class='pm-muted'><i>{row.get('scientific_name', '')}</i> · {row.get('plant_type', '')}</span>",
                    unsafe_allow_html=True,
                )
                st.write(f"**Luz:** {row.get('sunlight', '—')}  ·  **Riego:** {row.get('watering', '—')}  ·  **Ubicación:** {row.get('placement', '—')}")
            with right:
                st.metric("Desde", f"${min_price:,.0f} MXN")
                st.caption(f"★ {float(row.get('avg_rating', 0)):.1f} · {int(row.get('review_count', 0))} reseñas")

            options = group[["store", "price_mxn", "available", "size"]].copy()
            options["Disponibilidad"] = options["available"].map({True: "Disponible", False: "Agotada"})
            options = options.rename(columns={"store": "Tienda", "price_mxn": "Precio MXN", "size": "Presentación"})
            st.dataframe(options[["Tienda", "Precio MXN", "Disponibilidad", "Presentación"]], use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

elif page == "Comparar":
    st.markdown('<div class="pm-kicker">Comparador</div>', unsafe_allow_html=True)
    st.title("Compara especies")
    st.caption("Resume cuidados, valoración y precio mínimo observado.")

    if df.empty:
        st.warning("Ejecuta el pipeline antes de comparar.")
        st.stop()

    labels = (
        df[["product_id", "common_name"]]
        .drop_duplicates("product_id")
        .set_index("product_id")["common_name"]
        .to_dict()
    )
    options = list(labels.keys())
    selected = st.multiselect(
        "Selecciona hasta 3",
        options,
        default=options[:3],
        max_selections=3,
        format_func=lambda x: labels.get(x, x),
    )

    rows = []
    for pid in selected:
        g = df[df["product_id"] == pid]
        if g.empty:
            continue
        r = g.iloc[0]
        rows.append({
            "Planta": r.get("common_name", pid),
            "Precio mínimo": float(g["price_mxn"].min()),
            "Rating": float(r.get("avg_rating", 0)),
            "Reseñas": int(r.get("review_count", 0)),
            "Luz": r.get("sunlight", "—"),
            "Riego": r.get("watering", "—"),
            "Ubicación": r.get("placement", "—"),
            "Tiendas": int(g["store"].nunique()),
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

else:
    st.markdown('<div class="pm-kicker">Operación</div>', unsafe_allow_html=True)
    st.title("Estado del pipeline")
    st.caption("Resumen técnico para la defensa: ingesta, calidad, tolerancia a fallos y trazabilidad.")

    if not latest:
        st.warning("No hay una ejecución registrada todavía.")
        st.stop()

    status = latest.get("status", "unknown")
    cols = st.columns(5)
    cols[0].metric("Estado", pretty_status(status))
    cols[1].metric("Productos", latest.get("products", 0))
    cols[2].metric("Reseñas", latest.get("reviews", 0))
    cols[3].metric("Errores", latest.get("errors", 0))
    cols[4].metric("Calidad cruda", f"{latest.get('quality_pct', 0)}%")

    st.markdown("### Fuentes")
    counts = latest.get("store_counts", {})
    if counts:
        source_df = pd.DataFrame([{"Fuente": k, "Registros": v} for k, v in counts.items()])
        st.dataframe(source_df, use_container_width=True, hide_index=True)

    st.markdown("### Última ejecución")
    st.code(
        f"run_id: {latest.get('run_id')}\n"
        f"inicio: {latest.get('started_at')}\n"
        f"fin: {latest.get('finished_at')}\n"
        f"duración: {latest.get('duration_seconds')} s\n"
        f"landing: {latest.get('landing_path')}",
        language="text",
    )

    st.markdown("### Log reciente")
    log_path = LOG_DIR / "pipeline.log"
    if log_path.exists():
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-18:]
        st.code("\n".join(lines), language="text")
    else:
        st.caption("Sin log todavía.")
