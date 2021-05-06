import math
import scipy.integrate as integrate
from scipy.stats import norm


""" КОНСТАНТЫ И ПАРАМЕТРЫ """

AREA_UNIT_CONVERSION = 0.01
INERTION_UNIT_CONVERSION = 0.0001
METERS_UNIT_CONVERSION = 0.001
FORCE_UNIT_CONVERSION = 0.001

section_parameters = {"width": 150,
                      "height": 9,
                      "half distance": 92.5,
                      "variation": 0.002}

rod_parameters = {"length": 9000,
                  "variation": 0.0002}

material_parameters = {"elastic modulus": 2.06 * 10 ** 5,
                       "design resistance": 240,
                       "variation": 0.017}

force_parameters = {"force": 350000,
                    "variation": 0.067}


""" ВНЕШНИЙ ИНТЕРФЕЙС МОДУЛЯ """

class ReliabilityTaskSolve:
    def __init__ (self, parameters, sample_size):
        InputDataInitialize(parameters)
        self.reserve = Reserve(sample_size)
        self.total_reliability_calculate()
        self.table = {"Safety Feature": self.safety_feature,
                      "Malfunction": self.malfunction,
                      "Reliability": self.reliability,
                      "Critical Check": self.flag}

    def get_result (self):
        return self.table
    
    def total_reliability_calculate (self):
        if (self.reserve.stability_malfunction > self.reserve.strength_malfunction):
            self.safety_feature = self.reserve.stability_safety_feature
            self.malfunction = self.reserve.stability_malfunction
            self.reliability = self.reserve.stability_reliability
            self.flag = "Stability"
        else:
            self.safety_feature = self.reserve.strength_safety_feature
            self.malfunction = self.reserve.strength_malfunction
            self.reliability = self.reserve.strength_reliability
            self.flag = "Strength"

class InputDataInitialize:
    def __init__ (self, parameters):
        rod_parameters["length"] = parameters["Length"]
        force_parameters["force"] = parameters["Force"]
        section_parameters["width"] = parameters["Shelf Width"]
        section_parameters["height"] = parameters["Shelf Height"]
        section_parameters["half distance"] = parameters["Section Half Distance"]


""" ПАРАМЕТРЫ НАДЕЖНОСТИ ЗАДАЧИ ЦЕНТРАЛЬНОГО СЖАТИЯ """

class Reserve:
    def __init__ (self, size):
        self.sample = Sample(size)
        
        self.strength_reserve = self.get_strength_reserve_sample()
        self.strength_reserve_mean = get_mean(self.strength_reserve)
        self.strength_reserve_standard = get_standard_deviation(self.strength_reserve)
        self.strength_safety_feature = self.strength_reserve_mean / self.strength_reserve_standard
        self.strength_malfunction = 0.5 - safety_feature_bound_integral(self.strength_safety_feature)
        self.strength_reliability = 1 - self.strength_malfunction
        
        self.stability_reserve = self.get_stability_reserve_sample()
        self.stability_reserve_mean = get_mean(self.stability_reserve)
        self.stability_reserve_standard = get_standard_deviation(self.stability_reserve)
        self.stability_safety_feature = self.stability_reserve_mean / self.stability_reserve_standard
        self.stability_malfunction = 0.5 - safety_feature_bound_integral(self.stability_safety_feature)
        self.stability_reliability = 1 - self.stability_malfunction
    
    def get_strength_reserve_sample (self):
        res = []
        for i in range(0, len(self.sample.realization)):
            res.append(self.sample.resistance_sample[i] - self.sample.strength_sample[i])
        return res
    
    def get_stability_reserve_sample (self):
        res = []
        for i in range(0, len(self.sample.realization)):
            res.append(self.sample.resistance_sample[i] - self.sample.stability_sample[i])
        return res
    
    def print_out (self):        
        print("Среднее значение резерва несущей способности по условию прочности: {0:.2f}".format(self.strength_reserve_mean))
        print("Характеристика безопасности по условию прочности: {0:.3f}".format(self.strength_safety_feature))
        print("Вероятность отказа по условию прочности: {0:.5f}".format(self.strength_malfunction))
        print("Надежность по условию прочности: {0:.5f}".format(self.strength_reliability))
        print()
        print("Среднее значение резерва несущей способности по условию устойчивости: {0:.2f}".format(self.stability_reserve_mean))
        print("Характреристика безопасности по условию устойчивости: {0:.3f}".format(self.stability_safety_feature))
        print("Вероятность отказа по условию устойчивости: {0:.5f}".format(self.stability_malfunction))
        print("Надежность по условию устойчивости: {0:.5f}".format(self.stability_reliability))

