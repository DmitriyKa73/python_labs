def print_matrix_diagonally(size):
    """
    Функция для вывода индексов элементов матрицы по диагонали.
    Принимает размерность матрицы size и печатает индексы для матрицы size * size.
    """
    for slice in range(2 * size - 1):
        output = []
        for i in range(max(0, slice - size + 1), min(slice + 1, size)):
            j = slice - i
            output.append(f"Индекс: {i},{j}")
        print(" ".join(output))

"""
Запрос размера матрицы у пользователя.
"""
n = int(input("Введите размерность матрицы n*n: "))

"""
Проверка, что введено положительное число.
"""
if n > 0:
    """
    Вызов функции для печати индексов элементов матрицы по диагонали.
    """
    print_matrix_diagonally(n)
else:
    print("Размерность матрицы должна быть положительным числом.")
