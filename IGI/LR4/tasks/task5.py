from services.utils import MatrixAnalyzer
import numpy as np

def run():
    matrix = np.random.randint(1, 10, (5, 5))
    print("Матрица:")
    print(matrix)

    analyzer = MatrixAnalyzer(matrix)
    min_col = analyzer.column_with_min_sum()
    print(f"Столбец с минимальной суммой: {min_col}")

    median_np = analyzer.calculate_median(min_col)
    median_manual = analyzer.manual_median(min_col)

    print(f"Медиана (NumPy): {median_np}")
    print(f"Медиана (ручная): {median_manual}")