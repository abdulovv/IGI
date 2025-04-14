import math
from task1 import calculate_ln_expression
from task2 import sum_of_squares
from task3 import count_uppercase_letters
from task4 import analyze_text
from task5 import process_list


def do_task1():
    try:
        x = float(input("Enter x: "))
        eps = float(input("Enter epsilon: "))

        Fx, n, math_Fx = calculate_ln_expression(x, eps)

        print("\nResults:")
        print(f"x = {x}")
        print(f"F(x) (calculated) = {Fx}")
        print(f"Number of terms (n) = {n}")
        print(f"F(x) (math module) = {math_Fx}")
        print(f"Epsilon = {eps}\n")
    except:
        print("Please enter a numeric value")


def do_task2():
    result = sum_of_squares()
    print(f"Sum of squares: {result}\n")


def do_task3():
    text = input("Enter a string: ")
    result = count_uppercase_letters(text)
    print(f"Number of uppercase letters: {result}\n")


def do_task4():
    text = ("So she was considering in her own mind, as well as she could, "
            "for the hot day made her feel very sleepy and stupid, whether the pleasure "
            "of making a daisy-chain would be worth the trouble of getting up and picking "
            "the daisies, when suddenly a White Rabbit with pink eyes ran close by her.")
    result = analyze_text(text)
    print(f"Analysis results: {result}\n")


def do_task5():

    numbers = list(map(float, input("Enter a list of numbers separated by spaces: ").split()))
    result = process_list(numbers)
    print(f"Processing results: {result}\n")


def main():
    while True:
        print("Choose a task to test:")
        print("1. Calculate ln expression")
        print("2. Sum of squares")
        print("3. Count uppercase letters")
        print("4. Text analysis")
        print("5. List processing")
        print("0. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            do_task1()
        elif choice == "2":
            do_task2()
        elif choice == "3":
            do_task3()
        elif choice == "4":
            do_task4()
        elif choice == "5":
            do_task5()
        elif choice == "0":
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.\n")


if __name__ == "__main__":
    main()
