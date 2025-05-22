from abc import ABC, abstractmethod

class AreaMixin(ABC):
    @abstractmethod
    def area(self):
        pass

class Color:
    def __init__(self, color):
        self._color = color

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if not isinstance(value, str):
            raise ValueError("Цвет должен быть строкой")
        self._color = value


class GeometricFigure(AreaMixin, ABC):
    figure_count = 0

    def __init__(self, color):
        self.color = Color(color)
        GeometricFigure.figure_count += 1

    @property
    @abstractmethod
    def name(self):
        pass

    def __str__(self):
        return f"{self.name} (color={self.color.color}, area={self.area()})"


class Triangle(GeometricFigure):
    def __init__(self, base, height, color):
        super().__init__(color)
        self._base = base
        self._height = height

    @property
    def base(self):
        return self._base

    @base.setter
    def base(self, value):
        if value <= 0:
            raise ValueError("Основание должно быть положительным числом")
        self._base = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if value <= 0:
            raise ValueError("Высота должна быть положительным числом")
        self._height = value

    @property
    def name(self):
        return "Isosceles Triangle"

    def area(self):
        return 0.5 * self.base * self.height

    def __str__(self):
        return f"{self.name} (color={self.color.color}, base={self.base}, height={self.height}, area={self.area()})"