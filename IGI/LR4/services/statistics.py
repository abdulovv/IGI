import numpy as np

class SeriesCalculator:
    @staticmethod
    def calculate_with_eps(x, eps, max_iter=500):
        if x <= 1:
            raise ValueError("x должен быть больше 1")
        prev_sum = 0.0
        current_sum = 0.0
        n = 0
        while n < max_iter:
            term = 2.0 / ((2 * n + 1) * (x ** (2 * n + 1)))
            current_sum += term
            if abs(current_sum - prev_sum) < eps:
                break
            prev_sum = current_sum
            n += 1
        return current_sum, n + 1

class Statistics:
    def __init__(self, data):
        self.values = [item["F(x)"] for item in data]

    def mean(self):
        return np.mean(self.values)

    def median(self):
        return np.median(self.values)

    def mode(self):
        try:
            values_rounded = np.round(self.values, decimals=1)

            unique_values, counts = np.unique(values_rounded, return_counts=True)

            mode_value = unique_values[np.argmax(counts)]

            return float(mode_value)
        except Exception as e:
            raise ValueError(f"Мода не определена: {e}")

    def variance(self):
        return np.var(self.values)

    def std_deviation(self):
        return np.std(self.values)