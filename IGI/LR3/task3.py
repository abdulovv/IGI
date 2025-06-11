#Lr3, Var1, Task3
#Abdulov Alexandr 353503
#Date: 07.04.25
#Description: This module counts uppercase English letters in a string.

def count_uppercase_letters(text):
    count = 0

    for char in text:
        if char.isupper() and char.isalpha():
            count += 1

    return count


def main():

    while True:
        text = input("Enter a string: ")
        count = count_uppercase_letters(text)
        print(f"\nThe number of uppercase English letters is: {count}")

        # Ask if the user wants to repeat
        repeat = input("\nDo you want to perform another calculation? (yes/no): ").strip().lower()
        if repeat != "yes":
            break


if __name__ == "__main__":
    main()
