import random

py_num = random.randint(1, 3)

user_choice = input("Камень, ножницы, бумага > ").lower()

commands = {
    "камень": 1,
    "ножницы": 2,
    "бумага": 3
}

win_conditions_user = {
    (1, 2): "Камень победил ножницы!",
    (2, 3): "Ножницы победили бумагу!",
    (3, 1): "Бумага победила камень!"
}

win_conditions_py = {
    (1, 3): "Вы проиграли бумаге!",
    (2, 1): "Вы проиграли камню!",
    (3, 2): "Вы проиграли ножницам!"
}

result = (commands[user_choice], py_num)

print(win_conditions_user.get(result) if win_conditions_user.get(result) else win_conditions_py.get(result))

"""
Алгоритм:
Компьютер выбирает число, которое равняется выбору.
Получаем значение юзера и сравниваем с значением компьютера если число юзера бьёт число компьютера,
то выводим, что он победил,
если наоборот, то проиграл
"""