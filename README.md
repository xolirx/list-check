<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=JetBrains+Mono&weight=700&size=40&pause=100&color=FFFFFF&center=true&vCenter=true&width=800&height=100&lines=GHOSTSHIELD+VPN+%E2%96%88;SUBSCRIPTION+STORE+%E2%96%88;DARK+MODE+ON+%E2%96%88" alt="GhostShield VPN animated title" />
</p>

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=JetBrains+Mono&weight=500&size=16&pause=800&color=888888&center=true&vCenter=true&width=600&height=40&lines=%C2%BB+Open-Store+%D0%BF%D0%BE%D0%B4%D0%BF%D0%B8%D1%81%D0%BE%D0%BA+%D0%B8+%D0%BA%D0%BE%D0%BD%D1%84%D0%B8%D0%B3%D1%83%D1%80%D0%B0%D1%86%D0%B8%D0%B9;%C2%BB+%D0%B0%D0%B2%D1%82%D0%BE%D0%B3%D0%B5%D0%BD%D0%B5%D1%80%D0%B0%D1%86%D0%B8%D1%8F+%D0%B8+%D1%80%D0%B0%D0%B7%D0%B4%D0%B0%D1%87%D0%B0+%D0%BF%D0%BE%D0%B4%D0%BF%D0%B8%D1%81%D0%BE%D0%BA;%C2%BB+%D0%BF%D1%80%D0%BE%D0%B2%D0%B5%D1%80%D0%BA%D0%B0+%D1%81%D0%B5%D1%80%D0%B2%D0%B5%D1%80%D0%BE%D0%B2+%D0%B8+%D0%B6%D0%B8%D0%B2%D1%8B%D1%85+%D0%BA%D0%BE%D0%BD%D1%84%D0%B8%D0%B3%D0%BE%D0%B2" alt="subtitle" />
</p>

<div align="center">

![Status: Active](https://img.shields.io/badge/STATUS-ACTIVE-white?style=for-the-badge&labelColor=000000&color=000000)
![VPN](https://img.shields.io/badge/VLESS-Reality-white?style=for-the-badge&labelColor=000000&color=000000)
![Auto Update](https://img.shields.io/badge/UPDATE-daily-white?style=for-the-badge&labelColor=000000&color=000000)
![OS](https://img.shields.io/badge/PLATFORM-GitHub-white?style=for-the-badge&labelColor=000000&color=000000)

</div>

---

<br />

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=JetBrains+Mono&weight=700&size=20&pause=600&color=FFFFFF&center=true&vCenter=true&width=700&height=50&lines=%E2%9E%A4+%D0%9F%D1%80%D0%BE+%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82;%E2%9E%A4+%D1%8D%D1%82%D0%BE+%D0%BA%D0%BE%D0%BF%D0%B8%D0%BB%D0%BA%D0%B0%2C+%D0%B0+%D0%BD%D0%B5+%D0%BF%D1%80%D0%BE%D0%B4-%D0%B1%D0%B0%D0%B7%D0%B0;%E2%9E%A4+%D1%82%D0%B0%D0%BA+%D1%83%D0%B4%D0%BE%D0%B1%D0%BD%D0%BE" alt="about" />
</p>

<div align="center">

Это репозиторий-**копилка** GhostShield VPN. Сюда складываются актуальные списки серверов, всё автоматически проверяется на живость и раздаётся клиентам через персональные подписки.

Всё хранится в открытом виде — осознанно. Это хранилище конфигураций, а не прод-база.

</div>

<br />

---

## 📂 Структура репозитория

| Файл | Назначение |
|---|---|
| `Black Sub` | Общая подписка **BLACK** — основной список серверов |
| `LTE Sub` | Общая подписка **LTE** — мобильный канал |
| `wi-fi(black).txt` | Wi-Fi профиль с кастомной темой Happ |
| `proxy-tg.txt` | Telegram MTProto-прокси |
| `color.txt` | Happ color-profile — кастомная тема клиента |
| `subs/` | Индивидуальные подписки `<user_id>_<profile>.txt` |

> **Данные пользователей перенесены:** `users.json`, `config.json`, `users.txt`, `block.txt` теперь живут в репозитории [`xolirx/db`](https://github.com/xolirx/db) (папка `free bot`). Здесь остаются только сервера и подписки.

---

## 🛡️ Профили

> **BLACK** — серверы в Европе, России и США. VLESS + Reality / XHTTP, канал до 10 Gbit/s.
>
> **LTE** — мобильная линейка, оптимизирована под LTE-подключения.
>
> **Happ color-profile** — кастомная тема оформления подписки в приложении **Happ**.

---

## 🔁 Жизненный цикл подписки

```mermaid
flowchart LR
    A[Проверка серверов] --> B[Формирование списков]
    B --> C[Общая подписка]
    B --> D[Персональная подписка]
    D --> E[Выдача ссылки clck.ru]
    C --> F[Обновление раз в сутки]
    D --> F
```

1. Серверы проверяются на доступность, остаются только живые конфиги
2. Формируются общие подписки `Black Sub` / `LTE Sub`
3. Для каждого клиента из `users.json` собирается своя подписка в `subs/`
4. Клиенту выдаётся персональная ссылка, привязанная к его профилям

---

## 👤 Формат пользователя

```json
"123456789": {
  "terms": true,
  "subscribed": true,
  "profiles": ["black", "lte"],
  "links": { "black": "https://clck.ru/xxx" },
  "generations": 1,
  "pinned": true
}
```

| Поле | Назначение |
|---|---|
| `terms` | Принял пользовательское соглашение |
| `subscribed` | Активна ли подписка |
| `profiles` | Доступные профили (`black` / `lte`) |
| `links` | Выданные ссылки-подписки |
| `generations` | Количество генераций подписки |
| `pinned` | Приоритетный клиент |

---

## ⚙️ Конфигурация

```json
{
  "maintenance": false,
  "version": "1.0",
  "last_updated": "2026-08-02T17:57:03"
}
```

`maintenance: true` — перевод сервиса в режим обслуживания.

---

## 🔗 Ссылки

- **Поддержка:** [@GhostShield_Support](https://t.me/GhostShield_Support)
- **Протокол:** VLESS (Reality, XHTTP, gRPC, WS)

---

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=JetBrains+Mono&weight=600&size=16&pause=700&color=FFFFFF&center=true&vCenter=true&width=700&height=50&lines=%E2%96%88+GhostShield+VPN+%E2%80%94+%D0%BF%D0%BE%D0%B4%D0%BF%D0%B8%D1%81%D0%BD%D0%B0%D1%8F+%D0%BA%D0%BE%D0%BF%D0%B8%D0%BB%D0%BA%D0%B0+%D0%BA%D0%BE%D0%BD%D1%84%D0%B8%D0%B3%D1%83%D1%80%D0%B0%D1%86%D0%B8%D0%B9" alt="footer" />
</p>

<div align="center">

`© 2026 GhostShield VPN` · `dark mode on · forever`

</div>
