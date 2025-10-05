from pygame import *
import socket
import json
from threading import Thread

# ---ПУГАМЕ НАЛАШТУВАННЯ ---
WIDTH, HEIGHT = 800, 600
init()
screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Пінг-Понг")

# --- ЗОБРАЖЕННЯ ----

def draw_gradient(surface, color_top, color_bottom):
    """Малює вертикальний градієнт на поверхні."""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
        g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
        b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
        draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

# ---СЕРВЕР ---
def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 8080)) # ---- Підключення до сервера
            buffer = ""
            game_state = {}
            my_id = int(client.recv(24).decode())
            return my_id, game_state, buffer, client
        except:
            pass

def receive():
    global buffer, game_state, game_over
    while not game_over:
        try:
            data = client.recv(1024).decode()
            buffer += data
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)
                if packet.strip():
                    game_state = json.loads(packet)
        except:
            game_state["winner"] = -1
            break

# --- ШРИФТИ ---
font_win = font.Font(None, 72)
font_main = font.Font(None, 36)

# --- ГРА ---
game_over = False
winner = None
you_winner = None
my_id, game_state, buffer, client = connect_to_server()
Thread(target=receive, daemon=True).start()
while True:
    for e in event.get():
        if e.type == QUIT:
            exit()

    # Фон-градієнт
    draw_gradient(screen, (30, 30, 60), (80, 180, 220))

    # Рамка
    draw.rect(screen, (255, 255, 255), (10, 10, WIDTH-20, HEIGHT-20), 4)

    if "countdown" in game_state and game_state["countdown"] > 0:
        countdown_text = font.Font(None, 72).render(str(game_state["countdown"]), True, (255, 255, 255))
        screen.blit(countdown_text, (WIDTH // 2 - 20, HEIGHT // 2 - 30))
        display.update()
        continue

    if "winner" in game_state and game_state["winner"] is not None:
        if you_winner is None:
            if game_state["winner"] == my_id:
                you_winner = True
            else:
                you_winner = False

        text = "Ти переміг!" if you_winner else "Пощастить наступним разом!"
        win_text = font_win.render(text, True, (255, 215, 0))
        text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(win_text, text_rect)

        text = font_win.render('К - рестарт', True, (255, 215, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
        screen.blit(text, text_rect)

        display.update()
        continue

    if game_state:
        # Новий стиль платформ
        draw.rect(screen, (0, 255, 180), (20, game_state['paddles']['0'], 24, 100), border_radius=12)
        draw.rect(screen, (255, 80, 200), (WIDTH - 44, game_state['paddles']['1'], 24, 100), border_radius=12)
        # М'яч з обводкою
        draw.circle(screen, (255, 255, 255), (game_state['ball']['x'], game_state['ball']['y']), 12)
        draw.circle(screen, (0, 0, 0), (game_state['ball']['x'], game_state['ball']['y']), 12, 2)
        # Рахунок у стилі табло
        score_text = font_main.render(f"{game_state['scores'][0]}   |   {game_state['scores'][1]}", True, (255, 255, 0))
        score_bg = Surface((200, 50), SRCALPHA)
        score_bg.fill((0, 0, 0, 120))
        screen.blit(score_bg, (WIDTH // 2 - 90, 20))
        screen.blit(score_text, (WIDTH // 2 - 30, 30))

    else:
        wating_text = font_main.render(f"Очікування гравців...", True, (255, 255, 255))
        screen.blit(wating_text, (WIDTH // 2 - 100, HEIGHT // 2 - 20))

    display.update()
    clock.tick(60)

    keys = key.get_pressed()
    if keys[K_w]:
        client.send(b"UP")
    elif keys[K_s]:
        client.send(b"DOWN")

    display.update()
    clock.tick(60)

    keys = key.get_pressed()
    if keys[K_w]:
        client.send(b"UP")
    elif keys[K_s]:
        client.send(b"DOWN")