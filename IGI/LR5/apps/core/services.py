import requests
from django.conf import settings
from django.core.cache import cache
from decimal import Decimal

FRANKFURTER_API_URL = "https://api.frankfurter.app"
CURRENCY_CACHE_KEY = "exchange_rates_{base}_{targets_str}"
CACHE_TIMEOUT = 3600  # 1 час

def get_exchange_rates(base_currency='BYN', target_currencies=None):
    if target_currencies is None:
        target_currencies = ['USD', 'EUR', 'RUB']
    
    targets_str = ",".join(sorted(target_currencies))
    cache_key = CURRENCY_CACHE_KEY.format(base=base_currency, targets_str=targets_str)
    
    cached_rates = cache.get(cache_key)
    if cached_rates:
        return cached_rates

    try:
        params = {
            'from': base_currency,
            'to': targets_str
        }
        response = requests.get(f"{FRANKFURTER_API_URL}/latest", params=params, timeout=5)
        response.raise_for_status() # Вызовет исключение для HTTP-ошибок (4xx или 5xx)
        data = response.json()
        
        rates = data.get('rates', {})
        # Убедимся, что все целевые валюты присутствуют и являются Decimal
        processed_rates = {}
        for curr in target_currencies:
            if curr in rates and rates[curr] is not None:
                try:
                    processed_rates[curr] = Decimal(str(rates[curr]))
                except (TypeError, ValueError):
                    processed_rates[curr] = None # Или обработать ошибку иначе
            else:
                processed_rates[curr] = None

        if any(r is not None for r in processed_rates.values()): # Кэшируем, если хоть один курс получен
            cache.set(cache_key, processed_rates, CACHE_TIMEOUT)
        return processed_rates

    except requests.exceptions.RequestException as e:
        # Здесь можно добавить логирование ошибки
        # print(f"Error fetching exchange rates: {e}")
        return {curr: None for curr in target_currencies} # Возвращаем None для всех валют в случае ошибки
    except (ValueError, TypeError) as e:
        # Ошибка парсинга JSON или данных
        # print(f"Error processing exchange rate data: {e}")
        return {curr: None for curr in target_currencies} 