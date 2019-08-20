from flask import Flask, render_template, request, redirect, session, flash, url_for
import flask_monitoringdashboard as dashboard
import folium
import os
import io
from folium import plugins
from folium.plugins import Search
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import requests
import base64
import plotly
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import json

app = Flask(__name__)
dashboard.bind(app)

def create_plot1(df):
    asdf = df.groupby(['anoLicitacao','modalidade']) #,'numeroLicitacao','situacaoLicitacao'])
    asdf.size().unstack().fillna(0)
    print(asdf.head().columns)
    data = [
        go.Bar(
            x=asdf.iloc[:, 1], # assign x as the dataframe column 'x'
            # y=df['modalidade'],
            # color='anoLicitacao',  
        )
    ]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def create_plot2(df):
    plot = df.groupby(['tipoObjeto','anoLicitacao']).size().unstack().fillna(0).plot(kind='barh',figsize=(10,10), width=0.75, title='Distribuição dos tipos de objeto por ano')

    data = [
        go.Bar(
            y=df['modalidade'], # assign x as the dataframe column 'x'
            # y=df.iloc[1, :],
            # color='anoLicitacao',  
        )
    ]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def getInfoParticipantes(id_vencedor):
    url = 'http://apidadosabertos.tce.rn.gov.br/api/ProcedimentosLicitatoriosApi/ParticipantesDeLicitacao/json/%d'%( int(id_vencedor) )
    return pd.read_json(url)

def getProcedimentosLicitatorios(id_unidade,data_inicio,data_fim):
    url = 'http://apidadosabertos.tce.rn.gov.br/api/ProcedimentosLicitatoriosApi/LicitacaoPublica/Json/%d/%s/%s'%(id_unidade, data_inicio, data_fim)
    return pd.read_json(url)

def build_graph1(df):
    # df.groupby(['tipoObjeto','anoLicitacao']).size().unstack().fillna(0).plot(kind='barh',figsize=(10,10), width=0.75, title='Distribuição dos tipos de objeto por ano')
    asdf = df.groupby(['anoLicitacao','modalidade']) #,'numeroLicitacao','situacaoLicitacao'])
    asdf.size().unstack().fillna(0)
    # print(asdf.size().unstack().fillna(0))
    # print(asdf.size().unstack().fillna(0).shape)
    img = io.BytesIO()
    plot = asdf.size().unstack().fillna(0).plot(kind='bar',figsize=(10,5),width=1.25)
    fig = plot.get_figure()
    fig.savefig(img, format='png', bbox_inches = "tight")
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return 'data:image/png;base64,{}'.format(graph_url)

def build_graph2(df):
    img = io.BytesIO()
    plot = df.groupby(['tipoObjeto','anoLicitacao']).size().unstack().fillna(0).plot(kind='barh',figsize=(10,10), width=0.75, title='Distribuição dos tipos de objeto por ano')
    fig = plot.get_figure()
    fig.savefig(img, format='png', bbox_inches = "tight")
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return 'data:image/png;base64,{}'.format(graph_url)

def build_graph3(df):
    img = io.BytesIO()
    plot = df.groupby(['modalidade']).size().sort_values().plot(kind='barh', title='Distribuição por tipo de licitação')
    fig = plot.get_figure()
    fig.savefig(img, format='png', bbox_inches = "tight")
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return 'data:image/png;base64,{}'.format(graph_url)

def build_graph4(df):
    img = io.BytesIO()
    plot = df.groupby(['tipoObjeto']).size().plot('barh',title='Distribuição por tipo de objeto a ser adquirido com a licitação')
    fig = plot.get_figure()
    fig.savefig(img, format='png', bbox_inches = "tight")
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return 'data:image/png;base64,{}'.format(graph_url)

def color(elev): 
    if elev in range(0,500): 
        col = 'green'
    elif elev in range(501,1999): 
        col = 'blue'
    elif elev in range(2000,3000): 
        col = 'orange'
    else: 
        col='red'
    return col

