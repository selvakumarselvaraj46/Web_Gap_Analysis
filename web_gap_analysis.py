import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from sklearn.linear_model import LinearRegression

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Smart SaaS Dashboard", layout="wide")

# -----------------------------
# SAMPLE DATA
# -----------------------------
@st.cache_data
def generate_data():
    months = pd.date_range("2024-01-01", periods=24, freq="ME")  # FIXED
    templates = ["Real Estate", "Transport", "Business"]

    data = []
    for t in templates:
        for m in months:
            leads = np.random.randint(50, 200)
            conv = np.random.randint(10, 100)

            data.append({
                "Template": t,
                "Month": m,
                "Leads": leads,
                "Conversions": conv,
                "Conversion_Rate": (conv / leads) * 100,
                "Broken_Links": np.random.randint(10, 80),
                "SEO_Score": np.random.randint(20, 90),
                "Performance": np.random.randint(30, 90)
            })

    return pd.DataFrame(data)

df = generate_data()

# -----------------------------
# KPI SCORE
# -----------------------------
df["Score"] = (
    df["Conversion_Rate"] * 0.4 +
    df["SEO_Score"] * 0.2 +
    df["Performance"] * 0.2 +
    (100 - df["Broken_Links"]) * 0.2
)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("⚙️ Controls")

dashboard = st.sidebar.radio(
    "Select Business",
    ["Real Estate", "Transport", "Business"]
)

date_range = st.sidebar.date_input(
    "Date Range",
    [df["Month"].min(), df["Month"].max()]
)

theme = st.sidebar.color_picker("Theme", "#1f77b4")

# -----------------------------
# FILTER
# -----------------------------
filtered_df = df[
    (df["Template"] == dashboard) &
    (df["Month"] >= pd.to_datetime(date_range[0])) &
    (df["Month"] <= pd.to_datetime(date_range[1]))
]

# -----------------------------
# HEADER
# -----------------------------
st.title("🚀 Smart SaaS Dashboard")
st.caption("Analyze • Forecast • Optimize")

# -----------------------------
# KPI METRICS
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Leads", int(filtered_df["Leads"].sum()))
c2.metric("Conversions", int(filtered_df["Conversions"].sum()))
c3.metric("Conversion %", round(filtered_df["Conversion_Rate"].mean(), 2))
c4.metric("Score", round(filtered_df["Score"].mean(), 2))

# -----------------------------
# TREND
# -----------------------------
st.subheader("📈 Performance Trend")

trend = filtered_df.groupby("Month")[["Conversion_Rate", "Performance"]].mean()
st.line_chart(trend)

# -----------------------------
# FORECAST
# -----------------------------
def forecast(df, col):
    df = df.sort_values("Month").copy()
    df["t"] = range(len(df))

    model = LinearRegression()
    model.fit(df[["t"]], df[col])

    future = pd.DataFrame({
        "t": range(len(df), len(df) + 60)
    })

    future[col] = model.predict(future[["t"]])
    future["Month"] = pd.date_range(df["Month"].max(), periods=60, freq="ME")  # FIXED

    return future

st.subheader("🔮 Conversion Forecast (5 Years)")

past = filtered_df.groupby("Month")["Conversion_Rate"].mean().reset_index()
future = forecast(past, "Conversion_Rate")

combined = pd.concat([past, future])
st.line_chart(combined.set_index("Month"))

# -----------------------------
# WEBSITE AUDIT
# -----------------------------
st.subheader("🌐 Website Audit Tool")

url = st.text_input("Enter Website URL")

def audit_website(url):
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.title.string if soup.title else "Missing"
        meta = soup.find("meta", attrs={"name": "description"})

        links = soup.find_all("a")
        broken = 0

        for link in links[:20]:
            href = link.get("href")
            if href and href.startswith("http"):
                try:
                    res = requests.get(href, timeout=3)
                    if res.status_code >= 400:
                        broken += 1
                except:
                    broken += 1

        return {
            "Title": title,
            "Meta Description": "Present" if meta else "Missing",
            "Total Links": len(links),
            "Broken Links": broken
        }

    except:
        return None

if st.button("Run Audit"):
    result = audit_website(url)

    if result:
        st.json(result)

        st.subheader("🧠 Recommendations")

        if result["Meta Description"] == "Missing":
            st.warning("Add meta description for SEO")

        if result["Broken Links"] > 5:
            st.error("Fix broken links immediately")

        if result["Total Links"] < 10:
            st.info("Improve internal linking")

    else:
        st.error("Invalid URL or blocked request")

# -----------------------------
# AI INSIGHTS
# -----------------------------
st.subheader("🤖 Smart Insights")

if filtered_df["Conversion_Rate"].mean() < 30:
    st.warning("Low conversion rate → Improve CTA & UX")

if filtered_df["SEO_Score"].mean() < 50:
    st.info("SEO score is low → Optimize keywords & content")

if filtered_df["Performance"].mean() < 50:
    st.warning("Performance is poor → Improve speed & optimization")

# -----------------------------
# THEME STYLING
# -----------------------------
st.markdown(f"""
<style>
h1, h2, h3 {{
    color: {theme};
}}
</style>
""", unsafe_allow_html=True)