class Sample:
    def __init__ (self, size):
        self.realization = self.generate(size)
        
        self.strength_sample = self.get_strength_sample()
        self.strength_mean = get_mean(self.strength_sample)
        self.strength_standard = get_standard_deviation(self.strength_sample)
        
        self.stability_sample = self.get_stability_sample()
        self.stability_mean = get_mean(self.stability_sample)
        self.stability_standard = get_standard_deviation(self.stability_sample)
        
        self.resistance_sample = self.get_resistance_sample()
        self.resistance_mean = get_mean(self.resistance_sample)
        self.resistance_standard = get_standard_deviation(self.resistance_sample)
        
    def generate (self, size):
        realization = []
        for i in range(0, size):
            realization.append(Tension(force_parameters))
        return realization
    
    def get_strength_sample (self):
        res = []
        for i in range(0, len(self.realization)):
            res.append(self.realization[i].strength_tension)
        return res
    
    def get_stability_sample (self):
        res = []
        for i in range(0, len(self.realization)):
            res.append(self.realization[i].stability_tension)
        return res
    
    def get_resistance_sample (self):
        sample = []
        for i in range(0, len(self.realization)):
            sample.append(self.realization[i].resistance)
        return sample
    
    def print_out (self):
        if (len(self.realization) >= 5):
            
            print("Первые пять значений напряжений по условию прочности:")
            self.print_sample(self.strength_sample, 5)
            print()
            print("Среднее значение напряжений по условию прочности: {0:.2f} Н/мм2".format(self.strength_mean))
            print("Стандартное отклонение значений напряжений по условию прочности: {0:.2f}".format(self.strength_standard))
            print()
            
            print("Первые пять значений напряжений по условию устойчивости:")
            self.print_sample(self.stability_sample, 5)
            print()
            print("Среднее значение напряжений по условию устойчивости: {0:.2f} Н/мм2".format(self.stability_mean))
            print("Стандартное отклонение значений напряжений по условию устойчивости: {0:.2f}".format(self.stability_standard))
            print()
            
            print("Первые пять значений расчетного сопротивления:")
            self.print_sample(self.resistance_sample, 5)
            print()
            print("Среднее значение расчетного сопротивления: {0:.2f} Н/мм2".format(self.resistance_mean))
            print("Стандартное отклонение значений расчетного сопротивления: {0:.2f}".format(self.resistance_standard))
            
        else:
            print("В выборке менее пяти реализаций")
    
    def print_sample (self, sample, k):
        for i in range(0, k):
            print(sample[i])

def safety_feature_bound_integral (beta):
# интегрирует фунцию плотности распределения вероятности стандартного нормального распределения
# в границах от 0 до значения характеристики безопасности
    I = integrate.quad(standard_normal_pdf_integrand, 0, beta)
    return (1 / math.sqrt(2 * math.pi)) * I[0]

def standard_normal_pdf_integrand (x):
# подынтегральная часть функции плотности распределения вероятности стандартного нормального распределения
    return math.exp(-(x ** 2 / 2))


""" РЕАЛИЗАЦИЯ РЕШЕНИЯ И ВЕЛИЧИН ЗАДАЧИ ЦЕНТРАЛЬНОГО СЖАТИЯ """

class Tension:
    def __init__ (self, parameters):
        self.rod = Rod(rod_parameters)
        self.force = value_realization(parameters["force"], parameters["variation"])
        self.strength_tension = self.force / self.rod.section.area
        self.stability_tension = self.strength_tension / self.rod.phi_coefficient
        self.resistance = self.rod.material.design_resistance
        self.strength_use = self.strength_tension / self.resistance
        self.stability_use = self.stability_tension / self.resistance
    
    def print_out (self):
        self.rod.print_out()
        print()
        print("Внешняя сила: {0:.2f} кН".format(self.force * FORCE_UNIT_CONVERSION))
        print("Напряжение по условию прочности: {0:.2f} Н/мм2".format(self.strength_tension))
        print("Напряжение по условию устойчивости: {0:.2f} Н/мм2".format(self.stability_tension))
        print()
        print("Коэффициент использования по условию прочности: {0:.3f}".format(self.strength_use))
        print("Коэффициент использования по условию устойчивости: {0:.3f}".format(self.stability_use))
        
