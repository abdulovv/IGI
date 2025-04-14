#Lr3, Var1, Task5
#Abdulov Alexandr 353503
#Date: 07.04.25
#Description: This module processes a list of real numbers.

def negative_numbers_generator(numbers):
    for num in numbers:
        if num < 0:
            yield num

def process_list(numbers):
    sum_negatives = sum(negative_numbers_generator(numbers))
    numbers = list(numbers)

    # Ensure correct order
    min_val, max_val = min(numbers), max(numbers)
    min_index, max_index = numbers.index(min_val), numbers.index(max_val)
    start, end = sorted([min_index, max_index])

    multiplication = 1
    for num in numbers[start + 1 : end]:
        multiplication *= num

    return sum_negatives, multiplication


def main():

    while True:
        try:
            # Input list from the user
            user_input = input("Enter a list of real numbers separated by spaces: ")
            numbers = list(map(float, user_input.split()))

            # Process the list
            sum_negatives, multiplication = process_list(numbers)

            # Display results
            print("\nResults:")
            print(f"Sum of negative numbers: {sum_negatives}")
            print(f"Multiplication of elements between min and max: {multiplication}")

            # Ask if the user wants to repeat
            repeat = input("\nDo you want to process another list? (yes/no): ").strip().lower()
            if repeat != "yes":
                break

        except ValueError:
            print("Invalid input. Please enter real numbers separated by spaces.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
