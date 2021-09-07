"""
Handler - это функция, которая принимает на вход text (текст входящего сообщения) и context(dict), а возвращает bool:
True если шаг пройден, False если данные переданы неправильно
"""
import datetime
import re
from pprint import pprint

import flights_dispatcher
from generate_ticket import TicketGenerator

re_name = re.compile(r'^[\w\-\s]{3,40}$')
re_email = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
re_city = re.compile('Белград|Шанхай|Париж|Дублин|Берлин|Лондон')
re_phone = re.compile(r'(\d{3})\D*(\d{3})\D*(\d{4})\D*(\d*)$')
dispatcher = flights_dispatcher.Dispatcher()
all_flights = dispatcher.generate_flights()


def handle_departure_city(text, context):
    matches = re.findall(re_city, text.title())
    if len(matches) > 0:
        context['departure_city'] = matches[0]
        return True
    else:
        return False


def handle_arrival_city(text, context):
    matches = re.findall(re_city, text.title())
    if len(matches) > 0:
        context['arrival_city'] = matches[0]
        if context['arrival_city'] == context['departure_city']:
            return False
        else:
            return True
    else:
        return False


def handle_date(text, context):
    try:
        context['date'] = text
        flights, flights_date = dispatcher.return_flights(context['departure_city'],
                                                          context['arrival_city'],
                                                          context['date'])
        if flights != 'No flights':
            context['flights'] = flights
            context['flights_for_user'] = ''
            k = 1
            context['actual_date'] = f'{flights_date.day}-{flights_date.month}-{flights_date.year}'
            for number, time in flights.items():
                context['flights_for_user'] += f'{number} - {time} \n'
                k += 1
                if k > 5:
                    return True
        else:
            return False
    except ValueError:
        return False


def handle_flights(text, context):
    if text in context['flights']:
        time = context['flights'][text]
        context['flight'] = f'{text} - {time}'
        return True
    else:
        return False


def handle_sits(text, context):
    if int(text) in range(1, 6):
        context['sits'] = int(text)
        return True
    else:
        return False


def handle_comments(text, context):
    context['comment'] = text
    return True


def handle_answer(text, context):
    if 'нет' in text.lower():
        stop = '/stop'
        return stop
    elif 'да' in text.lower():
        return True


def handle_phone(text, context):
    matches = re.findall(re_phone, text)
    if len(matches) > 0:
        context['phone_number'] = matches[0]
        return True
    else:
        return False


def generate_tickets_handler(text, context):
    generetic = TicketGenerator(name='Иван Андреев',
                                departure=context['departure_city'],
                                arrival=context['arrival_city'],
                                date=context['date'],
                                flight_time=context['flight'],
                                sits=context['sits'])
    return generetic.generate_tickets()
