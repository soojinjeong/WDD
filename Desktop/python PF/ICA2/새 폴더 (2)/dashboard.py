### call library
import pandas as pd
import numpy as np

# Dash packages
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

from plotly.colors import DEFAULT_PLOTLY_COLORS  # chart default colors


# call dataset
df = pd.read_csv("covid-19.csv")
vacc = pd.read_csv("vaccine_g1.csv")

# year filter
years = list(df["year"].unique())
years.sort()

### App & Layout
# App structure
app = dash.Dash(__name__)
app.title = "Dashboard | Covid-19"
server = app.server

# App layout
app.layout = html.Div(
    [
        # Main Title
        html.H2(
            "Covid-19 Dashboard with Dash",
            style={"textAlign": "center", "marginBottom": 10, "marginTop": 10},
        ),
        # divide area - Left
        html.Div(
            [
                ### Indicater by Region, Bar by Country
                html.Div(
                    className="Indicator & Bar",
                    children=[
                        html.Div(
                            dcc.Graph(id="idc_afro"),
                            style={
                                "float": "left",
                                "display": "inline-block",
                                "width": "12%",
                            },
                        ),
                        html.Div(
                            dcc.Graph(id="idc_amro"),
                            style={
                                "float": "left",
                                "display": "inline-block",
                                "width": "12%",
                            },
                        ),
                        html.Div(
                            dcc.Graph(id="idc_wpro"),
                            style={
                                "float": "left",
                                "display": "inline-block",
                                "width": "12%",
                            },
                        ),
                        html.Div(
                            dcc.Graph(id="idc_euro"),
                            style={
                                "float": "left",
                                "display": "inline-block",
                                "width": "12%",
                            },
                        ),
                        html.Div(
                            dcc.Graph(id="idc_emro"),
                            style={
                                "float": "left",
                                "display": "inline-block",
                                "width": "12%",
                            },
                        ),
                        html.Div(
                            dcc.Graph(id="vaccination"),
                            style={
                                "float": "right",
                                "display": "inline-block",
                                "width": "40%",
                                "height": "310",
                            },
                        ),
                    ],
                ),
                # Line by Map
                html.Div(
                    className="Map",
                    children=[
                        html.Div(
                            dcc.Graph(id="map"),
                            style={"float": "left", "width": "100%"},
                        ),
                    ],
                ),
            ],
            style={"float": "left", "display": "inline-block", "width": "65%"},
        ),
        # divide - Right
        html.Div(
            [
                html.Div(
                    children=[
                        html.Div(
                            dcc.Dropdown(
                                id="id_year",
                                options=[{"label": i, "value": i} for i in years],
                                value=max(years),
                                style={"width": "50%"},
                            )
                        ),
                    ]
                ),
                html.Div(
                    className="Line",
                    children=[
                        html.Div(
                            dcc.Graph(id="line_case"),
                            style={
                                "float": "left",
                                "display": "inline-block",
                                "width": "100%",
                            },
                        ),
                        html.Div(
                            dcc.Graph(id="line_death"),
                            style={
                                "float": "left",
                                "display": "inline-block",
                                "width": "100%",
                            },
                        ),
                        html.Div(
                            dcc.Graph(id="bar_vacc"),
                            style={
                                "float": "left",
                                "display": "inline-block",
                                "width": "100%",
                            },
                        ),
                    ],
                ),
            ],
            style={"float": "right", "width": "35%"},
        ),
    ]
)

