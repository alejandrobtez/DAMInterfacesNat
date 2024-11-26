import pygame
import random
import sys
import cv2
import mediapipe as mp
import time

# Inicializar Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Inicialización de Pygame
pygame.init()

# Configuración de la ventana
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juego de esquivar obstáculos")
clock = pygame.time.Clock()

# Cargar la imagen de fondo
try:
    background_image = pygame.image.load("fondo.jpg")
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
except pygame.error as e:
    print(f"Error cargando la imagen de fondo: {e}")
    sys.exit()

# Cargar la imagen de la bola
try:
    ball_image = pygame.image.load("bola.png")
    ball_image = pygame.transform.scale(ball_image, (60, 60))
    ball_rect = ball_image.get_rect()
    ball_x, ball_y = WIDTH // 2, HEIGHT - 50
except pygame.error as e:
    print(f"Error cargando la imagen de la bola: {e}")
    sys.exit()

# Configuración de obstáculos circulares
obstacle_radius = 40
obstacle_speed_y = 5
obstacle_spawn_rate = 50
obstacles = []

# Lista de resultados
player_results = []

# Capturar nombre y foto
def get_player_data():
    global player_name, player_photo
    player_name = ""
    entering_name = True
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: No se pudo acceder a la cámara.")
        sys.exit()

    while entering_name:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Presiona Enter para capturar la foto
                    ret, frame = cap.read()
                    if ret:
                        player_photo = frame  # Guardar la foto sin rotación adicional
                        entering_name = False
                elif event.key == pygame.K_BACKSPACE:  # Borrar último carácter
                    player_name = player_name[:-1]
                else:
                    player_name += event.unicode  # Añadir carácter

        screen.fill((50, 50, 50))
        font = pygame.font.Font(None, 36)
        text_surface = font.render("Escribe tu nombre y presiona Enter:", True, (255, 255, 255))
        name_surface = font.render(player_name, True, (255, 255, 255))
        screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(name_surface, (WIDTH // 2 - name_surface.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()
        clock.tick(30)

    cap.release()


# Función para generar nuevos obstáculos
def create_obstacle():
    obstacle_x = random.randint(obstacle_radius, WIDTH - obstacle_radius)
    obstacles.append([obstacle_x, 0])  # Añadir obstáculo en la parte superior

# Función para reiniciar el juego
def reset_game():
    global obstacles, ball_x, ball_y, game_over, start_time, elapsed_time
    get_player_data()  # Pedir nuevamente los datos del jugador
    obstacles = []
    ball_x, ball_y = WIDTH // 2, HEIGHT - 50
    game_over = False
    start_time = time.time()
    elapsed_time = 0

# Configuración inicial
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: No se pudo acceder a la cámara.")
    sys.exit()

game_over = False
player_name = ""
player_photo = None
start_time = 0
elapsed_time = 0

# Obtener datos del jugador
get_player_data()
reset_game()

# Bucle principal del juego
while True:
    # Manejar eventos de Pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            cap.release()
            cv2.destroyAllWindows()
            sys.exit()
        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # Reiniciar el juego
                reset_game()
            if event.key == pygame.K_q:  # Salir del juego
                pygame.quit()
                cap.release()
                cv2.destroyAllWindows()
                sys.exit()

    if not game_over:
        # Leer fotograma de la cámara
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo leer el fotograma de la cámara.")
            break

        # Voltear y procesar la imagen
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # Detectar posición de la mano
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Extraer la posición de la punta del dedo índice
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                ball_x = int(index_finger_tip.x * WIDTH)

                # Dibujar la mano en la ventana de la cámara (opcional)
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Generar nuevos obstáculos
        if random.randint(1, obstacle_spawn_rate) == 1:
            create_obstacle()

        # Mover obstáculos
        for obstacle in obstacles[:]:
            obstacle[1] += obstacle_speed_y  # Mover hacia abajo

            # Verificar colisiones
            dx = ball_x - obstacle[0]
            dy = ball_y - obstacle[1]
            distance = (dx**2 + dy**2) ** 0.5
            if distance < obstacle_radius + ball_rect.width // 2:
                elapsed_time = round(time.time() - start_time, 2)
                player_results.append((player_name, elapsed_time, player_photo))
                game_over = True

            # Eliminar obstáculos fuera de pantalla
            if obstacle[1] > HEIGHT:
                obstacles.remove(obstacle)

        # Dibujar todo
        screen.blit(background_image, (0, 0))  # Fondo
        for obstacle in obstacles:
            pygame.draw.circle(screen, (255, 0, 0), (obstacle[0], obstacle[1]), obstacle_radius)  # Obstáculos
        screen.blit(ball_image, (ball_x - ball_rect.width // 2, ball_y - ball_rect.height // 2))  # Bola

    # Mostrar pantalla de Game Over
    if game_over:
        font = pygame.font.Font(None, 36)
        screen.fill((50, 50, 50))
        text_surface1 = font.render("Resultados:", True, (255, 255, 255))
        screen.blit(text_surface1, (WIDTH // 2 - text_surface1.get_width() // 2, 10))

        # Mostrar lista de jugadores
        y_offset = 50
        for name, duration, photo in player_results:
            text_surface = font.render(f"{name}: {duration} seg", True, (255, 255, 255))
            screen.blit(text_surface, (10, y_offset))
            if photo is not None:
                photo_surface = pygame.surfarray.make_surface(cv2.cvtColor(photo, cv2.COLOR_BGR2RGB))
                photo_surface = pygame.transform.scale(photo_surface, (50, 50))
                screen.blit(photo_surface, (WIDTH - 60, y_offset))
            y_offset += 60

        text_surface2 = font.render("Presiona 'R' para reiniciar o 'Q' para salir", True, (255, 255, 255))
        screen.blit(text_surface2, (WIDTH // 2 - text_surface2.get_width() // 2, HEIGHT - 40))

    # Mostrar ventana de cámara (opcional)
    cv2.imshow("Detección de Mano", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Actualizar pantalla
    pygame.display.flip()
    clock.tick(30)

# Liberar recursos
cap.release()
cv2.destroyAllWindows()
