import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="CO₂ vs GDP Analysis", layout="wide", initial_sidebar_state="expanded")

st.title("🌍 CO₂ Emissions vs GDP per Capita (1990–2020)")
st.markdown("""
**By Sang In Byeon** | DAT 301 — Enhanced Python Version  
Exploring how a country's wealth relates to its carbon footprint across 165 countries over 30 years.  
*Original analysis built in R — this version adds interactivity and deeper visual storytelling.*
""")

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
    df = pd.read_csv(url)
    # Add region manually using a simple mapping
    region_map = {
        "Africa": ["Nigeria","Ethiopia","Egypt","South Africa","Kenya","Ghana","Tanzania","Algeria","Morocco","Angola","Mozambique","Cameroon","Ivory Coast","Madagascar","Niger","Burkina Faso","Mali","Malawi","Zambia","Senegal","Zimbabwe","Chad","Guinea","Rwanda","Benin","Burundi","Tunisia","South Sudan","Togo","Sierra Leone","Libya","Congo","Liberia","Central African Republic","Mauritania","Eritrea","Namibia","Gambia","Botswana","Gabon","Lesotho","Guinea-Bissau","Equatorial Guinea","Mauritius","Eswatini","Djibouti","Comoros","Cabo Verde","Sao Tome and Principe","Seychelles","Somalia","Sudan","Uganda","Cameroon","Democratic Republic of Congo","Republic of Congo"],
        "Asia": ["China","India","Indonesia","Pakistan","Bangladesh","Japan","Philippines","Vietnam","Iran","Thailand","Myanmar","South Korea","Iraq","Afghanistan","Saudi Arabia","Uzbekistan","Malaysia","Yemen","Nepal","North Korea","Sri Lanka","Kazakhstan","Syria","Cambodia","Jordan","Azerbaijan","United Arab Emirates","Tajikistan","Israel","Laos","Lebanon","Kyrgyzstan","Turkmenistan","Singapore","Oman","Kuwait","Georgia","Mongolia","Armenia","Qatar","Bahrain","Timor","Brunei","Maldives","Bhutan"],
        "Europe": ["Russia","Germany","United Kingdom","France","Italy","Spain","Ukraine","Poland","Romania","Netherlands","Belgium","Czech Republic","Greece","Portugal","Sweden","Hungary","Belarus","Austria","Switzerland","Bulgaria","Serbia","Denmark","Finland","Slovakia","Norway","Ireland","Croatia","Bosnia and Herzegovina","Moldova","Lithuania","Albania","Slovenia","Latvia","North Macedonia","Estonia","Luxembourg","Montenegro","Malta","Iceland","Cyprus","Czechia"],
        "Americas": ["United States","Brazil","Mexico","Colombia","Argentina","Canada","Peru","Venezuela","Chile","Ecuador","Guatemala","Cuba","Bolivia","Haiti","Dominican Republic","Honduras","Paraguay","Nicaragua","El Salvador","Costa Rica","Panama","Uruguay","Jamaica","Trinidad and Tobago","Guyana","Suriname","Belize","Barbados","Saint Lucia","Grenada","Antigua and Barbuda"],
        "Oceania": ["Australia","Papua New Guinea","New Zealand","Fiji","Solomon Islands","Vanuatu","Samoa","Kiribati","Tonga","Micronesia","Palau","Marshall Islands","Nauru","Tuvalu"]
    }
    country_to_region = {}
    for region, countries in region_map.items():
        for c in countries:
            country_to_region[c] = region

    df = df[["country", "year", "co2_per_capita", "gdp", "population"]].dropna()
    df = df[df["year"].between(1990, 2020)]
    df["gdp_pc"] = df["gdp"] / df["population"]
    df = df.rename(columns={"co2_per_capita": "co2_pc"})
    df = df[df["gdp_pc"] > 0]
    df["region"] = df["country"].map(country_to_region).fillna("Other")
    # Remove extreme outliers (top 0.1%)
    upper = df["co2_pc"].quantile(0.999)
    df = df[df["co2_pc"] <= upper]
    return df

