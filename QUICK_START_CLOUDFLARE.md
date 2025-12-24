# Deploy to Cloudflare Workers - BEST FREE OPTION

## Чому Cloudflare краще ніж Railway?

| Параметр | Cloudflare | Railway | Heroku |
|----------|-----------|---------|--------|
| Вартість | **$0-20/mo** | $5-50/mo | $7+/mo |
| Холодний старт | < 50ms | 100ms+ | 5-10s |
| Глобальна мережа | ✅ 270+ міст | Лише США | Лише США |
| Масштабування | Автоматичне | Ручне | Ручне |
| Базові дані | D1 SQL (free) | PostgreSQL (платна) | Платна |
| CDN | Вбудована | Ні | Ні |
| DDoS захист | Вбудований | Ні | Ні |
| Caching | KV (free) | Redis | Платна |

---

## 🚀 Розгортування на Cloudflare Workers (30 хвилин)

### Крок 1: Створити Cloudflare акаунт (5 хв)
```bash
# Перейти на https://dash.cloudflare.com/sign-up
# Зареєструватися з email
# Підтвердити email
```

### Крок 2: Встановити Wrangler CLI (5 хв)
```bash
npm install -g wrangler
wrangler login
# Авторизуватися через браузер
```

### Крок 3: Налаштувати wrangler.toml (10 хв)
```toml
name = "heatmap-saas-api"
main = "src/index.js"
compatibility_date = "2024-12-20"
routes = [
  { pattern = "api.heatmap.dev/*", zone_id = "your-zone-id" }
]

[[kv_namespaces]]
binding = "HEATMAP_KV"
id = "your-kv-namespace-id"

[[d1_databases]]
binding = "HEATMAP_DB"
database_name = "heatmap"
database_id = "your-db-id"

[env.production]
vars = { API_KEY = "sk_live_..." }
```

### Крок 4: Створити функцію Worker (5 хв)
```javascript
// src/index.js
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    if (url.pathname === '/health') {
      return new Response(JSON.stringify({ status: 'ok' }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    if (url.pathname === '/api/heatmap') {
      // Отримати з KV cache
      const cached = await env.HEATMAP_KV.get(url.search);
      if (cached) return new Response(cached);
      
      // Запит до Google Gemini API
      const response = await fetch(
        'https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contents: [{ parts: [{ text: `Generate heatmap for: ${url.search}` }] }]
          })
        }
      );
      
      const result = await response.json();
      
      // Кешувати на 1 день
      await env.HEATMAP_KV.put(url.search, JSON.stringify(result), {
        expirationTtl: 86400
      });
      
      return new Response(JSON.stringify(result), {
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    return new Response('Not found', { status: 404 });
  }
};
```

### Крок 5: Розгорнути (3 хв)
```bash
wrangler deploy
# URL: https://heatmap-saas-api.username.workers.dev
```

---

## 💾 Cloudflare D1 для БД (Безплатна SQL БД)

### Створити базу даних
```bash
wrangler d1 create heatmap-db
```

### Міграція
```sql
-- schema.sql
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  email TEXT UNIQUE,
  stripe_id TEXT,
  plan TEXT,
  created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS heatmaps (
  id INTEGER PRIMARY KEY,
  user_id INTEGER,
  location TEXT,
  data JSON,
  created_at TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Запустити міграцію
```bash
wrangler d1 execute heatmap-db --file=schema.sql
```

---

## 🔗 Cloudflare KV для Кешування (Безплатна)

### Створити KV простір
```bash
wrangler kv:namespace create "HEATMAP_KV"
```

### Використання в коді
```javascript
// Встановити значення
await env.HEATMAP_KV.put('key', 'value', { expirationTtl: 3600 });

// Отримати значення
const value = await env.HEATMAP_KV.get('key');

// Видалити значення
await env.HEATMAP_KV.delete('key');
```

---

## 🌐 Cloudflare Durable Objects для Реал-тайму

Для WebSocket та реал-тайм оновлень (безплатна опція):

```javascript
// src/durable_object.js
export class HeatmapWebSocket {
  constructor(state) {
    this.state = state;
    this.sockets = [];
  }
  
