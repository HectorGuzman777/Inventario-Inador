import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

# Configuración de los pines GPIO para los servomotores
SERVO_PIN_1 = 15
SERVO_PIN_2 = 13

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN_1, GPIO.OUT)
GPIO.setup(SERVO_PIN_2, GPIO.OUT)

# Configuración de PWM para los servomotores
servo1 = GPIO.PWM(SERVO_PIN_1, 50)  # 50 Hz
servo2 = GPIO.PWM(SERVO_PIN_2, 50)  # 50 Hz

servo1.start(0)
servo2.start(0)

# Función para mover los servomotores
def mover_servos(angulo1, angulo2):
    duty1 = angulo1 / 18 + 2
    duty2 = angulo2 / 18 + 2
    GPIO.output(SERVO_PIN_1, True)
    GPIO.output(SERVO_PIN_2, True)
    servo1.ChangeDutyCycle(duty1)
    servo2.ChangeDutyCycle(duty2)
    time.sleep(1)
    GPIO.output(SERVO_PIN_1, False)
    GPIO.output(SERVO_PIN_2, False)
    servo1.ChangeDutyCycle(0)
    servo2.ChangeDutyCycle(0)
    print(f"Servos movidos a {angulo1}° y {angulo2}°")

# Función que se ejecuta cuando te conectas al broker MQTT
def on_connect(client, userdata, flags, reasonCode, properties=None):
    print(f"Conectado con código de resultado {reasonCode}")
    client.subscribe("Car/Control")

# Función que se ejecuta cuando se recibe un mensaje en un tópico suscrito
def on_message(client, userdata, msg):
    mensaje = msg.payload.decode().lower()
    print(f"Mensaje recibido en {msg.topic}: {mensaje}")
    if mensaje == "adelante":
        mover_servos(90, 90)  # Mover ambos servos hacia adelante
    elif mensaje == "atras":
        mover_servos(0, 0)  # Mover ambos servos hacia atrás
    elif mensaje == "izquierda":
        mover_servos(45, 90)  # Girar a la izquierda
    elif mensaje == "derecha":
        mover_servos(90, 45)  # Girar a la derecha

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
    servo1.stop()
    servo2.stop()
