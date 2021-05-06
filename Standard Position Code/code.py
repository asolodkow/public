import math
import random
import itertools
import time
import binmatrix as bm


""" ЛИНЕЙНЫЙ КОД """

class LinearCode:
# Линейный n, k, d код
    def __init__ (self, n, k, d):
        if not VarshamovLimit(n, k, d).predicate():
            raise Exception("Условие на существование кода не выполнено")
        self.A = AMatrix(n, k, d)
        self.H = HMatrix(self.A)
        self.G = GMatrix(self.A)
        ST = StandardTable(self.A)
        self.table = ST.table
        self.message = ST.message
        self.code_words = ST.code_words
        self.leaders = ST.leaders

    def print_table (self):
    # печатает стандартное расположение для кода
        self.print_table_head()
        for i in range(0, len(self.leaders)):
            self.print_table_line(i)

    def print_table_head (self):
    # печатает заголовки столбцов таблицы - вектора сообщения, заголовок столбца синдрома
        s = ""
        for i in range(0, len(self.message)):
            s += convert_into_string(self.message[i]) + (" " * (self.A.n - self.A.k + 1))
        print(s + "Syndrome")

    def print_table_line (self, i):
    # печатает i-ю строку таблицы
        s = ""
        for j in range(0, len(self.message)):
            s += convert_into_string(self.table[self.leaders[i]][self.message[j]]) + " "
        s += convert_into_string(self.table[self.leaders[i]]["Syndrome"])
        print(s)

    def encode_message (self, x):
    # кодирует вектор x
        return self.table[self.leaders[0]][x]

    def decode_message (self, y):
    # декодирует вектор y, возвращает исходное сообщение
        u = self.get_code_word(y)
        for i in range (0, len(self.message)):
            if u == list(self.table[self.leaders[0]][self.message[i]]):
                return self.message[i]
        raise Exception ("Не удалось декодировать вектор")

    def get_code_word (self, y):
    # возвращает кодовое слово по принятому вектору y
        return bm.sum_vector(y, self.get_error_vector(y))

    def get_error_vector (self, y):
    # возвращает вектор ошибок (лидер смежного класса) для принятого вектора y
        e = []
        for i in range(0, len(self.leaders)):
            if (self.table[self.leaders[i]]["Syndrome"] == syndrome_calculation(self.H, y)):
                e = list(self.leaders[i])
        if (e == []):
            raise Exception ("Не удалось декодировать вектор")
        return e

def convert_into_string (v):
# преобразует вектор v в строку
    return "".join(str(i) for i in v)


""" СТАНДАРТНОЕ РАСПОЛОЖЕНИЕ """

class StandardTable:
# Стандартное расположения для кода
    def __init__ (self, A):
        self.G = GMatrix(A)
        self.H = HMatrix(A)
        self.message = convert_lists_into_tuples(AllMessageWords(A.k).matrix)
        self.leaders = convert_lists_into_tuples(construct_all_leaders(A.n, (A.d - 1) / 2))
        self.code_words = AllCodeWords(self.G).matrix
        self.table = dict(list(zip(self.leaders, self.make_table_frame())))

    def print (self):
        for i in range(0, len(self.leaders)):
            print(self.leaders[i], self.table[self.leaders[i]])

    def make_table_frame (self):
    # строит список словарей - строк таблицы по всем лидерам смежных классов
        table_frame = []
        for i in range(0, len(self.leaders)):
            table_frame.append(self.make_table_line(self.leaders[i]))
        return table_frame

    def make_table_line (self, leader):
    # по лидеру смежного класса создает словарь - строку таблицы
        adjacent_class_elements = bm.add_vector_to_list_elements(leader, self.code_words)
        res = dict(list(zip(self.message, adjacent_class_elements)))
        res["Syndrome"] = syndrome_calculation(self.H, leader)
        return res

def syndrome_calculation (H, y):
# вычисляет значение синдрома по матрице H и вектору принятого сообщения y
    res = bm.multiply_matrices(bm.transpose_matrix(H.matrix), bm.transpose_matrix([y]))
    res = bm.transpose_matrix(res)[0]
    return res

def convert_lists_into_tuples (m):
# преобразует списки матрицы m в кортежи
    res = []
    for i in range(0, len(m)):
        res.append(tuple(m[i]))
    return res

def construct_all_leaders (n, w):
# строит список n-мерных векторов веса не более чем w
    res = []
    m = bm.construct_all_vectors(n)
    for i in range(0, len(m)):
        if bm.sum_elements(m[i]) <= w:
            res.append(m[i])
    res.sort(key = bm.sum_elements)
    return res