def df_to_geojson(df, properties, lat='lat', lon='lon'):
    """
    Turn a dataframe containing point data into a geojson formatted python dictionary
    
    df : the dataframe to convert to geojson
    properties : a list of columns in the dataframe to turn into geojson feature properties
    lat : the name of the column in the dataframe that contains latitude data
    lon : the name of the column in the dataframe that contains longitude data
    """
    
    # create a new python dict to contain our geojson data, using geojson format
    geojson = {'type':'FeatureCollection', 'features':[]}

    # loop through each row in the dataframe and convert each row to geojson format
    for _, row in df.iterrows():
        # create a feature template to fill in
        feature = {'type':'Feature',
                   'properties':{},
                   'geometry':{'type':'Point',
                               'coordinates':[]}}

        # fill in the coordinates
        feature['geometry']['coordinates'] = [row[lon],row[lat]]

        # for each column, get the value and add it as a new feature property
        for prop in properties:
            feature['properties'][prop] = row[prop]
        
        # add this feature (aka, converted dataframe row) to the list of features inside our dict
        geojson['features'].append(feature)
    
    return geojson


@app.route('/')
@app.route('/home')
def home():
    escolas = pd.read_csv('static/csv/escolas_estaduais.csv', sep=";") 
    escolas["lat"] = pd.to_numeric(escolas["lat"])
    escolas["lon"] = pd.to_numeric(escolas["lon"])
    escolas["cod"] = pd.to_numeric(escolas["cod"])

    empresas = pd.read_csv('static/csv/empresas_final.csv', sep=",") 
    empresas_score = pd.read_csv('static/csv/dataset_final_scores_mean.csv', sep=',') 
    useful_columns = ['cnpj', 'razao_social', 'score']
    empresas_json = df_to_geojson(empresas, properties=useful_columns)

    m = folium.Map(zoom_start=8, location=[-5.8, -36.6], tiles = 'Stamen Terrain') 

    empresasgeo = folium.GeoJson(
        empresas_json,
        name='Empresas razão social',
        tooltip=folium.GeoJsonTooltip(
            fields=['razao_social','score'],
            aliases=['cnpj',''],
            localize=True)
        
    ).add_to(m)

    razao_social_search = plugins.Search(
        layer=empresasgeo,
        geom_type='Point',
        placeholder='Busca razão social',
        collapsed=False,
        search_label='razao_social',
        weight=3
    ).add_to(m)
    
    fg1 = folium.FeatureGroup(name="Score 1")
    fg2 = folium.FeatureGroup(name="Score 2")
    fg3 = folium.FeatureGroup(name="Score 3")

    for i, r in empresas.iterrows():
        score = r['score']
        if score in range(0,2):
            fg1.add_child(folium.Marker(
            location=[r['lat'], r['lon']], # coordinates
            popup=r['razao_social'], # pop-up label 
            icon= folium.Icon(color='blue', 
                        icon_color='yellow')))
        elif score in range(2,5):
            fg2.add_child(folium.Marker(
            location=[r['lat'], r['lon']], # coordinates
            popup=r['razao_social'], # pop-up label 
            icon= folium.Icon(color='orange', 
                        icon_color='yellow')
            ))
        else:
            fg3.add_child(folium.Marker(
            location=[r['lat'], r['lon']], # coordinates
            popup=r['razao_social'], # pop-up label 
            icon= folium.Icon(color='red', 
                        icon_color='yellow')
            ))
    

    m.add_child(fg1)  
    m.add_child(fg2)
    m.add_child(fg3)

    folium.LayerControl(collapsed=False).add_to(m)

    df = getProcedimentosLicitatorios(422,'2016-01-01','2020-01-01')

    chart1 = build_graph1(df)
    chart2 = build_graph2(df)
    chart3 = build_graph3(df)
    chart4 = build_graph4(df)

    return render_template('home.html', 
            mapa=m._repr_html_(),
            chart1=chart1, 
            chart2=chart2,
            chart3=chart3,
            chart4=chart4,
        ), 200


