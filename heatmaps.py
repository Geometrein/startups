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


def plot_ai_categories_heatmap(pivot_df):
    import plotly.graph_objects as go
    import numpy as np

    def format_value(val):
        if val >= 1e9:
            return f"${val / 1e9:.1f}B"
        elif val >= 1e6:
            return f"${val / 1e6:.0f}M"
        elif val >= 1e3:
            return f"${val / 1e3:.0f}K"
        else:
            return f"${int(val)}"

    z_raw = pivot_df.values
    z_log = np.log1p(z_raw)  # log(1 + x) to avoid log(0)
    x = pivot_df.columns.tolist()
    y = pivot_df.index.tolist()
    text = [[format_value(val) for val in row] for row in z_raw]

    fig = go.Figure(
        data=go.Heatmap(
            z=z_log,
            x=x,
            y=y,
            colorscale="Blues",
            text=text,
            texttemplate="%{text}",
            hovertemplate="Year: %{x}<br>Category: %{y}<br>Funding: %{text}<extra></extra>",
            colorbar=dict(title="Log Funding Scale"),
            showscale=False,
        )
    )

    fig.update_layout(
        title="Venturing into Artificial Intelligence<br><sup>VC Funding worldwide by AI Industry Between 2000 and 2025 </sup><br><sup>Visualization by Tigran Khachatryan (github.com/geometrein) & data from dealroom.co </sup></sup><br><sup>",
        xaxis=dict(title="Year", tickmode="linear", dtick=1),
        yaxis_title="Category",
        margin=dict(t=150, b=50),
        height=1080,
        width=1920,
    )
    fig.update_xaxes(side="top")
    return fig.show()


def plot_industries_heatmap(pivot_df):
    z_raw = pivot_df.values
    x = pivot_df.columns.tolist()
    y = pivot_df.index.tolist()
    text = [[format_value(val) for val in row] for row in z_raw]

    flat_values = z_raw[z_raw > 0].flatten()
    transformed, lambda_ = boxcox(flat_values)

    z_transformed = np.zeros_like(z_raw, dtype=float)
    z_transformed[z_raw > 0] = transformed

    fig = go.Figure(
        data=go.Heatmap(
            z=z_transformed,
            x=x,
            y=y,
            colorscale="Plasma",
            text=text,
            texttemplate="%{text}",
            hovertemplate="Year: %{x}<br>Category: %{y}<br>Funding: %{text}<extra></extra>",
            colorbar=dict(title="Log Funding Scale"),
            showscale=False,
        )
    )

    fig.update_layout(
        title="VC Funding Worldwide by Industry Between 2000 and 2025<br><sup>Visualization by Tigran Khachatryan (github.com/geometrein) & data from dealroom.co </sup><br><sup>",
        xaxis=dict(title="Year", tickmode="linear", dtick=1),
        yaxis_title="Category",
        margin=dict(t=150, b=50),
        height=1080,
        width=1920,
    )
    fig.update_xaxes(side="top")
    return fig.show()


if __name__ == "__main__":
    industry_csv_path = os.path.join(os.getcwd(), "data", "vc_funding_by_industry.csv")
    industry_df = pd.read_csv(filepath_or_buffer=industry_csv_path, index_col=0)
    plot_industries_heatmap(industry_df)

    ai_industry_csv_path = os.path.join(
        os.getcwd(), "data", "vc_funding_by_ai_category.csv"
    )
    ai_industry_df = pd.read_csv(filepath_or_buffer=ai_industry_csv_path, index_col=0)
    plot_ai_categories_heatmap(ai_industry_df)
