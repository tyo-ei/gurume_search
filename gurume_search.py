
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="グルメサーチ", layout="wide")

@st.cache_data
def load_data(csv_path: str) -> pd.DataFrame:
    """Read and clean the gourmet CSV."""
    df = pd.read_csv(csv_path)

    df["score"] = pd.to_numeric(df["score"], errors="coerce")

    df["lowest_price"] = (
        df["lowest_price"]
        .astype(str)
        .str.replace("￥", "", regex=False)
        .str.replace(",", "", regex=False)
    )
    df["lowest_price"] = pd.to_numeric(df["lowest_price"], errors="coerce")

    return df.dropna(subset=["score", "lowest_price"])


def main():
    gurume_df = load_data("knzwgrm.csv")

    st.title("グルメサーチ")

    price_limit = st.slider(
        "最低価格の上限 (円)",
        min_value=1000,
        max_value=20000,
        step=500,
        value=10000,
    )
    score_limit = st.slider(
        "人気スコアの下限",
        min_value=0.0,
        max_value=5.0,
        step=0.05,
        value=3.2,
    )

    filtered_df = gurume_df[
        (gurume_df["score"] >= score_limit) & (gurume_df["lowest_price"] <= price_limit)
    ]

    st.subheader(f"フィルタ後の店舗数: {len(filtered_df)} 件")

    fig = px.scatter(
        filtered_df,
        x="score",
        y="lowest_price",
        hover_data=["name", "stress"],
        title="人気スコアと最低価格の散布図",
        labels={"score": "スコア", "lowest_price": "最低価格 (円)"},
    )
    st.plotly_chart(fig, use_container_width=True)

    selected_gurume = st.selectbox(
        "気になるグルメを選んで詳しく見る", filtered_df["name"]
    )

    sort_key = st.selectbox(
        "ランキング基準を選んでください", ("score", "lowest_price")
    )
    ascending = True if sort_key == "lowest_price" else False

    if selected_gurume:
        url = filtered_df.loc[
            filtered_df["name"] == selected_gurume, "link"
        ].values[0]
        st.markdown(
            f"[{selected_gurume} のページへ移動]({url})", unsafe_allow_html=True
        )

    st.subheader(f"{sort_key} によるランキング (上位 10 件)")
    ranking_df = filtered_df.sort_values(by=sort_key, ascending=ascending).head(10)
    st.dataframe(ranking_df[["name", "lowest_price", "score", "comment"]])


if __name__ == "__main__":
    main()
