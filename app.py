import streamlit as st  # HARUS PALING ATAS
st.set_page_config(
    page_title="Word Graph & PageRank",
    layout="wide",
    page_icon="📄"
)

import PyPDF2
import re
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict

# =============================
# HEADER
# =============================
st.title("📄 Word Graph & PageRank Centrality")
st.caption("Analisis keterkaitan kata dan pengaruhnya dari dokumen jurnal PDF")

# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.header("⚙️ Pengaturan")
    uploaded_file = st.file_uploader("📤 Upload Jurnal (PDF)", type="pdf")

    top_n = st.slider("🔝 Tampilkan Top PageRank", 5, 50, 20)
    graph_k = st.slider("🕸 Kerapatan Graph", 0.05, 0.5, 0.15)

    st.markdown("---")
    st.info("Aplikasi ini membangun **Word Co-occurrence Graph** dan menghitung **PageRank Centrality**.")

# =============================
# MAIN PROCESS
# =============================
if uploaded_file:
    progress = st.progress(0)

    # =============================
    # 1. LOAD & EXTRACT TEXT
    # =============================
    text = ""
    reader = PyPDF2.PdfReader(uploaded_file)
    for page in reader.pages:
        text += (page.extract_text() or "") + " "
    progress.progress(25)

    # =============================
    # 2. PREPROCESSING
    # =============================
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    tokens = text.split()

    stopwords = {
        "dan","yang","dari","ke","di","pada","untuk","dengan","adalah",
        "the","of","to","in","for","is","are","that","this","as","by"
    }

    tokens = [w for w in tokens if w not in stopwords and len(w) > 2]
    progress.progress(50)

    # =============================
    # 3. WORD CO-OCCURRENCE GRAPH
    # =============================
    edges = defaultdict(int)
    for i in range(len(tokens) - 1):
        a, b = tokens[i], tokens[i + 1]
        if a != b:
            edges[tuple(sorted((a, b)))] += 1

    G = nx.Graph()
    for (a, b), w in edges.items():
        G.add_edge(a, b, weight=w)

    progress.progress(75)

    # =============================
    # 4. PAGERANK
    # =============================
    pagerank = nx.pagerank(G, weight="weight")
    df_pr = pd.DataFrame(pagerank.items(), columns=["Word", "PageRank"])
    df_pr = df_pr.sort_values("PageRank", ascending=False)

    progress.progress(100)
    st.success("✅ Analisis selesai")

    # =============================
    # METRICS
    # =============================
    col1, col2, col3 = st.columns(3)
    col1.metric("📌 Total Token", len(tokens))
    col2.metric("🟢 Jumlah Node", G.number_of_nodes())
    col3.metric("🔗 Jumlah Edge", G.number_of_edges())

    st.markdown("---")

    # =============================
    # TOP PAGERANK TABLE
    # =============================
    with st.expander("🔝 Top PageRank Words", expanded=True):
        st.dataframe(
            df_pr.head(top_n),
            use_container_width=True,
            height=400
        )

    # =============================
    # GRAPH VISUALIZATION
    # =============================
    st.subheader("🕸 Visualisasi Word Graph")

    fig, ax = plt.subplots(figsize=(14, 12))
    pos = nx.spring_layout(G, k=graph_k, seed=42)

    node_sizes = [pagerank[n] * 15000 for n in G.nodes()]

    nx.draw_networkx_nodes(
        G, pos,
        node_size=node_sizes,
        node_color="cornflowerblue",
        alpha=0.85,
        ax=ax
    )

    nx.draw_networkx_edges(
        G, pos,
        alpha=0.15,
        edge_color="gray",
        ax=ax
    )

    top_words = dict(df_pr.head(10).values)
    nx.draw_networkx_labels(
        G, pos,
        top_words,
        font_size=11,
        font_weight="bold",
        ax=ax
    )

    ax.set_title("Word Co-occurrence Graph (Node Size = PageRank)", fontsize=14)
    ax.axis("off")

    st.pyplot(fig)

else:
    st.warning("📤 Silakan upload file PDF jurnal untuk memulai analisis.")
