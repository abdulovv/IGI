def main():
    while True:
        choice = input("Выберите задание (1-5) или e для выхода:").strip().lower()

        if choice == 'e':
            break

        try:
            if choice == '1':
                from tasks.task1 import run
            elif choice == '2':
                from tasks.task2 import run
            elif choice == '3':
                from tasks.task3 import run
            elif choice == '4':
                from tasks.task4 import run
            elif choice == '5':
                from tasks.task5 import run
            else:
                print("Некорректный выбор")
                continue

            run()

        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()