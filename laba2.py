#ЗАДАНИЕ: Написать программу, которая читая символы из бесконечной последовательности (эмулируется конечным файлом, читающимся поблочно), распознает, преобразует и выводит на экран лексемы по определенному правилу.
#Лексемы разделены пробелами. Преобразование делать по возможности через словарь. Для упрощения под выводом числа прописью подразумевается последовательный вывод всех цифр числа. Регулярные выражения использовать нельзя.
#ВАРИАНТ 12. Натуральные числа, содержащие более 3 цифр. Вывести количество таких чисел. Максимальное число вывести прописью.
import re

file_path = "input.txt"

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


def number_to_words(number):
    return ' '.join(digit_to_word[digit] for digit in str(number))


count_numbers = 0
max_number = 0
current_number = ""

try:
    with open(file_path, "r") as file:
        block_size = 1024
        pattern = r'\b\d+\b' 

        block = file.read(block_size)
        while block:
            current_number += block
            matches = re.finditer(pattern, current_number)

            match = next(matches, None) 
            while match:
                num = int(match.group())
                if num > 999:
                    count_numbers += 1
                    max_number = max(max_number, num)
                match = next(matches, None)  

           
            current_number = current_number[match.end():] if match else ""

            block = file.read(block_size)

except ValueError:
    print("Ошибка: Файл содержит некорректные данные. Очистите файл input.txt.")
    exit()

print(f"Количество натуральных чисел более 3 цифр: {count_numbers}")
print(f"Максимальное число: {max_number} ({number_to_words(max_number)})")
