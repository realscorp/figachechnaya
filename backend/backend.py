import re
import json
import fastapi

current_schema = 0

def figalize (word,substitutions_list):
    all_keys = ''
    current_position = 0
    found_keys = 0

    # Проверяем, сколько слогов по ключевым гласным у нас в слове
    for sub in substitutions_list:
        all_keys += sub['keys']
    # Для слов, оканчивающихся на 'ая', всегда меняем только первый слог - эмпирически, так прикольнее
    if word[-2:] == 'ая' or word[-2:] == 'я,' or word[-2:] == 'я.':
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


def load_schemas (filepath):
    with open(filepath) as json_file:
        schema_list = json.load(json_file)
        return schema_list['schemas']

schemas = load_schemas('example.json')

while True:
    figalized_result = ''
    phrase = str(input('Слово или фраза: '))
    pattern = re.compile("[а-яА-Яеё,. ]+")
    match = pattern.fullmatch(phrase)
    if match:
        for phrase_word in phrase.split(' '):
            figalized_result += (figalize (phrase_word,schemas[current_schema]['substitutions']) + ' ')
        print (figalized_result)
    else:
        print ('По-русски, пожалуйста, у нас тут культурное заведение')