import streamlit as st
import pandas as pd
import numpy as np
import hashlib
import requests
from bs4 import BeautifulSoup
from sklearn.linear_model import LinearRegression
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="AI SaaS Growth OS", layout="wide")

# =============================
# USERS + ROLES
# =============================
USERS = {
    "admin": {"pwd": hashlib.sha256("admin123".encode()).hexdigest(), "role": "admin"},
    "client": {"pwd": hashlib.sha256("client123".encode()).hexdigest(), "role": "client"},
    "viewer": {"pwd": hashlib.sha256("view123".encode()).hexdigest(), "role": "viewer"},
}

def login(user, pwd):
    u = USERS.get(user)
    if u and u["pwd"] == hashlib.sha256(pwd.encode()).hexdigest():
        return True, u["role"]
    return False, None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

# =============================
# LOGIN PAGE
# =============================
if not st.session_state.logged_in:
    st.title("🔐 SaaS Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        ok, role = login(u, p)
        if ok:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

# =============================
# SAMPLE DATA ENGINE
# =============================
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

# =============================
# METRICS ENGINE
# =============================
df["Score"] = (
    df["Conversion_Rate"] * 0.4 +
    df["SEO_Score"] * 0.2 +
    df["Performance"] * 0.2 +
    (100 - df["Broken_Links"]) * 0.2
)

df["Opportunity_Score"] = df["Leads"] * (100 - df["Conversion_Rate"])
df["Revenue"] = df["Conversions"] * 1000

# =============================
# SIDEBAR
# =============================
st.sidebar.title("⚙️ Controls")

dashboard = st.sidebar.radio("Business", ["Real Estate", "Transport", "Business"])

date_range = st.sidebar.date_input(
    "Date Range",
    [df["Month"].min(), df["Month"].max()]
)

theme = st.sidebar.color_picker("Theme", "#1f77b4")

# =============================
# FILTER
# =============================
filtered_df = df[
    (df["Template"] == dashboard) &
    (df["Month"] >= pd.to_datetime(date_range[0])) &
    (df["Month"] <= pd.to_datetime(date_range[1]))
]

# =============================
# HEADER
# =============================
st.title("🚀 AI SaaS Growth OS")
st.caption("Predict • Analyze • Optimize • Scale")

if st.session_state.role == "viewer":
    st.warning("👁 Read-only access enabled")

# =============================
# KPI DASHBOARD
# =============================
c1, c2, c3, c4 = st.columns(4)

c1.metric("Leads", int(filtered_df["Leads"].sum()))
c2.metric("Conversions", int(filtered_df["Conversions"].sum()))
c3.metric("Conv %", round(filtered_df["Conversion_Rate"].mean(), 2))
c4.metric("Score", round(filtered_df["Score"].mean(), 2))

# =============================
# TREND
# =============================
st.subheader("📈 Trend")
trend = filtered_df.groupby("Month")[["Conversion_Rate", "Performance"]].mean()
st.line_chart(trend)

# =============================
# FORECAST ENGINE
# =============================
st.subheader("🔮 Forecast")

def forecast(df, col):
    df = df.sort_values("Month")
    df["t"] = range(len(df))

    model = LinearRegression()
    model.fit(df[["t"]], df[col])

    future = pd.DataFrame({"t": range(len(df), len(df) + 60)})
    future[col] = model.predict(future[["t"]])
    future["Month"] = pd.date_range(df["Month"].max(), periods=60, freq="ME")  # FIXED

    return future

past = filtered_df.groupby("Month")["Conversion_Rate"].mean().reset_index()
future = forecast(past, "Conversion_Rate")

st.line_chart(future.set_index("Month"))

# =============================
# HIGH POTENTIAL
# =============================
st.subheader("🔥 High Potential")
st.dataframe(
    filtered_df.sort_values("Opportunity_Score", ascending=False)
    [["Month", "Leads", "Conversion_Rate", "Opportunity_Score"]].head(5)
)

# =============================
# ANOMALY DETECTION
# =============================
st.subheader("🚨 Anomalies")

mean = filtered_df["Conversion_Rate"].mean()
std = filtered_df["Conversion_Rate"].std()

anomaly = filtered_df[
    (filtered_df["Conversion_Rate"] > mean + 2*std) |
    (filtered_df["Conversion_Rate"] < mean - 2*std)
]

if not anomaly.empty:
    st.dataframe(anomaly[["Month", "Conversion_Rate"]])
else:
    st.success("No anomalies detected")

# =============================
# AI INSIGHTS
# =============================
st.subheader("🤖 AI Insight Engine")

def ai_insight(df):
    return f"""
    📊 Business Summary:
    - Avg Conversion: {df['Conversion_Rate'].mean():.2f}
    - Avg SEO Score: {df['SEO_Score'].mean():.2f}
    - Avg Performance: {df['Performance'].mean():.2f}

    💡 Insight:
    Focus on improving conversion rate and SEO optimization for growth.
    """

if st.button("Generate AI Insight"):
    st.write(ai_insight(filtered_df))

# =============================
# PERFORMANCE RANKING
# =============================
st.subheader("🏆 Ranking")

best = filtered_df.sort_values("Score", ascending=False).iloc[0]
worst = filtered_df.sort_values("Score", ascending=True).iloc[0]

col1, col2 = st.columns(2)

col1.success(f"🔥 Best: {best['Month'].date()} | Score {round(best['Score'],2)}")
col2.error(f"⚠️ Worst: {worst['Month'].date()} | Score {round(worst['Score'],2)}")

# =============================
# REVENUE
# =============================
st.subheader("💰 Revenue")
st.metric("Total Revenue", f"₹{int(filtered_df['Revenue'].sum()):,}")

# =============================
# WEBSITE SCRAPER
# =============================
st.subheader("🌐 Website Audit")

url = st.text_input("Enter URL")

def scrape(url):
    try:
        r = requests.get(url, timeout=5)
        s = BeautifulSoup(r.text, "html.parser")

        return {
            "title": s.title.text if s.title else "Missing",
            "links": len(s.find_all("a")),
            "images": len(s.find_all("img"))
        }
    except:
        return None

if st.button("Run Audit"):
    res = scrape(url)
    if res:
        st.json(res)
    else:
        st.error("Invalid URL")

# =============================
# PDF EXPORT
# =============================
st.subheader("📄 Export Report")

def generate_pdf(text):
    file = "report.pdf"
    doc = SimpleDocTemplate(file)
    styles = getSampleStyleSheet()
    doc.build([Paragraph(text, styles["Normal"])])
    return file

if st.button("Generate PDF"):
    file = generate_pdf(str(filtered_df.describe()))
    st.success("PDF Generated: report.pdf")

# =============================
# THEME
# =============================
st.markdown(f"""
<style>
h1, h2, h3 {{
    color: {theme};
}}
</style>
""", unsafe_allow_html=True)
