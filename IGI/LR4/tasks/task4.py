from services.geometry import Triangle
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def run():
    try:
        base = float(input("Введите основание: "))
        height = float(input("Введите высоту: "))
        color = input("Введите цвет: ").strip()

        triangle = Triangle(base, height, color)
        print(triangle)

        fig, ax = plt.subplots()
        ax.set_aspect('equal')
        ax.add_patch(patches.Polygon(
            [[0, 0], [base, 0], [base/2, height]],
            closed=True,
            facecolor=color
        ))
        ax.set_xlim(-1, base + 1)
        ax.set_ylim(-1, height + 1)
        ax.set_title("Равнобедренный треугольник")
        plt.savefig("triangle.png")

    except ValueError as e:
        print(f"Некорректный ввод: {e}")