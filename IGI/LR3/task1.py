#Lr3, Var1, Task1
#Abdulov Alexandr 353503
#Date: 07.04.25
#This module calculates the value of ln((x+1)/(x-1))

import math

def repeat(n_times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(n_times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(n_times = 3)
def hello():
    print('hello')

def calculate_ln_expression(x, eps):
    hello()

    try:
        # Validate input
        if abs(x) <= 1:
            raise ValueError("The argument x must satisfy |x| > 1.")

        # Initialize variables
        term = 1 / x
        F_x = term
        n = 1

        # Iterate until the desired accuracy is achieved or max iterations reached
        while abs(term) > eps and n < 500:
            term = 1 / ((2 * n + 1) * x ** (2 * n + 1))  # Next term of the series
            F_x += term
            n += 1

        # Multiply by 2 as per the formula
        F_x *= 2

        # Calculate the value using the math module
        math_F_x = math.log((x + 1) / (x - 1))

        return F_x, n, math_F_x

    except Exception as e:
        print(f"Error in calculate_ln_expression: {e}")
        return None, None, None


def main():
    while True:
        try:
            # Input from the user
            x = float(input("Enter the value of x (|x| > 1): "))
            eps = float(input("Enter the desired accuracy (eps): "))

            # Validate input
            if eps <= 0:
                raise ValueError("Accuracy (eps) must be positive.")

            # Calculate the result
            F_x, n, math_F_x = calculate_ln_expression(x, eps)

            # Display the result
            if F_x is not None:
                print("\nResults:")
                print(f"x = {x}")
                print(f"F(x) (calculated) = {F_x}")
                print(f"Number of terms (n) = {n}")
                print(f"F(x) (math module) = {math_F_x}")
                print(f"Epsilon = {eps}\n")

            # Ask if the user wants to repeat
            repeat = input("\nDo you want to perform another calculation? (yes/no): ").strip().lower()
            if repeat != "yes":
                break

        except ValueError as ve:
            print(f"Invalid input: {ve}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
