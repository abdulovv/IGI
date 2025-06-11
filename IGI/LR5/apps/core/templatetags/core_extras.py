from django import template
from django.utils import timezone
import datetime

register = template.Library()

@register.filter(name='to_timezone')
def to_timezone(value, tz_name):
    if not timezone.is_aware(value):
        # Если время не aware, делаем его aware по UTC (или другой дефолтной ТЗ, если нужно)
        # Это важно, если в БД хранятся naive datetime
        value = timezone.make_aware(value, datetime.timezone.utc)
    
    try:
        target_tz = timezone.pytz.timezone(tz_name)
        return value.astimezone(target_tz)
    except Exception:
        return value # В случае ошибки возвращаем как есть

@register.filter(name='format_datetime_local')
def format_datetime_local(value, user_timezone_str):
    if not value: return ""
    
    # Сначала убедимся, что значение aware (предполагаем UTC из БД)
    if timezone.is_naive(value):
        value = timezone.make_aware(value, datetime.timezone.utc)
    else:
        value = value.astimezone(datetime.timezone.utc) # Приводим к UTC для единообразия

    local_dt = value # Уже в UTC
    if user_timezone_str:
        try:
            target_tz = timezone.pytz.timezone(user_timezone_str)
            local_dt = value.astimezone(target_tz)
        except Exception:
            pass # останется UTC
    
    return local_dt.strftime("%d/%m/%Y %H:%M:%S")

@register.filter(name='format_datetime_utc')
def format_datetime_utc(value):
    if not value: return ""
    if timezone.is_naive(value):
        value = timezone.make_aware(value, datetime.timezone.utc)
    else:
        value = value.astimezone(datetime.timezone.utc)
    return value.strftime("%d/%m/%Y %H:%M:%S")

@register.filter(name='format_phone_number')
def format_phone_number(phone_number_str):
    if not phone_number_str: 
        return ""
    
    # Удаляем все нецифровые символы, кроме начального плюса, если он есть
    cleaned_number = ''
    if phone_number_str.startswith('+'):
        cleaned_number = '+' + ''.join(filter(str.isdigit, phone_number_str[1:]))
    else:
        cleaned_number = ''.join(filter(str.isdigit, phone_number_str))

    # Проверяем на стандартные белорусские номера
    # Пример: +375291234567 (13 символов) или 375291234567 (12 символов)
    # Или 80291234567 (11 символов с ведущей 8)
    
    if cleaned_number.startswith('+375') and len(cleaned_number) == 13:
        # +375 XX XXX XX XX
        return f"{cleaned_number[:4]} ({cleaned_number[4:6]}) {cleaned_number[6:9]}-{cleaned_number[9:11]}-{cleaned_number[11:13]}"
    elif cleaned_number.startswith('375') and len(cleaned_number) == 12:
        # 375 XX XXX XX XX -> +375 XX XXX XX XX
        return f"+375 ({cleaned_number[3:5]}) {cleaned_number[5:8]}-{cleaned_number[8:10]}-{cleaned_number[10:12]}"
    elif cleaned_number.startswith('80') and len(cleaned_number) == 11:
        # 80 XX XXX XX XX -> +375 XX XXX XX XX (заменяем 80 на +375)
        operator_code = cleaned_number[2:4]
        rest_of_number = cleaned_number[4:]
        return f"+375 ({operator_code}) {rest_of_number[:3]}-{rest_of_number[3:5]}-{rest_of_number[5:7]}"
    
    # Если не подошло под белорусские форматы, просто возвращаем очищенный номер или исходный
    return phone_number_str # Или можно вернуть cleaned_number, если нужно всегда удалять форматирование 