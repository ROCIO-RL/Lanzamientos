import pandas as pd
import joblib
from sklearn.preprocessing import OneHotEncoder
from pathlib import Path
import gdown
import os
import pickle
from copy import deepcopy
import numpy as np
from scipy.optimize import curve_fit

# ---------------------------
# Rutas y carga de datos
# ---------------------------
ruta_script = Path(__file__).resolve().parent

doc_test = os.path.join(ruta_script, "LAYOUTPRUEBAS.xlsx")
test = pd.read_excel(doc_test, sheet_name='Datos', engine='openpyxl')

# Extraer Año y Semana desde 'SEMANAGLI' (formato esperado: "YYYY-WW" o similar)
test[['Anio', 'Semana']] = test['SEMANAGLI'].str.split('-', expand=True).astype(int)
test = test.sort_values(['SKU', 'Anio', 'Semana']).reset_index(drop=True)

# ---------------------------
# Funciones auxiliares
# ---------------------------
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

def ponderar_modelos(semana):
    # Pesos dinámicos según antigüedad (SemNumero)
    if semana <= 8:
        return 0.8, 0.2
    elif semana <= 16:
        return 0.6, 0.4
    elif semana <= 24:
        return 0.4, 0.6
    else:
        return 0.2, 0.8

# Gompertz reparametrizada
def gompertz_reparam(t, A, mu, lamb):
    # acepta t escalar o array
    return A * np.exp(-np.exp((mu * np.e / A) * (lamb - t) + 1))

def ajustar_gompertz(grupo):
    """
    Ajusta la curva Gompertz usando SELLOUT_SP vs SemNumero.
    Retorna params (A, mu, lambda) o None si no es posible ajustar.
    """
    # Usamos SELLOUT_SP como la serie real histórica de ventas (sellout por semana)
    if 'SELLOUT_SP' not in grupo.columns:
        return None

    y = grupo['SELLOUT_SP'].astype(float).values
    x = grupo['SemNumero'].astype(float).values

    # Requisitos mínimos para ajustar
    if len(x) < 4 or np.nansum(y) == 0:
        return None

    # Condiciones iniciales razonables
    A0 = max(y.max(), 1e-6) * 1.3
    diffs = np.diff(y)
    mu0 = np.mean(diffs) if len(diffs) > 0 else 1.0
    mu0 = max(mu0, 1e-6)
    lamb0 = float(np.mean(x)) if len(x) > 0 else 1.0

    try:
        params, _ = curve_fit(
            gompertz_reparam,
            x, y,
            p0=[A0, mu0, lamb0],
            maxfev=20000
        )
        # Validación simple: parámetros finitos y A>0
        if np.isfinite(params).all() and params[0] > 0:
            return params
        else:
            return None
    except Exception as e:
        # print(f"Warning ajustar_gompertz: no fue posible ajustar ({e})")
        return None

# ---------------------------
# Preparación de datos
# ---------------------------
test = test.reset_index(drop=True)
test = test.groupby('SKU', group_keys=False).apply(calcular_sem_num_condicional).reset_index(drop=True)

# OneHotEncoding de 'Clasificacion'
enc = OneHotEncoder(sparse_output=False, dtype=int, drop=None)
X_encoded = enc.fit_transform(test[['Clasificacion']].fillna('NA'))
cols = enc.get_feature_names_out(['Clasificacion'])
df_enc = pd.DataFrame(X_encoded, columns=cols, index=test.index)
df_final = pd.concat([test.drop(columns=['Clasificacion']), df_enc], axis=1)

# Asegurar columnas esperadas (compatibilidad con modelo)
columnas_necesarias = [
    'Clasificacion_Crema', 'Clasificacion_Cuidado cabello',
    'Clasificacion_Jabon','Clasificacion_Rastrillos',
    'Clasificacion_Tratamiento capilar'
]
for col in columnas_necesarias:
    if col not in df_final.columns:
        df_final[col] = 0

# ---------------------------
# Cargar modelo RF (fallback: descarga si no existe)
# ---------------------------
if not os.path.exists(os.path.join(ruta_script, "model.pkl")):
    # Si necesitas cambiar file_id por el real, cámbialo aquí.
    file_id = "15ImIkHF8yTPiADAqlWRzZM_hMoBLvX99" 
    file_id = "1AzkSITfQ32OqxsRpixOtjdXwWQaHiTHi"
    url = f"https://drive.google.com/uc?id={file_id}"
    try:
        gdown.download(url, os.path.join(ruta_script, "model.pkl"), quiet=False)
    except Exception as e:
        print("No se pudo descargar model.pkl automáticamente:", e)

doc_model = os.path.join(ruta_script, "model.pkl")
if os.path.exists(doc_model):
    try:
        best_model = joblib.load(doc_model)
    except Exception as e:
        print("Error cargando model.pkl:", e)
        best_model = None
else:
    print("model.pkl no encontrado. El modelo RF no estará disponible (se usará Gompertz o 0).")
    best_model = None

