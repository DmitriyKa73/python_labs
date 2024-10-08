# PvP Арена

**PvP Арена** — это пошаговая стратегическая игра, в которой два игрока (человек и компьютер) сражаются друг против друга, используя команды персонажей с уникальными характеристиками. Игра создана на Python с использованием библиотек `pygame` и `tkinter`.

## Описание игры

Игра представляет собой пошаговую битву между командами персонажей. Каждый персонаж обладает уникальными характеристиками: количеством здоровья (HP), уроном, радиусом атаки и дальностью перемещения. Игроки по очереди управляют своими персонажами, перемещая их по сетке и атакуя врагов.

### Основные особенности:

- Пошаговая механика боя.
- Команды персонажей: игрок управляет командой из трёх персонажей (Воин, Маг, Лучник), компьютер — командой врагов (Гоблин, Огр, Тролль).
- Индикатор здоровья и информации о персонажах в боковой панели.
- Возможность атаковать противника на основе радиуса атаки.
- Автоматизированный ход врага после завершения хода игрока.

## Установка

Для запуска игры необходимо, чтобы у вас был установлен Python и библиотеки `pygame` и `tkinter`.

1. Клонируйте репозиторий или скачайте исходный код:
   ```bash
   git clone <https://github.com/DmitriyKa73/python_labs/tree/main/PVP_Arena>
   ```
2.Установите необходимые зависимости:
   ```bash
   pip install pygame tkinter
   ```
3. Запустите игру:
- python main_menu.py

### Управление

- Мышь: клик для выбора персонажа и наведение курсора мыши для выбора врага.
- W, A, S, D: перемещение выбранного персонажа.
- Space: атака врага, если он находится в радиусе действия выбранного персонажа.
  
### Структура проекта

- `main_menu.py`           # Основной файл с главным меню
- `game.py`               # Файл с основными механиками игры
- `README.md`              # Документация проекта

### Основные файлы

- `main_menu.py`: содержит код для отображения главного меню игры.
- `game.py`: реализует игровую механику, включая ходы персонажей, атаки и взаимодействие с врагами.

### Правила игры

Игрок начинает с командой из трех персонажей, каждый из которых обладает разными характеристиками (HP, урон, радиус атаки, дальность перемещения).

- Ход игрока:
1. Выберите персонажа для хода, кликнув по нему.
2. Переместите его с помощью клавиш W, A, S, D.
3. Для атаки врага используйте клавишу Space, если враг находится в радиусе действия.
4. После завершения хода игрока, ходит компьютер.
5. Игра продолжается до тех пор, пока одна из команд не будет побеждена.

### Будущие улучшения

* Добавление новых типов персонажей с уникальными способностями.
* Сетевая многопользовательская игра.
* Улучшение графики и интерфейса.

### Лицензия

Этот проект распространяется без лицензионного знака.

Этот `README.md` документирует игру, как её установить, запустить и управлять, а также даёт обзор структуры проекта.
by @crew_dev
