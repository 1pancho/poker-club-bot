# 🚀 Deployment Guide - Poker Club Bot

## Overview
This project consists of three main components:
1. **Telegram Bot** (Python) - Handles user interactions and game state
2. **WebSocket Server** (Node.js) - Real-time multiplayer game server
3. **Mini App Frontend** (React + Vite) - Beautiful poker UI in Telegram

## Prerequisites
- Server with Ubuntu/Debian
- Node.js 20+ (use nvm)
- Python 3.12+
- Nginx (for serving static files)
- Domain or subdomain for the Mini App

## 1. Deploy Telegram Bot

### On your server (212.113.106.241):

```bash
cd /opt/poker-club-bot
git pull origin main

# Install Python dependencies
pip install -r requirements.txt

# Update environment variables
sudo nano .env
```

Add these variables:
```env
BOT_TOKEN=your_bot_token
WEBAPP_URL=https://your-domain.com/poker
```

Restart the bot:
```bash
sudo systemctl restart poker-bot
sudo systemctl status poker-bot
```

## 2. Deploy WebSocket Server

```bash
cd /opt/poker-club-bot/server

# Install dependencies
npm install

# Start with PM2 (production process manager)
npm install -g pm2
pm2 start index.js --name poker-ws
pm2 save
pm2 startup
```

The WebSocket server runs on port 3001 by default.

### Nginx reverse proxy for WebSocket:
```nginx
# Add to your nginx config
location /ws {
    proxy_pass http://localhost:3001;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
}
```

## 3. Deploy Mini App Frontend

### Option A: GitHub Pages (Recommended for quick start)

```bash
cd webapp

# Build the app
npm run build

# Install gh-pages
npm install -D gh-pages

# Add to package.json scripts:
"deploy": "gh-pages -d dist"

# Deploy
npm run deploy
```

Your app will be available at: `https://USERNAME.github.io/REPO-NAME/`

### Option B: Self-hosted with Nginx

```bash
cd webapp
npm run build

# Copy dist folder to server
scp -r dist/* user@server:/var/www/poker-app/

# Nginx config
sudo nano /etc/nginx/sites-available/poker-app
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /var/www/poker-app;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # WebSocket proxy
    location /ws {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/poker-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL with Let's Encrypt (Required for Telegram Mini Apps):
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 4. Configure Telegram Bot

1. Go to [@BotFather](https://t.me/BotFather)
2. Send `/setmenubutton`
3. Choose your bot
4. Send button text: "🎮 Play Poker"
5. Send Mini App URL: `https://your-domain.com/`

## 5. Update Environment Variables

Update the bot's `.env` file with the Mini App URL:

```bash
WEBAPP_URL=https://your-domain.com/
```

Also update the WebSocket URL in `webapp/src/services/websocket.ts` if needed:
```typescript
connect(url: string = 'wss://your-domain.com/ws'): void {
```

## Testing

1. Start a chat with your bot: `@your_bot`
2. Send `/start`
3. Click "🎮 Играть в покер" button
4. The Mini App should open with the poker table

## Monitoring

Check logs:
```bash
# Bot logs
sudo journalctl -u poker-bot -f

# WebSocket server logs
pm2 logs poker-ws

# Nginx logs
sudo tail -f /var/nginx/logs/access.log
```

## Troubleshooting

### Mini App doesn't load:
- Check HTTPS is configured (required by Telegram)
- Verify WEBAPP_URL in bot's .env
- Check browser console for errors

### WebSocket connection fails:
- Ensure WebSocket server is running: `pm2 status`
- Check firewall allows port 3001
- Verify Nginx WebSocket proxy config

### Bot not responding:
- Check bot service: `sudo systemctl status poker-bot`
- Verify BOT_TOKEN in .env
- Check logs for errors

## Auto-deployment with GitHub Actions

The repo already has `.github/workflows/deploy.yml` configured for automatic deployment on push to main branch.

Update the secrets in GitHub repo settings:
- `SERVER_HOST`: Your server IP
- `SERVER_USER`: SSH user
- `SSH_PRIVATE_KEY`: Private key for deployment
- `BOT_TOKEN`: Telegram bot token
- `WEBAPP_URL`: Mini App URL

## Production Checklist

- [ ] SSL certificate configured
- [ ] Environment variables set
- [ ] Bot service running and enabled
- [ ] WebSocket server running with PM2
- [ ] Mini App accessible via HTTPS
- [ ] Telegram Bot menu button configured
- [ ] Database backups configured
- [ ] Monitoring and logging set up
- [ ] Firewall rules configured

## URLs

- **Bot**: [@your_bot](https://t.me/your_bot)
- **Mini App**: https://your-domain.com/
- **WebSocket**: wss://your-domain.com/ws
- **GitHub**: https://github.com/1pancho/poker-club-bot

## Support

For issues, check:
1. Server logs
2. Browser console (F12)
3. GitHub Issues

---

🎰 Happy gaming! 🃏
