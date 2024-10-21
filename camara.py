import cv2
# pip install opencv-python
import numpy as np
# pip install numpy


def callback(x):
    pass


# Inicia la captura de la webcam
cap = cv2.VideoCapture(0)

# Crea una ventana para las trackbars
cv2.namedWindow('Trackbars')
# Define un tamaño personalizado para la ventana de trackbars
cv2.resizeWindow('Trackbars', 600, 250)  # Ancho = 600 píxeles, Alto = 400 píxeles

# Crea trackbars para ajustar los valores H, S, V
cv2.createTrackbar('H Min', 'Trackbars', 0, 179, callback)
cv2.createTrackbar('H Max', 'Trackbars', 179, 179, callback)
cv2.createTrackbar('S Min', 'Trackbars', 0, 255, callback)
cv2.createTrackbar('S Max', 'Trackbars', 255, 255, callback)
cv2.createTrackbar('V Min', 'Trackbars', 0, 255, callback)
cv2.createTrackbar('V Max', 'Trackbars', 255, 255, callback)

while True:
    # Lee la imagen de la webcam
    ret, frame = cap.read()

    if not ret:
        break

    # Convierte la imagen de BGR a HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Obtiene los valores de las trackbars
    h_min = cv2.getTrackbarPos('H Min', 'Trackbars')
    s_min = cv2.getTrackbarPos('S Min', 'Trackbars')
    v_min = cv2.getTrackbarPos('V Min', 'Trackbars')
    h_max = cv2.getTrackbarPos('H Max', 'Trackbars')
    s_max = cv2.getTrackbarPos('S Max', 'Trackbars')
    v_max = cv2.getTrackbarPos('V Max', 'Trackbars')

    # Define los límites del filtro HSV
    lower_hsv = np.array([h_min, s_min, v_min])
    upper_hsv = np.array([h_max, s_max, v_max])

    # Aplica desenfoque gaussiano para reducir el ruido
    blurred = cv2.GaussianBlur(hsv, (15, 15), 0)

    # Aplica el filtro de color en la imagen desenfocada
    mask = cv2.inRange(blurred, lower_hsv, upper_hsv)

    # Erosión y dilatación para eliminar ruido en la máscara
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # Aplica la máscara a la imagen original
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # Muestra la imagen original, la imagen filtrada y la imagen filtrada sobrepuesta en la original
    cv2.imshow('Original', frame)
    cv2.imshow('Mask', mask)
    cv2.imshow('Filtrado', result)

    # Salir cuando se presiona 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera la captura y cierra las ventanas
cap.release()
cv2.destroyAllWindows()
