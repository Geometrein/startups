

import marimo

__generated_with = "0.13.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import io
    import marimo as mo
    import pandas as pd
    import networkx as nx
    import plotly.graph_objects as go
    from collections import Counter
    from urllib.request import urlopen

    return Counter, go, io, mo, nx, pd, urlopen


@app.cell
def _(io, mo, pd, urlopen):
    main_decision_makers_path = str(
        mo.notebook_location() / "data" / "company_info" / "main_decision_makers.csv"
    )

    def load_data(path):
        if path.startswith("http"):
            with urlopen(path) as response:
                data = response.read().decode("utf-8")
                return pd.read_csv(io.StringIO(data))
        else:
            return pd.read_csv(path)

    return load_data, main_decision_makers_path


@app.cell
def _(load_data, main_decision_makers_path):
    main_decision_makers_df = load_data(main_decision_makers_path)
    main_decision_makers_df.info()
    return (main_decision_makers_df,)


@app.cell
def _(main_decision_makers_df):
    main_decision_makers_df.sample(5)
    return


@app.cell
def _(main_decision_makers_df):
    main_decision_makers_df
    return


@app.cell
def _(go, main_decision_makers_df, nx, pd):
    def build_graph_from_df(df: pd.DataFrame) -> nx.Graph:
        df = df[
            ["business_id", "decision_person_id", "first_name", "last_name"]
        ].dropna(subset=["decision_person_id", "business_id"])
        df["label"] = df["first_name"].fillna("") + " " + df["last_name"].fillna("")
        edges = (
            df[["business_id", "decision_person_id"]]
            .drop_duplicates()
            .merge(df[["business_id", "decision_person_id"]], on="business_id")
        )
        edges = edges[edges["decision_person_id_x"] < edges["decision_person_id_y"]]
        edges = (
            edges.groupby(["decision_person_id_x", "decision_person_id_y"])
            .size()
            .reset_index(name="weight")
        )
        G = nx.Graph()
        for _, row in edges.iterrows():
            G.add_edge(
                row["decision_person_id_x"],
                row["decision_person_id_y"],
                weight=row["weight"],
            )
        label_map = df.drop_duplicates("decision_person_id").set_index(
            "decision_person_id"
        )["label"]
        for node in G.nodes():
            G.nodes[node]["label"] = label_map.get(node, str(node))
        return G


    def filter_graph(G: nx.Graph, min_degree: int = 1, min_weight: int = 1) -> nx.Graph:
        Gf = G.copy()
        for u, v, d in list(Gf.edges(data=True)):
            if d["weight"] < min_weight:
                Gf.remove_edge(u, v)
        low_degree_nodes = [n for n, d in Gf.degree() if d < min_degree]
        Gf.remove_nodes_from(low_degree_nodes)
        return Gf


    def graph_to_plotly(G: nx.Graph) -> go.Figure:
        pos = nx.spring_layout(G, seed=42)
        edge_x, edge_y = [], []
        for u, v in G.edges():
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

        node_x, node_y, labels, degrees = [], [], [], []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            labels.append(G.nodes[node]["label"])
            degrees.append(G.degree[node])

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=1, color="lightgray"),
            hoverinfo="none",
            mode="lines",
        )

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=labels,
            textposition="top center",
            hoverinfo="text",
            marker=dict(
                size=[3 + d for d in degrees],
                color=degrees,
                colorscale="Viridis",
                colorbar=dict(title="Degree"),
                line_width=0,
            ),
        )

        fig = go.Figure(data=[edge_trace, node_trace])
        fig.update_layout(
            showlegend=False, margin=dict(l=0, r=0, t=0, b=0), hovermode="closest"
        )
        return fig


    def visualize_decision_graph(
        df: pd.DataFrame, min_degree: int = 1, min_weight: int = 1
    ) -> go.Figure:
        G = build_graph_from_df(df)
        Gf = filter_graph(G, min_degree, min_weight)
        return Gf

    graph = visualize_decision_graph(
        main_decision_makers_df, min_degree=1, min_weight=1
    )
    print(graph)
    return graph, graph_to_plotly


@app.cell
def _(graph, graph_to_plotly):
    graph_to_plotly(graph)
    return


@app.cell
def _(Counter, go, graph, nx):
    def plot_component_size_distribution(G: nx.Graph, min_size: int) -> go.Figure:
        sizes = [len(c) for c in nx.connected_components(G) if len(c) >= min_size]
        counts = Counter(sizes)
        x, y = zip(*sorted(counts.items())) if counts else ([], [])

        fig = go.Figure(data=[go.Bar(x=x, y=y)])
        fig.update_layout(
            title=f"Connected Groups of Size ≥ {min_size}",
            xaxis_title="Group Size",
            yaxis_title="Number of Groups",
            bargap=0.2,
            template="plotly_white",
        )
        return fig

    plot_component_size_distribution(graph, min_size=2)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
