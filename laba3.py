#Лабораторная работа №3
#12.	Формируется матрица F следующим образом: если в В количество простых чисел в нечетных столбцах в области 2 больше,
# чем сумма чисел в четных строках в области 1, то поменять в Е симметрично области 1 и 2 местами, иначе С и Е поменять местами несимметрично.
# При этом матрица А не меняется. После чего вычисляется выражение: ((К*A)*А– K*AT . Выводятся по мере формирования А, F и все матричные операции последовательно.

import random

def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return False
    return True

def generate_matrix():
    return [[random.randint(-10, 10) for _ in range(2)] for _ in range(2)]

def count_primes(matrix):
    return sum(is_prime(num) for num in matrix)

def create_F_matrix(matrix_B):
    F = [row.copy() for row in matrix_B]
    area_1_sum = sum(F[i][j] for i in range(2) for j in range(2))
    area_2_primes = count_primes([F[i][1] for i in range(2)])

    if area_2_primes > area_1_sum:
        F[0][:2], F[1][:2] = F[1][::-1][:2], F[0][::-1][:2]
        F[2][:2], F[3][:2] = F[3][::-1][:2], F[2][::-1][:2]
    else:
        F[0][:2] = F[0][:2][::-1]
        F[1][:2] = F[1][:2][::-1]

    return F

def get_integer_input(prompt):
    while True:
        try:
            value = int(input(prompt))
            return value
        except ValueError:
            print("Ошибка! Введите целое число.")

def main():
    K = get_integer_input("Введите число K: ")
    N = get_integer_input("Введите число N: ")

    A = [[random.randint(-10, 10) for _ in range(N)] for _ in range(N)]
    B = generate_matrix()
    C = generate_matrix()
    D = generate_matrix()
    E = generate_matrix()

    F = create_F_matrix(B)

    result = [[K * A[i][j] * A[i][k] - K * A[k][j] for k in range(N)] for i in range(N) for j in range(N)]

    print("\nМатрица A:")
    for row in A:
        print(row)

    print("\nМатрица F:")
    for row in F:
        print(row)

    print("\nРезультат выражения ((К*A)*А– K*A^T):")
    for row in result:
        print(row)


if __name__ == "__main__":
    main()
