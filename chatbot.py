# -*- coding: utf-8 -*-
import requests
from pony.orm import db_session
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
import logging
import handlers
from models import UserState, Ticket

try:
    import settings
except ImportError:
    exit('Do cp settings.py.default settings.py and set token')

log = logging.getLogger("chat-bot")
log.setLevel(logging.DEBUG)


def configure_logging():

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_formatter = logging.Formatter('%(levelname)s - %(message)s')
    stream_handler.setFormatter(stream_formatter)
    log.addHandler(stream_handler)

    file_handler = logging.FileHandler('chats.log', 'a')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m-%Y %H:%M')
    file_handler.setFormatter(file_formatter)
    log.addHandler(file_handler)


class ChatBot:
    """
    Chatbot for vk.com.

    Use Python 3.7
    """
    def __init__(self, group_id, token):
        """
        :param group_id: group id - id of vk.com group
        :param token: secret token
        """
        self.group_id = group_id
        self.token = token
        self.vk = VkApi(token=token)
        self.api = self.vk.get_api()
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.scenario_is_going = None

    def run(self):
        """
        run the bot
        :return: None
        """
        for event in self.long_poller.listen():
            try:
                self._on_event(event)
            except Exception as exc:
                log.exception(exc)

    @db_session
    def _on_event(self, event):
        """
        send answer back to user
        :param event: VkBotMessageEvent object
        :return: None
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.debug('Мы пока не умеем обрабатывать сообщения такого типа', event.type)
            return
        user_id = event.message.peer_id
        text = event.message.text
        state = UserState.get(user_id=str(user_id))
        if state is not None and '/' not in text:
            self.continue_scenario(text, state, user_id)
        elif state is not None and '/' in text:
            state.delete()
            for intent in settings.INTENTS:
                if any(token in text for token in intent['tokens']):
                    if intent['answer']:
                        self.send_text(intent['answer'], user_id)
                    break
        else:
            for intent in settings.INTENTS:
                if any(token in text for token in intent['tokens']):
                    if intent['answer']:
                        self.send_text(intent['answer'], user_id)
                    else:
                        self.start_scenario(str(user_id), intent['scenario'], text)
                    break
            else:
                self.send_text(settings.DEFAULT_ANSWER, user_id)
        log.info(str(event.message.from_id) + ' - ' + str(event.message.text))

    def send_step(self, step, user_id, text, context):
        if 'text' in step:
            self.send_text(step['text'].format(**context), user_id)
        if 'image' in step:
            handler = getattr(handlers, step['image'])
            images = handler(text, context)
            print(images)
            for image in images:
                self.send_image(image, user_id)

    def send_image(self, image, user_id):
        upload_url = self.api.photos.getMessagesUploadServer(peer_id=user_id)['upload_url']
        upload_data = requests.post(url=upload_url, files={'photo': ('image.png', image, 'image/png')}).json()
        print(upload_data)
        image_data = self.api.photos.saveMessagesPhoto(**upload_data)

        owner_id = image_data[0]['owner_id']
        media_id = image_data[0]['id']
        attachment = f'photo{owner_id}_{media_id}'

        self.api.messages.send(
            attachment=attachment,
            random_id=random.randint(1, 2 ** 24),
            user_id=user_id,
        )

    def send_text(self, text_to_send, user_id):
        self.api.messages.send(
            message=text_to_send,
            random_id=random.randint(1, 2 ** 24),
            user_id=user_id,
        )

    def start_scenario(self, user_id, scenario_name, text):
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        self.send_step(step, user_id, text, context={})
        UserState(scenario_name=scenario_name, step_name=first_step, user_id=user_id, context={})

    def continue_scenario(self, text, state, user_id):
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]
        handler = getattr(handlers, step['handler'])
        if handler(text=text, context=state.context) and handler(text=text, context=state.context) != '/stop':
            next_step = steps[step['next_step']]
            self.send_step(next_step, user_id, text, state.context)
            if next_step['next_step']:
                state.step_name = step['next_step']
            else:
                Ticket(departure_city=state.context['departure_city'],
                       arrival_city=state.context['arrival_city'],
                       date=state.context['actual_date'],
                       flight=state.context['flight'],
                       sits=state.context['sits'],
                       phone_number=state.context['phone_number'])
                text_to_send = next_step['text']
                state.delete()
                log.info(state.context)
        elif handler(text=text, context=state.context) == '/stop':
            text_to_send = 'Сценарий был остановлен, если захотите попробовать еще раз, просто попросите.'
            self.send_text(text_to_send, user_id)
            state.delete()
        else:
            text_to_send = step['failure_text'].format(**state.context)
            self.send_text(text_to_send, user_id)
        log.info(state.context)


if __name__ == "__main__":
    configure_logging()
    bot = ChatBot(settings.GROUP_ID, settings.TOKEN)
    bot.run()
