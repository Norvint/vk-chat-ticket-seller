import datetime
from collections import defaultdict
from pprint import pprint
from random import randint, choice, shuffle


class Dispatcher():

    def __init__(self):
        self.numbers_of_flight = ['ML-101', 'ML-202', 'ML-303', 'ML-404', 'ML-505', 'ML-606', 'ML-707', 'ML-808', 'ML-909',
                                  'MB-101', 'MB-202', 'MB-303', 'MB-404', 'MB-505', 'MB-606', 'MB-707', 'MB-808', 'MB-909',
                                  'MP-101', 'MP-202', 'MP-303', 'MP-404', 'MP-505', 'MP-606', 'MP-707', 'MP-808', 'MP-909',
                                  'MD-101', 'MD-202', 'MD-303', 'MD-404', 'MD-505', 'MD-606', 'MD-707', 'MD-808', 'MD-909',
                                  'MS-101', 'MS-202', 'MS-303', 'MS-404', 'MS-505', 'MS-606', 'MS-707', 'MS-808', 'MS-909',
                                  'LS-101', 'LS-202', 'LS-303', 'LS-404', 'LS-505', 'LS-606', 'LS-707', 'LS-808', 'LS-909',
                                  'LD-101', 'LD-202', 'LD-303', 'LD-404', 'LD-505', 'LD-606', 'LD-707', 'LD-808', 'LD-909',
                                  'LP-101', 'LP-202', 'LP-303', 'LP-404', 'LP-505', 'LP-606', 'LP-707', 'LP-808', 'LP-909',
                                  'LB-101', 'LB-202', 'LB-303', 'LB-404', 'LB-505', 'LB-606', 'LB-707', 'LB-808', 'LB-909',
                                  'BP-101', 'BP-202', 'BP-303', 'BP-404', 'BP-505', 'BP-606', 'BP-707', 'BP-808', 'BP-909',]
        self.cities = ['Белград', 'Лондон', 'Берлин', 'Париж', 'Дублин', 'Шанхай']
        self.flights = defaultdict(str)

    def generate_flights(self):
        for city in self.cities:
            self.flights[city] = ''
        for send_city in self.flights:
            dept = dict()
            for dest_city in self.cities[:4]:
                if dest_city != send_city:
                    dept[dest_city] = ''
            self.flights[send_city] = dept
            for dest_city in self.flights[send_city]:
                date = {}
                for i in range(20):
                    actual_date = datetime.datetime.now().date()
                    day = randint(1, 19)
                    month = randint(0, 2)
                    flight_date = actual_date + datetime.timedelta(day) + datetime.timedelta(month)
                    date_str = f'{flight_date.day}-{flight_date.month}-2020'
                    date_formatted = datetime.datetime.strptime(date_str, '%d-%m-%Y').date()
                    date[date_formatted] = ''
                    date_for_tests = datetime.date(year=2020, month=8, day=6)
                    date[date_for_tests] = ''
                self.flights[send_city][dest_city] = date
                for date in self.flights[send_city][dest_city]:
                    time = {}
                    for hour in range(9, 22, 3):
                        if hour == 9:
                            time_str = f'0{hour}:00'
                        else:
                            time_str = f'{hour}:00'
                        number_of_fl = choice(self.numbers_of_flight)
                        time[number_of_fl] = time_str
                    self.flights[send_city][dest_city][date] = time
                    self.flights[send_city][dest_city][date_for_tests] = {'BB-101': '09:00',
                                                                          'BB-202': '12:00',
                                                                          'BB-303': '15:00',
                                                                          'BB-404': '18:00',
                                                                          'BB-505': '21:00',
                                                                          }
            # del self.flights[choice(self.cities)]
        return self.flights

    def return_flights(self, dept, dest, date):
        date_get = date
        flights = ''
        date_formatted = datetime.datetime.strptime(date_get, '%d-%m-%Y').date()
        count = 0
        while flights == '':
            try:
                # print('-'*100)
                # print(dept, dest)
                # pprint(str(self.flights[dept]) + '\n' + '+' * 100)
                flights = self.flights[dept][dest][date_formatted]
            except Exception as exc:
                count += 1
                date_formatted += datetime.timedelta(days=1)
                # print(exc, type(exc))
                if count > 40:
                    flights = 'No flights'
        return flights, date_formatted

# dispatcher = Dispatcher()
# dispatcher.generate_flights()
# flight, date = dispatcher.return_flights('Лондон', 'Берлин', '6-8-2020')
# print(flight)
# print(date)