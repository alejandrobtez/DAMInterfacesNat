import cv2
import mediapipe as mp
import pygame
import random
import sys
import time

# Configuración inicial de Pygame
pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juego de esquivar obstáculos con la mano")
clock = pygame.time.Clock()

# Cargar la imagen de la bola
ball_image = pygame.image.load("bola.png")  # Asegúrate de tener la imagen en el mismo directorio
ball_image = pygame.transform.scale(ball_image, (60, 60))  # Escalar la imagen si es necesario
ball_rect = ball_image.get_rect()
ball_x = WIDTH // 2
ball_y = HEIGHT - 50  # Posición fija en la parte inferior

# Configuración de obstáculos
obstacle_width, obstacle_height = 80, 20
obstacle_color = (255, 0, 0)
obstacle_speed_y = 5
obstacle_spawn_rate = 50
obstacles = []

# Inicializar la cámara y mediapipe para detectar la mano
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Tiempo inicial para la línea de meta
start_time = time.time()
goal_line_y = HEIGHT - 50  # Posición de la línea de meta en la parte inferior de la pantalla
goal_reached = False

# Función para reiniciar el juego
def reset_game():
    global ball_x, obstacles, start_time, goal_reached
    ball_x = WIDTH // 2
    obstacles = []
    start_time = time.time()
    goal_reached = False

# Bucle principal del juego
game_over = False
while True:
    # Manejar eventos de Pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            sys.exit()
        if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            game_over = False
            reset_game()

    # Lógica de juego si no es game over
    if not game_over and not goal_reached:
        # Capturar el frame de la cámara
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Procesar la detección de la mano
        results = hands.process(frame_rgb)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Calcular la posición horizontal (x) de la muñeca y escalarla a la pantalla de pygame
                wrist_x = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x
                ball_x = int(wrist_x * WIDTH)

        # Crear nuevos obstáculos aleatorios
        if random.randint(1, obstacle_spawn_rate) == 1:
            obstacle_x = random.randint(0, WIDTH - obstacle_width)
            obstacle_speed_x = random.choice([-3, -2, -1, 1, 2, 3])  # Movimiento horizontal al azar
            obstacles.append([obstacle_x, 0, obstacle_speed_x])

        # Actualizar posiciones de los obstáculos y verificar colisiones
        screen.fill((200, 200, 200))  # Fondo gris claro
        for obstacle in obstacles[:]:
            # Mover cada obstáculo hacia abajo y hacia los lados
            obstacle[1] += obstacle_speed_y  # Movimiento hacia abajo
            obstacle[0] += obstacle[2]       # Movimiento horizontal

            # Verificar los límites de la pantalla para los obstáculos
            if obstacle[0] < 0 or obstacle[0] > WIDTH - obstacle_width:
                obstacle[2] *= -1  # Cambia la dirección si llega a los bordes laterales

            # Dibujar el obstáculo
            pygame.draw.rect(screen, obstacle_color, (obstacle[0], obstacle[1], obstacle_width, obstacle_height))

            # Verificar si la bola ha colisionado con un obstáculo
            ball_rect.topleft = (ball_x - ball_rect.width // 2, ball_y - ball_rect.height // 2)
            obstacle_rect = pygame.Rect(obstacle[0], obstacle[1], obstacle_width, obstacle_height)
            if ball_rect.colliderect(obstacle_rect):
                game_over = True

            # Eliminar el obstáculo si ha salido de la pantalla
            if obstacle[1] > HEIGHT:
                obstacles.remove(obstacle)

        # Comprobar si han pasado 30 segundos para mostrar la línea de meta
        elapsed_time = time.time() - start_time
        if elapsed_time >= 30:
            # Dibujar la línea de meta
            pygame.draw.line(screen, (0, 255, 0), (0, goal_line_y), (WIDTH, goal_line_y), 5)

            # Verificar si el jugador ha alcanzado la línea de meta
            if ball_y + ball_rect.height // 2 >= goal_line_y:
                goal_reached = True

        # Dibujar la imagen de la bola en la pantalla
        screen.blit(ball_image, ball_rect.topleft)

    elif goal_reached:
        # Pantalla de victoria
        font = pygame.font.Font(None, 10)
        screen.fill((50, 200, 50))  # Fondo verde para victoria
        text_surface = font.render("¡Felicidades! Has ganado", True, (255, 255, 255))
        screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 2))
        text_surface = font.render("Presiona 'R' para jugar de nuevo", True, (255, 255, 255))
        screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 2 + 50))

    else:
        # Pantalla de Game Over
        font = pygame.font.Font(None, 50)
        screen.fill((50, 50, 50))  # Fondo oscuro para game over
        text_surface = font.render("¡Perdiste! Presiona 'R' para reiniciar", True, (255, 255, 255))
        screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 2))

    # Actualizar la pantalla y el reloj de juego
    pygame.display.flip()
    clock.tick(30)

    # Mostrar el frame de la cámara (opcional para depuración)
    cv2.imshow("Camera Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos al salir del juego
cap.release()
cv2.destroyAllWindows()
pygame.quit()
