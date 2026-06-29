# MessageCollector
Стек сервисов выполняющий сборку и кеширование в БД сообщений из заданных телеграм-каналов. Доступ к закешированым данным осуществляется через RES API сервис 

# Состав приложения
Стек состоит из 3-х контейнеров:
 - mc-database - БД на базе Postgres 18
 - mc-collector - Telegram user bot, получает сообщения из чатов и сохраняет их в БД
 - mc-api - REST API сервис для доступа к сохраненным сообщениям 
# Запуск
 - Запуск стека:
    `docker-compose -f docker-compose.yml.prod up -d --force-recreate`
 - Остановка:
    `docker-compose -f docker-compose.yml.prod down`
