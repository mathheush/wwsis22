import pygame
import random
import sys
import math
import json

# Inicjalizacja Pygame
pygame.init()

# Ustawienia pełnoekranowe
SCREEN_WIDTH = pygame.display.Info().current_w
SCREEN_HEIGHT = pygame.display.Info().current_h
win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Unikaj Strzałów")

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 128)
PINK = (255, 182, 193)
YELLOW = (255, 175, 0)

# Czcionka
font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 100)

# Plik z najlepszymi wynikami
highscore_file = 'highscores.json'

# Funkcja do ładowania najlepszych wyników
def load_highscores():
    try:
        with open(highscore_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"easy": 0, "medium": 0, "hard": 0}

# Funkcja do zapisywania najlepszych wyników
def save_highscores(highscores):
    with open(highscore_file, 'w') as file:
        json.dump(highscores, file)

# Najlepsze wyniki
highscores = load_highscores()

# Gracz
try:
    player_image = pygame.image.load('player.png')
    player_image = pygame.transform.scale(player_image, (50, 50))
except pygame.error as e:
    print(f"Could not load player image: {e}")
    pygame.quit()
    sys.exit()

player_rect = player_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
player_speed = 5
player_lives = 3  # Dodane życia gracza

# Strzały
bullet_size = 10
bullet_list = []
bullet_speed = 3  # Zmniejszona prędkość kulek
original_bullet_speed = bullet_speed  # Przechowywanie oryginalnej prędkości strzałów
new_bullet_event = pygame.USEREVENT + 1
bullet_spawn_time = 500  # Czas między pojawieniami się strzałów
pygame.time.set_timer(new_bullet_event, bullet_spawn_time)

# Przedmioty
item_size = 20
item_list = []
new_item_event = pygame.USEREVENT + 2
pygame.time.set_timer(new_item_event, 3000)  # Co 3 sekundy pojawia się nowy przedmiot

# Power-upy
power_up_size = 20
power_up_list = []
power_up_duration = 5000  # Czas trwania power-upa w milisekundach
new_power_up_event = pygame.USEREVENT + 3
power_up_end_event = pygame.USEREVENT + 4
pygame.time.set_timer(new_power_up_event, 10000)  # Co 10 sekund pojawia się nowy power-up

# Czas i punkty
points = 0
clock = pygame.time.Clock()
start_ticks = pygame.time.get_ticks()

# Poziom trudności
difficulty = "medium"

# Funkcja rysująca gracza
def draw_player():
    win.blit(player_image, player_rect.topleft)

# Funkcja rysująca strzały (czerwone kropki)
def draw_bullet(bullet):
    pygame.draw.circle(win, RED, bullet, bullet_size)

# Funkcja rysująca przedmioty (zielone kwadraty)
def draw_item(item):
    pygame.draw.rect(win, GREEN, (*item, item_size, item_size))

# Funkcja rysująca power-upy (niebieskie kwadraty)
def draw_power_up(power_up):
    pygame.draw.rect(win, BLUE, (*power_up, power_up_size, power_up_size))

# Funkcja detekcji kolizji
def detect_collision(player_rect, obj_pos, obj_size):
    obj_rect = pygame.Rect(obj_pos[0], obj_pos[1], obj_size, obj_size)
    return player_rect.colliderect(obj_rect)

# Funkcja wyświetlająca tekst
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect(topleft=(x, y))
    surface.blit(textobj, textrect)

# Funkcja gradientu radialnego tła
def create_radial_gradient(inner_color, outer_color):
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    max_radius = int(math.sqrt(center_x**2 + center_y**2))
    gradient_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for radius in range(max_radius, 0, -1):
        color = [
            inner_color[i] + (outer_color[i] - inner_color[i]) * radius // max_radius
            for i in range(3)
        ]
        pygame.draw.circle(gradient_surface, color + [255], (center_x, center_y), radius)
    return gradient_surface

# Przed rozpoczęciem gry stwórz gradient raz
gradient_surface = create_radial_gradient(PINK, DARK_BLUE)

