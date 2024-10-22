"""
Задание состоит из двух частей.
1 часть – написать программу в соответствии со своим вариантом задания. Написать 2 варианта формирования (алгоритмический и с помощью функций Питона), сравнив по времени их выполнение.
2 часть – усложнить написанную программу, введя по своему усмотрению в условие минимум одно ограничение на характеристики объектов (которое будет сокращать количество переборов)  и целевую функцию для нахождения оптимального  решения.
Вариант 12. Вывести все натуральные числа до n, в записи которых встречается ровно одна нечетная цифра на четной позиции.
"""

import timeit
import itertools

# Алгоритмический подход
def is_valid_alg(number):
    number_str = str(number)
    return sum(1 for i, d in enumerate(number_str, start=1) if i % 2 == 0 and int(d) % 2 == 1) == 1

def algorithmic_approach(n):
    result = []
    for number in range(n):
        if is_valid_alg(number):
            result.append(number)
    return result

# Функциональный подход с использованием itertools
def functional_approach_itertools(n):
    result = []
    for digits in itertools.product('0123456789', repeat=len(str(n - 1))):
        number = int(''.join(digits))
        if number < n and is_valid_alg(number):
            result.append(number)
    return result

# Усложненный алгоритмический подход с дополнительным условием кратности 5
def complex_algorithmic_approach(n):
    result = []
    for number in range(0, n, 5):  # Перебор с шагом 5
        if is_valid_alg(number):
            result.append(number)
    return result

# Усложненный функциональный подход с использованием itertools и условием кратности 5
def complex_functional_approach_itertools(n):
    result = []
    for digits in itertools.product('0123456789', repeat=len(str(n - 1))):
        number = int(''.join(digits))
        if number < n and number % 5 == 0 and is_valid_alg(number):
            result.append(number)
    return result

# Сравнение времени выполнения
n = int(input("Введите число n: "))

# Алгоритмический подход
start_time_alg = timeit.default_timer()
algorithmic_result = algorithmic_approach(n)
time_alg = timeit.default_timer() - start_time_alg

# Функциональный подход (itertools)
start_time_func = timeit.default_timer()
functional_result_itertools = functional_approach_itertools(n)
time_func = timeit.default_timer() - start_time_func

# Усложненный алгоритмический подход
start_time_complex_alg = timeit.default_timer()
complex_algorithmic_result = complex_algorithmic_approach(n)
time_complex_alg = timeit.default_timer() - start_time_complex_alg

# Усложненный функциональный подход (itertools)
start_time_complex_func = timeit.default_timer()
complex_functional_result_itertools = complex_functional_approach_itertools(n)
time_complex_func = timeit.default_timer() - start_time_complex_func

# Вывод результатов
print("Алгоритмический подход:")
print(algorithmic_result)
print("Время выполнения: {:.6f} секунд".format(time_alg))

print("\nФункциональный подход (itertools):")
print(functional_result_itertools)
print("Время выполнения: {:.6f} секунд".format(time_func))

print("\nУсложненный алгоритмический подход (кратные 5):")
print(complex_algorithmic_result)
print("Время выполнения: {:.6f} секунд".format(time_complex_alg))

print("\nУсложненный функциональный подход (itertools, кратные 5):")
print(complex_functional_result_itertools)
print("Время выполнения: {:.6f} секунд".format(time_complex_func))

# Сравнение времени выполнения алгоритмического и функционального подходов
if time_alg < time_func:
    print("\nАлгоритмический подход быстрее функционального на {:.6f} секунд.".format(time_func - time_alg))
else:
    print("\nФункциональный подход (itertools) быстрее алгоритмического на {:.6f} секунд.".format(time_alg - time_func))

# Сравнение времени выполнения усложненных подходов
if time_complex_alg < time_complex_func:
    print("Усложненный алгоритмический подход быстрее усложненного функционального на {:.6f} секунд.".format(time_complex_func - time_complex_alg))
else:
    print("Усложненный функциональный подход (itertools, кратные 5) быстрее усложненного алгоритмического на {:.6f} секунд.".format(time_complex_alg - time_complex_func))
