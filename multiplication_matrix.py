import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
import time
import re

class Tensor:
    def __init__(self, dimension, data=None):
        self.dimension = dimension
        if data is None:
            self.data = {}
        else:
            self.data = data

    def add_value(self, indices, value):
        self.data[tuple(indices)] = value

    def get_value(self, indices):
        return self.data.get(tuple(indices), 0)

    def get_all_indices(self):
        return list(self.data.keys())

    def to_nested_list(self):
        """Преобразование тензора во вложенное списковое представление"""
        if not self.data:
            return []

        # Найдём форму
        shape = []
        for indices in self.data.keys():
            for i, idx in enumerate(indices):
                if i >= len(shape):
                    shape.append(idx + 1)
                else:
                    shape[i] = max(shape[i], idx + 1)

        # Создание структуры вложенного списка
        result = self._create_nested_list(shape)

        # Заполнить значениями
        for indices, value in self.data.items():
            self._set_value_in_list(result, indices, value)

        return result

    def _create_nested_list(self, shape):
        """Создаём пустой вложенный список заданной формы"""
        if len(shape) == 1:
            return [0.0] * shape[0]
        else:
            return [self._create_nested_list(shape[1:]) for _ in range(shape[0])]

    def _set_value_in_list(self, lst, indices, value):
        """Установим значение во вложенном списке по заданным индексам"""
        if len(indices) == 1:
            lst[indices[0]] = value
        else:
            self._set_value_in_list(lst[indices[0]], indices[1:], value)

    def get_shape(self):
        """Получаем форму тензора"""
        if not self.data:
            return ()

        shape = []
        for indices in self.data.keys():
            for i, idx in enumerate(indices):
                if i >= len(shape):
                    shape.append(idx + 1)
                else:
                    shape[i] = max(shape[i], idx + 1)

        return tuple(shape)

    @classmethod
    def from_nested_list(cls, nested_list):
        """Создаём тензор из вложенного списка"""
        data = {}
        dimension = cls._get_dimension(nested_list)
        cls._fill_data_from_list(nested_list, (), data)
        return cls(dimension, data)

    @staticmethod
    def _get_dimension(lst):
        """Вычислить размер вложенного списка"""
        if not isinstance(lst, list) or len(lst) == 0:
            return 0
        return 1 + Tensor._get_dimension(lst[0])

    @staticmethod
    def _fill_data_from_list(lst, current_indices, data):
        """Рекурсивно заполнять тензорные данные из вложенного списка"""
        if isinstance(lst, list):
            for i, item in enumerate(lst):
                Tensor._fill_data_from_list(item, current_indices + (i,), data)
        else:
            data[current_indices] = lst

