import streamlit as st
import pandas as pd
import scipy.stats as stats

# Configuración para pantalla completa
st.set_page_config(layout="wide")

st.title("Pruebas de Independencia")
st.divider()

# Función para realizar las operaciones
def multiplicador_constante(constante, semilla, iteraciones):
    # Lista para almacenar los resultados
    resultados = []
    
    for i in range(iteraciones):
        # Calcula el producto de la semilla
        producto = semilla * constante
        longitud = len(str(producto))
        
        # Asegurándonos de que producto tenga 0 a la izquierda si es necesario
        if longitud <= 8:
            producto = f"{producto:08}"
        elif longitud <= 16:
            producto = f"{producto:016}"
        elif longitud <= 32:
            producto = f"{producto:032}"
        
        # Tomando los 4 dígitos de en medio según la longitud
        if longitud <= 8:
            medio = producto[2:6]
        elif longitud <= 16:
            medio = producto[6:10]
        elif longitud <= 32:
            medio = producto[14:18]
        
        # Convirtiendo a int()
        medio = int(medio)
        
        # Obteniendo ri
        ri = medio / 10000
        
        # Guardamos los resultados en una lista
        resultados.append({
            'Semilla 1': semilla,
            'Constante': constante,
            'Producto': producto,
            'Longitud': longitud,
            'Medio': medio,
            'ri': ri
        })
                
        # La nueva semilla será el valor de 'medio' calculado en esta iteración
        semilla = medio
        
    return resultados

# Lógica para navegar entre páginas
if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"  # Página inicial por defecto
    
# Página inicial
if st.session_state.pagina == "inicio":

    # Crear columnas para organizar el diseño (entrada en la izquierda y resultados en la derecha)
    col1, espacio, col2 = st.columns([2, 0.5, 3])

    with col1:
        st.header("1. Ingresa los datos")
        semilla_input = st.number_input("Ingresa tu semilla (número de dígitos pares y mayor a 0):", min_value = 0)
        constante_input = st.number_input("Ingresa tu constante (número de dígitos pares y mayor a 0):", min_value = 0)
        iteraciones_input = st.number_input("Ingresa las iteraciones:", min_value = 0, max_value = 30, step = 1)
    

    # Si ambos inputs están llenos, hacer las validaciones y mostrar los resultados
    if semilla_input and constante_input and iteraciones_input:
        try:
            semilla = int(semilla_input)  # Convertir la semilla a entero
            constante = int(constante_input)  # Convertir la semilla a entero
            iteraciones = int(iteraciones_input)  # Convertir las iteraciones a entero

            # Validación de las condiciones de entrada
            if semilla > 0 and len(str(semilla)) % 2 == 0 and constante > 0 and len(str(constante)) % 2 == 0 and iteraciones > 0:
                # Obtener los resultados de las operaciones
                resultados = multiplicador_constante(constante, semilla, iteraciones) 
                
                # Guardar los resultados en session_state para usarlos en otra página
                st.session_state.datos = resultados
                            
                # Mostrar la tabla en la columna derecha
                with col2:
                    st.header("Tabla Generada con Multiplicador Constante")
                                    
                    # Convertir la lista de diccionarios en un DataFrame
                    df = pd.DataFrame(resultados)
                    
                    df.index = df.index + 1
                    df = df.rename_axis("Iteración")
                    st.dataframe(df, use_container_width = True)     
                    
                with col1:
                    st.header("2. Escoge el tipo de corrida")
                    st.divider()
                    
                    tipo_corrida = st.selectbox(
                        "Selecciona una opción:",
                        ["Selecciona una opción", "Corrida Abajo y Arriba", "Corrida Abajo y Arriba de la Media"],
                        index=0
                    )
                    
                    if tipo_corrida != "Selecciona una opción":
                        st.session_state.tipo_corrida = tipo_corrida
                        st.session_state.pagina = "Resolver"
                        st.rerun()           

            else:
                st.error("Recuerda que la semilla debe tener un número de dígitos pares y mayor a 0, y las iteraciones deben ser mayores a 0.")
        except ValueError:
            st.error("Por favor, ingresa valores numéricos válidos para la semilla y las iteraciones.")
            
