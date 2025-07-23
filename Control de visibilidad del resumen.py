# Control de visibilidad del resumen
    if "mostrar_resumen" not in st.session_state:
        st.session_state.mostrar_resumen = False

    if st.button("Mostrar Resumen"):
        st.session_state.mostrar_resumen = True

        resumen_df = df_plot.copy()

        promedio_real = resumen_df['SELLOUT'].mean() if resumen_df['SELLOUT'].notna().any() else 0
        promedio_pred = resumen_df['PREDICCION'].mean()
        promedio_inventario = resumen_df['Inventario'].mean()
        inventario_actual = resumen_df['Inventario'].iloc[-1]  # Última semana

        # Ventas promedio para cálculo de días de inventario
        ventas_promedio_base = promedio_real if promedio_real>0 else promedio_pred
        sem_inventario = promedio_inventario / ventas_promedio_base if ventas_promedio_base > 0 else 0

        grps_min = resumen_df['Grps'].min()
        grps_max = resumen_df['Grps'].max()
        grps_actual = resumen_df['Grps'].iloc[-1]  # Última semana

        st.subheader("Resumen")
        st.markdown(f"""
        - **Unidades Reales Promedio**: {promedio_real:.0f}  
        - **Unidades Pronosticadas Promedio**: {promedio_pred:.0f}  
        - **Inventario Promedio**: {promedio_inventario:.0f}  
        - **Semanas de Inventario Restantes**: {sem_inventario:.1f} semanas  
        """)

        # GRPs Gauge (rango visual)
        

        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = grps_actual,
            title = {'text': "Nivel de GRPs"},
            gauge = {
                'axis': {'range': [grps_min, grps_max]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [grps_min, (grps_min + grps_max)/2], 'color': "lightgray"},
                    {'range': [(grps_min + grps_max)/2, grps_max], 'color': "lightgreen"},
                ]
            }
        ))

        st.plotly_chart(fig, use_container_width=True)

        # Reglas de negocio: Alertas
        st.subheader("🔔 Recomendaciones")
        alertas = []

        if sem_inventario < 3:
            alertas.append("⚠️ **Inventario bajo**: menos de 3 semanas de cobertura.")
        if grps_actual < (grps_min + grps_max)/2:
            alertas.append("⚠️ **GRPs bajos**: podrías necesitar más inversión publicitaria.")
        if not alertas:
            alertas.append("✅ Todo está en niveles óptimos. ¡Buen trabajo!")

        for alerta in alertas:
            st.markdown(alerta)

    if "mostrar_resumen2" not in st.session_state:
      st.session_state.mostrar_resumen2 = False

    if st.button("Mostrar Resumen2"):
        st.session_state.mostrar_resumen2 = True
    # Mostrar solo si el estado está activado
    if st.session_state.mostrar_resumen2:
        st.subheader("Selecciona variable a visualizar")
        resumen_df = df_plot.copy()

        promedio_real = resumen_df['SELLOUT'].mean() if resumen_df['SELLOUT'].notna().any() else 0
        promedio_pred = resumen_df['PREDICCION'].mean()
        promedio_inventario = resumen_df['Inventario'].mean()
        inventario_actual = resumen_df['Inventario'].iloc[-1]  # Última semana

        # Ventas promedio para cálculo de días de inventario
        ventas_promedio_base = promedio_real if promedio_real>0 else promedio_pred
        sem_inventario = promedio_inventario / ventas_promedio_base if ventas_promedio_base > 0 else 0

        grps_min = resumen_df['Grps'].min()
        grps_max = resumen_df['Grps'].max()
        grps_actual = resumen_df['Grps'].iloc[-1]  # Última semana
        col1, col2, col3 = st.columns(3)

        st.subheader("🔔 Recomendaciones")
        alertas = []

        if sem_inventario < 3:
            alertas.append("⚠️ **Inventario bajo**: menos de 3 semanas de cobertura.")
        if grps_actual < (grps_min + grps_max)/2:
            alertas.append("⚠️ **GRPs bajos**: podrías necesitar más inversión publicitaria.")
        if not alertas:
            alertas.append("✅ Todo está en niveles óptimos. ¡Buen trabajo!")

        for alerta in alertas:
            st.markdown(alerta)

        if "metric_display" not in st.session_state:
            st.session_state.metric_display = "GRPs"

        with col1:
            if st.button("Ventas"):
                st.session_state.metric_display = "Ventas"

        with col2:
            if st.button("Inventario"):
                st.session_state.metric_display = "Inventario"

        with col3:
            if st.button("GRPs"):
                st.session_state.metric_display = "GRPs"

        # Asignar variable
        if st.session_state.metric_display == "Ventas":
            valor = promedio_real if promedio_real > 0 else promedio_pred
            rango_min = resumen_df[['SELLOUT', 'PREDICCION']].min().min()
            rango_max = resumen_df[['SELLOUT', 'PREDICCION']].max().max()
            titulo = "Ventas promedio"

        elif st.session_state.metric_display == "Inventario":
            valor = inventario_actual
            rango_min = resumen_df['Inventario'].min()
            rango_max = resumen_df['Inventario'].max()
            titulo = "Inventario"

        else:
            valor = resumen_df['Grps'].iloc[-1]
            rango_min = resumen_df['Grps'].min()
            rango_max = resumen_df['Grps'].max()
            titulo = "Nivel de GRPs"

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=valor,
            title={'text': titulo},
            gauge={
                'axis': {'range': [rango_min, rango_max]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [rango_min, (rango_min + rango_max)/2], 'color': "lightgray"},
                    {'range': [(rango_min + rango_max)/2, rango_max], 'color': "lightgreen"},
                ]
            }
        ))

        st.plotly_chart(fig, use_container_width=True, key=f"plotly_{st.session_state.metric_display}")


