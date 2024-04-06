def print_matrix_diagonally(matrix):
    size = len(matrix)
    for slice in range(2 * size - 1):
        output = []
        """ 
        Начинаем с (0, slice) и идем вниз до (slice, 0)
        """
        for i in range(max(0, slice - size + 1), min(slice + 1, size)):
            j = slice - i
            output.append(f"Индекс: {i},{j}")
        print(" ".join(output))

"""
Создание матрицы 8x8
""" 
matrix = [[0 for j in range(8)] for i in range(8)]

""" 
Вызов функции для печати индексов элементов матрицы по диагонали
""" 
print_matrix_diagonally(matrix)
