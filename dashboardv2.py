from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objs as go
import finnhub
import yfinance as yf
import datetime as dt
import random

with open("finnhubkey.txt") as f:
    api_key = f.read()

finnhub_client = finnhub.Client(api_key=api_key)

DEFAULT_PLOT_LAYOUT = dict(
    hovermode="x unified",
    plot_bgcolor="#444545",
    paper_bgcolor="#444545",
    font=dict(color="#EA526F"),
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False),
    margin=dict(l=10, r=10, b=10, t=10),
    colorway=["#368F8B"],
    clickmode="event+select",
)


def get_all_tickers():
    return list(map(lambda x: x["symbol"], finnhub_client.stock_symbols("US")))


def make_company_card(name, location, logo_url, summary):
    return [
        dbc.CardImg(src=logo_url, top=True),
        dbc.CardBody(
            [
                html.H4(name, className="card-title"),
                html.P(
                    summary,
                    className="card-text",
                ),
            ]
        ),
    ]


def make_summary_card(ticker):
    return [
        dbc.CardGroup(
            [
                dbc.Card(
                    [
                        dbc.CardHeader("50 Day Average"),
                        dbc.CardBody(
                            html.H4(
                                "{:.2f}".format(
                                    ticker.info.get("fiftyDayAverage", "No Data")
                                )
                            )
                        ),
                    ],
                    className="summary-card",
                ),
                dbc.Card(
                    [
                        dbc.CardHeader("200 Day Average"),
                        dbc.CardBody(
                            html.H4(
                                "{:.2f}".format(
                                    ticker.info.get("twoHundredDayAverage", "No Data")
                                )
                            )
                        ),
                    ],
                    className="summary-card",
                ),
            ]
        ),
        dbc.CardGroup(
            [
                dbc.Card(
                    [
                        dbc.CardHeader("Short Ratio"),
                        dbc.CardBody(html.H4(ticker.info.get("shortRatio", "No Data"))),
                    ],
                    className="summary-card",
                ),
                dbc.Card(
                    [
                        dbc.CardHeader("Bid Size"),
                        dbc.CardBody(html.H4(ticker.info.get("bidSize", "No Data"))),
                    ],
                    className="summary-card",
                ),
            ]
        ),
        dbc.CardGroup(
            [
                dbc.Card(
                    [
                        dbc.CardHeader("Day Low"),
                        dbc.CardBody(html.H4(ticker.info.get("dayLow", "No Data"))),
                    ],
                    className="summary-card",
                ),
                dbc.Card(
                    [
                        dbc.CardHeader("Day High"),
                        dbc.CardBody(html.H4(ticker.info.get("dayHigh", "No Data"))),
                    ],
                    className="summary-card",
                ),
            ]
        ),
        dbc.CardGroup(
            [
                dbc.Card(
                    [
                        dbc.CardHeader("Close"),
                        dbc.CardBody(
                            html.H4(ticker.info.get("previousClose", "No Data"))
                        ),
                    ],
                    className="summary-card",
                ),
                dbc.Card(
                    [
                        dbc.CardHeader("Open"),
                        dbc.CardBody(html.H4(ticker.info.get("open", "No Data"))),
                    ],
                    className="summary-card",
                ),
            ]
        ),
        dbc.CardGroup(
            [
                dbc.Card(
                    [
                        dbc.CardHeader("Full Time Employees"),
                        dbc.CardBody(
                            html.H4(ticker.info.get("fullTimeEmployees", "No Data"))
                        ),
                    ],
                    className="summary-card",
                ),
            ]
        ),
    ]


