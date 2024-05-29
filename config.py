

MAX_USERS = 5
MAX_GPT_TOKENS = 1000
COUNT_LAST_MSG = 5

MAX_USER_STT_BLOCKS = 12   
MAX_USER_TTS_SYMBOLS = 1_000
MAX_USER_GPT_TOKENS = 5_000


SYSTEM_PROMPT = [{'role': 'system', 'text': 'Ты дружелюбный бот пощник, обращайся к пользователю на "ты" и поддерживай его.'
                                            'Поддерживай диалог. Не объясняй пользователю, что ты умеешь и можешь. '
                                            'Изображай лучшего друга'}]

IAM_TOKEN = ('t1.9euelZqNjJrKl4mJi56cjpWUypyLiu3rnpWax8uJlJ3MzJ6Szc-UxpCam4_l9PdjTG5N-e8FUWDb3fT3I3trTfnvBVFg283n9eue'
             'lZqKk8jOnJKTzo2ZnMiXlIyTkO_8xeuelZqKk8jOnJKTzo2ZnMiXlIyTkL3rnpWancmUyJKSjJWPkpGNxp3Licq13oac0ZyQko-Ki5r'
             'Ri5nSnJCSj4qLmtKSmouem56LntKMng.B6gREbTHCBBStCBp1mNy7GaEEMk8kh9ztybk5_2WiINv5KjSpBs-AS70OCH_SJQ0Eq0ClmR'
             'mRFxFPw9nwSMOBg')
FOLDER_ID = 'b1gi0q24so2nqvr1l202'

HOME_DIR = '/home/student/pythonProject31'  # путь к папке с проектом
LOGS = f'{HOME_DIR}/logs.txt'  # файл для логов
DB_FILE = f'{HOME_DIR}/messages.db'  # файл для базы данных

IAM_TOKEN_PATH = f'{HOME_DIR}/creds/iam_token.txt'  # файл для хранения iam_token
FOLDER_ID_PATH = f'{HOME_DIR}/creds/folder_id.txt'  # файл для хранения folder_id
BOT_TOKEN_PATH = f'{HOME_DIR}/creds/bot_token.txt'  # файл для хранения bot_token
