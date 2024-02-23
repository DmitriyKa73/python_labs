import random
digit_to_word = {
    '0': 'ноль',
    '1': 'один',
    '2': 'два',
    '3': 'три',
    '4': 'четыре',
    '5': 'пять',
    '6': 'шесть',
    '7': 'семь',
    '8': 'восемь',
    '9': 'девять'
}
file_path = "input.txt"

def number_to_words(number):
    return ' '.join(digit_to_word[digit] for digit in str(number))

target_count = 1000  # нужное количество чисел

with open(file_path, "w") as file:
    for _ in range(target_count):
        num = random.randint(1, 9999)
        file.write(str(num) + " ")

# Обработка файла

count_numbers = 0
max_number = 0

with open(file_path, "r") as file:
    numbers = [int(num) for num in file.read().split()]

for num in numbers:
    if num > 999:
        count_numbers += 1
        max_number = max(max_number, num)

print(f"Количество натуральных чисел более 3 цифр: {count_numbers}")
print(f"Максимальное число: {max_number} ({number_to_words(max_number)})")