@app.route("/mapa")
def mapa():
    escolas = pd.read_csv('static/csv/escolas_estaduais.csv', sep=";") 
    escolas["lat"] = pd.to_numeric(escolas["lat"])
    escolas["lon"] = pd.to_numeric(escolas["lon"])
    escolas["cod"] = pd.to_numeric(escolas["cod"])

    # empresas = pd.read_csv('static/csv/cnpj_dados_cadastrais_pj_merenda_rn.csv', sep="#") 
    empresas = pd.read_csv('static/csv/empresas_final.csv', sep=",") 

    # empresas = empresas[['cnpj','razao_social', 'nome_fantasia', 'data_situacao_cadastral', 'data_inicio_atividade', 
    #                  'cnae_fiscal', 'descricao_tipo_logradouro', 'logradouro', 'numero', 'bairro', 'municipio', 'cep', 'uf',
    #                 'correio_eletronico','qualificacao_responsavel', 'capital_social_empresa', 'porte_empresa', 
    #                 'opcao_pelo_simples', 'data_opcao_pelo_simples', 'data_exclusao_simples', 'opcao_pelo_mei', 
    #                 'situacao_especial', 'data_situacao_especial']]

    empresas_score = pd.read_csv('static/csv/dataset_final_scores_mean.csv', sep=',') 

    # empresas = empresas.join(empresas_score.set_index('cnpj'), on='cnpj')

    # api_key = "AIzaSyD8ZnQ-DfGulB41w7pIGUfgIqOjRlZ2D8U"

    # address = "1600 Amphitheatre Parkway, Mountain View, CA"

    # empresas['lat'] = 0.0
    # empresas['lon'] = 0.0

    # for i, row in empresas.iterrows():
    #     address = " ".join([str(row['descricao_tipo_logradouro']) + " ", 
    #                         row['logradouro']+ ", ", row['bairro']+ ", ", 
    #                         row['municipio'] + ", ", row['uf']+ ", ", 
    #                         str(row['cep']) + ', Brasil'])
    #     api_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}'.format(address, api_key))
    #     api_response_dict = api_response.json()
    #     if api_response_dict['status'] == 'OK':
    #         empresas.at[i, 'lat'] = api_response_dict['results'][0]['geometry']['location']['lat']
    #         empresas.at[i, 'lon'] = api_response_dict['results'][0]['geometry']['location']['lng']
    

    # empresas["lat"] = pd.to_numeric(empresas["lat"])
    # empresas["lon"] = pd.to_numeric(empresas["lon"])

    useful_columns = ['cnpj', 'razao_social', 'score']
    empresas_json = df_to_geojson(empresas, properties=useful_columns)

    # empresas.to_csv('static/csv/empresas_final.csv', sep=",")

    m = folium.Map(zoom_start=8, location=[-5.8, -36.6], tiles = 'Stamen Terrain') 


    empresasgeo = folium.GeoJson(
        empresas_json,
        name='Empresas razão social',
        tooltip=folium.GeoJsonTooltip(
            fields=['razao_social','score'],
            aliases=['cnpj',''],
            localize=True)
        
    ).add_to(m)

    razao_social_search = plugins.Search(
        layer=empresasgeo,
        geom_type='Point',
        placeholder='Busca razão social',
        collapsed=False,
        search_label='razao_social',
        weight=3
    ).add_to(m)
    
    fg1 = folium.FeatureGroup(name="Score 1")
    fg2 = folium.FeatureGroup(name="Score 2")
    fg3 = folium.FeatureGroup(name="Score 3")


    for i, r in empresas.iterrows():
        score = r['score']
        if score in range(0,2):
            fg1.add_child(folium.Marker(
            location=[r['lat'], r['lon']], # coordinates
            popup=r['razao_social'], # pop-up label 
            icon= folium.Icon(color='blue', 
                        icon_color='yellow')))
        elif score in range(2,5):
            fg2.add_child(folium.Marker(
            location=[r['lat'], r['lon']], # coordinates
            popup=r['razao_social'], # pop-up label 
            icon= folium.Icon(color='orange', 
                        icon_color='yellow')
            ))
        else:
            fg3.add_child(folium.Marker(
            location=[r['lat'], r['lon']], # coordinates
            popup=r['razao_social'], # pop-up label 
            icon= folium.Icon(color='red', 
                        icon_color='yellow')
            ))
    

    m.add_child(fg1)  
    m.add_child(fg2)
    m.add_child(fg3)

    folium.LayerControl(collapsed=False).add_to(m)

    return render_template('mapa.html', mapa=m._repr_html_()), 200

@app.route("/graficos")
def graficos():
    df = getProcedimentosLicitatorios(422,'2016-01-01','2020-01-01')

    chart1 = build_graph1(df)
    chart2 = build_graph2(df)
    chart3 = build_graph3(df)
    chart4 = build_graph4(df)
    return render_template('graficos.html', 
            chart1=chart1, 
            chart2=chart2,
            chart3=chart3,
            chart4=chart4
        ), 200

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

app.run(debug=True)