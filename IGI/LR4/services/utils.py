import numpy as np

class MatrixAnalyzer:
    def __init__(self, matrix):
        self.matrix = matrix

    def column_with_min_sum(self):
        col_sums = np.sum(self.matrix, axis=0)
        return np.argmin(col_sums)

    def calculate_median(self, column_index):
        column = self.matrix[:, column_index]
        return np.median(column)

    def manual_median(self, column_index):
        column = sorted(self.matrix[:, column_index].tolist())
        n = len(column)
        mid = n // 2
        if n % 2 == 0:
            return (column[mid - 1] + column[mid]) / 2
        else:
            return column[mid]