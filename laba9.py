import tkinter as tk
from tkinter import messagebox

window = tk.Tk()
window.title("Крестики-нолики")
window.state('zoomed')
window.configure(bg="#2b2b2b")

# Шрифты
font_big = ("Arial", 24, "bold")
font_small = ("Arial", 18)

current_player = "X"  # Текущий игрок
board = [""] * 9  # Игровое поле
play_vs_computer = False  

# Проверка на победителя
def check_winner():
    winning_combos = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                      (0, 3, 6), (1, 4, 7), (2, 5, 8),
                      (0, 4, 8), (2, 4, 6)]

    for a, b, c in winning_combos:
        if board[a] == board[b] == board[c] and board[a] != "":
            return board[a]

    if "" not in board:
        return "Ничья"

    return None

# Алгоритм для логики хода компьютера
def minimax(is_maximizing):
    winner = check_winner()
    if winner == "X":
        return -1
    elif winner == "O":
        return 1
    elif winner == "Ничья":
        return 0

    if is_maximizing:
        best_score = -float('inf')
        for i in range(9):
            if board[i] == "":
                board[i] = "O"
                score = minimax(False)
                board[i] = ""
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(9):
            if board[i] == "":
                board[i] = "X"
                score = minimax(True)
                board[i] = ""
                best_score = min(score, best_score)
        return best_score

# Ход компьютера
def computer_turn():
    best_score = -float('inf')
    best_move = None

    for i in range(9):
        if board[i] == "":
            board[i] = "O"
            score = minimax(False)
            board[i] = ""
            if score > best_score:
                best_score = score
                best_move = i

    if best_move is not None:
        board[best_move] = "O"
        buttons[best_move].config(text="O", state="disabled", disabledforeground="#ffffff")
        if check_winner():
            show_result(check_winner())
        else:
            switch_turn()

# Обработка нажатия на кнопку
def button_click(index):
    global current_player

    if board[index] == "" and not check_winner():
        board[index] = current_player
        buttons[index].config(text=current_player, state="disabled", disabledforeground="#ffffff")

        if check_winner():
            show_result(check_winner())
        else:
            if play_vs_computer and current_player == "X":
                switch_turn()
                computer_turn()
            else:
                switch_turn()

# Переключение хода между игроками
def switch_turn():
    global current_player
    current_player = "O" if current_player == "X" else "X"
    label_turn.config(text=f"Ход: {current_player}")

# Отображение результата игры
def show_result(winner):
    if winner == "Ничья":
        messagebox.showinfo("Результат", "Игра закончилась в ничью!")
    elif play_vs_computer:
        if winner == "X":
            messagebox.showinfo("Результат", "Вы выиграли!")
        else:
            messagebox.showinfo("Результат", "Компьютер выиграл!")
    else:
        messagebox.showinfo("Результат", f"Выиграл игрок {winner}!")
    reset_game()

# Перезапуск игры
def reset_game():
    global board, current_player
    board = [""] * 9
    current_player = "X"
    for button in buttons:
        button.config(text="", state="normal")
    label_turn.config(text=f"Ход: {current_player}")

# Начало игры против компьютера
def start_vs_computer():
    global play_vs_computer
    play_vs_computer = True
    label_status.config(text="Игра против компьютера")
    reset_game()

# Начало игры против другого игрока
def start_vs_player():
    global play_vs_computer
    play_vs_computer = False
    label_status.config(text="Игра против игрока")
    reset_game()

label_status = tk.Label(window, text="Игра против игрока", font=font_small, bg="#2b2b2b", fg="#ffffff")
label_status.pack(pady=5)

# Метка для отображения текущего хода
label_turn = tk.Label(window, text=f"Ход: {current_player}", font=font_small, bg="#2b2b2b", fg="#ffffff")
label_turn.pack(pady=5)

# Создаем игровое поле
frame = tk.Frame(window, bg="#2b2b2b")
frame.pack(pady=20)

buttons = []
for i in range(9):
    button = tk.Button(frame, text="", font=font_big, width=6, height=3,
                       command=lambda i=i: button_click(i), bg="#4682b4")
    button.grid(row=i // 3, column=i % 3, padx=8, pady=8)
    buttons.append(button)

reset_button = tk.Button(window, text="Перезапуск", font=font_small, command=reset_game, bg="#8b0000", fg="#ffffff")
reset_button.pack(pady=5)

computer_button = tk.Button(window, text="Играть против компьютера", font=font_small, command=start_vs_computer, bg="#006400", fg="#ffffff")
computer_button.pack(pady=5)

player_button = tk.Button(window, text="Играть против игрока", font=font_small, command=start_vs_player, bg="#1e90ff", fg="#ffffff")
player_button.pack(pady=5)

window.mainloop()
