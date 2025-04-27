import os

import numpy as np
import pandas as pd
from scipy.stats import boxcox

import plotly.graph_objects as go


def format_value(val):
    if val >= 1e9:
        return f"${val / 1e9:.1f}B"
    elif val >= 1e6:
        return f"${val / 1e6:.0f}M"
    elif val >= 1e3:
        return f"${val / 1e3:.0f}K"
    else:
        return f"${int(val)}"


def plot_heatmap(
    pivot_df: pd.DataFrame,
    title: str,
    colorscale: str = "Blues",
    transform: str = "log",
    showscale: bool = False
) -> None:
    z_raw = pivot_df.values
    x = pivot_df.columns.tolist()
    y = pivot_df.index.tolist()
    text = [[format_value(val) for val in row] for row in z_raw]

    if transform == "log":
        z = np.log1p(z_raw)
    elif transform == "boxcox":
        flat_values = z_raw[z_raw > 0].flatten()
        if flat_values.size > 0:
            transformed, _ = boxcox(flat_values)
            z = np.zeros_like(z_raw, dtype=float)
            z[z_raw > 0] = transformed
        else:
            z = z_raw
    else:
        z = z_raw

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=x,
            y=y,
            colorscale=colorscale,
            text=text,
            texttemplate="%{text}",
            hovertemplate="Year: %{x}<br>Category: %{y}<br>Funding: %{text}<extra></extra>",
            colorbar=dict(title="Funding Scale"),
            showscale=showscale,
        )
    )

    fig.update_layout(
        title=title,
        xaxis=dict(title="Year", tickmode="linear", dtick=1),
        yaxis_title="Category",
        margin=dict(t=150, b=50),
        height=1080,
        width=1920,
    )
    fig.update_xaxes(side="top")
    fig.show()



if __name__ == "__main__":
    industry_csv_path = os.path.join(os.getcwd(), "data", "dealroom", "vc_funding_by_industry.csv")
    industry_df = pd.read_csv(filepath_or_buffer=industry_csv_path, index_col=0)
    plot_heatmap(
        industry_df,
        title="VC Funding Worldwide by Industry Between 2000 and 2025<br><sup>Visualization by Tigran Khachatryan (github.com/geometrein) & data from dealroom.co</sup>",
        colorscale="Plasma",
        transform="boxcox",
        showscale=False,
    )

    ai_industry_csv_path = os.path.join(
        os.getcwd(), "data", "dealroom", "vc_funding_by_ai_category.csv"
    )
    ai_industry_df = pd.read_csv(filepath_or_buffer=ai_industry_csv_path, index_col=0)
    plot_heatmap(
        ai_industry_df,
        title="Venturing into Artificial Intelligence<br><sup>VC Funding worldwide by AI Industry Between 2000 and 2025</sup><br><sup>Visualization by Tigran Khachatryan (github.com/geometrein) & data from dealroom.co</sup>",
        colorscale="Blues",
        transform="log",
        showscale=False,
    )