# ---------------------------
# Columnas usadas por el modelo RF
# ---------------------------
X = ['Clasificacion_Crema', 'Clasificacion_Cuidado cabello',
     'Clasificacion_Jabon', 'Clasificacion_Rastrillos',
     'Clasificacion_Tratamiento capilar', 'Grps', 'INVENTARIO_TOTAL',
     'PRECIO_PROMEDIO', 'SELLOUT_SP', 'SUCURSALES_TOTAL', 'SemNumero','TEMPERATURA']

# Si faltan columnas numéricas, crear con 0 para evitar errores
for col in ['Grps', 'INVENTARIO_TOTAL', 'PRECIO_PROMEDIO', 'SELLOUT_SP', 'SUCURSALES_TOTAL', 'SemNumero','TEMPERATURA']:
    if col not in df_final.columns:
        df_final[col] = 0

df = df_final.copy()

pronosticos = []

# ---------------------------
# Loop principal por SKU
# ---------------------------
for sku, grupo in df.groupby("SKU"):
    grupo = grupo.sort_values("SemNumero").reset_index(drop=True)

    # Ajustar Gompertz usando historial del SKU
    params_gompertz = ajustar_gompertz(grupo)

    # -------------- Caso: solo 1 registro histórico --------------
    if len(grupo) == 1:
        registro_actual = grupo.iloc[0:1].copy()
        sem_numero_base = int(registro_actual['SemNumero'].iloc[0])

        # Si hay historial insuficiente, params_gompertz será None y usaremos RF o fallback
        for i in range(12):
            if float(registro_actual['INVENTARIO_TOTAL'].iloc[0]) <= 0:
                break  # stop si inventario se acabó
            if registro_actual['SemNumero'].iloc[0] > 25:
                break

            registro_procesado = deepcopy(registro_actual)
            # actualizar semnumero
            registro_procesado['SemNumero'] = sem_numero_base + i + 1

            # --- Predicción RF ---
            try:
                if best_model is not None:
                    pred_rf = float(best_model.predict(registro_procesado[X])[0])
                else:
                    pred_rf = 0.0
            except Exception as e:
                # print(f"Error predict RF SKU={sku}: {e}")
                pred_rf = 0.0

            # --- Predicción Gompertz ---
            semana = int(registro_procesado['SemNumero'].iloc[0])
            if params_gompertz is not None:
                try:
                    pred_g = float(gompertz_reparam(semana, *params_gompertz))
                except:
                    pred_g = pred_rf
            else:
                pred_g = pred_rf

            # --- Mezcla dinámica ---
            pg, pr = ponderar_modelos(semana)
            y_pred = float(pg * pred_g + pr * pred_rf)

            # Guardar predicciones y metadatos
            registro_procesado['Predicción Unidades Desplazadas'] = y_pred
            registro_procesado['Pred_Gompertz'] = pred_g
            registro_procesado['Pred_RF'] = pred_rf
            registro_procesado['Peso_Gompertz'] = pg
            registro_procesado['Peso_RF'] = pr

            if params_gompertz is not None:
                registro_procesado['Gompertz_A'] = float(params_gompertz[0])
                registro_procesado['Gompertz_mu'] = float(params_gompertz[1])
                registro_procesado['Gompertz_lambda'] = float(params_gompertz[2])
            else:
                registro_procesado['Gompertz_A'] = 0.0
                registro_procesado['Gompertz_mu'] = 0.0
                registro_procesado['Gompertz_lambda'] = 0.0

            registro_procesado['TipoPronostico'] = 'Proyectado'
            pronosticos.append(registro_procesado)

            # Actualizar variables para la siguiente iteración (estado)
            nuevo_inv = float(registro_actual['INVENTARIO_TOTAL'].iloc[0]) - y_pred
            registro_actual['INVENTARIO_TOTAL'] = max(nuevo_inv, 0)
            registro_actual['SELLOUT_SP'] = y_pred
            registro_actual['SemNumero'] = registro_actual['SemNumero'] + 1

    else:
        # -------------- Caso: historial existente (>=2 registros) --------------
        normales = grupo.iloc[:-1].copy()
        #ultimos = grupo.iloc[-1:].copy().to_frame().T.reset_index(drop=True)
        ultimos = grupo.iloc[-1:].copy().reset_index(drop=True)


        # Para las filas históricas (normales) calculamos predicciones RF y Gompertz (si aplica)
        # Pred RF vectorizado (si model disponible)
        try:
            if best_model is not None:
                preds_rf_normales = best_model.predict(normales[X])
            else:
                preds_rf_normales = np.zeros(len(normales))
        except Exception as e:
            # print("Error predict RF en normales:", e)
            preds_rf_normales = np.zeros(len(normales))

        # Pred Gompertz para normales
        if params_gompertz is not None:
            semanas_normales = normales['SemNumero'].astype(float).values
            try:
                preds_g_normales = gompertz_reparam(semanas_normales, *params_gompertz)
            except Exception as e:
                preds_g_normales = preds_rf_normales
        else:
            preds_g_normales = preds_rf_normales

        # Mezcla por fila según su SemNumero
        preds_final_normales = []
        pesos_g = []
        pesos_rf = []
        for sem, pg_row, pr_row in zip(normales['SemNumero'].astype(int).values,
                                       np.zeros(len(normales)),
                                       np.zeros(len(normales))):
            pg_row, pr_row = ponderar_modelos(int(sem))
            pesos_g.append(pg_row)
            pesos_rf.append(pr_row)

        pesos_g = np.array(pesos_g)
        pesos_rf = np.array(pesos_rf)
        preds_final_normales = pesos_g * np.array(preds_g_normales) + pesos_rf * np.array(preds_rf_normales)

        normales['Predicción Unidades Desplazadas'] = preds_final_normales
        normales['Pred_Gompertz'] = preds_g_normales
        normales['Pred_RF'] = preds_rf_normales
        normales['Peso_Gompertz'] = pesos_g
        normales['Peso_RF'] = pesos_rf
        if params_gompertz is not None:
            normales['Gompertz_A'] = float(params_gompertz[0])
            normales['Gompertz_mu'] = float(params_gompertz[1])
            normales['Gompertz_lambda'] = float(params_gompertz[2])
        else:
            normales['Gompertz_A'] = 0.0
            normales['Gompertz_mu'] = 0.0
            normales['Gompertz_lambda'] = 0.0

        normales['TipoPronostico'] = 'Directo'
        pronosticos.append(normales)

        # Proyección desde el último registro
        registro_actual = ultimos.copy()
        sem_numero_base = int(registro_actual['SemNumero'].iloc[0])

        for i in range(12):
            if float(registro_actual['INVENTARIO_TOTAL'].iloc[0]) <= 0:
                break
            if registro_actual['SemNumero'].iloc[0] > 25:
                break

            registro_procesado = deepcopy(registro_actual)
            registro_procesado['SemNumero'] = sem_numero_base + i + 1
            semana = int(registro_procesado['SemNumero'].iloc[0])

            # --- Predicción RF ---
            try:
                if best_model is not None:
                    pred_rf = float(best_model.predict(registro_procesado[X])[0])
                else:
                    pred_rf = 0.0
            except Exception as e:
                # print(f"Error predict RF SKU={sku}: {e}")
                pred_rf = 0.0

            # --- Predicción Gompertz ---
            if params_gompertz is not None:
                try:
                    pred_g = float(gompertz_reparam(semana, *params_gompertz))
                except:
                    pred_g = pred_rf
            else:
                pred_g = pred_rf

            # --- Mezcla dinámica ---
            pg, pr = ponderar_modelos(semana)
            y_pred = float(pg * pred_g + pr * pred_rf)

            # Guardar predicciones y metadatos
            registro_procesado['Predicción Unidades Desplazadas'] = y_pred
            registro_procesado['Pred_Gompertz'] = pred_g
            registro_procesado['Pred_RF'] = pred_rf
            registro_procesado['Peso_Gompertz'] = pg
            registro_procesado['Peso_RF'] = pr

            if params_gompertz is not None:
                registro_procesado['Gompertz_A'] = float(params_gompertz[0])
                registro_procesado['Gompertz_mu'] = float(params_gompertz[1])
                registro_procesado['Gompertz_lambda'] = float(params_gompertz[2])
            else:
                registro_procesado['Gompertz_A'] = 0.0
                registro_procesado['Gompertz_mu'] = 0.0
                registro_procesado['Gompertz_lambda'] = 0.0

            registro_procesado['TipoPronostico'] = 'Proyectado'
            pronosticos.append(registro_procesado)

            # Actualizar estado para la siguiente iteración
            nuevo_inv = float(registro_actual['INVENTARIO_TOTAL'].iloc[0]) - y_pred
            registro_actual['INVENTARIO_TOTAL'] = max(nuevo_inv, 0)
            registro_actual['SELLOUT_SP'] = y_pred
            registro_actual['SemNumero'] = registro_actual['SemNumero'] + 1

# ---------------------------
# Exportar resultados
# ---------------------------
if len(pronosticos) == 0:
    df_pronostico_total = pd.DataFrame()
else:
    # Algunos elementos de pronosticos pueden ser DataFrames (filas). Concatenar en un df final.
    df_pronostico_total = pd.concat(pronosticos, ignore_index=True, sort=False)

# Asegurar nombres de columnas esperadas por Streamlit
# Renombrar la columna creada para consistencia con tu código previo si hace falta
# (tu código previo esperaba 'Predicción Unidades Desplazadas' exactamente)
doc_final = os.path.join(ruta_script, "PRONOSTICO_PRUEBAS.xlsx")
df_pronostico_total.to_excel(doc_final, index=False)

#print(f'Resultados guardados en {doc_final}')
