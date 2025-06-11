from services.serializer import Serializer, ExportItems

def run():
    data = {
        0: {'name': 'Phone', 'country': 'Germany', 'quantity': 1500},
        1: {'name': 'Phone', 'country': 'France', 'quantity': 800},
        2: {'name': 'Car', 'country': 'USA', 'quantity': 200},
        3: {'name': 'Car', 'country': 'Germany', 'quantity': 150}
    }

    Serializer.save_to_csv(data, "items.csv")
    Serializer.save_to_pickle(data, "items.pkl")

    loaded_csv = Serializer.load_from_csv("items.csv")
    loaded_pkl = Serializer.load_from_pickle("items.pkl")

    for item in loaded_pkl:
        print(f"Товар: {item['name']}, Страна: {item['country']}, Количество: {item['quantity']}")

    print('\n')

    while True:
        product = input("Введите название товара (или 'e' для выхода): ").strip()
        if product.lower() == 'e':
            break

        countries = []
        total = 0
        for item in loaded_csv:
            if item.name == product:
                countries.append(item.country)
                total += item.quantity

        if countries:
            print(f"Страны: {', '.join(countries)}")
            print(f"Общий объем: {total}")
        else:
            print("Товар не найден")