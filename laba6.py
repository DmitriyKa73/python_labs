"""
Задание состоит из двух частей.
1 часть – написать программу в соответствии со своим вариантом задания. Написать 2 варианта формирования (алгоритмический и с помощью функций Питона), сравнив по времени их выполнение.
2 часть – усложнить написанную программу, введя по своему усмотрению в условие минимум одно ограничение на характеристики объектов (которое будет сокращать количество переборов)  и целевую функцию для нахождения оптимального  решения.
Вариант 12. Вывести все натуральные числа до n, в записи которых встречается ровно одна нечетная цифра на четной позиции.
"""
import time

def is_valid_number_alg(number):
    """Проверяет, есть ли в числе ровно одна нечетная цифра на четной позиции."""
    odd_count = 0
    position = 1
    while number > 0:
        digit = number % 10
        if position % 2 == 0 and digit % 2 != 0:
            odd_count += 1
        if odd_count > 1:
            return False
        number //= 10
        position += 1
    return odd_count == 1

def find_valid_numbers_alg(n):
    """Находит все подходящие числа алгоритмическим способом."""
    return [number for number in range(1, n+1) if is_valid_number_alg(number)]

def is_valid_number_func(number):
    """Проверяет, используя функции Python, наличие одной нечетной цифры на четной позиции."""
    return sum(1 for i, digit in enumerate(reversed(str(number)), start=1) if i % 2 == 0 and int(digit) % 2 != 0) == 1

def find_valid_numbers_func(n):
    """Находит все подходящие числа с использованием функций Python."""
    return [number for number in range(1, n+1) if is_valid_number_func(number)]

def is_prime(number):
    if number <= 1:
        return False
    if number == 2:
        return True
    if number % 2 == 0:
        return False
    for current in range(3, int(number ** 0.5) + 1, 2):
        if number % current == 0:
            return False
    return True

def has_one_odd_digit_on_even_position(number):
    str_number = str(number)
    odd_digits = [int(str_number[i]) for i in range(1, len(str_number), 2) if int(str_number[i]) % 2 != 0]
    return len(odd_digits) == 1

def find_valid_primes(n):
    valid_primes = []
    for number in range(1, n + 1):
        if has_one_odd_digit_on_even_position(number) and is_prime(number):
            valid_primes.append(number)
    return valid_primes

# Запрос ввода от пользователя
n = int(input("Введите число n: "))

# Измерение времени для алгоритмического подхода
start_time = time.time()
valid_numbers_alg = find_valid_numbers_alg(n)
end_time = time.time()
alg_time = end_time - start_time
print("ПЕРВАЯ ЧАСТЬ ЗАДАНИЯ")
print(f"Алгоритмический метод: {valid_numbers_alg}")
print(f"Затраченное время: {alg_time}")


# Измерение времени для функционального подхода
start_time = time.time()
valid_numbers_func = find_valid_numbers_func(n)
end_time = time.time()
func_time = end_time - start_time
print(f"Функциональный метод: {valid_numbers_func}")
print(f"затраченное время: {func_time}")

# Сравнение времени выполнения
if alg_time < func_time:
    print(f"Алгоритмический метод быстрее на {func_time - alg_time} секунд.")
else:
    print(f"Функциональный метод быстрее на {alg_time - func_time} секунд.")

# Находим и выводим все простые числа, удовлетворяющие условиям
valid_primes = find_valid_primes(n)
print("ВТОРАЯ ЧАСТЬ ЗАДАНИЯ")
print("Простые числа до n с одной нечетной цифрой на четной позиции:")
print(valid_primes)