class MunermanTensorMultiplier:
    @staticmethod
    def method1_cayley_square(tensor_a, tensor_b):
        """(0,2)-свернутое произведение для 3D тензоров"""
        result_data = {}
        for key_a, value_a in tensor_a.data.items():
            i1, i2, i3 = key_a
            for key_b, value_b in tensor_b.data.items():
                j1, j2, j3 = key_b
                # Кэлиевы индексы: A(i2,i3) = B(i1,i2)
                if i2 == j1 and i3 == j2:
                    new_key = (i1, j3)  # Свободные: A(i1), B(i3)
                    result_data[new_key] = result_data.get(new_key, 0) + value_a * value_b
        return Tensor(2, result_data)

    @staticmethod
    def method1_cayley_4d(tensor_a, tensor_b):
        """(0,2)-свернутое произведение для 4D тензоров"""
        result_data = {}
        for key_a, value_a in tensor_a.data.items():
            i1, i2, i3, i4 = key_a
            for key_b, value_b in tensor_b.data.items():
                j1, j2, j3, j4 = key_b
                # Кэлиевы индексы: A(i3,i4) = B(i1,i2)
                if i3 == j1 and i4 == j2:
                    new_key = (i1, i2, j3, j4)  # Свободные: A(i1,i2), B(i3,i4)
                    result_data[new_key] = result_data.get(new_key, 0) + value_a * value_b
        return Tensor(4, result_data)

    @staticmethod
    def method1_cayley_3d_4d(tensor_a, tensor_b):
        """(0,2)-свернутое произведение для 3D×4D тензоров"""
        result_data = {}
        for key_a, value_a in tensor_a.data.items():
            i1, i2, i3 = key_a
            for key_b, value_b in tensor_b.data.items():
                j1, j2, j3, j4 = key_b
                # Кэлиевы индексы: A(i2,i3) = B(i1,i2)
                if i2 == j1 and i3 == j2:
                    new_key = (i1, j3, j4)  # Свободные: A(i1), B(i3,i4)
                    result_data[new_key] = result_data.get(new_key, 0) + value_a * value_b
        return Tensor(3, result_data)

    @staticmethod
    def method1_cayley_4d_3d(tensor_a, tensor_b):
        """(0,2)-свернутое произведение для 4D×3D тензоров"""
        result_data = {}
        for key_a, value_a in tensor_a.data.items():
            i1, i2, i3, i4 = key_a
            for key_b, value_b in tensor_b.data.items():
                j1, j2, j3 = key_b
                # Кэлиевы индексы: A(i3,i4) = B(i1,i2)
                if i3 == j1 and i4 == j2:
                    new_key = (i1, i2, j3)  # Свободные: A(i1,i2), B(i3)
                    result_data[new_key] = result_data.get(new_key, 0) + value_a * value_b
        return Tensor(3, result_data)

    @staticmethod
    def method2_cayley_square(tensor_a, tensor_b):
        """(0,1)-свернутое произведение для 3D тензоров"""
        result_data = {}
        for key_a, value_a in tensor_a.data.items():
            i1, i2, i3 = key_a
            for key_b, value_b in tensor_b.data.items():
                j1, j2, j3 = key_b
                # Кэлиев индекс: A(i3) = B(i1)
                if i3 == j1:
                    new_key = (i1, i2, j2, j3)  # Свободные: A(i1,i2), B(i2,i3)
                    result_data[new_key] = result_data.get(new_key, 0) + value_a * value_b
        return Tensor(4, result_data)

    @staticmethod
    def method2_cayley_4d(tensor_a, tensor_b):
        """(0,1)-свернутое произведение для 4D тензоров"""
        result_data = {}
        for key_a, value_a in tensor_a.data.items():
            i1, i2, i3, i4 = key_a
            for key_b, value_b in tensor_b.data.items():
                j1, j2, j3, j4 = key_b
                # Кэлиев индекс: A(i4) = B(i1)
                if i4 == j1:
                    new_key = (i1, i2, i3, j2, j3, j4)  # Свободные: A(i1,i2,i3), B(i2,i3,i4)
                    result_data[new_key] = result_data.get(new_key, 0) + value_a * value_b
        return Tensor(6, result_data)

    @staticmethod
    def method2_cayley_3d_4d(tensor_a, tensor_b):
        """(0,1)-свернутое произведение для 3D×4D тензоров"""
        result_data = {}
        for key_a, value_a in tensor_a.data.items():
            i1, i2, i3 = key_a
            for key_b, value_b in tensor_b.data.items():
                j1, j2, j3, j4 = key_b
                # Кэлиев индекс: A(i3) = B(i1)
                if i3 == j1:
                    new_key = (i1, i2, j2, j3, j4)  # Свободные: A(i1,i2), B(i2,i3,i4)
                    result_data[new_key] = result_data.get(new_key, 0) + value_a * value_b
        return Tensor(5, result_data)

    @staticmethod
    def method2_cayley_4d_3d(tensor_a, tensor_b):
        """(0,1)-свернутое произведение для 4D×3D тензоров"""
        result_data = {}
        for key_a, value_a in tensor_a.data.items():
            i1, i2, i3, i4 = key_a
            for key_b, value_b in tensor_b.data.items():
                j1, j2, j3 = key_b
                # Кэлиев индекс: A(i4) = B(i1)
                if i4 == j1:
                    new_key = (i1, i2, i3, j2, j3)  # Свободные: A(i1,i2,i3), B(i2,i3)
                    result_data[new_key] = result_data.get(new_key, 0) + value_a * value_b
        return Tensor(5, result_data)

    @staticmethod
    def method3_scott_square(tensor_a, tensor_b):
        """(2,0)-свернутое произведение для 3D тензоров"""
        result_data = {}
        for key_a, value_a in tensor_a.data.items():
            i1, i2, i3 = key_a
            for key_b, value_b in tensor_b.data.items():
                j1, j2, j3 = key_b
                # Скоттовы индексы: A(i2,i3) = B(i1,i2)
                if i2 == j1 and i3 == j2:
                    new_key = (i1, i2, i3, j3)  # Свободные: A(i1,i2,i3), B(i3)
                    result_data[new_key] = value_a * value_b  # Без суммирования!
        return Tensor(4, result_data)

    @staticmethod
    def method3_scott_4d(tensor_a, tensor_b):
        """(2,0)-свернутое произведение для 4D тензоров"""
        result_data = {}
        for key_a, value_a in tensor_a.data.items():
            i1, i2, i3, i4 = key_a
            for key_b, value_b in tensor_b.data.items():
                j1, j2, j3, j4 = key_b
                # Скоттовы индексы: A(i3,i4) = B(i1,i2)
                if i3 == j1 and i4 == j2:
                    new_key = (i1, i2, i3, i4, j3, j4)  # Свободные: A(i1,i2,i3,i4), B(i3,i4)
                    result_data[new_key] = value_a * value_b  # Без суммирования!
        return Tensor(6, result_data)

    @staticmethod
    def method3_scott_3d_4d(tensor_a, tensor_b):
        """(2,0)-свернутое произведение для 3D×4D тензоров"""
        result_data = {}
        for key_a, value_a in tensor_a.data.items():
            i1, i2, i3 = key_a
            for key_b, value_b in tensor_b.data.items():
                j1, j2, j3, j4 = key_b
                # Скоттовы индексы: A(i2,i3) = B(i1,i2)
                if i2 == j1 and i3 == j2:
                    new_key = (i1, i2, i3, j3, j4)  # Свободные: A(i1,i2,i3), B(i3,i4)
                    result_data[new_key] = value_a * value_b  # Без суммирования!
        return Tensor(5, result_data)

    @staticmethod
    def method3_scott_4d_3d(tensor_a, tensor_b):
        """(2,0)-свернутое произведение для 4D×3D тензоров"""
        result_data = {}
        for key_a, value_a in tensor_a.data.items():
            i1, i2, i3, i4 = key_a
            for key_b, value_b in tensor_b.data.items():
                j1, j2, j3 = key_b
                # Скоттовы индексы: A(i3,i4) = B(i1,i2)
                if i3 == j1 and i4 == j2:
                    new_key = (i1, i2, i3, i4, j3)  # Свободные: A(i1,i2,i3,i4), B(i3)
                    result_data[new_key] = value_a * value_b  # Без суммирования!
        return Tensor(5, result_data)

    @staticmethod
    def method4_scott_square(tensor_a, tensor_b):
        """(1,0)-свернутое произведение для 3D тензоров"""
        result_data = {}
        for key_a, value_a in tensor_a.data.items():
            i1, i2, i3 = key_a
            for key_b, value_b in tensor_b.data.items():
                j1, j2, j3 = key_b
                # Скоттов индекс: A(i3) = B(i1)
                if i3 == j1:
                    new_key = (i1, i2, i3, j2, j3)  # Свободные: A(i1,i2,i3), B(i2,i3)
                    result_data[new_key] = value_a * value_b  # Без суммирования!
        return Tensor(5, result_data)

    @staticmethod
    def method4_scott_4d(tensor_a, tensor_b):
        """(1,0)-свернутое произведение для 4D тензоров"""
        result_data = {}
        for key_a, value_a in tensor_a.data.items():
            i1, i2, i3, i4 = key_a
            for key_b, value_b in tensor_b.data.items():
                j1, j2, j3, j4 = key_b
                # Скоттов индекс: A(i4) = B(i1)
                if i4 == j1:
                    new_key = (i1, i2, i3, i4, j2, j3, j4)  # Свободные: A(i1,i2,i3,i4), B(i2,i3,i4)
                    result_data[new_key] = value_a * value_b  # Без суммирования!
        return Tensor(7, result_data)

    @staticmethod
    def method4_scott_3d_4d(tensor_a, tensor_b):
        """(1,0)-свернутое произведение для 3D×4D тензоров"""
        result_data = {}
        for key_a, value_a in tensor_a.data.items():
            i1, i2, i3 = key_a
            for key_b, value_b in tensor_b.data.items():
                j1, j2, j3, j4 = key_b
                # Скоттов индекс: A(i3) = B(i1)
                if i3 == j1:
                    new_key = (i1, i2, i3, j2, j3, j4)  # Свободные: A(i1,i2,i3), B(i2,i3,i4)
                    result_data[new_key] = value_a * value_b  # Без суммирования!
        return Tensor(6, result_data)

    @staticmethod
    def method4_scott_4d_3d(tensor_a, tensor_b):
        """(1,0)-свернутое произведение для 4D×3D тензоров"""
        result_data = {}
        for key_a, value_a in tensor_a.data.items():
            i1, i2, i3, i4 = key_a
            for key_b, value_b in tensor_b.data.items():
                j1, j2, j3 = key_b
                # Скоттов индекс: A(i4) = B(i1)
                if i4 == j1:
                    new_key = (i1, i2, i3, i4, j2, j3)  # Свободные: A(i1,i2,i3,i4), B(i2,i3)
                    result_data[new_key] = value_a * value_b  # Без суммирования!
        return Tensor(6, result_data)

    @staticmethod
    def method5_combined_square(tensor_a, tensor_b):
        """(1,1)-свернутое произведение для 3D тензоров"""
        result_data = {}
        for key_a, value_a in tensor_a.data.items():
            i1, i2, i3 = key_a
            for key_b, value_b in tensor_b.data.items():
                j1, j2, j3 = key_b
                # Кэлиев: A(i3) = B(i1), Скоттов: A(i2) = B(i2)
                if i3 == j1 and i2 == j2:
                    new_key = (i1, i2, j3)  # Свободные: A(i1,i2), B(i3)
                    result_data[new_key] = result_data.get(new_key, 0) + value_a * value_b
        return Tensor(3, result_data)

    @staticmethod
    def method5_combined_4d(tensor_a, tensor_b):
        """(1,1)-свернутое произведение для 4D тензоров"""
        result_data = {}
        for key_a, value_a in tensor_a.data.items():
            i1, i2, i3, i4 = key_a
            for key_b, value_b in tensor_b.data.items():
                j1, j2, j3, j4 = key_b
                # Кэлиев: A(i4) = B(i1), Скоттов: A(i3) = B(i2)
                if i4 == j1 and i3 == j2:
                    new_key = (i1, i2, i3, j3, j4)  # Свободные: A(i1,i2,i3), B(i3,i4)
                    result_data[new_key] = result_data.get(new_key, 0) + value_a * value_b
        return Tensor(5, result_data)

    @staticmethod
    def method5_combined_3d_4d(tensor_a, tensor_b):
        """(1,1)-свернутое произведение для 3D×4D тензоров"""
        result_data = {}
        for key_a, value_a in tensor_a.data.items():
            i1, i2, i3 = key_a
            for key_b, value_b in tensor_b.data.items():
                j1, j2, j3, j4 = key_b
                # Кэлиев: A(i3) = B(i1), Скоттов: A(i2) = B(i2)
                if i3 == j1 and i2 == j2:
                    new_key = (i1, i2, j3, j4)  # Свободные: A(i1,i2), B(i3,i4)
                    result_data[new_key] = result_data.get(new_key, 0) + value_a * value_b
        return Tensor(4, result_data)

    @staticmethod
    def method5_combined_4d_3d(tensor_a, tensor_b):
        """(1,1)-свернутое произведение для 4D×3D тензоров"""
        result_data = {}
        for key_a, value_a in tensor_a.data.items():
            i1, i2, i3, i4 = key_a
            for key_b, value_b in tensor_b.data.items():
                j1, j2, j3 = key_b
                # Кэлиев: A(i4) = B(i1), Скоттов: A(i3) = B(i2)
                if i4 == j1 and i3 == j2:
                    new_key = (i1, i2, i3, j3)  # Свободные: A(i1,i2,i3), B(i3)
                    result_data[new_key] = result_data.get(new_key, 0) + value_a * value_b
        return Tensor(4, result_data)

