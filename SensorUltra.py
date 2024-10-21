import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

# Configuración de los pines GPIO para el sensor ultrasónico
TRIG_PIN = 11  # Pin de disparo
ECHO_PIN = 8   # Pin de eco

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(ECHO_PIN, GPIO.IN)

# Función para medir la distancia usando el sensor ultrasónico
def medir_distancia():
    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(0.000015)
    GPIO.output(TRIG_PIN, GPIO.LOW)
    
    while not GPIO.input(ECHO_PIN):
        pass
    t1 = time.time()
    
    while GPIO.input(ECHO_PIN):
        pass
    t2 = time.time()
    
    distancia = round((t2 - t1) * 340 / 2, 2)
    return distancia

# Función que se ejecuta cuando te conectas al broker MQTT
def on_connect(client, userdata, flags, reasonCode, properties=None):
    print(f"Conectado con código de resultado {reasonCode}")
    client.subscribe("Car/Ultrasonic")

# Función que se ejecuta cuando se recibe un mensaje en un tópico suscrito
def on_message(client, userdata, msg):
    mensaje = msg.payload.decode().lower()
    print(f"Mensaje recibido en {msg.topic}: {mensaje}")
    if mensaje == "medir":
        distancia = medir_distancia()
        client.publish("Car/Ultrasonic/Distance", f"Distancia: {distancia} cm")

# Configuración del cliente MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Conexión al broker MQTT (cambiar host y puerto si es necesario)
client.connect("10.25.83.216", 1883, 60)

# Inicio de un hilo para manejar la red y las callbacks
client.loop_start()

# Bucle principal para enviar mensajes desde la consola
try:
    while True:
        mensaje = input("Ingresa 'medir' para obtener la distancia medida por el sensor ultrasónico: ")
        client.publish("Car/Ultrasonic", mensaje)
except KeyboardInterrupt:
    print("Desconectando...")
    # Finaliza el hilo loop
    client.loop_stop()
    client.disconnect()
    GPIO.cleanup()




