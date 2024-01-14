import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from flask_pymongo import PyMongo
import pandas as pd
import dash_table

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# MongoDB Configuration
app.server.config['MONGO_URI'] = 'mongodb://localhost:27017/formpage'
mongo = PyMongo(app.server)

# Retrieve data from MongoDB collection
user_data = list(mongo.db.users.find())
user_df = pd.DataFrame(user_data)

# Define the available options for the sidebar
sidebar_options = [
    {'label': 'Users by Country', 'value': 'country-line-chart'},
    {'label': 'User Ratings', 'value': 'rating-bar-chart'},
    {'label': 'Recommendation', 'value': 'recommend-pie-chart'},
    {'label': 'All Feedbacks', 'value': 'all-feedbacks'},
]

# Layout of the dashboard
app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1("User Feedback Dashboard", className="text-center"),
                className="mb-4"
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Dropdown(
                                id='sidebar-dropdown',
                                options=sidebar_options,
                                value=sidebar_options[0]['value'],
                                multi=False,
                                clearable=False,
                                className="mb-3",
                            ),
                        )
                    ),
                    width=3,
                ),
                dbc.Col(
                    dbc.Card(
                        dcc.Loading(
                            dcc.Graph(id='main-chart'),
                            type="circle",
                        ),
                    ),
                    width=9,
                ),
            ],
        ),
        dbc.Row(
            dbc.Col(
                html.Div(children='''
                    Explore user feedback statistics.
                '''),
                className="mt-4"
            )
        ),
        dbc.Row(
            dbc.Col(
                dash_table.DataTable(
                    id='all-feedbacks-table',
                    columns=[
                        {'name': 'Name', 'id': 'Name'},
                        {'name': 'Feedback', 'id': 'Feedback'},
                    ],
                    data=[],
                    page_size=10,
                    sort_action='native',
                    style_table={'height': '300px', 'overflowY': 'auto'},
                ),
                className="mt-4"
            )
        ),
    ],
    fluid=True,
)

# Callback to update the main chart based on the selected option
@app.callback(
    Output('main-chart', 'figure'),
    Output('all-feedbacks-table', 'data'),
    [Input('sidebar-dropdown', 'value')]
)
def update_main_chart(selected_option):
    if selected_option == 'country-line-chart':
        chart_data = {
            'data': [
                {'x': user_df['country'].value_counts().index, 'y': user_df['country'].value_counts().values, 'type': 'line', 'name': 'Users by Country'},
            ],
            'layout': {
                'title': 'Users by Country (Line Chart)'
            }
        }
        return chart_data, []  # Returning an empty list for the DataTable data

    elif selected_option == 'rating-bar-chart':
        chart_data = {
            'data': [
                {'x': user_df['rating'].value_counts().index, 'y': user_df['rating'].value_counts().values, 'type': 'bar', 'name': 'User Ratings'},
            ],
            'layout': {
                'title': 'User Ratings (Bar Chart)'
            }
        }
        return chart_data, []  # Returning an empty list for the DataTable data

    elif selected_option == 'recommend-pie-chart':
        chart_data = {
            'data': [
                {'labels': ['Not Recommended', 'Recommended'], 'values': user_df['recommend'].value_counts().values, 'type': 'pie', 'name': 'Recommendation'},
            ],
            'layout': {
                'title': 'Recommendation (Pie Chart)'
            }
        }
        return chart_data, []  # Returning an empty list for the DataTable data

    elif selected_option == 'all-feedbacks':
        table_data = [
            {'Name': user_df.iloc[i]['name'], 'Feedback': user_df.iloc[i]['feedback']} for i in range(len(user_df))
        ]
        return {}, table_data  # Returning DataTable data

    return {}, []  # Returning empty data for unknown options

if __name__ == '__main__':
    app.run_server(debug=True)
