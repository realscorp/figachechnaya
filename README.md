# Фигачечная
https://figachechnaya.ru  

<details>
  <summary>Так выглядит сайт, когда облачный сервис оплачен</summary>
  ![скриншот](https://i.ibb.co/7NdXM2Y/front.gif)
</details>

https://grafana.figachechnaya.ru - метрики и логи *(user:o66Vsxt7PZbpQC_PYvWL59rNBkRcWMPA)*

<details>
  <summary>Мониторинг под нагрузочным тестированием через Jmeter</summary>
  ![скриншот](https://i.ibb.co/nkzGPrS/grafana2.png)
  ![скриншот](https://i.ibb.co/5j2pfqg/grafana3.png)
</details>

<details>
  <summary>Структура репозитория</summary>

    .
    ├── README.md
    ├── ci-cd/ - пайплайны для Gitlab-CI
    ├── docker-compose/ - всё, что нужно, чтобы поднять сервис локально, для удобства разработки
    ├── frontend/
    │   ├── Dockerfile
    │   ├── front.conf - настройка nginx
    │   └── site/ - HTML+CSS+Javascript фронтенд
    ├── kubernetes/
    │   └── manifests/ - манифесты с объектами K8s для деплоя сервиса
    │       ├── figalize/
    │       ├── frontend/
    │       ├── history/
    │       ├── imagizer/
    │       └── ingress/
    ├── microservices/
    │   ├── figalize/
    │   │   ├── Dockerfile - докерфайл для сборки образа
    │   │   ├── app/ - Python-код
    │   │   ├── data/ - схема преобразований
    │   │   └── requirements.txt - список Python-модулей для сборки
    │   ├── history/
    │   │   ├── Dockerfile
    │   │   ├── app/
    │   │   └── requirements.txt
    │   └── imagizer/
    │       ├── Dockerfile
    │       ├── app/
    │       └── requirements.txt
    ├── terraform
    │   ├── helm/ - yml-файлы с параметрами helm-чартов (почти не используется)
    │   ├── templates/ - шаблоны для кода
    │   └── *.tf - собственно Terraform-код для настройки сети, DBaaS, кластера k8s и деплоя
    └── tools - вспомогательные скрипты

</details>

Репозиторий автоматически зеркалируется https://gitlab.com/realscorp/figachechnaya -> https://github.com/realscorp/figachechnaya  
  
Автоматизация построена через Gitlab CI
## Что это и зачем
**Фигачечная** - относительно сложно устроенный, но простой функционально сервис по офигачиванию слов (*Велосипед -> Фигасипед*).  
Для меня это тренировка, чтобы обновить, закрепить и показать навыки:
- Python (REST API, Metrics, Logging)
- Docker, Docker compose
- Kubernetes
- Gitlab CI
- Kafka
- S3 API
- Observability (Prometheus/Grafana)  

А ещё это способ показать понимание принципов построения микросервисного приложения и просто повод немного повеселиться :)
# Техническое задание
Компания-стартап "Фигант Кузбасса" уверена в том, что новый сервис "Фигачечная" выстрелит на рынке и готова сразу строить приложение по микросервисной архитектуре, чтобы упростить его дальнейшее развитие и масштабирование.
### Product owner хочет следующую функциональность
- Сайт позволяет пользователю ввести слово или фразу на русском языке и, нажав кнопку, сразу получить офигализированный вариант
- Сайт позволяет выбрать схему преобразования слова
- В подсказке под полем ввода показывается предыдущий выполненный запрос к сервису от любого пользователя, который постоянно обновляется: это даёт пользователю "чувство локтя"
- В футере страницы показывается автоматически обновляемая статистика: количество запросов к сервису. Это демонстрирует пользователю популярность сервиса.
- Для каждого успешно обработанного запроса показывается ссылка на скачивание результата в виде картинки
- Сервис доступен по https с валидным сертификатом для SEO-оптимизации
### Разработка предлагает
- Сервис разделяется на простой фронтенд (HTML+CSS+JavaScript) и бэкенд, состоящий из двух **RESTful**-микросервисов: микросервис Figalize (преобразование слова, список схем преобразования) и микросервис History (добавление запроса к истории, предоставление списка выполненных запросов)
- Разработка ведётся на **Python** + **FastAPI**
- Для хранения истории используется БД **PostgreSQL**
- Для генерации картинок используется отдельный микросервис, который загружает результат в **S3**
- Для гибкости масштабирования и более полной утилизации ресурсов микросервис картинок получает задания на обработку из **Kafka** топика от микросервиса преобразования слов
### Эксплуатация предлагает
- Использовать инструменты observability
- Получать из микросервисов метрики производительности в формате **Prometheus**
- Получать из микросервисов логи
- Graceful degradation для микросервисов
- Запуск в **Kubernetes**
- Запуск в облаке
- Использовать подход Infrastructure as Code с помощью **Terraform**
- Для ускорения запуска будет использоваться DBaaS в облаке
- Для упрощения и ускорения разработки, тестирования и деплоя необходимо построить автоматизированный пайплайн **Gitlab-CI**
- Использовать паттерны [12 Factor App](https://12factor.net/)
## Архитектура

                                                            ... .......
                                                          ... ..      ......
                 https://figachechnaya.ru                .                 ..
                            │                            .                 ..
                            │SSL                      ....        S3      ..
                            │                         .         bucket    ...
                    ┌───────▼───────┐                 ..   .                ..
                    │ INGRESS NGINX │                  ......               ..
                    └───────┬───────┘                       ...  ...   .....
                            │            dowload image        ▲... ......
                            │  ┌──────────────────────────────┘    ▲
                            │  │                                   │
                        HTTP│  │ ┌─────────────────────────────┐   │
                            │  │ │               get image url │   │
         get history ┌──────▼──┴─┴┐ figalize                   │   │
           ┌─────────┤  FRONTEND  ├───────────┐                │   │upload to S3
           │         └────────────┘ get schema│                │   │generated PNG
           │                                  │                │   │
           │                                  │                │   │
    ┌──────▼────────┐                ┌────────▼─────┐  ┌───────▼───┴──┐
    │    HISTORY    │  POST history  │   FIGALIZE   │  │   IMAGIZER   │
    │  microservice │◄───────────────┤ microservice │  │ microservice │
    └──────┬────────┘                └──────┬───────┘  └────────▲─────┘
           │                                │                   │
           │                          phrase│                   │msg
           │       ┌──────────┐         ┌───▼───────────────────┴──┐
           │       │          │         │          KAFKA           │
           │STORE  │          │         └──────────────────────────┘
           └──────►│POSTGRESQL│
            QUERY  │          │
                   │          │
                   └──────────┘

## API
API доступен из интернета, и автоматически построенную OpenAPI-документацию можно посмотреть здесь:
- Figalize: https://figachechnaya.ru/api/figalize/docs
- History: https://figachechnaya.ru/api/history/docs
## Сделано
- Написан простой фронтенд на HTML+CSS+JS
- Написаны асинхронные RESTful stateless-микросервисы на **Python + FastAPI** с хранением данных в БД **PostgreSQL**
- Микросервисы Figalize и Imagizer используют **Kafka** для передачи и получения заданий на создание картинок
- Созданные картинки автоматически загружаются в **S3**, а ссылка на них асинхронно передаётся во фронтенд
- Микросервисы экспортируют метрики в **Prometheus**-формате
- Микросервисы умеют в асинхронное выполнение запросов
- Сервисы частично умеют в graceful degradation
- Написан инфраструктурный **Terraform**-код (облачные сетевые объекты, DBaaS, K8s-кластер, деплой приложений и helm-чартов в K8s)
- Написан **Gitlab-CI** пайплайн для разворачивания всего сервиса из кода (Validate -> Build -> Deploy)
- Сервисы получают сертификаты через **cert-manager**
- В кластер деплоится Prometheus-stack для сбора метрик и визуализации
- **Prometheus** настроен из кода на service discovery и скрейп метрик из приложений
- В **Grafana** настроены 4 golden signal по метрикам из ингресса приложения и ещё пара дашбордов
## Todo
- Общий формат логирования
- Сбор логов в Loki
- **Многочисленные** доработки мониторинга
  - Добавить метрики в сервис Imagizer
  - Собрать метрики из DBaaS
  - Провижининг Grafana
  - Доработка дашбордов
- Упаковка приложения в Helm-чарт
- Доработка пайплайна деплоя, добавить роллбек
- Управление резервными копиями БД
- Линтинг для Python на шаге Validate
- Добавить шаг с юнит-тестами для Python
- Добавить шаг с SAST-тестами
- Автоматическое управление релизами

## Не сделано и в планах нет
- Доработка фронтенда и линтер HTML+CSS+JS на шаге Validate: слишком нерелевантный навык для меня
- Автотесты HTML+CSS+JS
- Отдельные окружения для DEV/QA/Stage: слишком дорогая аренда ресурсов
## Автор всего кода
Сергей Краснов, realscorp@outlook.com