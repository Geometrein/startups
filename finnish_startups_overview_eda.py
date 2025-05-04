import marimo

__generated_with = "0.13.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from io import StringIO

    return mo, os, pd, px


@app.cell
def _(mo, pd):
    company_data_path = str(
        mo.notebook_location() / "data" / "company_info" / "basic_details.csv"
    )
    print(company_data_path)
    company_info_df = pd.read_csv(company_data_path, compression=None, engine='python', encoding="utf-8")

    financials_df_path = str(
        mo.notebook_location() / "data" / "company_info" / "financial_details.csv"
    )
    financial_df = pd.read_csv(financials_df_path, compression=None, engine='python', encoding="utf-8")
    return company_info_df, financial_df


@app.cell
def _(company_info_df):
    company_info_df.info()
    return


@app.cell
def _(financial_df):
    financial_df.info()
    return


@app.cell
def _(company_info_df, financial_df, pd):
    merged_df = pd.merge(
        financial_df,
        company_info_df,
        on="business_id",
        how="inner",
    )

    merged_df.info()
    return (merged_df,)


@app.cell
def _(company_info_df):
    company_info_df
    return


@app.cell
def _(financial_df):
    financial_df
    return


@app.cell
def _(merged_df):
    merged_df
    return


@app.cell
def _(mo):
    mo.md(r"""## Spatial Distribution of Startups""")
    return


@app.cell
def _(company_info_df, pd, px):
    def plot_business_by_city(
        df: pd.DataFrame, column: str = "main_line_of_business", top_n: int = None
    ) -> None:
        """
        Args:
            df (pd.DataFrame): The input DataFrame.
            column (str): The column to group and plot.
            top_n (int, optional): If set, only the top N categories are shown.
        """
        category_counts = (
            df[column].dropna().value_counts(normalize=True).mul(100).reset_index()
        )
        category_counts.columns = [column, "percentage"]

        if top_n:
            category_counts = category_counts.head(top_n)

        fig = px.bar(
            category_counts,
            x="percentage",
            y=column,
            orientation="h",
            title=f"Startup Distribution by {column.replace('_', ' ').title()} (%)",
            labels={"percentage": "Percentage of Companies", column: "City"},
        )

        fig.update_layout(
            yaxis={"categoryorder": "total ascending"},
            margin=dict(l=150, r=50, t=80, b=50),
        )

        fig.show()

    plot_business_by_city(df=company_info_df, column="city", top_n=15)
    return


@app.cell
def _(company_info_df, pd, px):
    def plot_company_locations_map(df: pd.DataFrame):
        df = df[["business_id", "name", "coordinates"]].dropna()
        df = df[df["coordinates"].str.contains(",")]

        df["coordinates"] = df["coordinates"].str.replace(r"[() ]", "", regex=True)
        df[["lat", "lon"]] = df["coordinates"].str.split(",", expand=True)
        df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
        df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
        df = df.dropna(subset=["lat", "lon"])

        fig = px.scatter_map(
            df,
            lat="lat",
            lon="lon",
            hover_name="name",
            hover_data={"business_id": True},
            zoom=5,
            height=600,
            title="Startup Locations in Finland",
        )
        fig.update_layout(mapbox_style="carto-positron")
        fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
        return fig

    plot_company_locations_map(company_info_df)
    return


@app.cell
def _(mo):
    mo.md("""## Startup Categories""")
    return


@app.cell
def _(company_info_df, pd, px):
    def plot_main_business_categories(
        df: pd.DataFrame, column: str = "main_line_of_business", top_n: int = None
    ) -> None:
        """
        Args:
            df (pd.DataFrame): The input DataFrame.
            column (str): The column to group and plot.
            top_n (int, optional): If set, only the top N categories are shown.
        """
        category_counts = (
            df[column].dropna().value_counts(normalize=True).mul(100).reset_index()
        )
        category_counts.columns = [column, "percentage"]

        if top_n:
            category_counts = category_counts.head(top_n)

        fig = px.bar(
            category_counts,
            x="percentage",
            y=column,
            orientation="h",
            title=f"Startup Distribution by {column.replace('_', ' ').title()} (%)",
            labels={
                "percentage": "Percentage of Companies (%)",
                column: "Business Category",
            },
            height=600,
        )

        fig.update_layout(
            yaxis={"categoryorder": "total ascending"},
            margin=dict(l=150, r=50, t=80, b=50),
        )

        fig.show()

    plot_main_business_categories(
        df=company_info_df, column="main_line_of_business_category", top_n=15
    )
    return (plot_main_business_categories,)