def make_article_card(symbol, date=dt.datetime.today(), days_ago=3):
    week_ago = (date - dt.timedelta(days=days_ago)).strftime("%Y-%m-%d")
    articles = finnhub_client.company_news(
        symbol, _from=week_ago, to=date.strftime("%Y-%m-%d")
    )
    if len(articles) == 0:
        week_ago = (dt.datetime.today() - dt.timedelta(days=days_ago)).strftime(
            "%Y-%m-%d"
        )
        articles = finnhub_client.company_news(
            symbol, _from=week_ago, to=dt.datetime.today().strftime("%Y-%m-%d")
        )
    news_articles_cols = [
        dbc.CardGroup(
            [
                dbc.Card(
                    [
                        dbc.CardImg(src=article["image"], top=True),
                        dbc.CardBody(
                            [
                                html.H4(article["headline"], className="card-title"),
                                html.H6(
                                    dt.datetime.fromtimestamp(
                                        article["datetime"]
                                    ).strftime("%m/%d/%Y"),
                                    className="card-subtitle",
                                ),
                                html.P(
                                    article["summary"],
                                    className="card-text",
                                ),
                                dbc.CardLink("Read More", href=article["url"]),
                            ]
                        ),
                    ],
                )
                for article in articles[i : i + 4]
            ]
        )
        for i in range(0, len(articles), 4)
    ]

    return news_articles_cols


symbols = get_all_tickers()


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.themes.GRID])

grid = [
    dbc.Col(
        [
            dbc.Card(
                html.H3("Stocks Dashboard", className="navbar-light"),
                body=True,
                color="#3d3d3d",
            ),
            html.Div(
                [
                    dbc.Input(
                        id="symbol-input",
                        placeholder="AAPL",
                        # autoComplete=True,
                        value="AAPL",
                        debounce=True,
                        className="p-2",
                    ),
                    dbc.Button(
                        id="random-stock-button",
                        children=["Random Ticker"],
                        block=True,
                        className="p-2",
                    ),
                ],
                className="p-2",
            ),
        ],
        width=2,
        className="navbar-group",
        style={"height": "100vh", "float": "left"},
    ),
    dbc.Row(
        [
            dbc.Col(
                [dcc.Loading(dbc.Card(id="company-profile-card"))],
                width=2,
            ),
            dbc.Col(
                [dcc.Loading(dbc.Card(id="company-summary-card"))],
                width=2,
            ),
            dbc.Col([dcc.Loading(dbc.Card(id="company-news-card"))], width=8),
        ],
        no_gutters=True,
    ),
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.CardGroup(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardHeader(
                                                html.H4("Explore tick data")
                                            ),
                                            dbc.CardBody(
                                                """
                                            Click on data points in the tick graph to filter
                                            news articles by the selected data point's date.
                                            It is interesting to see news events and how they
                                            revolve around certain data points. This is especially
                                            true for data points with high spikes.
                                            """
                                            ),
                                        ],
                                        # style={"height": "100%"}
                                    ),
                                    dbc.Card(
                                        [
                                            dbc.CardHeader(html.H4("Period")),
                                            dbc.CardBody(
                                                dcc.RadioItems(
                                                    id="period-radio-item",
                                                    options=[
                                                        {
                                                            "label": "1D",
                                                            "value": "1d",
                                                        },
                                                        {
                                                            "label": "5D",
                                                            "value": "5d",
                                                        },
                                                        {
                                                            "label": "1M",
                                                            "value": "1mo",
                                                        },
                                                        {
                                                            "label": "3M",
                                                            "value": "3mo",
                                                        },
                                                        {
                                                            "label": "6M",
                                                            "value": "6mo",
                                                        },
                                                        {
                                                            "label": "1Y",
                                                            "value": "1y",
                                                        },
                                                        {
                                                            "label": "2Y",
                                                            "value": "2y",
                                                        },
                                                        {
                                                            "label": "5Y",
                                                            "value": "5y",
                                                        },
                                                        {
                                                            "label": "10Y",
                                                            "value": "10y",
                                                        },
                                                    ],
                                                    value="3mo",
                                                    labelStyle={
                                                        "display": "inline-block",
                                                        "padding": "10px",
                                                    },
                                                ),
                                            ),
                                        ]
                                    ),
                                    dbc.Card(
                                        [
                                            dbc.CardHeader(html.H4("Status")),
                                            dbc.CardBody(
                                                dcc.Checklist(
                                                    id="status-checklist",
                                                    options=[
                                                        {
                                                            "label": "High",
                                                            "value": "High",
                                                        },
                                                        {
                                                            "label": "Low",
                                                            "value": "Low",
                                                        },
                                                        {
                                                            "label": "Open",
                                                            "value": "Open",
                                                        },
                                                    ],
                                                    value=[
                                                        "High",
                                                        "Low",
                                                        "Open",
                                                    ],
                                                )
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                        ],
                        width=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dcc.Loading(
                                        dcc.Graph(
                                            id="company-tick-graph",
                                            figure=dict(layout=DEFAULT_PLOT_LAYOUT),
                                        ),
                                    )
                                ],
                            )
                        ],
                        width=8,
                    ),
                ],
                no_gutters=True,
            ),
        ],
        fluid=True,
    ),
]

