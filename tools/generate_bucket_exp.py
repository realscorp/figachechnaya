# Для удобной генерации значений для бакетов гистограмм метрик latency, потому что стандартный бакет даёт не такие информативные графики
import math

while True:
    lambda_const = float(input('Введите коэффициент лямбда (по-умолчанию: 0.095): ') or 0.095)
    decrement = float(input('Введите декремент для выравнивания значений (по-умолчанию: 0.004): ') or 0.004)
    bucket_size = int(input('Введите размер бакета (по-умолчанию: 40): ') or 40)
    bucket_numbers = range(1,bucket_size,1)
    result = []
    for n in bucket_numbers:
        result.append(round ((lambda_const*math.exp(lambda_const*n)-lambda_const-decrement), 3))
    # result.append('+inf')
    print ('\n', result, '\n')