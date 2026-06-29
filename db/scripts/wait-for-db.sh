#!/bin/sh

# Скрипт ожидания готовности PostgreSQL базы данных
# Использование: ./wait-for-db.sh host port

set -e

#host="$1"
#port="$2"
#shift 2
cmd="$@"

echo "🕐 Ожидаем доступность PostgreSQL на $DB_HOST:$DB_PORT..."

# Ожидаем пока БД не станет доступна
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_DB" -c '\q' > /dev/null 2>&1; do
  echo "📡 PostgreSQL недоступен, ждем..."
  sleep 2
done

echo "✅ PostgreSQL доступен на $DB_HOST:$DB_PORT!"

# Запускаем команду (например, миграции или приложение)
exec $cmd