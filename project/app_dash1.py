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

from .parser_convergence import *
from .models import *
import pandas as pd
import numpy as np
from .text_utils import *

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']



dash_app1 = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=external_stylesheets,
    url_base_pathname='/convergence/'
)



dash_app1.layout = html.Div([
    html.Div(id='user-div'),
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
    html.Div(id='output-data-upload'),
])

    
def draw_graph(df, norm, html_id):
    all_variations = np.concatenate(df[norm].values)
    
    df_loc = df
    df_loc['step length'] = df[norm].apply(lambda x: len(x))
    df_loc['cum sum'] = df['step length'].cumsum()
    df_loc['last variation'] = df[norm].apply(lambda x: x[-1])
    
    
    fig = go.Figure()
    
    fig = px.line(dict(iterations=list(range(1, len(all_variations) + 1)),
                   variations=all_variations),
                   x='iterations', 
                   y='variations', 
                   title=norm.title())
    
    
    mask_converged_steps_this = (df_loc['converged'] == True) & df['governing norm'].apply(lambda x: norm in x.keys())

    
    fig.add_trace(go.Scatter(x=df_loc['cum sum'][mask_converged_steps_this], 
                            y=df_loc['last variation'][mask_converged_steps_this],
                            mode='markers',
                            name='converged steps current norm',
                            marker=dict(
                               color='lime',
                               size=6,
                               line=dict(
                                   color='black',
                                   width=1
                               ))
                            ))
    
    mask_converged_steps_other = (df_loc['converged'] == True) & df['governing norm'].apply(lambda x: norm not in x.keys())
    
    
    fig.add_trace(go.Scatter(x=df_loc['cum sum'][mask_converged_steps_other], 
                             y=df_loc['last variation'][mask_converged_steps_other],
                             mode='markers',
                             name='converged steps other norm',
                             marker=dict(
                                color='aqua',
                                size=6,
                                line=dict(
                                    color='black',
                                    width=1
                                ))
                             ))
    
    mask_unconverged_steps = (df_loc['converged'] == False)
    
    
    fig.add_trace(go.Scatter(x=df_loc['cum sum'][mask_unconverged_steps], 
                             y=df_loc['last variation'][mask_unconverged_steps],
                             mode='markers',
                             name='unconverged steps',
                             marker=dict(
                                color='red',
                                size=6,
                                line=dict(
                                    color='black',
                                    width=1
                                ))
                             ))
    
    max_val = np.amax(all_variations)
    min_val = np.amin(all_variations)
    print(max_val, min_val)
    fig.update_layout(yaxis_type="log",
                      yaxis = dict(rangemode = 'tozero')
                    #   yaxis=dict(range=[min_val, max_val]),
                    )
    
    print(df_loc)
    df_1 = df_loc
    df_1[norm] = df_1[norm].apply(lambda x: str(x))
    
    df_1["id"] = df_1.index + 1
    df_1 = df_1.loc[:, ["id", "step number", norm,  "last variation", "step length", "cum sum"]]
    print(df_1)

    
    return html.Div([
        html.Hr(), 
        dcc.Graph(
            id = html_id,
            figure = fig),
        html.Hr(), 
        dash_table.DataTable(
            id = html_id + "_table",
            columns = [{"name": i, "id": i} for i in df_1.columns],
            data = df_1.to_dict("records"),
            style_cell={
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'maxWidth': 0
                },
            style_cell_conditional=[
                {'if': {'column_id': 'id'},
                'width': '5%'},
                {'if': {'column_id': 'step number'},
                'width': '5%'},
                {'if': {'column_id': norm},
                'width': '60%'},
                {'if': {'column_id': 'step length'},
                'width': '10%'},
                {'if': {'column_id': 'cum sum'},
                'width': '10%'},
            ],
            style_table={
                        'overflowY': 'auto',
                        'maxHeight': 200,
                        
                        },
            tooltip_data=[
            {column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()} for row in df_1.to_dict('rows')
            ], 
            tooltip_duration=None
            )
        
    ])
    


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    

    decoded = base64.b64decode(content_string)
    # print(decoded.decode())
    text = text_analaysis(decoded.decode())

    step_objects = get_data(text)
 
    results_list = []
    for obj in step_objects:
        data = {}
        data['step number'] = obj.step_no
        data['displacement norm'] = obj.displacement_norm
        data['force norm'] = obj.force_norm
        data['energy norm'] = obj.energy_norm
        data['governing norm'] = obj.governing_norm
        data['converged'] = obj.converged
        data['start step'] = obj.start_step
        
        results_list.append(data)
        
    df = pd.DataFrame(results_list)
    
    div_1 = draw_graph(df, 'displacement norm', 'plot_displa')
    div_2 = draw_graph(df, 'force norm', 'plot_force')
    div_3 = draw_graph(df, 'energy norm', 'plot_energy')
    
    
    db.session.query(Data).delete()
    db.session.execute("ALTER SEQUENCE data_id_seq RESTART WITH 1")
    db.session.commit()
    
    
    project = Project.query.filter(Project.id == int(session['project_id'])).first()
    r = project.results 
    # PROJECT_DATA.results = curr_result
    
    update_results(step_objects, r)
    
    # print("Length of results is:", len(PROJECT_DATA.results.data))
    db.session.commit()

    return html.Div([
        html.H5(filename),
        div_1,
        div_2,
        div_3
    ])
    
def update_results(obj_list, results_db):
    for obj in obj_list:
        data = {}
        data['step number'] = obj.step_no
        data['displacement norm'] = obj.displacement_norm
        data['force norm'] = obj.force_norm
        data['energy norm'] = obj.energy_norm
        data['governing norm'] = obj.governing_norm
        data['converged'] = obj.converged
        data['start step'] = obj.start_step
        
        data_json = json.dumps(data)
        print(data_json)
        
        d = Data(data=data_json, result_id=results_db.id)
        db.session.add(d)
        results_db.data.append(d)
    


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

        children = [html.H3(f'You are logged in as: {current_user.username}'),
                    html.H3(f'Your current project: {project.title}')]
                    
    else:
        children = [html.H1('User non authenticated')]
                
    
    return children



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
            # print(df)
            if df.empty:
                return
            
            children = [
                draw_graph(df, 'displacement norm', 'plot_displa'),
                draw_graph(df, 'force norm', 'plot_force'),
                draw_graph(df, 'energy norm', 'plot_energy')
            ]
            return children
    
    
