import cv2
import mediapipe as mp
import numpy as np
import os

# --- Configuración de MediaPipe ---
mp_hands = mp.solutions.hands
# Mantenemos una confianza alta para evitar trazos accidentales
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8, max_num_hands=1)

# 1. Configuración de Cámara y Hardware
width, height = 1280, 720
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# 2. Cargar imágenes de la cabecera (Header)
# Se busca la carpeta Header en el mismo directorio que el script
folderPath = os.path.join(os.path.dirname(__file__), 'Header')
overlayList = []

if os.path.exists(folderPath):
    # Ordenamos los archivos para que coincidan con la lógica de selección
    files = sorted([f for f in os.listdir(folderPath) if f.endswith(('.png', '.jpg', '.jpeg'))])
    for imPath in files:
        img = cv2.imread(os.path.join(folderPath, imPath))
        if img is not None:
            overlayList.append(img)

# Fallback: Si no hay imágenes, creamos una cabecera vacía para evitar errores
if not overlayList:
    header = np.zeros((125, width, 3), np.uint8)
    overlayList = [header] * 4
else:
    header = overlayList[0]

# 3. Variables de Dibujo
drawColor = (0, 0, 255) # Color inicial: Rojo
thickness = 20
xp, yp = 0, 0 # Coordenadas previas (last position)
imgCanvas = np.zeros((height, width, 3), np.uint8) # Lienzo persistente
tipIds = [4, 8, 12, 16, 20] # Índices de las puntas de los dedos en MediaPipe

print("Iniciando... Levanta el dedo índice para pintar.")

while cap.isOpened():
    success, img = cap.read()
    if not success:
        break

    # Espejo y conversión de color para MediaPipe
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            # Extraer lista de puntos (Landmarks)
            lmList = []
            for id, lm in enumerate(handLms.landmark):
                cx, cy = int(lm.x * width), int(lm.y * height)
                lmList.append([id, cx, cy])

            if lmList:
                # Coordenadas de los dedos principales
                x1, y1 = lmList[8][1:]  # Índice
                x2, y2 = lmList[12][1:] # Medio

                # Detectar qué dedos están levantados
                fingers = []
                
                # Pulgar (Lógica para mano derecha con flip)
                if lmList[tipIds[0]][1] < lmList[tipIds[0] - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)

                # Otros 4 dedos (Comparar punta con articulación inferior)
                for id in range(1, 5):
                    if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                # --- LÓGICA DE GESTOS ---

                # A. MODO SELECCIÓN: Índice y Medio arriba
                if fingers[1] and fingers[2]:
                    xp, yp = 0, 0 # Reset para no dibujar líneas al cambiar de modo
                    
                    # Selección de colores en la cabecera
                    if y1 < 125:
                        if 170 < x1 < 295:
                            drawColor = (0, 0, 255) # Rojo
                            header = overlayList[0]
                        elif 436 < x1 < 561:
                            drawColor = (255, 0, 0) # Azul
                            header = overlayList[1]
                        elif 700 < x1 < 825:
                            drawColor = (0, 255, 0) # Verde
                            header = overlayList[2]
                        elif 980 < x1 < 1105:
                            drawColor = (0, 0, 0)   # Borrador
                            header = overlayList[3]

                    cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)

                # B. MODO DIBUJO: Solo Índice arriba
                elif fingers[1] and not fingers[2]:
                    cv2.circle(img, (x1, y1), 15, drawColor, cv2.FILLED)
                    
                    if xp == 0 and yp == 0:
                        xp, yp = x1, y1

                    # Dibujar en el lienzo negro
                    if drawColor == (0, 0, 0): # Si es borrador, trazo más grueso
                        cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, 80)
                    else:
                        cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, thickness)
                    
                    xp, yp = x1, y1
                
                else:
                    # Si no hay un gesto de dibujo válido, reseteamos el punto previo
                    xp, yp = 0, 0

    # --- PROCESAMIENTO FINAL DE IMAGEN ---
    # Fusionamos el lienzo con el video de la cámara
    img[0:125, 0:width] = header # Colocar la cabecera seleccionada

    # Crear máscara para el dibujo
    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 5, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    
    # Combinar bit a bit
    img = cv2.bitwise_and(img, imgInv) # Crea el hueco negro donde hay dibujo
    img = cv2.bitwise_or(img, imgCanvas) # Rellena ese hueco con el color del lienzo

    cv2.imshow("Pintor Virtual", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()