### Pie
@app.callback(Output("vaccination", "figure"), [Input("id_year", "value")])
def update_output(val):

    df_ch = df[df["year"] == val]
    df_ch = (
        df_ch.loc[:, ["who_region_x", "persons_fully_vaccinated"]]
        .groupby(by=["who_region_x"], as_index=False)
        .sum()
    )

    df_ch["text"] = (
        round(df_ch["persons_fully_vaccinated"] / 1000000, 1).astype(str) + "M"
    )

    trace = go.Pie(
        labels=df_ch["who_region_x"],
        values=df_ch["persons_fully_vaccinated"],
        name="",
        text=df_ch["text"],
        textinfo="label+percent",
        hovertemplate="[%{label}]<br> Revenue: %{text}<br> Rate: %{percent}",
        hoverinfo="text",
        insidetextorientation="tangential",
        hole=0.4,
    )

    data = [trace]

    layout = go.Layout(
        title="Fully vaccinated",
        showlegend=False,
        height=330,
        margin=dict(l=50, r=50, b=10, t=50),
    )

    figure = {"data": data, "layout": layout}

    return figure


### Indicator

########## by Region
@app.callback(
    [
        Output("idc_afro", "figure"),
        Output("idc_amro", "figure"),
        Output("idc_wpro", "figure"),
        Output("idc_euro", "figure"),
        Output("idc_emro", "figure"),
    ],
    [Input("id_year", "value")],
)
def update_output(val):

    # reg - unique value's
    reg = df["who_region_x"].unique()

    # data by Region
    figures = []

    for i in range(len(reg)):
        df_fig = df[(df["year"] == val) & (df["who_region_x"] == reg[i])]
        df_fig = round(df_fig.loc[:, ["new_cases", "new_deaths"]].sum(), 1)

        values = df_fig["new_cases"]
        deltas = df_fig["new_deaths"]

        trace = go.Indicator(
            mode="number+delta",
            value=values,
            number=dict(
                font_size=30
            ),  # font size fixed (If not, it is responsive and the size is different)
            delta=dict(
                reference=values - deltas,
                font_size=20,
                relative=False,
                increasing_color="#3078b4",
                increasing_symbol="",
                decreasing_color="#d13b40",
                decreasing_symbol="",
                position="top",
            ),
            title=dict(text=reg[i], font_size=20),
        )
        data = [trace]

        layout = go.Layout(height=310)
        figure = go.Figure(data, layout)
        figures.append(figure)

    return figures[0], figures[1], figures[2], figures[3], figures[4]


### Map
### Choropleth Map
@app.callback(Output("map", "figure"), [Input("id_year", "value")])
def update_output(val):

    # Code3 by Country
    df_code = df.loc[:, ["country_x", "country_clean"]].drop_duplicates()

    # data
    df_map = df[df["year"] == val]
    df_map = (
        df_map.loc[:, ["country_x", "new_cases"]]
        .groupby(by=["country_x"], as_index=False)
        .sum()
    )

    # Join map & Code3
    df_m = df_map.merge(df_code, on="country_x", how="left")

    # hover_text
    df_m["text"] = (
        df_m["country_x"]
        + " - Total New Cases : "
        + round(df_m["new_cases"] / 1000000, 1).astype(str)
        + "M"
    )

    trace = go.Choropleth(
        locations=df_m["country_clean"],
        z=df_m["new_cases"],
        text=df_m["text"],
        hoverinfo="text",  # Activate only entered text
        colorscale="Reds",  # color= Greens, Reds, Oranges, ...
        autocolorscale=False,
        reversescale=False,
        marker_line_color="darkgray",
        marker_line_width=0.5,
        colorbar_title="new_cases (M)",
        colorbar_thickness=15,  # bar thickness (default=30)
        colorbar_len=1,  # bar lenght (default=1)
        colorbar_x=1.01,  # bar x location (default=1.01, -2~3)
        colorbar_ticklen=10,  # bar grid line length (default=5)
    )

    data = [trace]
    layout = go.Layout(
        title="New Case Map",
        geo=dict(
            showframe=False, showcoastlines=False, projection_type="equirectangular"
        ),
        height=800,
        margin=dict(l=50, r=50, b=20, t=50),
    )

    figure = {"data": data, "layout": layout}

    return figure


###Bar

#####Rank for vaccinated Top 10


