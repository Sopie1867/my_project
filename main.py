import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from database import create_database, add_message, select_n_last_messages
import logging
from validators import check_number_of_users, is_gpt_token_limit, is_tts_symbol_limit, is_stt_block_limit
from yandex_gpt import ask_gpt
from config import LOGS, COUNT_LAST_MSG
from speechkit import speech_to_text, text_to_speech
from creds import get_bot_token

bot = telebot.TeleBot(get_bot_token())


logging.basicConfig(filename=LOGS, level=logging.ERROR, format="%(asctime)s FILE: %(filename)s IN: %(funcName)s "
                                                               "MESSAGE: %(message)s", filemode="w")

markup = ReplyKeyboardMarkup(resize_keyboard=True)
markup.add(KeyboardButton('/help'))
markup.add(KeyboardButton('/start'))
create_database()


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, "Привет! Я твой бот-помощник в учебе. Отправь мне голосовое сообщение"
                                           " или текст, и я тебе отвечу!\n", reply_markup=markup)


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.from_user.id, "Чтобы приступить к общению, отправь мне голосовое сообщение или текст")


@bot.message_handler(commands=['debug'])
def debug(message):
    with open("logs.txt", "rb") as f:
        bot.send_document(message.chat.id, f)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        user_id = message.from_user.id
        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)
            return
        logging.info("Запись в БД.")
        full_user_message = [message.text, 'user', 0, 0, 0]
        add_message(user_id=user_id, full_message=full_user_message)
        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error_message:
            bot.send_message(user_id, error_message)
            return
        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        if not status_gpt:
            bot.send_message(user_id, answer_gpt)
            return
        total_gpt_tokens += tokens_in_answer
        full_gpt_message = [answer_gpt, 'assistant', total_gpt_tokens, 0, 0]
        add_message(user_id=user_id, full_message=full_gpt_message)
        bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)
    except Exception as e:
        logging.error(e)
        bot.send_message(message.from_user.id, "Не получилось ответить. Попробуй написать другое сообщение")

@bot.message_handler(content_types=['voice'])
def handle_voice(message: telebot.types.Message):

    user_id = message.from_user.id
    if not message.voice:
        return
    stt_blocks = is_stt_block_limit(user_id, message.voice.duration)
    if not stt_blocks:
        return
    file_id = message.voice.file_id
    file_info = bot.get_file(file_id)
    file = bot.download_file(file_info.file_path)
    status_stt, stt_text = speech_to_text(file)
    if not status_stt:
        bot.send_message(user_id, stt_text)
        return
    add_message(user_id=user_id, full_message=[stt_text, 'user', 0, 0, stt_blocks])
    last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
    total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
    if error_message:
        bot.send_message(user_id, error_message)
        return
    status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
    if not status_gpt:
        bot.send_message(user_id, answer_gpt)
        return
    total_gpt_tokens += tokens_in_answer
    tts_symbols = is_tts_symbol_limit(user_id, answer_gpt)
    add_message(user_id=user_id, full_message=[answer_gpt, 'assistant', total_gpt_tokens, tts_symbols, 0])
    if error_message:
        bot.send_message(user_id, error_message)
        return
    status_tts, voice_response = text_to_speech(answer_gpt)
    if status_tts:
        bot.send_voice(user_id, voice_response, reply_to_message_id=message.id)
    else:
        bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)

@bot.message_handler(commands=['tts'])
def text_speak(message):
    bot.send_message(message.chat.id, 'напиши текст и я его озвучу. Если голосовое сообщение не пришло превого раза, то отправь запрос ещё раз')
    bot.register_next_step_handler(message, text_to_speech_handler)


def text_to_speech_handler(message):
    text = message.text
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'введите текст')
        return
    text_symbol = is_tts_symbol_limit(message, text)
    if text_symbol is None:
        return
    status, content = text_to_speech(text)
    if status is True:
        bot.send_voice(message.chat.id, content)
    else:
        bot. send_message(message.chat.id, content)




@bot.message_handler (commands=['stt'])
def stt_handler(message):
    bot.send_message(message.chat.id, "Отправь голосовое сообщение, чтобы я его распознал!")
    bot.register_next_step_handler(message, stt)
def stt(message):
    user_id = message.from_user.id
    if not message.voice:
        return
    stt_blocks = is_stt_block_limit(message, message.voice.duration)
    if not stt_blocks:
        return
    file_id = message.voice.file_id
    file_info = bot.get_file(file_id)
    file = bot.download_file(file_info.file_path)
    status, text = speech_to_text(file)
    if status:
        length_text = len(text)
        add_message(user_id, text, length_text, stt_blocks)
        bot.send_message(user_id, text, reply_to_message_id=message.id)
    else:
        bot.send_message(user_id, text)




@bot.message_handler(func=lambda: True)
def handler(message):
    bot.send_message(message.from_user.id, "Отправь мне голосовое или текстовое сообщение, и я тебе отвечу")


bot.infinity_polling()
