import streamlit as st
import pickle
import pandas as pd

st.set_page_config(layout="wide")

# -------------------------
# Load model
# -------------------------
similarity = pickle.load(open("./models/similarity.pkl", "rb"))
df = pickle.load(open("./models/products.pkl", "rb"))

# -------------------------
# Clean numeric columns
# -------------------------
# df["price"] = (
#     df["price"]
#     .astype(str)
#     .str.replace("₹", "", regex=False)
#     .str.replace(",", "", regex=False)
# )

# df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
df["price"] = (
    df["price"]
    .astype(str)
    .str.replace(r"[^\d.]", "", regex=True)
)

df["price"] = (pd.to_numeric(df["price"], errors="coerce").fillna(0))*8

df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0)

# df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0)


# -------------------------
# Title
# -------------------------
st.title("🌱 Eco-Friendly Product Recommendation System")
st.caption("Find sustainable alternatives powered by AI ♻️")


# -------------------------
# Sidebar
# -------------------------
st.sidebar.header("🔍 Filters")

category = st.sidebar.selectbox(
    "Category",
    ["All"] + sorted(df["category"].unique())
)

budget = st.sidebar.slider(
    "Max Budget (₹)",
    0,
    int(df["price"].max()),
    1000
)

min_rating = st.sidebar.slider("Minimum Rating ⭐", 0.0, 5.0, 3.0)


# -------------------------
# Search
# -------------------------
search = st.text_input("🔎 Search product")


# -------------------------
# Recommendation logic
# -------------------------
def recommend(product_name, top_n=6):
    idx = df[df["product"] == product_name].index[0]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    return df.iloc[[i[0] for i in scores]]


# -------------------------
# Product selector
# -------------------------
product_list = df["product"].values
selected_product = st.selectbox("Choose a product for similar eco alternatives", product_list)


# -------------------------
# Show results function
# -------------------------
def show_cards(data):

    cols = st.columns(3)

    for i, (_, row) in enumerate(data.iterrows()):
        with cols[i % 3]:

            st.image(row["img_url"], use_container_width=True)

            st.markdown(f"**{row['product'][:60]}**")

            st.write(f"💰 ₹ {int(row['price'])}")
            st.write(f"⭐ {row['rating']}")
            st.success(f"♻️ Eco Score: {row['eco_score']}")

            # 🔥 BUY LINK BUTTON
            st.link_button("🛒 Buy Now", row["url"])

            st.markdown("---")



# -------------------------
# Filter base dataset
# -------------------------
filtered = df.copy()

if category != "All":
    filtered = filtered[filtered["category"] == category]

filtered = filtered[
    (filtered["price"] <= budget) &
    (filtered["rating"] >= min_rating)
]

if search:
    filtered = filtered[
        filtered["product"].str.contains(search, case=False)
    ]


# -------------------------
# Default view (top eco products)
# -------------------------
st.subheader("🌿 Top Eco Products")

top_eco = filtered.sort_values("eco_score", ascending=False).head(6)
show_cards(top_eco)


# -------------------------
# Button recommendations
# -------------------------
if st.button("✨ Recommend Similar Products"):
    st.subheader("🤖 AI Recommendations")
    recs = recommend(selected_product)
    show_cards(recs)
