import pygame
import sys
import json
import os
import random

# Инициализация Pygame и глобальных переменных
pygame.init()
info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h
tile_size = min(screen_width, screen_height) // 9
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Chess Endgame Simulator")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Загрузка фона
background = pygame.image.load("assets/background.jpg")
background = pygame.transform.scale(background, (screen_width, screen_height))


# Загрузка моделей фигур из папки assets
def load_images():
    pieces = {}
    for color in ["black", "white"]:
        for piece in ["king", "queen", "rook", "pawn", "bishop", "knight"]:
            image = pygame.image.load(f"assets/{color}_{piece}.png").convert_alpha()
            pieces[f"{color}_{piece}"] = pygame.transform.scale(image, (tile_size, tile_size))
            # Добавляем уменьшенные версии фигур для отображения съеденных
            pieces[f"{color}_{piece}_small"] = pygame.transform.scale(image, (tile_size // 2, tile_size // 2))
    return pieces


# Шахматная доска
board_color_1 = (235, 235, 208)
board_color_2 = (92, 86, 83)
highlight_color = (186, 202, 68)
button_color = (70, 130, 180)  # Более насыщенный синий цвет
button_hover_color = (100, 149, 237)  # Светло-синий при наведении
selected_piece = None
current_turn = "white"  # Добавляем переменную для отслеживания текущего хода

pieces = load_images()


class Button:
    def __init__(self, x, y, width, height, text, color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        self.custom_color = color

    def draw(self, screen):
        # Скругленные углы и градиент
        if self.custom_color:
            color = self.custom_color
        else:
            color = button_hover_color if self.is_hovered else button_color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (50, 50, 50), self.rect, 2, border_radius=10)

        # Тень для текста
        text_shadow = font.render(self.text, True, (0, 0, 0))
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_shadow, (text_rect.x + 2, text_rect.y + 2))
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False


# Классы для шахматных фигур и доски
class Piece:
    def __init__(self, color, type, position):
        self.color = color
        self.type = type
        self.position = position
        self.image = pieces[f"{color}_{type}"]
        self.has_moved = False

    def draw(self, screen):
        board_offset_x = (screen_width - 8 * tile_size) // 2
        board_offset_y = (screen_height - 8 * tile_size) // 2
        x, y = self.position
        screen.blit(self.image, (board_offset_x + x * tile_size, board_offset_y + y * tile_size))

    def move_to(self, new_position):
        self.position = new_position
        self.has_moved = True


class ChessBoard:
    def __init__(self):
        self.pieces = {}
        self.board_offset_x = (screen_width - 8 * tile_size) // 2
        self.board_offset_y = (screen_height - 8 * tile_size) // 2
        self.message = ""
        self.message_timer = 0
        self.moves_history = []
        self.current_save = None
        self.valid_moves = []  # Добавляем список для хранения возможных ходов
        self.captured_pieces = []  # Добавляем список для хранения съеденных фигур
        self.game_over = False  # Добавляем переменную для отслеживания конца игры

        # Создаем кнопки
        button_width = 200
        button_height = 50
        container_width = 300
        button_x = self.board_offset_x - container_width - 50 + (container_width - button_width) // 2
        button_spacing = 20

        # Вычисляем начальную позицию для центрирования кнопок по вертикали
        container_height = 600  # Высота контейнера
        total_buttons_height = (button_height + button_spacing) * 5 - button_spacing
        start_y = (container_height - total_buttons_height) // 2 + 200

        self.buttons = {
            'new_game': Button(button_x, start_y, button_width, button_height, "Новая игра"),
            'save_game': Button(button_x, start_y + button_height + button_spacing, button_width, button_height,
                                "Сохранить игру"),
            'load_game': Button(button_x, start_y + (button_height + button_spacing) * 2, button_width, button_height,
                                "Загрузить игру"),
            'instructions': Button(button_x, start_y + (button_height + button_spacing) * 3, button_width,
                                   button_height,
                                   "Инструкция"),
            'exit': Button(button_x, start_y + (button_height + button_spacing) * 4, button_width, button_height,
                           "Выход из игры")
        }

    def setup_pieces(self, piece_set, color):
        pieces = {}
        positions = [(x, y) for x in range(8) for y in range(8)]
        random.shuffle(positions)

        def get_random_position():
            while positions:
                pos = positions.pop()
                if pos[1] not in [0, 7]:  # Исключаем крайние верхние и нижние клетки для пешек
                    return pos
            return None

        def create_pieces():
            if piece_set == "king_queen":
                if color == "white":
                    return {
                        "white_king": Piece("white", "king", positions.pop()),
                        "white_queen": Piece("white", "queen", positions.pop()),
                        "black_king": Piece("black", "king", positions.pop()),
                        "black_rook": Piece("black", "rook", positions.pop()),
                        "black_pawn_1": Piece("black", "pawn", get_random_position()),
                        "black_pawn_2": Piece("black", "pawn", get_random_position())
                    }
                else:
                    return {
                        "black_king": Piece("black", "king", positions.pop()),
                        "black_queen": Piece("black", "queen", positions.pop()),
                        "white_king": Piece("white", "king", positions.pop()),
                        "white_rook": Piece("white", "rook", positions.pop()),
                        "white_pawn_1": Piece("white", "pawn", get_random_position()),
                        "white_pawn_2": Piece("white", "pawn", get_random_position())
                    }
            elif piece_set == "king_rook_pawns":
                if color == "white":
                    return {
                        "white_king": Piece("white", "king", positions.pop()),
                        "white_rook": Piece("white", "rook", positions.pop()),
                        "white_pawn_1": Piece("white", "pawn", get_random_position()),
                        "white_pawn_2": Piece("white", "pawn", get_random_position()),
                        "black_king": Piece("black", "king", positions.pop()),
                        "black_queen": Piece("black", "queen", positions.pop())
                    }
                else:
                    return {
                        "black_king": Piece("black", "king", positions.pop()),
                        "black_rook": Piece("black", "rook", positions.pop()),
                        "black_pawn_1": Piece("black", "pawn", get_random_position()),
                        "black_pawn_2": Piece("black", "pawn", get_random_position()),
                        "white_king": Piece("white", "king", positions.pop()),
                        "white_queen": Piece("white", "queen", positions.pop())
                    }

        # Создаем фигуры и проверяем на шах
        while True:
            positions = [(x, y) for x in range(8) for y in range(8)]
            random.shuffle(positions)
            pieces = create_pieces()
            self.pieces = pieces

            # Проверяем, нет ли шаха для обоих королей
            if not self.is_check("white") and not self.is_check("black"):
                break

        return pieces

    def add_move_to_history(self, piece, start_pos, end_pos, captured=None):
        piece_symbol = {
            'king': 'K', 'queen': 'Q', 'rook': 'R', 'pawn': '', 'bishop': 'B', 'knight': 'N'
        }
        start_coord = f"{chr(97 + start_pos[0])}{8 - start_pos[1]}"
        end_coord = f"{chr(97 + end_pos[0])}{8 - end_pos[1]}"
        move_text = f"{piece_symbol[piece.type]}{start_coord}-{end_coord}"
        if captured:
            move_text += "x"
        self.moves_history.append(move_text)

    def is_piece_between(self, start_pos, end_pos):
        x1, y1 = start_pos
        x2, y2 = end_pos

        # Определяем направление движения
        dx = 0 if x2 == x1 else (x2 - x1) // abs(x2 - x1)
        dy = 0 if y2 == y1 else (y2 - y1) // abs(y2 - y1)

        current_x, current_y = x1 + dx, y1 + dy
        while (current_x, current_y) != (x2, y2):
            if self.get_piece_at((current_x, current_y)):
                return True
            current_x += dx
            current_y += dy

        return False

    def is_check(self, color):
        king_pos = None
        for piece in self.pieces.values():
            if piece.type == "king" and piece.color == color:
                king_pos = piece.position
                break

        for piece in self.pieces.values():
            if piece.color != color:
                if piece.type == "knight":
                    # Для коня проверяем только возможность хода, без проверки препятствий
                    x_diff = abs(king_pos[0] - piece.position[0])
                    y_diff = abs(king_pos[1] - piece.position[1])
                    if (x_diff == 2 and y_diff == 1) or (x_diff == 1 and y_diff == 2):
                        return True
                elif self.is_valid_move(piece, king_pos):
                    if not self.is_piece_between(piece.position, king_pos):
                        return True
        return False

    def is_checkmate(self, color):
        if not self.is_check(color):
            return False

        for piece in self.pieces.values():
            if piece.color == color:
                valid_moves = self.get_valid_moves(piece)
                for move in valid_moves:
                    # Пробуем сделать ход
                    original_pos = piece.position
                    captured_piece = self.get_piece_at(move)
                    piece.move_to(move)
                    if captured_piece:
                        captured_key = None
                        for k, v in self.pieces.items():
                            if v == captured_piece:
                                captured_key = k
                                break
                        if captured_key:
                            del self.pieces[captured_key]

                    # Проверяем, остается ли король под шахом
                    still_in_check = self.is_check(color)

                    # Возвращаем все назад
                    piece.move_to(original_pos)
                    if captured_piece and captured_key:
                        self.pieces[captured_key] = captured_piece

                    if not still_in_check:
                        return False
        return True

    def is_stalemate(self, color):
        if self.is_check(color):
            return False

        for piece in self.pieces.values():
            if piece.color == color:
                valid_moves = self.get_valid_moves(piece)
                for move in valid_moves:
                    # Пробуем сделать ход
                    original_pos = piece.position
                    captured_piece = self.get_piece_at(move)
                    piece.move_to(move)
                    if captured_piece:
                        captured_key = None
                        for k, v in self.pieces.items():
                            if v == captured_piece:
                                captured_key = k
                                break
                        if captured_key:
                            del self.pieces[captured_key]

                    # Проверяем, не ставит ли этот ход короля под шах
                    legal_move = not self.is_check(color)

                    # Возвращаем все назад
                    piece.move_to(original_pos)
                    if captured_piece and captured_key:
                        self.pieces[captured_key] = captured_piece

                    if legal_move:
                        return False
        return True

    def draw(self, screen):
        # Отрисовка фона
        screen.blit(background, (0, 0))

        # Отрисовка доски
        for row in range(8):
            for col in range(8):
                color = board_color_1 if (row + col) % 2 == 0 else board_color_2
                pygame.draw.rect(screen, color,
                                 pygame.Rect(self.board_offset_x + col * tile_size,
                                             self.board_offset_y + row * tile_size,
                                             tile_size, tile_size))

        # Отрисовка возможных ходов
        for move in self.valid_moves:
            pygame.draw.circle(screen, highlight_color,
                               (self.board_offset_x + move[0] * tile_size + tile_size // 2,
                                self.board_offset_y + move[1] * tile_size + tile_size // 2),
                               10)

            # Отрисовка координат и полоски вокруг доски
        for i in range(8):
            # Цифры слева
            pygame.draw.rect(screen, (26, 7, 4),
                             (self.board_offset_x - 30, self.board_offset_y + i * tile_size, 30, tile_size))
            text = font.render(str(8 - i), True, (255, 255, 255))
            screen.blit(text, (self.board_offset_x - 25, self.board_offset_y + i * tile_size + tile_size // 3))

            # Буквы снизу
            pygame.draw.rect(screen, (26, 7, 4),
                             (self.board_offset_x - 30 + i * tile_size, self.board_offset_y + 8 * tile_size,
                              tile_size + 30, 30))
            text = font.render(chr(97 + i), True, (255, 255, 255))
            screen.blit(text, (
                self.board_offset_x + i * tile_size + tile_size // 3, self.board_offset_y + 8 * tile_size + 5))

            # Полоска сверху
            pygame.draw.rect(screen, (26, 7, 4),
                             (self.board_offset_x - 30, self.board_offset_y - 30, 8 * tile_size + 60, 30))

            # Полоска справа
            pygame.draw.rect(screen, (26, 7, 4),
                             (self.board_offset_x + 8 * tile_size, self.board_offset_y - 30, 30, 8 * tile_size + 60))

        # Отрисовка фигур
        for piece in self.pieces.values():
            piece.draw(screen)

        # Отрисовка сообщений
        if self.message and self.message_timer > 0:
            # Создаем полупрозрачный фон для сообщения
            message_surface = pygame.Surface((screen_width, 100), pygame.SRCALPHA)
            message_surface.fill((0, 0, 0, 128))  # Черный цвет с прозрачностью

            # Отрисовываем текст сообщения с тенью
            text_shadow = font.render(self.message, True, (0, 0, 0))
            text_surface = font.render(self.message, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(screen_width // 2, 50))
            message_surface.blit(text_shadow, (text_rect.x + 4, text_rect.y + 4))
            message_surface.blit(text_surface, text_rect)

            # Отображаем сообщение на экране
            screen.blit(message_surface, (0, 0))
            self.message_timer -= 1

        # Определяем размеры контейнеров
        container_width = 300
        container_height = screen_height - 400
        buttons_x = self.board_offset_x - container_width - 50
        buttons_y = 170
        moves_x = self.board_offset_x + 8 * tile_size + 50
        moves_y = 170

        # Отрисовка контейнера для кнопок
        pygame.draw.rect(screen, (100, 100, 100),
                         (buttons_x - 2, buttons_y - 2, container_width + 4, container_height + 4), 2)
        pygame.draw.rect(screen, (235, 235, 208),
                         (buttons_x, buttons_y, container_width, container_height))

        # Отрисовка заголовка "Шахматный эндшпиль" в две строки
        title_font = pygame.font.Font(None, 52)
        title_text_1 = title_font.render("Шахматный", True, (0, 0, 0))
        title_text_2 = title_font.render("эндшпиль", True, (0, 0, 0))

        # Создаем прямоугольники для заголовков
        title_rect_1 = title_text_1.get_rect(center=(buttons_x + container_width // 2, buttons_y + 70))
        title_rect_2 = title_text_2.get_rect(center=(buttons_x + container_width // 2, buttons_y + 115))

        # Отрисовываем заголовки с тенями для красоты
        shadow_offset = 2
        shadow_color = (150, 150, 150)

        # Тень для первого заголовка
        shadow_rect_1 = title_rect_1.copy()
        shadow_rect_1.center = (title_rect_1.centerx + shadow_offset, title_rect_1.centery + shadow_offset)
        screen.blit(title_font.render("Шахматный", True, shadow_color), shadow_rect_1)

        # Тень для второго заголовка
        shadow_rect_2 = title_rect_2.copy()
        shadow_rect_2.center = (title_rect_2.centerx + shadow_offset, title_rect_2.centery + shadow_offset)
        screen.blit(title_font.render("эндшпиль", True, shadow_color), shadow_rect_2)

        # Основной текст заголовков
        screen.blit(title_text_1, title_rect_1)
        screen.blit(title_text_2, title_rect_2)

        # Отрисовка кнопок
        for button in self.buttons.values():
            button.draw(screen)

        # Отрисовка правого контейнера
        pygame.draw.rect(screen, (100, 100, 100),
                         (moves_x - 2, moves_y - 2, container_width + 4, container_height + 4), 2)
        pygame.draw.rect(screen, (235, 235, 208),
                         (moves_x, moves_y, container_width, container_height))

        # Отображение текущего сохранения и хода в правом контейнере
        if self.current_save:
            save_text = font.render("Текущее сохранение:", True, (0, 0, 0))
            screen.blit(save_text, (moves_x + 10, moves_y + 10))
            save_name = font.render(f"{self.current_save}", True, (0, 0, 0))
            screen.blit(save_name, (moves_x + 10, moves_y + 40))
            turn_text = font.render(
                f"Ход {'белых' if current_turn == 'white' else 'черных'}",
                True, (0, 0, 0))
            screen.blit(turn_text, (moves_x + 10, moves_y + 80))

        elif not self.game_over:
            if not self.pieces:
                turn_text = font.render("Начните новую игру!", True, (0, 0, 0))
            else:
                turn_text = font.render(
                    f"Ход {'белых' if current_turn == 'white' else 'черных'}",
                    True, (0, 0, 0))
            screen.blit(turn_text, (moves_x + 10, moves_y + 80))
        else:
            turn_text = font.render("Конец игры!", True, (0, 0, 0))
            screen.blit(turn_text, (moves_x + 10, moves_y + 80))

        # Отрисовка истории ходов
        history_text = font.render("История ходов:", True, (0, 0, 0))
        screen.blit(history_text, (moves_x + 10, moves_y + 120))

        # Отображаем последние 11 ходов, используя прокрутку если нужно
        visible_moves = 11  # Количество видимых ходов
        start_index = max(0, len(self.moves_history) - visible_moves)

        for i, move in enumerate(self.moves_history[start_index:]):
            move_number = start_index + i + 1
            move_text = font.render(f"{move_number}. {move}", True, (0, 0, 0))
            screen.blit(move_text, (moves_x + 10, moves_y + 160 + i * 30))

        # Отрисовка съеденных фигур
        small_piece_size = tile_size // 2
        captured_x = moves_x + 10
        captured_y = moves_y + container_height - small_piece_size * 2 - 20

        # Отрисовка заголовка для съеденных фигур
        captured_text = font.render("Съеденные фигуры:", True, (0, 0, 0))
        screen.blit(captured_text, (captured_x, captured_y - 30))

        # Разделяем съеденные фигуры по цветам
        white_captured = [p for p in self.captured_pieces if p.color == "white"]
        black_captured = [p for p in self.captured_pieces if p.color == "black"]

        # Отрисовка черных съеденных фигур
        for i, piece in enumerate(black_captured):
            if i < 8:  # Максимум 8 фигур в ряду
                x = captured_x + i * small_piece_size
                y = captured_y
                small_image = pieces[f"{piece.color}_{piece.type}_small"]
                screen.blit(small_image, (x, y))

        # Отрисовка белых съеденных фигур
        for i, piece in enumerate(white_captured):
            if i < 8:  # Максимум 8 фигур в ряду
                x = captured_x + i * small_piece_size
                y = captured_y + small_piece_size
                small_image = pieces[f"{piece.color}_{piece.type}_small"]
                screen.blit(small_image, (x, y))

    def promote_pawn(self, pawn):
        # Создаем поверхность для меню выбора фигуры
        menu_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for i in range(screen_height):
            alpha = min(128, i // 16)
            pygame.draw.line(menu_surface, (70, 130, 180, alpha), (0, i), (screen_width, i))

        menu_width = 800  # Увеличиваем ширину меню
        menu_height = 300
        menu_rect = pygame.Rect((screen_width - menu_width) // 2,
                                (screen_height - menu_height) // 2,
                                menu_width, menu_height)

        piece_types = ["queen", "rook", "bishop", "knight"]  # Добавляем bishop и knight
        piece_rects = []
        piece_size = tile_size
        spacing = 20
        total_width = len(piece_types) * piece_size + (len(piece_types) - 1) * spacing
        start_x = menu_rect.centerx - total_width // 2 + 70  # Сдвигаем фигуры правее

        for i, piece_type in enumerate(piece_types):
            piece_image = pieces[f"{pawn.color}_{piece_type}"]
            piece_rect = piece_image.get_rect()
            piece_rect.centerx = start_x + i * (piece_size + spacing)
            piece_rect.centery = menu_rect.centery
            piece_rects.append((piece_rect, piece_type))

        selecting = True
        while selecting:
            screen.blit(background, (0, 0))  # Отрисовка фона
            screen.blit(menu_surface, (0, 0))

            # Рисуем контейнер с обводкой
            pygame.draw.rect(screen, (235, 235, 208), menu_rect)
            pygame.draw.rect(screen, (100, 100, 100), menu_rect, 2)

            title = font.render("Выберите фигуру для превращения:", True, (0, 0, 0))
            title_rect = title.get_rect(center=(screen_width // 2, menu_rect.top + 30))
            screen.blit(title, title_rect)

            # Отрисовка фигур
            for rect, piece_type in piece_rects:
                screen.blit(pieces[f"{pawn.color}_{piece_type}"], rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for rect, piece_type in piece_rects:
                        if rect.collidepoint(event.pos):
                            new_piece = Piece(pawn.color, piece_type, pawn.position)
                            for key, value in self.pieces.items():
                                if value == pawn:
                                    self.pieces[key] = new_piece
                                    break
                            selecting = False
                            return

    def get_next_save_number(self):
        existing_saves = [f for f in os.listdir() if f.startswith('save') and f.endswith('.json')]
        if not existing_saves:
            return 1
        numbers = [int(f.replace('save', '').replace('.json', '')) for f in existing_saves]
        max_number = max(numbers)
        next_number = max_number + 1 if max_number < 9 else 1
        return next_number

    def delete_all_saves(self):
        saves = [f for f in os.listdir() if f.startswith('save') and f.endswith('.json')]
        for save in saves:
            os.remove(save)
        self.current_save = None
        self.show_message("Все сохранения удалены!")

    def save_game(self):
        if not self.pieces or self.game_over:
            self.show_message("Нечего сохранять!")
            return

        save_number = self.get_next_save_number()
        filename = f'save{save_number}.json'
        game_state = {
            'pieces': [(p.color, p.type, p.position) for p in self.pieces.values()],
            'moves_history': self.moves_history,
            'current_turn': current_turn,
            'captured_pieces': [(p.color, p.type) for p in self.captured_pieces]  # Сохраняем съеденные фигуры
        }
        with open(filename, 'w') as f:
            json.dump(game_state, f)
        self.current_save = filename
        if save_number < 9:
            self.show_message(f"Игра сохранена как {filename}!")
        else:
            self.show_message(f"Сохранено в {filename} Дальнейшие сохранения будут в save1.json. Очистите память")

    def load_game(self):
        saves = [f for f in os.listdir() if f.startswith('save') and f.endswith('.json')]
        if not saves:
            self.show_message("Нет доступных сохранений!")
            return

        # Создаем поверхность для меню загрузки с градиентным фоном
        menu_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for i in range(screen_height):
            alpha = min(128, i // 16)
            pygame.draw.line(menu_surface, (70, 130, 180, alpha), (0, i), (screen_width, i))

        # Создаем контейнер для меню загрузки
        menu_width = 400
        menu_height = len(saves) * 60 + 220  # Увеличиваем высоту для кнопок
        menu_rect = pygame.Rect((screen_width - menu_width) // 2,
                                (screen_height - menu_height) // 2,
                                menu_width, menu_height)

        # Рисуем контейнер с обводкой
        pygame.draw.rect(menu_surface, (235, 235, 208), menu_rect)
        pygame.draw.rect(menu_surface, (100, 100, 100), menu_rect, 2)

        # Добавляем заголовок
        title = font.render("Выберите нужное сохранение:", True, (0, 0, 0))
        title_rect = title.get_rect(center=(screen_width // 2, menu_rect.top + 30))

        save_buttons = []
        button_height = 50
        button_spacing = 10
        start_y = menu_rect.top + 70

        for i, save in enumerate(saves):
            button = Button(menu_rect.centerx - 100, start_y + i * (button_height + button_spacing),
                            200, button_height, save)
            save_buttons.append((button, save))

        # Добавляем кнопку "Назад"
        back_button = Button(menu_rect.centerx - 100,
                             start_y + len(saves) * (button_height + button_spacing),
                             200, button_height, "Назад")

        # Добавляем кнопку удаления всех сохранений
        delete_button = Button(menu_rect.centerx - 150,
                               start_y + len(saves) * (button_height + button_spacing) + button_height + button_spacing,
                               300, button_height, "Удалить все сохранения", (255, 0, 0))

        selecting = True
        while selecting:
            screen.blit(background, (0, 0))  # Отрисовка фона
            screen.blit(menu_surface, (0, 0))
            screen.blit(title, title_rect)

            for button, _ in save_buttons:
                button.draw(screen)

            back_button.draw(screen)
            delete_button.draw(screen)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if delete_button.rect.collidepoint(event.pos):
                        self.delete_all_saves()
                        selecting = False
                        break
                    elif back_button.rect.collidepoint(event.pos):
                        selecting = False
                        break

                    for button, save_file in save_buttons:
                        if button.rect.collidepoint(event.pos):
                            try:
                                with open(save_file, 'r') as f:
                                    game_state = json.load(f)
                                self.pieces = {}
                                for color, type, position in game_state['pieces']:
                                    piece_key = f"{color}_{type}"
                                    if len([p for p in self.pieces.values() if
                                            p.type == type and p.color == color]) > 0:
                                        piece_key += f"_{len([p for p in self.pieces.values() if p.type == type and p.color == color]) + 1}"
                                    self.pieces[piece_key] = Piece(color, type, tuple(position))
                                self.moves_history = game_state['moves_history']
                                global current_turn
                                current_turn = game_state.get('current_turn', 'white')
                                # Загружаем съеденные фигуры
                                self.captured_pieces = []
                                if 'captured_pieces' in game_state:
                                    for color, type in game_state['captured_pieces']:
                                        self.captured_pieces.append(Piece(color, type, (-1, -1)))
                                self.current_save = save_file
                                self.show_message(f"Игра загружена из {save_file}!")
                                selecting = False
                            except:
                                self.show_message("Ошибка загрузки игры!")
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        selecting = False

    def show_message(self, text, duration=180):
        self.message = text
        self.message_timer = duration

    def get_piece_at(self, position):
        for piece in self.pieces.values():
            if piece.position == position:
                return piece
        return None

    def is_valid_move(self, piece, new_pos):
        if not (0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8):
            return False

        target_piece = self.get_piece_at(new_pos)
        if target_piece and target_piece.color == piece.color:
            return False

        x_diff = abs(new_pos[0] - piece.position[0])
        y_diff = abs(new_pos[1] - piece.position[1])

        if piece.type == "king":
            return x_diff <= 1 and y_diff <= 1
        elif piece.type == "queen":
            return (x_diff == y_diff or x_diff == 0 or y_diff == 0) and not self.is_piece_between(piece.position,
                                                                                                  new_pos)
        elif piece.type == "rook":
            return (x_diff == 0 or y_diff == 0) and not self.is_piece_between(piece.position, new_pos)
        elif piece.type == "bishop":
            return x_diff == y_diff and not self.is_piece_between(piece.position, new_pos)
        elif piece.type == "knight":
            return (x_diff == 2 and y_diff == 1) or (x_diff == 1 and y_diff == 2)
        elif piece.type == "pawn":
            direction = -1 if piece.color == "white" else 1
            if target_piece:
                return y_diff == 1 and x_diff == 1 and (new_pos[1] - piece.position[1]) == direction
            else:
                if not piece.has_moved:
                    return x_diff == 0 and (new_pos[1] - piece.position[1]) == direction * (
                        1 if y_diff == 1 else 2) and not self.is_piece_between(piece.position, new_pos)
                return x_diff == 0 and (new_pos[1] - piece.position[1]) == direction and y_diff == 1

        return False
    def get_valid_moves(self, piece):
        valid_moves = []
        for x in range(8):
            for y in range(8):
                if self.is_valid_move(piece, (x, y)):
                    # Проверяем, не ставит ли этот ход короля под шах
                    original_pos = piece.position
                    captured_piece = self.get_piece_at((x, y))
                    piece.move_to((x, y))

                    if captured_piece:
                        captured_key = None
                        for k, v in self.pieces.items():
                            if v == captured_piece:
                                captured_key = k
                                break
                        if captured_key:
                            del self.pieces[captured_key]

                    if not self.is_check(piece.color):
                        valid_moves.append((x, y))

                    # Возвращаем все назад
                    piece.move_to(original_pos)
                    if captured_piece and captured_key:
                        self.pieces[captured_key] = captured_piece

        return valid_moves

    def handle_click(self, pos):
        global selected_piece, current_turn
        board_x = (pos[0] - self.board_offset_x) // tile_size
        board_y = (pos[1] - self.board_offset_y) // tile_size

        if not (0 <= board_x < 8 and 0 <= board_y < 8):
            return

        clicked_pos = (board_x, board_y)
        clicked_piece = self.get_piece_at(clicked_pos)

        if selected_piece:
            if clicked_piece and clicked_piece.color == selected_piece.color:
                selected_piece = clicked_piece
                self.valid_moves = self.get_valid_moves(selected_piece)
            elif (board_x, board_y) in self.valid_moves:
                start_pos = selected_piece.position
                captured = clicked_piece is not None
                selected_piece.move_to(clicked_pos)
                if clicked_piece:
                    captured_key = None
                    for k, v in self.pieces.items():
                        if v == clicked_piece:
                            captured_key = k
                            break
                    if captured_key:
                        del self.pieces[captured_key]
                        self.captured_pieces.append(clicked_piece)  # Добавляем съеденную фигуру в список
                self.add_move_to_history(selected_piece, start_pos, clicked_pos, captured)

                # Проверяем превращение пешки
                if selected_piece.type == "pawn":
                    if (selected_piece.color == "white" and clicked_pos[1] == 0) or \
                            (selected_piece.color == "black" and clicked_pos[1] == 7):
                        self.promote_pawn(selected_piece)

                # Проверяем шах, мат или пат
                next_color = "black" if current_turn == "white" else "white"
                if self.is_check(next_color):
                    if self.is_checkmate(next_color):
                        self.show_message(f"Шах и мат! Победа {current_turn}!")
                        self.game_over = True
                    else:
                        self.show_message("Шах!")
                elif self.is_stalemate(next_color):
                    self.show_message("Пат! Ничья!")
                    self.game_over = True

                current_turn = next_color
                selected_piece = None
                self.valid_moves = []
            else:
                self.show_message("Некорректный ход!")
                selected_piece = None
                self.valid_moves = []
        elif clicked_piece and clicked_piece.color == current_turn:
            selected_piece = clicked_piece
            self.valid_moves = self.get_valid_moves(selected_piece)

        # Проверка на наличие только двух королей
        if len(self.pieces) == 2 and all(piece.type == "king" for piece in self.pieces.values()):
            self.show_message("Пат! Ничья!")
            self.game_over = True

    def handle_events(self):
        global selected_piece, current_turn
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Проверяем нажатия на кнопки
                for button_name, button in self.buttons.items():
                    if button.handle_event(event):
                        if button_name == 'new_game':
                            # Сохраняем текущее состояние перед показом меню
                            self.show_new_game_menu()
                            selected_piece = None

                        elif button_name == 'save_game':
                            self.save_game()
                        elif button_name == 'load_game':
                            self.load_game()
                            selected_piece = None
                        elif button_name == 'instructions':
                            self.show_instructions()
                        elif button_name == 'exit':
                            pygame.quit()
                            sys.exit()
                        return

                # Обработка кликов по доске
                self.handle_click(mouse_pos)

            elif event.type == pygame.MOUSEMOTION:
                # Обновление состояния наведения для кнопок
                for button in self.buttons.values():
                    button.handle_event(event)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    def clear_board(self):
        self.pieces.clear()
        self.captured_pieces.clear()

    def show_instructions(self):
        instructions = [
            "ИНСТРУКЦИЯ ПО ИГРЕ ШАХМАТНЫЙ ЭНДШПИЛЬ:",
            " ",
            "1. Кликните на фигуру, чтобы выбрать ее",
            "2. Кликните на клетку, куда хотите переместить фигуру",
            "3. Используйте кнопки слева для управления игрой",
            "4. История ходов отображается справа",
            "5. Съеденные фигуры отображаются сбоку от доски",
            "6. При мате или пате игра завершается с соответствующим сообщением",
            " ",
            "Нажмите любую клавишу, чтобы продолжить...",
            "gamedev Dmitriy Kazarov, 2024"
        ]

        # Создаем поверхность для инструкций с градиентным фоном
        instruction_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for i in range(screen_height):
            alpha = min(128, i // 16)
            pygame.draw.line(instruction_surface, (70, 130, 180, alpha), (0, i), (screen_width, i))

        # Создаем контейнер для инструкций
        container_width = 900
        container_height = 500
        container_rect = pygame.Rect((screen_width - container_width) // 2,
                                     (screen_height - container_height) // 2,
                                     container_width, container_height)

        showing_instructions = True
        while showing_instructions:
            screen.blit(background, (0, 0))  # Отрисовка фона
            screen.blit(instruction_surface, (0, 0))

            # Рисуем контейнер с обводкой
            pygame.draw.rect(screen, (235, 235, 208), container_rect)
            pygame.draw.rect(screen, (100, 100, 100), container_rect, 2)

            for i, line in enumerate(instructions):
                text = font.render(line, True, (0, 0, 0))
                screen.blit(text, (container_rect.centerx - text.get_width() // 2,
                                   container_rect.top + 40 + i * 40))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    showing_instructions = False

    def show_new_game_menu(self):
        global current_turn
        # Сохраняем текущее состояние игры
        saved_state = {
            'pieces': self.pieces.copy(),
            'captured_pieces': self.captured_pieces.copy(),
            'moves_history': self.moves_history.copy(),
            'current_turn': current_turn,
            'game_over': self.game_over
        }

        # Создаем поверхность для меню новой игры с градиентным фоном
        menu_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for i in range(screen_height):
            alpha = min(128, i // 16)
            pygame.draw.line(menu_surface, (70, 130, 180, alpha), (0, i), (screen_width, i))

        # Создаем контейнер для меню новой игры
        menu_width = 800  # Увеличиваем ширину меню
        menu_height = 400
        menu_rect = pygame.Rect((screen_width - menu_width) // 2,
                                (screen_height - menu_height) // 2,
                                menu_width, menu_height)

        # Опции для выбора
        options = {
            "Противник:": ["Игрок", "ПК"],
            "Сторона:": ["Белые", "Черные"],
            "Набор фигур:": ["Король, ферзь", "Король, ладья, 2 пешки"]
        }

        selected_options = {
            "Противник:": 0,
            "Сторона:": 0,
            "Набор фигур:": 0
        }

        selecting = True
        start_new_game = False
        while selecting:
            screen.blit(background, (0, 0))  # Отрисовка фона
            screen.blit(menu_surface, (0, 0))

            # Рисуем контейнер с обводкой
            pygame.draw.rect(screen, (235, 235, 208), menu_rect)
            pygame.draw.rect(screen, (100, 100, 100), menu_rect, 2)

            title = font.render("Настройки новой игры", True, (0, 0, 0))
            title_rect = title.get_rect(center=(screen_width // 2, menu_rect.top + 30))
            screen.blit(title, title_rect)

            # Отрисовка опций
            for i, (option, values) in enumerate(options.items()):
                option_text = font.render(option, True, (0, 0, 0))
                screen.blit(option_text, (menu_rect.left + 50, menu_rect.top + 80 + i * 80))

                for j, value in enumerate(values):
                    value_text = font.render(value, True, (0, 0, 0) if selected_options[option] != j else (255, 0, 0))
                    # Перемещение кнопок выбора команды, набора фигур и тд
                    screen.blit(value_text, (menu_rect.left + 250 + j * 200, menu_rect.top + 80 + i * 80))

            # Отрисовка кнопки "Начать игру"
            start_button = Button(menu_rect.centerx - 5, menu_rect.bottom - 70, 200, 50, "Начать игру")
            start_button.draw(screen)

            # Отрисовка кнопки "Назад"
            back_button = Button(menu_rect.centerx - 240, menu_rect.bottom - 70, 200, 50, "Назад")
            back_button.draw(screen)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if start_button.rect.collidepoint(mouse_pos):
                        start_new_game = True
                        selecting = False
                    elif back_button.rect.collidepoint(mouse_pos):
                        # Восстанавливаем сохраненное состояние игры
                        self.pieces = saved_state['pieces']
                        self.captured_pieces = saved_state['captured_pieces']
                        self.moves_history = saved_state['moves_history']
                        current_turn = saved_state['current_turn']
                        self.game_over = saved_state['game_over']
                        selecting = False
                    else:
                        for i, (option, values) in enumerate(options.items()):
                            for j, value in enumerate(values):
                                value_rect = pygame.Rect(menu_rect.left + 200 + j * 150, menu_rect.top + 80 + i * 80,
                                                         150, 40)
                                if value_rect.collidepoint(mouse_pos):
                                    selected_options[option] = j

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Восстанавливаем сохраненное состояние игры
                        self.pieces = saved_state['pieces']
                        self.captured_pieces = saved_state['captured_pieces']
                        self.moves_history = saved_state['moves_history']
                        current_turn = saved_state['current_turn']
                        self.game_over = saved_state['game_over']
                        selecting = False

        if start_new_game:
            self.clear_board()  # Очищаем доску перед началом новой игры
            if selected_options["Набор фигур:"] == 0:
                self.pieces = self.setup_pieces("king_queen",
                                                "white" if selected_options["Сторона:"] == 0 else "black")
            else:
                self.pieces = self.setup_pieces("king_rook_pawns",
                                                "white" if selected_options["Сторона:"] == 0 else "black")
            self.moves_history = []  # Стираем историю ходов
            self.current_save = None  # Удаляем текущее сохранение
            self.captured_pieces = []  # Удаляем съеденные фигуры
            self.game_over = False  # Сбрасываем состояние конца игры
            current_turn = "white"  # Сбрасываем ход

def main():
    board = ChessBoard()

    while True:
        screen.fill((255, 255, 255))
        board.handle_events()
        board.draw(screen)
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
