import streamlit as st
import pandas as pd
import os
import subprocess
import altair as alt
import subprocess
import sys
import plotly.graph_objects as go
import tempfile
import numpy as np
from scipy.optimize import curve_fit

marcas_porcentajes = {
    'AFFAIR': {'Benavides': 0.00, 'Chedraui': 1.00, 'Soriana': 0.00, 'Walmart': 0.00},
    'ALERT': {'Benavides': 0.00, 'Chedraui': 0.2669, 'Soriana': 0.3410, 'Walmart': 0.3921},
    'ALLIVIAX': {'Benavides': 0.3263, 'Chedraui': 0.1338, 'Soriana': 0.1824, 'Walmart': 0.3575},
    'ASEPXIA': {'Benavides': 0.0199, 'Chedraui': 0.2063, 'Soriana': 0.1916, 'Walmart': 0.5821},
    'BENGUE': {'Benavides': 0.1438, 'Chedraui': 0.1472, 'Soriana': 0.2453, 'Walmart': 0.4638},
    'BIO': {'Benavides': 0.2257, 'Chedraui': 0.1097, 'Soriana': 0.1940, 'Walmart': 0.4707},
    'CICATRICURE': {'Benavides': 0.0363, 'Chedraui': 0.1706, 'Soriana': 0.2610, 'Walmart': 0.5321},
    'COLEDIA': {'Benavides': 0.0991, 'Chedraui': 0.0668, 'Soriana': 0.3335, 'Walmart': 0.5006},
    'COLONIA SANBORNS': {'Benavides': 0.0077, 'Chedraui': 0.1616, 'Soriana': 0.3007, 'Walmart': 0.5300},
    'CONDON M': {'Benavides': 0.2085, 'Chedraui': 0.1522, 'Soriana': 0.2759, 'Walmart': 0.3634},
    'DALAY': {'Benavides': 0.00, 'Chedraui': 0.2210, 'Soriana': 0.1980, 'Walmart': 0.5810},
    'DERMOPRADA': {'Benavides': 1.00, 'Chedraui': 0.00, 'Soriana': 0.00, 'Walmart': 0.00},
    'ENGLISH LEATHER': {'Benavides': 0.00, 'Chedraui': 0.0002, 'Soriana': 0.9998, 'Walmart': 0.00},
    'FERMODYL': {'Benavides': 0.00, 'Chedraui': 0.2236, 'Soriana': 0.2571, 'Walmart': 0.5193},
    'GARGAX': {'Benavides': 0.2855, 'Chedraui': 0.1481, 'Soriana': 0.1772, 'Walmart': 0.3892},
    'GELBECK': {'Benavides': 0.1653, 'Chedraui': 0.1612, 'Soriana': 0.1577, 'Walmart': 0.5159},
    'GENOPRAZOL': {'Benavides': 0.1375, 'Chedraui': 0.1714, 'Soriana': 0.2455, 'Walmart': 0.4456},
    'GOICOECHEA': {'Benavides': 0.0040, 'Chedraui': 0.1208, 'Soriana': 0.2004, 'Walmart': 0.6748},
    'GOICOECHEA DIABET TX': {'Benavides': 0.0233, 'Chedraui': 0.1237, 'Soriana': 0.1866, 'Walmart': 0.6663},
    'GOICOTINES': {'Benavides': 0.00, 'Chedraui': 0.00, 'Soriana': 1.00, 'Walmart': 0.00},
    'GROOMEN':  {'Benavides': 0.00, 'Chedraui': 0.1368, 'Soriana': 0.243, 'Walmart': 0.6203},
    'HENNA EGIPCIA': {'Benavides': 0.00, 'Chedraui': 0.00, 'Soriana': 1.00, 'Walmart': 0.00},
    'KAOPECTATE': {'Benavides': 0.1429, 'Chedraui': 0.1655, 'Soriana': 0.0896, 'Walmart': 0.6020},
    'LOMECAN V': {'Benavides': 0.0528, 'Chedraui': 0.1266, 'Soriana': 0.1796, 'Walmart': 0.6410},
    'LOSECA': {'Benavides': 0.1457, 'Chedraui': 0.1421, 'Soriana': 0.1804, 'Walmart': 0.5318},
    'MAEV-MEDIC': {'Benavides': 0.0221, 'Chedraui': 0.0512, 'Soriana': 0.0664, 'Walmart': 0.8603},
    'MEDICASP': {'Benavides': 0.0346, 'Chedraui': 0.1160, 'Soriana': 0.2149, 'Walmart': 0.6346},
    'NASALUB': {'Benavides': 0.2404, 'Chedraui': 0.1850, 'Soriana': 0.2670, 'Walmart': 0.3075},
    'NEXT': {'Benavides': 0.1321, 'Chedraui': 0.1384, 'Soriana': 0.1778, 'Walmart': 0.5517},
    'NIKZON': {'Benavides': 0.2648, 'Chedraui': 0.1138, 'Soriana': 0.1832, 'Walmart': 0.4382},
    'NORDIKO': {'Benavides': 0.00, 'Chedraui': 0.5248, 'Soriana': 0.4752, 'Walmart': 0.00},
    'NOVAMIL': {'Benavides': 0.9331, 'Chedraui': 0.0030, 'Soriana': 0.0325, 'Walmart': 0.0314},
    'POINTTS': {'Benavides': 0.3268, 'Chedraui': 0.1410, 'Soriana': 0.1535, 'Walmart': 0.3787},
    'POMADA DE LA CAMPANA': {'Benavides': 0.0310, 'Chedraui': 0.0888, 'Soriana': 0.2048, 'Walmart': 0.6755},
    'QG5': {'Benavides': 0.3024, 'Chedraui': 0.1173, 'Soriana': 0.1761, 'Walmart': 0.4042},
    'ROHTO': {'Benavides': 0.0075, 'Chedraui': 0.1120, 'Soriana': 0.1538, 'Walmart': 0.7267},
    'SHOT B': {'Benavides': 0.2187, 'Chedraui': 0.1813, 'Soriana': 0.1706, 'Walmart': 0.4294},
    'SILKAMEDIC': {'Benavides': 0.0567, 'Chedraui': 0.1155, 'Soriana': 0.1972, 'Walmart': 0.6306},
    'SILUET 40': {'Benavides': 0.00, 'Chedraui': 0.0940, 'Soriana': 0.1226, 'Walmart': 0.7834},
    'SISTEMA GB': {'Benavides': 0.0662, 'Chedraui': 0.1552, 'Soriana': 0.2140, 'Walmart': 0.5647},
    'SUEROX': {'Benavides': 0.0482, 'Chedraui': 0.1573, 'Soriana': 0.3051, 'Walmart': 0.4894},
    'TEATRICAL': {'Benavides': 0.0036, 'Chedraui': 0.1432, 'Soriana': 0.2137, 'Walmart': 0.6395},
    'TIO NACHO': {'Benavides': 0.0091, 'Chedraui': 0.1712, 'Soriana': 0.2223, 'Walmart': 0.5975},
    'TOUCH ME': {'Benavides': 0.0160, 'Chedraui': 0.4733, 'Soriana': 0.5103, 'Walmart': 0.0003},
    'TUKOL': {'Benavides': 0.2774, 'Chedraui': 0.1249, 'Soriana': 0.1755, 'Walmart': 0.4221},
    'UNESIA': {'Benavides': 0.0562, 'Chedraui': 0.1207, 'Soriana': 0.1893, 'Walmart': 0.6338},
    'VANART': {'Benavides': 0.00, 'Chedraui': 0.1412, 'Soriana': 0.2679, 'Walmart': 0.5909},
    'WILDROOT': {'Benavides': 0.00, 'Chedraui': 0.3798, 'Soriana': 0.4734, 'Walmart': 0.1467},
    'X RAY': {'Benavides': 0.0656, 'Chedraui': 0.2164, 'Soriana': 0.2099, 'Walmart': 0.5080},
    'XL-3': {'Benavides': 0.1829, 'Chedraui': 0.1261, 'Soriana': 0.2085, 'Walmart': 0.4825},
    'XL-3 AB': {'Benavides': 0.00, 'Chedraui': 0.00, 'Soriana': 0.3945, 'Walmart': 0.6055},
    'ZANZUSI': {'Benavides': 0.0001, 'Chedraui': 0.2316, 'Soriana': 0.5563, 'Walmart': 0.2121},
}


