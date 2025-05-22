from services.statistics import SeriesCalculator, Statistics
from math import log
import matplotlib.pyplot as plt

def run():
    while True:
        try:
            x = float(input("Введите x (x > 1): "))
            if x <= 1:
                print("x должен быть больше 1")
                continue
            eps = float(input("Введите точность eps: "))
            if eps <= 0:
                print("eps должен быть положительным")
                continue
            break
        except ValueError:
            print("Некорректный ввод")

    calculator = SeriesCalculator()
    series_val, n_iterations = calculator.calculate_with_eps(x, eps)
    math_val = log((x + 1) / (x - 1))

    print(f"\nРезультаты для x = {x}:")
    print(f"F(x) (ряд): {series_val:.6f}")
    print(f"Math F(x): {math_val:.6f}")
    print(f"Количество итераций (n): {n_iterations}")

    x_values = [i for i in range(2, 11)]
    data = []
    for x_val in x_values:
        val, _ = calculator.calculate_with_eps(x_val, eps)
        data.append({"F(x)": val})

    stats = Statistics(data)
    print("\nСтатистика по значениям ряда:")
    print(f"Среднее значение: {stats.mean():.6f}")
    print(f"Медиана: {stats.median():.6f}")
    try:
        print(f"Мода: {stats.mode():.6f}")
    except Exception as e:
        print(f"Мода: Не определена ({e})")
    print(f"Дисперсия: {stats.variance():.6f}")
    print(f"Стандартное отклонение: {stats.std_deviation():.6f}")

    plt.figure(figsize=(10, 6))
    plt.plot(
        x_values,
        [item["F(x)"] for item in data],
        "r-",
        label="Ряд Тейлора"
    )
    plt.plot(
        x_values,
        [log((x_val + 1) / (x_val - 1)) for x_val in x_values],
        "b--",
        label="Math.log"
    )
    plt.title("Сравнение ряда и Math.log")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()
    plt.grid(True)
    plt.savefig("graph.png")