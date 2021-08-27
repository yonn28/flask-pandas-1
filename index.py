from flask import Flask, jsonify
import pandas as pd
from itertools import cycle
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
base_pivot['FechaValoracionNutricional_MesAño'] = base_pivot['FechaValoracionNutricional'].dt.to_period('M')
frecuencias_mes = base_pivot[['FechaValoracionNutricional_MesAño','EstadoPesoTalla_New']].groupby(['FechaValoracionNutricional_MesAño','EstadoPesoTalla_New']).size()
porcentajes_mes = frecuencias_mes.groupby(level=0).apply(lambda x : 100 * x / float(x.sum()))
porcentajes_mes = porcentajes_mes.reset_index()
porcentajes_mes.columns = ['FechaValoracionNutricional_MesAño', 'EstadoPesoTalla_New', 'Porcentajes']




@app.route('/api/v1/x', methods=['GET'])
def ploting_get_x():
    x = porcentajes_mes['FechaValoracionNutricional_MesAño'].unique().strftime('%b')[:12]
    df_list = x.values.tolist()
    JSONP_data = jsonpify(df_list)
    return JSONP_data

@app.route('/api/v1/y', methods=['GET'])
def ploting_get_y():
    y = porcentajes_mes[porcentajes_mes['EstadoPesoTalla_New'] == 'Desnutricion']['Porcentajes']
    df_list = y.values.tolist()
    JSONP_data = jsonpify(df_list)
    return JSONP_data


if __name__ == '__main__':
    app.run(debug=True, port=3000)