""" ПРОВЕРОЧНАЯ И ПОРОЖДАЮЩАЯ МАТРИЦЫ КОДА """

class GMatrix:
# порождающая матрица кода, с матрицей А
    def __init__ (self, A):
        self.n = A.n
        self.k = A.k
        self.d = A.d
        self.r = A.r
        self.matrix = bm.unit_matrix(self.k)
        self.matrix = bm.concate_matrix(self.matrix, A.matrix)
        self.matrix = bm.transpose_matrix(self.matrix)
    def print(self):
        bm.print_matrix(bm.transpose_matrix(self.matrix))
    def print_in_string_format(self):
        m = bm.transpose_matrix(self.matrix)
        for i in range(0, len(m)):
            print(convert_into_string(m[i]))

class HMatrix:
# проверочная матрица кода, с матрицей A
    def __init__ (self, A):
        self.n = A.n
        self.k = A.k
        self.d = A.d
        self.r = A.r
        self.matrix = bm.transpose_matrix(A.matrix)
        self.matrix = bm.concate_matrix(self.matrix, bm.unit_matrix(self.r))
        self.matrix = bm.transpose_matrix(self.matrix)
    def print(self):
        bm.print_matrix(bm.transpose_matrix(self.matrix))

class AMatrix:
# матрица случайных не единичных d - 1 линейно независимых векторов
    def __init__ (self, n, k, d):
        self.n = n
        self.k = k
        self.d = d
        self.r = n - k
        self.matrix = bm.unit_matrix(self.r)
        vectors = AllVectorsMatrix(self.r).matrix
        while len(self.matrix) < n:
            t1 = time.time()
            for i in range(1, (d - 2) + 1):
                vectors = bm.delete_matrix_from_matrix(vectors, bm.vector_combinations_sum_result(self.matrix, i))
                t2 = time.time()
                if (t2 - t1 > 30): raise Exception("Превышено максимально допустимое время ожидания")
            self.matrix.append(vectors[random.randint(0, len(vectors) - 1)])
        self.matrix = bm.delete_matrix_from_matrix(self.matrix, bm.unit_matrix(self.r))
    def print(self):
        bm.print_matrix(bm.transpose_matrix(self.matrix))

class AllVectorsMatrix:
# Матрица всех возможных векторов размерности n, за исключением нулевого вектора
    def __init__ (self, n):
        self.matrix = bm.construct_all_vectors(n)
        self.matrix = bm.delete_vector_from_matrix(self.matrix, bm.zero_vector(n))
        self.matrix = bm.delete_matrix_from_matrix(self.matrix, bm.unit_matrix(n))
        self.matrix = bm.transpose_matrix(bm.concate_matrix(bm.unit_matrix(n), bm.transpose_matrix(self.matrix)))
    def print (self):
        bm.print_matrix(bm.transpose_matrix(self.matrix))


""" СООБЩЕНИЯ И КОДОВЫЕ СЛОВА """

class AllCodeWords:
# список всех кодовых слов, порождаемых матрицей G
    def __init__ (self, G):
        self.message_words = AllMessageWords(G.k)
        self.matrix = bm.multiply_matrices(self.message_words.matrix, bm.transpose_matrix(G.matrix))
    def print (self):
        bm.print_matrix(self.matrix)

class AllMessageWords:
# список всех возможных двоичных векторов - слов сообщения; k - число символов сообщения
    def __init__ (self, k):
        self.matrix = bm.construct_all_vectors(k)
        self.matrix.sort(key = bm.sum_elements)
    def print (self):
        bm.print_matrix(self.matrix)


""" ГРАНИЦА ВАРШАМОВА - ГИЛБЕРТА """

class VarshamovLimit: # Проверка условия "Граница Варшамова-Гилберта"
    def __init__ (self, n, k, d):
        r = n - k
        self.list_form = []
        self.list_form.append(1)
        self.append_members(n, d)
        self.left_part = self.sum_members()
        self.right_part = 2 ** r
    def append_members (self, n, d): # Добавляет в списочную форму выражения биномиальные члены
        i = 1
        while i <= d - 2:
            self.list_form.append(bm.binomial(n - 1, i))
            i += 1
    def sum_members (self): # Суммирует левую часть условия
        i = 0
        s = 0
        while i <= len(self.list_form) - 1:
            s += self.list_form[i]
            i += 1
        return s
    def predicate (self): # Возвращает результат проверки условия "Граница Варшамова-Гилберта"
        if self.left_part < self.right_part:
            return True
        else:
            return False