app.layout = html.Div(grid)
server = app.server # for deployment

@app.callback(
    [
        Output("company-profile-card", "children"),
        Output("company-summary-card", "children"),
        Output("period-radio-item", "value"),
        Output("company-tick-graph", "selectedData"),
    ],
    [Input("symbol-input", "value")],
    State("period-radio-item", "value"),
)
def symbol_input(symbol, curr_radio):

    ticker = yf.Ticker(symbol)

    name = ticker.info.get("longName", "")
    location = f"{ticker.info.get('city', '')}, {ticker.info.get('state', '')}"
    logo_url = ticker.info.get(
        "logo_url",
        "https://dash-bootstrap-components.opensource.faculty.ai/static/images/placeholder286x180.png",
    )
    if logo_url == "":
        logo_url = "https://dash-bootstrap-components.opensource.faculty.ai/static/images/placeholder286x180.png"
    summary = ticker.info.get("longBusinessSummary", "")
    company_card = make_company_card(name, location, logo_url, summary)
    summary_card = make_summary_card(ticker)

    return company_card, summary_card, curr_radio, None


@app.callback(
    Output("symbol-input", "value"), [Input("random-stock-button", "n_clicks")]
)
def random_stock(n_clicks):
    if n_clicks:
        errord = False
        while not errord:
            try:
                choice = random.choice(symbols)
                yf.Ticker(choice).info
                return choice
            except:
                choice = random.choice(symbols)
    else:
        return "AAPL"


@app.callback(
    Output("company-tick-graph", "figure"),
    [
        Input("period-radio-item", "value"),
        Input("status-checklist", "value"),
    ],
    State("symbol-input", "value"),
)
def graph_input(period, checked, symbol):
    # get the graph
    ticker = yf.Ticker(symbol)
    if "d" in period:
        ticks = (
            ticker.history(period=period, interval="5m")
            .reset_index()
            .rename(columns={"Datetime": "Date"})
        )
    else:
        ticks = ticker.history(period=period).reset_index()
    ticks = ticks[["Date"] + checked]
    ticks.Date = ticks.Date.astype(str)
    fig = go.Figure()
    for check in checked:
        fig.add_trace(
            go.Scatter(
                x=ticks["Date"],
                y=ticks[check],
                mode="lines+markers",
                name=check,
                customdata=["Date"],
            )
        )
    colorway = {"High": "#EA526F", "Low": "#368F8B", "Open": "#023436"}
    fig.update_layout(DEFAULT_PLOT_LAYOUT)
    fig.update_layout(dict(colorway=[colorway[k] for k in checked]))
    fig.update_traces(mode="lines+markers")
    return fig


@app.callback(
    Output("company-news-card", "children"),
    [Input("company-tick-graph", "selectedData")],
    State("symbol-input", "value"),
)
def update_articles(selected, symbol):
    if selected:
        chosen_date = selected["points"][0]["x"]
        if isinstance(chosen_date, str):
            date = dt.datetime.fromisoformat(chosen_date)
        else:
            date = dt.datetime(chosen_date)
        article_card = make_article_card(symbol, date=date)
    else:
        article_card = make_article_card(symbol)

    return article_card


if __name__ == "__main__":
    app.run_server(debug=True, port=8999)
