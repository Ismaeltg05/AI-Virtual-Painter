# 🖌️ AI Virtual Painter

> Proyecto final para la asignatura **Tópicos de Matemática Aplicada al Procesamiento de Imágenes (MAE353)** — UFRJ.

Implementación de un pintor virtual en tiempo real mediante seguimiento de manos con **MediaPipe** y **OpenCV**. Dibuja con el dedo índice directamente sobre la imagen de tu cámara, cambia colores, ajusta el grosor del trazo y borra con gestos naturales.

---

## 🎬 Demo

| Seleccionar color | Ajustar grosor | Borrar pantalla | Modo espera |
|:-:|:-:|:-:|:-:|
| ![Selecting](https://user-images.githubusercontent.com/74989519/121432273-d7cc7700-c950-11eb-91af-21f270f7c8a7.gif) | ![Thickness](https://user-images.githubusercontent.com/74989519/121432960-bc15a080-c951-11eb-91fc-1bdb8b5d832c.gif) | ![Cleaning](https://user-images.githubusercontent.com/74989519/121432623-4b6e8400-c951-11eb-85ec-cd0612e797b2.gif) | ![Drawing](https://user-images.githubusercontent.com/74989519/121436537-22e98880-c957-11eb-9904-55d43fe346ef.gif) |

---

## ✋ Controles por gestos

| Gesto | Acción |
|---|---|
| ☝️ Solo índice arriba | **Modo dibujo** — dibuja con el dedo índice |
| ✌️ Índice + medio arriba | **Modo selección** — elige color o borrador en la barra superior |
| 🤙 Índice + meñique arriba | **Modo espera** — levanta el lápiz para dibujar trazos separados |
| ✊ Mano cerrada | **Borrar lienzo** — limpia toda la pantalla |

---

## 🎨 Colores disponibles

- 🔴 **Rojo**
- 🔵 **Azul**
- 🟢 **Verde**
- ⬜ **Borrador**

> Los colores se seleccionan colocando los dedos índice y medio sobre la barra superior de la pantalla.

---

## ⚙️ Instalación

### Requisitos previos
- Python 3.7+
- Webcam funcional

### Dependencias

```bash
pip install opencv-python numpy
pip install mediapipe==0.10.13 protobuf==5.26.1
```

### Estructura del proyecto

```
AI-Virtual-Painter/
│
├── Virtual_Painter.py      # Script principal
├── Header/                 # Carpeta con imágenes de la barra de colores
│   ├── 1.png               # Barra con rojo seleccionado
│   ├── 2.png               # Barra con azul seleccionado
│   ├── 3.png               # Barra con verde seleccionado
│   └── 4.png               # Barra con borrador seleccionado
└── README.md
```

> **Nota:** Si la carpeta `Header/` no existe o está vacía, el programa generará una barra de colores vacía como fallback y seguirá funcionando.

---

## ▶️ Ejecución

```bash
python Virtual_Painter.py
```

Pulsa **`Q`** para salir.

---

## 🧠 Cómo funciona

El programa utiliza los 21 landmarks de la mano que detecta MediaPipe para inferir el estado de cada dedo (arriba/abajo) y determinar el gesto activo:

1. **Detección de mano** — MediaPipe identifica y rastrea los puntos clave de la mano en cada frame.
2. **Clasificación de gestos** — Se evalúa la posición relativa de las puntas de los dedos respecto a sus articulaciones.
3. **Modo de dibujo** — El trazo se genera interpolando la posición actual con la anterior (`xp, yp`) sobre un lienzo (`imgCanvas`) separado del video.
4. **Fusión de imagen** — El lienzo se combina con el frame de la cámara mediante operaciones bitwise de OpenCV, superponiendo el dibujo sobre el video en tiempo real.

---

## 🛠️ Tecnologías

- [MediaPipe](https://google.github.io/mediapipe/) — Detección y seguimiento de manos
- [OpenCV](https://opencv.org/) — Captura de video y procesamiento de imagen
- [NumPy](https://numpy.org/) — Operaciones matriciales sobre los frames

---

## 📄 Licencia

Proyecto académico — UFRJ, MAE353.