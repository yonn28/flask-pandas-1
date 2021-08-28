from flask import Flask, jsonify
import pandas as pd
from itertools import cycle
from flask_cors import CORS
from flask_sslify import SSLify
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

base_pivot = pd.read_csv('https://storage.googleapis.com/ds4all-test-bd1/tomas_pivot.csv')
base_pivot = base_pivot.drop(columns = ['Unnamed: 0'])

def nombres(x):
    if x == 'Desnutricion Aguda Moderada' or x == 'Desnutricion aguda severa':
        x = 'Desnutricion'
    else:
        x
    return x

base_pivot['EstadoPesoTalla_New'] = base_pivot['EstadoPesoTalla'].apply(nombres)
base_pivot['FechaValoracionNutricional'] = pd.to_datetime(base_pivot['FechaValoracionNutricional'])
base_pivot['FechaValoracionNutricional_MesAno'] = base_pivot['FechaValoracionNutricional'].dt.to_period('M')
frecuencias_mes = base_pivot[['FechaValoracionNutricional_MesAno','EstadoPesoTalla_New']].groupby(['FechaValoracionNutricional_MesAno','EstadoPesoTalla_New']).size()
porcentajes_mes = frecuencias_mes.groupby(level=0).apply(lambda x : 100 * x / float(x.sum()))
porcentajes_mes = porcentajes_mes.reset_index()
porcentajes_mes.columns = ['FechaValoracionNutricional_MesAno', 'EstadoPesoTalla_New', 'Porcentajes']




@app.route('/api/v1/x', methods=['GET'])
def ploting_get_x():
    x = porcentajes_mes['FechaValoracionNutricional_MesAno'].unique().strftime('%b')[:12]
    df_list = x.tolist()
    JSONP_data = jsonify(df_list)
    return JSONP_data

@app.route('/api/v1/y', methods=['GET'])
def ploting_get_y():
    y = porcentajes_mes[porcentajes_mes['EstadoPesoTalla_New'] == 'Desnutricion']['Porcentajes']
    df_list = y.tolist()
    JSONP_data = jsonify(df_list)
    return JSONP_data

@app.route('/api/v1/df', methods=['GET'])
def getting_dataframe():
    porcentajes_mes['FechaValoracionNutricional_MesAno']=porcentajes_mes['FechaValoracionNutricional_MesAno'].astype(str)
    return jsonify(porcentajes_mes.to_dict("records"))


if __name__ == '__main__':
    app.run(debug=True, port=8080, host="0.0.0.0")# change host to 0.0.0.0 and port 8080