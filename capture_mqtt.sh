#!/bin/bash
USER_DECLINED=3 #Usuario rechazó solución automatica de errores (sin solucioanrlo no se puede continuar)
DEPS_UNSATISFIED=4 #Isntalacion fallida de dependencias
MAX_SIGTERM=10
kill_timer=0
force=1

main() {
    read -p "Introduzca el tiempo de captura (En segundos)" tiempo
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
    ./plot_mqtt.py
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
    MQTTVersion=$(strings /usr/local/lib/libpaho-mqttpp3.so.1 | grep -Ei "Paho MQTT C\+\+")
    if [[ "$MQTTVersion" == *"v. 1.4."* ]]; then
        echo "Version Paho MQTT C++ correcta o compatible"
    else
        echo "Paho MQTT C++ no esta instalado o la version isntalada es incompatible"
        echo "Porfavor instale una versión compatible con C++ 1.4.0"
        exit $DEPS_UNSATISFIED
    fi
else
    echo "Este progrma necesita la instalacion de pyhton3"
    exit 1
fi