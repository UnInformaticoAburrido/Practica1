# Importamos las librerías necesarias
import os
import json
import matplotlib.pyplot as plt


# Constantes del programa
LOG_FILE = "mqtt_capture.log"
PLOTS_DIR = "plots"


# Leer archivo log
def leer_log(nombre_archivo):

    # Verificar si el archivo existe
    if not os.path.exists(nombre_archivo):
        print("El archivo log no existe.")
        return []

    try:
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            lineas = f.readlines()

            # Verificar si el archivo esta vacaio
            if len(lineas) == 0:
                print("El archivo log está vacío.")
                return []

            return lineas

    except (OSError, UnicodeDecodeError) as e:
        print(f"Error al leer el archivo: {e}")
        return []


# Extraer JSON de las lineas
def extraer_payloads(lineas):

    lista_payloads = []

    for linea in lineas:
        if "Payload:" in linea:
            try:
                parte_json = linea.split("Payload:")[1].strip()
                datos = json.loads(parte_json)
                lista_payloads.append(datos)
            except json.JSONDecodeError:
                continue

    return lista_payloads



# Organizar datos por sensor
def organizar_datos(lista_payloads):

    datos_organizados = {}

    for payload in lista_payloads:
        for clave, valor in payload.items():

            if isinstance(valor, (int, float)):

                if clave not in datos_organizados:
                    datos_organizados[clave] = []

                datos_organizados[clave].append(valor)

    return datos_organizados



# Generar graficos PNG
def generar_graficos(datos):

    # Crear carpeta si no existe
    if not os.path.exists(PLOTS_DIR):
        os.makedirs(PLOTS_DIR)

    for clave, valores in datos.items():

        if not valores:
            continue

        plt.figure()
        plt.plot(valores)
        plt.title(f"{clave} a lo largo del tiempo")
        plt.xlabel("Medición")
        plt.ylabel("Valor")
        plt.grid(True)

        ruta = os.path.join(PLOTS_DIR, f"{clave}.png")
        plt.savefig(ruta)
        plt.close()

        print(f"Gráfico guardado en: {ruta}")



# Grafico ASCII en terminal
def grafico_ascii(datos):

    print("\nVisualización ASCII:\n")

    for clave, valores in datos.items():

        print(f"\n{clave}:")

        for valor in valores:

            barra = "*" * int(min(valor, 50))
            print(f"{valor:>6} | {barra}")



# Funcion principal
def main():

    # Leer archivo
    lineas = leer_log(LOG_FILE)

    if not lineas:
        return

    # Extraer JSON
    payloads = extraer_payloads(lineas)

    if not payloads:
        print("No se encontraron payloads válidos.")
        return

    # Organizar datos
    datos = organizar_datos(payloads)

    if not datos:
        print("No hay datos numéricos para graficar.")
        return

    # Generar graficos
    generar_graficos(datos)

    # Mostrar grafico ASCII
    grafico_ascii(datos)


# Ejecutar programa
if __name__ == "__main__":
    main()