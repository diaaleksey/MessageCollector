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

# Создаем пользователя и БД если они не существуют
psql -v ON_ERROR_STOP=1 --username "postgres" --dbname "postgres" <<-EOSQL
    -- Создаем пользователя если не существует
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$DB_USER') THEN
            CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
        ELSE
            ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
        END IF;
    END
    \$\$;

    -- Создаем БД если не существует
    SELECT 'CREATE DATABASE $DB_DB'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_DB')\gexec

    -- Даем права пользователю
    GRANT ALL PRIVILEGES ON DATABASE $DB_DB TO $DB_USER;
    ALTER DATABASE $DB_DB OWNER TO $DB_USER;

    -- Даем права на создание БД (для параллельных тестов)
    ALTER USER $DB_USER CREATEDB;

    -- Разрешаем подключения для пользователя
    GRANT pg_read_all_data TO $DB_USER;
    GRANT pg_write_all_data TO $DB_USER;

    -- Разрешаем удаленные подключения для пользователя
    ALTER SYSTEM SET listen_addresses TO '*';

    -- Перезагружаем конфигурацию
    SELECT pg_reload_conf();


EOSQL

echo "✅ БД '$DB_DB' и пользователь '$DB_USER' созданы!"
echo "🌐 Удаленный доступ для пользователя '$DB_USER' настроен!"



#    -- Добавляем правила в pg_hba.conf
#    DO \$\$
#    BEGIN
#        -- Разрешаем подключения от любого хоста для тестового пользователя
#        IF NOT EXISTS (
#            SELECT FROM pg_hba_file_rules
#            WHERE database = '{$DB_DB}'
#            AND user_name = '{$DB_USER}'
#            AND address = '0.0.0.0/0'
#        ) THEN
#            EXECUTE 'ALTER SYSTEM SET pg_hba.conf = pg_hba.conf || $$host $DB_DB $DB_USER 0.0.0.0/0 md5$$';
#        END IF;
#
#        -- Разрешаем подключения от любого хоста для всех пользователей (для тестов)
#        IF NOT EXISTS (
#            SELECT FROM pg_hba_file_rules
#            WHERE database = '{all}'
#            AND user_name = '{all}'
#            AND address = '0.0.0.0/0'
#        ) THEN
#            EXECUTE 'ALTER SYSTEM SET pg_hba.conf = pg_hba.conf || $host all all 0.0.0.0/0 md5$$';
#        END IF;
#    END
#    \$\$;
#    RAISE NOTICE 'Удаленный доступ настроен для пользователя $DB_USER';