def obtener_porcentajes(producto):
    for marca, porcentajes in marcas_porcentajes.items():
        if marca.lower() in producto.lower():
            return porcentajes
    return None 


columnas = ['SEMANAGLI','SKU','Producto','Clasificacion','INVENTARIO_TOTAL','PRECIO_PROMEDIO','Grupo Benavides','Grupo Chedraui','Grupo Soriana','Wal-Mart de México','SUCURSALES_TOTAL','SELLOUT_SP','Grps','SELLOUT','TEMPERATURA']
st.title("MODELO LANZAMIENTOS")
st.write("La información debe ser en base a los grupos: Soriana, Benavides,Wal-Mart de México,Chedraui")
st.subheader("Cargar Excel")
archivo = st.file_uploader("Sube un archivo Excel con las columnas requeridas", type=['xlsx'])

if archivo:
    try:
        df_subido = pd.read_excel(archivo)
        if set(columnas).issubset(df_subido.columns):
            st.session_state.tabla_datos = df_subido[columnas].copy()
            st.success("Archivo cargado correctamente.")
        else:
            st.error("El archivo no contiene todas las columnas requeridas.")
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")

if st.button("Ejecutar Modelo"):
    try:
        st.session_state.tabla_datos.to_excel("LAYOUTPRUEBAS.xlsx", sheet_name='Datos',index=False)
        st.success("Archivo guardado exitosamente como LAYOUTPRUEBAS.xlsx")
    except Exception as e:
        st.error(f"Error al guardar archivo: {e}")

    if not os.path.exists("LAYOUTPRUEBAS.xlsx"):
        st.error("No se encuentra el archivo LAYOUTPRUEBAS.xlsx. Guárdalo primero.")
    else:
        try:
            result = subprocess.run([sys.executable, 'MODELO.py'], check=True, capture_output=True, text=True)
            st.success("Modelo ejecutado correctamente.")
            st.text(result.stdout)
        except subprocess.CalledProcessError as e:
            st.error(f"Ocurrió un error: {e.stderr}")