# Funkcja przycisku
def button(text, x, y, width, height, color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(win, hover_color, (x, y, width, height), border_radius=10)
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(win, color, (x, y, width, height), border_radius=10)
    draw_text(text, small_font, WHITE, win, x + (width // 2 - small_font.size(text)[0] // 2), y + (height // 2 - small_font.size(text)[1] // 2))

# Funkcja restartu gry
def restart_game():
    global player_rect, bullet_list, item_list, power_up_list, start_ticks, game_over, points, bullet_spawn_time, player_lives, bullet_speed, original_bullet_speed
    player_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    bullet_list = []
    item_list = []
    power_up_list = []
    start_ticks = pygame.time.get_ticks()
    game_over = False
    points = 0
    bullet_spawn_time = 500  # Reset czasu między pojawieniami się strzałów
    bullet_speed = original_bullet_speed  # Reset prędkości kulek
    player_lives = 3  # Reset żyć gracza
    pygame.time.set_timer(new_bullet_event, bullet_spawn_time)
    start_game()

# Funkcja wyjścia z gry
def quit_game():
    pygame.quit()
    sys.exit()

# Funkcja ustawienia poziomu trudności
def set_difficulty(level):
    global difficulty, player_lives
    difficulty = level
    player_lives = 3  # Reset żyć przy zmianie poziomu trudności
    start_game()

# Ekran startowy
def game_intro():
    intro = True
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
        win.blit(gradient_surface, (0, 0))
        draw_text("Unikaj Strzałów", font, WHITE, win, SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 150)
        button("Łatwy", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 - 50, 150, 50, GREEN, BLUE, lambda: set_difficulty("easy"))
        button("Średni", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 25, 150, 50, GREEN, BLUE, lambda: set_difficulty("medium"))
        button("Trudny", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 100, 150, 50, GREEN, BLUE, lambda: set_difficulty("hard"))
        button("Wyjście", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 175, 150, 50, RED, BLUE, quit_game)
        pygame.display.update()
        clock.tick(15)

# Rozpoczęcie gry
def start_game():
    global start_ticks, game_over, bullet_spawn_time, bullet_speed
    start_ticks = pygame.time.get_ticks()
    game_over = False
    pygame.mouse.set_visible(False)
    # Ustawienia trudności
    if difficulty == "easy":
        bullet_spawn_time = 1000
        bullet_speed = 3
    elif difficulty == "medium":
        bullet_spawn_time = 500
        bullet_speed = 5
    elif difficulty == "hard":
        bullet_spawn_time = 300
        bullet_speed = 7
    pygame.time.set_timer(new_bullet_event, bullet_spawn_time)
    game_loop()

# Pętla gry
def game_loop():
    global game_over, points, bullet_spawn_time, bullet_speed, original_bullet_speed, player_lives
    game_over = False
    bullet_timer = 0  # Zmienna śledząca czas od ostatniego zwiększenia strzałów
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == new_bullet_event:
                side = random.choice(['top', 'bottom', 'left', 'right'])
                if side == 'top':
                    bullet_pos = [random.randint(0, SCREEN_WIDTH - bullet_size), 0]
                    bullet_dir = [0, 1]
                elif side == 'bottom':
                    bullet_pos = [random.randint(0, SCREEN_WIDTH - bullet_size), SCREEN_HEIGHT]
                    bullet_dir = [0, -1]
                elif side == 'left':
                    bullet_pos = [0, random.randint(0, SCREEN_HEIGHT - bullet_size)]
                    bullet_dir = [1, 0]
                else:
                    bullet_pos = [SCREEN_WIDTH, random.randint(0, SCREEN_HEIGHT - bullet_size)]
                    bullet_dir = [-1, 0]
                bullet_list.append([bullet_pos, bullet_dir])
            if event.type == new_item_event:
                item_pos = [random.randint(0, SCREEN_WIDTH - item_size), random.randint(0, SCREEN_HEIGHT - item_size)]
                item_list.append(item_pos)
            if event.type == new_power_up_event:
                power_up_pos = [random.randint(0, SCREEN_WIDTH - power_up_size),
                                random.randint(0, SCREEN_HEIGHT - power_up_size)]
                power_up_list.append(power_up_pos)
            if event.type == power_up_end_event:
                bullet_speed = original_bullet_speed  # Przywróć pierwotną prędkość strzałów

        # Sterowanie myszką - aktualizacja pozycji gracza
        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_rect.center = (mouse_x, mouse_y)

        # Rysowanie tła
        win.blit(gradient_surface, (0, 0))

        # Rysowanie strzałów i sprawdzanie kolizji
        for bullet in bullet_list:
            bullet[0][0] += bullet[1][0] * bullet_speed
            bullet[0][1] += bullet[1][1] * bullet_speed
            draw_bullet(bullet[0])
            if detect_collision(player_rect, bullet[0], bullet_size * 2):
                player_lives -= 1
                bullet_list.remove(bullet)
                if player_lives <= 0:
                    survival_time = (pygame.time.get_ticks() - start_ticks) / 1000
                    total_score = (points + 1) * survival_time * 22  # Oblicz wynik
                    game_over = True
                    game_over_screen("Game Over!", survival_time, points, total_score)

        # Rysowanie przedmiotów i sprawdzanie kolizji
        for item in item_list:
            draw_item(item)
            if detect_collision(player_rect, item, item_size):
                points += 1
                item_list.remove(item)

        # Obsługa power-upów
        for power_up in power_up_list:
            draw_power_up(power_up)
            if detect_collision(player_rect, power_up, power_up_size):
                power_up_list.remove(power_up)
                original_bullet_speed = bullet_speed  # Zapamiętaj obecną prędkość strzałów
                bullet_speed = max(1, bullet_speed - 1)  # Spowolnij strzały
                pygame.time.set_timer(power_up_end_event, power_up_duration)  # Ustaw timer na 5 sekund, aby przywrócić prędkość

        # Aktualizacja czasu przetrwania i zwiększanie częstotliwości strzałów
        survival_time = (pygame.time.get_ticks() - start_ticks) / 1000
        bullet_timer += clock.get_time()
        if bullet_timer >= 5000:  # Co 5 sekund zwiększaj częstotliwość pojawiania się strzałów
            bullet_spawn_time = max(100, bullet_spawn_time - 50)  # Zmniejsz czas między strzałami do minimum 100ms
            pygame.time.set_timer(new_bullet_event, bullet_spawn_time)
            bullet_timer = 0

        # Rysowanie gracza
        draw_player()

        # Wyświetlanie informacji
        draw_text(f"Survival Time: {survival_time:.2f}s", small_font, WHITE, win, 10, 10)
        draw_text(f"Points: {points}", small_font, WHITE, win, 10, 50)
        draw_text(f"Lives: {player_lives}", small_font, WHITE, win, 10, 90)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()
    sys.exit()

# Funkcja ekranu końcowego
def game_over_screen(message, survival_time, points, total_score):
    global game_over
    best_score = highscores[difficulty]
    pygame.mouse.set_visible(True)
    if total_score > best_score:
        best_score = total_score
        highscores[difficulty] = best_score
        save_highscores(highscores)
    while game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
        win.blit(gradient_surface, (0, 0))
        draw_text(message, big_font, WHITE, win, SCREEN_WIDTH // 2 - 175, SCREEN_HEIGHT // 2 - 150)
        draw_text(f"Total Score: {total_score:.2f}", small_font, WHITE, win, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50)
        draw_text(f"Best Score: {best_score:.2f}", small_font, WHITE, win, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100)
        button("Restart", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 175, 150, 50, GREEN, BLUE, restart_game)
        button("Menu", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 250, 150, 50, YELLOW, BLUE, game_intro)
        button("Wyjście", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 325, 150, 50, RED, BLUE, quit_game)
        pygame.display.update()
        clock.tick(15)


# Uruchomienie ekranu startowego
game_intro()