@app.cell
def _(company_info_df, plot_main_business_categories):
    plot_main_business_categories(
        df=company_info_df, column="main_line_of_business", top_n=15
    )
    return


@app.cell
def _(company_info_df, financial_df, pd, px):
    def plot_business_categories_by_employees(
        financial_df: pd.DataFrame, company_info_df: pd.DataFrame, top_n: int = None
    ) -> None:
        """
        Args:
            financial_df (pd.DataFrame): Financial data containing business_id and num_employees.
            company_info_df (pd.DataFrame): Company info containing business_id and main_line_of_business.
            top_n (int, optional): If set, only the top N categories are shown.
        """
        merged_df = pd.merge(
            financial_df[["business_id", "num_employees"]],
            company_info_df[["business_id", "main_line_of_business_category"]],
            on="business_id",
            how="inner",
        )

        merged_df = merged_df.dropna(
            subset=["num_employees", "main_line_of_business_category"]
        )

        category_employees = (
            merged_df.groupby("main_line_of_business_category")["num_employees"]
            .sum()
            .reset_index()
        )

        category_employees = category_employees.sort_values(
            "num_employees", ascending=False
        )

        if top_n:
            category_employees = category_employees.head(top_n)

        fig = px.bar(
            category_employees,
            x="num_employees",
            y="main_line_of_business_category",
            orientation="h",
            title="Total Employees by Business Category",
            labels={
                "num_employees": "Number of Employees",
                "main_line_of_business_category": "Business Category",
            },
        )

        fig.update_layout(
            yaxis={"categoryorder": "total ascending"},
            margin=dict(l=150, r=50, t=80, b=50),
        )

        fig.show()

    plot_business_categories_by_employees(financial_df, company_info_df, 15)
    return


@app.cell
def _(mo):
    mo.md(r"""## Financials""")
    return


@app.cell
def _(financial_df, pd, px):
    def plot_financial_data_years(
        df: pd.DataFrame, column: str = "year", top_n: int = None
    ) -> None:
        """
        Args:
            df (pd.DataFrame): The input DataFrame.
            column (str): The column to group and plot.
            top_n (int, optional): If set, only the top N categories are shown.
        """
        year_counts = df[column].dropna().value_counts().reset_index()
        year_counts.columns = [column, "count"]

        if top_n:
            year_counts = year_counts.head(top_n)

        fig = px.bar(
            year_counts,
            x=column,
            y="count",
            orientation="v",
            title=f"Number of Available Financial Records by {column.title()}",
            labels={"count": "Number of Records", column: "Year"},
        )

        fig.update_layout(
            yaxis={"categoryorder": "total ascending"},
            margin=dict(l=150, r=50, t=80, b=50),
        )

        fig.show()

    plot_financial_data_years(financial_df)
    return


@app.cell
def _(company_info_df, financial_df, pd, px):
    def plot_turnover_vs_profit_by_year(
        df: pd.DataFrame,
        company_info_df: pd.DataFrame,
        x_col: str = "num_employees",
        y_col: str = "turnover",
        year_col: str = "year",
    ) -> None:
        merged_df = df.merge(company_info_df, on="business_id", how="left")
        merged_df[year_col] = merged_df[year_col].astype(int)
        all_years = sorted(merged_df[year_col].unique())

        fig = px.scatter(
            merged_df,
            x=x_col,
            y=y_col,
            animation_frame=year_col,
            hover_name="name",
            title="Turnover vs Operating Profit by Year",
            labels={x_col: "Operating Profit (€)", y_col: "Turnover (€)"},
            category_orders={year_col: all_years},
        )

        fig.update_traces(
            textposition="top center", textfont=dict(size=10, color="black")
        )

        fig.update_layout(
            yaxis_type="log",
            xaxis_type="log",
            margin=dict(l=100, r=50, t=80, b=50),
            transition={"duration": 100, "easing": "cubic-in-out"},
        )

        fig.show()

    plot_turnover_vs_profit_by_year(financial_df, company_info_df)
    return


