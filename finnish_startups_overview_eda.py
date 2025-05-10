

import marimo

__generated_with = "0.13.2"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(
        r"""
        # Finnish Startup Ecosystem Analysis

        This project explores the Finnish startup ecosystem, focusing on the sample of Finnish startups listed on [statup100](https://startup100.net/companies/).
        The goal is to analyze the publicly available data of these startups and gain insights into the startup landscape in Finland.
        """
    )
    return


@app.cell
def _():
    import os
    import io

    import marimo as mo
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from urllib.request import urlopen
    import folium
    from folium.plugins import MarkerCluster

    return MarkerCluster, folium, io, mo, pd, px, urlopen


@app.cell
def _(io, mo, pd, urlopen):
    company_data_path = str(
        mo.notebook_location() / "data" / "company_info" / "basic_details.csv"
    )
    financials_df_path = str(
        mo.notebook_location() / "data" / "company_info" / "financial_details.csv"
    )

    def load_data(path):
        if path.startswith("http"):
            with urlopen(path) as response:
                data = response.read().decode("utf-8")
                return pd.read_csv(io.StringIO(data))
        else:
            return pd.read_csv(path)

    company_info_df = load_data(company_data_path)
    financial_df = load_data(financials_df_path)
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
def _(mo):
    mo.md(
        r"""
        ## Data Overview

        The original sample of the startups was fetched from [startup100](https://startup100.net/).
        This dataframe contains the basic company information including business id, address, business type and main line of business. The sample has 757 unique companies.
        """
    )
    return


@app.cell
def _(company_info_df):
    company_info_df
    return


