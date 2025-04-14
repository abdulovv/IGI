#Lr3, Var1, Task2
#Abdulov Alexandr 353503
#Date: 07.04.25
#Description: This module calculates the sum of squares of integers entered by the user.
from itertools import repeat

def sum_of_squares():
    total = 0
    while True:
        try:
            num = int(input("Enter an integer (0 to stop): "))
            if num == 0:
                break
            total += num ** 2
        except ValueError:
            print("Invalid input. Please enter an integer.")
    return total


def main():

    while True:
        total = sum_of_squares()
        print(f"\nThe sum of squares is: {total}")

        # Ask if the user wants to repeat
        repeat = input("\nDo you want to perform another calculation? (yes/no): ").strip().lower()
        if repeat != "yes":
            break


if __name__ == "__main__":
    main()