class Rod:
    def __init__ (self, parameters):
        self.section = Section(section_parameters)
        self.material = Material(material_parameters)
        self.length = value_realization(parameters["length"], parameters["variation"])
        self.flexibility = self.length / self.section.radius
        self.material_coefficient = math.sqrt(self.material.design_resistance / self.material.elastic_modulus)
        self.conditional_flexibility = self.flexibility * self.material_coefficient
        self.phi_coefficient = get_phi_coefficient(self.conditional_flexibility)
    
    def print_out (self):
        self.section.print_out()
        print()
        self.material.print_out()
        print()
        print("Длина стержня: {0:.3f} м".format(self.length * METERS_UNIT_CONVERSION))
        print("Гибкость стержня: {0:.2f}".format(self.flexibility))
        print("Услованя гибкость стержня: {0:.2f}".format(self.conditional_flexibility))
        print("Коэффициент продольного изгиба: {0:.3f}".format(self.phi_coefficient))

class Material:
    def __init__ (self, parameters):
        self.elastic_modulus = value_realization(parameters["elastic modulus"], parameters["variation"])
        self.design_resistance = value_realization(parameters["design resistance"], parameters["variation"])
        
    def print_out (self):
        print("Модуль упругости: {0:.2f} Н/мм2".format(self.elastic_modulus))
        print("Расчетное сопротивление: {0:.2f} Н/мм2".format(self.design_resistance))

class Section:
    def __init__ (self, parameters):
        self.shelf = Shelf(section_parameters)
        self.half_distance = value_realization(parameters["half distance"], parameters["variation"])
        self.area = 2 * self.shelf.area
        self.inertion = 2 * self.shelf.area * self.half_distance ** 2
        self.radius = self.half_distance
        
    def print_out (self):
        self.shelf.print_out()
        print("Половина расстояния между центрами полок: {0:.2f} мм".format(self.half_distance))
        print()
        print("Площадь сечения: {0:.2f} см2".format(self.area * AREA_UNIT_CONVERSION))
        print("Момент инерции сечения: {0:.2f} см4".format(self.inertion * INERTION_UNIT_CONVERSION))
        print("Радиус инерции: {0:.2f} мм".format(self.radius))
        
class Shelf:
    def __init__ (self, parameters):
        self.width = value_realization(parameters["width"], parameters["variation"])
        self.height = value_realization(parameters["height"], parameters["variation"])
        self.area = self.width * self.height
        
    def print_out (self):
        print("Ширина полки: {0:.2f} мм".format(self.width))
        print("Толщина полки: {0:.2f} мм".format(self.height))
        print("Площадь полки: {0:.2f} см2".format(self.area * AREA_UNIT_CONVERSION))


""" СТАТИСТИЧЕСКИЕ ФУНКЦИИ """

def value_realization (mean, variation_coefficient):
# возвращает реализацию случайной величины по заданному мат. ожиданию и коэффициенту вариации
    return mean + norm.rvs() * mean * variation_coefficient

def get_mean (sample):
# возвращает выборочное среднее значений выборки sample
    n = len(sample)
    sum = 0
    for i in range(0, n):
        sum += sample[i]
    return (1 / n) * sum

def get_dispersion_unbaised_estimate (sample):
# возвращает несмещенную оценку дисперсии значений выборки sample
    n = len(sample)
    sum = 0
    mean = get_mean(sample)
    for i in range (0, n):
        sum += (sample[i] - mean) ** 2
    return (1 / (n - 1)) * sum

def get_standard_deviation (sample):
# возвращает стандартное отклонение (стандарт) значений выборки sample
    return math.sqrt(get_dispersion_unbaised_estimate(sample))


""" ТАБЛИЦА КОЭФФИЦИЕНТОВ ПРОДОЛЬНОГО ИЗГИБА """

phi_table_value = [1000, 986, 967, 948, 927, 905, 881, 855, 826, 794, 760, 723, 683, 643, 602, 562, 524,
                   487, 453, 422, 392, 359, 330, 304, 281, 261, 242, 226, 211, 198, 186, 174, 164, 155, 147,
                   139, 132, 125, 119, 105, 94, 84, 76]
phi_table_key = [round(i * 0.1, 1) for i in range(4, 80, 2)] + [round(i * 0.1, 1) for i in range(80, 105, 5)]
phi_table = list(zip(phi_table_key, phi_table_value))

def get_phi_coefficient (lam):
# возвращает значение коэффициента продольного изгиба по условной гибкости conditional_lam
    k = -2
    for i in phi_table:
        k += 1
        if lam < 0.4:
            return 0
        elif lam == i[0]:
            return i[1] * 0.001
        elif lam < i[0]:
            j = phi_table[k]
            return ((lam - j[0]) * ((i[1] - j[1]) / (i[0] - j[0])) + j[1]) * 0.001
    return 0

