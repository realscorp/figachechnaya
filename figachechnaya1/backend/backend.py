import re


while True:
    inp = str(input('Ну-с, что там у вас: '))
    pattern = re.compile("[а-яА-Я]+")
    match = pattern.fullmatch(inp)
    if match:
        print ('Годится')
    else:
        print ('По-русски, пожалуйста, у нас тут культурное заведение')