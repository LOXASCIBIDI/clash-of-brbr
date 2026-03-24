from random import randint
import pygame
import time
import math
import socket
import threading

# включать выключать музыку на ескейп описание на пкм выйти из описания лкм
pygame.init()
client_socket = None
connecting = False
window = pygame.display.set_mode((1000, 1000))
clock = pygame.time.Clock()
back = (200, 255, 255)
pygame.mixer.init()
y = 1
menu_music = "mp3menu.mp3"
battle_music = "mp3battle.mp3"
overtime_music = 'mp3overtime.mp3'

current_music = None
player_run = [f'img{i}.png' for i in range(1, 3)]

loxa_alive = False
ykrgap_alive = False
busa_alive = False
sachur_alive = False
bisek_alive = False
hekit_alive = False
escere_alive = False
airpots_alive = False
brbr_alive = False
oleg_alive = False
konus_alive = False
settings_open = False
music_on = True

class Player:
    def __init__(self, x, y, width, height, images):
        self.images = [pygame.transform.scale(pygame.image.load(img), (width, height)) for img in images]
        self.frame_index = 0
        self.image_speed = 0.1
        self.rect = self.images[0].get_rect(topleft=(x, y))
        self.current_img = self.images[0]

    def reset(self):
        window.blit(self.current_img, (self.rect.x, self.rect.y))

    def animate(self):
        self.frame_index += self.image_speed
        if self.frame_index >= len(self.images):
            self.frame_index = 0
        self.current_img = self.images[int(self.frame_index)]

class Picture:
    def __init__(self, filename, x=0, y=0, width=150, height=150):
        self.image_name = filename
        self.image = pygame.image.load(filename)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hp = 500
        self.alive = True

    def draw(self):
        if self.alive:
            window.blit(self.image, (self.rect.x, self.rect.y))
            font = pygame.font.SysFont("Arial", 20)
            hp_text = font.render(str(self.hp), True, (255, 0, 0))
            window.blit(hp_text, (self.rect.centerx - 20, self.rect.y - 20))
            font = pygame.font.SysFont("Arial", 20)
