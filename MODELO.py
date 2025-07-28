import pandas as pd
import joblib
from sklearn.preprocessing import OneHotEncoder
from pathlib import Path
import gdown
import os
import pickle
from copy import deepcopy


ruta_script = Path(__file__).resolve().parent

doc_test = os.path.join(ruta_script, "LAYOUTPRUEBAS.xlsx")
test = pd.read_excel(doc_test, sheet_name='Datos', engine='openpyxl')
test[['Anio', 'Semana']] = test['SEMANAGLI'].str.split('-', expand=True).astype(int)
test = test.sort_values(['SKU', 'Anio', 'Semana']).reset_index(drop=True)

def calcular_sem_num_condicional(grupo):

    grupo = grupo.sort_values(['Anio', 'Semana']).copy()
    semanac_actual = None
    contador = 0
    semana_nums = []

    for _, row in grupo.iterrows():
        clave = (row['Anio'], row['Semana'])
        if clave != semanac_actual:
            contador += 1
            semanac_actual = clave
        semana_nums.append(contador)

    grupo['SemNumero'] = semana_nums
    return grupo
    
test = test.reset_index(drop=True)

test = test.groupby('SKU', group_keys=False).apply(calcular_sem_num_condicional).reset_index(drop=True)


enc = OneHotEncoder(sparse_output=False, dtype=int, drop=None)
X_encoded = enc.fit_transform(test[['Clasificacion']])
cols = enc.get_feature_names_out(['Clasificacion'])
df_enc = pd.DataFrame(X_encoded, columns=cols, index=test.index)
df_final = pd.concat([test.drop(columns=['Clasificacion']), df_enc], axis=1)

columnas_necesarias = [
    'Clasificacion_Crema', 'Clasificacion_Cuidado cabello',
    'Clasificacion_Jabon','Clasificacion_Rastrillos',
       'Clasificacion_Tratamiento capilar'
]

for col in columnas_necesarias:
    if col not in df_final.columns:
        df_final[col] = 0
#print(df_final)

if not os.path.exists("model.pkl"):
    file_id = "15ImIkHF8yTPiADAqlWRzZM_hMoBLvX99" 
    file_id = "1AzkSITfQ32OqxsRpixOtjdXwWQaHiTHi" 
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, "model.pkl", quiet=False)

doc_model = os.path.join(ruta_script, "model.pkl")
best_model = joblib.load(doc_model) 

X = ['Clasificacion_Crema', 'Clasificacion_Cuidado cabello',
       'Clasificacion_Jabon', 'Clasificacion_Rastrillos',
       'Clasificacion_Tratamiento capilar', 'Grps', 'INVENTARIO_TOTAL',
       'PRECIO_PROMEDIO', 'SELLOUT_SP', 'SUCURSALES_TOTAL', 'SemNumero','TEMPERATURA']

df = df_final.copy()
pronosticos = []


for sku, grupo in df.groupby("SKU"):
    grupo = grupo.sort_values("SemNumero").reset_index(drop=True)

    if len(grupo) == 1:
        # Solo un registro, proyectar 4 semanas
        registro_actual = grupo.iloc[0:1].copy()
        sem_numero_base = registro_actual['SemNumero'].iloc[0]

        for i in range(12):

            if registro_actual['INVENTARIO_TOTAL'].iloc[0] <= 0:
                break  # Se detiene si el inventario es 0 o menos
            if registro_actual['SemNumero'].iloc[0] >25:
                break   
            registro_procesado = deepcopy(registro_actual)
            #registro_procesado['SemNumero'] = sem_numero_base + i + 1

            try:
                y_pred = best_model.predict(registro_procesado[X])[0]
            except Exception as e:
                print(f"Error en predicción SKU={sku}: {e}")
                y_pred = 0

            registro_procesado['Predicción Unidades Desplazadas'] = y_pred
            registro_procesado['TipoPronostico'] = 'Proyectado'
            pronosticos.append(registro_procesado)

            # Actualizar variables para la siguiente semana
            nuevo_inv = float(registro_actual['INVENTARIO_TOTAL'].iloc[0]) - y_pred
            registro_actual['INVENTARIO_TOTAL'] = max(nuevo_inv, 0)
            registro_actual['SELLOUT_SP'] = y_pred
            registro_actual['SemNumero'] += 1

    else:
        # Predicción normal para todos menos el último
        normales = grupo.iloc[:-1].copy()
        ultimos = grupo.iloc[-1:].copy()

        normales['Predicción Unidades Desplazadas'] = best_model.predict(normales[X])
        normales['TipoPronostico'] = 'Directo'
        pronosticos.append(normales)

        # Proyección desde el último registro
        registro_actual = ultimos.copy()
        sem_numero_base = registro_actual['SemNumero'].iloc[0]

        for i in range(12):

            if registro_actual['INVENTARIO_TOTAL'].iloc[0] <= 0:
                break  # Se detiene si el inventario es 0 o menos    
            if registro_actual['SemNumero'].iloc[0] >25:
                break     
            registro_procesado = deepcopy(registro_actual)
            registro_procesado['SemNumero'] = sem_numero_base + i + 1

            try:
                y_pred = best_model.predict(registro_procesado[X])[0]
            except Exception as e:
                print(f"Error en predicción SKU={sku}: {e}")
                y_pred = 0

            registro_procesado['Predicción Unidades Desplazadas'] = y_pred
            registro_procesado['TipoPronostico'] = 'Proyectado'
            pronosticos.append(registro_procesado)

            # Actualizar variables
            nuevo_inv = float(registro_actual['INVENTARIO_TOTAL'].iloc[0]) - y_pred
            registro_actual['INVENTARIO_TOTAL'] = max(nuevo_inv, 0)
            registro_actual['SELLOUT_SP'] = y_pred
            registro_actual['SemNumero'] += 1

# Combinar todo
df_pronostico_total = pd.concat(pronosticos, ignore_index=True)
#print(df_pronostico_total)
doc_final = os.path.join(ruta_script, "PRONOSTICO_PRUEBAS.xlsx")
df_pronostico_total.to_excel(doc_final, index=False)
#print(f'Resultados en {doc_final}')