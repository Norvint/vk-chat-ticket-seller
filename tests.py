from copy import deepcopy
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, Mock
from pony.orm import db_session, rollback
from vk_api.bot_longpoll import VkBotEvent
from chatbot import ChatBot
from generate_ticket import TicketGenerator

try:
    import settings
except ImportError:
    exit('Do cp settings.py.default settings.py and set token')


def isolate_db(test_func):
    def wrapper(*args, **kwargs):
        with db_session:
            test_func(*args, **kwargs)
            rollback()
    return wrapper


class TestOne(TestCase):
    RAW_EVENT = {'type': 'message_new',
                 'object': {'message': {'date': 1588319466, 'from_id': 1, 'id': 128,
                                        'out': 0, 'peer_id': 1, 'text': 'Дай мне ивент',
                                        'conversation_message_id': 125, 'fwd_messages': [],
                                        'important': False, 'random_id': 0, 'attachments': [],
                                        'is_hidden': False},
                            'client_info': {'button_actions': ['text', 'vkpay', 'open_app', 'location',
                                                               'open_link', 'open_photo'],
                                            'keyboard': True, 'inline_keyboard': True, 'carousel': True,
                                            'lang_id': 0}},
                 'group_id': 192607335, 'event_id': '07135ab43e89ded7ddd318daedf058b290fd3473'}

    def test_run(self):
        count = 5
        obj = {'a': 1}
        events = [obj] * count
        long_poll_mock = Mock(return_value=events)
        long_poll_listen_mock = Mock()
        long_poll_listen_mock.listen = long_poll_mock

        with patch('chatbot.VkApi'):
            with patch('chatbot.VkBotLongPoll', return_value=long_poll_listen_mock):
                chatbot = ChatBot('', '')
                chatbot._on_event = Mock()
                chatbot.run()

                chatbot._on_event.assert_called()
                chatbot._on_event.assert_any_call(obj)
                assert chatbot._on_event.call_count == 5

    INPUTS = [
        'Лямбда',
        'Откуда',
        'Прибываем',
        'Привет',
        'Хватит',
        'Заказать',
        'Бангладеш',
        'Лондон',
        'Берлин',
        '23:10:2020',
        '06-08-2020',
        'BB-102',
        'BB-101',
        '7',
        '4',
        'some comment',
        'не понял',
        'да',
        '8-сто-333-45-43',
        '89888980008'
    ]

    EXPECTED_OUTPUTS = [
        settings.DEFAULT_ANSWER,
        settings.INTENTS[0]['answer'],
        settings.INTENTS[1]['answer'],
        settings.INTENTS[2]['answer'],
        settings.INTENTS[3]['answer'],
        settings.SCENARIOS['registration']['steps']['step1']['text'],
        settings.SCENARIOS['registration']['steps']['step1']['failure_text'],
        settings.SCENARIOS['registration']['steps']['step2']['text'],
        settings.SCENARIOS['registration']['steps']['step3']['text'],
        settings.SCENARIOS['registration']['steps']['step3']['failure_text'],
        settings.SCENARIOS['registration']['steps']['step4']['text'].format(actual_date='6-8-2020',
                                                                            flights_for_user='BB-101 - 09:00 \n'
                                                                                             'BB-202 - 12:00 \n'
                                                                                             'BB-303 - 15:00 \n'
                                                                                             'BB-404 - 18:00 \n'
                                                                                             'BB-505 - 21:00 \n'),

        settings.SCENARIOS['registration']['steps']['step4']['failure_text'],
        settings.SCENARIOS['registration']['steps']['step5']['text'],
        settings.SCENARIOS['registration']['steps']['step5']['failure_text'],
        settings.SCENARIOS['registration']['steps']['step6']['text'],
        settings.SCENARIOS['registration']['steps']['step7']['text'].format(departure_city='Лондон',
                                                                            arrival_city='Берлин',
                                                                            flight='BB-101 - 09:00',
                                                                            actual_date='6-8-2020',
                                                                            sits='4'),
        settings.SCENARIOS['registration']['steps']['step7']['failure_text'],
        settings.SCENARIOS['registration']['steps']['step8']['text'],
        settings.SCENARIOS['registration']['steps']['step8']['failure_text'],
        settings.SCENARIOS['registration']['steps']['step9']['text'],
    ]

    @isolate_db
    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock
        events = []
        real_outputs = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT)
            event['object']['message']['text'] = input_text
            events.append(VkBotEvent(event))
        long_poll_mock = Mock()
        long_poll_mock.listen = Mock(return_value=events)
        with patch('chatbot.VkBotLongPoll', return_value=long_poll_mock):
            bot = ChatBot('', '')
            bot.api = api_mock
            bot.run()
        assert send_mock.call_count == len(self.INPUTS)
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])
        assert real_outputs == self.EXPECTED_OUTPUTS

    def test_image_generation(self):
        generetic = TicketGenerator('Антон', 'Лондон', 'Берлин', datetime(year=2020, month=8, day=6).date(),
                                    'BB-102 - 9:00', 1)
        ticket_file = generetic.generate_tickets()[0]
        with open('files/ticket_example.png', 'rb') as expected_file:
            expected_bytes = expected_file.read()
            assert ticket_file.read() == expected_bytes