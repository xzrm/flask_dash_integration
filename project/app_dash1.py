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

from .data import *
from .models import *
import pandas as pd
import numpy as np
from .phases import *

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']



dash_app1 = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=external_stylesheets,
    url_base_pathname='/app1/'
    # requests_pathname_prefix='/chart1'
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

def draw_graph(values, title, html_id):
    fig = px.line(dict(iterations=list(range(1, len(values) + 1)),
                       variations=values),
                       x='iterations', 
                       y='variations', 
                       title=title)
    
    fig.add_trace(go.Scatter(x=[1], y=[1]))
    
    fig.update_traces(mode='lines')
    fig.update_layout(yaxis_type="log")
    
    return html.Div([
        html.Hr(), 
        dcc.Graph(
            id = html_id,
            figure = fig)
    ])
    
def draw_graph_1(df, norm, html_id):
    all_variations = np.concatenate(df[norm].values)
    
    df_loc = df
    df_loc['step length'] = df[norm].apply(lambda x: len(x))
    df_loc['cum sum'] = df['step length'].cumsum()
    df_loc['last variation'] = df[norm].apply(lambda x: x[-1])
    
    # print(df_loc)
    print("NORM", norm)
    
    fig = go.Figure()
    
    fig = px.line(dict(iterations=list(range(1, len(all_variations) + 1)),
                   variations=all_variations),
                   x='iterations', 
                   y='variations', 
                   title=norm.title())
    
    
    mask_converged_steps_this = (df_loc['converged'] == True) & df['governing norm'].apply(lambda x: norm in x.keys())

    print("mask_converged_steps_this")
    print(mask_converged_steps_this.value_counts())
    
    fig.add_trace(go.Scatter(x=df_loc['cum sum'][mask_converged_steps_this], 
                             y=df_loc['last variation'][mask_converged_steps_this],
                             mode='markers',
                             name='converged steps current norm',
                             marker=dict(
                                color='lime',
                                size=10,
                                line=dict(
                                    color='black',
                                    width=2
                                ))
                             ))
    
    mask_converged_steps_other = (df_loc['converged'] == True) & df['governing norm'].apply(lambda x: norm not in x.keys())
    
    print("mask_converged_steps_other")
    print(mask_converged_steps_other.value_counts())
    
    fig.add_trace(go.Scatter(x=df_loc['cum sum'][mask_converged_steps_other], 
                             y=df_loc['last variation'][mask_converged_steps_other],
                             mode='markers',
                             name='converged steps other norm',
                             marker=dict(
                                color='aqua',
                                size=10,
                                line=dict(
                                    color='black',
                                    width=2
                                ))
                             ))
    
    mask_unconverged_steps = (df_loc['converged'] == False)
    
    print("unconverged")
    print(mask_unconverged_steps.value_counts())
    
    fig.add_trace(go.Scatter(x=df_loc['cum sum'][mask_unconverged_steps], 
                             y=df_loc['last variation'][mask_unconverged_steps],
                             mode='markers',
                             name='unconverged steps',
                             marker=dict(
                                color='red',
                                size=10,
                                line=dict(
                                    color='black',
                                    width=2
                                ))
                             ))
    
    fig.update_layout(yaxis_type="log")
    
    return html.Div([
        html.Hr(), 
        dcc.Graph(
            id = html_id,
            figure = fig)
    ])
    


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    

    decoded = base64.b64decode(content_string)
    # print(decoded.decode())
    text = text_analaysis(decoded.decode())
    c = 0
    for l in text[0].split('\n'):
        print(l)
        c = c + 1
        if c == 10:
            break
    step_objects = get_data(text)
    # convergence_displ = Convergence(step_objects, "displacement_norm", 0.01) #exlude tolerance ? 
    # convergence_force = Convergence(step_objects, "force_norm", 0.01)
    # convergence_energy = Convergence(step_objects, "energy_norm", 0.01)
    
    # div_1 = draw_graph(convergence_displ.all_iterations, 'Convergence displacement norm', 'plot_displ')
    # div_2 = draw_graph(convergence_force.all_iterations, 'Convergence force norm', 'plot_force')
    # div_3 = draw_graph(convergence_energy.all_iterations, 'Convergence energy norm', 'plot_energy')
    results_list = []
    for obj in step_objects:
        data = {}
        data['displacement norm'] = obj.displacement_norm
        data['force norm'] = obj.force_norm
        data['energy norm'] = obj.energy_norm
        data['governing norm'] = obj.governing_norm
        data['converged'] = obj.converged
        data['start step'] = obj.start_step
        
        results_list.append(data)
        
    df = pd.DataFrame(results_list)
    
    div_1 = draw_graph_1(df, 'displacement norm', 'plot_displa')
    div_2 = draw_graph_1(df, 'force norm', 'plot_force')
    div_3 = draw_graph_1(df, 'energy norm', 'plot_energy')
    
    # fig_1 = px.line(dict(iterations=list(range(1, len(convergence_displ.all_iterations) + 1)),
    #                variations=convergence_displ.all_iterations),
    #                x='iterations', 
    #                y='variations', 
    #                title='convergence')

    # fig_1.update_traces(mode='lines')
    # fig_1.update_layout(yaxis_type="log")
    
    # fig_2 = px.line(dict(iterations=list(range(1, len(convergence_force.all_iterations) + 1)),
    #                variations=convergence_force.all_iterations),
    #                x='iterations', 
    #                y='variations', 
    #                title='convergence')

    # fig_2.update_traces(mode='lines')
    # fig_2.update_layout(yaxis_type="log")
    
    # fig_3 = px.line(dict(iterations=list(range(1, len(convergence_energy.all_iterations) + 1)),
    #                variations=convergence_energy.all_iterations),
    #                x='iterations', 
    #                y='variations', 
    #                title='convergence')

    # fig_3.update_traces(mode='lines')
    # fig_3.update_layout(yaxis_type="log")
    
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
            print(df)
            if df.empty:
                return
            
            # values_displ = np.concatenate(df['displacement norm'].values)
            # print(values_displ)
            # values_force = np.concatenate(df['force norm'].values)
            # values_energy = np.concatenate(df['energy norm'].values)
            # print(values_displ)
            children = [
                draw_graph_1(df, 'displacement norm', 'plot_displa'),
                draw_graph_1(df, 'force norm', 'plot_force'),
                draw_graph_1(df, 'energy norm', 'plot_energy')
                # draw_graph(values_displ, 'Convergence displacement norm', 'plot_displ'),
                # draw_graph(values_force, 'Convergence force norm', 'plot_force'),
                # draw_graph(values_energy, 'Convergence energy norm', 'plot_energy')
            ]
            return children
    
    