# Página de resolución
elif st.session_state.pagina == "Resolver":
    
    if "tipo_corrida" in st.session_state:
        if st.session_state.tipo_corrida == "Corrida Abajo y Arriba":
            st.subheader("Corrida Abajo y Arriba")
            
            # Crear columnas para organizar el diseño (entrada en la izquierda y resultados en la derecha)
            col1, espacio, col2 = st.columns([2, 0.2, 3])
            
            if "resultados" in st.session_state:  # Verifica que los datos existan
                resultados = st.session_state.resultados

            if "datos" in st.session_state:  # Verifica que los datos existan
                datos = st.session_state["datos"]
                
                with col1:
                    # Crear un DataFrame solo con la columna 'ri'
                    df_ri = pd.DataFrame(datos)[['ri']]
                    
                    # Mostrar la tabla con solo la columna 'ri'
                    st.subheader("Números Pseudoaleatorios")
                    df_ri.index = df_ri.index + 1
                    df = df_ri.rename_axis("Iteraciones")
                    st.dataframe(df, use_container_width = True)
                    
                with col2: 
                    # A partir de aquí va la lógica de AA        
                    st.subheader("Tabla de Validaciones")

                    # Lista para almacenar resultados
                    resultados = []

                    # Comparar valores consecutivos y almacenar 'S'
                    for i in range(len(df_ri) - 1):
                        if  df_ri.iloc[i + 1]['ri'] > df_ri.iloc[i]['ri']:
                            s = 1  # Subida
                        else:
                            s = 0  # Bajada

                        resultados.append({'S': s})

                    # Convertir la lista en un DataFrame
                    df_resultados = pd.DataFrame(resultados)

                    # Lista para almacenar las corridas
                    corridas = []

                    # Comparar valores consecutivos en la columna 'S'
                    for i in range(len(df_resultados) - 1):
                        if df_resultados.iloc[i]['S'] == df_resultados.iloc[i + 1]['S']:
                            corridas.append(0)  # No hay cambio
                        else:
                            corridas.append(1)  # Hay cambio

                    # Agregar un último valor (puedes ajustar esto según lo que necesites)
                    corridas.append(0)  # Última fila no tiene siguiente, por defecto 0

                    # Agregar la columna de corridas al DataFrame
                    df_resultados['Corridas'] = corridas
                    
                    total_corridas = sum(corridas) + 1
                        
                    # Crear una lista para 'C0' con el total solo en la primera celda y el resto vacías
                    c0_column = [total_corridas] + [""] * (len(df_resultados) - 1)

                    # Agregar la columna al DataFrame
                    df_resultados['C0'] = c0_column
                    
                    df_resultados.index += 1
                    df_resultados = df_resultados.rename_axis("Iteraciones")

                    # Mostrar la tabla en Streamlit
                    st.dataframe(df_resultados, use_container_width=True)
                
                # Aca la tabla de resultados
                st.subheader("Tabla de Abajo y Arriba")
                            
                # Intervalo de confianza
                intervalo_de_cf = st.number_input("Ingresa el intervalo de confianza: ", min_value = 0, max_value = 100, step = 1)
                
                if intervalo_de_cf:
                    # Resultado de la tabla
                    resultados_tabla = []
                
                    # Total de números pseudoaleatorios
                    n = len(df_ri)
                    
                    # Alpha
                    alpha = (100 - intervalo_de_cf) / 100
                    
                    # Valor esperado
                    val_esp = ((2 * n) - 1) / 3
                    
                    # Varianza
                    varianza = ((16 * n)-29) / 90
                    
                    # C0
                    c0 = int(df_resultados.at[1, 'C0'])
                    
                    # Estadístico
                    estadistico = abs((c0 - val_esp) / (varianza ** 0.5 ))
                    
                    # Agregando datos a lista
                    resultados_tabla.append({
                        'n': n,
                        'Alfa': alpha,
                        'Valor Esperado': val_esp,
                        'Varianza': varianza,
                        'Estadístico': estadistico,
                    })
                    
                    # Convertir los resultados en un DataFrame para mostrar
                    df_resultados_tabla = pd.DataFrame(resultados_tabla)
                    st.dataframe(df_resultados_tabla, use_container_width = True, hide_index = True)
                    
                    # Z
                    z = stats.norm.ppf(1 - (alpha / 2))

                    # Estadístico de chi cuadrada
                    st.write(f"El valor estadístico encontrado en la tabla Z fue {z}")
                    
                    # Mostrar el valor crítico para referencia
                    st.write(f"Valor estadístico generado: {estadistico}")

                    # Ahora compara el valor calculado (chi_cuadrada) con el valor crítico
                    if estadistico < z:
                        st.success("Se acepta la hipótesis nula")
                    else:
                        st.error("Hipótesis nula rechazada")
            
        elif st.session_state.tipo_corrida == "Corrida Abajo y Arriba de la Media":
            st.subheader("Corrida Abajo y Arriba de la Media")
            
            # Crear columnas para organizar el diseño (entrada en la izquierda y resultados en la derecha)
            col1, espacio, col2 = st.columns([2, 0.2, 3])
            
            if "resultados" in st.session_state:  # Verifica que los datos existan
                resultados = st.session_state.resultados

            if "datos" in st.session_state:  # Verifica que los datos existan
                datos = st.session_state["datos"]
                
                with col1:
                    # Crear un DataFrame solo con la columna 'ri'
                    df_ri = pd.DataFrame(datos)[['ri']]
                    
                    # Mostrar la tabla con solo la columna 'ri'
                    st.subheader("Números Pseudoaleatorios")
                    df_ri.index = df_ri.index + 1
                    df = df_ri.rename_axis("Iteraciones")
                    st.dataframe(df, use_container_width = True)
                    
            # A partir de aquí va la lógica de AAM
            
            with col2:
                st.subheader("Tabla de Validaciones")

                # Lista para almacenar resultados
                resultados = []
                
                # Promedio
                promedio = df_ri['ri'].mean()

                # Comparar valores consecutivos y almacenar 'S'
                for i in range(len(df_ri)):
                    if df_ri.iloc[i]['ri'] > promedio:
                        s = 1  # Subida
                    else:
                        s = 0  # Bajada

                    resultados.append({'S': s})
                    
                # Convertir la lista en un DataFrame
                df_resultados_media = pd.DataFrame(resultados)
                    
                # Lista para almacenar las corridas
                corridas = []

                # Comparar valores consecutivos en la columna 'S'
                for i in range(len(df_resultados_media) - 1):
                    if df_resultados_media.iloc[i]['S'] == df_resultados_media.iloc[i + 1]['S']:
                        corridas.append(0)  # No hay cambio
                    else:
                        corridas.append(1)  # Hay cambio

                # Agregar un último valor (puedes ajustar esto según lo que necesites)
                corridas.append(0)  # Última fila no tiene siguiente, por defecto 0

                # Agregar la columna de corridas al DataFrame
                df_resultados_media['Corridas'] = corridas
                
                total_corridas = sum(corridas) + 1
                        
                # Crear una lista para 'C0' con el total solo en la primera celda y el resto vacías
                columna_c0 = [total_corridas] + [""] * (len(df_resultados_media) - 1)

                # Agregar la columna al DataFrame
                df_resultados_media['C0'] = columna_c0
                
                # Crear una lista para 'C0' con el total solo en la primera celda y el resto vacías
                column_prom = [promedio] + [""] * (len(df_resultados_media) - 1)
                
                # Agregar la columna al DataFrame
                df_resultados_media['Media'] = column_prom
                
                df_resultados_media.index += 1
                df_resultados_media = df_resultados_media.rename_axis("Iteraciones")
                
                # Dataframe
                st.dataframe(df_resultados_media, use_container_width = True)
            
            # Aca la tabla de resultados
            st.subheader("Tabla de Abajo y Arriba de la Media")
                        
            # Intervalo de confianza
            intervalo_de_cf = st.number_input("Ingresa el intervalo de confianza: ", min_value = 0, max_value = 100, step = 1)
            
            # Variables para corridas
            n1 = 0
            n0 = 0
            
            if intervalo_de_cf:
                
                # Resultado de la tabla
                resultados_tabla_media = []
                
                # Total de números pseudoaleatorios
                n = len(df_ri)
                
                # Alpha
                alpha = (100 - intervalo_de_cf) / 100
                
                for resultado in df_resultados_media['S']:
                    if resultado == 1:
                        n1 += 1
                    else:
                        n0 += 1
                
                # Media        
                media_c0 = ((2 * n0 * n1) / n) + 0.5
                
                # Varianza
                varianza_c0 = ((2 * n0 * n1) * (2 * n0 * n1 - n) / ((n ** 2) * (n - 1)))
                
                # Desv. Estándar
                desv_est = varianza_c0 ** 0.5
                
                # Total corridas
                total_corridas = sum(corridas) + 1 # Esto es como si fuera C0
                
                # Estadístico
                estadistico = abs((total_corridas - media_c0) / desv_est)
                
                # Agregando datos a lista
                resultados_tabla_media.append({
                    'n0': n0,
                    'n1': n1,
                    'n': n,
                    'Media μc0': media_c0,
                    'Varianza': varianza_c0,
                    'Desviación Estándar': desv_est,
                    'Valor estadístico': estadistico,
                })
            
                # Convertir los resultados en un DataFrame para mostrar
                df_resultados_tabla = pd.DataFrame(resultados_tabla_media)
                st.dataframe(df_resultados_tabla, use_container_width = True, hide_index = True)   
                
                # Z
                z = stats.norm.ppf(1 - (alpha / 2))

                # Estadístico de chi cuadrada
                st.write(f"El valor estadístico encontrado en la tabla Z fue {z}")
                
                # Mostrar el valor crítico para referencia
                st.write(f"Valor estadístico generado: {estadistico}")

                # Ahora compara el valor calculado (chi_cuadrada) con el valor crítico
                if estadistico < z:
                    st.success("Se acepta la hipótesis nula")
                else:
                    st.error("Hipótesis nula rechazada")

        else:
            st.error("Error. Verifica datos")
            