st.subheader("Recomendaciones")
        alertas = []

        if sem_inventario < 3:
            if sem_inventario==0:
                alertas.append(f"⚠️ **Inventario agotado**")
            else:
                alertas.append(f"⚠️ **Inventario bajo**: {sem_inventario:.1f} semanas de cobertura.")
        if grps_actual < (grps_min + grps_max)/2:
            alertas.append("⚠️ **GRPs por debajo del promedio**: podrías necesitar más inversión publicitaria.")
        if sellout_base < ventas_promedio_base:
            alertas.append("⚠️ **Sellout por debajo del promedio**")
        if not alertas:
            alertas.append("✅ Todo está en niveles óptimos.")

        for alerta in alertas:
            st.markdown(alerta)

        st.subheader("Selecciona variable a visualizar")
        col1, col2, col3 = st.columns(3)

        

        if "metric_display" not in st.session_state:
            st.session_state.metric_display = "GRPs"

        with col1:
            if st.button("Ventas"):
                st.session_state.metric_display = "Ventas"

        with col2:
            if st.button("Inventario"):
                st.session_state.metric_display = "Inventario"

        with col3:
            if st.button("GRPs"):
                st.session_state.metric_display = "GRPs"

        # Asignar variable
        if st.session_state.metric_display == "Ventas":
            #valor = promedio_real if promedio_real > 0 else promedio_pred
            valor = sellout_base
            rango_min = resumen_df[['SELLOUT', 'PREDICCION']].min().min()
            rango_max = resumen_df[['SELLOUT', 'PREDICCION']].max().max()
            titulo = "Ventas promedio"

        elif st.session_state.metric_display == "Inventario":
            valor = inventario_actual
            rango_min = resumen_df['Inventario'].min()
            rango_max = resumen_df['Inventario'].max()
            titulo = "Inventario"

        else:
            #valor = resumen_df['Grps'].iloc[-1]
            valor = grps_actual
            rango_min = resumen_df['Grps'].min()
            rango_max = resumen_df['Grps'].max()
            titulo = "Nivel de GRPs"

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=valor,
            title={'text': titulo},
            gauge={
                'axis': {'range': [rango_min, rango_max]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [rango_min, (rango_min + rango_max)/2], 'color': "lightgray"},
                    {'range': [(rango_min + rango_max)/2, rango_max], 'color': "lightgreen"},
                ]
            }
        ))

        st.plotly_chart(fig, use_container_width=True, key=f"plotly_{st.session_state.metric_display}")


if len(x) < 3 or grps_actual==0:
                st.warning("⚠️ Datos insuficientes para ajustar el modelo. Se usará una estimación proporcional como referencia.")

                base_grps = grps_actual if grps_actual > 0 else 1
                base_pred = sellout_pred_actual
                x = sim_df['GRPs Simulados']
                sim_df['Predicción Estimada'] = sim_df['GRPs Simulados'].apply(lambda g: base_pred * g / base_grps)
                st.dataframe(sim_df.style.format({"GRPs Simulados": "{:,.1f}", "Predicción Estimada": "{:,.0f}"}))
                st.markdown("Puedes usar estos valores en el apartado de **Editar información del Producto** para probar cómo afectaría el aumento de GRPs a las unidades desplazadas ")
            # Para regresión logarítmica: y = a + b*log(x)