import math
import itertools



""" ОПЕРАЦИИ НАД ВЕКТОРАМИ И МАТРИЦАМИ """

""" Единчная матрица """

def unit_matrix (n):
# Строит единичную матрицу размера n
    matrix = []
    j = 1
    while j <= n:
        matrix.append(unit_vector(n, j))
        j += 1
    return matrix

def unit_vector (n, j):
# Строит вектор единичной матрицы длины n, с единицей на позиции j
    vector = []
    i = 0
    while i < n:
        if i == j - 1:
            vector.append(1)
        else:
            vector.append(0)
        i += 1
    return vector


""" Вывод матрицы на печать """

def print_matrix (m):
# Выводит матрицу построчно
    l = len(m)
    i = 0
    while i < l:
        print(m[i])
        i += 1


""" Транспонировние матрицы """

def transpose_matrix (m):
# Транспонирует матрицу m
    res = []
    i = 0
    while i < len(m[0]):
        vector = []
        j = 0
        while j < len(m):
            vector.append(m[j][i]) 
            j += 1
        res.append(vector)
        i += 1
    return res


""" Конкатенация матриц """

def concate_matrix (a, b):
# Дописывает матрицу b к матрице a
    res = []
    i = 0
    if len(a) != len(b):
        return res
    else:
        while i < len(a):
            res.append(a[i] + b[i])
            i += 1
        return res


""" Сумма векторов по mod 2 """

def sum_vector (a, b):
# Суммирует векторы a и b по модулю 2
    vector = []
    i = 0
    if len(a) != len(b): return vector
    while i < len(a):
        if a[i] == 0 and b[i] == 1 or a[i] == 1 and b[i] == 0:
            vector.append(1)
        else:
            vector.append(0)
        i += 1
    return vector


""" Удаление матрицы из матрицы """

def delete_matrix_from_matrix (matrix_origin, matrix_deleted):
# удаляет из матрицы matrix_origin матрицу marix_deleted
    res1 = matrix_origin
    for i in range(0, len(matrix_deleted)):
        res2 = delete_vector_from_matrix(res1, matrix_deleted[i])
        res1 = res2
    return res1

def delete_vector_from_matrix (m, v):
# Удаляет ветор v из матрицы m
    res = []
    for i in range(0, len(m)):
        if m[i] != v: res.append(m[i])
    return res

def zero_vector (n):
# Строит нулевой вектор длины n
    res = []
    for i in range(0, n):
        res.append(0)
    return res


""" Умножение матриц """

def multiply_matrices (m1, m2):
# перемножает матрицы m1, m2; результат приводится по mod 2
    res = []
    m2 = transpose_matrix(m2)
    for i in range(0, len(m1)):
        v = []
        for j in range(0, len(m2)):
            v.append(multiply_vectors(m1[i], m2[j]))
        res.append(v)
    return res

def multiply_vectors(v1, v2):
# поэлементно перемножает вектора v1, v2, складывает и  приводит результат по mod 2
    sum = 0
    for i in range(0, len(v1)):
        sum += (v1[i] * v2[i])
    return (sum % 2)


""" Сложение вектора с каждым вектором из заданного списка """

def add_vector_to_list_elements (v, l):
# складывает по mod 2 вектор v с каждым вектором из списка l
    res = []
    for i in range(0, len(l)):
        res.append(sum_vector(v, l[i]))
    return res


""" Сумма элементов вектора """

def sum_elements (v):
# суммирует элмементы вектора v
    res = 0
    for i in range(0, len(v)): res += v[i]
    return res



""" КОМБИНАТОРНЫЕ ПОСТРОЕНИЯ """

""" Матрица всех возможных двоичных векторов """

def construct_all_vectors(n):
# Строит матрицу всех возможных двоичных векторов размерности n
# Матрица записывается по столбцам
    res = []
    it = itertools.product('10', repeat = n)
    for i in it:
       v = []
       for j in range(0, len(i)):
           v.append(int(i[j]))
       res.append(v)
    return res


""" Комбинации и суммы комбинаций векторов матрицы """

def vector_combinations_list (m, n):
# строит список сочетаний по n векторов матрицы m 
    res = []
    it = itertools.combinations(m, n)
    for i in it:
        s = []
        for j in range(0, len(i)):
            s.append(i[j])
        res.append(s)
    return res

def sum_vector_list (vector_list):
# суммирует вектора из vector_list
    res = []
    for j in range(0, len(vector_list[0])):
        sum = 0
        for i in range(0, len(vector_list)):
            sum += vector_list[i][j]
        res.append(sum)
    return res

def vector_modulo_2 (v):
# приводит элементы вектора v по модулю 2
    res = []
    for i in range(0, len(v)):
        res.append(v[i] % 2)
    return res

def vector_combinations_sum_result (m, n):
# возвращает список результирующих сумм сочетаний n векторов матрицы m
    vector_combinations = vector_combinations_list(m, n)
    res = []
    for i in range(0, len(vector_combinations)):
        res.append(vector_modulo_2(sum_vector_list(vector_combinations[i])))
    return res


""" Биномиальный коэффициент """

def binomial (n, j):
# Возвращает значение биномиального коэффициента, C из n по j
    if j > n:
        return 0
    else:
        return int((math.factorial(n) / (math.factorial(j) * math.factorial(n - j))))
