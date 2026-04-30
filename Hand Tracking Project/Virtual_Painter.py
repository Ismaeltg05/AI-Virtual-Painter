import cv2
import mediapipe as mp
import numpy as np
import os
import math

# --- Configuración de MediaPipe ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8, max_num_hands=1)

# 1. Configuración de Cámara y Hardware
width, height = 1280, 720
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# 2. Cargar imágenes de la cabecera (Header)
folderPath = os.path.join(os.path.dirname(__file__), 'Header')
overlayList = []

if os.path.exists(folderPath):
    files = sorted([f for f in os.listdir(folderPath) if f.endswith(('.png', '.jpg', '.jpeg'))])
    for imPath in files:
        img = cv2.imread(os.path.join(folderPath, imPath))
        if img is not None:
            overlayList.append(img)

if not overlayList:
    header = np.zeros((125, width, 3), np.uint8)
    overlayList = [header] * 4
else:
    header = overlayList[0]

# 3. Variables de Dibujo
drawColor = (0, 0, 255)  # Color inicial: Rojo
thickness = 20
THICKNESS_MIN = 5
THICKNESS_MAX = 80
xp, yp = 0, 0
imgCanvas = np.zeros((height, width, 3), np.uint8)
tipIds = [4, 8, 12, 16, 20]

print("Iniciando... Levanta el dedo índice para pintar.")
print("  - Índice + Medio:   Seleccionar color")
print("  - Solo Índice:      Dibujar")
print("  - Índice + Meñique: Ajustar grosor (mueve pulgar hacia/lejos del índice)")
print("  - Puño cerrado:     Borrar lienzo")

while cap.isOpened():
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lmList = []
            for id, lm in enumerate(handLms.landmark):
                cx, cy = int(lm.x * width), int(lm.y * height)
                lmList.append([id, cx, cy])

            if lmList:
                x1, y1 = lmList[8][1:]   # Punta índice
                x2, y2 = lmList[12][1:]  # Punta medio

                # Detectar qué dedos están levantados
                fingers = []

                # Pulgar
                if lmList[tipIds[0]][1] < lmList[tipIds[0] - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)

                # Índice, Medio, Anular, Meñique
                for id in range(1, 5):
                    if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                # fingers: [pulgar, indice, medio, anular, menique]

                # -------------------------------------------------------
                # GESTO: PUÑO CERRADO → Borrar lienzo
                # Todos los dedos (excepto pulgar) abajo
                # -------------------------------------------------------
                if fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                    imgCanvas = np.zeros((height, width, 3), np.uint8)
                    xp, yp = 0, 0
                    # Feedback visual: flash rojo en el borde
                    cv2.rectangle(img, (0, 125), (width, height), (0, 0, 200), 6)
                    cv2.putText(img, "LIENZO BORRADO", (width // 2 - 160, height // 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

                # -------------------------------------------------------
                # GESTO: ÍNDICE + MEÑIQUE → Ajustar grosor del pincel
                # -------------------------------------------------------
                elif fingers[1] and fingers[4] and not fingers[2] and not fingers[3]:
                    xp, yp = 0, 0

                    # Distancia entre pulgar (punta) e índice (punta)
                    x_thumb, y_thumb = lmList[4][1], lmList[4][2]
                    x_idx,   y_idx   = lmList[8][1], lmList[8][2]
                    dist = math.hypot(x_idx - x_thumb, y_idx - y_thumb)

                    # Mapear distancia (20px–250px) a grosor (THICKNESS_MIN–THICKNESS_MAX)
                    thickness = int(np.interp(dist, [20, 250], [THICKNESS_MIN, THICKNESS_MAX]))

                    # Línea entre pulgar e índice como indicador
                    mid_x, mid_y = (x_thumb + x_idx) // 2, (y_thumb + y_idx) // 2
                    cv2.line(img, (x_thumb, y_thumb), (x_idx, y_idx), drawColor, 3)
                    cv2.circle(img, (mid_x, mid_y), thickness // 2, drawColor, cv2.FILLED)
                    cv2.putText(img, f"Grosor: {thickness}", (x_idx + 10, y_idx - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, drawColor, 2)

                # -------------------------------------------------------
                # GESTO: ÍNDICE + MEDIO → Selección de color
                # -------------------------------------------------------
                elif fingers[1] and fingers[2]:
                    xp, yp = 0, 0

                    if y1 < 125:
                        if 170 < x1 < 295:
                            drawColor = (0, 0, 255)
                            header = overlayList[0]
                        elif 436 < x1 < 561:
                            drawColor = (255, 0, 0)
                            header = overlayList[1]
                        elif 700 < x1 < 825:
                            drawColor = (0, 255, 0)
                            header = overlayList[2]
                        elif 980 < x1 < 1105:
                            drawColor = (0, 0, 0)
                            header = overlayList[3]

                    cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)

                # -------------------------------------------------------
                # GESTO: SOLO ÍNDICE → Dibujar
                # -------------------------------------------------------
                elif fingers[1] and not fingers[2]:
                    cv2.circle(img, (x1, y1), thickness // 2, drawColor, cv2.FILLED)

                    if xp == 0 and yp == 0:
                        xp, yp = x1, y1

                    line_thickness = 80 if drawColor == (0, 0, 0) else thickness
                    cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, line_thickness)

                    xp, yp = x1, y1

                else:
                    xp, yp = 0, 0

    # --- PROCESAMIENTO FINAL ---
    img[0:125, 0:width] = header

    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 5, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)

    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)

    # HUD: mostrar grosor actual en esquina
    cv2.putText(img, f"Grosor: {thickness}", (10, height - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

    cv2.imshow("Pintor Virtual", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()