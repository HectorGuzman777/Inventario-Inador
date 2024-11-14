import cv2
import threading
from time import sleep
import paho.mqtt.client as mqtt


def conectar(client, userdata, flags, reasonCode, properties=None):
    print(f"Conectado con código de resultado {reasonCode}")
    client.subscribe("rasptank/qr")


def rutina(datos):
    """
    Función que permite la realización del recorrido tras escanear.

    Su parámetro es la información del QR leído.
    """
    print("Iniciando viaje con: ", datos)
    sleep(5)
    print("Listo.")


def cam():
    """
    Función que inicializa la cámara y el lector QR.

    No recibe parámetros.
    """
    vid = cv2.VideoCapture(0)
    qr = cv2.QRCodeDetector()
    qr_visto = False
    hilo_rutina = None

    client = mqtt.Client()
    client.on_connect = conectar
    client.connect(" 192.168.224.97", 1883, 60)
    client.loop_start()

    if not vid.isOpened():
        return

    while True:
        ret, frame = vid.read()
        if not ret:
            break

        if qr_visto and (hilo_rutina is None or not hilo_rutina.is_alive()):
            qr_visto = False

        if not qr_visto:
            ruta, puntos, _ = qr.detectAndDecode(frame)

            if ruta:  # Solo procesar si se detectó un QR
                qr_visto = True

                client.publish("rasptank2/qr", ruta)

                hilo_rutina = threading.Thread(target=rutina, args=(ruta,))
                hilo_rutina.start()

                # Verificar si los puntos son válidos
                if puntos is not None and len(puntos) > 0:
                    puntos = puntos[0]
                    for i in range(len(puntos)):
                        pt1 = tuple(map(int, puntos[i]))
                        pt2 = tuple(map(int, puntos[(i + 1) % len(puntos)]))
                        cv2.line(frame, pt1, pt2, (0, 255, 0), 3)

        cv2.imshow("Imagen", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    vid.release()
    cv2.destroyAllWindows()

    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    cam()
