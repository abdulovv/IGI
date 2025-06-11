import csv
import pickle


class ExportItems:
    def __init__(self, name, country, quantity):
        self.name = name
        self.country = country
        self.quantity = quantity


class Serializer:
    @staticmethod
    def save_to_csv(data, filename):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Name', 'Country', 'Quantity'])
                for item in data.values():
                    writer.writerow([item['name'], item['country'], item['quantity']])
        except IOError as e:
            print(f"Ошибка записи в CSV: {e}")

    @staticmethod
    def load_from_csv(filename):
        data = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(ExportItems(
                        row['Name'],
                        row['Country'],
                        int(row['Quantity'])
                    ))
        except (IOError, KeyError) as e:
            print(f"Ошибка чтения CSV: {e}")
        return data

    @staticmethod
    def save_to_pickle(data, filename):
        try:
            with open(filename, 'wb') as f:
                pickle.dump(list(data.values()), f)
        except pickle.PicklingError as e:
            print(f"Ошибка сериализации: {e}")

    @staticmethod
    def load_from_pickle(filename):
        try:
            with open(filename, 'rb') as f:
                return pickle.load(f)
        except (IOError, pickle.UnpicklingError) as e:
            print(f"Ошибка десериализации: {e}")
            return []