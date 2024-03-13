#Вар.12 12.	Формируется матрица F следующим образом: скопировать в нее А и если в В количество простых чисел в нечетных столбцах больше, 
# чем сумма чисел в четных строках, то поменять местами В и Е симметрично, иначе С и Е поменять местами несимметрично. 
# При этом матрица А не меняется. После чего если определитель матрицы А больше суммы диагональных элементов матрицы F, то вычисляется 
# выражение: A-1*AT – K * F-1, иначе вычисляется выражение (A-1 +G-F-1)*K, где G-нижняя треугольная матрица, полученная из А. 
# Выводятся по мере формирования А, F и все матричные операции последовательно.

import numpy as np
import matplotlib.pyplot as plt

def create_matrix(N):
    return np.random.randint(-10, 11, size=(N, N))

def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(np.sqrt(num)) + 1):
        if num % i == 0:
            return False
    return True

def count_primes_in_odd_columns(B):
    count = 0
    odd_columns = B[:, 1::2]
    for value in np.nditer(odd_columns):
        if is_prime(value):
            count += 1
    return count

def sum_in_even_rows(C):
    even_rows = C[1::2, :]
    return np.sum(even_rows)

def main():
    K = int(input("Введите число K: "))
    N = int(input("Введите размерность матрицы N: "))

    A = create_matrix(N)
    print("Матрица A:")
    print(A)

    mid = N // 2
    B = A[:mid, :mid]
    C = A[:mid, mid:]
    D = A[mid:, :mid]
    E = A[mid:, mid:]

    F = A.copy()
    if count_primes_in_odd_columns(B) > sum_in_even_rows(C):
        F[:mid, :mid], F[mid:, mid:] = E.T, B.T
    else:
        F[:mid, mid:], F[mid:, mid:] = E, C

    print("Матрица F после преобразований:")
    print(F)

    det_A = np.linalg.det(A)
    sum_diag_F = np.trace(F)

    if det_A > sum_diag_F:
        result = np.linalg.inv(A) @ A.T - K * np.linalg.inv(F)
    else:
        G = np.tril(A)
        result = (np.linalg.inv(A) + G - np.linalg.inv(F)) * K

    print("Результат выражения:")
    print(result)

    plt.matshow(A)
    plt.title('Матрица A')
    plt.colorbar()
    plt.show()

    plt.matshow(F)
    plt.title('Матрица F')
    plt.colorbar()
    plt.show()

    plt.matshow(result)
    plt.title('Результат выражения')
    plt.colorbar()
    plt.show()

if __name__ == "__main__":
    main()