with st.spinner("Loading data..."):
    df = load_data()

st.success(f"✅ Loaded {len(df):,} rows across {df['country'].nunique()} countries")

# Sidebar
st.sidebar.header("🔧 Filters")
years = st.sidebar.slider("Year Range", 1990, 2020, (1990, 2020))
regions = st.sidebar.multiselect("Region", sorted(df["region"].unique()), default=sorted(df["region"].unique()))

df_filtered = df[df["year"].between(years[0], years[1])]
if regions:
    df_filtered = df_filtered[df_filtered["region"].isin(regions)]

# Chart 1 - Scatter
st.subheader("📊 Overall Relationship: Wealth vs Emissions")
fig1 = px.scatter(df_filtered, x="gdp_pc", y="co2_pc",
                  color="region",
                  hover_name="country",
                  hover_data={"year": True, "gdp_pc": ":.0f", "co2_pc": ":.2f", "region": False},
                  trendline="lowess",
                  opacity=0.6,
                  labels={"gdp_pc": "GDP per Capita (USD)", "co2_pc": "CO₂ per Capita (tons)", "region": "Region"},
                  title="CO₂ vs GDP per Capita — colored by region")
fig1.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
st.plotly_chart(fig1, use_container_width=True)
st.caption("💡 Hover over any dot to see the country, year, and exact values.")

# Chart 2 - Line
st.subheader("📈 Trend Over Time: Top 10 Emitters")
top_countries = df[df["year"].between(years[0], years[1])].groupby("country")["co2_pc"].mean().nlargest(10).index.tolist()
df_top = df_filtered[df_filtered["country"].isin(top_countries)]
fig2 = px.line(df_top, x="year", y="co2_pc", color="country",
               markers=True,
               labels={"co2_pc": "CO₂ per Capita (tons)", "year": "Year"},
               title="Top 10 Countries by Average CO₂ per Capita Over Time")
fig2.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
st.plotly_chart(fig2, use_container_width=True)

# Chart 3 - Bar
st.subheader("🏆 Top 20 Countries by Average CO₂ Emissions")
top20_df = (df_filtered.groupby("country")["co2_pc"].mean()
            .nlargest(20).reset_index()
            .sort_values("co2_pc", ascending=True))
fig3 = px.bar(top20_df, x="co2_pc", y="country",
              orientation="h",
              color="co2_pc",
              color_continuous_scale="Reds",
              labels={"co2_pc": "Avg CO₂ per Capita (tons)", "country": "Country"},
              title="Top 20 Countries — Average CO₂ per Capita")
fig3.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig3, use_container_width=True)

# Metrics
st.subheader("📌 Key Stats")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Countries", df_filtered["country"].nunique())
col2.metric("Avg CO₂ per Capita", f"{df_filtered['co2_pc'].mean():.2f} tons")
col3.metric("Highest Emitter", df_filtered.groupby("country")["co2_pc"].mean().idxmax())
col4.metric("Years Covered", f"{years[0]}–{years[1]}")

st.subheader("💡 Key Insights")
st.markdown("""
- **Wealth and emissions are strongly correlated**, but the relationship flattens at high income levels — richer countries don't always emit more.
- **Middle Eastern nations dominate** the top emitters list, driven by oil economies and energy-intensive industries.
- **Some high-income countries have reduced emissions** over time (notably in Europe), showing that clean energy policy can decouple growth from carbon output.
- **Asia shows the widest spread** — ranging from very low emitters like India to high emitters like Kuwait and Qatar.
""")

st.subheader("🔍 Raw Data Explorer")
display_cols = ["country", "year", "region", "co2_pc", "gdp_pc"]
st.dataframe(df_filtered[display_cols].sort_values("co2_pc", ascending=False).reset_index(drop=True))