@app.cell
def _(merged_df, pd, px):
    def plot_turnover_distribution_by_city(
        input_df: pd.DataFrame, year: int = 2023, min_city_count: int = 10
    ) -> None:
        input_df = input_df[input_df["year"] == year]
        df = input_df[["city", "turnover"]].dropna()

        city_counts = df["city"].value_counts()
        valid_cities = city_counts[city_counts >= min_city_count].index
        df = df[df["city"].isin(valid_cities)]

        df["city"] = pd.Categorical(
            df["city"], categories=city_counts.loc[valid_cities].index, ordered=True
        )

        fig = px.box(
            df,
            x="turnover",
            y="city",
            orientation="h",
            title=f"Turnover Distribution by City ({year})",
        )

        fig.update_layout(
            margin=dict(l=120, r=20, t=50, b=50), xaxis_type="log", showlegend=False
        )

        fig.show()

    plot_turnover_distribution_by_city(input_df=merged_df, year=2023)
    return


@app.cell
def _(financial_df, pd, px):
    def plot_median_financials_over_time(financial_df: pd.DataFrame):
        df = financial_df.copy()
        df_grouped = (
            df.groupby("year")
            .agg(
                {
                    "turnover": "median",
                    "operating_profit": "median",
                    "net_income": "median",
                }
            )
            .reset_index()
        )

        df_melted = df_grouped.melt(
            id_vars="year", var_name="metric", value_name="value"
        )

        fig = px.line(
            df_melted,
            x="year",
            y="value",
            color="metric",
            markers=True,
            title="Median Financial Metrics Over Time",
            labels={"value": "EUR"},
        )
        fig.show()

    plot_median_financials_over_time(financial_df)
    return