class Tower:
    def __init__(self, x, y, width, height, color, hp=1000, image_file=None, id=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hp = hp
        self.id = id
        self.alive = True
        if image_file:
            self.image = pygame.image.load(image_file)
            self.image = pygame.transform.scale(self.image, (width, height))
        else:
            self.image = None

    def draw(self):
        if self.alive:
            if self.image:
                window.blit(self.image, self.rect.topleft)
            else:
                pygame.draw.rect(window, self.color, self.rect)

            # Рисуем HP над башней
            font = pygame.font.SysFont("Arial", 20)
            hp_text = font.render(str(self.hp), True, (255, 0, 0))
            window.blit(hp_text, (self.rect.centerx - hp_text.get_width()//2, self.rect.y - 25))
class Unit:
    def __init__(self, name, image_file, x, y, width, height, hp, damage, speed, attack_speed, attack_range=120):
        self.name = name
        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = pygame.Rect(x, y, width, height)
        self.rect.center = (x, y)
        self.hp = hp
        self.damage = damage
        self.speed = speed
        self.attack_speed = attack_speed
        self.last_attack = time.time()
        self.alive = True
        self.attack_range = attack_range

    def move_towards(self, target):
        if not self.alive or not target.alive:
            return

        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)

        if distance > 0:
            move_x = int(self.speed * dx / distance)
            move_y = int(self.speed * dy / distance)
            new_rect = self.rect.move(move_x, move_y)

            for other in spawned_units:
                if other != self and other.alive and new_rect.colliderect(other.rect):
                    # сдвигаем вбок
                    move_x += randint(-2, 2)
                    move_y += randint(-2, 2)
                    new_rect = self.rect.move(move_x, move_y)

            self.rect = new_rect
    def attack(self, target):
        if not self.alive or not target.alive:
            return

        # расстояние от центра юнита до центра башни
        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)

        if distance <= getattr(self, "attack_range", 120):
            if time.time() - self.last_attack < self.attack_speed:
                return

            self.last_attack = time.time()
            target.hp -= self.damage
            if target.hp <= 0:
                target.hp = 0
                target.alive = False

    def draw(self):
        if self.alive:
            window.blit(self.image, self.rect.topleft)

            font = pygame.font.SysFont("Arial", 16)
            hp_text = font.render(str(self.hp), True, (255, 0, 0))
            window.blit(hp_text, (self.rect.centerx - 10, self.rect.y - 15))


zagruska = Picture('photo_2025-11-27_10-27-26.jpg', 0, 0, 1000, 1000)
zagruska_krug = Player(450, 500, 150, 200, player_run)
menu = Picture('fon.jpg', 0, 0, 1000, 1000)

characters = [
    Picture('brewmaster.png'),
    Picture('photo_2025-12-01_22-06-37.jpg'),
    Picture('nekit.jpg'),
    Picture('ykrgap.jpg'),
    Picture('super_busa.jpg'),
    Picture('loxa.jpg'),
    Picture('escere.jpg'),
    Picture('brbrpatapim.jpg'),
    Picture('bisektrisa.jpg'),
    Picture('airpots.jpg'),
    Picture('oleg.jpg'),
    Picture('konys.jpg')
]

prices = {
    "brewmaster.png": 8,
    "loxa.jpg": 8,
    "ykrgap.jpg": 5,
    "super_busa.jpg": 3,
    "photo_2025-12-01_22-06-37.jpg": 5,
    "bisektrisa.jpg": 1,
    "nekit.jpg": 2,
    "escere.jpg": 3,
    "airpots.jpg": 7,
    "brbrpatapim.jpg": 5,
    "oleg.jpg": 5,
    "konys.jpg": 3
}
card_descriptions = {
    "brewmaster.png": "пивний лев с тремя медведями, мой любимый.",
    "loxa.jpg": "Описание Лёхи\n\n лоха очень толстый и сильный.",
    "ykrgap.jpg": "Описание Юкргапа\n\n мало здоровя но неймоверная скорость атаки.",
    "super_busa.jpg": "Описание Бусы\n\n ультра быстрая бабушка которая купила крем для коленей.",
    "photo_2025-12-01_22-06-37.jpg": "Описание Сачура\n\n войн которий ждет свойго часа, очень загадочный.",
    "bisektrisa.jpg": "Описание Бисектрисы\n\n кошка самоубица дух который ранше был землей.",
    "nekit.jpg": "Описание Некита\n\n абсолютно не интересный персонаж с плохими характеристиками.",
    "escere.jpg": "Описание Эскере\n\n джокер после падения ешкерий ставит город гдебы то небыло и оппалюет свойх врагов.",
    "airpots.jpg": "Описание Аирпотса\n\n просто робот призваный служыть и ломать.",
    "brbrpatapim.jpg": "Описание БРБР\n\n икона игры сильный и храбрый войн.",
    "oleg.jpg": "Описание Олега\n\n нечем особо не отлечаеца но без негобы нечего небыло.",
    "konys.jpg": "Описание Конуса\n\n здание имеет неймоверно маленький запас здоровя но неймоверный урон."
}
show_description = None
selected = []
max_selected = 8

tower_my = Tower(450, 800, 100, 150, (70, 120, 255), hp=400, image_file='mycorol.png', id="tower_my_center" )
tower_enemy = Tower(450, 50, 100, 150, (255, 60, 60), hp=400, image_file='enemycorol.png', id="tower_enemy_center")
arena = Picture('arena.jpg', -150, -150, 1300, 1300)
mytl = Tower(240, 660, 100, 70, (70, 120, 255), hp=200, image_file='mytaver.png', id="my_tl")
mytr = Tower(670, 660, 100, 70, (70, 120, 255), hp=200, image_file='mytaver.png', id="my_tr")
enemytl = Tower(240, 280, 100, 70, (255, 60, 60), hp=200, image_file='enemytaver.png', id="enemy_tl")
enemytr = Tower(660, 280, 100, 70, (255, 60, 60), hp=200, image_file='enemytaver.png', id="enemy_tr")


enemyc = Picture('enemycorol.png', 435, 200, 130, 130)
myc = Picture('mycorol.png', 435, 650, 130, 130)
pula1 = Picture('pula-removebg-preview.png', 240, 280, 40, 40)
pula2 = Picture('pula-removebg-preview.png', 660, 280, 40, 40)
play_button = pygame.Rect(400, 850, 200, 80)
update_positions_needed = True
elixir = 6
max_elixir = 10
last_elixir_time = time.time()
battle_start_time = None
battle_time_limit = 150
overtime = False
overtime_text_time = 0
red_screen = pygame.Surface((1000, 1000))
red_screen.set_alpha(120)
red_screen.fill((255, 0, 0))
red_effect_timer = 0
spawned_units = []

forbidden_zone = pygame.Surface((1000, 500))
forbidden_zone.set_alpha(120)
forbidden_zone.fill((255, 0, 0))
kubasiki = 0
running = True
arena_mode = False
cards_queue = []
current_cards = []
active_unit = None
unit_on_mouse = False
loading_done = False

enemy_targets = [enemytl, enemytr, tower_enemy]
my_targets = [mytl, mytr, tower_my]

from queue import Queue
net_queue = Queue()

def listen_server():
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break

            print("NET:", data)

            parts = data.split()

            if parts[0] == "SPAWN":
                name = parts[1]
                x = int(parts[2])
                y = int(parts[3])
                net_queue.put(("SPAWN", name, x, y))
            elif parts[0] == "TOWER_HP":
                tower_id = parts[1]
                hp = int(parts[2])

                for t in enemy_targets + my_targets:
                    if t.id == tower_id:
                        t.hp = hp
            elif parts[0] == "DESTROY_TOWER":
                tower_name = parts[1]  # берем имя из сети

                for t in enemy_targets + my_targets:
                    if getattr(t, "name", None) == tower_name:
                        t.alive = False

        except Exception as e:
            print("Ошибка сети:", e)
            break
def draw_description(card):
    window.blit(pygame.transform.scale(card.image, (1000, 1000)), (0, 0))

    dark = pygame.Surface((1000,1000))
    dark.set_alpha(180)
    dark.fill((0,0,0))
    window.blit(dark,(0,0))

    font_title = pygame.font.SysFont("Verdana", 60)
    font_text = pygame.font.SysFont("Verdana", 30)

    title = font_title.render(card.image_name, True, (255,255,255))
    window.blit(title,(200,100))

    text = card_descriptions.get(card.image_name,"пивний лев с тремя медведями, мой любимый.")

    y = 700
    for line in text.split("\n"):
        txt = font_text.render(line, True, (255,255,255))
        window.blit(txt,(150,y))
        y += 40
def spawn_unit(name, x, y, enemy=False):
    prefix = "enemy_" if enemy else ""

    if name == 'loxa.jpg':
        spawned_units.append(Unit(prefix + 'loxa', 'loxa-removebg-preview.png', x, y, 80, 80, 90, 8, 2, 1))

    elif name == 'ykrgap.jpg':
        spawned_units.append(Unit(prefix + 'ykrgap', 'ykrgap-removebg-preview.png', x, y, 70, 70, 30, 5, 2, 5))

    elif name == 'brewmaster.png':
        offset = 40
        if enemy:
            positions = [
                ( x + offset, y ),
                ( x - offset, y ),
                ( x, y + offset )
            ]
        else:
            positions = [
                ( x - offset, y ),
                ( x + offset, y ),
                ( x, y - offset )
            ]

        images = ['brew1.png', 'brew2.png', 'brew3.png']
        stats = [
            (60, 6, 2, 1),
            (50, 8, 2, 1.2),
            (70, 4, 1, 0.8)
        ]

        for (px, py), img, (hp, dmg, spd, atkspd) in zip(positions, images, stats):
            spawned_units.append(
                Unit(prefix + 'brewmaster', img, px, py, 60, 60, hp, dmg, spd, atkspd)
            )

    elif name == 'super_busa.jpg':
        spawned_units.append(Unit(prefix + 'busa', 'super_busa-removebg-preview.png', x, y, 50, 50, 40, 5, 4, 0.8))

    elif name == 'photo_2025-12-01_22-06-37.jpg':
        spawned_units.append(Unit(prefix + 'sachur', 'photo_2025-12-01_22-06-37-removebg-preview.png', x, y, 70, 70, 55, 10, 2, 1))

    elif name == 'bisektrisa.jpg':
        spawned_units.append(Unit(prefix + 'bisek', 'bisektrisa-removebg-preview.png', x, y, 30, 30, 30, 5, 2, 1))

    elif name == 'nekit.jpg':
        spawned_units.append(Unit(prefix + 'hekit', 'nekit!.png', x, y, 50, 50, 45, 6, 2, 1))

    elif name == 'escere.jpg':
        spawned_units.append(Unit(prefix + 'escere', 'escere-removebg-preview.png', x, y, 70, 70, 70, 7, 0, 1))

    elif name == 'airpots.jpg':
        spawned_units.append(Unit(prefix + 'airpots', 'airpots-removebg-preview.png', x, y, 70, 70, 95, 7, 2, 1))

    elif name == 'brbrpatapim.jpg':
        spawned_units.append(Unit(prefix + 'brbr', 'brbrpatapim-removebg-preview.png', x, y, 70, 70, 50, 10, 2, 1))

    elif name == 'oleg.jpg':
        spawned_units.append(Unit(prefix + 'oleg', 'oleg-removebg-preview.png', x, y, 70, 70, 50, 4, 2, 2))

    elif name == 'konys.jpg':
        spawned_units.append(Unit(prefix + 'konus', 'konys-removebg-preview.png', x, y, 80, 80, 1, 5, 0, 10))
def get_closest_target(unit, targets):
    alive_targets = []
    for t in targets:
        if hasattr(t, "alive") and t.alive:
            alive_targets.append(t)
        elif not hasattr(t, "alive"):
            alive_targets.append(t)
    if not alive_targets:
        return None
    def dist(a, b):
        return math.hypot(a.rect.centerx - b.rect.centerx, a.rect.centery - b.rect.centery)
    closest = min(alive_targets, key=lambda t: dist(unit, t))
    return closest
def connect_to_server():
    global arena_mode, client_socket, connecting, battle_start_time, overtime
    global client_socket

    if client_socket:
        try:
            client_socket.close()
        except:
            pass
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("192.168.1.144", 5555))
        print("Подключение к серверу...")

        msg = client_socket.recv(1024).decode()
        if msg == "FOUND":
            threading.Thread(target=listen_server, daemon=True).start()
            print("Противник найден! Вы подключены!")
            arena_mode = True
            if not overtime:
                play_music(battle_music)
            battle_start_time = time.time()
            overtime = False
            connecting = False
    except:
        print("Ошибка подключения к серверу")
        connecting = False