class TensorOperations:
    @staticmethod
    def multiply_tensors(tensor_a, tensor_b, method, dimension_type):
        """
        Умножение тензоров с использованием указанного метода

        Args:
            tensor_a: первый тензор
            tensor_b: второй тензор
            method: номер метода (1-5)
            dimension_type: тип размерности ('square' для 3D, '4d' для 4D, 'mixed' для смешанного)
        """
        multiplier = MunermanTensorMultiplier()

        # Определяем тип умножения на основе размерностей тензоров
        if tensor_a.dimension == 3 and tensor_b.dimension == 3:
            dim_type = 'square'
        elif tensor_a.dimension == 4 and tensor_b.dimension == 4:
            dim_type = '4d'
        elif tensor_a.dimension == 3 and tensor_b.dimension == 4:
            dim_type = '3d_4d'
        elif tensor_a.dimension == 4 and tensor_b.dimension == 3:
            dim_type = '4d_3d'
        else:
            raise ValueError(f"Неподдерживаемые тензорные размеры: A={tensor_a.dimension}D, B={tensor_b.dimension}D")

        if method == 1:
            if dim_type == 'square':
                return multiplier.method1_cayley_square(tensor_a, tensor_b)
            elif dim_type == '4d':
                return multiplier.method1_cayley_4d(tensor_a, tensor_b)
            elif dim_type == '3d_4d':
                return multiplier.method1_cayley_3d_4d(tensor_a, tensor_b)
            elif dim_type == '4d_3d':
                return multiplier.method1_cayley_4d_3d(tensor_a, tensor_b)

        elif method == 2:
            if dim_type == 'square':
                return multiplier.method2_cayley_square(tensor_a, tensor_b)
            elif dim_type == '4d':
                return multiplier.method2_cayley_4d(tensor_a, tensor_b)
            elif dim_type == '3d_4d':
                return multiplier.method2_cayley_3d_4d(tensor_a, tensor_b)
            elif dim_type == '4d_3d':
                return multiplier.method2_cayley_4d_3d(tensor_a, tensor_b)

        elif method == 3:
            if dim_type == 'square':
                return multiplier.method3_scott_square(tensor_a, tensor_b)
            elif dim_type == '4d':
                return multiplier.method3_scott_4d(tensor_a, tensor_b)
            elif dim_type == '3d_4d':
                return multiplier.method3_scott_3d_4d(tensor_a, tensor_b)
            elif dim_type == '4d_3d':
                return multiplier.method3_scott_4d_3d(tensor_a, tensor_b)

        elif method == 4:
            if dim_type == 'square':
                return multiplier.method4_scott_square(tensor_a, tensor_b)
            elif dim_type == '4d':
                return multiplier.method4_scott_4d(tensor_a, tensor_b)
            elif dim_type == '3d_4d':
                return multiplier.method4_scott_3d_4d(tensor_a, tensor_b)
            elif dim_type == '4d_3d':
                return multiplier.method4_scott_4d_3d(tensor_a, tensor_b)

        elif method == 5:
            if dim_type == 'square':
                return multiplier.method5_combined_square(tensor_a, tensor_b)
            elif dim_type == '4d':
                return multiplier.method5_combined_4d(tensor_a, tensor_b)
            elif dim_type == '3d_4d':
                return multiplier.method5_combined_3d_4d(tensor_a, tensor_b)
            elif dim_type == '4d_3d':
                return multiplier.method5_combined_4d_3d(tensor_a, tensor_b)

        else:
            raise ValueError(f"Неизвестный метод: {method}")

class MatrixApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Многомерные матрицы Спиридонов")
        self.root.geometry("1000x700")

        # Переменные для хранения тензоров
        self.tensor_a = None
        self.tensor_b = None
        self.result_tensor = None

        self.create_widgets()

    def create_widgets(self):
        # Создание вкладок
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Вкладка создания матриц
        creation_frame = ttk.Frame(notebook)
        notebook.add(creation_frame, text="Создание матриц")

        # Вкладка умножения
        multiplication_frame = ttk.Frame(notebook)
        notebook.add(multiplication_frame, text="Умножение матриц")

        # Вкладка результатов
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="Результаты")

        self.setup_creation_tab(creation_frame)
        self.setup_multiplication_tab(multiplication_frame)
        self.setup_results_tab(results_frame)

    def setup_creation_tab(self, parent):
        # Фрейм для матрицы A
        frame_a = ttk.LabelFrame(parent, text="Матрица A", padding=10)
        frame_a.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        ttk.Label(frame_a, text="Размерность:").grid(row=0, column=0, sticky='w')
        self.dim_a = ttk.Combobox(frame_a, values=["3D", "4D"], state="readonly")
        self.dim_a.set("3D")
        self.dim_a.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_a, text="Форма (через запятую):").grid(row=1, column=0, sticky='w')
        self.shape_a = ttk.Entry(frame_a, width=20)
        self.shape_a.grid(row=1, column=1, padx=5, pady=5)
        self.shape_a.insert(0, "2,2,2")

        ttk.Button(frame_a, text="Создать случайную",
                   command=lambda: self.create_random_tensor('A')).grid(row=2, column=0, columnspan=2, pady=5)

        ttk.Button(frame_a, text="Ввести вручную",
                   command=lambda: self.open_matrix_editor('A')).grid(row=3, column=0, columnspan=2, pady=5)

        ttk.Button(frame_a, text="Показать полную матрицу",
                   command=lambda: self.show_full_tensor('A')).grid(row=4, column=0, columnspan=2, pady=5)

        self.tensor_a_info = ttk.Label(frame_a, text="Матрица A не создана")
        self.tensor_a_info.grid(row=5, column=0, columnspan=2, pady=5)

        # Фрейм для матрицы B
        frame_b = ttk.LabelFrame(parent, text="Матрица B", padding=10)
        frame_b.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        ttk.Label(frame_b, text="Размерность:").grid(row=0, column=0, sticky='w')
        self.dim_b = ttk.Combobox(frame_b, values=["3D", "4D"], state="readonly")
        self.dim_b.set("3D")
        self.dim_b.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_b, text="Форма (через запятую):").grid(row=1, column=0, sticky='w')
        self.shape_b = ttk.Entry(frame_b, width=20)
        self.shape_b.grid(row=1, column=1, padx=5, pady=5)
        self.shape_b.insert(0, "2,2,2")

        ttk.Button(frame_b, text="Создать случайную",
                   command=lambda: self.create_random_tensor('B')).grid(row=2, column=0, columnspan=2, pady=5)

        ttk.Button(frame_b, text="Ввести вручную",
                   command=lambda: self.open_matrix_editor('B')).grid(row=3, column=0, columnspan=2, pady=5)

        ttk.Button(frame_b, text="Показать полную матрицу",
                   command=lambda: self.show_full_tensor('B')).grid(row=4, column=0, columnspan=2, pady=5)

        self.tensor_b_info = ttk.Label(frame_b, text="Матрица B не создана")
        self.tensor_b_info.grid(row=5, column=0, columnspan=2, pady=5)

        # Информационная панель
        info_frame = ttk.LabelFrame(parent, text="Информация", padding=10)
        info_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='we')

        self.info_text = scrolledtext.ScrolledText(info_frame, height=12, width=80)
        self.info_text.pack(fill='both', expand=True)
        self.info_text.insert('1.0', "Добро пожаловать в приложение для работы с многомерными матрицами!\n\n")
        self.info_text.insert('end', "Примеры форм матриц:\n")
        self.info_text.insert('end', "- 3D: [2,2,2], [2,3,2], [3,2,2]\n")
        self.info_text.insert('end', "- 4D: [2,2,2,2], [2,2,3,2], [2,3,2,2]\n\n")
        self.info_text.insert('end', "Методы умножения:\n")
        self.info_text.insert('end', "1. (0,2)-свернутое произведение - Кэлиевы индексы\n")
        self.info_text.insert('end', "2. (0,1)-свернутое произведение - Кэлиев индекс\n")
        self.info_text.insert('end', "3. (2,0)-свернутое произведение - Скоттовы индексы\n")
        self.info_text.insert('end', "4. (1,0)-свернутое произведение - Скоттов индекс\n")
        self.info_text.insert('end', "5. (1,1)-свернутое произведение - Смешанные индексы\n")

        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

    def setup_multiplication_tab(self, parent):
        ttk.Label(parent, text="Выберите метод умножения:").pack(pady=10)

        self.method_var = tk.StringVar(value="1")

        methods_frame = ttk.Frame(parent)
        methods_frame.pack(pady=10)

        methods = [
            ("1. (0,2)-свернутое произведение - Кэлиевы индексы", "1"),
            ("2. (0,1)-свернутое произведение - Кэлиев индекс", "2"),
            ("3. (2,0)-свернутое произведение - Скоттовы индексы", "3"),
            ("4. (1,0)-свернутое произведение - Скоттов индекс", "4"),
            ("5. (1,1)-свернутое произведение - Смешанные индексы", "5")
        ]

        for text, value in methods:
            ttk.Radiobutton(methods_frame, text=text, variable=self.method_var,
                            value=value).pack(anchor='w')

        ttk.Button(parent, text="Выполнить умножение",
                   command=self.perform_multiplication).pack(pady=20)

        self.mult_info = ttk.Label(parent, text="")
        self.mult_info.pack(pady=10)

    def setup_results_tab(self, parent):
        self.results_text = scrolledtext.ScrolledText(parent, height=20, width=80)
        self.results_text.pack(fill='both', expand=True, padx=10, pady=10)

        ttk.Button(parent, text="Очистить результаты",
                   command=self.clear_results).pack(pady=10)

    def create_random_tensor(self, tensor_type):
        try:
            if tensor_type == 'A':
                shape_str = self.shape_a.get()
                dim = self.dim_a.get()
            else:
                shape_str = self.shape_b.get()
                dim = self.dim_b.get()

            shape = tuple(map(int, shape_str.split(',')))

            # Проверка размерности
            if dim == "3D" and len(shape) != 3:
                raise ValueError("Для 3D матрицы нужно 3 размера")
            elif dim == "4D" and len(shape) != 4:
                raise ValueError("Для 4D матрицы нужно 4 размера")

            # Создаем случайный тензор
            tensor = self.generate_random_tensor(shape)

            if tensor_type == 'A':
                self.tensor_a = tensor
                shape_str = "x".join(map(str, tensor.get_shape()))
                self.tensor_a_info.config(text=f"Матрица A: {shape_str}")
                self.log_info(f"Создана случайная матрица A формы {shape_str}")
            else:
                self.tensor_b = tensor
                shape_str = "x".join(map(str, tensor.get_shape()))
                self.tensor_b_info.config(text=f"Матрица B: {shape_str}")
                self.log_info(f"Создана случайная матрица B формы {shape_str}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Неверные параметры: {str(e)}")

    def generate_random_tensor(self, shape):
        """Создает случайный тензор заданной формы"""
        tensor = Tensor(len(shape))

        # Генерируем все возможные комбинации индексов
        indices = [list(range(dim)) for dim in shape]
        from itertools import product
        for idx in product(*indices):
            value = round(random.uniform(0, 10), 2)
            tensor.add_value(idx, value)

        return tensor

    def open_matrix_editor(self, matrix_type):
        editor = MatrixEditor(self.root, matrix_type, self)
        self.root.wait_window(editor)

    def set_tensor_from_editor(self, matrix_type, tensor):
        if matrix_type == 'A':
            self.tensor_a = tensor
            shape_str = "x".join(map(str, tensor.get_shape()))
            self.tensor_a_info.config(text=f"Матрица A: {shape_str}")
            self.log_info(f"Создана матрица A формы {shape_str}")
        else:
            self.tensor_b = tensor
            shape_str = "x".join(map(str, tensor.get_shape()))
            self.tensor_b_info.config(text=f"Матрица B: {shape_str}")
            self.log_info(f"Создана матрица B формы {shape_str}")

    def show_full_tensor(self, tensor_type):
        if tensor_type == 'A':
            tensor = self.tensor_a
            title = "Матрица A"
        else:
            tensor = self.tensor_b
            title = "Матрица B"

        if tensor is None:
            messagebox.showwarning("Предупреждение", f"{title} не создана!")
            return

        # Создаем новое окно для отображения матрицы
        tensor_window = tk.Toplevel(self.root)
        tensor_window.title(f"Полный просмотр {title}")
        tensor_window.geometry("600x500")
        tensor_window.minsize(400, 300)

        # Основной контейнер
        main_container = ttk.Frame(tensor_window)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Настраиваем веса
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=0)

        # Создаем текстовое поле с прокруткой
        text_area = scrolledtext.ScrolledText(main_container, wrap=tk.WORD)
        text_area.grid(row=0, column=0, sticky='nsew', pady=(0, 10))

        # Преобразуем тензор в строку в формате Соколова
        tensor_text = self.matrix_to_string_sokolov(tensor.to_nested_list())
        text_area.insert(tk.END, f"{title}:\n\n{tensor_text}")
        text_area.config(state=tk.DISABLED)

        # Фрейм для кнопок - компактный, как в редакторе
        button_frame = ttk.Frame(main_container)
        button_frame.grid(row=1, column=0, sticky='')

        # Кнопки с естественным размером (не растягиваются)
        ttk.Button(button_frame, text="Скопировать матрицу",
                   command=lambda: self.copy_tensor_to_clipboard(tensor_text, tensor_window)) \
            .pack(side='left', padx=5)

        ttk.Button(button_frame, text="Закрыть",
                   command=tensor_window.destroy) \
            .pack(side='left', padx=5)

    def copy_tensor_to_clipboard(self, tensor_text, tensor_window):
        self.root.clipboard_clear()
        self.root.clipboard_append(tensor_text)
        tensor_window.destroy()

    def matrix_to_string_sokolov(self, matrix):
        """Преобразование матрицы в строку по частичному методу Соколова"""
        if isinstance(matrix, (int, float)):
            return f"{matrix:.2f}"

        if isinstance(matrix, list):
            if len(matrix) == 0:
                return "[]"

            # Определяем размерность матрицы
            dim = self.get_tensor_dimension(matrix)

            if dim == 1:
                # 1D - простой список
                elements = [f"{x:.2f}" for x in matrix]
                return "[" + ", ".join(elements) + "]"
            elif dim == 2:
                # 2D - используем точку с запятой между строками
                rows = []
                for row in matrix:
                    if isinstance(row, list):
                        elements = [f"{x:.2f}" for x in row]
                        rows.append("[" + ", ".join(elements) + "]")
                    else:
                        rows.append(f"{row:.2f}")
                return "[" + "; ".join(rows) + "]"
            else:
                # 3D+ - рекурсивная обработка с разными разделителями
                return self._format_nd_matrix_sokolov(matrix, dim)

        return str(matrix)

    def _format_nd_matrix_sokolov(self, matrix, dim, current_level=0):
        """Рекурсивное форматирование многомерной матрицы по частичному методу Соколова"""
        if not isinstance(matrix, list) or len(matrix) == 0:
            return "[]"

        if current_level == dim - 1:
            # Самый внутренний уровень - элементы через запятую
            elements = [
                f"{x:.2f}" if isinstance(x, (int, float)) else self._format_nd_matrix_sokolov(x, dim, current_level + 1)
                for x in matrix]
            return "[" + ", ".join(elements) + "]"
        elif current_level == dim - 2:
            # Предпоследний уровень - через точку с запятой
            elements = [self._format_nd_matrix_sokolov(x, dim, current_level + 1) for x in matrix]
            return "[" + "; ".join(elements) + "]"
        else:
            # Внешние уровни - через запятую с переносами
            elements = []
            for i, item in enumerate(matrix):
                element_str = self._format_nd_matrix_sokolov(item, dim, current_level + 1)
                if i < len(matrix) - 1:
                    elements.append(element_str + ",")
                else:
                    elements.append(element_str)

            indent = "  " * (current_level + 1)
            return "[\n" + indent + ("\n" + indent).join(elements) + "\n" + "  " * current_level + "]"

    def get_tensor_dimension(self, tensor):
        """Определение размерности тензора"""
        if not isinstance(tensor, list) or len(tensor) == 0:
            return 0
        return 1 + self.get_tensor_dimension(tensor[0])

    def get_tensor_shape_str(self, tensor):
        shape = self.get_tensor_shape(tensor)
        return "x".join(map(str, shape))

    def get_tensor_shape(self, tensor):
        if isinstance(tensor, (int, float)):
            return ()
        if isinstance(tensor, list):
            if len(tensor) == 0:
                return (0,)
            return (len(tensor),) + self.get_tensor_shape(tensor[0])
        return ()

    def perform_multiplication(self):
        if self.tensor_a is None or self.tensor_b is None:
            messagebox.showwarning("Предупреждение", "Сначала создайте обе матрицы!")
            return

        method = int(self.method_var.get())

        # Определяем тип умножения на основе размерностей тензоров
        if self.tensor_a.dimension == 3 and self.tensor_b.dimension == 3:
            dim_type = 'square'
        elif self.tensor_a.dimension == 4 and self.tensor_b.dimension == 4:
            dim_type = '4d'
        elif self.tensor_a.dimension == 3 and self.tensor_b.dimension == 4:
            dim_type = '3d_4d'
        elif self.tensor_a.dimension == 4 and self.tensor_b.dimension == 3:
            dim_type = '4d_3d'
        else:
            messagebox.showerror("Ошибка",
                                 f"Неподдерживаемые размерности: A={self.tensor_a.dimension}D, B={self.tensor_b.dimension}D")
            return

        try:
            start_time = time.time()
            result_tensor = TensorOperations.multiply_tensors(
                self.tensor_a, self.tensor_b, method, dim_type)
            end_time = time.time()
            time_taken = end_time - start_time

            self.result_tensor = result_tensor
            result_shape = result_tensor.get_shape()

            # Обновляем информацию
            self.mult_info.config(text=f"Умножение выполнено за {time_taken:.6f} сек")

            # Выводим результаты
            self.show_results(method, time_taken, result_shape)

            self.log_info(f"Метод {method} выполнен за {time_taken:.6f} сек. Результат: {result_shape}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка умножения: {str(e)}")
            self.log_info(f"Ошибка в методе {method}: {str(e)}")

    def show_results(self, method, time_taken, result_shape):
        result_text = f"=== РЕЗУЛЬТАТЫ УМНОЖЕНИЯ ===\n\n"
        result_text += f"Метод: {method}\n"
        result_text += f"Время выполнения: {time_taken:.6f} сек\n"
        result_text += f"Форма результата: {result_shape}\n\n"

        # Показываем результат по методу Соколова
        result_text += "Результат умножения:\n"
        if self.result_tensor:
            result_text += self.matrix_to_string_sokolov(self.result_tensor.to_nested_list())

        self.results_text.delete('1.0', tk.END)
        self.results_text.insert('1.0', result_text)

    def log_info(self, message):
        self.info_text.insert(tk.END, f"{message}\n")
        self.info_text.see(tk.END)

    def clear_results(self):
        self.results_text.delete('1.0', tk.END)