@app.callback(Output("bar_vacc", "figure"), Input("id_year", "value"))
def update_bar_chart(val):

    df_con = vacc.loc[:, ["top10", "total_10", "fullly_10"]]
    df_con = df_con.sort_values(by=["total_10"], ascending=False)

    df_con["rank"] = list(range(1, len(df_con["top10"]) + 1))
    df_con = df_con[df_con["rank"] <= 10].reset_index(drop=True)

    trace1 = go.Bar(
        y=df_con["top10"],
        x=df_con["total_10"],
        name="Total Vaccination",
        orientation="h",
    )
    trace2 = go.Bar(
        y=df_con["top10"],
        x=df_con["fullly_10"],
        name="Person Fully Vaccinated",
        orientation="h",
    )

    data = [trace1, trace2]

    layout = go.Layout(
        title="Country (Top 10)",
        title_y=0.8,
        height=500,
        barmode="group",
        yaxis=dict(autorange="reversed"),
    )

    figure = {"data": data, "layout": layout}

    return figure


### Scatter & Line Chart

##### By death


@app.callback(Output("line_death", "figure"), [Input("id_year", "value")])
def update_output(val):

    df_line = df[df["year"] == val]
    df_line = (
        df_line.loc[:, ["new_deaths", "year", "month"]]
        .groupby(by=["year", "month"], as_index=False)
        .sum()
    )

    # hover_text
    df_line["text"] = round(df_line["new_deaths"] / 1000000, 1).astype(str) + "M"

    trace = go.Scatter(
        x=df_line["month"],
        y=df_line["new_deaths"],
        text=df_line["text"],
        hovertemplate="%{text}",
        mode="lines+markers",
        marker=dict(size=10),
        name=val,
    )

    data = [trace]

    layout = go.Layout(
        title="Monthly Deaths",
        # tick0 = Set placement of first tick (used with dtick), dtick = set spacing between ticks
        xaxis=dict(title="Month", tickmode="linear", tick0=1, dtick=1, showgrid=False),
        legend=dict(
            orientation="h",  # option= 'v', 'h'
            xanchor="center",  # option= 'auto', 'left', 'center', 'right'
            x=0.5,  # x= 0(left), 1 (right)
            yanchor="bottom",  # option= 'auto', 'top', 'middle', 'bottom'
            y=-1,  # 1.1,         # y= 1(top), -1(bottom)
        ),
        height=300,
        margin=dict(l=50, r=10),
    )

    figure = {"data": data, "layout": layout}

    return figure


### Scatter & Line Chart

##### By Cases


@app.callback(Output("line_case", "figure"), [Input("id_year", "value")])
def update_output(val):

    df_line = df[df["year"] == val]
    df_line = (
        df_line.loc[:, ["new_cases", "year", "month"]]
        .groupby(by=["year", "month"], as_index=False)
        .sum()
    )

    # hover_text
    df_line["text"] = round(df_line["new_cases"] / 1000000, 1).astype(str) + "M"

    trace = go.Scatter(
        x=df_line["month"],
        y=df_line["new_cases"],
        text=df_line["text"],
        hovertemplate="%{text}",
        mode="lines+markers",
        marker=dict(size=10),
        name=val,
    )

    data = [trace]

    layout = go.Layout(
        title="Monthly Cases",
        # tick0 = Set placement of first tick (used with dtick), dtick = set spacing between ticks
        xaxis=dict(title="Month", tickmode="linear", tick0=1, dtick=1, showgrid=False),
        legend=dict(
            orientation="h",  # option= 'v', 'h'
            xanchor="center",  # option= 'auto', 'left', 'center', 'right'
            x=0.5,  # x= 0(left), 1 (right)
            yanchor="bottom",  # option= 'auto', 'top', 'middle', 'bottom'
            y=-1,  # 1.1,         # y= 1(top), -1(bottom)
        ),
        height=300,
        margin=dict(l=50, r=10),
    )

    figure = {"data": data, "layout": layout}

    return figure


### App Launch
# Run App
if __name__ == "__main__":
    app.run_server(debug=False)