def draw_elixir():
    pygame.draw.rect(window, (60, 60, 60), (20, 780, 300, 30), border_radius=10)
    fill_w = int((elixir / max_elixir) * 300)
    pygame.draw.rect(window, (120, 0, 255), (20, 780, fill_w, 30), border_radius=10)

def update_positions():
    start_x_left = 20
    start_y_left = 20
    spacing = 20
    cards_per_row = 3
    for i, pic in enumerate(selected):
        row = i // cards_per_row
        col = i % cards_per_row
        pic.rect.x = start_x_left + col * (pic.rect.width + spacing)
        pic.rect.y = start_y_left + row * (pic.rect.height + spacing)
    start_x_right = 500
    start_y_right = 20
    idx = 0
    for pic in characters:
        if pic not in selected:
            row = idx // cards_per_row
            col = idx % cards_per_row
            pic.rect.x = start_x_right + col * (pic.rect.width + spacing)
            pic.rect.y = start_y_right + row * (pic.rect.height + spacing)
            idx += 1

def menushca(duration):
    end_time = time.time() + duration
    while time.time() < end_time:
        zagruska.draw()
        zagruska_krug.animate()
        zagruska_krug.reset()
        pygame.display.update()
        clock.tick(40)
def can_move(unit, new_rect):
    for other in spawned_units:
        if other != unit and other.alive:
            if new_rect.colliderect(other.rect):
                return False
    return True
