import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State


app = dash.Dash(
    __name__,
    requests_pathname_prefix='/chart1'
)

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    ),
    html.Div(id='page-content'),
])

# if __name__ == '__main__':
#     app.run_server(debug=True)
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    # this is called every page load and every URL change
    # you can update your components with this URL in here
    return html.Div([
        html.H3('You are on page {}'.format(pathname))
    ])