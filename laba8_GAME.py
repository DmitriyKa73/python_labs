import pygame
import tkinter as tk
from tkinter import messagebox
import random
import math

# Инициализация Pygame
pygame.init()

# Основные настройки игры
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('PvP Арена')

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (220, 220, 220)
SELECTED_BORDER_COLOR = (0, 0, 0)  # Цвет обводки выбранного персонажа

# Размеры панели
PANEL_WIDTH = 250
PANEL_X = WIDTH - PANEL_WIDTH

# Размеры ячейки сетки
CELL_SIZE = 50


# Персонаж
class Character:
    def __init__(self, name, color, x, y, hp, damage, move_range=150, attack_range=1):
        self.name = name
        self.color = color
        self.rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.move_range = move_range  # Радиус перемещения в пикселях
        self.attack_range = attack_range  # Радиус атаки
        self.steps_left = 3  # Количество оставшихся шагов
        self.alive = True

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y - 10, CELL_SIZE, 5))
        pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y - 10, CELL_SIZE * (self.hp / self.max_hp), 5))
        # Рисуем обводку выбранного персонажа
        if selected_character == self:
            pygame.draw.rect(screen, SELECTED_BORDER_COLOR, self.rect, 3)

    def move(self, target_x, target_y):
        if self.steps_left > 0:
            # Перемещаемся строго по сетке
            new_x = round(target_x / CELL_SIZE) * CELL_SIZE
            new_y = round(target_y / CELL_SIZE) * CELL_SIZE
            distance = math.hypot(new_x - self.rect.x, new_y - self.rect.y)
            if distance <= self.move_range and not self.is_colliding(new_x, new_y):
                self.rect.x = new_x
                self.rect.y = new_y
                self.steps_left -= 1

    def is_colliding(self, x, y):
        for other in enemy_team + player_team:
            if other != self and other.rect.colliderect(pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)):
                return True
        return False

    def attack(self, target):
        if target and target.alive:
            distance = math.hypot(self.rect.x - target.rect.x, self.rect.y - target.rect.y)
            if distance <= self.attack_range * CELL_SIZE:
                target.hp -= self.damage
                if target.hp < 0:
                    target.hp = 0
                    target.alive = False

    def is_alive(self):
        return self.alive


def create_team(names, color, x_start, y_start, attack_ranges):
    team = []
    spacing = CELL_SIZE  # Расстояние между персонажами
    for i, (name, attack_range) in enumerate(zip(names, attack_ranges)):
        hp = random.randint(80, 120)
        damage = random.randint(10, 30)
        x = x_start
        y = y_start + i * (CELL_SIZE + spacing)  # Увеличиваем расстояние между персонажами
        team.append(Character(name, color, x, y, hp, damage, attack_range=attack_range))
    return team



def check_winner():
    if not any(char.is_alive() for char in player_team):
        return "Команда врага победила!"
    elif not any(char.is_alive() for char in enemy_team):
        return "Команда игрока победила!"
    return None


# Логика хода компьютера
def ai_move():
    living_enemies = [char for char in player_team if char.is_alive()]
    living_computers = [char for char in enemy_team if char.is_alive()]

    for computer_char in living_computers:
        if living_enemies:
            target = random.choice(living_enemies)
            distance = math.hypot(computer_char.rect.x - target.rect.x, computer_char.rect.y - target.rect.y)

            if distance <= computer_char.attack_range * CELL_SIZE:
                computer_char.attack(target)
            else:
                move_x = target.rect.x - computer_char.rect.x
                move_y = target.rect.y - computer_char.rect.y
                length = math.hypot(move_x, move_y)
                if length > 0:
                    move_x = (move_x / length) * min(computer_char.move_range, length)
                    move_y = (move_y / length) * min(computer_char.move_range, length)

                new_x = computer_char.rect.x + move_x
                new_y = computer_char.rect.y + move_y

                new_x = round(new_x / CELL_SIZE) * CELL_SIZE
                new_y = round(new_y / CELL_SIZE) * CELL_SIZE

                if not computer_char.is_colliding(new_x, new_y):
                    computer_char.rect.x = new_x
                    computer_char.rect.y = new_y


