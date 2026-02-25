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
PLOTS_DIR = "plots"

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

def grafico_ascii(datos):

    print("\nVisualización ASCII:\n")  # Mostramos un titulo en la terminal

    for clave, valores in datos.items():  # Recorremos cada sensor y su lista de valores

        print(f"\n{clave}:")  # Mostramos el nombre del sensor

        for valor in valores:  # Recorremos cada valor del sensor

            # craar una barra usando el simbolo "*" y con tamano maximo 50

            barra = "*" * int(min(valor, 50))

            # Mostrar el valor numérico y su representacion en forma de barra
            print(f"{valor} | {barra}")
def main():  

    #leer el archivo log
    lineas = leer_log(LOG_FILE)  

    #archivo no existe o esta vacio
    if not lineas:
        return

    #Extraer los datos JSON de las lineas
    payloads = extraer_payloads(lineas)  # Obtenemos una lista de diccionarios

    #Organizar los datos por sensor
    datos = organizar_datos(payloads)  # Convertimos la lista en diccionario organizado

    if not datos:
        print("No se encontraron datos válidos.")
        return

    #Generar los graficos PNG
    generar_graficos(datos)

    #Mostrar la visualizacion ASCII en la terminal
    grafico_ascii(datos)

if __name__ == "__main__":
    main()


    
