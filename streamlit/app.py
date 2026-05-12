import streamlit as st
import pandas as pd
import altair as alt
from snowflake.snowpark.context import get_active_session

session = get_active_session()

st.title("Sweden: Energy Prices & Weather")


@st.cache_data
def load_data() -> pd.DataFrame:
    df = session.sql("""
        SELECT
            TO_VARCHAR(date, 'YYYY-MM-DD') AS date,
            city,
            bidding_zone,
            temperature_max_c,
            temperature_min_c,
            temperature_mean_c,
            precipitation_mm,
            wind_speed_max_kmh,
            price_avg_eur_mwh,
            price_min_eur_mwh,
            price_max_eur_mwh
        FROM ANALYTICS_DB.STAGING_MART.mart_weather_energy
        ORDER BY date
    """).to_pandas()
    df["date"] = pd.to_datetime(df["DATE"])
    return df


df = load_data()

# --- Sidebar filters ---
with st.sidebar:
    st.header("Filters")

    cities = sorted(df["CITY"].unique())
    selected_city = st.selectbox("City", cities)

    selected_zone = df[df["CITY"] == selected_city]["BIDDING_ZONE"].iloc[0]

    date_min = df["date"].min().date()
    date_max = df["date"].max().date()
    date_range = st.date_input("Date Range", value=(date_min, date_max), min_value=date_min, max_value=date_max)

if len(date_range) == 2:
    start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start_date, end_date = pd.Timestamp(date_min), pd.Timestamp(date_max)

filtered_df = df[
    (df["CITY"] == selected_city)
    & (df["date"] >= start_date)
    & (df["date"] <= end_date)
]

st.subheader(f"Price & Temperature — {selected_city} ({selected_zone})")

price_line = (
    alt.Chart(filtered_df)
    .mark_line(color="#E8501A", strokeWidth=2)
    .encode(
        x=alt.X("date:T", title=""),
        y=alt.Y("PRICE_AVG_EUR_MWH:Q", title="Avg Price (EUR/MWh)"),
        tooltip=[
            alt.Tooltip("date:T", title="Date"),
            alt.Tooltip("PRICE_AVG_EUR_MWH:Q", title="Price (EUR/MWh)", format=".1f"),
        ],
    )
)

temp_line = (
    alt.Chart(filtered_df)
    .mark_line(color="#29B5E8", strokeWidth=2, strokeDash=[4, 4])
    .encode(
        x=alt.X("date:T", title=""),
        y=alt.Y("TEMPERATURE_MEAN_C:Q", title="Mean Temperature (°C)"),
        tooltip=[
            alt.Tooltip("date:T", title="Date"),
            alt.Tooltip("TEMPERATURE_MEAN_C:Q", title="Temp (°C)", format=".1f"),
        ],
    )
)

chart = (
    alt.layer(price_line, temp_line)
    .resolve_scale(y="independent")
    .properties(height=350)
)

st.altair_chart(chart, use_container_width=True)
st.caption("🟠 Price  🔵 Temperature (dashed)")

st.divider()

# --- Scatter plot ---
zone_df = df[
    (df["BIDDING_ZONE"] == selected_zone)
    & (df["date"] >= start_date)
    & (df["date"] <= end_date)
]

st.subheader(f"Temperature vs Price — {selected_zone}")

scatter = (
    alt.Chart(zone_df)
    .mark_circle(size=50, opacity=0.6)
    .encode(
        x=alt.X("TEMPERATURE_MEAN_C:Q", title="Mean Temperature (°C)"),
        y=alt.Y("PRICE_AVG_EUR_MWH:Q", title="Avg Price (EUR/MWh)"),
        color=alt.Color("CITY:N", legend=alt.Legend(title="City")),
        tooltip=[
            alt.Tooltip("DATE:N", title="Date"),
            alt.Tooltip("CITY:N", title="City"),
            alt.Tooltip("TEMPERATURE_MEAN_C:Q", title="Temp (°C)", format=".1f"),
            alt.Tooltip("PRICE_AVG_EUR_MWH:Q", title="Price (EUR/MWh)", format=".1f"),
        ],
    )
)

st.altair_chart(scatter, use_container_width=True)

st.divider()

# --- Cortex Analyst ---
st.subheader("Ask the Data (Cortex Analyst)")
st.caption("Ask questions in plain English about energy prices and weather.")

SEMANTIC_MODEL_PATH = "@ANALYTICS_DB.STREAMLIT.STREAMLIT_STAGE/semantic_model.yaml"

question = st.text_input("Your question", placeholder="e.g. What was the average price in SE3 in January?")

if question:
    with st.spinner("Thinking..."):
        try:
            response = session.sql("""
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'analyst',
                    OBJECT_CONSTRUCT(
                        'semantic_model_file', ?,
                        'messages', ARRAY_CONSTRUCT(
                            OBJECT_CONSTRUCT('role', 'user', 'content', ?)
                        )
                    )::VARCHAR
                )
            """, [SEMANTIC_MODEL_PATH, question]).collect()[0][0]

            import json
            data = json.loads(response)
            message = data.get("message", {})
            content = message.get("content", [])

            for block in content:
                if block.get("type") == "text":
                    st.markdown(block["text"])
                elif block.get("type") == "sql":
                    sql = block["sql"]
                    st.code(sql, language="sql")
                    result_df = session.sql(sql).to_pandas()
                    st.dataframe(result_df)

        except Exception as e:
            st.error(f"Cortex Analyst failed: {e}")
