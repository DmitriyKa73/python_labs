"""
Задана рекуррентная функция. Область определения функции – натуральные числа. Написать программу сравнительного вычисления данной функции рекурсивно и итерационно.
#Определить границы применимости рекурсивного и итерационного подхода. Результаты сравнительного исследования времени вычисления представить в табличной и графической форме.
#Вариант 12: F(1) = 1, F(n) = (-1)^n* (F(n–1) + (n - 1)! /(2n)!), при n > 1
"""
import timeit
import matplotlib.pyplot as plt

"""
Кэш для хранения вычисленных значений факториалов
"""
factorial_cache = {0: 1, 1: 1}

"""
Динамическая функция для вычисления факториала
"""
def dynamic_factorial(n):
    if n not in factorial_cache:
        factorial_cache[n] = n * dynamic_factorial(n-1)
    return factorial_cache[n]

"""
Рекурсивная функция для вычисления факториала
"""
def recursive_factorial(n):
    if n == 0:
        return 1
    else:
        return n * recursive_factorial(n-1)

"""
Итеративная функция для вычисления факториала
"""
def iterative_factorial(n):
    result = 1
    for i in range(2, n+1):
        result *= i
    return result

"""
Динамическая функция для вычисления F(n)
"""
def dynamic_F(n, cache={1: 1}):
    if n in cache:
        return cache[n]
    else:
        """
        Здесь используем dynamic_factorial для вычисления факториалов
        """
        result = (-1)**n * (dynamic_F(n-1, cache) + dynamic_factorial(n-1) / dynamic_factorial(2*n))
        cache[n] = result
        return result

"""
Функция для измерения времени выполнения
"""
def score_time(func, n):
    return timeit.timeit(lambda: func(n), number=1000)

"""
Значения n для которых мы хотим измерить время выполнения
"""
n_values = range(1, 10)
recursive_times = []
iterative_times = []
dynamic_times = []

"""
Измерение времени выполнения для каждого значения n
"""
for n in n_values:
    recursive_times.append(score_time(recursive_factorial, n))
    iterative_times.append(score_time(iterative_factorial, n))
    dynamic_times.append(score_time(dynamic_F, n))

"""
Вывод результатов в табличной форме
"""
print(f"{'n':<10}{'Рекурсивное время (мс)':<25}{'Итерационное время (мс)':<25}{'Динамическое время (мс)':<25}")
for i, n in enumerate(n_values):
    print(f"{n:<10}{recursive_times[i]:<25}{iterative_times[i]:<25}{dynamic_times[i]:<25}")

"""
Построение и вывод графика результатов
"""
plt.plot(n_values, recursive_times, label='Рекурсивно')
plt.plot(n_values, iterative_times, label='Итерационно')
plt.plot(n_values, dynamic_times, label='Динамическое')
plt.xlabel('n')
plt.ylabel('Время (в миллисекундах)')
plt.legend()
plt.title('Сравнение времени вычисления функции F(n)')
plt.show()