  async fetch(request) {
    if (request.headers.get('upgrade') === 'websocket') {
      const pair = new WebSocketPair();
      this.sockets.push(pair[1]);
      
      pair[1].accept();
      pair[1].addEventListener('message', (msg) => {
        // Трансляція повідомлення всім клієнтам
        for (const socket of this.sockets) {
          socket.send(msg.data);
        }
      });
      
      return new Response(null, { status: 101, webSocket: pair[0] });
    }
  }
}
```

---

## 💰 Цінова модель Cloudflare

### Безплатна tier (IDEAL для MVP):
- 100,000 запитів/день на Workers ✅
- D1 SQL (5GB, 1M рядків) ✅
- KV (1GB сховище) ✅
- Durable Objects: 1M операцій/день ✅
- Глобальна мережа CDN ✅
- SSL/TLS сертифікати ✅

### Платна (якщо потрібно масштабування):
- $0.50 за мільйон запитів
- Виходити за безплатні ліміти рідко для MVP

---

## 🔑 Stripe інтеграція на Cloudflare

### Webhook обробник
```javascript
export default {
  async fetch(request, env) {
    if (request.method === 'POST' && request.url.includes('/stripe-webhook')) {
      const payload = await request.text();
      const signature = request.headers.get('stripe-signature');
      
      // Верифікація підпису
      const crypto = require('crypto');
      const hmac = crypto
        .createHmac('sha256', env.STRIPE_WEBHOOK_SECRET)
        .update(payload)
        .digest('hex');
      
      if (hmac !== signature.split(',')[1].split('=')[1]) {
        return new Response('Invalid signature', { status: 403 });
      }
      
      const event = JSON.parse(payload);
      
      if (event.type === 'customer.subscription.created') {
        // Зберегти підписку в D1
        await env.HEATMAP_DB.prepare(
          'INSERT INTO subscriptions (stripe_id, plan) VALUES (?, ?)'
        ).bind(event.data.object.customer, event.data.object.items.data[0].price.nickname).run();
      }
      
      return new Response('OK', { status: 200 });
    }
  }
};
```

---

## 🎯 Стратегія розгортування

### Варіант A: Тільки Workers (НАЙШВИДШИЙ) - 30 хвилин
```
Cloudflare Workers (API) 
    ↓ 
Cloudflare KV (Cache) 
    ↓ 
Google Gemini API (LLM) 
    ↓ 
Stripe API (Платежі)
```

### Варіант B: Workers + D1 (З БАЗОЮ) - 1 година
```
Cloudflare Workers (API) 
    ↓ 
Cloudflare D1 (SQL БД) 
    ↓ 
Cloudflare KV (Cache) 
    ↓ 
Google Gemini API
```

### Варіант C: Full Stack (PRODUCTION) - 2 години
```
Cloudflare Pages (Frontend) 
    ↓ 
Cloudflare Workers (Backend) 
    ↓ 
Cloudflare D1 (БД) 
    ↓ 
Cloudflare Durable Objects (Реал-тайм) 
    ↓ 
Cloudflare KV (Cache)
```

---

## ✅ Швидка контрольна таблиця (30 хвилин)

- [ ] Зареєстуватися на Cloudflare
- [ ] Встановити Wrangler
- [ ] Клонувати цей репо
- [ ] Створити wrangler.toml
- [ ] Додати GOOGLE_API_KEY
- [ ] Додати STRIPE_API_KEY
- [ ] Запустити `wrangler deploy`
- [ ] Тестувати `/health` endpoint
- [ ] Готово! 🎉

---

## 🚀 Тестування

```bash
# Здоров'я
curl https://heatmap-saas-api.username.workers.dev/health

# Генерувати теплову карту
curl "https://heatmap-saas-api.username.workers.dev/api/heatmap?location=NYC&category=restaurants"

# Крім того, розроблювати локально
wrangler dev
# Відкрити http://localhost:8787
```

---

**Резюме:** Cloudflare Workers — це НАЙКРАЩИЙ вибір для MVP. Це безплатна, глобальна, швидка мережа з вбудованим кешуванням, БД, WebSockets — все що вам потрібно для запуску SaaS за 30 хвилин! 🚀
