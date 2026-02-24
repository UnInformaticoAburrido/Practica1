# importamos las librerias necesarias
#nos permite trabajar con el sistema opeartivo
import os
#nos permite convertir el texto en formato JSON
import json
#nos permite crear graficos y guardarlos como imagenes
import matplotlib.pyplot as plt

#nombre del archivo del script Bash
LOG_FILE = "mqtt_capture.log"

#carpeta para guardar las imagenes 
LOG_FILE = "mqtt_capture.log"

#lee el archivo log y devuelve todas las lineas
def leer_log(nombre_archivo):
    if not os.path.exists(nombre_archivo):
        print("El archivo log no existe")
        return []
    with open(nombre_archivo,"r") as f:
        return f.readlines()

#Extrae los JSON de las lineas y devuelve una lista de diccionarios
def extraer_payloads(lineas):
    
    lista_payloads = []

    for linea in lineas:
        if "Payload:" in linea:
            try:
                # Separamos la parte JSON
                parte_json = linea.split("Payload:")[1].strip()
                
                # Convertimos el texto JSON en diccionario
                datos = json.loads(parte_json)

                # Anadimos el diccionario a la lista
                lista_payloads.append(datos)

            except json.JSONDecodeError:
                # Si hay error en el JSON, ignoramos la linea
                continue

    return lista_payloads
#Funcion para organizar los datos por sensor por ejemplo GM102B": [41.0, 45.0]
def organizar_datos(lista_payloads):

    datos_organizados = {}  # Diccionario vacio

    # Recorremos cada diccionario JSON
    for payload in lista_payloads:

        # Recorremos cada clave y valor
        for clave, valor in payload.items():

            # Solo trabajamos con valores numéricos
            if isinstance(valor, (int, float)):
                if clave not in datos_organizados:
                    datos_organizados[clave] = []

                # Anadimos el valor a la lista
                datos_organizados[clave].append(valor)

    return datos_organizados

#Funcion para generar graficos PNG
def generar_graficos(datos):

    # Creamos la carpeta si no existe
    if not os.path.exists(PLOTS_DIR):
        os.makedirs(PLOTS_DIR)

    # Recorremos cada sensor
    for clave, valores in datos.items():

        # Si no hay valores, continuamos
        if len(valores) == 0:
            continue

        # Creamos el grafico
        plt.figure()
        plt.plot(valores)

        # Titulo y nombres de ejes
        plt.title(f"{clave} a lo largo del tiempo")
        plt.xlabel("Medicion")
        plt.ylabel("Valor")

        # Guardamos el grafico
        ruta = os.path.join(PLOTS_DIR, f"{clave}.png")
        plt.savefig(ruta)

        # Cerramos el grafico
        plt.close()

        print(f"Grafico guardado en: {ruta}")


    
