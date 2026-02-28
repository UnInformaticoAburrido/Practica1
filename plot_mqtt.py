import sys
import json
import matplotlib.pyplot as plt

LOG_FILE = "mqtt_capture.log"
OUTPUT_IMAGE = "Grafica.png"
PRECISION_GRAFICA=10 #Para la representacion se usa esta constante y determina la presicion y altura del grafico ya que los datos se normalizan

def read_log(LOG_FILE):
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as file:
                lines = file.readlines()
                return lines
    except FileNotFoundError:
        print("El archivo log no existe.")
        sys.exit(1)#If the program dont will do nothing is veter stop the program

def extract_payloads(lines):
    data = []
    for line in lines:
        if "Payload:" in line:
            text_after = line.split("Payload:", 1)[1].strip()
            start = text_after.find("{")
            if start != -1:
                end = text_after.find("}", start)
                if end != -1:
                    possible_json = text_after[start:end+1]
                    try:
                        jsonLine = json.loads(possible_json)
                        data.append(jsonLine)
                    except json.JSONDecodeError:
                        pass #For now we don't do nothing with not valid json lines
    return data

def generar_grafico(data):
    all_values = []
    for item in data:
        for val in item.values():
            if isinstance(val, (int, float)): #We use the funtion isinstance() to check if the value (val) is an int or an float to avoid use not numeric values
                all_values.append(val)

    plt.figure(figsize=(12, 6))
    plt.plot(all_values)
    plt.title("Todos los datos recogidos")
    plt.xlabel("Índice")
    plt.ylabel("Valor")
    plt.grid(True)
    plt.savefig(OUTPUT_IMAGE)
    plt.close()

    print(f"Gráfico guardado en: {OUTPUT_IMAGE}")

def grafico_ascii(data):
    vals = []
    for d in data:
        for v in d.values():
            if isinstance(v, (int, float)):
                vals.append(v)

    if not vals: #Toda lista vacia en pyhton 3 se considra false negar un valor falso da positivo por lo que este if solo saltara si no se ha guardado nada en vals
        print("No hay datos para mostrar.")
        return
    
    min_val = 0
    max_val = max(vals)
    n = len(vals)

    wide = max_val if max_val != 0 else 1

    lines = []
    for v in vals:
        valor_escalado = int((v - min_val) / wide  * (PRECISION_GRAFICA - 1))
        lines.append(valor_escalado)

    width = n + 3

    canvas = []
    for _ in range(PRECISION_GRAFICA+1):
        row = []
        for _ in range(width+3):
            row.append(" ")
        canvas.append(row)

    for x, f in enumerate(lines):
        y = PRECISION_GRAFICA - f
        canvas[y][x+3] = "*"

    for y in range(PRECISION_GRAFICA+1):
        canvas[y][3] = "|"

    for x in range(3, width):
        canvas[PRECISION_GRAFICA][x] = "-"
    canvas[PRECISION_GRAFICA][width+1] = f"{len(vals)-3}"
    
    canvas[PRECISION_GRAFICA][0:3] = [" "," ", "0"]

    label_max = f"{max_val:.0f}"
    lbl = list(label_max.rjust(2))
    canvas[0][0:3] = lbl
    print(f"Imprimiendo grafico con {PRECISION_GRAFICA} de precision")
    for linea in canvas:
        print("".join(linea))

def main():
    lines = read_log(LOG_FILE)
    data = extract_payloads(lines)
    generar_grafico(data)
    grafico_ascii(data)


if __name__ == "__main__":
    main()