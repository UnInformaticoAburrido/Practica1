# IMPORTACION DE LIBRERIAS
import os                 # Permite trabajar con archivos y carpetas
import json               # Permite convertir texto JSON en diccionario Python
import matplotlib.pyplot as plt   # Permite crear graficos

LOG_FILE = "mqtt_capture.log"      # Archivo generado por MQTT
OUTPUT_IMAGE = "all_sensors.png"   # Imagen unica con todos los sensores

#LEER EL ARCHIVO LOG
#Lee el archivo log y devuelve todas las lineas si no existe o esta vacio devuelve lista vacia   
def leer_log(nombre_archivo):
    
    # Verificamos si el archivo existe
    if not os.path.exists(nombre_archivo):
        print("El archivo log no existe.")
        return []
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        lineas = f.readlines()

        # Verificamos si esta vacio
        if len(lineas) == 0:
            print("El archivo esta vacio.")
            return []

        return lineas


#Extraer los JSON despues de la palabra 'Payload:'y devolver una lista de diccionarios
def extraer_payloads(lineas):
    lista_payloads = []

    # Recorremos todas las lineas
    for linea in lineas:

        # Solo procesamos las lineas que contienen datos
        if "Payload:" in linea:

            try:
                # Separar la parte JSON
                parte_json = linea.split("Payload:")[1].strip()

                # Convertir texto JSON en diccionario
                datos = json.loads(parte_json)

                # Guardar el diccionario
                lista_payloads.append(datos)

            except json.JSONDecodeError:
                # Si el JSON esta mal formado, lo ignoramos
                continue

    return lista_payloads



#ORGANIZAR LOS DATOS POR SENSOR
def organizar_datos(lista_payloads):
    
    #clave = nombre del sensor
    #valor = lista de mediciones
    datos_organizados = {}

    # Recorremos cada mensaje JSON
    for payload in lista_payloads:

        # Recorremos cada sensor dentro del JSON
        for clave, valor in payload.items():

            # Solo aceptamos valores numericos
            if isinstance(valor, (int, float)):

                # Si el sensor no existe aun en el diccionario
                if clave not in datos_organizados:
                    datos_organizados[clave] = []

                # Anadimos el valor a su lista
                datos_organizados[clave].append(valor)

    return datos_organizados




#Generar un grafico PNG
def generar_grafico_unico(datos):
    # Creamos una figura grande para mejor visibilidad
    plt.figure(figsize=(12, 6))

    # Dibujamos cada sensor como una curva diferente
    for clave, valores in datos.items():
        plt.plot(valores, label=clave)

    # Titulo y etiquetas
    plt.title("Todos los sensores")
    plt.xlabel("Numero de medicion")
    plt.ylabel("Valor original")

    # Mostramos la leyenda
    plt.legend(fontsize=8)

    # Activamos cuadricula
    plt.grid(True)

    # Guardamos la imagen
    plt.savefig(OUTPUT_IMAGE)

    # Cerramos la figura
    plt.close()

    print(f"Grafico guardado en: {OUTPUT_IMAGE}")



#Generar un grafico ASCII y mostrarlo en la terminal
def grafico_ascii_global(datos):
    print("\n---GRAFICO ASCII GLOBAL---\n")

    # Recorremos cada sensor
    for clave, valores in datos.items():

        print(f"\nSensor: {clave}")

        # Recorremos cada valor del sensor
        for valor in valores:

            # Creamos una barra proporcional al valor (maximo 50)
            barra = "*" * int(min(valor, 50))

            # Mostramos el valor y la barra
            print(f"{valor:>8.2f} | {barra}")


# FUNCION PRINCIPAL
def main():
    # 1) Leer archivo
    lineas = leer_log(LOG_FILE)
    if not lineas:
        return

    # 2) Extraer JSON
    payloads = extraer_payloads(lineas)
    if not payloads:
        print("No se encontraron datos validos.")
        return

    # 3) Organizar datos
    datos = organizar_datos(payloads)
    if not datos:
        print("No hay datos numericos.")
        return

    # 4) Generar grafico PNG
    generar_grafico_unico(datos)

    # 5) Mostrar grafico ASCII
    grafico_ascii_global(datos)


if __name__ == "__main__":
    main()