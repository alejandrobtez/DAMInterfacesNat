import pygame
import random
import sys
import cv2
import mediapipe as mp
import os
import time

# Inicializar pygame
pygame.init()

# Configuración de pantalla
ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego con Control por Mano")

# Configuración de reloj
reloj = pygame.time.Clock()

# Fuentes
fuente = pygame.font.Font(None, 50)
fuente_pequeña = pygame.font.Font(None, 30)

# Mediapipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Captura de cámara
cap = cv2.VideoCapture(0)

# Cargar imágenes
def cargar_imagen(ruta, ancho, alto):
    """Carga y escala una imagen."""
    imagen = pygame.image.load(ruta)
    return pygame.transform.scale(imagen, (ancho, alto))

try:
    fondo = cargar_imagen("fondo.jpg", ANCHO, ALTO)
    jugador_img = cargar_imagen("bola.png", 120, 120)
    obstaculo_img = cargar_imagen("obstaculo.png", 80, 80)
except pygame.error as e:
    print(f"Error al cargar las imágenes: {e}")
    pygame.quit()
    sys.exit()

# Variables del juego
velocidad_obstaculos = 5
puntuacion = 0
obstaculos = []
intervalo_obstaculos = 1000
jugador_pos = [ANCHO // 2, ALTO // 2]

# Dificultad
dificultad_actual = ""

# Carpeta para las imágenes de los jugadores
CARPETA_IMAGENES = "imagenes_jugadores"
if not os.path.exists(CARPETA_IMAGENES):
    os.makedirs(CARPETA_IMAGENES)

# Función para mostrar texto
def mostrar_texto(texto, fuente, color, x, y):
    """Muestra texto en la pantalla."""
    superficie = fuente.render(texto, True, color)
    rect = superficie.get_rect(center=(x, y))
    pantalla.blit(superficie, rect)

# Función para la pantalla inicial
def pantalla_inicial():
    """Pantalla para seleccionar el modo de juego."""
    global velocidad_obstaculos, intervalo_obstaculos, dificultad_actual
    while True:
        pantalla.blit(fondo, (0, 0))
        mostrar_texto("Selecciona el modo de juego", fuente, (255, 255, 255), ANCHO // 2, ALTO // 3)
        mostrar_texto("Fácil (F)", fuente, (0, 255, 255), ANCHO // 2, ALTO // 2)
        mostrar_texto("Medio (M)", fuente, (0, 255, 0), ANCHO // 2, (ALTO // 2) + 60)
        mostrar_texto("Difícil (D)", fuente, (255, 0, 0), ANCHO // 2, (ALTO // 2) + 120)
        mostrar_texto("Muy Difícil (V)", fuente, (255, 0, 255), ANCHO // 2, (ALTO // 2) + 180)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_f:
                    velocidad_obstaculos = 3
                    intervalo_obstaculos = 1500
                    dificultad_actual = "Fácil"
                    return
                elif evento.key == pygame.K_m:
                    velocidad_obstaculos = 5
                    intervalo_obstaculos = 1200
                    dificultad_actual = "Medio"
                    return
                elif evento.key == pygame.K_d:
                    velocidad_obstaculos = 10
                    intervalo_obstaculos = 800
                    dificultad_actual = "Difícil"
                    return
                elif evento.key == pygame.K_v:
                    velocidad_obstaculos = 15
                    intervalo_obstaculos = 600
                    dificultad_actual = "Muy Difícil"
                    return

        pygame.display.flip()
        reloj.tick(30)

# Función para detectar la mano
def detectar_mano():
    """Detecta la posición de la mano usando Mediapipe y devuelve las coordenadas."""
    ret, frame = cap.read()
    if not ret:
        return None

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = hands.process(frame_rgb)

    if resultado.multi_hand_landmarks:
        landmark = resultado.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        x = int((1 - landmark.x) * ANCHO)  # Invertir el eje X
        y = int(landmark.y * ALTO)
        return x, y

    return None

# Función para tomar una foto
def tomar_foto():
    """Toma una foto y la guarda en el disco."""
    ret, frame = cap.read()
    if ret:
        nombre_foto = f"game_over_{int(time.time())}.jpg"
        cv2.imwrite(os.path.join(CARPETA_IMAGENES, nombre_foto), frame)
        return nombre_foto  # Retorna el nombre de la foto

# Función de Game Over
def game_over():
    """Pantalla de Game Over y opciones para reiniciar o salir."""
    global puntuacion, dificultad_actual
    for i in range(3, 0, -1):
        pantalla.fill((0, 0, 0))
        mostrar_texto(f"¡GAME OVER!", fuente, (255, 0, 0), ANCHO // 2, ALTO // 4)
        mostrar_texto(f"Foto en {i} segundos...", fuente, (255, 255, 255), ANCHO // 2, ALTO // 2)
        pygame.display.flip()
        reloj.tick(1)
    
    nombre_foto = tomar_foto()  # Toma la foto y guarda el nombre

    pantalla.fill((0, 0, 0))
    mostrar_texto("¡GAME OVER!", fuente, (255, 0, 0), ANCHO // 2, ALTO // 4)
    mostrar_texto(f"Puntuación Final: {puntuacion}", fuente, (255, 255, 255), ANCHO // 2, ALTO // 2)
    mostrar_texto(f"Dificultad: {dificultad_actual}", fuente, (0, 255, 0), ANCHO // 2, (ALTO // 2) + 60)

    # Mostrar la foto tomada centrada
    foto_imagen = cargar_imagen(os.path.join(CARPETA_IMAGENES, nombre_foto), 400, 300)
    foto_rect = foto_imagen.get_rect(center=(ANCHO // 2, ALTO // 2 + 100))  # Centrar la imagen
    pantalla.blit(foto_imagen, foto_rect)

    mostrar_texto("Presiona 'R' para jugar nuevamente o 'Q' para salir", fuente_pequeña, (255, 255, 255), ANCHO // 2, (ALTO // 2) + 250)

    pygame.display.flip()

    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    reiniciar_juego()
                elif evento.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def reiniciar_juego():
    """Reinicia el juego."""
    global puntuacion
    puntuacion = 0
    obstaculos.clear()
    juego()

# Función principal del juego
def juego():
    global puntuacion
    puntuacion = 0
    tiempo_ultimo_obstaculo = pygame.time.get_ticks()

    while True:
        pantalla.fill((0, 0, 0))
        pantalla.blit(fondo, (0, 0))

        mano_pos = detectar_mano()
        if mano_pos:
            jugador_pos[0] = mano_pos[0] - 60  # Centrar el jugador en la posición de la mano
            jugador_pos[1] = mano_pos[1] - 60  # Centrar el jugador en la posición de la mano

        for obstaculo in obstaculos[:]:
            obstaculo[0] -= velocidad_obstaculos
            if obstaculo[0] < 0:
                puntuacion += 1
                obstaculos.remove(obstaculo)

            obstaculo_rect = pygame.Rect(obstaculo[0], obstaculo[1], 80, 80) 
            jugador_rect = pygame.Rect(jugador_pos [0], jugador_pos[1], 120, 120)

            if obstaculo_rect.colliderect(jugador_rect):
                game_over()
                return

            pantalla.blit(obstaculo_img, (obstaculo[0], obstaculo[1]))

        pantalla.blit(jugador_img, (jugador_pos[0], jugador_pos[1]))
        mostrar_texto(f"Puntuación: {puntuacion}", fuente, (255, 255, 255), ANCHO // 2, 50)

        if pygame.time.get_ticks() - tiempo_ultimo_obstaculo > intervalo_obstaculos:
            obstaculo_pos = [ANCHO, random.randint(0, ALTO - 80)]  # Posición aleatoria en Y
            obstaculos.append(obstaculo_pos)
            tiempo_ultimo_obstaculo = pygame.time.get_ticks()

        pygame.display.flip()
        reloj.tick(60)

# Ejecutar el juego
pantalla_inicial()
juego()