import cv2
import mediapipe as mp
import pygame
import sys
import random
import time
import os
 
# Inicializar Pygame
pygame.init()
screen_width, screen_height = 1200, 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Control de Bola con Gestos")
 
# Crear carpeta para guardar fotos si no existe
photos_dir = "fotos"
os.makedirs(photos_dir, exist_ok=True)
 
# Configuración de la bola
ball_color = (255, 0, 0)
ball_radius = 20
ball_start_x, ball_start_y = screen_width // 2, 50
ball_x, ball_y = ball_start_x, ball_start_y
 
# Configuración de las líneas
line_color = (0, 0, 0)
line_thickness = 15
num_lines = 5
top_offset = 150
line_spacing = (screen_height - top_offset) // (num_lines + 1)
line_gap_width = 120
 
# Generar posiciones iniciales de los huecos
lines = []
for i in range(num_lines):
    gap_position = random.randint(50, screen_width - line_gap_width - 50)
    lines.append((top_offset + line_spacing * (i + 1), gap_position))
 
# Configurar Mediapipe para detección de manos
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1,
                       min_detection_confidence=0.5, min_tracking_confidence=0.5)
 
# Variables para suavizar el movimiento
smoothing_factor = 0.2
 
# Estados del juego
state = "start"
start_time = None
final_time = 0
player_name = ""
photo_path = None
 
# Archivo de ranking
ranking_file = "ranking.txt"
 
# Función para mostrar texto en la pantalla, centrado
def display_text(text, size, color, y_offset=0):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2 + y_offset))
    screen.blit(text_surface, text_rect)
 
# Función para guardar el puntaje en el archivo de ranking
def save_score(name, time_score, photo_path):
    try:
        with open(ranking_file, "a") as file:
            file.write(f"{name},{time_score:.2f},{photo_path}\n")
    except Exception as e:
        print(f"Error al guardar el puntaje: {e}")
 
