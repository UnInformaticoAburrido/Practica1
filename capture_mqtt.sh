#!/bin/bash
USER_DECLINED=3 #Usuario rechazó solución automatica de errores (sin solucioanrlo no se puede continuar)
DEPS_UNSATISFIED=4 #Isntalacion fallida de dependencias
MAX_SIGTERM=10
kill_timer=0
force=1
EXPECTED_PAHO_CPP_VERSION="1.3.2"
EXPECTED_PAHO_CPP_SERIES="1.3."
main(){
    read -p "Introduzca el tiempo de captura (En segundos): " tiempo
    echo "[1/4] Ejecutando mqtt_subscribe_emqx_linux y guardando salida en mqtt_capture.log"
    ./mqtt_subscribe_emqx_linux > ./mqtt_capture.log &
    PID=$!
    echo "[info] PID=$PID"
    sleep $tiempo
    echo "[2/4] Finaliznado proceso (pid=$PID)"
    kill $PID
    while kill -0 "$PID" >/dev/null 2>&1; do
        if [[ $kill_timer -ge $MAX_SIGTERM && $force == 1 ]]; then
            echo "[warn] Ejecutnado segundo metodo de finalizacion"
            kill -2 "$PID"
            force=0
            kill_timer=0
        elif [[ $kill_timer -ge $MAX_SIGTERM && $force == 0 ]]; then
            echo "[error] Elimiando proceso se pueden producir erores..."
            kill -9 "$PID"
        fi
        sleep 1
        ((kill_timer++))
    done
    python3 - << 'PY'
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
PY
}


#(>/dev/null 2>&1) manda toda salida a null (no muestra salida ni errores)
if command -v python3 >/dev/null 2>&1; then ## command -v comprueba si python3 está disponible (y cómo lo resolvería bash)
    if python3 -c "import matplotlib" >/dev/null 2>&1; then
        echo "Dependencia python3 comprovada"
    else
        echo "Matplotlib no está instalada es necesaria para una correcta instalacion"
        read -r -p "Quieres instalar la libreria? [s/N]" respuesta
        if [[ $respuesta == [Ss] ]]; then ## [[ - ]] permite patrones y [Ss] acepta 'S' o 's'
            if python3 -m pip install --user matplotlib; then
                echo "matplotlib intalado correctamente"
            else
                echo "No se a podido ejecutar python3 -m pip install matplotlib"
                echo "Porfavor comprueva si pip esta isntalado"
                
                [ -r /etc/os-release ] && . /etc/os-release #Se comprueva que . /etc/os-release existe.

                if [[ "$ID" == "arch" ]]; then
                    echo "Ejecute: "
                    echo "sudo pacman -S python-pip"
                elif [[ "$ID" == "debian" || "$ID_LIKE" == *debian* ]]; then
                    echo "Ejecute: "
                    echo -e "sudo apt update\n sudo apt install python3-pip"
                elif [[ "$ID" == "ubuntu" ]]; then
                    echo "Ejecute: "
                    echo -e "sudo apt update\n sudo apt install python3-pip"
                else
                    echo "Inastale pip antes de volver a iniciar el programa"
                fi
                exit $DEPS_UNSATISFIED
            fi
        else
            exit $USER_DECLINED
        fi
    fi
    MQTTLibPath=$(ldconfig -p 2>/dev/null | awk '/libpaho-mqttpp3\.so/{print $4; exit}')
    if [[ -z "$MQTTLibPath" ]]; then
        MQTTLibPath=$(ls /usr/local/lib/libpaho-mqttpp3.so* /usr/local/lib64/libpaho-mqttpp3.so* 2>/dev/null | head -n1)
    fi

    if [[ -z "$MQTTLibPath" ]]; then
        echo "Paho MQTT C++ no esta instalado (no se encontro libpaho-mqttpp3)"
        exit $DEPS_UNSATISFIED
    fi

    MQTTVersion=$(strings "$MQTTLibPath" | grep -Eio "v\. [0-9]+\.[0-9]+\.[0-9]+" | head -n1)
    if [[ "$MQTTVersion" == *"v. ${EXPECTED_PAHO_CPP_VERSION}"* ]]; then
        echo "Version Paho MQTT C++ exacta detectada: ${EXPECTED_PAHO_CPP_VERSION}"
    elif [[ "$MQTTVersion" == *"v. ${EXPECTED_PAHO_CPP_SERIES}"* ]]; then
        echo "Version Paho MQTT C++ compatible detectada (${MQTTVersion}). Continuando..."
    else
        if [[ -n "$MQTTVersion" ]]; then
            echo "[warn] Version Paho MQTT C++ no esperada (${MQTTVersion}), pero se intentara continuar"
        else
            echo "[warn] No se pudo leer version de Paho MQTT C++ en ${MQTTLibPath}, pero la libreria existe. Continuando..."
        fi
    fi
else
    echo "Este progrma necesita la instalacion de pyhton3"
    exit 1
fi
main
