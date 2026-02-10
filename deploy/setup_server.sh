#!/bin/bash

# Скрипт для первоначальной настройки сервера
# Запустите этот скрипт на вашем сервере один раз

set -e

echo "🚀 Начало настройки сервера для Poker Club Bot"

# Проверяем, что скрипт запущен с правами sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ Пожалуйста, запустите скрипт с sudo"
    exit 1
fi

# Обновляем систему
echo "📦 Обновление пакетов..."
apt-get update
apt-get upgrade -y

# Устанавливаем необходимые пакеты
echo "📦 Установка необходимых пакетов..."
apt-get install -y python3 python3-pip python3-venv git

# Спрашиваем путь для установки
read -p "Введите путь для установки бота (по умолчанию: /opt/poker-bot): " INSTALL_PATH
INSTALL_PATH=${INSTALL_PATH:-/opt/poker-bot}

# Создаем директорию для бота
echo "📁 Создание директории $INSTALL_PATH..."
mkdir -p $INSTALL_PATH
cd $INSTALL_PATH

# Клонируем репозиторий
read -p "Введите URL вашего GitHub репозитория: " REPO_URL
if [ ! -d ".git" ]; then
    echo "📥 Клонирование репозитория..."
    git clone $REPO_URL .
else
    echo "ℹ️ Репозиторий уже клонирован"
fi

# Создаем виртуальное окружение
echo "🐍 Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
echo "📦 Установка зависимостей Python..."
pip install -r requirements.txt

# Создаем .env файл
echo "⚙️ Создание конфигурационного файла..."
read -p "Введите BOT_TOKEN от @BotFather: " BOT_TOKEN
cat > .env << EOF
BOT_TOKEN=$BOT_TOKEN
DATABASE_URL=poker_club.db
EOF

# Создаем systemd service
echo "🔧 Создание systemd service..."
cat > /etc/systemd/system/poker-bot.service << EOF
[Unit]
Description=Poker Club Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_PATH
Environment="PATH=$INSTALL_PATH/venv/bin"
ExecStart=$INSTALL_PATH/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Перезагружаем systemd и запускаем сервис
echo "🔄 Запуск сервиса..."
systemctl daemon-reload
systemctl enable poker-bot
systemctl start poker-bot

# Проверяем статус
echo ""
echo "✅ Настройка завершена!"
echo ""
echo "Проверка статуса бота:"
systemctl status poker-bot --no-pager

echo ""
echo "📝 Полезные команды:"
echo "  Просмотр логов:        sudo journalctl -u poker-bot -f"
echo "  Перезапуск бота:       sudo systemctl restart poker-bot"
echo "  Остановка бота:        sudo systemctl stop poker-bot"
echo "  Статус бота:           sudo systemctl status poker-bot"
echo ""
echo "🔑 Для настройки GitHub Actions добавьте следующие secrets:"
echo "  SERVER_HOST:           IP адрес вашего сервера"
echo "  SERVER_USER:           root (или другой пользователь)"
echo "  SERVER_PORT:           22 (или другой SSH порт)"
echo "  SSH_PRIVATE_KEY:       Приватный SSH ключ для доступа"
echo "  DEPLOY_PATH:           $INSTALL_PATH"
