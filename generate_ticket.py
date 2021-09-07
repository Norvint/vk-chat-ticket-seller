from io import BytesIO
from random import randint

from PIL import ImageDraw, Image, ImageFont, ImageColor
from datetime import datetime, timedelta

class TicketGenerator:

    def __init__(self, name, departure, arrival, date, flight_time, sits):
        flight, time = flight_time.split(' - ')
        self.name = name.upper()
        self.departure = departure.upper()
        self.arrival = arrival.upper()
        self.date = str(date).upper()
        self.flight = flight.upper()
        self.time = time.upper()
        self.sits = int(sits)
        self.tickets = []

    def generate_tickets(self):
        landing_time = datetime.strptime(self.time, '%H:%M')
        departure_time_raw = landing_time + timedelta(minutes=30)
        departure_time = datetime.strftime(departure_time_raw, '%H:%M')
        sit_num = randint(1, 45)
        sits_letters = ['A', 'B', 'C', 'E', 'F']
        for ticket in range(self.sits):
            sit = '35' + sits_letters[ticket]
            self.generate_ticket(sit, '35', departure_time)
        return self.tickets

    def generate_ticket(self, sit, row, departure_time):
        image = Image.open('files/ticket_template.png').convert('RGBA')
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('files/Roboto-Black.ttf', 15)
        draw.line((40, 140, 250, 140), fill=ImageColor.colormap['white'], width=3)
        draw.text((44, 128), text=self.name, font=font, fill=ImageColor.colormap['black'])
        draw.line((40, 210, 250, 210), fill=ImageColor.colormap['white'], width=3)
        draw.text((44, 198), text=self.departure, font=font, fill=ImageColor.colormap['black'])
        draw.line((40, 277, 450, 277), fill=ImageColor.colormap['white'], width=24)
        draw.text((44, 265), text=self.arrival, font=font, fill=ImageColor.colormap['black'])
        draw.text((288, 265), text=self.date, font=font, fill=ImageColor.colormap['black'])
        draw.text((395, 265), text=departure_time, font=font, fill=ImageColor.colormap['black'])
        draw.line((40, 337, 450, 337), fill=ImageColor.colormap['white'], width=20)
        draw.text((44, 327), text=self.flight, font=font, fill=ImageColor.colormap['black'])
        draw.text((180, 327), text=sit, font=font, fill=ImageColor.colormap['black'])
        draw.text((290, 327), text=row, font=font, fill=ImageColor.colormap['black'])
        draw.text((395, 327), text=self.time, font=font, fill=ImageColor.colormap['black'])

        # image.save('files/ticket_example.png')
        temp_file = BytesIO()
        image.save(temp_file, 'png')
        temp_file.seek(0)

        self.tickets.append(temp_file)

