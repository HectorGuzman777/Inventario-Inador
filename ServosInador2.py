import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

# Configuración de los pines GPIO para los motores DC
ENA_PIN = 12  # Enable A
IN1_PIN = 16  # Motor A IN1
IN2_PIN = 20  # Motor A IN2

ENB_PIN = 21  # Enable B
IN3_PIN = 26  # Motor B IN3
IN4_PIN = 19  # Motor B IN4

GPIO.setmode(GPIO.BCM)
GPIO.setup(ENA_PIN, GPIO.OUT)
GPIO.setup(IN1_PIN, GPIO.OUT)
GPIO.setup(IN2_PIN, GPIO.OUT)
GPIO.setup(ENB_PIN, GPIO.OUT)
GPIO.setup(IN3_PIN, GPIO.OUT)
GPIO.setup(IN4_PIN, GPIO.OUT)

# Configuración de PWM para los motores
motorA = GPIO.PWM(ENA_PIN, 50)  # 50 Hz
motorB = GPIO.PWM(ENB_PIN, 50)  # 50 Hz

motorA.start(0)
motorB.start(0)

# Función para mover los motores DC
def mover_motores(velocidadA, velocidadB, direccionA, direccionB):
    GPIO.output(IN1_PIN, direccionA == "adelante")
    GPIO.output(IN2_PIN, direccionA == "atras")
    GPIO.output(IN3_PIN, direccionB == "adelante")
    GPIO.output(IN4_PIN, direccionB == "atras")
    
    motorA.ChangeDutyCycle(velocidadA)
    motorB.ChangeDutyCycle(velocidadB)
    time.sleep(1)
    
    motorA.ChangeDutyCycle(0)
    motorB.ChangeDutyCycle(0)
    print(f"Motores movidos con velocidad {velocidadA}% y {velocidadB}% en direcciones {direccionA} y {direccionB}")

# Función que se ejecuta cuando te conectas al broker MQTT
def on_connect(client, userdata, flags, reasonCode, properties=None):
    print(f"Conectado con código de resultado {reasonCode}")
    client.subscribe("Car/Control")

# Función que se ejecuta cuando se recibe un mensaje en un tópico suscrito
def on_message(client, userdata, msg):
    mensaje = msg.payload.decode().lower()
    print(f"Mensaje recibido en {msg.topic}: {mensaje}")
    if mensaje == "adelante":
        mover_motores(100, 100, "adelante", "adelante")  # Mover ambos motores hacia adelante
    elif mensaje == "atras":
        mover_motores(100, 100, "atras", "atras")  # Mover ambos motores hacia atrás
    elif mensaje == "izquierda":
        mover_motores(50, 100, "adelante", "adelante")  # Girar a la izquierda
    elif mensaje == "derecha":
        mover_motores(100, 50, "adelante", "adelante")  # Girar a la derecha

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
        mensaje = input("Ingresa 'adelante', 'atras', 'izquierda' o 'derecha' para mover el carrito: ")
        client.publish("Car/Control", mensaje)
except KeyboardInterrupt:
    print("Desconectando...")
    # Finaliza el hilo loop
    client.loop_stop()
    client.disconnect()
    GPIO.cleanup()
    motorA.stop()
    motorB.stop()
