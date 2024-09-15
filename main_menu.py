import pygame
import sys

# Инициализация Pygame
pygame.init()

# Основные настройки окна меню
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('PvP Арена')

# Цвета
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
DARK_GRAY = (50, 50, 50)
BLUE = (70, 130, 180)
LIGHT_BLUE = (173, 216, 230)


# Функция для отображения инструкции
def show_instructions():
    instruction_running = True
    font = pygame.font.SysFont(None, 36)
    title_font = pygame.font.SysFont(None, 72)

    # Инструкция построчно
    instructions = [
        "Правила игры PvP Арена:",
        "1. Управляйте персонажами, используя клавиши W, A, S, D для передвижения.",
        "2. Для атаки врага нажмите SPACE, когда выбрали врага.",
        "3. Каждый персонаж имеет ограниченное количество шагов и радиус атаки.",
        "4. Уничтожьте всех врагов, чтобы победить.",
        "5. Персонажи разного типа имеют разные атаки и способности."
    ]

    while instruction_running:
        screen.fill(WHITE)

        # Добавляем рамку для инструкции
        pygame.draw.rect(screen, DARK_GRAY, (120, 110, WIDTH - 200, HEIGHT - 200), 5)

        # Отображаем заголовок
        title_text = title_font.render("Инструкция", True, BLUE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 130))

        # Отображаем текст инструкции построчно
        for i, line in enumerate(instructions):
            text = font.render(line, True, BLACK)
            screen.blit(text, (150, 250 + i * 50))

        # Кнопка возврата в меню
        pygame.draw.rect(screen, GRAY, (WIDTH // 2 - 100, HEIGHT - 150, 200, 50))
        back_text = font.render('Назад', True, BLACK)
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 140))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                # Обработка клика на кнопку "Назад"
                if WIDTH // 2 - 100 < mouse_pos[0] < WIDTH // 2 + 100 and HEIGHT - 150 < mouse_pos[1] < HEIGHT - 100:
                    instruction_running = False


# Основное меню
def main_menu():
    menu_running = True
    font = pygame.font.SysFont(None, 48)
    title_text = font.render('PvP Арена', True, BLACK)

    while menu_running:
        screen.fill(WHITE)

        # Отображаем название игры
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))

        # Отображаем кнопки
        pygame.draw.rect(screen, GRAY, (WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50))
        pygame.draw.rect(screen, GRAY, (WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50))
        pygame.draw.rect(screen, GRAY, (WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 50))

        start_text = font.render('Начать игру', True, BLACK)
        instr_text = font.render('Инструкция', True, BLACK)
        exit_text = font.render('Выход', True, BLACK)

        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 - 50 + 10))
        screen.blit(instr_text, (WIDTH // 2 - instr_text.get_width() // 2, HEIGHT // 2 + 20 + 10))
        screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 90 + 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if WIDTH // 2 - 100 < mouse_pos[0] < WIDTH // 2 + 100:
                    if HEIGHT // 2 - 50 < mouse_pos[1] < HEIGHT // 2:
                        # Запуск основной игры
                        import game
                        game.main_game()
                    elif HEIGHT // 2 + 20 < mouse_pos[1] < HEIGHT // 2 + 70:
                        # Показать инструкцию
                        show_instructions()
                    elif HEIGHT // 2 + 90 < mouse_pos[1] < HEIGHT // 2 + 140:
                        pygame.quit()
                        sys.exit()


if __name__ == "__main__":
    main_menu()
