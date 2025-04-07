import os
from geometric_lib import circle, square

def main():

    r = float(os.getenv('CIRCLE_RADIUS'))
    a = float(os.getenv('SQUARE_SIDE'))

    print(f"Радиус круга: {r}")
    print(f"Сторона квадрата: {a} \n")

    print(f"Площадь круга: {circle.area(r)}")
    print(f"Площадь квадрата: {square.area(a)}")
    print(f"Периметр круга: {circle.perimeter(r)}")
    print(f"Периметр квадрата: {square.perimeter(a)}")

if __name__ == "__main__":
    main()