class MatrixEditor(tk.Toplevel):
    def __init__(self, parent, matrix_type, app):
        super().__init__(parent)
        self.matrix_type = matrix_type
        self.app = app
        self.tensor = None

        self.title(f"Редактор матрицы {matrix_type}")
        self.geometry("600x400")

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        ttk.Label(main_frame, text=f"Введите матрицу {self.matrix_type}:").pack(anchor='w')

        # Текстовое поле для ввода
        self.text_area = scrolledtext.ScrolledText(main_frame, height=15, width=70)
        self.text_area.pack(fill='both', expand=True, pady=10)

        # Пример формата в стиле Соколова
        example_text = "# Пример формата для 3D матрицы:\n[[[1, 2]; [3, 4]], [[5, 6]; [7, 8]]]\n\n"
        example_text += "# Пример для 4D матрицы:\n[[[[1, 2]; [3, 4]], [[5, 6]; [7, 8]]], [[[9, 10]; [11, 12]], [[13, 14]; [15, 16]]]]"
        self.text_area.insert('1.0', example_text)

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="Сохранить",
                   command=self.save_matrix).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Отмена",
                   command=self.destroy).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Очистить",
                   command=self.clear_text).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Вставить матрицу",
                   command=self.paste_matrix).pack(side='left', padx=5)

    def save_matrix(self):
        try:
            text = self.text_area.get('1.0', tk.END).strip()

            # Удаляем комментарии
            lines = text.split('\n')
            clean_lines = []
            for line in lines:
                if '#' in line:
                    line = line.split('#')[0]
                clean_lines.append(line.strip())
            text = ' '.join(clean_lines)

            # Заменяем запятые в числах на точки (для корректного парсинга)
            text = re.sub(r'(\d),(\d)', r'\1.\2', text)

            # Преобразуем формат Соколова в стандартный Python формат
            text = self.convert_sokolov_to_python(text)

            # Парсим матрицу
            matrix = eval(text)

            # Проверяем, что это действительно список
            if not isinstance(matrix, list):
                raise ValueError("Введенные данные не являются матрицей")

            # Преобразуем в тензор
            tensor = Tensor.from_nested_list(matrix)

            self.tensor = tensor
            self.app.set_tensor_from_editor(self.matrix_type, tensor)
            self.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Неверный формат матрицы: {str(e)}")

    def paste_matrix(self):
        try:
            # Получаем текст из буфера обмена
            clipboard_text = self.app.root.clipboard_get()
            # Вставляем текст в текстовое поле
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert('1.0', clipboard_text)
        except Exception as e:
            pass

    def convert_sokolov_to_python(self, text):
        """Конвертирует формат Соколова в стандартный Python формат"""
        # Обрабатываем матрицы с квадратными скобками
        if text.startswith('[') and text.endswith(']'):
            # Заменяем точки с запятой на '], [' для разделения строк
            depth = 0
            result = []
            i = 0

            while i < len(text):
                char = text[i]

                if char == '[':
                    depth += 1
                    result.append(char)
                elif char == ']':
                    depth -= 1
                    result.append(char)
                elif char == ';' and depth == 1:
                    # Заменяем точку с запятой на '], ['
                    result.append('], [')
                elif char == ';' and depth > 1:
                    # Для вложенных уровней просто заменяем на запятую
                    result.append(',')
                else:
                    result.append(char)

                i += 1

            return ''.join(result)
        return text

    def clear_text(self):
        self.text_area.delete('1.0', tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = MatrixApp(root)
    root.mainloop()