def draw_arena():
    window.fill((80, 140, 90))
    pygame.draw.rect(window, (0, 200, 200), (0, 450, 1000, 100))
    pygame.draw.rect(window, (150, 100, 50), (250, 450, 120, 30))
    pygame.draw.rect(window, (150, 100, 50), (630, 450, 120, 30))
    tower_enemy.draw()
    tower_my.draw()
    arena.draw()
    enemytl.draw()
    enemytr.draw()
    mytl.draw()
    mytr.draw()
    enemyc.draw()
    myc.draw()
    x = 150
    for card in current_cards:
        window.blit(card.image, (x, 850))
        x += 180
    for unit in spawned_units:
        unit.draw()
    if unit_on_mouse and active_unit:
        mx, my = pygame.mouse.get_pos()
        rect = active_unit['rect']
        rect.center = (mx, my)
        window.blit(active_unit['image'], rect.topleft)
        window.blit(forbidden_zone, (0, 0))
    if battle_start_time:
        elapsed = int(time.time() - battle_start_time)
        remaining = battle_time_limit - elapsed

        if remaining < 0:
            remaining = 0

        minutes = remaining // 60
        seconds = remaining % 60

        font = pygame.font.SysFont("Verdana", 40)
        timer_text = font.render(f"{minutes}:{seconds:02}", True, (255, 255, 255))
        window.blit(timer_text, (880, 20))

