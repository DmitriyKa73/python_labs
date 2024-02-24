#ВАРИАНТ 12. Натуральные числа, содержащие более 3 цифр. 
#Вывести количество таких чисел. Максимальное число вывести прописью.
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
file_path = "text.txt"

def number_to_words(number):
    return ' '.join(digit_to_word[digit] for digit in str(number))
count_numbers = 0
max_number = 0
try:
    with open(file_path, "r") as file:
        block_size = 1024
        block = file.read(block_size)

        while block:        
            numbers = [int(num) for num in block.split() if num.isdigit() and int(num) > 999]

            for num in numbers:
                if num > 999:
                    count_numbers += 1
                    max_number = max(max_number, num)
            block = file.read(block_size)

except ValueError:
    print("Ошибка: Файл содержит некорректные данные. Очистите файл input.txt.")
    exit()
print(f"Количество натуральных чисел более 3 цифр: {count_numbers}")
print(f"Максимальное число: {max_number} ({number_to_words(max_number)})")
