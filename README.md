#VKinder
Программа для поиска людей в сети Vkontakte на основе следующих данных профиля:

- возраста
- пола
- общих групп
- расположение (города)
- общих интересов
- общих книг

Вы должны быть зарегистрированы в VK и иметь заполненный профиль.
Если информации из профиля недостаточно, то программа запросит ее.

###Систамные требования
- ОС Windows или Linux
- Python 3.7 или выше [скачать](https://www.python.org/downloads/)
- База данных Postgres [скачать](https://www.postgresql.org/download/)



### Установка, настройка и запуск программы
1. Установить Python и Postgres
1. Открыть консоль и перейти в каталог программы
1. Установить зависимости командой `pip install -r requirements.txt`
1. В файле настроек `system_settings.py` выполнить настройку поключения к базе данных
1. Для запуска программы введите `python main.py`


### Пользовательский файл настроек (settings.py)

- VK_TOKEN - ключ доступа для VK (обновляется программой при автоматически)
- VK_COUNT_TO_FIND - количество кандидатов при каждом поиске (не более 1000)
 
\* при изменении параметров необходимо перезапустить программу 

### Системный файл настроек (system_settings.py)

- DB_ADMIN_USER - супервользователь базы данных, по умолчанию "postgres"
- DB_ADMIN_PASSWORD - пароль суперпользователя, по умолчанию пустой
- DB_HOSTNAME - IP-адрес или Hostname сервера. При отсутствии параметра подразумевается localhost.
- DEBUG - включение отладки
- RAW_OUTPUT_FILE - Выходной файл для запросов API VK. По умолчанию raw.txt
- SAVE_RAW_RESPONSE - Сохранить все ответы VK API в файл RAW_OUTPUT_FILE. При отсутствии параметра по умолчанию False

\* при изменении параметров необходимо перезапустить программу

## Руководство пользователя
Для доступа к базе данных Вконтакте программе необходим специальный ключ доступа
(токен). При запуске программа проверет валидность токена. Следуйте подсказкам программы
для получения и добавление нового токена.

Интерфейс программы представляет собой командную строку с опциями главного меню.

#### Главное меню

**u - Select lonely user**

Выбор текущего пользователя (screen_name или ID).
Текущий пользователь отображается в квадратных
скобках. После выбора текущего пользователя появляется информация о
количестве найденных кандидатов для текущего пользователя
в результате прошлых запусков программы.

**s - Search new candidates for lonely user;**

Запуск поиска кандидатов для текущего пользователя.
Во время выполнения отображаются информационные сооющения о текущем
этапе выполнения. Результат записывается в базу данных.
Лучше 10 кандидатов выводятся на экран и записываются в файл out.json.

**t - Top 10 scored candidates (from local database)**

Показать 10 наиболее подходящих кандидатов из базы данных и
записать результат в файл out.json.

**r - reset database;**

Удаление всех данных из локальной базы данных.

**q - for exit** 

Выход из программы.