st.subheader("Gráfico")

if 'graficar' not in st.session_state:
    st.session_state.graficar = False

if st.button("Graficar"):
    st.session_state.graficar = True

if st.session_state.graficar:


    if os.path.exists("PRONOSTICO_PRUEBAS.xlsx"):
        df_resultado = pd.read_excel("PRONOSTICO_PRUEBAS.xlsx")

        required_cols = ['SemNumero', 'Producto', 'INVENTARIO_TOTAL', 'PRECIO_PROMEDIO','Grupo Benavides','Grupo Chedraui','Grupo Soriana','Wal-Mart de México','SUCURSALES_TOTAL','SELLOUT', 'Predicción Unidades Desplazadas','Grps']
        if set(required_cols).issubset(df_resultado.columns):

            productos = df_resultado['Producto'].unique()
            prod_sel = st.selectbox("Selecciona un Producto:", productos)

            df_filtro = df_resultado[df_resultado['Producto'] == prod_sel].copy()
            df_filtro.sort_values(by='SemNumero', inplace=True)

            df_plot = df_filtro[['SemNumero', 'Producto',  'INVENTARIO_TOTAL','PRECIO_PROMEDIO',	'Grupo Benavides','Grupo Chedraui','Grupo Soriana','Wal-Mart de México','SUCURSALES_TOTAL','SELLOUT', 'Predicción Unidades Desplazadas','Grps']].copy()
            df_plot = df_plot.rename(columns={'Predicción Unidades Desplazadas': 'PREDICCION',
                                  'INVENTARIO_TOTAL':'Inventario',
                                  'PRECIO_PROMEDIO': 'Precio',
                                  'SUCURSALES_TOTAL': 'Sucursales',
                                  'Grupo Benavides':'Sucursales Benavides',
                                  'Grupo Chedraui':'Sucursales Chedraui',
                                  'Grupo Soriana':'Sucursales Soriana',
                                  'Wal-Mart de México':'Sucursales Walmart'
                                  })
            df_plot['Monto'] = df_plot['PREDICCION'] * df_plot['Precio']
            porcentajes = obtener_porcentajes(prod_sel)

            if porcentajes is not None:
                for grupo, porcentaje in porcentajes.items():
                    df_plot[f'PREDICCION {grupo}'] = df_plot['PREDICCION'] * porcentaje
            

                #df_melt = df_plot.melt(id_vars='SemNumero', var_name='Tipo', value_name='Unidades')
                #df_melt = df_plot.melt(id_vars=['SemNumero', 'Precio', 'Sucursales Benavides','Sucursales Chedraui','Sucursales Soriana','Sucursales Wal-Mart', 'Monto'],
                #           var_name='Tipo', value_name='Unidades')
                # Aplica los porcentajes de cada grupo a la predicción
                porcentajes = obtener_porcentajes(prod_sel)

                df_plot['Pred_Benavides'] = df_plot['PREDICCION'] * porcentajes['Benavides']
                df_plot['Pred_Chedraui'] = df_plot['PREDICCION'] * porcentajes['Chedraui']
                df_plot['Pred_Soriana'] = df_plot['PREDICCION'] * porcentajes['Soriana']
                df_plot['Pred_Walmart'] = df_plot['PREDICCION'] * porcentajes['Walmart']

                df_pred_stack = df_plot.melt(
                    id_vars=['SemNumero'],
                    value_vars=['Pred_Benavides', 'Pred_Chedraui', 'Pred_Soriana', 'Pred_Walmart'],
                    var_name='Grupo',
                    value_name='Unidades'
                )
                df_pred_stack['Grupo'] = df_pred_stack['Grupo'].str.replace('Pred_', '')
                df_pred_stack['Tipo'] = 'Predicción'
                for grupo in ['Benavides', 'Chedraui', 'Soriana', 'Walmart']:
                    mask = df_pred_stack['Grupo'] == grupo
                    df_pred_stack.loc[mask, 'Precio'] = df_plot['Precio'].values
                    df_pred_stack.loc[mask, 'Monto'] = df_plot['Precio'].values * df_pred_stack.loc[mask, 'Unidades']
                    df_pred_stack.loc[mask, 'Sucursales'] = df_plot[f'Sucursales {grupo}'].values
                    df_pred_stack.loc[mask,'Inventario'] = df_plot['Inventario'].values
                    df_pred_stack.loc[mask,'Grps'] = df_plot['Grps'].values

                df_sellout = df_plot[['SemNumero', 'SELLOUT']].copy()
                df_sellout = df_sellout.rename(columns={'SELLOUT': 'Unidades'})
                df_sellout['Grupo'] = 'Sellout Real'
                df_sellout['Tipo'] = 'Sellout'
                df_sellout['Precio'] = df_plot['Precio'].values
                df_sellout['Monto'] = df_plot['Precio'].values * df_sellout['Unidades']
                df_sellout['Sucursales'] = df_plot['Sucursales']
                df_sellout['Inventario'] = df_plot['Inventario'].values
                df_sellout['Grps'] = df_plot['Grps'].values

                df_melt = pd.concat([df_pred_stack, df_sellout], ignore_index=True)


                #chart = alt.Chart(df_melt).mark_bar().encode(
                #    x=alt.X('SemNumero:O', title='Semana'),
                #    xOffset='Tipo:N',
                #    y=alt.Y('Unidades:Q', title='Unidades Desplazadas'),
                #    color=alt.Color('Tipo:N',
                #                    scale=alt.Scale(domain=['PREDICCION', 'SELLOUT'],
                #                                    range=['#4f81bd', '#c0504d'])),
                #    tooltip=['Tipo','SemNumero', alt.Tooltip('Unidades:Q', format=f",.0f", title="Unidades"), 
                #             alt.Tooltip('Monto:Q', format=f"$,.2f", title="Monto"), alt.Tooltip('Precio:Q', format=f"$,.2f", title="Precio"),
                #             'Sucursales Benavides','Sucursales Chedraui','Sucursales Soriana','Sucursales Wal-Mart']
                #).properties(
                #    title=f"{prod_sel}",
                #    width=700,
                #    height=400
                #)
                chart = alt.Chart(df_melt).mark_bar().encode(
                    x=alt.X('SemNumero:O', title='Semana'),
                    xOffset='Tipo:N',
                    y=alt.Y('Unidades:Q', title='Unidades'),
                    color=alt.Color('Grupo:N', scale=alt.Scale(scheme='category10')),
                    tooltip=[
                        'Tipo', 'Grupo', 'SemNumero',
                        alt.Tooltip('Unidades:Q', format=',.0f', title='Forecast Unidades'),
                        alt.Tooltip('Monto:Q', format='$,.2f', title='Forecast Monto'),
                        alt.Tooltip('Inventario:Q', format=',.0f', title='Inventario Total'),
                        alt.Tooltip('Precio:Q', format='$,.2f', title='Precio'),
                        alt.Tooltip('Sucursales:Q', format=',.0f', title='Sucursales'),
                        alt.Tooltip('Grps:Q', format=',.0f', title='Grps')
                    ]
                ).properties(
                    title=f"Predicción vs Sellout - {prod_sel}",
                    width=700,
                    height=400
                )

                st.altair_chart(chart, use_container_width=True)
            else:
                st.warning("No se encontró una marca coincidente en el producto.")

        else:
            st.error("Faltan columnas requeridas.")
    else:
        st.error("No se encontró el archivo PRONOSTICO_PRUEBAS.xlsx")


    if os.path.exists("LAYOUTPRUEBAS.xlsx"):
        df_layout = pd.read_excel("LAYOUTPRUEBAS.xlsx")
        df_producto_layout = df_layout[df_layout['Producto'] == prod_sel].copy()

        st.subheader("Editar Información del Producto")
        df_editado = st.data_editor(df_producto_layout, num_rows="dynamic")

        if st.button("Recargar Producto y Ejecutar Modelo"):
            try:
                # Reemplaza solo las filas correspondientes al producto
                df_layout_actualizado = df_layout[df_layout['Producto'] != prod_sel].copy()
                df_layout_actualizado = pd.concat([df_layout_actualizado, df_editado], ignore_index=True)
                # Ejecutar el modelo
                df_layout_actualizado.to_excel("LAYOUTPRUEBAS.xlsx", sheet_name='Datos',index=False)
                st.success("Archivo guardado exitosamente como LAYOUTPRUEBAS.xlsx")
                result = subprocess.run([sys.executable, 'MODELO.py'], check=True, capture_output=True, text=True)
                st.success("Modelo ejecutado correctamente.")
                st.text(result.stdout)
            except Exception as e:
                st.error(f"Error al actualizar y ejecutar modelo: {e}")
    else:
        st.warning("El archivo LAYOUTPRUEBAS.xlsx no se ha generado aún.")


    if "mostrar_resumen" not in st.session_state:
      st.session_state.mostrar_resumen = False

    if st.button("Mostrar Resumen"):
        st.session_state.mostrar_resumen = True
    # Mostrar solo si el estado está activado
    if st.session_state.mostrar_resumen:
        
        resumen_df = df_plot.copy()

        promedio_real = resumen_df['SELLOUT'].mean() if resumen_df['SELLOUT'].notna().any() else 0
        promedio_pred = resumen_df['PREDICCION'].mean()
        promedio_inventario = resumen_df['Inventario'].mean()
        inventario_actual = resumen_df['Inventario'].iloc[-1]  # Última semana
        sellout_real_actual = resumen_df['SELLOUT'].iloc[-1] if resumen_df['SELLOUT'].notna().any() else 0 # Última semana
        sellout_pred_actual = resumen_df['PREDICCION'].iloc[-1]  # Última semana

        # Ventas promedio para cálculo de días de inventario
        ventas_promedio_base = promedio_real if promedio_real>0 else promedio_pred
        sem_inventario = inventario_actual / ventas_promedio_base if ventas_promedio_base > 0 else 0
        dias_inventario = sem_inventario*7
        sellout_base = sellout_real_actual if sellout_real_actual>0 else sellout_pred_actual

        grps_min = resumen_df['Grps'].min()
        grps_max = resumen_df['Grps'].max()
        grps_actual = resumen_df['Grps'].iloc[-1]  # Última semana


        st.subheader("Resumen")
        st.markdown(f"""
        - **Unidades Reales Promedio**: {promedio_real:,.0f}  
        - **Unidades Pronosticadas Promedio**: {promedio_pred:,.0f}  
        - **Inventario Restante**: {inventario_actual:,.0f}  
        - **Dias de Inventario Restantes**: {dias_inventario:,.0f} dias  
        - **Mínimo de Grps**: {grps_min:,.0f}
        - **Máximo de Grps**: {grps_max:,.0f}
        """)

        medios_bajo = grps_actual < (grps_min + grps_max)/2 if grps_actual>0 else 1

        def modelo_log(x, a, b):
                return a + b * np.log(x)
        if medios_bajo:
            st.markdown("Grps Bajos")
            st.subheader("Recomendación de Incremento de GRPs")
            
            # Tomamos el último GRPs real como base
            grps_base = grps_actual

            # Ajustamos una regresión logarítmica con los datos históricos
            if grps_actual==0:
                resumen_df['Grps']=100
                grps_base=100
            x = resumen_df['Grps'] 
            y = resumen_df['PREDICCION']

            # Simulamos incrementos de 10% a 100%
            incrementos = np.arange(0.1, 1.1, 0.1)
            grps_simulados = grps_base * (1 + incrementos)

            # Creamos un DataFrame para registrar simulaciones
            sim_df = pd.DataFrame({
                'GRPs Simulados': grps_simulados
            })

             
            try:
                params, _ = curve_fit(modelo_log, x[x > 0], y[x > 0])  # Solo usar GRPs > 0
                sim_df['Predicción Estimada'] = modelo_log(sim_df['GRPs Simulados'], *params)
                st.dataframe(sim_df.style.format({"GRPs Simulados": "{:,.1f}", "Predicción Estimada": "{:,.0f}"}))
                st.markdown("Puedes usar estos valores en el apartado de **Editar información del Producto** para probar cómo afectaría el aumento de GRPs a las unidades desplazadas ")
            except Exception as e:
                st.markdown("")




        