@app.cell
def _(financial_df, pd, px):
    def plot_median_ratios_over_time(financial_df: pd.DataFrame):
        df = financial_df.copy()
        df_grouped = (
            df.groupby("year")
            .agg(
                {
                    "quick_ratio": "median",
                    "current_ratio": "median",
                    "solvency_ratio": "median",
                }
            )
            .reset_index()
        )

        df_melted = df_grouped.melt(
            id_vars="year", var_name="metric", value_name="value"
        )

        fig = px.line(
            df_melted,
            x="year",
            y="value",
            color="metric",
            markers=True,
            title="Median Financial Ratios Over Time",
            labels={"value": "Ratio Value", "year": "Year", "metric": "Metric"},
        )
        fig.update_layout(yaxis_title="Median Ratio Value")
        fig.show()

    plot_median_ratios_over_time(financial_df)
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        #### Quick Ratio
        Stays mostly in the 1.3–2.0 range, indicating:

        On average, startups have just enough or slightly more liquid assets than current liabilities.

        A dip in 2017 suggests tighter liquidity or increased short-term liabilities.

        Recovery post-2018 → possibly due to increased funding or improved cash flow management.

        #### Current Ratio
        Follows a very similar pattern to quick ratio, but slightly higher as it includes inventory.

        The spike in 2020 could reflect pandemic-related uncertanity induced cash hoarding.

        Flattening after 2021 migth suggests a return to steady-state operating conditions.

        #### Solvency Ratio
        - Remains consistently low (0.2–0.35) across all years.

        - Indicates that startups are heavily leveraged or equity-light, which is typical for early-stage ventures.

        - Little variation suggests persistent structural reliance on short-term capital or external funding.
        """
    )
    return


@app.cell
def _(merged_df, pd, px):
    def plot_turnover_per_employee_grouped(merged_df: pd.DataFrame):
        df = merged_df[["year", "turnover", "num_employees"]].copy()
        df = df.dropna(subset=["turnover", "num_employees"])
        df = df[df["num_employees"] > 0]
        df["turnover_per_employee"] = df["turnover"] / df["num_employees"]

        bins = [0, 5, 10, 20, 50, 100, 500, float("inf")]
        labels = ["1–5", "6–10", "11–20", "21–50", "51–100", "101–500", "500+"]
        df["employee_group"] = pd.cut(
            df["num_employees"], bins=bins, labels=labels, right=True
        )

        fig = px.box(
            df,
            x="employee_group",
            y="turnover_per_employee",
            points="outliers",
            title="Turnover per Emploee Distribution by Company Size",
            labels={
                "turnover_per_employee": "€ / Employee",
                "employee_group": "Employee Group",
            },
        )
        fig.update_layout(
            xaxis_title="Employee Group",
            yaxis_title="Turnover per Employee (€)",
            yaxis_type="log",
        )
        return fig

    plot_turnover_per_employee_grouped(merged_df)
    return


@app.cell
def _(merged_df, px):
    def plot_turnover_vs_profit(merged_df, year):
        df = merged_df[merged_df["year"] == year].copy()
        df = df[
            (df["turnover"].notna())
            & (df["operating_profit"].notna())
            & (df["num_employees"].notna())
            & (df["main_line_of_business_category"].notna())
        ]
        df = df[df["turnover"] > 0]

        fig = px.scatter(
            df,
            x="turnover",
            y="operating_profit",
            size="num_employees",
            color="main_line_of_business_category",
            hover_name="name",
            log_x=True,
            log_y=True,
            title="Turnover vs Operating Profit by Sector (log scale)",
            labels={
                "turnover": "Turnover (€)",
                "operating_profit": "Operating Profit (€)",
                "main_line_of_business_category": "Business Category",
                "num_employees": "Employees",
            },
            height=700,
        )
        fig.update_layout(legend_title_text="Sector", margin=dict(l=0, r=0, t=50, b=0))
        return fig

    plot_turnover_vs_profit(merged_df, year=2023)
    return


@app.cell
def _(merged_df, pd):
    def filter_top_companies_by_turnover_and_profit(
        input_df: pd.DataFrame, year: int
    ) -> pd.DataFrame:
        df = input_df.copy()
        df = df[df["year"] == year]

        turnover_threshold = df["turnover"].quantile(0.8)
        profit_threshold = df["operating_profit"].quantile(0.8)

        top_df = df[
            (df["turnover"] >= turnover_threshold)
            & (df["operating_profit"] >= profit_threshold)
        ]

        return top_df

    top_df = filter_top_companies_by_turnover_and_profit(input_df=merged_df, year=2023)
    return (top_df,)


@app.cell
def _(pd, px, top_df):
    def plot_turnover_vs_profit_scatter(
        top_df: pd.DataFrame, label_top_n: int = 20
    ) -> None:
        df = top_df.copy()
        df["show_label"] = False
        top_labeled = df.nlargest(label_top_n, "turnover")
        df.loc[top_labeled.index, "show_label"] = True
        df["label"] = df["name"].where(df["show_label"])

        fig = px.scatter(
            df,
            x="turnover",
            y="operating_profit",
            text="label",
            title="Top Companies: Turnover vs Operating Profit",
            labels={
                "turnover": "Turnover (€)",
                "operating_profit": "Operating Profit (€)",
            },
        )

        fig.update_traces(
            textposition="top center",
            textfont=dict(size=12, color="black", family="Arial"),
            marker=dict(size=10),
            opacity=0.8,
        )

        fig.update_layout(
            margin=dict(l=60, r=60, t=60, b=60), xaxis_type="log", yaxis_type="log"
        )

        fig.show()

    plot_turnover_vs_profit_scatter(top_df)
    return


@app.cell
def _(pd, px, top_df):
    def plot_turnover_and_profit_bars(top_df: pd.DataFrame, top_n) -> None:
        df = top_df[["name", "turnover", "operating_profit"]].copy()
        df = df.sort_values("turnover", ascending=False).head(top_n)

        melted = df.melt(
            id_vars="name",
            value_vars=["turnover", "operating_profit"],
            var_name="metric",
            value_name="amount",
        )

        fig = px.bar(
            melted,
            x="amount",
            y="name",
            color="metric",
            barmode="group",
            orientation="h",
            title="Turnover and Operating Profit per Company",
            labels={"amount": "€ Amount", "name": "Company", "metric": "Metric"},
        )

        fig.update_layout(margin=dict(l=150, r=50, t=60, b=40), xaxis_type="log")

        fig.show()

    plot_turnover_and_profit_bars(top_df, top_n=25)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