# Función para mostrar el ranking con imágenes
def display_ranking():
    screen.fill((255, 255, 255))
    display_text("Ranking", 64, (0, 0, 0), -300)
 
    try:
        with open(ranking_file, "r") as file:
            scores = []
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split(",")
                    if len(parts) == 3:  # Nombre, tiempo, ruta_imagen
                        name, score, image_path = parts
                        scores.append((name, float(score), image_path))
 
            # Ordenar por tiempo (menor tiempo es mejor)
            scores = sorted(scores, key=lambda x: x[1])[:5]
 
            y_offset = -200
            for i, (name, score, image_path) in enumerate(scores):
                # Texto del resultado
                text = f"{i + 1}. {name} - {score:.2f} segundos"
                font = pygame.font.Font(None, 48)
                text_surface = font.render(text, True, (0, 0, 0))
                text_rect = text_surface.get_rect(midleft=(350, screen_height // 2 + y_offset))
                screen.blit(text_surface, text_rect)
 
                # Imagen del jugador
                try:
                    player_image = pygame.image.load(image_path)
                    player_image = pygame.transform.scale(player_image, (80, 80))  # Redimensionar la imagen
                    image_x = text_rect.right + 40 # Más separación entre texto e imagen
                    image_y = screen_height // 2 + y_offset - 40
                    screen.blit(player_image, (image_x, image_y))
                except pygame.error:
                    print(f"No se pudo cargar la imagen: {image_path}")
 
                y_offset += 100  # Más espacio entre filas
    except FileNotFoundError:
        display_text("No hay datos de ranking todavía.", 48, (0, 0, 0), 0)
    except Exception as e:
        print(f"Error al leer el archivo de ranking: {e}")
 
# Captura y guarda la foto del jugador en modo espejo, solo cuando gana
def capture_player_photo():
    ret, frame = cap.read()
    if ret:
        # Reflejar la imagen (modo espejo)
        frame = cv2.flip(frame, 1)
       
        filename = f"winning_{int(time.time())}.png"
        filepath = os.path.join(photos_dir, filename)
        cv2.imwrite(filepath, frame)
        return filepath
    return None
 
# Bucle principal del juego
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if state == "start":
                state = "posing"
                pose_start_time = time.time()
            elif state == "lose" and event.key == pygame.K_RETURN:
                state = "start"
            elif state == "win" and event.key == pygame.K_RETURN and player_name:
                photo_path = capture_player_photo()  # Guardar la foto solo al ganar
                save_score(player_name, final_time, photo_path)
                state = "ranking"
            elif state == "ranking" and event.key == pygame.K_RETURN:
                state = "start"
            elif state == "enter_name":
                if event.key == pygame.K_RETURN:
                    state = "win"
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif len(player_name) < 10:  # Limitar la longitud del nombre
                    player_name += event.unicode
 
    if state == "posing":
        screen.fill((255, 255, 255))
        countdown = max(0, 3 - int(time.time() - pose_start_time))
        if countdown == 0:
            # No se guarda foto en este estado
            state = "playing"
            ball_x, ball_y = ball_start_x, ball_start_y
            start_time = time.time()
        else:
            display_text(f"Posa para la foto: {countdown}", 64, (0, 0, 0))
        pygame.display.flip()
        continue
 
    if state == "start":
        screen.fill((255, 255, 255))
        display_text("Presiona cualquier tecla para comenzar", 48, (0, 0, 0))
        pygame.display.flip()
        continue
    elif state == "lose":
        screen.fill((255, 255, 255))
        display_text("¡Perdiste!", 64, (255, 0, 0), -50)
        display_text("Presiona ENTER para reiniciar", 48, (0, 0, 0), 50)
        pygame.display.flip()
        continue
    elif state == "win":
        screen.fill((255, 255, 255))
        display_text(f"¡Ganaste! Tiempo: {final_time:.2f} segundos", 48, (0, 255, 0), -100)
        display_text("Presiona ENTER para ver el ranking", 48, (0, 0, 0), 50)
        pygame.display.flip()
        continue
    elif state == "ranking":
        display_ranking()
        display_text("Presiona ENTER para volver al inicio", 36, (0, 0, 0), 300)
        pygame.display.flip()
        continue
    elif state == "enter_name":
        screen.fill((255, 255, 255))
        display_text("Introduce tu nombre:", 48, (0, 0, 0), -100)
        display_text(player_name, 64, (0, 0, 255), 50)
        display_text("Presiona ENTER para continuar", 36, (0, 0, 0), 200)
        pygame.display.flip()
        continue
 
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)
 
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            wrist_x = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x
            wrist_y = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y
            target_x = int(wrist_x * screen_width)
            target_y = int(wrist_y * screen_height)
            ball_x += (target_x - ball_x) * smoothing_factor
            ball_y += (target_y - ball_y) * smoothing_factor
 
    screen.fill((255, 255, 255))
    for y, gap_x in lines:
        pygame.draw.line(screen, line_color, (0, y), (gap_x, y), line_thickness)
        pygame.draw.line(screen, line_color, (gap_x + line_gap_width, y), (screen_width, y), line_thickness)
 
        if (y - line_thickness // 2 <= ball_y + ball_radius <= y + line_thickness // 2 or
            y - line_thickness // 2 <= ball_y - ball_radius <= y + line_thickness // 2):
            if not (gap_x <= ball_x - ball_radius and ball_x + ball_radius <= gap_x + line_gap_width):
                state = "lose"
                break
 
    pygame.draw.circle(screen, ball_color, (int(ball_x), int(ball_y)), ball_radius)
    if ball_y >= screen_height:
        final_time = time.time() - start_time
        player_name = ""  # Limpia el nombre al iniciar "enter_name"
        state = "enter_name"
 
    pygame.display.flip()
 
cap.release()
hands.close()
pygame.quit()