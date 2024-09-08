#Создать игру крестики-нолики
import tkinter as tk
from tkinter import messagebox

# Главное окно
root = tk.Tk()
root.title("Крестики-нолики")
root.state('zoomed')  # Открыть окно на весь экран
root.configure(bg="#282c34")

font_large = ("Arial", 24, "bold")
font_small = ("Arial", 18)

player = "X"
game_board = [""] * 9

# Проверка победителя
def check_winner():
    win_lines = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                 (0, 3, 6), (1, 4, 7), (2, 5, 8),
                 (0, 4, 8), (2, 4, 6)]

    for a, b, c in win_lines:
        if game_board[a] == game_board[b] == game_board[c] and game_board[a] != "":
            return game_board[a]

    if "" not in game_board:
        return "Ничья"

    return None

# Логика нажатия кнопки
def button_click(index):
    global player

    if game_board[index] == "" and not check_winner():
        game_board[index] = player
        buttons[index].config(text=player, state="disabled", disabledforeground="white")

        winner = check_winner()
        if winner:
            if winner == "Ничья":
                messagebox.showinfo("Результат", "Игра закончилась в ничью!")
            else:
                messagebox.showinfo("Результат", f"Победитель: {winner}!")
            restart_game()
        else:
            player = "O" if player == "X" else "X"
            label_player.config(text=f"Ход: {player}")

# Сброс игры
def restart_game():
    global game_board, player
    game_board = [""] * 9
    player = "X"
    for button in buttons:
        button.config(text="", state="normal")
    label_player.config(text=f"Ход: {player}")

# Интерфейс
frame = tk.Frame(root, bg="#282c34")
frame.pack(pady=20)

buttons = []
for i in range(9):
    button = tk.Button(frame, text="", font=font_large, width=6, height=3,
                       command=lambda i=i: button_click(i), bg="#61afef")
    button.grid(row=i // 3, column=i % 3, padx=8, pady=8)
    buttons.append(button)

label_player = tk.Label(root, text=f"Ход: {player}", font=font_small, bg="#282c34", fg="white")
label_player.pack(pady=15)

reset_button = tk.Button(root, text="Перезапуск", font=font_small, command=restart_game, bg="#e06c75", fg="white")
reset_button.pack(pady=15)

root.mainloop()