def draw_character_info(char, screen):
    pygame.draw.rect(screen, LIGHT_GRAY, (PANEL_X, 0, PANEL_WIDTH, HEIGHT))
    font = pygame.font.SysFont(None, 24)

    name_text = font.render(f"Имя: {char.name}", True, BLACK)
    hp_text = font.render(f"HP: {char.hp}/{char.max_hp}", True, BLACK)
    damage_text = font.render(f"Урон: {char.damage}", True, BLACK)
    range_text = font.render(f"Радиус атаки: {char.attack_range} клетки", True, BLACK)
    steps_text = font.render(f"Осталось шагов: {char.steps_left}", True, BLACK)

    screen.blit(name_text, (PANEL_X + 10, 10))
    screen.blit(hp_text, (PANEL_X + 10, 40))
    screen.blit(damage_text, (PANEL_X + 10, 70))
    screen.blit(range_text, (PANEL_X + 10, 100))
    screen.blit(steps_text, (PANEL_X + 10, 130))


def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))


# Инициализация команд с радиусами атаки
player_team = create_team(['Воин', 'Маг', 'Лучник'], BLUE, 100, 100, [2, 4, 3])
enemy_team = create_team(['Гоблин', 'Огр', 'Тролль'], RED, 600, 100, [1, 2, 3])

# Выбираем первого персонажа игрока по умолчанию
selected_character = player_team[0]
viewing_enemy = None  # Переменная для отображения информации о враге

running = True
clock = pygame.time.Clock()
player_turn = True  # Пошаговая механика, начинает игрок

while running:
    screen.fill(WHITE)

    # Рисуем сетку
    draw_grid()

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if player_turn:
                for char in player_team:
                    if char.rect.collidepoint(mouse_pos) and char.is_alive():
                        selected_character = char
                        viewing_enemy = None  # Сбрасываем просмотр врага
                        break
                for char in enemy_team:
                    if char.rect.collidepoint(mouse_pos) and char.is_alive():
                        viewing_enemy = char  # Выбираем врага для просмотра информации
                        selected_character = None  # Отключаем управление персонажем
                        break

        if event.type == pygame.KEYDOWN and selected_character and player_turn:
            if event.key == pygame.K_SPACE:
                # Атака выбранного врага
                for char in enemy_team:
                    if char.rect.collidepoint(pygame.mouse.get_pos()) and char.is_alive():
                        selected_character.attack(char)
                        selected_character.steps_left = 3  # Сброс шагов после атаки
                        player_turn = False
                        ai_move()  # Ход AI после атаки игрока
                        player_turn = True
            elif event.key == pygame.K_w:
                new_x = selected_character.rect.x
                new_y = selected_character.rect.y - CELL_SIZE
                selected_character.move(new_x, new_y)
            elif event.key == pygame.K_s:
                new_x = selected_character.rect.x
                new_y = selected_character.rect.y + CELL_SIZE
                selected_character.move(new_x, new_y)
            elif event.key == pygame.K_a:
                new_x = selected_character.rect.x - CELL_SIZE
                new_y = selected_character.rect.y
                selected_character.move(new_x, new_y)
            elif event.key == pygame.K_d:
                new_x = selected_character.rect.x + CELL_SIZE
                new_y = selected_character.rect.y
                selected_character.move(new_x, new_y)

    # Рисуем персонажей
    for char in player_team + enemy_team:
        if char.is_alive():
            char.draw(screen)

    # Отображаем информацию о выбранном персонаже или враге
    if selected_character:
        draw_character_info(selected_character, screen)
    elif viewing_enemy:
        draw_character_info(viewing_enemy, screen)

    # Проверка победителя
    winner = check_winner()
    if winner:
        running = False
        break

    pygame.display.flip()
    clock.tick(30)

# Завершение Pygame и вывод победителя
pygame.quit()

# Окно победителя на tkinter
root = tk.Tk()
root.withdraw()
messagebox.showinfo("Конец игры", winner)
root.destroy()
