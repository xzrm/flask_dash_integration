import base64
# import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
from flask_login import current_user

from project import db
from project import server

from flask import request, session

import json

from .data import *
from .models import *
import pandas as pd
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']



dash_app1 = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=external_stylesheets,
    url_base_pathname='/app1/'
    # requests_pathname_prefix='/chart1'
)



dash_app1.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    html.Div(id='path'),
    html.Div(id='prev-results-div'),
    html.Div(id='user-div'),
    html.Div(id='output-data-upload'),
])


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    step_objects, convergence = get_data([decoded.decode()], "displacement_norm", 0.001)

    fig = px.line(dict(iterations=list(range(1, len(convergence.all_iterations) + 1)),
                       variations=convergence.all_iterations),
                       x='iterations', 
                       y='variations', 
                       title='convergence')
    
    fig.update_traces(mode='lines')
    fig.update_layout(yaxis_type="log")
    
    print("PROJECT DATA FROM PARSER")
    
    
    db.session.query(Data).delete()
    db.session.execute("ALTER SEQUENCE data_id_seq RESTART WITH 1")
    db.session.commit()
    
    print("commiting worked")
    
    project = Project.query.filter(Project.id == int(session['project_id'])).first()
    r = project.results 
    print(r.id)
    # PROJECT_DATA.results = curr_result
    
    update_results(step_objects, r)
    
    # print("Length of results is:", len(PROJECT_DATA.results.data))
    db.session.commit()

    return html.Div([
        html.H5(filename),
        html.Hr(), 
        dcc.Graph(id='conv_plot', figure=fig)
    ])
    
def update_results(obj_list, results_db):
    for obj in obj_list:
        data = {}
        data['displacement_norm'] = obj.displacement_norm
        data['force_norm'] = obj.force_norm
        data['energy_norm'] = obj.energy_norm
        
        data_json = json.dumps(data)
        print(data_json)
        
        d = Data(data=data_json, result_id=results_db.id)
        db.session.add(d)
        results_db.data.append(d)
    
    
def draw_graph(values):
    fig = px.line(dict(iterations=list(range(1, len(values) + 1)),
                       variations=values),
                       x='iterations', 
                       y='variations', 
                       title='convergence')
    
    fig.update_traces(mode='lines')
    fig.update_layout(yaxis_type="log")
    
    return html.Div([
        html.Hr(), 
        dcc.Graph(
            id = 'conv_plot',
            figure = fig)
    ])
    

@dash_app1.callback(Output('user-div', 'children'),
            [Input('user-div', 'id')])
def cur_user(input1):


    if current_user.is_authenticated:
        project_id = session['project_id']
        user_id = current_user.id
        user = User.query.filter(User.id == int(user_id)).first()
        project = Project.query.filter(Project.id == int(project_id)).first()
        

        r = project.results
        print("PROJECT_DATA RESULTS", r)
        # r = sorted(r, key=lambda i: i.id)
        # res_data = r.data
        # res_data = sorted(res_data, key=lambda i: i.id)
        
        # print("Length of results on fresh start is:", len(res_data))
        # data_list = []
        # for d in res_data:
        #     new_d = json.loads(d.data)
        #     data_list.append(new_d)

        # GLOBAL_DF = pd.DataFrame(data_list)
        # print(GLOBAL_DF.head(100))

                
        return f'User: {current_user.username}; current project {project.title}'  
    else:
        return 'User non authenticated'


# @dash_app1.callback(Output('prev-results-div', 'children'),
#             [Input('prev-results-div', 'id')])
# def upload_results(input1):
#     r = PROJECT_DATA.results
#     for d in r.data:
#         new_d = json.loads(d.data)
#         print(new_d)
    

    
@dash_app1.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_output(content, name):
    if current_user.is_authenticated:
        print("Plotting")
        if content is not None:
            children = [
                parse_contents(content, name)
            ]
            return children
        else:
            
            project = Project.query.filter(Project.id == int(session['project_id'])).first()
            res_data = sorted(project.results.data, key=lambda i: i.id)
            
            data_list = []
            for d in res_data:
                new_d = json.loads(d.data)
                data_list.append(new_d)

            df = pd.DataFrame(data_list)
            if df.empty:
                return
            values_displ = np.concatenate(df['displacement_norm'].values)
            print(values_displ)
            children = [
                draw_graph(values_displ)
            ]
            return children
    
    
