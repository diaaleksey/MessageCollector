set -e

echo "🔄 Инициализация БД..."

# Ждем пока PostgreSQL запустится
until pg_isready; do
  echo "📡 Ожидаем запуск PostgreSQL..."
  sleep 2
done


echo "📊 Настройки:"
echo "  - Основной пользователь: $DB_USER"
echo "  - Имя БД: $DB_DB"

# Создаем таблицы
psql -v ON_ERROR_STOP=1 --username "$DB_USER" --dbname "$DB_DB" <<-EOSQL
        -- Создание таблицы сообщений
    CREATE TABLE IF NOT EXISTS messages (
        id SERIAL PRIMARY KEY,
        tg_message_id BIGINT NOT NULL,
        chat_id VARCHAR(255) NOT NULL,
        chat_name VARCHAR(255),
        timestamp TIMESTAMPTZ NOT NULL,
        text TEXT,
        media_paths JSONB,
        raw_json JSONB,
        UNIQUE(tg_message_id, chat_id)
    );

    -- Создание таблицы статуса сборщика (одна строка)
    CREATE TABLE IF NOT EXISTS collector_status (
        id INTEGER PRIMARY KEY DEFAULT 1,
        is_connected BOOLEAN,
        last_message_timestamp TIMESTAMPTZ,
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        CONSTRAINT single_row CHECK (id = 1)
    );

    -- Вставка начальной записи, если её нет
    INSERT INTO collector_status (id, is_connected, last_message_timestamp)
    VALUES (1, false, NULL)
    ON CONFLICT (id) DO NOTHING;

    -- Индексы для ускорения запросов
    CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages (timestamp DESC);
    CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages (chat_id);

EOSQL

echo "✅ Таблицы БД '$DB_DB' созданы!"