def play_music(track):
    global current_music

    if current_music != track:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(track)
        pygame.mixer.music.play(-1)
        current_music = track
while running:
    while not net_queue.empty():
        cmd = net_queue.get()

        if cmd[0] == "SPAWN":
            spawn_unit(cmd[1], cmd[2], cmd[3], enemy=True)

        if cmd[0] == "DESTROY_TOWER":
            tower_id = cmd[1]

            for t in enemy_targets + my_targets:
                if t.id == tower_id:
                    t.alive = False
                    break
    if not loading_done:
        menushca(5)
        loading_done = True
    if update_positions_needed:
        update_positions()
        update_positions_needed = False
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                settings_open = not settings_open
        if e.type == pygame.MOUSEBUTTONDOWN:
            if settings_open:
                mx, my = e.pos
                if 450 < mx < 550 and 500 < my < 600:
                    music_on = not music_on
                    if music_on:
                        pygame.mixer.music.set_volume(1)
                    else:
                        pygame.mixer.music.set_volume(0)
                continue
            mx, my = e.pos
            if e.button == 3 and not arena_mode:
                for pic in characters:
                    if pic.rect.collidepoint(mx, my):
                        show_description = pic
                        break
            if e.button == 1:
                if show_description:
                    show_description = None
                    continue
            if not arena_mode and play_button.collidepoint(mx, my):
                if len(selected) >= 8 and not connecting:
                    print("Идёт подключение к серверу...")
                    connecting = True
                    menushca(5)
                    connect_to_server()
                    cards_queue = list(selected)
                    current_cards = []
                    for _ in range(4):
                        if cards_queue:
                            current_cards.append(cards_queue.pop(0))
            if not arena_mode:
                for pic in characters:
                    if pic.rect.collidepoint(mx, my):
                        if pic in selected:
                            selected.remove(pic)
                        else:
                            if len(selected) < max_selected:
                                selected.append(pic)
                        update_positions_needed = True
                        break
            if arena_mode:
                if battle_start_time:
                    elapsed = time.time() - battle_start_time

                    if elapsed >= battle_time_limit and not overtime:
                        overtime = True
                        overtime_text_time = time.time()
                x = 150
                for i, card in enumerate(current_cards):
                    card_rect = pygame.Rect(x, 850, card.rect.width, card.rect.height)
                    if card_rect.collidepoint(mx, my):
                        active_unit = {'image': card.image.copy(), 'rect': card.rect.copy(),
                                       'name': card.image_name, 'index': i}
                        unit_on_mouse = True
                        break
                    x += 180

        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            if unit_on_mouse and active_unit:
                mx, my = pygame.mouse.get_pos()
                cost = prices.get(active_unit['name'], 0)
                if my >= 500:
                    if elixir < cost:
                        red_effect_timer = time.time() + 1
                        unit_on_mouse = False
                        active_unit = None
                    else:
                        elixir -= cost
                        name = active_unit['name']
                        x, y = mx, my
                        if client_socket:
                            mirror_x = 1000 - x
                            mirror_y = 1000 - y
                            msg = f"SPAWN {name} {x} {mirror_y}"
                            client_socket.send(msg.encode())

                        spawn_unit(name, x, y)
                        idx = active_unit['index']
                        if cards_queue:
                            current_cards[idx] = cards_queue.pop(0)
                            cards_queue.append(Picture(active_unit['name']))
                        unit_on_mouse = False
                        active_unit = None
                else:
                    unit_on_mouse = False
                    active_unit = None

    if arena_mode:
        regen_time = 3
        if overtime:
            play_music(overtime_music)
            regen_time = 1
        if time.time() - last_elixir_time >= regen_time:
            if elixir < max_elixir:
                elixir += 1
            last_elixir_time = time.time()

    if not arena_mode:
        play_music(menu_music)
        menu.draw()
        if show_description:
            draw_description(show_description)
        font = pygame.font.SysFont("Verdana", 40)
        kub_text = font.render(f"Кубки: {kubasiki}", True, (255, 255, 0))
        window.blit(kub_text, (40, 900))
        for pic in characters:
            pic.draw()
        pygame.draw.rect(window, (50, 150, 255), play_button, border_radius=20)
        font = pygame.font.SysFont("Verdana", 40)
        t = font.render("Играть", True, (255, 255, 255))
        window.blit(t, (play_button.x + 35, play_button.y + 15))
        y = 1
    else:
        if y == 1:
            menushca(5)
            y = 0
        draw_arena()
        draw_elixir()
        if overtime and time.time() - overtime_text_time < 3:
            font = pygame.font.SysFont("Verdana", 80)
            text = font.render("OVERTIME", True, (255, 50, 50))
            window.blit(text, (350, 80))
        if time.time() < red_effect_timer:
            window.blit(red_screen, (0, 0))

    my_units = [u for u in spawned_units if not u.name.startswith("enemy") and u.alive]
    enemy_units = [u for u in spawned_units if u.name.startswith("enemy") and u.alive]

    for unit in spawned_units:
        if not unit.alive:
            continue

        if unit.name.startswith("enemy"):
            possible_targets = my_units + [t for t in my_targets if t.alive]
        else:
            possible_targets = enemy_units + [t for t in enemy_targets if t.alive]

        target = get_closest_target(unit, possible_targets)
        target = get_closest_target(unit, possible_targets)
        if target is None:
            continue
        unit.move_towards(target)
        distance = math.hypot(
                unit.rect.centerx - target.rect.centerx,
                unit.rect.centery - target.rect.centery,
            )
        if distance <= unit.attack_range:
            unit.attack(target)
        else:

            pass
    enemy_all_dead = True
    for t in enemy_targets:
        if hasattr(t, "alive"):
            if t.alive:
                enemy_all_dead = False
    my_all_dead = True
    for t in my_targets:
        if hasattr(t, "alive"):
            if t.alive:
                my_all_dead = False
    if my_all_dead:
        kubki = randint(27, 32)
        kubasiki -= kubki
        if kubasiki < 0:
            kubasiki = 0
        arena_mode = False

        font = pygame.font.SysFont("Verdana", 80)
        text = font.render("Ты проиграл!", True, (255, 0, 0))
        window.blit(text, (220, 400))
        end_time = time.time() + 3
        while time.time() < end_time:
            pygame.display.update()

        spawned_units.clear()
        elixir = 6

        tower_enemy.hp = 1250
        tower_enemy.alive = True
        tower_enemy.rect.topleft = (450, 50)

        enemytl.hp = 725
        enemytl.alive = True
        enemytl.rect.topleft = (240, 280)

        enemytr.hp = 725
        enemytr.alive = True
        enemytr.rect.topleft = (660, 280)

        tower_my.hp = 1250
        tower_my.alive = True
        tower_my.rect.topleft = (450, 800)

        mytl.hp = 725
        mytl.alive = True
        mytl.rect.topleft = (240, 660)

        mytr.hp = 725
        mytr.alive = True
        mytr.rect.topleft = (670, 660)

        enemy_targets = [enemytl, enemytr, tower_enemy]
        my_targets = [mytl, mytr, tower_my]

        continue
    if enemy_all_dead:
        arena_mode = False
        kubki = randint(27, 35)
        font = pygame.font.SysFont("Verdana", 80)
        text = font.render("Ты выиграл!", True, (0, 255, 0))
        kubasiki = kubasiki + kubki
        window.blit(text, (250, 400))
        pygame.display.update()
        time.sleep(3)

        spawned_units.clear()
        elixir = 6

        tower_enemy.hp = 500
        tower_enemy.alive = True
        tower_enemy.rect.topleft = (450, 50)

        enemytl.hp = 400
        enemytl.alive = True
        enemytl.rect.topleft = (240, 280)

        enemytr.hp = 400
        enemytr.alive = True
        enemytr.rect.topleft = (660, 280)

        tower_my.hp = 500
        tower_my.alive = True
        tower_my.rect.topleft = (450, 800)

        mytl.hp = 400
        mytl.alive = True
        mytl.rect.topleft = (240, 660)

        mytr.hp = 400
        mytr.alive = True
        mytr.rect.topleft = (670, 660)

        enemy_targets = [enemytl, enemytr, tower_enemy]
        my_targets = [mytl, mytr, tower_my]

        continue
    if settings_open:
        white = pygame.Surface((1000, 1000))
        white.fill((255, 255, 255))
        window.blit(white, (0, 0))

        font = pygame.font.SysFont("Verdana", 60)
        text = font.render("Музыка", True, (0, 0, 0))
        window.blit(text, (350, 300))

        color = (0, 255, 0) if music_on else (255, 0, 0)
        pygame.draw.circle(window, color, (500, 550), 50)
    pygame.display.update()
    clock.tick(60)

pygame.quit()