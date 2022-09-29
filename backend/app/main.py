import re
import json
from fastapi import FastAPI, Response, status
from pydantic import BaseModel

regexp_pattern = "[а-яА-Яеё,. ]+"
json_path = '../data/example.json'

# Создаём свой тип данных, чтобы загружать в него данные из запроса
class Request(BaseModel):
    schema_id: int
    phrase: str

def figalize (word,substitutions_list):
    # Создаём пустые переменные
    all_keys = ''
    current_position = 0
    found_keys = 0
    # Проверяем, сколько слогов по ключевым гласным у нас в слове
    for sub in substitutions_list:
        all_keys += sub['keys']
    # Для слов, оканчивающихся на 'ая', всегда меняем только первый слог - эмпирически, так прикольнее
    if word[-2:] == 'ая' or word[-3:] == 'ая,' or word[-3:] == 'ая.':
        replacement_step = 1
    # Если слогов меньше 3, то будем заменять первый слог, иначе некрасиво
    elif len([i for i in list(word) if i in set(all_keys)]) <= 2:
        replacement_step = 1
    # Для длинных слов с количеством слогов от 3 - меняем первые два слога
    else:
        replacement_step = 2
    print (replacement_step)
    for letter in word:
        current_position += 1
        for substitution in substitutions_list:
            key_list = set(substitution['keys'])
            if letter in key_list:
                found_keys += 1
                if found_keys == replacement_step:
                    cropped_word = word[current_position:]
                    return (substitution['value'] + cropped_word)

# Проверка фразы на неверные символы
def verify_phrase (phrase):
    pattern = re.compile(regexp_pattern)
    match = pattern.fullmatch(phrase)
    return match

# Загрузка в память схемы из файла
def load_schemas (filepath):
    with open(filepath) as json_file:
        schema_list = json.load(json_file)
        return schema_list['schemas']

# Создаём API-интерфейс
app = FastAPI()
# Описываем обработку запроса к API фигализации
@app.post("/api/figalize/", status_code=200)
async def api_figalize_phrase(request: Request, response: Response):
    figalized_result = ''
    # Если фраза не содержит неверных символов, то разбиваем её по словам и процессим их по очереди
    if verify_phrase(request.phrase):
        for phrase_word in request.phrase.split(' '):
            figalized_result += (figalize (phrase_word,schemas[request.schema_id]['substitutions']) + ' ')
        else:
            return {'data': figalized_result}
    else:
        # Если фраза содержит неверные символы, возвращаем код 400 и сообщение об ошибке
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'data':'По-русски, пожалуйста, у нас тут культурное заведение'}

# Описываем обработку запроса списка схем
@app.get("/api/getschemas/", status_code=200)
async def api_getschemas():
    count = 0
    schema_list = {}
    for schema in schemas:
        schema_list[count]=schema['name']
        count += 1
    return schema_list

# Подгружаем схемы фигализации из файла
schemas = load_schemas(json_path)
