import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

# Configuración de los pines GPIO para los motores DC
Motor_A_EN = 7
Motor_B_EN = 11

Motor_A_Pin1 = 8
Motor_A_Pin2 = 10
Motor_B_Pin1 = 13
Motor_B_Pin2 = 12

def motorStop():
    GPIO.output(Motor_A_Pin1, GPIO.LOW)
    GPIO.output(Motor_A_Pin2, GPIO.LOW)
    GPIO.output(Motor_B_Pin1, GPIO.LOW)
    GPIO.output(Motor_B_Pin2, GPIO.LOW)
    GPIO.output(Motor_A_EN, GPIO.LOW)
    GPIO.output(Motor_B_EN, GPIO.LOW)

def setup():
    global pwm_A, pwm_B
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(Motor_A_EN, GPIO.OUT)
    GPIO.setup(Motor_B_EN, GPIO.OUT)
    GPIO.setup(Motor_A_Pin1, GPIO.OUT)
    GPIO.setup(Motor_A_Pin2, GPIO.OUT)
    GPIO.setup(Motor_B_Pin1, GPIO.OUT)
    GPIO.setup(Motor_B_Pin2, GPIO.OUT)

    motorStop()
    pwm_A = GPIO.PWM(Motor_A_EN, 1000)
    pwm_B = GPIO.PWM(Motor_B_EN, 1000)
    pwm_A.start(0)
    pwm_B.start(0)

def motor_A(direction, speed):
    if direction == 1:
        GPIO.output(Motor_A_Pin1, GPIO.HIGH)
        GPIO.output(Motor_A_Pin2, GPIO.LOW)
    elif direction == 0:
        GPIO.output(Motor_A_Pin1, GPIO.LOW)
        GPIO.output(Motor_A_Pin2, GPIO.HIGH)
    pwm_A.ChangeDutyCycle(speed)

def motor_B(direction, speed):
    if direction == 1:
        GPIO.output(Motor_B_Pin1, GPIO.HIGH)
        GPIO.output(Motor_B_Pin2, GPIO.LOW)
    elif direction == 0:
        GPIO.output(Motor_B_Pin1, GPIO.LOW)
        GPIO.output(Motor_B_Pin2, GPIO.HIGH)
    pwm_B.ChangeDutyCycle(speed)

def on_connect(client, userdata, flags, reasonCode, properties=None):
    print(f"Conectado con código de resultado {reasonCode}")
    client.subscribe("Car/Control")

def on_message(client, userdata, msg):
    mensaje = msg.payload.decode().lower()
    print(f"Mensaje recibido en {msg.topic}: {mensaje}")
    if mensaje == "adelante":
        motor_A(1, 100)
        motor_B(0, 100)
    elif mensaje == "atras":
        motor_A(0, 100)
        motor_B(1, 100)
    elif mensaje == "izquierda":
        motor_A(0, 100)
        motor_B(0, 100)
    elif mensaje == "derecha":
        motor_A(1, 100)
        motor_B(1, 100)
    time.sleep(3)
    motorStop()

# Configuración del cliente MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Conexión al broker MQTT (cambiar host y puerto si es necesario)
client.connect("10.25.83.216", 1883, 60)

# Inicio de un hilo para manejar la red y las callbacks
client.loop_start()

setup()

# Bucle principal para mantener el script en ejecución
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Desconectando...")
    client.loop_stop()
    client.disconnect()
    GPIO.cleanup()
    pwm_A.stop()
    pwm_B.stop()
