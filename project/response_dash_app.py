import base64
# import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
import plotly.graph_objects as go
from flask_login import current_user

from project import db
from project import server

from flask import request, session

import json

from .parser_response import *
from .models import *
import pandas as pd
import numpy as np


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


resp_dash_app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=external_stylesheets,
    url_base_pathname='/response/'
)

resp_dash_app.config.suppress_callback_exceptions = True

upload_styles = {
    'width': '100%',
    'height': '60px',
    'lineHeight': '60px',
    'borderWidth': '1px',
    'borderStyle': 'dashed',
    'borderRadius': '5px',
    'textAlign': 'center',
    'margin': '10px'
}

resp_dash_app.layout = html.Div([
    html.Div(id='user-div'),
    html.Div(['Force csv file.']),
    dcc.Upload(
        id='upload-data-force',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select File')
        ]),
        style=upload_styles,
        multiple=False
    ),
    html.Div(['Displacement csv file.']),
        dcc.Upload(
        id='upload-data-displ',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select File')
        ]),
        style=upload_styles,
        multiple=False
    ),
    html.Div(['Output file.']),
        dcc.Upload(
        id='upload-data-outfile',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select File')
        ]),
        style=upload_styles,
        multiple=False
    ),
    html.Div(id='output-data-upload'),
])


def read_from_csv(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), header=[1,2])
            print(df.head())
        # elif 'xls' in filename:
        #     # Assume that the user uploaded an excel file
        #     df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return None
    
    return df
    

def get_global_df(df_displ, df_force):
    global df_global
    df_global = pd.DataFrame()
    
    df_force = df_force.groupby([df_force.columns[0]], as_index=False, sort=False).sum()
    df_force.to_csv('out_react_verification.csv')
    
    df_force = df_force.iloc[:, -1]
    df_displ = df_displ.iloc[:, -1]
    
    unit_displ = df_displ.name
    unit_react = df_force.name
    
    factor_displ = 1000 if '[m]' in unit_displ else 1
    factor_force = 1000 if '[N]' in unit_react else 1

    df_global['displacements'] = df_displ
    df_global['reactions'] = df_force

    df_global = df_global.apply(lambda x: (x.astype(float)))
    df_global.index += 1

    df_global.iloc[:, 0] = df_global.iloc[:, 0].apply(lambda x: x*(-1 * factor_displ))
    df_global.iloc[:, 1] = df_global.iloc[:, 1].apply(lambda x: x/( factor_force))
    

def parse_outfile(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return parse_global_data(decoded.decode())


@resp_dash_app.callback(Output('output-data-upload', 'children'),
                    [Input('upload-data-force', 'contents'),
                    Input('upload-data-displ', 'contents'),
                    Input('upload-data-outfile', 'contents')
                    ],
                    [State('upload-data-force', 'filename'),
                    State('upload-data-displ', 'filename'),
                    State('upload-data-outfile', 'filename')
                    ])
def update_output(file_force, file_displ, file_out, name_1, name_2, name_3):
    
    children = []
    fig = go.Figure()
    
    if file_force != None and file_displ != None:
        
        df_force = read_from_csv(file_force, name_1)
        df_displ = read_from_csv(file_displ, name_2)
        
        get_global_df(df_displ, df_force)
        
        df_global.insert(0, 'step index', df_global.index)

    
        fig.add_trace(go.Scatter(
                        x=df_global['displacements'].values, 
                        y=df_global['reactions'].values, 
                        mode='lines+markers+text',
                        name='Response',
                        marker=dict(
                            size=6
                        ),
                        text=df_global['step index'],
                        textposition="top right",
                )
        )
        
        fig.update_layout(
                title='Response',
                xaxis_title="Displacement",
                yaxis_title="Force",
        )
        
        results_table = dash_table.DataTable(
            id = "results_table",
            columns = [{"name": i, "id": i} for i in df_global.columns],
            data = df_global.to_dict("records"),
            style_cell={
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'maxWidth': 0
                },
            style_table={
                        'overflowY': 'auto',
                        'maxHeight': 200,
                        
                        },
            )

        if file_out != None:
            step_numbers, unconverged_step_numbers, steps_in_phases, phases = parse_outfile(file_out)
            df_unconv = df_global.iloc[df_global.index.isin(list(map(lambda x: x[0], unconverged_step_numbers)))] 
            print(df_unconv)
            fig.add_trace(go.Scatter(
                x=df_unconv['displacements'].values, 
                y=df_unconv['reactions'].values, 
                mode='markers',
                name='Unconverged steps',
                marker=dict(
                    color='red',
                    size=6
                ))
            )
        
    children.append(html.Div([
        dcc.Graph(
            id = 'force-displ',
            style={'height': '800px',
                   'width': '800px'},
            figure = fig),
        ]))
    try:
        children.append(html.Div([
            results_table
        ]))
    except NameError:
        pass
    
    return children
    

    
    

        
