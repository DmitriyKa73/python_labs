import pygame
import sys
import json
import os
import random
import hashlib
import textwrap

pygame.init()
info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h
tile_size = min(screen_width, screen_height) // 9
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Шахматный эндшпиль")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

background = pygame.image.load("assets/background.jpg")
background = pygame.transform.scale(background, (screen_width, screen_height))

# Load sound
move_sound = pygame.mixer.Sound("assets/soundChess.mp3")
move_sound.set_volume(0.5)  \

def load_images():
    pieces = {}
    for color in ["black", "white"]:
        for piece in ["king", "queen", "rook", "pawn", "bishop", "knight"]:
            image = pygame.image.load(f"assets/{color}_{piece}.png").convert_alpha()
            pieces[f"{color}_{piece}"] = pygame.transform.scale(image, (tile_size, tile_size))
            pieces[f"{color}_{piece}_small"] = pygame.transform.scale(image, (tile_size // 2, tile_size // 2))
    return pieces

board_color_1 = (235, 235, 208)
board_color_2 = (92, 86, 83)
highlight_color = (186, 202, 68)
button_color = (70, 130, 180)
button_hover_color = (100, 149, 237)
selected_piece = None
current_turn = "white"

pieces = load_images()
is_authenticated = False
play_against_pc = False
player_color = "white"
current_user = None

class Button:
    def __init__(self, x, y, width, height, text, color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        self.custom_color = color
        self.disabled = False

    def draw(self, screen):
        if self.custom_color:
            color = self.custom_color
        else:
            color = button_hover_color if self.is_hovered else button_color
        if self.disabled:
            color = (169, 169, 169)
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (50, 50, 50), self.rect, 2, border_radius=10)

        text_shadow = font.render(self.text, True, (0, 0, 0))
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_shadow, (text_rect.x + 2, text_rect.y + 2))
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if self.disabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

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
        self.valid_moves = []  # список для хранения возможных ходов
        self.captured_pieces = []  # список для хранения съеденных фигур
        self.game_over = False  # переменная для отслеживания конца игры
        self.piece_values = {
            'king': 10000,
            'queen': 90,
            'rook': 50,
            'bishop': 35,
            'knight': 32,
            'pawn': 10
        }
        self.transposition_table = {}

        button_width = 200
        button_height = 50
        container_width = 300
        button_x = self.board_offset_x - container_width - 50 + (container_width - button_width) // 2
        button_spacing = 20

        container_height = 700
        total_buttons_height = (button_height + button_spacing) * 6 - button_spacing
        start_y = (container_height - total_buttons_height) // 2 + 200

        self.buttons = {
            'login': Button(button_x, start_y, button_width, button_height, "Авторизация"),
            'new_game': Button(button_x, start_y + button_height + button_spacing, button_width, button_height,
                               "Новая игра"),
            'save_game': Button(button_x, start_y + (button_height + button_spacing) * 2, button_width, button_height,
                                "Сохранить игру"),
            'load_game': Button(button_x, start_y + (button_height + button_spacing) * 3, button_width, button_height,
                                "Загрузить игру"),
            'instructions': Button(button_x, start_y + (button_height + button_spacing) * 4, button_width,
                                   button_height,
                                   "Инструкция"),
            'exit': Button(button_x, start_y + (button_height + button_spacing) * 5, button_width, button_height,
                           "Выход из игры")
        }
    def setup_pieces(self, piece_set, color):
        pieces = {}
        positions = [(x, y) for x in range(8) for y in range(8)]
        random.shuffle(positions)

        def get_random_position():
            while positions:
                pos = positions.pop()
                if pos[1] not in [0, 7]:  # условие для исключения крайних верхних и нижних клеток для пешек
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

        while True:
            positions = [(x, y) for x in range(8) for y in range(8)]
            random.shuffle(positions)
            pieces = create_pieces()
            self.pieces = pieces

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
        if king_pos is None:
            return False
        for piece in self.pieces.values():
            if piece.color != color:
                if piece.type == "knight":
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

        pieces_list = list(self.pieces.values())
        for piece in pieces_list:
            if piece.color == color:
                valid_moves = self.get_valid_moves(piece)
                for move in valid_moves:
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

                    still_in_check = self.is_check(color)

                    piece.move_to(original_pos)
                    if captured_piece and captured_key:
                        self.pieces[captured_key] = captured_piece

                    if not still_in_check:
                        return False
        return True

    def is_stalemate(self, color):
        if self.is_check(color):
            return False

        pieces_list = list(self.pieces.values())
        for piece in pieces_list:
            if piece.color == color:
                valid_moves = self.get_valid_moves(piece)
                for move in valid_moves:
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

                    legal_move = not self.is_check(color)

                    piece.move_to(original_pos)
                    if captured_piece and captured_key:
                        self.pieces[captured_key] = captured_piece

                    if legal_move:
                        return False
        return True

    def draw(self, screen):
        screen.blit(background, (0, 0))

        for row in range(8):
            for col in range(8):
                color = board_color_1 if (row + col) % 2 == 0 else board_color_2
                pygame.draw.rect(screen, color,
                                 pygame.Rect(self.board_offset_x + col * tile_size,
                                             self.board_offset_y + row * tile_size,
                                             tile_size, tile_size))

        for piece in self.pieces.values():
            piece.draw(screen)

        if selected_piece:
            valid_moves = self.get_valid_moves(selected_piece)
            for move in valid_moves:
                target_piece = self.get_piece_at(move)
                if target_piece and target_piece.color != selected_piece.color:
                    pygame.draw.circle(screen, (255, 165, 0),
                                       (self.board_offset_x + move[0] * tile_size + tile_size // 2,
                                        self.board_offset_y + move[1] * tile_size + tile_size // 2),
                                       10)
                else:
                    pygame.draw.circle(screen, highlight_color,
                                       (self.board_offset_x + move[0] * tile_size + tile_size // 2,
                                        self.board_offset_y + move[1] * tile_size + tile_size // 2),
                                       10)

        for i in range(8):
            pygame.draw.rect(screen, (26, 7, 4),
                             (self.board_offset_x - 30, self.board_offset_y + i * tile_size, 30, tile_size))
            text = font.render(str(8 - i), True, (255, 255, 255))
            screen.blit(text, (self.board_offset_x - 25, self.board_offset_y + i * tile_size + tile_size // 3))

            pygame.draw.rect(screen, (26, 7, 4),
                             (self.board_offset_x - 30 + i * tile_size, self.board_offset_y + 8 * tile_size,
                              tile_size + 30, 30))
            text = font.render(chr(97 + i), True, (255, 255, 255))
            screen.blit(text, (
                self.board_offset_x + i * tile_size + tile_size // 3, self.board_offset_y + 8 * tile_size + 5))

            pygame.draw.rect(screen, (26, 7, 4),
                             (self.board_offset_x - 30, self.board_offset_y - 30, 8 * tile_size + 60, 30))

            pygame.draw.rect(screen, (26, 7, 4),
                             (self.board_offset_x + 8 * tile_size, self.board_offset_y - 30, 30, 8 * tile_size + 60))

        if self.message and self.message_timer > 0:
            message_surface = pygame.Surface((screen_width, 100), pygame.SRCALPHA)
            message_surface.fill((0, 0, 0, 128))

            text_shadow = font.render(self.message, True, (0, 0, 0))
            text_surface = font.render(self.message, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(screen_width // 2, 50))
            message_surface.blit(text_shadow, (text_rect.x + 4, text_rect.y + 4))
            message_surface.blit(text_surface, text_rect)

            screen.blit(message_surface, (0, 0))
            self.message_timer -= 1

        container_width = 300
        container_height = screen_height - 400
        buttons_x = self.board_offset_x - container_width - 50
        buttons_y = 170
        moves_x = self.board_offset_x + 8 * tile_size + 50
        moves_y = 170

        pygame.draw.rect(screen, (235, 235, 208),
                         (buttons_x, buttons_y, container_width, container_height))
        pygame.draw.rect(screen, (26, 7, 4),
                         (buttons_x, buttons_y, container_width, container_height), 6)

        title_font = pygame.font.Font(None, 52)
        title_text_1 = title_font.render("Шахматный", True, (0, 0, 0))
        title_text_2 = title_font.render("эндшпиль", True, (0, 0, 0))

        title_rect_1 = title_text_1.get_rect(center=(buttons_x + container_width // 2, buttons_y + 70))
        title_rect_2 = title_text_2.get_rect(center=(buttons_x + container_width // 2, buttons_y + 115))

        shadow_offset = 2
        shadow_color = (150, 150, 150)

        shadow_rect_1 = title_rect_1.copy()
        shadow_rect_1.center = (title_rect_1.centerx + shadow_offset, title_rect_1.centery + shadow_offset)
        screen.blit(title_font.render("Шахматный", True, shadow_color), shadow_rect_1)

        shadow_rect_2 = title_rect_2.copy()
        shadow_rect_2.center = (title_rect_2.centerx + shadow_offset, title_rect_2.centery + shadow_offset)
        screen.blit(title_font.render("эндшпиль", True, shadow_color), shadow_rect_2)

        screen.blit(title_text_1, title_rect_1)
        screen.blit(title_text_2, title_rect_2)

        for button in self.buttons.values():
            button.draw(screen)

        pygame.draw.rect(screen, (235, 235, 208),
                         (moves_x, moves_y, container_width, container_height))
        pygame.draw.rect(screen, (26, 7, 4),
                         (moves_x, moves_y, container_width, container_height), 6)

        if self.current_save:
            save_text = font.render("Текущее сохра��ение:", True, (0, 0, 0))
            screen.blit(save_text, (moves_x + 10, moves_y + 10))
            save_name = font.render(f"{self.current_save}", True, (0, 0, 0))
            screen.blit(save_name, (moves_x + 10, moves_y + 40))
            turn_text = font.render(
                f"Ход {'белых' if current_turn == 'white' else 'черных'}",
                True, (0, 0, 0))
            screen.blit(turn_text, (moves_x + 10, moves_y + 80))

        elif not self.game_over:
            if not self.pieces:
                turn_text = font.render("Добро пожаловать!", True, (0, 0, 0))
            else:
                turn_text = font.render(
                    f"Ход {'белых' if current_turn == 'white' else 'черных'}",
                    True, (0, 0, 0))
            screen.blit(turn_text, (moves_x + 10, moves_y + 80))
        else:
            turn_text = font.render("Конец игры!", True, (0, 0, 0))
            screen.blit(turn_text, (moves_x + 10, moves_y + 80))

        history_text = font.render("История ходов:", True, (0, 0, 0))
        screen.blit(history_text, (moves_x + 10, moves_y + 120))

        visible_moves = 11
        start_index = max(0, len(self.moves_history) - visible_moves)

        for i, move in enumerate(self.moves_history[start_index:]):
            move_number = start_index + i + 1
            move_text = font.render(f"{move_number}. {move}", True, (0, 0, 0))
            screen.blit(move_text, (moves_x + 10, moves_y + 160 + i * 30))

        small_piece_size = tile_size // 2
        captured_x = moves_x + 10
        captured_y = moves_y + container_height - small_piece_size * 2 - 20

        captured_text = font.render("Съеденные фигуры:", True, (0, 0, 0))
        screen.blit(captured_text, (captured_x, captured_y - 30))

        white_captured = [p for p in self.captured_pieces if p.color == "white"]
        black_captured = [p for p in self.captured_pieces if p.color == "black"]

        for i, piece in enumerate(black_captured):
            if i < 8:
                x = captured_x + i * small_piece_size
                y = captured_y
                small_image = pieces[f"{piece.color}_{piece.type}_small"]
                screen.blit(small_image, (x, y))

        for i, piece in enumerate(white_captured):
            if i < 8:
                x = captured_x + i * small_piece_size
                y = captured_y + small_piece_size
                small_image = pieces[f"{piece.color}_{piece.type}_small"]
                screen.blit(small_image, (x, y))

    def promote_pawn(self, pawn):
        # Создание поверхности для меню выбора фигуры
        menu_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for i in range(screen_height):
            alpha = min(128, i // 16)
            pygame.draw.line(menu_surface, (70, 130, 180, alpha), (0, i), (screen_width, i))

        menu_width = 800
        menu_height = 300
        menu_rect = pygame.Rect((screen_width - menu_width) // 2,
                                (screen_height - menu_height) // 2,
                                menu_width, menu_height)

        piece_types = ["queen", "rook", "bishop", "knight"]
        piece_rects = []
        piece_size = tile_size
        spacing = 20
        total_width = len(piece_types) * piece_size + (len(piece_types) - 1) * spacing
        start_x = menu_rect.centerx - total_width // 2 + 70

        for i, piece_type in enumerate(piece_types):
            piece_image = pieces[f"{pawn.color}_{piece_type}"]
            piece_rect = piece_image.get_rect()
            piece_rect.centerx = start_x + i * (piece_size + spacing)
            piece_rect.centery = menu_rect.centery
            piece_rects.append((piece_rect, piece_type))

        selecting = True
        while selecting:
            screen.blit(background, (0, 0))
            screen.blit(menu_surface, (0, 0))

            pygame.draw.rect(screen, (235, 235, 208), menu_rect)
            pygame.draw.rect(screen, (26, 7, 4), menu_rect, 6)

            title = font.render("Выберите фигуру для превращения:", True, (0, 0, 0))
            title_rect = title.get_rect(center=(screen_width // 2, menu_rect.top + 30))
            screen.blit(title, title_rect)

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
        user_save_dir = os.path.join('saves', current_user)
        existing_saves = [f for f in os.listdir(user_save_dir) if f.startswith('save') and f.endswith('.json')]
        if not existing_saves:
            return 1
        numbers = [int(f.replace('save', '').replace('.json', '')) for f in existing_saves]
        max_number = max(numbers)
        next_number = max_number + 1 if max_number < 9 else 1
        return next_number

    def delete_all_saves(self):
        user_save_dir = os.path.join('saves', current_user)
        saves = [f for f in os.listdir(user_save_dir) if f.startswith('save') and f.endswith('.json')]
        for save in saves:
            os.remove(os.path.join(user_save_dir, save))
        self.current_save = None
        self.show_message("Все сохранения удалены!")

    def save_game(self):
        if not self.pieces or self.game_over:
            self.show_message("Нечего сохранять!")
            return

        user_save_dir = os.path.join('saves', current_user)
        if not os.path.exists(user_save_dir):
            os.makedirs(user_save_dir)

        save_number = self.get_next_save_number()
        filename = os.path.join(user_save_dir, f'save{save_number}.json')
        game_state = {
            'pieces': [(p.color, p.type, p.position) for p in self.pieces.values()],
            'moves_history': self.moves_history,
            'current_turn': current_turn,
            'captured_pieces': [(p.color, p.type) for p in self.captured_pieces],
            'play_against_pc': play_against_pc,
            'player_color': player_color
        }
        with open(filename, 'w') as f:
            json.dump(game_state, f)
        self.current_save = filename
        if save_number < 9:
            self.show_message(f"Игра сохранена как {filename}!")
        else:
            self.show_message(f"Сохранено в {filename} Дальнейшие сохранения будут в save1.json. Очистите память")

    def load_game(self):
        user_save_dir = os.path.join('saves', current_user)
        saves = [f for f in os.listdir(user_save_dir) if f.startswith('save') and f.endswith('.json')]
        if not saves:
            self.show_message("Нет доступных сохранений!")
            return

        menu_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for i in range(screen_height):
            alpha = min(128, i // 16)
            pygame.draw.line(menu_surface, (70, 130, 180, alpha), (0, i), (screen_width, i))

        menu_width = 400
        menu_height = len(saves) * 60 + 220
        menu_rect = pygame.Rect((screen_width - menu_width) // 2,
                                (screen_height - menu_height) // 2,
                                menu_width, menu_height)

        pygame.draw.rect(menu_surface, (235, 235, 208), menu_rect)
        pygame.draw.rect(menu_surface, (26, 7, 4), menu_rect, 6)

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

        back_button = Button(menu_rect.centerx - 100,
                             start_y + len(saves) * (button_height + button_spacing),
                             200, button_height, "Назад")

        delete_button = Button(menu_rect.centerx - 150,
                               start_y + len(saves) * (button_height + button_spacing) + button_height + button_spacing,
                               300, button_height, "Удалить все сохранения", (255, 0, 0))

        selecting = True
        while selecting:
            screen.blit(background, (0, 0))
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
                                with open(os.path.join(user_save_dir, save_file), 'r') as f:
                                    game_state = json.load(f)
                                self.pieces = {}
                                for color, type, position in game_state['pieces']:
                                    piece_key = f"{color}_{type}"
                                    if len([p for p in self.pieces.values() if
                                            p.type == type and p.color == color]) > 0:
                                        piece_key += f"_{len([p for p in self.pieces.values() if p.type == type and p.color == color]) + 1}"
                                    self.pieces[piece_key] = Piece(color, type, tuple(position))
                                self.moves_history = game_state['moves_history']
                                global current_turn, play_against_pc, player_color
                                current_turn = game_state.get('current_turn', 'white')
                                play_against_pc = game_state.get('play_against_pc',
                                                                 False)  # Загружаем режим игры против ПК
                                player_color = game_state.get('player_color', 'white')  # Загружаем цвет игрока
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
                        self.captured_pieces.append(clicked_piece)

                # Автоматическое превращение пешки бота в ферзя
                if selected_piece.type == "pawn":
                    if (selected_piece.color == "white" and clicked_pos[1] == 0) or \
                            (selected_piece.color == "black" and clicked_pos[1] == 7):
                        if play_against_pc and current_turn != player_color:
                            selected_piece.type = "queen"
                            selected_piece.image = pieces[f"{selected_piece.color}_queen"]
                        else:
                            self.promote_pawn(selected_piece)

                self.add_move_to_history(selected_piece, start_pos, clicked_pos, captured)
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
                move_sound.play()

                pieces_backup = self.pieces.copy()
                captured_backup = self.captured_pieces.copy()

                if play_against_pc and current_turn != player_color and not self.game_over:
                    best_move = self.get_best_move(2, current_turn)
                    if best_move and isinstance(best_move, tuple) and len(best_move) == 2:
                        piece, move = best_move
                        if isinstance(piece, Piece):
                            self.handle_click((self.board_offset_x + piece.position[0] * tile_size + tile_size // 2,
                                               self.board_offset_y + piece.position[1] * tile_size + tile_size // 2))
            else:
                self.show_message("Некорректный ход!")
                selected_piece = None
                self.valid_moves = []
        elif clicked_piece and clicked_piece.color == current_turn:
            selected_piece = clicked_piece
            self.valid_moves = self.get_valid_moves(selected_piece)

        if len(self.pieces) == 2 and all(piece.type == "king" for piece in self.pieces.values()):
            self.show_message("Пат! Ничья!")
            self.game_over = True

    def handle_events(self):
        global selected_piece, current_turn, is_authenticated, play_against_pc, player_color
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                for button_name, button in self.buttons.items():
                    if button.handle_event(event):
                        if button_name == 'login':
                            self.show_login_menu()
                            selected_piece = None
                        elif button_name == 'new_game' and is_authenticated:
                            self.show_new_game_menu()
                            selected_piece = None
                        elif button_name == 'new_game' and not is_authenticated:
                            self.show_message("Для начала новой игры, пожалуйста, авторизуйтесь!")
                        elif button_name == 'save_game' and is_authenticated:
                            self.save_game()
                        elif button_name == 'save_game' and not is_authenticated:
                            self.show_message("Нечего сохранять!")
                        elif button_name == 'load_game' and is_authenticated:
                            self.load_game()
                            selected_piece = None
                        elif button_name == 'load_game' and not is_authenticated:
                            self.show_message("Для загрузки игры, пожалуйста, авторизуйтесь!")
                        elif button_name == 'instructions':
                            self.show_instructions()
                        elif button_name == 'exit':
                            pygame.quit()
                            sys.exit()
                        return

                self.handle_click(mouse_pos)

            elif event.type == pygame.MOUSEMOTION:
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
            ("", "assets/first_page.jpg"),
            ("", "assets/second_page.jpg"),
            ("", "assets/third_page.jpg"),
            ("", "assets/fourth_page.jpg"),
            ("", "assets/fifth_page.jpg"),
            ("", "assets/sixth_page.jpg"),
            ("", "assets/seventh_page.jpg"),
        ]

        instruction_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for i in range(screen_height):
            alpha = min(128, i // 16)
            pygame.draw.line(instruction_surface, (70, 130, 180, alpha), (0, i), (screen_width, i))

        container_width = 900
        container_height = screen_height - 100
        container_rect = pygame.Rect((screen_width - container_width) // 2,
                                    50,
                                    container_width, container_height)

        current_index = 0
        showing_instructions = True
        while showing_instructions:
            screen.blit(background, (0, 0))
            screen.blit(instruction_surface, (0, 0))

            pygame.draw.rect(screen, (236,233,218), container_rect)
            pygame.draw.rect(screen, (26, 7, 4), container_rect, 6)

            title_font = pygame.font.Font(None, 52)
            title_text = title_font.render("Инструкция к игре", True, (0, 0, 0))
            title_rect = title_text.get_rect(center=(container_rect.centerx, container_rect.top + 40))
            screen.blit(title_text, title_rect)

            text, image_path = instructions[current_index]

            wrapped_text = textwrap.fill(text, width=70)  # 70 - количество символов в строке

            if image_path:
                image = pygame.image.load(image_path).convert_alpha()
                image_width = container_width - 40  # Отступы по 20 пикселей с каждой стороны в инструкции
                image_height = int(image.get_height() * (image_width / image.get_width()))
                image = pygame.transform.scale(image, (image_width, image_height))
                screen.blit(image, (container_rect.left + 20, container_rect.top + 100))
                text_y_position = container_rect.top + 120 + image_height
            else:
                text_y_position = container_rect.top + 100

            for i, line in enumerate(wrapped_text.split('\n')):
                text_surface = font.render(line, True, (0, 0, 0))
                screen.blit(text_surface, (container_rect.left + 20, text_y_position + i * 30))

            # Пагинация
            page_text = f"{current_index + 1}/{len(instructions)}"
            page_surface = font.render(page_text, True, (0, 0, 0))
            page_rect = page_surface.get_rect(center=(container_rect.centerx, container_rect.bottom - 30))
            screen.blit(page_surface, page_rect)

            # Отрисовка кнопок навигации
            left_button = pygame.Rect(container_rect.left + 20, container_rect.bottom - 60, 50, 40)
            right_button = pygame.Rect(container_rect.right - 70, container_rect.bottom - 60, 50, 40)
            pygame.draw.rect(screen, (70, 130, 180), left_button)
            pygame.draw.rect(screen, (70, 130, 180), right_button)

            left_text = font.render("<", True, (255, 255, 255))
            right_text = font.render(">", True, (255, 255, 255))
            screen.blit(left_text, left_button.move(15, 5))
            screen.blit(right_text, right_button.move(15, 5))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if left_button.collidepoint(event.pos):
                        current_index = (current_index - 1) % len(instructions)
                    elif right_button.collidepoint(event.pos):
                        current_index = (current_index + 1) % len(instructions)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        current_index = (current_index - 1) % len(instructions)
                    elif event.key == pygame.K_RIGHT:
                        current_index = (current_index + 1) % len(instructions)
                    elif event.key == pygame.K_ESCAPE:
                        showing_instructions = False

    def show_new_game_menu(self):
        global current_turn, play_against_pc, player_color
        saved_state = {
            'pieces': self.pieces.copy(),
            'captured_pieces': self.captured_pieces.copy(),
            'moves_history': self.moves_history.copy(),
            'current_turn': current_turn,
            'game_over': self.game_over
        }

        menu_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for i in range(screen_height):
            alpha = min(128, i // 16)
            pygame.draw.line(menu_surface, (70, 130, 180, alpha), (0, i), (screen_width, i))

        menu_width = 800
        menu_height = 400
        menu_rect = pygame.Rect((screen_width - menu_width) // 2,
                                (screen_height - menu_height) // 2,
                                menu_width, menu_height)

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
            screen.blit(background, (0, 0))
            screen.blit(menu_surface, (0, 0))

            pygame.draw.rect(screen, (235, 235, 208), menu_rect)
            pygame.draw.rect(screen, (100, 100, 100), menu_rect, 2)

            title = font.render("Настройки новой игры", True, (0, 0, 0))
            title_rect = title.get_rect(center=(screen_width // 2, menu_rect.top + 30))
            screen.blit(title, title_rect)

            for i, (option, values) in enumerate(options.items()):
                option_text = font.render(option, True, (0, 0, 0))
                screen.blit(option_text, (menu_rect.left + 50, menu_rect.top + 80 + i * 80))

                for j, value in enumerate(values):
                    value_text = font.render(value, True, (0, 0, 0) if selected_options[option] != j else (255, 0, 0))
                    screen.blit(value_text, (menu_rect.left + 250 + j * 200, menu_rect.top + 80 + i * 80))

            start_button = Button(menu_rect.centerx - 5, menu_rect.bottom - 70, 200, 50, "Начать игру")
            start_button.draw(screen)

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
                        self.pieces = saved_state['pieces']
                        self.captured_pieces = saved_state['captured_pieces']
                        self.moves_history = saved_state['moves_history']
                        current_turn = saved_state['current_turn']
                        self.game_over = saved_state['game_over']
                        selecting = False

        if start_new_game:
            self.clear_board()
            if selected_options["Набор фигур:"] == 0:
                self.pieces = self.setup_pieces("king_queen",
                                                "white" if selected_options["Сторона:"] == 0 else "black")
            else:
                self.pieces = self.setup_pieces("king_rook_pawns",
                                                "white" if selected_options["Сторона:"] == 0 else "black")
            self.moves_history = []
            self.current_save = None
            self.captured_pieces = []
            self.game_over = False
            current_turn = "white"
            global play_against_pc
            play_against_pc = selected_options["Противник:"] == 1
            player_color = "white" if selected_options["Сторона:"] == 0 else "black"

    def show_login_menu(self):
        global is_authenticated, current_user
        menu_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for i in range(screen_height):
            alpha = min(128, i // 16)
            pygame.draw.line(menu_surface, (70, 130, 180, alpha), (0, i), (screen_width, i))

        menu_width = 500
        menu_height = 400
        menu_rect = pygame.Rect((screen_width - menu_width) // 2,
                                (screen_height - menu_height) // 2,
                                menu_width, menu_height)

        pygame.draw.rect(menu_surface, (235, 235, 208), menu_rect)
        pygame.draw.rect(menu_surface, (26, 7, 4), menu_rect, 6)

        title = font.render("Авторизация", True, (0, 0, 0))
        title_rect = title.get_rect(center=(screen_width // 2, menu_rect.top + 30))

        username_input = ""
        password_input = ""
        active_input = None

        login_button = Button(menu_rect.centerx - 125, menu_rect.bottom - 190, 250, 50, "Войти")
        register_button = Button(menu_rect.centerx - 125, menu_rect.bottom - 130, 250, 50, "Регистрация")
        back_button = Button(menu_rect.centerx - 125, menu_rect.bottom - 70, 250, 50, "Назад")

        selecting = True
        message = ""
        message_timer = 0
        while selecting:
            screen.blit(background, (0, 0))
            screen.blit(menu_surface, (0, 0))
            screen.blit(title, title_rect)

            username_text = font.render("Никнейм:", True, (0, 0, 0))
            screen.blit(username_text, (menu_rect.left + 20, menu_rect.top + 80))
            username_input_rect = pygame.Rect(menu_rect.left + 150, menu_rect.top + 80, 300, 30)
            pygame.draw.rect(screen, (255, 255, 255), username_input_rect)
            pygame.draw.rect(screen, (0, 0, 0), username_input_rect, 2)
            username_surface = font.render(username_input + ('|' if active_input == "username" else ''), True,
                                           (0, 0, 0))
            screen.blit(username_surface, (username_input_rect.x + 5, username_input_rect.y + 5))

            password_text = font.render("Пароль:", True, (0, 0, 0))
            screen.blit(password_text, (menu_rect.left + 20, menu_rect.top + 130))
            password_input_rect = pygame.Rect(menu_rect.left + 150, menu_rect.top + 130, 300, 30)
            pygame.draw.rect(screen, (255, 255, 255), password_input_rect)
            pygame.draw.rect(screen, (0, 0, 0), password_input_rect, 2)
            password_surface = font.render("*" * len(password_input) + ('|' if active_input == "password" else ''),
                                           True, (0, 0, 0))
            screen.blit(password_surface, (password_input_rect.x + 5, password_input_rect.y + 5))

            login_button.draw(screen)
            register_button.draw(screen)
            back_button.draw(screen)

            if message and message_timer > 0:
                message_surface = pygame.Surface((screen_width, 100), pygame.SRCALPHA)
                message_surface.fill((0, 0, 0, 128))
                text_shadow = font.render(message, True, (0, 0, 0))
                text_surface = font.render(message, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(screen_width // 2, 50))
                screen.blit(message_surface, (0, 0))
                screen.blit(text_shadow, (text_rect.x + 2, text_rect.y + 2))
                screen.blit(text_surface, text_rect)
                message_timer -= 1

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if username_input_rect.collidepoint(event.pos):
                        active_input = "username"
                    elif password_input_rect.collidepoint(event.pos):
                        active_input = "password"
                    elif login_button.rect.collidepoint(event.pos):
                        if self.authenticate(username_input, password_input):
                            is_authenticated = True
                            current_user = username_input
                            self.buttons['login'].disabled = True
                            self.message = f"Добрый день, {username_input}!"
                            self.message_timer = 180
                            selecting = False
                        else:
                            message = "Неверный логин или пароль!"
                            message_timer = 180
                    elif register_button.rect.collidepoint(event.pos):
                        self.show_register_menu()
                        selecting = False
                    elif back_button.rect.collidepoint(event.pos):
                        selecting = False
                elif event.type == pygame.KEYDOWN:
                    if active_input == "username":
                        if event.key == pygame.K_BACKSPACE:
                            username_input = username_input[:-1]
                        elif event.key not in [pygame.K_ESCAPE, pygame.K_TAB, pygame.K_DELETE, pygame.K_SPACE] and len(username_input) < 16:
                            username_input += event.unicode
                    elif active_input == "password":
                        if event.key == pygame.K_BACKSPACE:
                            password_input = password_input[:-1]
                        elif event.key not in [pygame.K_ESCAPE, pygame.K_TAB, pygame.K_DELETE, pygame.K_SPACE] and len(password_input) < 16:
                            password_input += event.unicode

    def show_register_menu(self):
        menu_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for i in range(screen_height):
            alpha = min(128, i // 16)
            pygame.draw.line(menu_surface, (70, 130, 180, alpha), (0, i), (screen_width, i))

        menu_width = 500
        menu_height = 400
        menu_rect = pygame.Rect((screen_width - menu_width) // 2,
                                (screen_height - menu_height) // 2,
                                menu_width, menu_height)

        pygame.draw.rect(menu_surface, (235, 235, 208), menu_rect)
        pygame.draw.rect(menu_surface, (26, 7, 4), menu_rect, 6)

        title = font.render("Регистрация", True, (0, 0, 0))
        title_rect = title.get_rect(center=(screen_width // 2, menu_rect.top + 30))

        username_input = ""
        password_input = ""
        active_input = None

        register_button = Button(menu_rect.centerx - 125, menu_rect.bottom - 130, 250, 50, "Зарегистрироваться")
        back_button = Button(menu_rect.centerx - 125, menu_rect.bottom - 70, 250, 50, "Назад")

        selecting = True
        message = ""
        message_timer = 0
        while selecting:
            screen.blit(background, (0, 0))
            screen.blit(menu_surface, (0, 0))
            screen.blit(title, title_rect)

            username_text = font.render("Никнейм:", True, (0, 0, 0))
            screen.blit(username_text, (menu_rect.left + 20, menu_rect.top + 80))
            username_input_rect = pygame.Rect(menu_rect.left + 150, menu_rect.top + 80, 300, 30)
            pygame.draw.rect(screen, (255, 255, 255), username_input_rect)
            pygame.draw.rect(screen, (0, 0, 0), username_input_rect, 2)
            username_surface = font.render(username_input + ('|' if active_input == "username" else ''), True,
                                           (0, 0, 0))
            screen.blit(username_surface, (username_input_rect.x + 5, username_input_rect.y + 5))

            password_text = font.render("Пароль:", True, (0, 0, 0))
            screen.blit(password_text, (menu_rect.left + 20, menu_rect.top + 130))
            password_input_rect = pygame.Rect(menu_rect.left + 150, menu_rect.top + 130, 300, 30)
            pygame.draw.rect(screen, (255, 255, 255), password_input_rect)
            pygame.draw.rect(screen, (0, 0, 0), password_input_rect, 2)
            password_surface = font.render("*" * len(password_input) + ('|' if active_input == "password" else ''),
                                           True, (0, 0, 0))
            screen.blit(password_surface, (password_input_rect.x + 5, password_input_rect.y + 5))

            register_button.draw(screen)
            back_button.draw(screen)

            if message and message_timer > 0:
                message_surface = pygame.Surface((screen_width, 100), pygame.SRCALPHA)
                message_surface.fill((0, 0, 0, 128))
                text_shadow = font.render(message, True, (0, 0, 0))
                text_surface = font.render(message, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(screen_width // 2, 50))
                screen.blit(message_surface, (0, 0))
                screen.blit(text_shadow, (text_rect.x + 2, text_rect.y + 2))
                screen.blit(text_surface, text_rect)
                message_timer -= 1

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if username_input_rect.collidepoint(event.pos):
                        active_input = "username"
                    elif password_input_rect.collidepoint(event.pos):
                        active_input = "password"
                    elif register_button.rect.collidepoint(event.pos):
                        if len(username_input) < 5:
                            message = "Никнейм должен содержать минимум 5 символ��в!"
                            message_timer = 180
                        elif len(password_input) < 5:
                            message = "Пароль должен содержать минимум 5 символов!"
                            message_timer = 180
                        elif self.is_username_taken(username_input):
                            message = "Данный пользователь уже зарегистрирован"
                            message_timer = 180
                        else:
                            self.register(username_input, password_input)
                            self.show_message(f"Добро пожаловать, {username_input}! Пожалуйста, авторизуйтесь!", 180)
                            selecting = False
                    elif back_button.rect.collidepoint(event.pos):
                        selecting = False
                elif event.type == pygame.KEYDOWN:
                    if active_input == "username":
                        if event.key == pygame.K_BACKSPACE:
                            username_input = username_input[:-1]
                        elif event.key not in [pygame.K_ESCAPE, pygame.K_TAB, pygame.K_DELETE, pygame.K_SPACE] and len(username_input) < 16:
                            username_input += event.unicode
                    elif active_input == "password":
                        if event.key == pygame.K_BACKSPACE:
                            password_input = password_input[:-1]
                        elif event.key not in [pygame.K_ESCAPE, pygame.K_TAB, pygame.K_DELETE, pygame.K_SPACE] and len(password_input) < 16:
                            password_input += event.unicode

    def authenticate(self, username, password):
        try:
            with open('users.json', 'r') as f:
                users = json.load(f)
            if username in users:
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                return users[username]['password'] == hashed_password
        except FileNotFoundError:
            return False
        except json.JSONDecodeError:
            return False
        return False

    def is_username_taken(self, username):
        try:
            with open('users.json', 'r') as f:
                users = json.load(f)
            return username in users
        except FileNotFoundError:
            return False
        except json.JSONDecodeError:
            return False

    def register(self, username, password):
        try:
            with open('users.json', 'r') as f:
                users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            users = {}

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        users[username] = {'password': hashed_password}

        with open('users.json', 'w') as f:
            json.dump(users, f)

        # Create user save directory
        user_save_dir = os.path.join('saves', username)
        if not os.path.exists(user_save_dir):
            os.makedirs(user_save_dir)

    def draw_message(self, screen):
        if self.message and self.message_timer > 0:
            message_surface = pygame.Surface((screen_width, 100), pygame.SRCALPHA)
            message_surface.fill((0, 0, 0, 128))
            text_shadow = font.render(self.message, True, (0, 0, 0))
            text_surface = font.render(self.message, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(screen_width // 2, 50))
            message_surface.blit(text_shadow, (text_rect.x + 4, text_rect.y + 4))
            message_surface.blit(text_surface, text_rect)
            screen.blit(message_surface, (0, 0))
            self.message_timer -= 1

    def evaluate_board(self):
        score = 0

        white_pawns = len([p for p in self.pieces.values() if p.type == 'pawn' and p.color == 'white'])
        black_pawns = len([p for p in self.pieces.values() if p.type == 'pawn' and p.color == 'black'])

        for piece in list(self.pieces.values()):
            value = self.piece_values[piece.type]

            # Приоритет развития пешек в начале игры
            if piece.type == 'pawn':
                if (white_pawns > 0 and piece.color == 'white') or (black_pawns > 0 and piece.color == 'black'):
                    value *= 2  # ценность пешек

                    if 2 <= piece.position[0] <= 5:
                        if piece.color == 'white' and piece.position[1] > 4:
                            value *= 1.5
                        elif piece.color == 'black' and piece.position[1] < 3:
                            value *= 1.5

            if piece.type != 'king':
                for enemy in list(self.pieces.values()):
                    if enemy.color != piece.color and enemy.type == 'king':
                        dist = abs(enemy.position[0] - piece.position[0]) + abs(enemy.position[1] - piece.position[1])
                        if dist <= 2:
                            value *= 3.0
                        elif dist <= 4:
                            value *= 1.5

            if piece.type == 'king':
                protectors = sum(1 for p in self.pieces.values()
                                 if p.color == piece.color and p != piece
                                 and abs(p.position[0] - piece.position[0]) + abs(
                    p.position[1] - piece.position[1]) <= 1)
                value *= (1 + 0.2 * protectors)

            if piece.type == 'pawn':
                if piece.color == 'white':
                    value += (7 - piece.position[1]) * 5
                    if 2 <= piece.position[0] <= 5:
                        value += 10
                    for other_pawn in [p for p in self.pieces.values() if
                                       p.type == 'pawn' and p.color == 'white' and p != piece]:
                        if piece.position[0] == other_pawn.position[0]:
                            value -= 10
                else:
                    value += piece.position[1] * 5
                    if 2 <= piece.position[0] <= 5:
                        value += 10
                    for other_pawn in [p for p in self.pieces.values() if
                                       p.type == 'pawn' and p.color == 'black' and p != piece]:
                        if piece.position[0] == other_pawn.position[0]:
                            value -= 10

            if piece.color == 'white':
                score += value
            else:
                score -= value

        if self.is_checkmate('black'):
            score += 10000
        elif self.is_checkmate('white'):
            score -= 10000

        return score

    def get_best_move(self, depth, color, alpha=float('-inf'), beta=float('inf'), use_transposition=True):
        if depth == 0 or self.game_over:
            return None, self.evaluate_board()

        best_move = None
        if color == 'white':
            best_value = float('-inf')
        else:
            best_value = float('inf')

        if use_transposition:
            board_hash = self.hash_board()
            if board_hash in self.transposition_table:
                return self.transposition_table[board_hash]

        pieces = [p for p in self.pieces.values() if p.color == color]

        pieces.sort(key=lambda p: self._move_priority(p, p.position), reverse=True)

        for piece in pieces:
            valid_moves = self.get_valid_moves(piece)
            valid_moves.sort(key=lambda m: self._move_priority(piece, m), reverse=True)

            for move in valid_moves:
                target_piece = self.get_piece_at(move)

                original_pos = piece.position
                original_pieces = self.pieces.copy()

                piece.move_to(move)
                if target_piece:
                    target_key = None
                    for k, v in original_pieces.items():
                        if v == target_piece:
                            target_key = k
                            break
                    if target_key:
                        del self.pieces[target_key]

                was_promoted = False
                if piece.type == 'pawn':
                    if (color == 'white' and move[1] == 0) or (color == 'black' and move[1] == 7):
                        piece.type = 'queen'
                        was_promoted = True

                _, evaluation = self.get_best_move(depth - 1, 'black' if color == 'white' else 'white', alpha, beta, use_transposition)

                if was_promoted:
                    piece.type = 'pawn'
                piece.move_to(original_pos)
                self.pieces = original_pieces.copy()

                if color == 'white':
                    if evaluation > best_value:
                        best_value = evaluation
                        best_move = (piece, move)
                    alpha = max(alpha, evaluation)
                else:
                    if evaluation < best_value:
                        best_value = evaluation
                        best_move = (piece, move)
                    beta = min(beta, evaluation)

                if beta <= alpha:
                    break

        if use_transposition:
            self.transposition_table[board_hash] = (best_move, best_value)

        return best_move, best_value

    def hash_board(self):
        return hash(tuple((p.color, p.type, p.position) for p in self.pieces.values()))

    def _move_priority(self, piece, move):
        priority = 0
        target = self.get_piece_at(move)

        if target:
            priority += self.piece_values[target.type] * 15

        if piece.type == 'pawn':
            if (piece.color == 'white' and move[1] == 0) or (piece.color == 'black' and move[1] == 7):
                priority += 1000

            if 2 <= move[0] <= 5:
                priority += 100

            if piece.color == 'white':
                priority += (7 - move[1]) * 20
            else:
                priority += move[1] * 20

        if 2 <= move[0] <= 5 and 2 <= move[1] <= 5:
            priority += 80

        for enemy in self.pieces.values():
            if enemy.color != piece.color and enemy.type == 'king':
                dist = abs(enemy.position[0] - move[0]) + abs(enemy.position[1] - move[1])
                if dist <= 2:
                    priority += 200
                elif dist <= 4:
                    priority += 100

        return priority

    def get_best_promotion(self, piece, move):
        return 'queen'


def main():
    global play_against_pc, current_turn, player_color
    board = ChessBoard()
    last_move_time = 0
    move_delay = 200

    while True:
        current_time = pygame.time.get_ticks()

        if (play_against_pc and current_turn != player_color and
                not board.game_over and current_time - last_move_time >= move_delay):

            best_move, _ = board.get_best_move(2, current_turn)

            if best_move:
                piece, move = best_move
                board.handle_click((
                    board.board_offset_x + piece.position[0] * tile_size + tile_size // 2,
                    board.board_offset_y + piece.position[1] * tile_size + tile_size // 2
                ))

                pygame.time.wait(100)

                board.handle_click((
                    board.board_offset_x + move[0] * tile_size + tile_size // 2,
                    board.board_offset_y + move[1] * tile_size + tile_size // 2
                ))

                if piece.type == 'pawn' and (move[1] == 0 or move[1] == 7):
                    piece.type = 'queen'

                last_move_time = current_time

        screen.fill((255, 255, 255))
        board.handle_events()
        board.draw(screen)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