@app.cell
def _(mo):
    mo.md(r"""The initial company data was later enriched with financial information by matching business IDs to corresponding financial reports. This dataframe includes financial data only for companies with publicly available reports.""")
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

        return fig

    plot_business_by_city(df=company_info_df, column="city", top_n=15)
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        #### Key Takeaways: Spatial Distribution of Startups
        - Over **62.4%** of all startups are located in the **Helsinki Metropolitan Area** (Helsinki, Espoo, and Vantaa), emphasizing the region’s importance as the **core of Finland's startup economy**.
        - **Tampere**, while smaller, stands out as the **leading non-metropolitan startup city**, accounting for **7.4%** of all startups.
        - Other cities such as **Turku**, **Oulu**, and **Jyväskylä** also show startup activity, but at much smaller scales.
        - The data highlights the **centralization of startup activity** around major urban areas, where access to **talent, funding, infrastructure, and community** is more concentrated.
        """
    )
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
    mo.md(r"""Interestingly, there are no startups located above the Arctic Circle. The closest is Overpower, a sim racing startup based near the Arctic Circle.""")
    return


@app.cell
def _(MarkerCluster, company_info_df, folium, pd):
    def plot_clustered_company_locations(df: pd.DataFrame):
        df = df[["business_id", "name", "coordinates"]].dropna()
        df = df[df["coordinates"].str.contains(",")]

        df["coordinates"] = df["coordinates"].str.replace(r"[() ]", "", regex=True)
        df[["lat", "lon"]] = df["coordinates"].str.split(",", expand=True)
        df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
        df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
        df = df.dropna(subset=["lat", "lon"])

        m = folium.Map(
            location=[df["lat"].mean(), df["lon"].mean()],
            zoom_start=6,
            tiles="CartoDB positron",
            control_scale=True,
        )
        marker_cluster = MarkerCluster().add_to(m)

        for _, row in df.iterrows():
            popup = f"<b>{row['name']}</b><br>ID: {row['business_id']}"
            folium.Marker(location=[row["lat"], row["lon"]], popup=popup).add_to(
                marker_cluster
            )

        return m

    plot_clustered_company_locations(company_info_df)
    return


@app.cell
def _(mo):
    mo.md(r"""The highest concentration of startups is found at [Maria 01](https://maria.io/), the leading startup incubator in the Nordics, with over 40 startups represented in our sample.""")
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

        return fig

    plot_main_business_categories(
        df=company_info_df, column="main_line_of_business_category", top_n=15
    )
    return (plot_main_business_categories,)


@app.cell
def _(mo):
    mo.md(
        r"""
        #### Key Takeaways:

        - **IT Consulting and IT Services** dominate the startup landscape, representing **over 56%** of all companies in the dataset.
        - **Product Development, Research, and Design Services** is the second-largest category but accounts for **less than 5%**, showing a sharp drop after IT.
        - The distribution reveals a **strong concentration in IT and digital services**, mirroring the current trends in the global startup ecosystem.
        """
    )
    return


@app.cell
def _(company_info_df, plot_main_business_categories):
    plot_main_business_categories(
        df=company_info_df, column="main_line_of_business", top_n=15
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        #### Key Takeaways:
        - **Software Design and Development** is the dominant category, accounting for **over 46%** of all startups in the dataset.
        - **Computer Hardware and Software Consulting** and **Engineering Research and Development** follow, but each represents only a **small share (~3%)**.
        - The data shows a **clear skew toward software-centric startups**.
        """
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

        return fig

    plot_business_categories_by_employees(financial_df, company_info_df, 15)
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        #### Key Takeaways:
        - **IT Consulting and IT Services** employ by far the most people, with **over 12,000 employees**, reflecting both high concentration and operational scale in the sector.
        - **Mobile Phones and Accessories** is the second-largest employer, though significantly smaller, with under **2,000 employees**.
        - Some unexpected categories like **Cleaning Services** and **Sand, Gravel, Stone, and Other Aggregates** also appear, highlighting on-the-ground operational needs and scaling specificity in these secotrs.
        - Overall, the chart underscores the **dominance of IT-related employment**, while most other sectors show a more limited workforce footprint.
        """
    )
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

        return fig

    plot_financial_data_years(financial_df)
    return


@app.cell
def _(mo):
    mo.md(r"""Since public financial records become available only after the financial year has concluded, our dataset exhibits a noticeable lag. As a result, it captures the period between **2019 and 2023** most reliably, while data for earlier years is sparse and **2024 remains incomplete**.""")
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

        return fig

    plot_turnover_vs_profit_by_year(financial_df, company_info_df)
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        #### Key Takeaways:

        - The scatter plot shows a **positive correlation** between turnover and operating profit across all years, particularly for companies with higher revenues.  
          *(Note: The log scale excludes negative values, so loss-making companies are not visible in the chart.)*
        - Most startups are clustered in the **low-profit, low-turnover** range, consistent with early-stage or small-scale operations.
        - A few outliers stand out with **both high profitability and turnover**, likely reflecting more established or fast-growing ventures.
        - The **logarithmic axes** emphasize the broad spectrum of financial performance, from micro-startups to scale-ups.
        """
    )
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

        return fig

    plot_turnover_distribution_by_city(input_df=merged_df, year=2023)
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        #### Key Takeaways: Turnover Distribution by City (2023)

        - **The Helsinki Metropolitan Area** clearly dominates in terms of financial performance. With Helsinki and Espoo showing the widest turnover ranges and most high-value outliers, it’s evident that capital, scale, and investor attention continue to concentrate around the capital region. These cities act as financial anchors. HMA also shows the widest spread in turnover with numerous high-value outliers, including companies reaching above **100M€**, indicating the presence of major players.
        - **Tampere**, **Turku**, and **Oulu** display relatively balanced distributions, though their upper turnover bounds are lower compared to the capital region.
        - **Jyväskylä** shows the narrowest distribution and the lowest median, with fewer high-performing companies.
        - The use of a **logarithmic scale** emphasizes the skewed nature of startup turnover—most are small, but a few drive a disproportionately large share of economic value.
        """
    )
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
        return fig

    plot_median_financials_over_time(financial_df)
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        #### Key Takeaways:
        - **Median turnover** saw a sharp rise starting in **2017**, peaking around **2021–2023** at nearly **€191K**, before dipping in **2024**—likely due to partial data availability.
        - Despite growing turnover, both **median operating profit** and **net income** have remained **consistently negative** since **2018**, suggesting ongoing profitability challenges among startups.
        - The **lowest profitability point** occurred in **2023**, with median net income dropping below **–€60K**, highlighting increased burn or cost pressure.
        - The **uptick in 2024** across all metrics may signal a rebound, though it likely reflects **early filers or a biased subset** of the year’s data.
        - Overall, the trend illustrates a **scaling revenue base**, but persistent difficulty in achieving profitability for the median startup.
        """
    )
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
        return fig

    plot_median_ratios_over_time(financial_df)
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        #### Key Takeaways:

        - **Liquidity ratios** (quick and current) have generally remained above **1.0**, indicating that the median startup is able to cover short-term liabilities with current assets.
        - The peak in **2020**, with median ratios approaching **2.0**, reflects especially strong liquidity—likely due to **COVID-related uncertainty**, which may have driven companies to hoard cash.
        - The **solvency ratio** has remained consistently low—mostly **below 0.3**—highlighting that many startups are **equity-weak and debt-reliant**, a common trait in early-stage ventures.
        - The combination of **strong liquidity but weak solvency** suggests that while startups manage working capital effectively, they often lack long-term financial independence—**indicative of a strong reliance on venture capital**.
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

        df["employee_group"] = pd.Categorical(
            df["employee_group"], categories=labels, ordered=True
        )

        fig = px.box(
            df,
            x="employee_group",
            y="turnover_per_employee",
            points="outliers",
            title="Turnover per Employee Distribution by Company Size",
            labels={
                "turnover_per_employee": "€ / Employee",
                "employee_group": "Employee Group",
            },
            category_orders={"employee_group": labels},
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
def _(mo):
    mo.md(
        r"""
        Key Takeaways:

        - **Turnover per employee increases** with company size up to the **101–500 employee group**, which shows the **highest median productivity per employee**.
        - The **500+ group** has a slightly lower median than 101–500, indicating possible **efficiency plateauing** or increased structural overhead in the largest firms.
        - Small companies (**1–50 employees**) display **high variance**, with some startups achieving extremely high productivity and others generating very little revenue per employee.
        - The **21–50** and **51–100** ranges show consistent improvement in median turnover per employee, suggesting that growing companies often gain efficiency as they scale.
        - The **log scale** reveals the full spread, from micro firms with single-digit revenue per head to outliers exceeding **€10M per employee**, likely driven by IP-heavy or SaaS models.
        """
    )
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
            title=f"Turnover vs Operating Profit by Sector ({year})",
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
def _(mo):
    mo.md(
        r"""
        #### Key Takeaways:

        - There is a **strong overall positive correlation** between turnover and operating profit across sectors, particularly evident among companies with higher revenues. *(Note: The log scale excludes negative values, so loss-making companies are not visible in the chart.)*
        - Sectors such as **IT Consulting & Services**, **Product Development**, and **Finance** host some of the **largest and most profitable companies**, with multiple firms exceeding **€1M in operating profit**.
        - **Applications and Software** companies are clustered in the **mid-turnover range**, but many show **healthy margins**, with several above the **€100k profit line**.
        - **Bubble sizes** represent **employee counts**, suggesting that higher turnover and profit are often—but not always—associated with larger teams.
        - The **logarithmic scale** reveals the vast spread in financial performance, from startups generating under **€10k in turnover** to established firms nearing **€1B**.
        """
    )
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

        return fig

    plot_turnover_vs_profit_scatter(top_df)
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        #### Key Takeaways:

        - This chart highlights the **top-performing startups** (above the 80th percentile) in terms of **turnover and operating profit**, giving insight into Finland’s most successful scale-ups.
        - **HMD Global Oy** stands out dramatically with **€500M+ turnover** and multi-million euro profits—an outlier in both scale and profitability.
        - **Redhill Games Oy** and **Sensofusion Oy** demonstrate exceptionally high profitability relative to turnover, indicating **high-margin business models**.
        - Companies like **ResQ Club Oy** and **Gobybike Finland Oy** show a **strong balance between revenue and profitability**, reflecting Finnish consumers' increasing **preference for sustainable and responsible services**—from food waste reduction to eco-friendly commuting.
        - **Kamrock Oy**, while having high turnover, shows **low operating profit**, hinting at thin margins or high fixed costs. Which makes sense for an industrial company specialising in aggregates crushing and processing.
        - Several high-turnover companies such as **Sortter Oy** and **Treamer Oy** fall lower on the profit scale, underlining the importance of not just growth but also **operational efficiency**.
        - This filtered view reveals a **clear cluster of high-performing, many already operating in the **€5–50M turnover range** with healthy profits.
        """
    )
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

        return fig

    plot_turnover_and_profit_bars(top_df, top_n=25)
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        #### Key Takeaways:

        - **HMD Global Oy** dominates the chart with a **massive lead in turnover** and one of the **highest profit figures**, standing far apart from the rest of the sample.
        - Most top companies exhibit **healthy profitability relative to their turnover**, with **Sensofusion Oy**, **Redhill Games Oy**, and **Youpret Oy** showing particularly strong **profit margins**.
        - Companies like **Vertaa Ensin Suomi Oy**, **Sortter Oy**, and **Kamrock Oy** show relatively **low profitability** despite sizable turnover, indicating **thin margins** or **heavy cost structures**.
        - **ResQ Club Oy**, **Gobybike Finland Oy**, and **Smartum Oy** present a **strong balance between revenue and operating profit**, reflecting both **sustainability-driven consumer demand** and the **employee benefit culture** prevalent in Finland.
        """
    )
    return


if __name__ == "__main__":
    app.run()
