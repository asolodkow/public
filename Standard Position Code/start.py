import math
import random
import itertools
import sys
import time
import binmatrix as bm
import code as cd


""" ЧТЕНИЕ ОПИСАНИЯ КОДА ИЗ ФАЙЛА """

class LinearCodeReaded (cd.LinearCode):
# код, восстановленный по матрице A, прочитанной из файла
    def __init__ (self, A):
        self.A = A
        self.H = cd.HMatrix(self.A)
        self.G = cd.GMatrix(self.A)
        ST = cd.StandardTable(self.A)
        self.table = ST.table
        self.message = ST.message
        self.code_words = ST.code_words
        self.leaders = ST.leaders

class AMatrixReaded (cd.AMatrix):
# матрица A, восстановленная из файла с описанием кода
    def __init__ (self):
        f = open(r"code.txt", "r")
        f.__next__()
        self.d = int(f.__next__())
        f.__next__()
        f.__next__()
        f.__next__()
        G = self.read_GMatrix(f)
        f.close()
        self.n = len(G)
        self.k = len(bm.transpose_matrix(G))
        self.r = self.n - self.k
        self.matrix = bm.transpose_matrix(self.get_AMatrix(G))

    def read_GMatrix (self, f):
    # считывает порождающую матрицу G из файла описания кода
        res = []
        s = f.__next__()
        while (s != "\n"):
            res.append(convert_string_into_list(s))
            s = f.__next__()
        res = bm.transpose_matrix(res)
        return res

    def get_AMatrix (self, G):
    # извлекает из матрицы G матрицу A
        res = []
        l = len(bm.transpose_matrix(G))
        for i in range(l, len(G)):
            res.append(G[i])
        return res


""" Преобразование строк """

def convert_string_into_list (s):
# преобразует строку s в список
    res = []
    for i in range(0, len(s)):
        if (s[i] != '\n'):
            res.append(int(s[i]))
    return res


""" Случайный вектор ошибок """

def generate_random_error (n, k):
# возвращает случайный n-вектор ошибки, с количеством единиц равным k
    res = []
    error_position = []
    while (len(error_position) < k):
        error_position.append(random.randint(0, n-1))
        error_position = list(set(error_position))
    for i in range(0, n):
        if (i in error_position):
            res.append(1)
        else:
            res.append(0)
    return res


""" Вероятность ошибки на слово для данной схемы декодирования """

def error_decoding_probability (n, t):
# возвращает вероятность ошибки на слово для данной схемы декодирования
    s = 0
    p = 0.01
    for i in range(0, t + 1):
        s += (bm.binomial(n, i) * p ** i) * ((1 - p) ** (n - i))
    return 1 - s


""" Корректный ввод """

def binary_symbol_correct (s):
# проверяет символы строки s. Строка должна состоять из символов '0', '1'
    res = True
    for i in range(0, len(s)):
        if (s[i] != '0' and s[i] != '1'): res = False
    return res


""" СЦЕНАРИИ РАБОТЫ """

tmp_out = sys.stdout

def code_scenario ():
# сценарий работы в режиме генерации кода
    f = open(r"code.txt", "w")
    try:
        print("Режим генерации кода")
        r = int(input("Число проверочных символов, r: "))
        n = int(input("Желаемая максимальная длина блока сообщения, n: "))
        t = int(input("Число ошибок, которое нужно исправить, t: "))
        if ((t < 1) or (n < 2) or (r < 1) or (r > n)):
            raise Exception("Некорректный ввод")
        print()
        k = n - r
        d = 2 * t + 1
        if d < 3: d = 3
        LC = cd.LinearCode(n, k, d)
        sys.stdout = f
        print("Минимальное расстояние кода, d")
        print(d)
        print()
        print("Порождающая матрица кода")
        print()
        LC.G.print_in_string_format()
        print()
        print()
        print("Стандартное расположение для кода")
        print()
        LC.print_table()
        sys.stdout = tmp_out
        f.close()
        print("Генерация кода выполнена успешно.")
        print("Вероятность ошибки на слово для данной схемы декодирования: ", round(error_decoding_probability(n, t), 5))
    except Exception as msg:
        print(msg)

def encode_scenario ():
# сценарий работы в режиме кодирования
    try:
        print("Режим кодирования")
        A = AMatrixReaded()
        LC = LinearCodeReaded(A)
        print("Число символов сообщения", A.k)
        m = input("Введите сообщение m: ")
        if (len(m) != A.k): raise Exception("Неверное число символов")
        if not(binary_symbol_correct(m)): raise Exception("Неверный символ")
        m = tuple(convert_string_into_list(m))
        code_vector = LC.encode_message(m)
        print("Кодовый вектор: ", cd.convert_into_string(code_vector))
        print("Для генерации случайного вектора ошибок введите 0")
        e = input("Введите вектор ошибок e: ")
        if not(binary_symbol_correct(e)): raise Exception("Неверный символ")
        if (e == "0"):
            e = generate_random_error(A.n, ((A.d - 1) / 2))
            print("Сгенерирован вектор ошибок e: ", cd.convert_into_string(e))
        elif (len(e) != A.n):
            raise Exception("Неверное число символов")
        else:
            e = convert_string_into_list(e)
        y = bm.sum_vector(code_vector, e)
        print("Принятый вектор сообщения: ", cd.convert_into_string(y))
    except Exception as msg:
        print(msg)

def decode_scenario ():
# сценарий работы в режиме декодирования
    try:
        print("Режим декодирования")
        A = AMatrixReaded()
        LC = LinearCodeReaded(A)
        print("Число символов кодового вектора", A.n)
        y = input("Введите принятое сообщение y: ")
        if not(binary_symbol_correct(y)): raise Exception("Неверный символ")
        if (len(y) != A.n): raise Exception("Неверное число символов")
        y = convert_string_into_list(y)
        m = LC.decode_message(y)
        e = LC.get_error_vector(y)
        print("Вектор ошибки: ", cd.convert_into_string(e))
        print("Декодированное сообщение: ", cd.convert_into_string(list(m)))
    except Exception as msg:
        print(msg)


""" ВЫЗОВ ПРОГРАММЫ """

if (len(sys.argv) > 1):
    if (sys.argv[1] == "-c"):
        code_scenario()
    elif (sys.argv[1] == "-e"):
        encode_scenario()
    elif (sys.argv[1] == "-d"):
        decode_scenario()
    else:
        print("Задан неверный ключ")
else:
    print("Не задан режим работы")
