# 🔐 GitHub Secrets Setup Guide

## Необходимые секреты для автоматического деплоя

Перейдите в настройки репозитория:
**GitHub → Settings → Secrets and variables → Actions → New repository secret**

### 1. SERVER_HOST
**Описание:** IP-адрес или домен вашего сервера
```
Значение: 212.113.106.241
```
или
```
Значение: your-domain.com
```

### 2. SERVER_USER
**Описание:** SSH пользователь на сервере
```
Значение: root
```
или другой пользователь с sudo правами

### 3. SSH_PRIVATE_KEY
**Описание:** Приватный SSH ключ для доступа к серверу

**Как получить:**
```bash
# На вашем локальном компьютере
cat ~/.ssh/id_rsa
```

**Или создать новый ключ специально для деплоя:**
```bash
# Создать новый ключ
ssh-keygen -t rsa -b 4096 -C "poker-deploy" -f ~/.ssh/poker-deploy

# Скопировать публичный ключ на сервер
ssh-copy-id -i ~/.ssh/poker-deploy.pub root@212.113.106.241

# Скопировать приватный ключ для GitHub Secrets
cat ~/.ssh/poker-deploy
```

**Формат:** Весь вывод команды, включая заголовки:
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
...
-----END OPENSSH PRIVATE KEY-----
```

### 4. SERVER_PORT (опционально)
**Описание:** SSH порт (по умолчанию 22)
```
Значение: 22
```

### 5. DEPLOY_PATH
**Описание:** Путь к директории на сервере где будет развёрнуто приложение
```
Значение: /opt/poker-club-bot
```

### 6. BOT_TOKEN
**Описание:** Токен вашего Telegram бота от @BotFather
```
Значение: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 7. WEBAPP_URL
**Описание:** URL где будет доступен Mini App
```
Значение: http://212.113.106.241/
```
или
```
Значение: https://your-domain.com/
```

**ВАЖНО:** Для Telegram Mini Apps требуется HTTPS! Настройте SSL:
```bash
# На сервере установите certbot
apt-get install certbot python3-certbot-nginx

# Получите SSL сертификат
certbot --nginx -d your-domain.com
```

## 🚀 После настройки секретов

1. Проверьте что все секреты добавлены:
   - GitHub → Settings → Secrets and variables → Actions

2. Запустите деплой:
   - Вариант A: Сделайте любой коммит и пуш в main
   - Вариант B: GitHub → Actions → Re-run workflow

3. Отслеживайте прогресс:
   - https://github.com/1pancho/poker-club-bot/actions

## ✅ Проверка после деплоя

После успешного деплоя проверьте:

### 1. Telegram Bot
```bash
ssh root@212.113.106.241
systemctl status poker-bot
journalctl -u poker-bot -f
```

### 2. WebSocket Server
```bash
pm2 status
pm2 logs poker-ws
curl http://localhost:3001/health
```

### 3. Mini App
```bash
curl http://localhost/
```
Или откройте в браузере: http://212.113.106.241/

### 4. Nginx
```bash
systemctl status nginx
nginx -t
```

## 🔧 Настройка Telegram Bot Menu Button

После деплоя настройте кнопку меню в боте:

1. Откройте [@BotFather](https://t.me/BotFather)
2. Отправьте `/setmenubutton`
3. Выберите вашего бота
4. Текст кнопки: `🎮 Play Poker`
5. URL Mini App: `http://212.113.106.241/` (или ваш домен)

## 🌐 Настройка домена (опционально)

Если у вас есть домен:

1. Добавьте A-запись в DNS:
```
poker.yourdomain.com → 212.113.106.241
```

2. Настройте SSL:
```bash
certbot --nginx -d poker.yourdomain.com
```

3. Обновите WEBAPP_URL в GitHub Secrets:
```
WEBAPP_URL=https://poker.yourdomain.com/
```

4. Сделайте пуш чтобы обновить деплой

## 📊 Мониторинг

### Логи в реальном времени:
```bash
# Bot logs
journalctl -u poker-bot -f

# WebSocket logs
pm2 logs poker-ws

# Nginx access log
tail -f /var/log/nginx/access.log

# Nginx error log
tail -f /var/log/nginx/error.log
```

### Перезапуск сервисов:
```bash
# Restart bot
systemctl restart poker-bot

# Restart WebSocket
pm2 restart poker-ws

# Restart nginx
systemctl restart nginx
```

## 🆘 Troubleshooting

### Bot не запускается:
```bash
journalctl -u poker-bot -n 50
# Проверить .env файл
cat /opt/poker-club-bot/.env
```

### WebSocket не работает:
```bash
pm2 logs poker-ws --lines 50
# Проверить что порт 3001 свободен
netstat -tulpn | grep 3001
```

### Mini App не открывается:
```bash
# Проверить nginx
nginx -t
systemctl status nginx
# Проверить файлы
ls -la /var/www/poker-app/
```

### SSL проблемы:
```bash
certbot certificates
certbot renew --dry-run
```

---

**После настройки всех секретов деплой будет происходить автоматически при каждом пуше в main!** 🚀
