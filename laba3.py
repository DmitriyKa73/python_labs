#Лабораторная работа №3
#12.	Формируется матрица F следующим образом: если в В количество простых чисел в нечетных столбцах в области 2 больше,
# чем сумма чисел в четных строках в области 1, то поменять в Е симметрично области 1 и 2 местами, иначе С и Е поменять местами несимметрично.
# При этом матрица А не меняется. После чего вычисляется выражение: ((К*A)*А– K*AT . Выводятся по мере формирования А, F и все матричные операции последовательно.
import random
def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

def create_matrix(N):
    return [[random.randint(-10, 10) for _ in range(N)] for _ in range(N)]

def count_primes_in_odd_columns(B):
    count = 0
    for row in B:
        for i in range(0, len(row), 2):  # Нечетные столбцы (с индексом 0, 2, ...)
            if is_prime(row[i]):
                count += 1
    return count

def sum_in_even_rows(C):
    total = 0
    for i in range(1, len(C), 2):  # Четные строки (с индексом 1, 3, ...)
        total += sum(C[i])
    return total

def transpose_matrix(matrix):
    return [list(row) for row in zip(*matrix)]

def multiply_matrix_by_scalar(matrix, scalar):
    return [[scalar * cell for cell in row] for row in matrix]

def subtract_matrices(A, B):
    return [[A[i][j] - B[i][j] for j in range(len(A[i]))] for i in range(len(A))]

def matrix_multiplication(A, B):
    result = [[0 for _ in range(len(B[0]))] for _ in range(len(A))]
    for i in range(len(A)):
        for j in range(len(B[0])):
            for k in range(len(B)):
                result[i][j] += A[i][k] * B[k][j]
    return result

def print_matrix(matrix):
    for row in matrix:
        print(' '.join(map(str, row)))
    print()

def main():
    K = int(input("Введите число K: "))
    N = int(input("Введите размерность матрицы N: "))

    if N % 2 != 0:
        print("N должно быть четным.")
        return

    A = create_matrix(N)
    print("Матрица A:")
    print_matrix(A)

    mid = N // 2
    B = [row[:mid] for row in A[:mid]]
    C = [row[mid:] for row in A[:mid]]
    D = [row[:mid] for row in A[mid:]]
    E = [row[mid:] for row in A[mid:]]

    if count_primes_in_odd_columns(B) > sum_in_even_rows(C):
        for i in range(mid):
            for j in range(mid):
                E[i][j], E[j][i] = E[j][i], E[i][j]
    else:
        C, E = E, C

    F = [B[i] + C[i] for i in range(mid)] + [D[i] + E[i] for i in range(mid)]

    print("Матрица F после преобразований:")
    print_matrix(F)

    KA = multiply_matrix_by_scalar(A, K)
    A_transposed = transpose_matrix(A)
    KA_transposed = multiply_matrix_by_scalar(A_transposed, K)
    A_squared = matrix_multiplication(A, A)
    KAA_minus_KAT = subtract_matrices(multiply_matrix_by_scalar(A_squared, K), KA_transposed)

    # Вывод результатов
    print("Матрица KA (K умноженное на A):")
    print_matrix(KA)

    print("Матрица A транспонированная:")
    print_matrix(A_transposed)

    print("Матрица KAT (K умноженное на A транспонированное):")
    print_matrix(KA_transposed)

    print("Матрица KAA (K умноженное на A квадрат):")
    print_matrix(multiply_matrix_by_scalar(A_squared, K))

    print("Результат выражения ((К*A)A– KA^T):")
    print_matrix(KAA_minus_KAT)

if __name__ == "__main__":
    main()
