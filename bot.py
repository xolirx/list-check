import asyncio
import aiohttp
import os
import logging
import logging.handlers
import sys
import json
import base64
import sqlite3
import re
import time
import signal
import ssl
import random
import gc
from html import escape
from urllib.parse import unquote
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from contextlib import contextmanager
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.handlers.RotatingFileHandler("bot.log", maxBytes=2_000_000, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

PROXIES_GITHUB_URL = "https://raw.githubusercontent.com/xolirx/list-check/main/proxy-tg.txt"
VLESS_BLACK_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS_mobile.txt"
VLESS_WHITE_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt"
VPN_GITHUB_PATH = "bla.txt"
WHITE_GITHUB_PATH = "white.txt"
VPN_BACKUP_PATH = "vpn_backup.txt"
BLACK_LIST_MY_URL = "https://raw.githubusercontent.com/xolirx/list-check/refs/heads/main/100%25.txt"

CHANNEL_USERNAME = "@vpn_by_xolirx"
WIFI_HAPP_URL = "happ://crypt5/fzvdJUczeaGwHFwuwNFnsITA18EN/m4oJL1Yie6ZbajXbiF9fb5DP7oumoFisxAqTTKd3cCOyYPnV1fiTfmBMfp1dSQ9vm1PwcMqDhqHEBtNivkjuRpCsLJACDfUnMjEpUUEm4ZRsQMlWUaa1q3LNka3cCxcqIAvXgQP0cCrlXcM9ukWwNI+3DZB7Cer6BBCHeP+m4SM4gXxmjiVxADUg3==kkJuasuzX+lDPJLW0oE+V0dEBClvQzlB4mGkbvBlqeAH0UCT40YdUiUuQnQufqObRNjepgCAXpp6dSN4FxBtueRaO7OVstnTQnR5eYrWdcB8T4HsHTO980yPACF0HIc9VMmpf4G5tC7c6ea7GOnRhiKeS5Muc0Lwecvh6yTTXvHfPr4mrQP15yyYQLCvxpsMYxHZvsgdN0QRdtnHAuwtGvZV6WPWXRPRcQ/b/D2QQo4URZm1BMj2MTLD1ney32QYGUCWyARLVXLGSSIQrg5edDXUqo8WiIau7lktBHvQ67Avi3pQTDkQ/9Pkx3RaE8rxqd+5ZvZtGv0dTC6T4mT/CFoTKoN6MwoWT1/n01O+yxMBO3Q3qajB0/J39vSTlUhiCNTds6puB9X90kj//32jQxfJ+bDowSbkzv8blPoci4uvOpGNnR539Z+C++y99cPFJup7VXiFwY/4GqaR3B6b/T3xPhARN342STmnY3ipu/9M2GfqHYYdgpL8/s9OhBKtY9jWoV1ZCwCUq6qUr8JE9/AHFUcfBWrP3dD33k7CbID39JZEIr8v6aTftN+tOgCxj11umWBhLHFayfFqR+fTqTlkPVJJDSsX49vuscQ32oLkUudbyHj9X+f82ng9UVjT2MPec8kJsu/mLQcRyF40Jp5EU52gAE3smijGfZk2fow=ff"
LTE_HAPP_URL = "happ://crypt5/fzvdmoSTHgYL6VYjUVrjbLSP20qEo54ARlhqnn4hzAWt0vgxqEV44NP6hp87uilQo7Jw2jas/auCZ8hcutw5VSEsupu7ICeoGqJTYPj44g2red8gnMw+j9XNAStpqnc47SP8DHeAiEFu2Kxr5luaHO0fJaibDLnpWOqNlshgw2yXm+F9Vd92HsgpqOB97PNv8ZoAlOMmmbSNj7/sWeQ5nJ4RWccrm9BZEE5nwJlW5Oms=W1TCm/0IGRqpoghNvvfl4DRp4QDHWW468h0tghywRNswejb3d2k41wLTuC63pAXhdocaNzzi2kR6DRFpqn6MrIkOd9UFgfw9d5ffO3vQ2uN1d7vZoC/nX4NIDgQ303Nj5OskSPd7amEEzCEwpI6aFjy1aL1unsYmbQm246AGH5CK2QPbYkzjwaHDBFJ0nC13Xeo06Ds+oZJgWFsuCjUTzkbvmMDvTVYomkfeizXNYlgK1Rm0d0iHC1+eqyrrkNPEU9NsQ444uC5Nmh9+LwJSR1SmOaeNbAFMisLU5lJGEdqSCFCuGhW3i88q4GzxPWNf7gpt0IZHyejPsy7RoNeQ8OHIshAkKptRZLJzO/A71bbf3uxqIsKclx7dpOUaOEXzKsUlGtleh85RXyFnurPrE+/n/kQKRrGdmsgKrUWLaJOO6Tq0hom6qlI8hoD5JCGqCrP7TBoxTjJb4p2llR5HMPHIGZJlPjqszDadunb9jSEZDlxGhAVTf/DJ1sd0YfvAxCf1KKwQ1LiFSPVbRYgU5iIVcz1xOMiEV3ujlqrSyBfWEe9cjrmCWJs0oONPrl++NB5WyqMokJAe0Ptf6x+kuwHx7+dYHPVlWBS3FOixV7P9Gxp9ZIggFyYqh0vCqe7x+0CqpiQth4gWpYilXfV038UiE2Tk6sLQyUdm7dx4fo8=ff"
CHANNEL_URL = "https://t.me/vpn_by_xolirx"
AGREEMENT_URL = "https://xolirx-vpn.vercel.app/terms"
RULES_URL = "https://xolirx-vpn.vercel.app/rules"
BOT_USERNAME = "xolirx_vpn_bot"
DONATE_URL = "https://finance.ozon.ru/apps/sbp/ozonbankpay/019b8af5-2537-73a7-b8f5-7b715ff19de5"
SHARE_URL = f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME}&text="

VPN_FACTS = [
    "73% пользователей не знают, что их провайдер видит название сервера, но не трафик. С современным протоколом даже это невозможно отличить от обычного HTTPS.",
    "Wi-Fi в кафе — лёгкая цель. 80% публичных сетей незашифрованы. Защита шифрует весь трафик даже в открытых сетях.",
    "Telegram шифрует чаты, но не метаданные. Защита скрывает от кого и кому вы пишете.",
    "Браузерный режим инкогнито не скрывает IP. Только защищённое подключение может это сделать.",
    "Провайдер может продавать вашу историю просмотра рекламодателям. Защита делает это невозможным.",
    "В России трафик не блокируется, если используется современный протокол. Он выглядит как обычный HTTPS.",
    "DNS-запросы видят все сайты, которые вы посещаете. Защита с собственным DNS закрывает эту утечку.",
    "Тор не заменяет защищённое подключение. Тор медленный и не защищает от утечки IP в браузере.",
    "Бесплатные сервисы продают ваши данные. В 2020 году 10GB пользовательских данных были проданы за $0.60.",
    "Современный протокол маскирует трафик под обычный HTTPS. Даже провайдер не может отличить его от обычного сайта.",
    "IPv6-утечка может раскрыть ваш реальный IP даже с защитой. Наш сервис блокирует IPv6 автоматически.",
    "Скорость зависит от расстояния до сервера. Ближайший сервер = максимальная скорость.",
    "Защита от DNS-спуфинга. Мошенники не смогут перенаправить вас на поддельный сайт.",
    "Одно подключение может одновременно защищать телефон, планшет и компьютер.",
    "Современный протокол — самый быстрый. Потеря скорости менее 5% по сравнению с прямым подключением.",
    "Защита шифрует трафик до отправки в сеть. Провайдер видит только зашифрованные данные.",
    "Публичный Wi-Fi в аэропорту — золотая жила для хакеров. Защита — единственная безопасность.",
    "Настройка занимает 2 минуты. Не требует сертификатов.",
    "WebRTC-утечка в браузере может раскрыть IP даже с защитой. Наш сервис блокирует WebRTC.",
    "Трафик невозможно дешифровать без ключа. Даже спецслужбы не могут прочитать данные.",
    "Один аккаунт может защищать всю семью. Достаточно поделиться конфигурацией.",
    "Современный протокол быстрее старых решений на 300%. Это самый быстрый протокол для обхода блокировок.",
    "Защита не замедляет интернет. Замедление вызвано шифрованием, которое занимает менее 1% времени.",
    "Наш сервис полностью бесплатный. Мы не продаём данные пользователей.",
]

SECRET_CATS = [
    "  /\\_/\\  \n ( o.o ) \n  > ^ <\n /|   |\\\n(_|   |_)",
    "  /\\_/\\  \n ( -.- ) \n  > w <\n /|   |\\\n(_|   |_)",
    "  /\\_/\\  \n ( o.o ) \n  = ^ =\n /|   |\\\n(_|   |_)",
    "  /\\_/\\  \n ( ^.^ ) \n  > ~ <\n /|   |\\\n(_|   |_)",
    "  /\\_/\\  \n ( o.o ) \n  > . <\n /|   |\\\n(_|   |_)",
]

SECRET_TIPS = [
    "Этот кот защищает твой IP.",
    "Этот кот шифрует твои данные.",
    "Этот кот блокирует слежку.",
    "Этот кот обходит блокировки.",
    "Этот кот скрывает твоё местоположение.",
]

MOSCOW_TZ = timezone(timedelta(hours=3))
PROXIES_PER_PAGE = 5
DB_TIMEOUT = 30
UPDATE_TIMEOUT = 120
BACKGROUND_INTERVAL = 60
MAX_RETRIES = 3
SUBSCRIPTION_CACHE_TTL = 300
DONATE_REMINDER_INTERVAL = 12 * 3600
MAX_DB_RETRIES = 3
VLESS_CHECK_TIMEOUT = 3
VLESS_CHECK_INTERVAL = 3600
MAX_WORKERS = 50
COMMAND_LIMIT = 10
COMMAND_WINDOW = 60

NEWS_TITLE = 1
NEWS_TEXT = 2
NEWS_IMAGE = 3
TICKET_RECEIPT = 4

BLACK_LIST_SOURCE = "all"

IMAGES = {"main": "images/gl.jpg", "donate": "images/gl.jpg"}

BUTTON_EMOJIS = {
    "connect": "5884343982816759327", "status": "5877465816030515018", "proxy": "5874986954180791957",
    "docs": "5877332341331857066", "donate": "5906995262378741881", "channel": "5924720918826848520",
    "support": "5886436057091673541", "check_servers": "5884343982816759327", "back": "5877536313623711363",
    "arrow_left": "5877536313623711363", "arrow_right": "5875506366050734240", "wifi": "5874986954180791957",
    "lte": "5874986954180791957", "cross": "5774077015388852135", "news": "5884343982816759327",
    "send": "5884343982816759327", "cancel": "5774077015388852135", "photo": "5874986954180791957",
    "skip": "5877465816030515018", "back_title": "5877536313623711363", "back_text": "5877536313623711363",
    "lang": "5877465816030515018", "stats": "5877465816030515018", "block": "5774077015388852135",
    "unblock": "5886436057091673541"
}

LANGUAGES = {
    "ru": {
        "name": "Русский", "flag": "🇷🇺", "menu": "Главное меню", "connect": "Подключиться",
        "status": "Статус", "proxy": "Прокси", "docs": "Документы", "donate": "Поддержать",
        "channel": "Канал", "support": "Поддержка", "back": "Назад", "lang_changed": "Язык изменён на Русский",
        "lang_select": "Выберите язык", "welcome": "Добро пожаловать!", "choose_lang": "Пожалуйста, выберите язык",
        "subscribe": "Для использования бота необходимо подписаться на наш канал!",
        "subscribe_desc": "В этом канале публикуются:\n\n- Розыгрыши платных подписок\n- Розыгрыши аккаунтов VPN\n- Еженедельные розыгрыши подарков\n- Анонсы новых серверов\n- Эксклюзивные предложения\n- Промокоды и скидки",
        "subscribed": "Подписаться", "check_sub": "Проверить подписку",
        "agreement": "Пожалуйста, ознакомьтесь с условиями использования",
        "accept": "Принимаю", "decline": "Отказываюсь", "connecting": "Подключение",
        "connection_desc": "Выберите подписку:\n\nБесплатная — Wi-Fi через Happ\nПремиум — все серверы + LTE",
        "choose_sub": "Выберите подписку",
        "premium_title": "30₽ за МЕСЯЦ",
        "free_sub": "Бесплатная подписка",
        "premium_desc": "Вы получаете 3 vless ключа которые обходят блокировки ютуб телеграмм дискорд и всё в быстром качестве\n\nСервера не падают\n\nГЛАВНОЕ: ВЫ ПОКУПАЕТЕ ТОЛЬКО СЕБЕ КЛЮЧИ если вы поделитесь с кем то то будет нарушение и ключ будет отозван",
        "pay": "Оплатить 30₽",
        "i_paid": "Я оплатил",
        "send_receipt": "Отправьте скриншот или фото чека об оплате\n\nНажмите /cancel чтобы отменить",
        "ticket_created": "Заявка создана!\n\nАдминистратор проверит оплату и выдаст ключи в ближайшее время.\n\nНомер заявки: #{ticket_id}",
        "ticket_exists": "У вас уже есть активная заявка #{ticket_id}. Ожидайте проверки администратором.",
        "ticket_cancelled": "Создание заявки отменено",
        "admin_tickets": "Тикеты",
        "no_tickets": "Нет заявок",
        "ticket_list_title": "Заявки на оплату ({count})",
        "ticket_status_pending": "Ожидает",
        "ticket_status_approved": "Одобрена",
        "ticket_status_rejected": "Отклонена",
        "ticket_approve": "Одобрить",
        "ticket_reject": "Отклонить",
        "ticket_notify_approved": "Заявка #{ticket_id} одобрена!\n\nВаш чек принят. Администратор свяжется с вами для выдачи ключей.",
        "ticket_notify_rejected": "Заявка #{ticket_id} отклонена.\n\nПопробуйте оформить заново или свяжитесь с поддержкой.",
        "ticket_user_info": "Пользователь: {name}\nID: {user_id}\nUsername: {username}\nСтатус: {status}\nСоздана: {created_at}",
        "loading_1": "⏳ Загрузка подписки...",
        "loading_2": "⚙️ Почти готово...",
        "loading_3": "✅ Готово!",
        "loading_4": "🔗 Ваша ссылка:"
    },
    "en": {
        "name": "English", "flag": "🇬🇧", "menu": "Main Menu", "connect": "Connect",
        "status": "Status", "proxy": "Proxy", "docs": "Documents", "donate": "Donate",
        "channel": "Channel", "support": "Support", "back": "Back", "lang_changed": "Language changed to English",
        "lang_select": "Choose language", "welcome": "Welcome!", "choose_lang": "Please choose language",
        "subscribe": "You must subscribe to our channel to use the bot!",
        "subscribe_desc": "In this channel we publish:\n\n- Paid subscription giveaways\n- VPN account giveaways\n- Weekly gift giveaways\n- New server announcements\n- Exclusive offers\n- Promo codes and discounts",
        "subscribed": "Subscribe", "check_sub": "Check subscription",
        "agreement": "Please read the terms of use",
        "accept": "Accept", "decline": "Decline", "connecting": "Connecting",
        "connection_desc": "Choose subscription:\n\nFree — Wi-Fi via Happ\nPremium — all servers + LTE",
        "choose_sub": "Choose subscription",
        "premium_title": "30₽ per MONTH",
        "free_sub": "Free subscription",
        "premium_desc": "You get 3 vless keys that bypass all blocks - youtube telegram discord and everything in fast quality\n\nServers never go down\n\nIMPORTANT: You buy keys ONLY FOR YOURSELF if you share with someone it will be a violation and the key will be revoked",
        "pay": "Pay 30₽",
        "i_paid": "I paid",
        "send_receipt": "Send a screenshot or photo of the payment receipt\n\nPress /cancel to cancel",
        "ticket_created": "Ticket created!\n\nThe admin will check the payment and send you the keys soon.\n\nTicket #: #{ticket_id}",
        "ticket_exists": "You already have an active ticket #{ticket_id}. Please wait for admin review.",
        "ticket_cancelled": "Ticket creation cancelled",
        "admin_tickets": "Tickets",
        "no_tickets": "No tickets",
        "ticket_list_title": "Payment tickets ({count})",
        "ticket_status_pending": "Pending",
        "ticket_status_approved": "Approved",
        "ticket_status_rejected": "Rejected",
        "ticket_approve": "Approve",
        "ticket_reject": "Reject",
        "ticket_notify_approved": "Ticket #{ticket_id} approved!\n\nYour receipt has been accepted. The admin will contact you with the keys.",
        "ticket_notify_rejected": "Ticket #{ticket_id} rejected.\n\nPlease try again or contact support.",
        "ticket_user_info": "User: {name}\nID: {user_id}\nUsername: {username}\nStatus: {status}\nCreated: {created_at}",
        "loading_1": "⏳ Loading subscription...",
        "loading_2": "⚙️ Almost ready...",
        "loading_3": "✅ Ready!",
        "loading_4": "🔗 Your link:"
    }
}

COUNTRIES_RU = {
    "russia": "Россия", "russian federation": "Россия", "ru": "Россия",
    "netherlands": "Нидерланды", "nl": "Нидерланды",
    "germany": "Германия", "de": "Германия",
    "usa": "США", "united states": "США", "us": "США",
    "united kingdom": "Великобритания", "uk": "Великобритания", "gb": "Великобритания",
    "france": "Франция", "fr": "Франция",
    "italy": "Италия", "it": "Италия",
    "spain": "Испания", "es": "Испания",
    "poland": "Польша", "pl": "Польша",
    "sweden": "Швеция", "se": "Швеция",
    "norway": "Норвегия", "no": "Норвегия",
    "finland": "Финляндия", "fi": "Финляндия",
    "denmark": "Дания", "dk": "Дания",
    "switzerland": "Швейцария", "ch": "Швейцария",
    "austria": "Австрия", "at": "Австрия",
    "belgium": "Бельгия", "be": "Бельгия",
    "portugal": "Португалия", "pt": "Португалия",
    "greece": "Греция", "gr": "Греция",
    "turkey": "Турция", "tr": "Турция",
    "japan": "Япония", "jp": "Япония",
    "china": "Китай", "cn": "Китай",
    "india": "Индия", "in": "Индия",
    "australia": "Австралия", "au": "Австралия",
    "canada": "Канада", "ca": "Канада",
    "brazil": "Бразилия", "br": "Бразилия",
    "singapore": "Сингапур", "sg": "Сингапур",
    "hong kong": "Гонконг", "hk": "Гонконг",
    "ukraine": "Украина", "ua": "Украина",
    "belarus": "Беларусь", "by": "Беларусь",
    "kazakhstan": "Казахстан", "kz": "Казахстан",
    "uae": "ОАЭ", "ae": "ОАЭ",
    "israel": "Израиль", "il": "Израиль",
    "mexico": "Мексика", "mx": "Мексика",
    "argentina": "Аргентина", "ar": "Аргентина",
    "chile": "Чили", "cl": "Чили",
    "colombia": "Колумбия", "co": "Колумбия",
    "peru": "Перу", "pe": "Перу",
    "venezuela": "Венесуэла", "ve": "Венесуэла",
    "egypt": "Египет", "eg": "Египет",
    "south africa": "ЮАР", "za": "ЮАР",
    "nigeria": "Нигерия", "ng": "Нигерия",
    "kenya": "Кения", "ke": "Кения",
    "morocco": "Марокко", "ma": "Марокко",
    "saudi arabia": "Саудовская Аравия", "sa": "Саудовская Аравия",
    "iran": "Иран", "ir": "Иран",
    "iraq": "Ирак", "iq": "Ирак",
    "syria": "Сирия", "sy": "Сирия",
    "lebanon": "Ливан", "lb": "Ливан",
    "jordan": "Иордания", "jo": "Иордания",
    "kuwait": "Кувейт", "kw": "Кувейт",
    "qatar": "Катар", "qa": "Катар",
    "bahrain": "Бахрейн", "bh": "Бахрейн",
    "oman": "Оман", "om": "Оман",
    "yemen": "Йемен", "ye": "Йемен",
    "afghanistan": "Афганистан", "af": "Афганистан",
    "pakistan": "Пакистан", "pk": "Пакистан",
    "bangladesh": "Бангладеш", "bd": "Бангладеш",
    "sri lanka": "Шри-Ланка", "lk": "Шри-Ланка",
    "nepal": "Непал", "np": "Непал",
    "bhutan": "Бутан", "bt": "Бутан",
    "myanmar": "Мьянма", "mm": "Мьянма",
    "thailand": "Таиланд", "th": "Таиланд",
    "vietnam": "Вьетнам", "vn": "Вьетнам",
    "malaysia": "Малайзия", "my": "Малайзия",
    "indonesia": "Индонезия", "id": "Индонезия",
    "philippines": "Филиппины", "ph": "Филиппины",
    "taiwan": "Тайвань", "tw": "Тайвань",
    "south korea": "Южная Корея", "kr": "Южная Корея",
    "mongolia": "Монголия", "mn": "Монголия",
    "cambodia": "Камбоджа", "kh": "Камбоджа",
    "laos": "Лаос", "la": "Лаос",
    "brunei": "Бруней", "bn": "Бруней",
    "east timor": "Восточный Тимор", "tl": "Восточный Тимор",
    "new zealand": "Новая Зеландия", "nz": "Новая Зеландия",
    "fiji": "Фиджи", "fj": "Фиджи",
    "papua new guinea": "Папуа-Новая Гвинея", "pg": "Папуа-Новая Гвинея",
    "latvia": "Латвия", "lv": "Латвия",
    "lithuania": "Литва", "lt": "Литва",
    "estonia": "Эстония", "ee": "Эстония",
    "slovakia": "Словакия", "sk": "Словакия",
    "czech": "Чехия", "cz": "Чехия",
    "hungary": "Венгрия", "hu": "Венгрия",
    "romania": "Румыния", "ro": "Румыния",
    "bulgaria": "Болгария", "bg": "Болгария",
    "croatia": "Хорватия", "hr": "Хорватия",
    "serbia": "Сербия", "rs": "Сербия",
    "slovenia": "Словения", "si": "Словения",
    "ireland": "Ирландия", "ie": "Ирландия",
    "luxembourg": "Люксембург", "lu": "Люксембург",
    "monaco": "Монако", "mc": "Монако",
    "iceland": "Исландия", "is": "Исландия",
    "malta": "Мальта", "mt": "Мальта",
    "cyprus": "Кипр", "cy": "Кипр",
    "albania": "Албания", "al": "Албания",
    "montenegro": "Черногория", "me": "Черногория",
    "moldova": "Молдова", "md": "Молдова",
    "georgia": "Грузия", "ge": "Грузия",
    "armenia": "Армения", "am": "Армения",
    "azerbaijan": "Азербайджан", "az": "Азербайджан",
    "anycast": "Anycast", "anycast-ip": "Anycast"
}

COUNTRY_FLAGS = {
    "Россия": "🇷🇺", "Нидерланды": "🇳🇱", "Германия": "🇩🇪", "США": "🇺🇸",
    "Великобритания": "🇬🇧", "Франция": "🇫🇷", "Италия": "🇮🇹", "Испания": "🇪🇸",
    "Польша": "🇵🇱", "Швеция": "🇸🇪", "Норвегия": "🇳🇴", "Финляндия": "🇫🇮",
    "Дания": "🇩🇰", "Швейцария": "🇨🇭", "Австрия": "🇦🇹", "Бельгия": "🇧🇪",
    "Португалия": "🇵🇹", "Греция": "🇬🇷", "Турция": "🇹🇷", "Япония": "🇯🇵",
    "Китай": "🇨🇳", "Индия": "🇮🇳", "Австралия": "🇦🇺", "Канада": "🇨🇦",
    "Бразилия": "🇧🇷", "Сингапур": "🇸🇬", "Гонконг": "🇭🇰", "Украина": "🇺🇦",
    "Беларусь": "🇧🇾", "Казахстан": "🇰🇿", "ОАЭ": "🇦🇪", "Израиль": "🇮🇱",
    "Мексика": "🇲🇽", "Аргентина": "🇦🇷", "Чили": "🇨🇱", "Колумбия": "🇨🇴",
    "Перу": "🇵🇪", "Венесуэла": "🇻🇪", "Египет": "🇪🇬", "ЮАР": "🇿🇦",
    "Нигерия": "🇳🇬", "Кения": "🇰🇪", "Марокко": "🇲🇦", "Саудовская Аравия": "🇸🇦",
    "Иран": "🇮🇷", "Ирак": "🇮🇶", "Сирия": "🇸🇾", "Ливан": "🇱🇧",
    "Иордания": "🇯🇴", "Кувейт": "🇰🇼", "Катар": "🇶🇦", "Бахрейн": "🇧🇭",
    "Оман": "🇴🇲", "Йемен": "🇾🇪", "Афганистан": "🇦🇫", "Пакистан": "🇵🇰",
    "Бангладеш": "🇧🇩", "Шри-Ланка": "🇱🇰", "Непал": "🇳🇵", "Бутан": "🇧🇹",
    "Мьянма": "🇲🇲", "Таиланд": "🇹🇭", "Вьетнам": "🇻🇳", "Малайзия": "🇲🇾",
    "Индонезия": "🇮🇩", "Филиппины": "🇵🇭", "Тайвань": "🇹🇼", "Южная Корея": "🇰🇷",
    "Монголия": "🇲🇳", "Камбоджа": "🇰🇭", "Лаос": "🇱🇦", "Бруней": "🇧🇳",
    "Восточный Тимор": "🇹🇱", "Новая Зеландия": "🇳🇿", "Фиджи": "🇫🇯",
    "Папуа-Новая Гвинея": "🇵🇬", "Латвия": "🇱🇻", "Литва": "🇱🇹", "Эстония": "🇪🇪",
    "Словакия": "🇸🇰", "Чехия": "🇨🇿", "Венгрия": "🇭🇺", "Румыния": "🇷🇴",
    "Болгария": "🇧🇬", "Хорватия": "🇭🇷", "Сербия": "🇷🇸", "Словения": "🇸🇮",
    "Ирландия": "🇮🇪", "Люксембург": "🇱🇺", "Монако": "🇲🇨", "Исландия": "🇮🇸",
    "Мальта": "🇲🇹", "Кипр": "🇨🇾", "Албания": "🇦🇱", "Черногория": "🇲🇪",
    "Молдова": "🇲🇩", "Грузия": "🇬🇪", "Армения": "🇦🇲", "Азербайджан": "🇦🇿",
    "Anycast": "🌍"
}

STATUS = {
    "vless_last": None, "vless_next": None, "proxies_last": None, "proxies_next": None,
    "proxies_count": 0, "vless_count": 0, "vless_working": 0, "vless_status": "Недоступен",
    "last_update_stats": {}
}

cached_proxies = []
cached_proxies_lock = asyncio.Lock()
status_lock = asyncio.Lock()
session = None
session_lock = asyncio.Lock()
background_task = None
image_cache = {}
is_background_updating = False
maintenance_mode = False
subscription_cache = {}
MAX_SUBSCRIPTION_CACHE = 5000
donate_reminder_last = None
bot_instance = None
user_commands = defaultdict(list)
user_langs = {}
blacklist = set()
DB_PATH = "bot_data.db"

def premium_button(text, emoji_key=None, callback_data=None, url=None, web_app=None, style=None):
    kwargs = {"text": text, "callback_data": callback_data, "url": url, "web_app": web_app}
    if emoji_key and emoji_key in BUTTON_EMOJIS:
        kwargs["icon_custom_emoji_id"] = BUTTON_EMOJIS[emoji_key]
    if style:
        kwargs["style"] = style
    return InlineKeyboardButton(**kwargs)

def safe_html(text):
    return escape(str(text)) if text else ""

def get_moscow_time():
    return datetime.now(MOSCOW_TZ)

def format_time(dt):
    if not dt:
        return "—"
    return dt.strftime('%d.%m.%Y %H:%M')

def format_time_until(dt):
    if not dt:
        return "Неизвестно"
    now = get_moscow_time()
    if dt <= now:
        return "Сейчас"
    diff = dt - now
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    if diff.days > 0:
        return f"{diff.days}д {hours}ч"
    if hours > 0:
        return f"{hours}ч {minutes}м"
    return f"{minutes}м"

def is_admin(user_id):
    return user_id == ADMIN_ID

def get_user_lang(user_id):
    return user_langs.get(user_id, "ru")

def set_user_lang(user_id, lang):
    user_langs[user_id] = lang
    with get_db_connection() as conn:
        conn.execute("INSERT INTO users (user_id, lang) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET lang = excluded.lang", (user_id, lang))
        conn.commit()

def parse_vless_config(config):
    if not config.startswith('vless://'):
        return None
    config = config[8:]
    if '@' not in config:
        return None
    parts = config.split('@')
    if len(parts) != 2:
        return None
    uuid = parts[0]
    rest = parts[1]
    if ':' not in rest:
        return None
    addr_parts = rest.split(':')
    if len(addr_parts) < 2:
        return None
    address = addr_parts[0]
    port_part = addr_parts[1]
    port_match = re.match(r'^(\d+)', port_part)
    if not port_match:
        return None
    port = int(port_match.group(1))
    params = {}
    if '?' in port_part:
        params_str = port_part.split('?')[1]
        if '#' in params_str:
            params_str = params_str.split('#')[0]
        for param in params_str.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key] = value
    return {'uuid': uuid, 'address': address, 'port': port, 'params': params}

geo_cache = {}
MAX_GEO_CACHE = 1000
IP_API_QUEUE = []
IP_API_LOCK = asyncio.Lock()
IP_API_BATCH_SIZE = 100
IP_API_RATE_LIMIT = 1.5
IP_API_LAST_CALL = 0
IP_BATCH_RESULT = {}
IP_BATCH_EVENT = {}
LAST_USER_LANGS_CLEANUP = None
USER_LANGS_CLEANUP_INTERVAL = 3600
LAST_USER_INTERACTION = {}
INTERACTION_DEBOUNCE = 30

async def _flush_ip_batch():
    global IP_API_LAST_CALL, IP_API_QUEUE
    async with IP_API_LOCK:
        if not IP_API_QUEUE:
            return
        batch = list(set(IP_API_QUEUE[:IP_API_BATCH_SIZE]))
        IP_API_QUEUE = [ip for ip in IP_API_QUEUE if ip not in batch]
        elapsed = time.time() - IP_API_LAST_CALL
        if elapsed < IP_API_RATE_LIMIT:
            await asyncio.sleep(IP_API_RATE_LIMIT - elapsed)
        sess = await get_session()
        if sess is None or sess.closed:
            return
        try:
            async with sess.post("http://ip-api.com/batch?fields=status,country,countryCode", json=[{"query": ip} for ip in batch], timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    results = await resp.json()
                    for r in results:
                        ip = r.get("query", "")
                        if r.get("status") == "success":
                            country = r.get("country", "Anycast")
                            code = r.get("countryCode", "").lower()
                            if code and len(code) == 2:
                                flag = chr(0x1F1E6 + ord(code[0].upper()) - 65) + chr(0x1F1E6 + ord(code[1].upper()) - 65)
                                IP_BATCH_RESULT[ip] = (country, flag)
                            else:
                                IP_BATCH_RESULT[ip] = (country, "🌍")
                        else:
                            IP_BATCH_RESULT[ip] = ("Anycast", "🌍")
                        if len(geo_cache) < MAX_GEO_CACHE:
                            geo_cache[ip] = IP_BATCH_RESULT[ip]
                IP_API_LAST_CALL = time.time()
        except Exception:
            pass

async def detect_country_from_ip(ip):
    if ip in geo_cache:
        return geo_cache[ip]
    if len(geo_cache) >= MAX_GEO_CACHE:
        sorted_keys = sorted(geo_cache.keys(), key=lambda k: geo_cache[k])
        for k in sorted_keys[:len(sorted_keys) // 2]:
            del geo_cache[k]
    event = asyncio.Event()
    async with IP_API_LOCK:
        if ip not in IP_API_QUEUE and ip not in IP_BATCH_RESULT:
            IP_API_QUEUE.append(ip)
        else:
            if ip in IP_BATCH_RESULT:
                return IP_BATCH_RESULT[ip]
        IP_BATCH_EVENT.setdefault(ip, event)
    await _flush_ip_batch()
    for _ in range(50):
        if ip in geo_cache:
            return geo_cache[ip]
        if ip in IP_BATCH_RESULT:
            result = IP_BATCH_RESULT.pop(ip)
            return result
        await asyncio.sleep(0.1)
    return "Anycast", "🌍"

async def format_config_with_country(line, list_type="black"):
    if list_type == "white":
        base_url = line.split('#')[0] if '#' in line else line
        return f"{base_url}#🇪🇺 Europe"
    if '#' not in line:
        return line + "#🌍 Anycast"
    base_url, fragment = line.split('#', 1)
    fragment_decoded = unquote(fragment)
    flag_match = re.search(r'([\U0001F1E6-\U0001F1FF]{2})', fragment_decoded)
    if flag_match:
        flag = flag_match.group(1)
        rest = fragment_decoded.replace(flag, '').strip()
        for name, flg in COUNTRY_FLAGS.items():
            if flg == flag:
                return f"{base_url}#{flag} {name}"
        for eng, ru in COUNTRIES_RU.items():
            if eng in rest.lower() or rest.lower() in eng:
                return f"{base_url}#{flag} {ru}"
        return f"{base_url}#{flag} {rest if rest else 'Anycast'}"
    parsed = parse_vless_config(line)
    if parsed:
        address = parsed['address']
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', address):
            country, flag = await detect_country_from_ip(address)
            if country != "Anycast":
                return f"{base_url}#{flag} {country}"
    return f"{base_url}#🌍 Anycast"

def get_vpn_status():
    if maintenance_mode:
        return "Тех. перерыв"
    if not STATUS.get('vless_last'):
        return "Недоступен"
    try:
        if get_moscow_time() - STATUS['vless_last'] > timedelta(hours=2):
            return "Требуется обновление"
    except Exception:
        return "Ошибка"
    return STATUS.get('vless_status', 'Недоступен')

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        try:
            conn.close()
        except Exception:
            pass

def init_db():
    try:
        with get_db_connection() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, user_name TEXT, accepted_at TEXT, lang TEXT DEFAULT 'ru', last_activity TEXT)""")
            conn.execute("""CREATE TABLE IF NOT EXISTS all_users (user_id INTEGER PRIMARY KEY, first_seen TEXT, last_activity TEXT)""")
            conn.execute("""CREATE TABLE IF NOT EXISTS bot_status (key TEXT PRIMARY KEY, value TEXT, updated_at TEXT)""")
            conn.execute("""CREATE TABLE IF NOT EXISTS cached_proxies (id INTEGER PRIMARY KEY AUTOINCREMENT, proxy_url TEXT UNIQUE)""")
            conn.execute("""CREATE TABLE IF NOT EXISTS donate_reminder (user_id INTEGER PRIMARY KEY, last_reminder TEXT)""")
            conn.execute("""CREATE TABLE IF NOT EXISTS blacklist (user_id INTEGER PRIMARY KEY, reason TEXT, blocked_at TEXT)""")
            conn.execute("""CREATE TABLE IF NOT EXISTS tickets (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, user_name TEXT, username TEXT, status TEXT DEFAULT 'pending', receipt_file_id TEXT, receipt_type TEXT, created_at TEXT, updated_at TEXT)""")
            try:
                conn.execute("ALTER TABLE tickets ADD COLUMN receipt_file_id TEXT")
            except sqlite3.OperationalError:
                pass
            try:
                conn.execute("ALTER TABLE tickets ADD COLUMN receipt_type TEXT")
            except sqlite3.OperationalError:
                pass
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_accepted ON users(accepted_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_activity ON users(last_activity)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_all_users_activity ON all_users(last_activity)")
            conn.commit()
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database init error: {e}")

def with_db_retry(func):
    def wrapper(*args, **kwargs):
        for attempt in range(MAX_DB_RETRIES):
            try:
                return func(*args, **kwargs)
            except sqlite3.OperationalError as e:
                if attempt < MAX_DB_RETRIES - 1:
                    time.sleep(0.2)
                else:
                    raise
            except Exception as e:
                logger.error(f"DB operation error: {e}")
                raise
    return wrapper

@with_db_retry
def save_proxies_to_db(proxies):
    if not proxies:
        return 0
    with get_db_connection() as conn:
        conn.execute("DELETE FROM cached_proxies")
        added = 0
        for proxy in proxies:
            proxy = proxy.strip()
            if proxy.startswith("tg://proxy?") and "server=" in proxy and "port=" in proxy and "secret=" in proxy:
                try:
                    conn.execute("INSERT INTO cached_proxies (proxy_url) VALUES (?)", (proxy,))
                    added += 1
                except sqlite3.IntegrityError:
                    pass
        conn.commit()
        return added

@with_db_retry
def load_proxies_from_db():
    with get_db_connection() as conn:
        return [row["proxy_url"] for row in conn.execute("SELECT proxy_url FROM cached_proxies")]

@with_db_retry
def save_status_to_db():
    with get_db_connection() as conn:
        now = get_moscow_time().isoformat()
        status_data = {
            "proxies_count": str(STATUS.get("proxies_count", 0)),
            "vless_count": str(STATUS.get("vless_count", 0)),
            "vless_working": str(STATUS.get("vless_working", 0)),
            "vless_status": str(STATUS.get("vless_status", "Недоступен")),
            "black_list_source": str(BLACK_LIST_SOURCE),
        }
        for key, value in status_data.items():
            conn.execute("INSERT OR REPLACE INTO bot_status (key, value, updated_at) VALUES (?, ?, ?)", (key, value, now))
        for key in ["proxies_last", "proxies_next", "vless_last", "vless_next"]:
            value = STATUS.get(key)
            if value:
                conn.execute("INSERT OR REPLACE INTO bot_status (key, value, updated_at) VALUES (?, ?, ?)", (key, value.isoformat(), now))
        conn.commit()

@with_db_retry
def load_status_from_db():
    global BLACK_LIST_SOURCE
    with get_db_connection() as conn:
        for row in conn.execute("SELECT key, value FROM bot_status"):
            key, value = row["key"], row["value"]
            if not value:
                continue
            if key == "black_list_source":
                if value in ["all", "my_lk"]:
                    BLACK_LIST_SOURCE = value
            elif key in ["proxies_count", "vless_count", "vless_working"]:
                try:
                    STATUS[key] = int(value)
                except ValueError:
                    pass
            elif key == "vless_status":
                STATUS[key] = value.replace("🔴 ", "").replace("🟢 ", "").replace("🟡 ", "") if value else "Недоступен"
            elif key in ["proxies_last", "proxies_next", "vless_last", "vless_next"]:
                try:
                    STATUS[key] = datetime.fromisoformat(value)
                except (ValueError, TypeError):
                    pass

@with_db_retry
def load_blacklist():
    global blacklist
    with get_db_connection() as conn:
        blacklist = {row["user_id"] for row in conn.execute("SELECT user_id FROM blacklist")}
        logger.info(f"Loaded {len(blacklist)} blacklisted users")

@with_db_retry
def load_user_langs():
    global user_langs
    with get_db_connection() as conn:
        for row in conn.execute("SELECT user_id, lang FROM users WHERE lang IS NOT NULL"):
            user_langs[row["user_id"]] = row["lang"]

@with_db_retry
def user_has_accepted(user_id):
    with get_db_connection() as conn:
        result = conn.execute("SELECT 1 FROM users WHERE user_id = ? AND accepted_at IS NOT NULL", (user_id,)).fetchone()
        return result is not None

@with_db_retry
def save_user_accept(user_id, user_name):
    with get_db_connection() as conn:
        lang = get_user_lang(user_id)
        now = get_moscow_time().isoformat()
        conn.execute("INSERT INTO users (user_id, user_name, accepted_at, lang, last_activity) VALUES (?, ?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET user_name=excluded.user_name, accepted_at=excluded.accepted_at, lang=excluded.lang, last_activity=excluded.last_activity", (user_id, user_name, now, lang, now))
        conn.commit()

@with_db_retry
def save_user_interaction(user_id):
    now = get_moscow_time()
    last = LAST_USER_INTERACTION.get(user_id)
    if last and (now - last).total_seconds() < INTERACTION_DEBOUNCE:
        return
    LAST_USER_INTERACTION[user_id] = now
    if len(LAST_USER_INTERACTION) > 10000:
        cutoff = now - timedelta(seconds=INTERACTION_DEBOUNCE * 10)
        stale = [uid for uid, ts in LAST_USER_INTERACTION.items() if ts < cutoff]
        for uid in stale:
            del LAST_USER_INTERACTION[uid]
    now_iso = now.isoformat()
    with get_db_connection() as conn:
        conn.execute("INSERT OR IGNORE INTO all_users (user_id, first_seen) VALUES (?, ?)", (user_id, now_iso))
        conn.execute("UPDATE all_users SET last_activity = ? WHERE user_id = ?", (now_iso, user_id))
        conn.execute("UPDATE users SET last_activity = ? WHERE user_id = ?", (now_iso, user_id))
        conn.commit()

@with_db_retry
def get_all_users():
    with get_db_connection() as conn:
        return [row["user_id"] for row in conn.execute("SELECT user_id FROM all_users UNION SELECT user_id FROM users")]

@with_db_retry
def get_accepted_users():
    with get_db_connection() as conn:
        return [row["user_id"] for row in conn.execute("SELECT user_id FROM users")]

@with_db_retry
def get_user_stats():
    with get_db_connection() as conn:
        total_all = conn.execute("SELECT COUNT(*) FROM all_users").fetchone()[0]
        total_accepted = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        moscow_now = get_moscow_time()
        today_cutoff = (moscow_now - timedelta(days=1)).isoformat()
        week_cutoff = (moscow_now - timedelta(days=7)).isoformat()
        today = conn.execute("SELECT COUNT(*) FROM users WHERE accepted_at >= ?", (today_cutoff,)).fetchone()[0]
        week = conn.execute("SELECT COUNT(*) FROM users WHERE accepted_at >= ?", (week_cutoff,)).fetchone()[0]
        active_today = conn.execute("SELECT COUNT(*) FROM users WHERE last_activity >= ?", (today_cutoff,)).fetchone()[0]
        active_week = conn.execute("SELECT COUNT(*) FROM users WHERE last_activity >= ?", (week_cutoff,)).fetchone()[0]
        return {"total": total_all, "accepted": total_accepted, "today": today, "week": week, "active_today": active_today, "active_week": active_week}

@with_db_retry
def get_donate_reminder_last(user_id):
    with get_db_connection() as conn:
        row = conn.execute("SELECT last_reminder FROM donate_reminder WHERE user_id = ?", (user_id,)).fetchone()
        if row and row["last_reminder"]:
            try:
                return datetime.fromisoformat(row["last_reminder"])
            except ValueError:
                pass
        return None

@with_db_retry
def save_donate_reminder(user_id):
    with get_db_connection() as conn:
        conn.execute("INSERT OR REPLACE INTO donate_reminder (user_id, last_reminder) VALUES (?, ?)", (user_id, get_moscow_time().isoformat()))
        conn.commit()

@with_db_retry
def create_ticket(user_id, user_name, username, receipt_file_id=None, receipt_type=None):
    with get_db_connection() as conn:
        now = get_moscow_time().isoformat()
        conn.execute("INSERT INTO tickets (user_id, user_name, username, receipt_file_id, receipt_type, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)", (user_id, user_name, username, receipt_file_id, receipt_type, now, now))
        conn.commit()
        return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

@with_db_retry
def get_tickets(status=None):
    with get_db_connection() as conn:
        if status:
            return [dict(row) for row in conn.execute("SELECT * FROM tickets WHERE status = ? ORDER BY created_at DESC", (status,))]
        return [dict(row) for row in conn.execute("SELECT * FROM tickets ORDER BY created_at DESC")]

@with_db_retry
def get_ticket(ticket_id):
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        return dict(row) if row else None

@with_db_retry
def update_ticket_status(ticket_id, status):
    with get_db_connection() as conn:
        now = get_moscow_time().isoformat()
        conn.execute("UPDATE tickets SET status = ?, updated_at = ? WHERE id = ?", (status, now, ticket_id))
        conn.commit()

@with_db_retry
def get_tickets_by_user(user_id):
    with get_db_connection() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM tickets WHERE user_id = ? ORDER BY created_at DESC", (user_id,))]

def cleanup_inactive_data():
    global user_langs, user_commands, geo_cache, subscription_cache
    now = get_moscow_time()
    try:
        with get_db_connection() as conn:
            week_ago = (now - timedelta(days=7)).isoformat()
            active_ids = {row["user_id"] for row in conn.execute("SELECT user_id FROM all_users WHERE last_activity >= ?", (week_ago,))}
        stale_langs = [uid for uid in user_langs if uid not in active_ids]
        for uid in stale_langs:
            del user_langs[uid]
        stale_cmds = [uid for uid in user_commands if uid not in active_ids]
        for uid in stale_cmds:
            del user_commands[uid]
        logger.info(f"Cleanup: removed {len(stale_langs)} langs, {len(stale_cmds)} command entries")
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

def rate_limit(user_id, command, limit=COMMAND_LIMIT, window=COMMAND_WINDOW):
    if user_id in blacklist:
        return False
    now = get_moscow_time()
    user_commands[user_id].append((command, now))
    user_commands[user_id] = [(cmd, ts) for cmd, ts in user_commands[user_id] if (now - ts).total_seconds() < window]
    if len(user_commands) > 5000:
        cutoff = now - timedelta(seconds=window * 2)
        stale = [uid for uid, cmds in user_commands.items() if all(ts < cutoff for _, ts in cmds)]
        for uid in stale:
            del user_commands[uid]
    return len(user_commands.get(user_id, [])) <= limit

async def get_session():
    global session
    async with session_lock:
        if session is None or session.closed:
            try:
                timeout = aiohttp.ClientTimeout(total=60, connect=15)
                connector = aiohttp.TCPConnector(limit=100, ttl_dns_cache=300, keepalive_timeout=30, enable_cleanup_closed=True)
                session = aiohttp.ClientSession(timeout=timeout, connector=connector)
            except Exception as e:
                logger.error(f"Failed to create session: {e}")
                session = None
                raise
        return session

async def close_session():
    global session
    if session and not session.closed:
        try:
            await session.close()
        except Exception:
            pass
    session = None

async def fetch_url(url, timeout=30):
    global session
    try:
        sess = await get_session()
    except Exception:
        sess = None
    if sess is None or sess.closed:
        async with session_lock:
            session = None
        sess = await get_session()
    try:
        async with sess.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
            if resp.status != 200:
                raise Exception(f"HTTP {resp.status}")
            text = await resp.text()
            if not text or len(text.strip()) < 10:
                raise Exception("Empty or too short response")
            return text
    except (aiohttp.ClientError, ConnectionError, OSError) as e:
        async with session_lock:
            session = None
        raise

async def fetch_url_with_retry(url, max_retries=MAX_RETRIES, timeout=15):
    last_error = None
    for attempt in range(max_retries):
        try:
            return await fetch_url(url, timeout)
        except Exception as e:
            last_error = e
            logger.warning(f"Error fetching {url}, attempt {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
    raise last_error or Exception(f"Failed to fetch {url} after {max_retries} attempts")

async def upload_to_github(file_path, content):
    if not GITHUB_TOKEN or not content or not content.strip():
        return False
    repo_owner = "xolirx"
    repo_name = "list-check"
    branch = "main"
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
    sha = None
    try:
        sess = await get_session()
        async with sess.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status == 200:
                data = await resp.json()
                sha = data.get("sha")
    except Exception as e:
        logger.warning(f"GitHub get error: {e}")
    data = {"message": f"Update {file_path}", "content": base64.b64encode(content.encode()).decode(), "branch": branch}
    if sha:
        data["sha"] = sha
    try:
        sess = await get_session()
        async with sess.put(url, headers=headers, json=data, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            success = resp.status in [200, 201]
            if success:
                logger.info(f"Uploaded to GitHub: {file_path}")
            else:
                logger.warning(f"GitHub upload failed: {resp.status}")
            return success
    except Exception as e:
        logger.error(f"github upload error: {e}")
        return False

async def generate_routing():
    try:
        config_json = {
            "Name": "XolirX Routing", "GlobalProxy": "true", "UseChunkFiles": "true",
            "RemoteDns": "8.8.8.8", "DomesticDns": "77.88.8.8",
            "RemoteDNSType": "DoH", "RemoteDNSDomain": "https://8.8.8.8/dns-query", "RemoteDNSIP": "8.8.8.8",
            "DomesticDNSType": "DoH", "DomesticDNSDomain": "https://77.88.8.8/dns-query", "DomesticDNSIP": "77.88.8.8",
            "Geoipurl": "https://cdn.jsdelivr.net/gh/hydraponique/roscomvpn-geoip@202607020649/release/geoip.dat",
            "Geositeurl": "https://cdn.jsdelivr.net/gh/hydraponique/roscomvpn-geosite@202604152235/release/geosite.dat",
            "LastUpdated": str(int(time.time())),
            "DnsHosts": {"lkfl2.nalog.ru": "213.24.64.175", "lknpd.nalog.ru": "213.24.64.181"},
            "RouteOrder": "block-proxy-direct",
            "DirectSites": ["geosite:private", "geosite:category-ru", "geosite:whitelist", "geosite:microsoft", "geosite:apple", "geosite:epicgames", "geosite:riot", "geosite:escapefromtarkov", "geosite:steam", "geosite:twitch", "geosite:pinterest", "geosite:faceit"],
            "DirectIp": ["geoip:private", "geoip:direct"],
            "ProxySites": ["geosite:google-play", "geosite:github", "geosite:twitch-ads", "geosite:youtube", "geosite:telegram"],
            "ProxyIp": [],
            "BlockSites": ["geosite:win-spy", "geosite:torrent", "geosite:category-ads"],
            "BlockIp": [],
            "DomainStrategy": "IPIfNonMatch",
            "FakeDNS": "false"
        }
        new_base64 = base64.b64encode(json.dumps(config_json, separators=(',', ':')).encode()).decode().rstrip('=')
        return f"happ://routing/onadd/{new_base64}"
    except Exception as e:
        logger.error(f"Routing generation error: {e}")
        return ""

async def check_vless_server(parsed_config):
    address = parsed_config["address"]
    port = parsed_config["port"]
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(address, port, ssl=False), timeout=VLESS_CHECK_TIMEOUT)
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        pass
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        reader, writer = await asyncio.wait_for(asyncio.open_connection(address, port, ssl=context), timeout=VLESS_CHECK_TIMEOUT)
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        pass
    return False

async def check_vless_servers_batch(configs):
    if not configs:
        return 0, 0, []
    parsed_configs = []
    valid_configs = []
    for config in configs:
        parsed = parse_vless_config(config)
        if parsed:
            parsed_configs.append(parsed)
            valid_configs.append(config)
    if not parsed_configs:
        return 0, 0, []
    semaphore = asyncio.Semaphore(MAX_WORKERS)
    async def check_with_semaphore(parsed):
        async with semaphore:
            return await check_vless_server(parsed)
    tasks = [check_with_semaphore(parsed) for parsed in parsed_configs]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    working_count = 0
    for result in results:
        if isinstance(result, Exception):
            continue
        if result:
            working_count += 1
    return len(parsed_configs), working_count, valid_configs

async def update_vless_status():
    try:
        if BLACK_LIST_SOURCE == "my_lk":
            text = await fetch_url_with_retry(BLACK_LIST_MY_URL, timeout=15)
            if text:
                all_servers = [line.strip() for line in text.splitlines() if line.strip().startswith('vless://')]
                all_servers = list(set(all_servers))
                total = len(all_servers)
                STATUS['vless_working'] = total
                STATUS['vless_count'] = total
                STATUS['vless_status'] = '100% рабочие' if total > 0 else 'Недоступен'
                logger.info(f"MY LK VLESS: {total} servers (all working)")
            else:
                STATUS['vless_working'] = 0
                STATUS['vless_count'] = 0
                STATUS['vless_status'] = 'Недоступен'
        else:
            black_text = await fetch_url_with_retry(VLESS_BLACK_URL, timeout=15)
            white_text = await fetch_url_with_retry(VLESS_WHITE_URL, timeout=15)
            all_servers = []
            for text in [black_text, white_text]:
                if text:
                    for line in text.splitlines():
                        if line.strip().startswith('vless://'):
                            all_servers.append(line.strip())
            all_servers = list(set(all_servers))
            if not all_servers:
                logger.warning("No VLESS servers found for checking")
                STATUS['vless_working'] = 0
                STATUS['vless_count'] = 0
                STATUS['vless_status'] = 'Недоступен'
                return
            total, working, valid = await check_vless_servers_batch(all_servers)
            STATUS['vless_working'] = working
            STATUS['vless_count'] = total
            STATUS['vless_status'] = 'Онлайн' if total > 0 and working > 0 else 'Недоступен'
            logger.info(f"ALL VLESS check: {working}/{total} servers working")
    except Exception as e:
        logger.error(f"VLESS status update error: {e}")
        if STATUS.get('vless_working', 0) == 0:
            STATUS['vless_status'] = 'Недоступен'

async def fetch_and_save_black():
    try:
        url = BLACK_LIST_MY_URL if BLACK_LIST_SOURCE == "my_lk" else VLESS_BLACK_URL
        logger.info(f"Using {BLACK_LIST_SOURCE} source for Black List")
        text = await fetch_url_with_retry(url, timeout=30)
        if not text:
            logger.error("Empty response from Black List")
            return False
        content_lines = []
        for line in text.splitlines():
            if line.startswith("#") or not line.strip():
                continue
            if line.strip().startswith("vless://"):
                formatted = await format_config_with_country(line, "black")
                content_lines.append(formatted)
        clean_content = "\n".join(content_lines)
        if not clean_content:
            logger.error("No VLESS servers found in Black List")
            return False
        routing_link = await generate_routing()
        header = "#profile-title: XolirX VPN | 🚀\n#profile-update-interval: 1\n#subscription-userinfo: expire=3082665600; download=10737418240; upload=0; total=21474836480\n#support-url: https://t.me/xolirx\n#profile-web-page-url: https://xolirx-vpn.vercel.app/\n#announce: 🟠 Сервис полностью бесплатный | 🟠 Поддержка - @xolirx - telegram | 🟠 Канал - @vpn_by_xolirx\n#subscription-pin: true\n#hide-settings: 1\n#color-profile: {\"backgroundGradientRotationAngle\":37.1,\"serverRowBackgroundColor\":\"#2D0000FF\",\"subsHeaderColor\":\"#FF3B30FF\",\"profileWebPageIconColor\":\"#FF6B6BFF\",\"selectedServerRowColor\":\"#5A1E1EFF\",\"disclosureSubHeaderTextColor\":\"#FFA3A3FF\",\"buttonTextColor\":\"#FFFFFFFF\",\"buttonTimerColor\":\"#FFFFFFFF\",\"subscriptionInfoBackgroundColor\":\"#3D0000FF\",\"backgroundColors\":[\"#4A0E0EFF\",\"#7A1A1AFF\",\"#B32424FF\"],\"disclosureHeaderTextColor\":\"#FFFFFFFF\",\"backgroundGradientColorIntensity\":1,\"additionalOptionsButtonColor\":\"#FFFFFFFF\",\"buttonImageType\":\"light\",\"serverRowSubTitleTextColor\":\"#FFA3A3FF\",\"supportIconColor\":\"#FFFFFFFF\",\"topBarButtonsColor\":\"#FFFFFFFF\",\"subscriptionTrafficBackgroundColor\":\"#5C1A1AFF\",\"subHeaderButtonColor\":\"#FFFFFFFF\",\"buttonColor\":\"#FF3B30FF\",\"powerIconColor\":\"#7A1A1AFF\",\"subscriptionInfoTextColor\":\"#FFFFFFFF\",\"serverRowTitleTextColor\":\"#FFFFFFFF\",\"backgroundImageType\":\"system\",\"elipseColors\":[\"#FF2D2DFF\",\"#FF6B6BFF\",\"#FFA3A3FF\"],\"serverRowChevronColor\":\"#FFFFFFFF\",\"settingsControlsTintColor\":\"#FF3B30FF\"}\n#subscriptions-collapse: 0\n#ping-result: time\n#sub-info-text: 🚀 XolirX VPN - полностью бесплатный сервис! Приятного использования ❤️\n#sub-info-color: red\n#sub-info-button-text: Перейти в канал\n#sub-info-button-link: https://t.me/vpn_by_xolirx\n\n"
        content = header + clean_content + "\n\n" + routing_link
        def _write_files():
            with open(VPN_GITHUB_PATH, "w", encoding="utf-8") as f:
                f.write(content)
            with open(VPN_BACKUP_PATH, "w", encoding="utf-8") as f:
                f.write(content)
        await asyncio.to_thread(_write_files)
        github_ok = await upload_to_github(VPN_GITHUB_PATH, content)
        logger.info(f"Black List saved, GitHub: {github_ok}")
        return github_ok
    except Exception as e:
        logger.error(f"Black List error: {e}")
        return False

async def fetch_and_save_white():
    try:
        text = await fetch_url_with_retry(VLESS_WHITE_URL, timeout=30)
        if not text:
            logger.error("Empty response from White List")
            return False
        content_lines = []
        for line in text.splitlines():
            if line.startswith("#") or not line.strip():
                continue
            if line.strip().startswith("vless://") or line.strip().startswith("hysteria2://") or line.strip().startswith("trojan://"):
                formatted = await format_config_with_country(line, "white")
                content_lines.append(formatted)
        clean_content = "\n".join(content_lines)
        if not clean_content:
            logger.error("No servers found in White List")
            return False
        routing_link = await generate_routing()
        header = "#profile-title: XolirX VPN | 🚀 | WHITE\n#profile-update-interval: 1\n#subscription-userinfo: expire=3082665600; download=10737418240; upload=0; total=21474836480\n#support-url: https://t.me/xolirx\n#profile-web-page-url: https://xolirx-vpn.vercel.app/\n#announce: 🟠 Сервис полностью бесплатный | 🟠 Поддержка - @xolirx - telegram | 🟠 Канал - @vpn_by_xolirx\n#subscription-pin: true\n#hide-settings: 1\n#color-profile: {\"backgroundGradientRotationAngle\":37.1,\"serverRowBackgroundColor\":\"#2D0000FF\",\"subsHeaderColor\":\"#FF3B30FF\",\"profileWebPageIconColor\":\"#FF6B6BFF\",\"selectedServerRowColor\":\"#5A1E1EFF\",\"disclosureSubHeaderTextColor\":\"#FFA3A3FF\",\"buttonTextColor\":\"#FFFFFFFF\",\"buttonTimerColor\":\"#FFFFFFFF\",\"subscriptionInfoBackgroundColor\":\"#3D0000FF\",\"backgroundColors\":[\"#4A0E0EFF\",\"#7A1A1AFF\",\"#B32424FF\"],\"disclosureHeaderTextColor\":\"#FFFFFFFF\",\"backgroundGradientColorIntensity\":1,\"additionalOptionsButtonColor\":\"#FFFFFFFF\",\"buttonImageType\":\"light\",\"serverRowSubTitleTextColor\":\"#FFA3A3FF\",\"supportIconColor\":\"#FFFFFFFF\",\"topBarButtonsColor\":\"#FFFFFFFF\",\"subscriptionTrafficBackgroundColor\":\"#5C1A1AFF\",\"subHeaderButtonColor\":\"#FFFFFFFF\",\"buttonColor\":\"#FF3B30FF\",\"powerIconColor\":\"#7A1A1AFF\",\"subscriptionInfoTextColor\":\"#FFFFFFFF\",\"serverRowTitleTextColor\":\"#FFFFFFFF\",\"backgroundImageType\":\"system\",\"elipseColors\":[\"#FF2D2DFF\",\"#FF6B6BFF\",\"#FFA3A3FF\"],\"serverRowChevronColor\":\"#FFFFFFFF\",\"settingsControlsTintColor\":\"#FF3B30FF\"}\n#subscriptions-collapse: 0\n#ping-result: time\n#sub-info-text: 🚀 XolirX VPN - полностью бесплатный сервис! Приятного использования ❤️\n#sub-info-color: red\n#sub-info-button-text: Перейти в канал\n#sub-info-button-link: https://t.me/vpn_by_xolirx\n\n"
        content = header + clean_content + "\n\n" + routing_link
        def _write_white():
            with open(WHITE_GITHUB_PATH, "w", encoding="utf-8") as f:
                f.write(content)
        await asyncio.to_thread(_write_white)
        github_ok = await upload_to_github(WHITE_GITHUB_PATH, content)
        logger.info(f"White List saved, GitHub: {github_ok}")
        return github_ok
    except Exception as e:
        logger.error(f"White List error: {e}")
        return False

async def update_all_simple():
    black_ok = await fetch_and_save_black()
    white_ok = await fetch_and_save_white()
    await update_vless_status()
    now = get_moscow_time()
    STATUS['vless_last'] = now
    STATUS['vless_next'] = now + timedelta(hours=1)
    await asyncio.to_thread(save_status_to_db)
    return black_ok, white_ok

async def update_proxies_from_github():
    global cached_proxies
    try:
        text = await fetch_url_with_retry(PROXIES_GITHUB_URL, timeout=30)
        if not text or len(text.strip()) < 10:
            logger.warning("Proxies list empty or too short")
            async with cached_proxies_lock:
                cached_proxies = await asyncio.to_thread(load_proxies_from_db)
            return False, 0
        matches = [line.strip() for line in text.splitlines() if line.strip().startswith("tg://proxy?") and "server=" in line and "port=" in line and "secret=" in line]
        if not matches:
            logger.warning("No valid proxies found")
            async with cached_proxies_lock:
                cached_proxies = await asyncio.to_thread(load_proxies_from_db)
            return False, 0
        added = await asyncio.to_thread(save_proxies_to_db, matches)
        async with cached_proxies_lock:
            cached_proxies = await asyncio.to_thread(load_proxies_from_db)
            if not cached_proxies:
                logger.warning("Failed to load proxies from DB after save")
                return False, 0
            proxies_count = len(cached_proxies)
        STATUS['proxies_last'] = get_moscow_time()
        STATUS['proxies_next'] = STATUS['proxies_last'] + timedelta(hours=1)
        STATUS['proxies_count'] = proxies_count
        await asyncio.to_thread(save_status_to_db)
        logger.info(f"Proxies updated: {len(matches)} found, {added} new")
        return True, added
    except Exception as e:
        logger.error(f"Proxy update error: {e}")
        async with cached_proxies_lock:
            cached_proxies = await asyncio.to_thread(load_proxies_from_db)
        return False, 0

async def update_proxies_with_timeout():
    global cached_proxies
    try:
        return await asyncio.wait_for(update_proxies_from_github(), timeout=UPDATE_TIMEOUT)
    except asyncio.TimeoutError:
        logger.error("Proxies update timeout")
        async with cached_proxies_lock:
            cached_proxies = await asyncio.to_thread(load_proxies_from_db)
        return False, 0
    except Exception as e:
        logger.error(f"Proxies update error: {e}")
        async with cached_proxies_lock:
            cached_proxies = await asyncio.to_thread(load_proxies_from_db)
        return False, 0

async def send_photo(update, image_key, caption="", reply_markup=None, edit=False):
    img_data = image_cache.get(image_key)
    try:
        if edit and update and update.callback_query:
            if img_data:
                await update.callback_query.edit_message_media(media=InputMediaPhoto(media=img_data, caption=caption, parse_mode="HTML"), reply_markup=reply_markup)
            else:
                await update.callback_query.edit_message_text(caption, parse_mode="HTML", reply_markup=reply_markup)
        else:
            if update and update.effective_chat:
                if img_data:
                    await update.effective_chat.send_photo(photo=img_data, caption=caption, parse_mode="HTML", reply_markup=reply_markup)
                else:
                    await update.effective_chat.send_message(caption, parse_mode="HTML", reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Send photo error: {e}")
        try:
            if update and update.effective_chat:
                await update.effective_chat.send_message(caption, parse_mode="HTML", reply_markup=reply_markup)
        except Exception:
            pass

async def check_subscription(bot, user_id):
    try:
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        is_member = chat_member.status in ["member", "administrator", "creator"]
        return True, is_member
    except Exception as e:
        logger.error(f"Check subscription error for user {user_id}: {e}")
        return False, None

async def is_subscribed_cached(bot, user_id):
    now = time.time()
    if len(subscription_cache) >= MAX_SUBSCRIPTION_CACHE:
        sorted_keys = sorted(subscription_cache.keys(), key=lambda k: subscription_cache[k]["time"])
        for k in sorted_keys[:len(sorted_keys) // 2]:
            del subscription_cache[k]
    if user_id in subscription_cache:
        cached = subscription_cache[user_id]
        if now - cached["time"] < SUBSCRIPTION_CACHE_TTL:
            return True, cached["status"]
    ok, subscribed = await check_subscription(bot, user_id)
    subscription_cache[user_id] = {"status": subscribed, "time": now}
    return ok, subscribed

async def require_subscription(update, context):
    user_id = update.effective_user.id
    if user_id in blacklist:
        lang = get_user_lang(user_id)
        msg = "You are blocked" if lang == "en" else "Вы заблокированы"
        if update.callback_query:
            await update.callback_query.answer(msg, show_alert=True)
        return False
    ok, subscribed = await is_subscribed_cached(context.bot, user_id)
    if not ok:
        lang = get_user_lang(user_id)
        msg = "Check error" if lang == "en" else "Ошибка проверки"
        if update.callback_query:
            await update.callback_query.answer(msg, show_alert=True)
        return False
    if not subscribed:
        lang = get_user_lang(user_id)
        text = f"<b>Subscription Required</b>\n\n{LANGUAGES[lang]['subscribe']}\n\n{LANGUAGES[lang]['subscribe_desc']}\n\nSubscribe and press the button below:" if lang == "en" else f"<b>Подписка обязательна</b>\n\n{LANGUAGES[lang]['subscribe']}\n\n{LANGUAGES[lang]['subscribe_desc']}\n\nПодпишитесь и нажмите кнопку ниже:"
        keyboard = InlineKeyboardMarkup([[premium_button(LANGUAGES[lang]['subscribed'], "channel", url=CHANNEL_URL, style="success")], [premium_button(LANGUAGES[lang]['check_sub'], "status", callback_data="check_sub", style="primary")]])
        if update.callback_query:
            try:
                await update.callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
            except Exception:
                await update.callback_query.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)
        else:
            await update.effective_chat.send_message(text, parse_mode="HTML", reply_markup=keyboard)
        return False
    return True

BROADCAST_SEMAPHORE = asyncio.Semaphore(10)

async def safe_send_message(bot, chat_id, text, parse_mode="HTML", reply_markup=None):
    for attempt in range(3):
        try:
            await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode, reply_markup=reply_markup)
            return True
        except Exception as e:
            err_str = str(e).lower()
            if "429" in err_str or "too many" in err_str or "retry after" in err_str:
                wait = 30 * (attempt + 1)
                logger.warning(f"Rate limited (429), waiting {wait}s...")
                await asyncio.sleep(wait)
                continue
            return False
    return False

async def safe_send_photo(bot, chat_id, photo, caption, parse_mode="HTML", reply_markup=None):
    for attempt in range(3):
        try:
            await bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, parse_mode=parse_mode, reply_markup=reply_markup)
            return True
        except Exception as e:
            err_str = str(e).lower()
            if "429" in err_str or "too many" in err_str or "retry after" in err_str:
                wait = 30 * (attempt + 1)
                logger.warning(f"Rate limited (429), waiting {wait}s...")
                await asyncio.sleep(wait)
                continue
            return False
    return False

async def send_recovery_notification(bot, previous_working, current_working):
    if previous_working > 0 or current_working == 0:
        return
    users = await asyncio.to_thread(get_accepted_users)
    if not users:
        return
    text_ru = "<b>Серверы восстановлены!</b>\n\nVPN снова работает. Приятного пользования!"
    text_en = "<b>Servers Recovered!</b>\n\nVPN is back online. Enjoy!"
    sent = 0
    async with BROADCAST_SEMAPHORE:
        for user_id in users:
            if user_id in blacklist:
                continue
            lang = get_user_lang(user_id)
            text = text_en if lang == "en" else text_ru
            keyboard = InlineKeyboardMarkup([[premium_button("Подключиться" if lang == "ru" else "Connect", "connect", callback_data="show_connection_types", style="success")]])
            try:
                if await safe_send_message(bot, user_id, text, reply_markup=keyboard):
                    sent += 1
                await asyncio.sleep(0.05)
            except Exception:
                pass
    logger.info(f"Recovery notification sent to {sent} users")

async def send_donate_reminder(bot):
    users = await asyncio.to_thread(get_accepted_users)
    if not users:
        return
    now = get_moscow_time()
    sent = 0
    img_data = image_cache.get("donate")
    async with BROADCAST_SEMAPHORE:
        for user_id in users:
            if user_id in blacklist:
                continue
            last_reminder = await asyncio.to_thread(get_donate_reminder_last, user_id)
            if last_reminder and (now - last_reminder).total_seconds() < DONATE_REMINDER_INTERVAL:
                continue
            lang = get_user_lang(user_id)
            if lang == "en":
                text = f"<b>Support XolirX VPN</b>\n\nYour donations help us maintain the service!\n\nSBP (Ozon Bank):\n<code>{DONATE_URL}</code>\n\nThank you for your support!"
                keyboard = InlineKeyboardMarkup([[premium_button("Donate", "donate", url=DONATE_URL, style="success")], [premium_button("Hide for 24h", "back", callback_data="donate_snooze", style="primary")]])
            else:
                text = f"<b>Поддержите XolirX VPN</b>\n\nВаши пожертвования помогают нам поддерживать сервис!\n\nСБП (Ozon Банк):\n<code>{DONATE_URL}</code>\n\nСпасибо за поддержку!"
                keyboard = InlineKeyboardMarkup([[premium_button("Поддержать", "donate", url=DONATE_URL, style="success")], [premium_button("Скрыть на 24ч", "back", callback_data="donate_snooze", style="primary")]])
            try:
                if img_data:
                    if await safe_send_photo(bot, user_id, img_data, text, reply_markup=keyboard):
                        await asyncio.to_thread(save_donate_reminder, user_id)
                        sent += 1
                else:
                    if await safe_send_message(bot, user_id, text, reply_markup=keyboard):
                        await asyncio.to_thread(save_donate_reminder, user_id)
                        sent += 1
                await asyncio.sleep(0.05)
            except Exception:
                pass
    logger.info(f"Donate reminder sent: {sent} users")

def get_menu_text(user_name="Гость", lang="ru"):
    if maintenance_mode:
        return "Technical break" if lang == "en" else "Технический перерыв"
    proxies_count = STATUS.get('proxies_count', 0)
    vless_count = STATUS.get('vless_count', 0)
    vless_working = STATUS.get('vless_working', 0)
    vless_status = get_vpn_status()
    if lang == "en":
        return (
            f"━━━ XolirX ━━━\n"
            f"Hello, {user_name}!\n\n"
            f"Protection: {vless_status} ({vless_working}/{vless_count})\n"
            f"Proxy: {proxies_count}\n"
            f"━━━━━━━━━━━━━━━━"
        )
    return (
        f"━━━ XolirX ━━━\n"
        f"Привет, {user_name}!\n\n"
        f"Защита: {vless_status} ({vless_working}/{vless_count})\n"
        f"Прокси: {proxies_count}\n"
        f"━━━━━━━━━━━━━━━━"
    )

def get_main_keyboard(lang="ru"):
    if maintenance_mode:
        if lang == "en":
            return InlineKeyboardMarkup([[premium_button("Maintenance", "settings", callback_data="maintenance_info", style="danger")], [premium_button("Channel", "channel", url=CHANNEL_URL, style="primary")], [premium_button("Support", "support", url="https://t.me/xolirx", style="primary")]])
        return InlineKeyboardMarkup([[premium_button("Тех. перерыв", "settings", callback_data="maintenance_info", style="danger")], [premium_button("Канал", "channel", url=CHANNEL_URL, style="primary")], [premium_button("Поддержка", "support", url="https://t.me/xolirx", style="primary")]])
    if lang == "en":
        return InlineKeyboardMarkup([
            [premium_button("Connect", "connect", callback_data="show_connection_types", style="success")],
            [premium_button("Status", "status", callback_data="show_status", style="primary"), premium_button("Proxy", "proxy", callback_data="show_proxies_info", style="primary")],
            [premium_button("Security Tips", "docs", callback_data="show_tips", style="primary")],
            [premium_button("FAQ", "docs", callback_data="show_faq", style="primary"), premium_button("Donate", "donate", callback_data="show_donate", style="primary")],
            [premium_button("Channel", "channel", url=CHANNEL_URL, style="primary"), premium_button("Language", "lang", callback_data="select_lang", style="primary")],
            [premium_button("Support", "support", url="https://t.me/xolirx", style="primary"), premium_button("Share", "send", url=SHARE_URL + "XolirX%20-%20Secure%20Connection", style="primary")]
        ])
    return InlineKeyboardMarkup([
        [premium_button("Подключиться", "connect", callback_data="show_connection_types", style="success")],
        [premium_button("Статус", "status", callback_data="show_status", style="primary"), premium_button("Прокси", "proxy", callback_data="show_proxies_info", style="primary")],
        [premium_button("Безопасность", "docs", callback_data="show_tips", style="primary")],
        [premium_button("FAQ", "docs", callback_data="show_faq", style="primary"), premium_button("Поддержать", "donate", callback_data="show_donate", style="primary")],
        [premium_button("Канал", "channel", url=CHANNEL_URL, style="primary"), premium_button("Язык", "lang", callback_data="select_lang", style="primary")],
        [premium_button("Поддержка", "support", url="https://t.me/xolirx", style="primary"), premium_button("Поделиться", "send", url=SHARE_URL + "XolirX%20-%20Безопасное%20подключение", style="primary")]
    ])

def get_admin_keyboard(lang="ru"):
    source_label = "MY LK" if BLACK_LIST_SOURCE == "my_lk" else "ALL"
    if lang == "en":
        keyboard = [
            [premium_button("Statistics", "stats", callback_data="admin_stats"), premium_button("Update", "connect", callback_data="admin_update", style="success")],
            [premium_button("Update Proxy", "proxy", callback_data="admin_update_proxies", style="success"), premium_button("Maintenance", "settings", callback_data="admin_maintenance_toggle", style="danger")],
            [premium_button("News", "news", callback_data="admin_news", style="success"), premium_button("Tickets", "stats", callback_data="admin_tickets", style="success")],
            [premium_button("Blacklist", "block", callback_data="admin_blacklist", style="danger")],
        ]
    else:
        keyboard = [
            [premium_button("Статистика", "stats", callback_data="admin_stats"), premium_button("Обновить", "connect", callback_data="admin_update", style="success")],
            [premium_button("Обновить прокси", "proxy", callback_data="admin_update_proxies", style="success"), premium_button("Тех. перерыв", "settings", callback_data="admin_maintenance_toggle", style="danger")],
            [premium_button("Новость", "news", callback_data="admin_news", style="success"), premium_button("Тикеты", "stats", callback_data="admin_tickets", style="success")],
            [premium_button("Черный список", "block", callback_data="admin_blacklist", style="danger")],
        ]
    if BLACK_LIST_SOURCE == "all":
        keyboard.append([premium_button("Switch to MY LK" if lang == "en" else "Переключить на MY LK", "settings", callback_data="admin_toggle_black", style="primary")])
    else:
        keyboard.append([premium_button("Switch to ALL" if lang == "en" else "Переключить на ALL", "settings", callback_data="admin_toggle_black", style="primary")])
    keyboard.append([premium_button("Main Menu" if lang == "en" else "Главное меню", "back", callback_data="back_to_menu", style="danger")])
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard(lang="ru"):
    return InlineKeyboardMarkup([[premium_button("Main Menu" if lang == "en" else "Главное меню", "back", callback_data="back_to_menu", style="danger")]])

async def show_menu(update, context):
    try:
        if not await require_subscription(update, context):
            return
        user_id = update.effective_user.id
        lang = get_user_lang(user_id)
        user_name = escape(update.effective_user.username or update.effective_user.first_name or ("Guest" if lang == "en" else "Гость"))
        await send_photo(update, "main", get_menu_text(user_name, lang), get_main_keyboard(lang), edit=True)
    except Exception as e:
        logger.error(f"Show menu error: {e}")

async def start(update, context):
    user_id = update.effective_user.id
    if user_id in blacklist:
        lang = get_user_lang(user_id)
        await update.message.reply_text("You are blocked" if lang == "en" else "Вы заблокированы")
        return
    if not rate_limit(user_id, "start"):
        lang = get_user_lang(user_id)
        await update.message.reply_text("Too many requests. Please wait" if lang == "en" else "Слишком много запросов. Подождите")
        return
    logger.info(f"Start command from user {user_id}")
    await asyncio.to_thread(save_user_interaction, user_id)
    if user_id in user_langs:
        lang = user_langs[user_id]
        user_name = escape(update.effective_user.username or update.effective_user.first_name or ("Guest" if lang == "en" else "Гость"))
        try:
            ok, subscribed = await is_subscribed_cached(context.bot, user_id)
            if not ok:
                await update.message.reply_text("Check error. Try later" if lang == "en" else "Ошибка проверки. Попробуйте позже")
                return
            if not subscribed:
                text = f"<b>Subscription Required</b>\n\n{LANGUAGES[lang]['subscribe']}\n\n{LANGUAGES[lang]['subscribe_desc']}\n\nSubscribe and press the button below:" if lang == "en" else f"<b>Подписка обязательна</b>\n\n{LANGUAGES[lang]['subscribe']}\n\n{LANGUAGES[lang]['subscribe_desc']}\n\nПодпишитесь и нажмите кнопку ниже:"
                keyboard = InlineKeyboardMarkup([[premium_button(LANGUAGES[lang]['subscribed'], "channel", url=CHANNEL_URL, style="success")], [premium_button(LANGUAGES[lang]['check_sub'], "status", callback_data="check_sub", style="primary")]])
                await update.message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")
                return
            if await asyncio.to_thread(user_has_accepted, user_id):
                await send_photo(update, "main", get_menu_text(user_name, lang), get_main_keyboard(lang), edit=False)
                return
            await show_agreement(update, context, user_name, user_id)
        except Exception as e:
            logger.error(f"Start error: {e}")
            await update.message.reply_text("Error. Try later" if lang == "en" else "Ошибка. Попробуйте позже")
        return
    text = f"<b>{LANGUAGES['ru']['choose_lang']}</b>"
    keyboard = InlineKeyboardMarkup([[premium_button("Русский", "lang", callback_data="set_lang_ru", style="primary")], [premium_button("English", "lang", callback_data="set_lang_en", style="primary")]])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)


async def show_agreement(update, context, user_name, user_id):
    lang = get_user_lang(user_id)
    if lang == "en":
        text = f"<b>Welcome to XolirX VPN!</b>\n\n{LANGUAGES[lang]['agreement']}\n\n<a href='{AGREEMENT_URL}'>Terms of Service</a>\n<a href='{RULES_URL}'>Rules</a>\n\nPlease accept to continue:"
        keyboard = InlineKeyboardMarkup([[premium_button(LANGUAGES[lang]['accept'], "status", callback_data=f"accept_{user_id}", style="success")], [premium_button(LANGUAGES[lang]['decline'], "cross", callback_data="decline_agreement", style="danger")]])
    else:
        text = f"<b>Добро пожаловать в XolirX VPN!</b>\n\n{LANGUAGES[lang]['agreement']}\n\n<a href='{AGREEMENT_URL}'>Пользовательское соглашение</a>\n<a href='{RULES_URL}'>Правила использования</a>\n\nПожалуйста, примите условия для продолжения:"
        keyboard = InlineKeyboardMarkup([[premium_button(LANGUAGES[lang]['accept'], "status", callback_data=f"accept_{user_id}", style="success")], [premium_button(LANGUAGES[lang]['decline'], "cross", callback_data="decline_agreement", style="danger")]])
    if update.callback_query:
        try:
            await update.callback_query.message.delete()
        except Exception:
            pass
        await send_photo(update, "main", text, keyboard, edit=False)
    else:
        await send_photo(update, "main", text, keyboard, edit=False)

async def show_connection_types(update, context):
    if maintenance_mode:
        lang = get_user_lang(update.effective_user.id)
        await send_photo(update, "main", "Технический перерыв", get_back_keyboard(lang), edit=True)
        return
    if not await require_subscription(update, context):
        return
    lang = get_user_lang(update.effective_user.id)
    lang_data = LANGUAGES.get(lang, LANGUAGES["ru"])
    if lang == "en":
        text = (
            f"<b>{lang_data['choose_sub']}</b>\n\n"
            "━━━━━━━━━━━━━━━━\n\n"
            f"<b>{lang_data['free_sub']}</b>\n"
            "• Wi-Fi via Happ\n"
            "• LTE via Happ\n"
            "• Easy setup\n\n"
            "━━━━━━━━━━━━━━━━"
        )
    else:
        text = (
            f"<b>{lang_data['choose_sub']}</b>\n\n"
            "━━━━━━━━━━━━━━━━\n\n"
            f"<b>{lang_data['free_sub']}</b>\n"
            "• Wi-Fi через Happ\n"
            "• LTE через Happ\n"
            "• Простая настройка\n\n"
            "━━━━━━━━━━━━━━━━"
        )
    keyboard = InlineKeyboardMarkup([
        [premium_button(lang_data['free_sub'], "status", callback_data="show_free_sub", style="success")],
        [premium_button(lang_data['back'], "back", callback_data="back_to_menu", style="danger")]
    ])
    await send_photo(update, "main", text, keyboard, edit=True)

async def show_premium_subscription(update, context):
    if maintenance_mode:
        lang = get_user_lang(update.effective_user.id)
        await send_photo(update, "main", "Технический перерыв", get_back_keyboard(lang), edit=True)
        return
    if not await require_subscription(update, context):
        return
    lang = get_user_lang(update.effective_user.id)
    lang_data = LANGUAGES.get(lang, LANGUAGES["ru"])
    text = (
        f"<b>{lang_data['premium_title']}</b>\n\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"{lang_data['premium_desc']}\n\n"
        "━━━━━━━━━━━━━━━━"
    )
    keyboard = InlineKeyboardMarkup([
        [premium_button(lang_data['pay'], "donate", url=DONATE_URL, style="success")],
        [premium_button(lang_data['i_paid'], "connect", callback_data="create_ticket", style="success")],
        [premium_button(lang_data['back'], "back", callback_data="show_connection_types", style="danger")]
    ])
    await send_photo(update, "main", text, keyboard, edit=True)

async def create_ticket_handler(update, context):
    if maintenance_mode:
        lang = get_user_lang(update.effective_user.id)
        await send_photo(update, "main", "Технический перерыв", get_back_keyboard(lang), edit=True)
        return ConversationHandler.END
    if not await require_subscription(update, context):
        return ConversationHandler.END
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    lang_data = LANGUAGES.get(lang, LANGUAGES["ru"])
    existing = await asyncio.to_thread(get_tickets_by_user, user_id)
    if any(t["status"] == "pending" for t in existing):
        active = [t for t in existing if t["status"] == "pending"][0]
        text = lang_data['ticket_exists'].format(ticket_id=active["id"])
        keyboard = InlineKeyboardMarkup([[premium_button(lang_data['back'], "back", callback_data="show_premium_sub", style="danger")]])
        await send_photo(update, "main", text, keyboard, edit=True)
        return ConversationHandler.END
    text = lang_data['send_receipt']
    if update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode="HTML")
    else:
        await update.message.reply_text(text, parse_mode="HTML")
    context.user_data['ticket_user_name'] = update.effective_user.first_name or "User"
    context.user_data['ticket_username'] = update.effective_user.username or ""
    context.user_data['ticket_created_at'] = time.time()
    return TICKET_RECEIPT

async def ticket_get_receipt(update, context):
    user_id = update.effective_user.id
    if maintenance_mode:
        await update.message.reply_text("Technical break" if get_user_lang(user_id) == "en" else "Технический перерыв")
        return ConversationHandler.END
    if 'ticket_user_name' not in context.user_data:
        return ConversationHandler.END
    created_at = context.user_data.get('ticket_created_at', 0)
    if time.time() - created_at > 300:
        context.user_data.pop('ticket_user_name', None)
        context.user_data.pop('ticket_username', None)
        context.user_data.pop('ticket_created_at', None)
        return ConversationHandler.END
    lang = get_user_lang(user_id)
    lang_data = LANGUAGES.get(lang, LANGUAGES["ru"])
    user_name = context.user_data.get('ticket_user_name', update.effective_user.first_name or "User")
    username = context.user_data.get('ticket_username', update.effective_user.username or "")
    receipt_file_id = None
    receipt_type = None
    if update.message.photo:
        receipt_file_id = update.message.photo[-1].file_id
        receipt_type = "photo"
    elif update.message.document:
        receipt_file_id = update.message.document.file_id
        receipt_type = "document"
    ticket_id = await asyncio.to_thread(create_ticket, user_id, user_name, username, receipt_file_id, receipt_type)
    text = lang_data['ticket_created'].format(ticket_id=ticket_id)
    keyboard = InlineKeyboardMarkup([[premium_button(lang_data['back'], "back", callback_data="show_premium_sub", style="danger")]])
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")
    context.user_data.pop('ticket_user_name', None)
    context.user_data.pop('ticket_username', None)
    return ConversationHandler.END

async def cancel_ticket(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    lang_data = LANGUAGES.get(lang, LANGUAGES["ru"])
    if update.message:
        await update.message.reply_text(lang_data['ticket_cancelled'])
    elif update.callback_query:
        await update.callback_query.message.edit_text(lang_data['ticket_cancelled'])
    context.user_data.pop('ticket_user_name', None)
    context.user_data.pop('ticket_username', None)
    context.user_data.pop('ticket_created_at', None)
    return ConversationHandler.END

async def show_free_subscription(update, context):
    if maintenance_mode:
        lang = get_user_lang(update.effective_user.id)
        await send_photo(update, "main", "Технический перерыв", get_back_keyboard(lang), edit=True)
        return
    if not await require_subscription(update, context):
        return
    lang = get_user_lang(update.effective_user.id)
    lang_data = LANGUAGES.get(lang, LANGUAGES["ru"])
    try:
        await update.callback_query.message.delete()
    except Exception:
        pass
    msg = await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f"<b>{lang_data['loading_1']}</b>",
        parse_mode="HTML"
    )
    await asyncio.sleep(1.2)
    try:
        await msg.edit_text(f"<b>{lang_data['loading_2']}</b>", parse_mode="HTML")
    except Exception:
        pass
    await asyncio.sleep(1.2)
    try:
        await msg.edit_text(f"<b>{lang_data['loading_3']}</b>", parse_mode="HTML")
    except Exception:
        pass
    await asyncio.sleep(0.8)
    if lang == "en":
        final_text = (
            f"<b>{lang_data['loading_4']}</b>\n\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "<b>Wi-Fi</b>\n"
            f"<code>{WIFI_HAPP_URL}</code>\n\n"
            "<b>LTE</b>\n"
            f"<code>{LTE_HAPP_URL}</code>\n\n"
            "━━━━━━━━━━━━━━━━"
        )
        keyboard = InlineKeyboardMarkup([
            [premium_button("Wi-Fi", "wifi_connect", url=WIFI_HAPP_URL, style="success"),
             premium_button("LTE", "lte_connect", url=LTE_HAPP_URL, style="success")],
            [premium_button("Back", "back", callback_data="show_connection_types", style="danger")]
        ])
    else:
        final_text = (
            f"<b>{lang_data['loading_4']}</b>\n\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "<b>Wi-Fi</b>\n"
            f"<code>{WIFI_HAPP_URL}</code>\n\n"
            "<b>LTE</b>\n"
            f"<code>{LTE_HAPP_URL}</code>\n\n"
            "━━━━━━━━━━━━━━━━"
        )
        keyboard = InlineKeyboardMarkup([
            [premium_button("Wi-Fi", "wifi_connect", url=WIFI_HAPP_URL, style="success"),
             premium_button("LTE", "lte_connect", url=LTE_HAPP_URL, style="success")],
            [premium_button("Назад", "back", callback_data="show_connection_types", style="danger")]
        ])
    try:
        await msg.edit_text(final_text, parse_mode="HTML", reply_markup=keyboard)
    except Exception:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=final_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

async def show_loading_animation(update, context, lang, final_text=None, final_keyboard=None):
    lang_data = LANGUAGES.get(lang, LANGUAGES["ru"])
    try:
        await update.callback_query.message.edit_text(
            f"<b>{lang_data['loading_1']}</b>",
            parse_mode="HTML"
        )
        await asyncio.sleep(1.2)
        await update.callback_query.message.edit_text(
            f"<b>{lang_data['loading_2']}</b>",
            parse_mode="HTML"
        )
        await asyncio.sleep(1.2)
        await update.callback_query.message.edit_text(
            f"<b>{lang_data['loading_3']}</b>",
            parse_mode="HTML"
        )
        await asyncio.sleep(0.8)
        if final_text:
            await update.callback_query.message.edit_text(
                final_text,
                parse_mode="HTML",
                reply_markup=final_keyboard
            )
    except Exception:
        pass

async def show_status(update, context):
    if maintenance_mode:
        lang = get_user_lang(update.effective_user.id)
        await send_photo(update, "main", "Technical break\n\nWe'll be back soon!" if lang == "en" else "Технический перерыв", get_back_keyboard(lang), edit=True)
        return
    if not await require_subscription(update, context):
        return
    text = get_status_text(get_user_lang(update.effective_user.id))
    keyboard = InlineKeyboardMarkup([[premium_button("Проверить сервера" if get_user_lang(update.effective_user.id) == "ru" else "Check servers", "check_servers", callback_data="check_servers")], [premium_button("Главное меню" if get_user_lang(update.effective_user.id) == "ru" else "Main Menu", "back", callback_data="back_to_menu", style="danger")]])
    await send_photo(update, "main", text, keyboard, edit=True)

async def show_donate(update, context):
    if maintenance_mode:
        lang = get_user_lang(update.effective_user.id)
        await send_photo(update, "main", "Технический перерыв", get_back_keyboard(lang), edit=True)
        return
    if not await require_subscription(update, context):
        return
    lang = get_user_lang(update.effective_user.id)
    if lang == "en":
        text = (
            "<b>Support the Project</b>\n\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "Your donations help us maintain\n"
            "and improve the service!\n\n"
            "<b>SBP (Ozon Bank):</b>\n"
            f"<code>{DONATE_URL}</code>\n\n"
            "Every contribution matters.\n"
            "Thank you for your support!\n\n"
            "━━━━━━━━━━━━━━━━"
        )
        keyboard = InlineKeyboardMarkup([[premium_button("Donate", "donate", url=DONATE_URL, style="success")], [premium_button("Main Menu", "back", callback_data="back_to_menu", style="danger")]])
    else:
        text = (
            "<b>Поддержка проекта</b>\n\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "Ваши пожертвования помогают нам\n"
            "поддерживать и улучшать сервис!\n\n"
            "<b>СБП (Ozon Банк):</b>\n"
            f"<code>{DONATE_URL}</code>\n\n"
            "Каждый вклад важен.\n"
            "Спасибо за поддержку!\n\n"
            "━━━━━━━━━━━━━━━━"
        )
        keyboard = InlineKeyboardMarkup([[premium_button("Поддержать", "donate", url=DONATE_URL, style="success")], [premium_button("Главное меню", "back", callback_data="back_to_menu", style="danger")]])
    await send_photo(update, "donate", text, keyboard, edit=True)

async def show_proxies_info(update, context):
    if maintenance_mode:
        lang = get_user_lang(update.effective_user.id)
        await send_photo(update, "main", "Технический перерыв", get_back_keyboard(lang), edit=True)
        return
    if not await require_subscription(update, context):
        return
    lang = get_user_lang(update.effective_user.id)
    if lang == "en":
        text = (
            "<b>MTProto Proxy</b>\n\n"
            "━━━━━━━━━━━━━━━━\n\n"
            f"Available: {STATUS.get('proxies_count', 0)}\n"
            f"Updated: {format_time(STATUS.get('proxies_last'))}\n"
            f"Status: {'Working' if STATUS.get('proxies_count', 0) > 0 else 'None'}\n\n"
            "━━━━━━━━━━━━━━━━"
        )
        keyboard = InlineKeyboardMarkup([[premium_button("Show List", "proxy", callback_data="show_proxies_list", style="success")]], [premium_button("Main Menu", "back", callback_data="back_to_menu", style="danger")]])
    else:
        text = (
            "<b>MTProto Proxy</b>\n\n"
            "━━━━━━━━━━━━━━━━\n\n"
            f"Доступно: {STATUS.get('proxies_count', 0)}\n"
            f"Обновлено: {format_time(STATUS.get('proxies_last'))}\n"
            f"Статус: {'Работает' if STATUS.get('proxies_count', 0) > 0 else 'Нет'}\n\n"
            "━━━━━━━━━━━━━━━━"
        )
        keyboard = InlineKeyboardMarkup([[premium_button("Показать список", "proxy", callback_data="show_proxies_list", style="success")]], [premium_button("Главное меню", "back", callback_data="back_to_menu", style="danger")]])
    await send_photo(update, "main", text, keyboard, edit=True)

async def show_docs(update, context):
    if maintenance_mode:
        lang = get_user_lang(update.effective_user.id)
        await send_photo(update, "main", "Технический перерыв" if lang == "en" else "Технический перерыв", get_back_keyboard(lang), edit=True)
        return
    if not await require_subscription(update, context):
        return
    lang = get_user_lang(update.effective_user.id)
    if lang == "en":
        text = f"<b>Documents</b>\n\n<a href='{AGREEMENT_URL}'>Terms of Service</a>\n<a href='{RULES_URL}'>Rules</a>\n<a href='{CHANNEL_URL}'>Channel</a>"
        keyboard = InlineKeyboardMarkup([[premium_button("Agreement", "docs", url=AGREEMENT_URL, style="primary")], [premium_button("Rules", "docs", url=RULES_URL, style="primary")], [premium_button("Main Menu", "back", callback_data="back_to_menu", style="danger")]])
    else:
        text = f"<b>Документы</b>\n\n<a href='{AGREEMENT_URL}'>Пользовательское соглашение</a>\n<a href='{RULES_URL}'>Правила использования</a>\n<a href='{CHANNEL_URL}'>Канал</a>"
        keyboard = InlineKeyboardMarkup([[premium_button("Соглашение", "docs", url=AGREEMENT_URL, style="primary")], [premium_button("Правила", "docs", url=RULES_URL, style="primary")], [premium_button("Главное меню", "back", callback_data="back_to_menu", style="danger")]])
    await send_photo(update, "main", text, keyboard, edit=True)

async def show_instruction(update, context):
    if maintenance_mode:
        lang = get_user_lang(update.effective_user.id)
        await send_photo(update, "main", "Технический перерыв", get_back_keyboard(lang), edit=True)
        return
    if not await require_subscription(update, context):
        return
    lang = get_user_lang(update.effective_user.id)
    if lang == "en":
        text = (
            "<b>Setup Guide</b>\n\n"
            "━━━━━━━━━━━━━━━━\n"
            "<b>Step 1:</b> Install the Happ app\n"
            "<b>Step 2:</b> Click \"Connect\" below\n"
            "<b>Step 3:</b> The link will open in the app\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "<b>Apps:</b>\n"
            "• iOS — <b>Happ</b> (recommended)\n"
            "• Android — <b>Happ</b> or <b>V2rayNG</b>\n"
            "• PC — <b>Nekoray</b>\n\n"
            "<b>Instructions:</b>\n"
            "1. Install Happ from App Store or Google Play\n"
            "2. Click \"Connect\" below\n"
            "3. The link will open in the app\n"
            "4. Click \"Import\" in the app\n"
            "5. Select a server and press \"Start\"\n\n"
            "If you have questions — ask support!"
        )
        keyboard = InlineKeyboardMarkup([
            [premium_button("Подключиться", "wifi_connect", url=WIFI_HAPP_URL, style="success")],
            [premium_button("Support", "support", url="https://t.me/xolirx", style="primary")],
            [premium_button("Main Menu", "back", callback_data="back_to_menu", style="danger")]
        ])
    else:
        text = (
            "<b>  Инструкция по настройке</b>\n\n"
            "━━━━━━━━━━━━━━━━\n"
            "<b>Шаг 1:</b> Установите приложение Happ\n"
            "<b>Шаг 2:</b> Нажмите «Подключиться»\n"
            "<b>Шаг 3:</b> Ссылка откроется в приложении\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "<b>Приложения:</b>\n"
            "• iOS — <b>Happ</b> (рекомендуется)\n"
            "• Android — <b>Happ</b> или <b>V2rayNG</b>\n"
            "• ПК — <b>Nekoray</b>\n\n"
            "<b>Как настроить:</b>\n"
            "1. Установите Happ из App Store или Google Play\n"
            "2. Нажмите «Подключиться» ниже\n"
            "3. Ссылка откроется в приложении\n"
            "4. Нажмите «Импорт» в приложении\n"
            "5. Выберите сервер и нажмите «Старт»\n\n"
            "Остались вопросы? Напишите в поддержку!"
        )
        keyboard = InlineKeyboardMarkup([
            [premium_button("Подключиться", "wifi_connect", url=WIFI_HAPP_URL, style="success")],
            [premium_button("Поддержка", "support", url="https://t.me/xolirx", style="primary")],
            [premium_button("Главное меню", "back", callback_data="back_to_menu", style="danger")]
        ])
    await send_photo(update, "main", text, keyboard, edit=True)

SECURITY_TIPS = {
    "ru": [
        ("  1. Публичный Wi-Fi", "Не доверяйте открытым сетям в кафе, аэропортах и отелях. 80% из них не зашифрованы. Всегда включайте защиту перед подключением к публичному Wi-Fi."),
        ("  2. DNS-утечка", "Даже с защитой ваш провайдер может видеть какие сайты вы посещаете через DNS-запросы. Наш сервис блокирует эту утечку автоматически."),
        ("  3. Метаданные", "Telegram шифрует сообщения, но не скрывает от кого и кому вы пишете. Защита скрывает эту информацию."),
        ("  4. Браузерный режим", "Режим инкогнито НЕ скрывает ваш IP-адрес. Только защищённое подключение может это сделать."),
        ("  5. IPv6-утечка", "Ваше устройство может отправлять данные через IPv6 даже с активной защитой. Мы блокируем это автоматически."),
        ("  6. DNS-спуфинг", "Мошенники могут перенаправить вас на поддельный сайт через DNS. Защита от DNS-спуфинга встроена."),
        ("  7. Приватность", "Ваш провайдер может продавать историю просмотра рекламодателям. Защита делает это невозможным."),
    ],
    "en": [
        ("  1. Public Wi-Fi", "Don't trust open networks in cafes, airports, and hotels. 80% of them are unencrypted. Always enable protection before connecting to public Wi-Fi."),
        ("  2. DNS Leak", "Even with protection, your ISP can see which websites you visit through DNS requests. Our service blocks this leak automatically."),
        ("  3. Metadata", "Telegram encrypts messages but doesn't hide who you're talking to. Protection hides this information."),
        ("  4. Incognito Mode", "Incognito mode does NOT hide your IP address. Only a secure connection can do that."),
        ("  5. IPv6 Leak", "Your device may send data via IPv6 even with active protection. We block this automatically."),
        ("  6. DNS Spoofing", "Attackers can redirect you to a fake website through DNS. DNS spoofing protection is built in."),
        ("  7. Privacy", "Your ISP can sell your browsing history to advertisers. Protection makes this impossible."),
    ]
}

async def show_tips(update, context):
    if maintenance_mode:
        lang = get_user_lang(update.effective_user.id)
        await send_photo(update, "main", "Технический перерыв", get_back_keyboard(lang), edit=True)
        return
    if not await require_subscription(update, context):
        return
    lang = get_user_lang(update.effective_user.id)
    tips = SECURITY_TIPS.get(lang, SECURITY_TIPS["ru"])
    if lang == "en":
        text = "<b>Security Tips</b>\n\n━━━━━━━━━━━━━━━━\n\n"
        for title, desc in tips:
            text += f"<b>{title}</b>\n{desc}\n\n"
        text += "━━━━━━━━━━━━━━━━\nStay safe online!"
        keyboard = InlineKeyboardMarkup([
            [premium_button("Support", "support", url="https://t.me/xolirx", style="primary")],
            [premium_button("Main Menu", "back", callback_data="back_to_menu", style="danger")]
        ])
    else:
        text = "<b>  Советы по безопасности</b>\n\n━━━━━━━━━━━━━━━━\n\n"
        for title, desc in tips:
            text += f"<b>{title}</b>\n{desc}\n\n"
        text += "━━━━━━━━━━━━━━━━\nБудьте в безопасности в сети!"
        keyboard = InlineKeyboardMarkup([
            [premium_button("Поддержка", "support", url="https://t.me/xolirx", style="primary")],
            [premium_button("Главное меню", "back", callback_data="back_to_menu", style="danger")]
        ])
    await send_photo(update, "main", text, keyboard, edit=True)

FAQ_ITEMS = {
    "ru": [
        ("Бесплатно ли это?", "Да, полностью бесплатно. Мы не продаём данные пользователей и не требуем оплаты."),
        ("Как это работает?", "Вы устанавливаете приложение на устройство, импортируете наше подключение и нажимаете «Старт». Весь трафик защищается автоматически."),
        ("Какое приложение установить?", "Рекомендуем <b>Happ</b> — доступно в App Store и Google Play. Также подойдут V2rayNG (Android) или Nekoray (ПК)."),
        ("Wi-Fi или LTE — что выбрать?", "Сейчас доступен только Wi-Fi режим для Happ. LTE появится позже."),
        ("Почему нужна подписка на канал?", "В канале мы публикуем обновления, розыгрыши и промокоды. Подписка — это способ поддержать проект."),
        ("Безопасно ли это?", "Да. Трафик шифруется современным протоколом. Даже ваш провайдер не может видеть какие сайты вы посещаете."),
        ("Что делать если не работает?", "Попробуйте переподключиться, сменить сервер или перезапустить приложение. Если не помогло — напишите в поддержку."),
    ],
    "en": [
        ("Is it free?", "Yes, completely free. We don't sell user data and don't require payment."),
        ("How does it work?", "You install an app on your device, import our connection and press \"Start\". All traffic is protected automatically."),
        ("Which app should I install?", "We recommend <b>Happ</b> — available on App Store and Google Play. Also works with V2rayNG (Android) or Nekoray (PC)."),
        ("Wi-Fi or LTE — which to choose?", "Only Wi-Fi mode is available for Happ at the moment. LTE coming later."),
        ("Why subscribe to the channel?", "We publish updates, giveaways and promo codes in the channel. Subscription is a way to support the project."),
        ("Is it safe?", "Yes. Traffic is encrypted with a modern protocol. Even your ISP can't see which websites you visit."),
        ("What if it doesn't work?", "Try reconnecting, switching servers or restarting the app. If it doesn't help — contact support."),
    ]
}

async def show_faq(update, context):
    if maintenance_mode:
        lang = get_user_lang(update.effective_user.id)
        await send_photo(update, "main", "Технический перерыв", get_back_keyboard(lang), edit=True)
        return
    if not await require_subscription(update, context):
        return
    lang = get_user_lang(update.effective_user.id)
    faq = FAQ_ITEMS.get(lang, FAQ_ITEMS["ru"])
    if lang == "en":
        text = "<b>FAQ — Frequently Asked Questions</b>\n\n━━━━━━━━━━━━━━━━\n\n"
        for q, a in faq:
            text += f"<b>Q: {q}</b>\n{a}\n\n"
        text += "━━━━━━━━━━━━━━━━\nDidn't find your answer? Contact support!"
        keyboard = InlineKeyboardMarkup([
            [premium_button("Support", "support", url="https://t.me/xolirx", style="primary")],
            [premium_button("Main Menu", "back", callback_data="back_to_menu", style="danger")]
        ])
    else:
        text = "<b>❓ Частые вопросы</b>\n\n━━━━━━━━━━━━━━━━\n\n"
        for q, a in faq:
            text += f"<b>В: {q}</b>\n{a}\n\n"
        text += "━━━━━━━━━━━━━━━━\nНе нашли ответ? Напишите в поддержку!"
        keyboard = InlineKeyboardMarkup([
            [premium_button("Поддержка", "support", url="https://t.me/xolirx", style="primary")],
            [premium_button("Главное меню", "back", callback_data="back_to_menu", style="danger")]
        ])
    await send_photo(update, "main", text, keyboard, edit=True)

async def send_proxy_list(update, context, page=0):
    global cached_proxies
    try:
        if maintenance_mode:
            lang = get_user_lang(update.effective_user.id)
            await send_photo(update, "main", "Technical break\n\nWe'll be back soon!" if lang == "en" else "Технический перерыв", get_back_keyboard(lang), edit=False)
            return
        if not await require_subscription(update, context):
            return
        lang = get_user_lang(update.effective_user.id)
        if not cached_proxies:
            cached_proxies = await asyncio.to_thread(load_proxies_from_db)
        if not cached_proxies:
            ok, _ = await update_proxies_with_timeout()
            if not ok or not cached_proxies:
                await send_photo(update, "main", "Proxies not found\n\nAdd to GitHub:\n" + PROXIES_GITHUB_URL if lang == "en" else "Прокси не найдены\n\nДобавьте на GitHub:\n" + PROXIES_GITHUB_URL, get_back_keyboard(lang), edit=False)
                return
        if not cached_proxies:
            await send_photo(update, "main", "No proxies available" if lang == "en" else "Нет доступных прокси", get_back_keyboard(lang), edit=False)
            return
        page = int(page) if page else 0
        total_pages = max(1, (len(cached_proxies) + PROXIES_PER_PAGE - 1) // PROXIES_PER_PAGE)
        page = max(0, min(page, total_pages - 1))
        start = page * PROXIES_PER_PAGE
        end = min(start + PROXIES_PER_PAGE, len(cached_proxies))
        if lang == "en":
            text = f"<b>MTProto Proxy List</b>\n\n- Available: {len(cached_proxies)}\n- Page {page + 1}/{total_pages}"
        else:
            text = f"<b>Список MTProto прокси</b>\n\n- Доступно: {len(cached_proxies)}\n- Страница {page + 1}/{total_pages}"
        keyboard = []
        for i, url in enumerate(cached_proxies[start:end]):
            keyboard.append([premium_button(f"Proxy #{start + i + 1}", "proxy", url=url, style="primary")])
        nav = []
        if page > 0:
            nav.append(premium_button("Back" if lang == "en" else "Назад", "arrow_left", callback_data=f"proxy_page_{page - 1}", style="primary"))
        if page < total_pages - 1:
            nav.append(premium_button("Next" if lang == "en" else "Вперед", "arrow_right", callback_data=f"proxy_page_{page + 1}", style="primary"))
        if nav:
            keyboard.append(nav)
        keyboard.append([premium_button("Main Menu" if lang == "en" else "Главное меню", "back", callback_data="back_to_menu", style="danger")])
        await send_photo(update, "main", text, InlineKeyboardMarkup(keyboard), edit=True)
    except Exception as e:
        logger.error(f"Send proxy list error: {e}")
        lang = get_user_lang(update.effective_user.id)
        await send_photo(update, "main", "Proxy load error" if lang == "en" else "Ошибка загрузки прокси", get_back_keyboard(lang), edit=False)

async def check_servers_now(update, context):
    if not await require_subscription(update, context):
        return
    lang = get_user_lang(update.effective_user.id)
    await send_photo(update, "main", "Checking servers..." if lang == "en" else "Проверка серверов...", None, edit=True)
    try:
        await update_vless_status()
        await show_status(update, context)
    except Exception as e:
        logger.error(f"Manual server check error: {e}")
        lang = get_user_lang(update.effective_user.id)
        await send_photo(update, "main", "Check error" if lang == "en" else "Ошибка проверки", get_back_keyboard(lang), edit=True)

async def ping(update, context):
    start_time = time.time()
    await update.message.reply_text("Pong!")
    await update.message.reply_text(f"{round((time.time() - start_time) * 1000)} ms")

async def status(update, context):
    if maintenance_mode:
        await update.message.reply_text("Maintenance" if get_user_lang(update.effective_user.id) == "en" else "Тех.перерыв")
        return
    lang = get_user_lang(update.effective_user.id)
    vless_count = STATUS.get('vless_count', 0)
    vless_working = STATUS.get('vless_working', 0)
    bar = get_status_bar(vless_working, vless_count)
    if vless_count > 0:
        working_percent = vless_working / vless_count * 100
        server_detail = f"{vless_working}/{vless_count} ({working_percent:.1f}%)"
    else:
        server_detail = "No data" if lang == "en" else "Нет данных"
    vless_status = get_vpn_status()
    if lang == "en":
        text = f"<b>System Status</b>\n\n{bar} VPN: {vless_status}\n\nServers: {server_detail}\nProxy: {STATUS.get('proxies_count', 0)}\nUpdated: {format_time(STATUS.get('vless_last'))}"
    else:
        text = f"<b>Статус системы</b>\n\n{bar} VPN: {vless_status}\n\nСерверы: {server_detail}\nПрокси: {STATUS.get('proxies_count', 0)}\nОбновлено: {format_time(STATUS.get('vless_last'))}"
    await update.message.reply_text(text, parse_mode="HTML")

async def check(update, context):
    user_id = update.effective_user.id
    if user_id in blacklist:
        lang = get_user_lang(user_id)
        await update.message.reply_text("You are blocked" if lang == "en" else "Вы заблокированы")
        return
    if not rate_limit(user_id, "check"):
        lang = get_user_lang(user_id)
        await update.message.reply_text("Too many requests. Please wait" if lang == "en" else "Слишком много запросов. Подождите")
        return
    if maintenance_mode:
        lang = get_user_lang(user_id)
        await update.message.reply_text("Maintenance mode. Try later" if lang == "en" else "Технический перерыв. Попробуйте позже")
        return
    if not await require_subscription(update, context):
        return
    lang = get_user_lang(user_id)
    status_msg = await update.message.reply_text("Checking servers..." if lang == "en" else "Проверка серверов...")
    try:
        await update_vless_status()
        vless_count = STATUS.get('vless_count', 0)
        vless_working = STATUS.get('vless_working', 0)
        bar = get_status_bar(vless_working, vless_count)
        vless_status = get_vpn_status()
        if vless_count > 0:
            working_percent = vless_working / vless_count * 100
            if lang == "en":
                text = f"<b>Check Complete</b>\n\n{bar} VPN: {vless_status}\n\nServers: {vless_working}/{vless_count} working ({working_percent:.1f}%)\nUpdated: {format_time(STATUS.get('vless_last'))}"
            else:
                text = f"<b>Проверка завершена</b>\n\n{bar} VPN: {vless_status}\n\nСерверы: {vless_working}/{vless_count} рабочих ({working_percent:.1f}%)\nОбновлено: {format_time(STATUS.get('vless_last'))}"
        else:
            text = "No servers available" if lang == "en" else "Нет доступных серверов"
        await status_msg.edit_text(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Check command error: {e}")
        await status_msg.edit_text("Check error" if lang == "en" else "Ошибка проверки серверов")

async def select_language(update, context):
    user_id = update.effective_user.id
    if not await require_subscription(update, context):
        return
    text = "<b>Choose language / Выберите язык</b>"
    keyboard = InlineKeyboardMarkup([[premium_button("Русский", "lang", callback_data="set_lang_ru", style="primary")], [premium_button("English", "lang", callback_data="set_lang_en", style="primary")], [premium_button("Back" if get_user_lang(user_id) == "en" else "Назад", "back", callback_data="back_to_menu", style="danger")]])
    await send_photo(update, "main", text, keyboard, edit=True)

async def set_language(update, context):
    query = update.callback_query
    user_id = update.effective_user.id
    lang = "ru" if query.data == "set_lang_ru" else "en"
    set_user_lang(user_id, lang)
    await query.answer(LANGUAGES[lang]["lang_changed"], show_alert=True)
    user_name = escape(update.effective_user.username or update.effective_user.first_name or ("Guest" if lang == "en" else "Гость"))
    try:
        ok, subscribed = await is_subscribed_cached(context.bot, user_id)
        if not ok:
            await query.message.edit_text("Check error. Try later" if lang == "en" else "Ошибка проверки. Попробуйте позже")
            return
        if not subscribed:
            text = f"<b>Subscription Required</b>\n\n{LANGUAGES[lang]['subscribe']}\n\n{LANGUAGES[lang]['subscribe_desc']}\n\nSubscribe and press the button below:" if lang == "en" else f"<b>Подписка обязательна</b>\n\n{LANGUAGES[lang]['subscribe']}\n\n{LANGUAGES[lang]['subscribe_desc']}\n\nПодпишитесь и нажмите кнопку ниже:"
            keyboard = InlineKeyboardMarkup([[premium_button(LANGUAGES[lang]['subscribed'], "channel", url=CHANNEL_URL, style="success")], [premium_button(LANGUAGES[lang]['check_sub'], "status", callback_data="check_sub", style="primary")]])
            await query.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
            return
        if await asyncio.to_thread(user_has_accepted, user_id):
            await send_photo(update, "main", get_menu_text(user_name, lang), get_main_keyboard(lang), edit=True)
            return
        await show_agreement(update, context, user_name, user_id)
    except Exception as e:
        logger.error(f"Set language error: {e}")
        await query.message.edit_text("Error. Try later" if lang == "en" else "Ошибка. Попробуйте позже")

async def admin_command(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        if update.callback_query:
            await update.callback_query.edit_message_text("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён")
        else:
            await update.message.reply_text("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён")
        return
    lang = get_user_lang(user_id)
    source_label = "MY LK" if BLACK_LIST_SOURCE == "my_lk" else "ALL"
    if lang == "en":
        text = f"Admin Panel\n\n- VPN: {get_vpn_status()} ({STATUS.get('vless_count', 0)})\n- Working: {STATUS.get('vless_working', 0)}\n- Proxy: {STATUS.get('proxies_count', 0)}\n- Black List: {source_label}\n- Maintenance: {'On' if maintenance_mode else 'Off'}\n- Updated: {format_time(STATUS.get('vless_last'))}"
    else:
        text = f"Админ-панель\n\n- VPN: {get_vpn_status()} ({STATUS.get('vless_count', 0)})\n- Рабочих: {STATUS.get('vless_working', 0)}\n- Прокси: {STATUS.get('proxies_count', 0)}\n- Black List: {source_label}\n- Тех.перерыв: {'Вкл' if maintenance_mode else 'Выкл'}\n- Обновлено: {format_time(STATUS.get('vless_last'))}"
    if update.callback_query:
        await send_photo(update, "main", text, get_admin_keyboard(lang), edit=True)
    else:
        await send_photo(update, "main", text, get_admin_keyboard(lang), edit=False)

async def admin_stats(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        if update.callback_query:
            await update.callback_query.answer("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён", show_alert=True)
        else:
            await update.message.reply_text("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён")
        return
    stats = await asyncio.to_thread(get_user_stats)
    lang = get_user_lang(user_id)
    if lang == "en":
        text = f"Statistics\n\nTotal users: {stats['total']}\nAccepted: {stats['accepted']}\n- Today: {stats['today']}\n- Week: {stats['week']}\nActive today: {stats['active_today']}\nActive week: {stats['active_week']}"
        keyboard = InlineKeyboardMarkup([[premium_button("Update", "status", callback_data="admin_stats", style="success")], [premium_button("Back", "back", callback_data="back_to_admin", style="danger")]])
    else:
        text = f"Статистика\n\nВсего пользователей: {stats['total']}\nПриняли соглашение: {stats['accepted']}\n- Сегодня: {stats['today']}\n- Неделя: {stats['week']}\nАктивных сегодня: {stats['active_today']}\nАктивных за неделю: {stats['active_week']}"
        keyboard = InlineKeyboardMarkup([[premium_button("Обновить", "status", callback_data="admin_stats", style="success")], [premium_button("Назад", "back", callback_data="back_to_admin", style="danger")]])
    if update.callback_query:
        await send_photo(update, "main", text, keyboard, edit=True)
    else:
        await send_photo(update, "main", text, keyboard, edit=False)

async def admin_blacklist(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.callback_query.answer("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён", show_alert=True)
        return
    lang = get_user_lang(user_id)
    if lang == "en":
        text = f"Blacklist ({len(blacklist)} users)\n\nCommands:\n/block <user_id> - block user\n/unblock <user_id> - unblock user\n\nCurrent blacklist:"
    else:
        text = f"Черный список ({len(blacklist)} пользователей)\n\nКоманды:\n/block <user_id> - заблокировать\n/unblock <user_id> - разблокировать\n\nТекущий список:"
    if blacklist:
        users_list = list(blacklist)[:50]
        text += "\n" + "\n".join(f"- {uid}" for uid in users_list)
        if len(blacklist) > 50:
            text += f"\n... and {len(blacklist) - 50} more" if lang == "en" else f"\n... и ещё {len(blacklist) - 50}"
    keyboard = InlineKeyboardMarkup([[premium_button("Back" if lang == "en" else "Назад", "back", callback_data="back_to_admin", style="danger")]])
    await send_photo(update, "main", text, keyboard, edit=True)

async def block_user(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён")
        return
    if not context.args:
        await update.message.reply_text("Usage: /block <user_id>" if get_user_lang(user_id) == "en" else "Использование: /block <user_id>")
        return
    try:
        target_id = int(context.args[0])
        with get_db_connection() as conn:
            conn.execute("INSERT OR REPLACE INTO blacklist (user_id, reason, blocked_at) VALUES (?, ?, ?)", (target_id, "Blocked by admin", get_moscow_time().isoformat()))
            conn.commit()
        blacklist.add(target_id)
        await update.message.reply_text(f"User {target_id} blocked" if get_user_lang(user_id) == "en" else f"Пользователь {target_id} заблокирован")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}" if get_user_lang(user_id) == "en" else f"Ошибка: {e}")

async def unblock_user(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён")
        return
    if not context.args:
        await update.message.reply_text("Usage: /unblock <user_id>" if get_user_lang(user_id) == "en" else "Использование: /unblock <user_id>")
        return
    try:
        target_id = int(context.args[0])
        with get_db_connection() as conn:
            conn.execute("DELETE FROM blacklist WHERE user_id = ?", (target_id,))
            conn.commit()
        blacklist.discard(target_id)
        await update.message.reply_text(f"User {target_id} unblocked" if get_user_lang(user_id) == "en" else f"Пользователь {target_id} разблокирован")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}" if get_user_lang(user_id) == "en" else f"Ошибка: {e}")

async def toggle_maintenance(update, context):
    global maintenance_mode
    user_id = update.effective_user.id
    if not is_admin(user_id):
        if update.callback_query:
            await update.callback_query.answer("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён", show_alert=True)
        return
    maintenance_mode = not maintenance_mode
    if maintenance_mode:
        if update.callback_query:
            await update.callback_query.answer("Maintenance ON" if get_user_lang(user_id) == "en" else "Тех.перерыв ВКЛ", show_alert=True)
        await send_maintenance_notification(context.bot, True, "Updating" if get_user_lang(user_id) == "en" else "Проводится обновление")
    else:
        if update.callback_query:
            await update.callback_query.answer("Maintenance OFF" if get_user_lang(user_id) == "en" else "Тех.перерыв ВЫКЛ", show_alert=True)
        await send_maintenance_notification(context.bot, False, "Complete" if get_user_lang(user_id) == "en" else "Работы завершены")
    await admin_command(update, context)

async def admin_tickets_handler(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        if update.callback_query:
            await update.callback_query.answer("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён", show_alert=True)
        return
    lang = get_user_lang(user_id)
    lang_data = LANGUAGES.get(lang, LANGUAGES["ru"])
    tickets = await asyncio.to_thread(get_tickets)
    if not tickets:
        text = f"<b>{lang_data['admin_tickets']}</b>\n\n{lang_data['no_tickets']}"
        keyboard = InlineKeyboardMarkup([[premium_button(lang_data['back'], "back", callback_data="back_to_admin", style="danger")]])
        await send_photo(update, "main", text, keyboard, edit=True)
        return
    text = f"<b>{lang_data['admin_tickets']}</b> ({len(tickets)})"
    keyboard_rows = []
    for t in tickets[:20]:
        ticket_id = t["id"]
        uid = t["user_id"]
        name = t["user_name"] or str(uid)
        username = t["username"] or ""
        label = f"#{ticket_id} {escape(name)}"
        if username:
            label += f" @{escape(username)}"
        keyboard_rows.append([premium_button(label, "stats", callback_data=f"ticket_view_{ticket_id}", style="primary")])
    keyboard_rows.append([premium_button(lang_data['back'], "back", callback_data="back_to_admin", style="danger")])
    keyboard = InlineKeyboardMarkup(keyboard_rows)
    await send_photo(update, "main", text, keyboard, edit=True)

async def ticket_view_handler(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.callback_query.answer("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён", show_alert=True)
        return
    data = update.callback_query.data
    ticket_id = int(data.split("_")[-1])
    lang = get_user_lang(user_id)
    lang_data = LANGUAGES.get(lang, LANGUAGES["ru"])
    ticket = await asyncio.to_thread(get_ticket, ticket_id)
    if not ticket:
        await update.callback_query.answer("Ticket not found" if lang == "en" else "Заявка не найдена", show_alert=True)
        return
    uid = ticket["user_id"]
    name = ticket["user_name"] or str(uid)
    username = ticket["username"] or ""
    created_fmt = get_moscow_time().strftime('%d.%m.%Y %H:%M')
    try:
        created_dt = datetime.fromisoformat(ticket["created_at"])
        created_fmt = created_dt.strftime('%d.%m.%Y %H:%M')
    except Exception:
        pass
    status_key = f"ticket_status_{ticket['status']}"
    status_label = lang_data.get(status_key, ticket['status'])
    user_info = lang_data['ticket_user_info'].format(
        name=escape(name), user_id=uid,
        username=f"@{escape(username)}" if username else "—",
        status=status_label, created_at=created_fmt
    )
    text = f"<b>Ticket #{ticket_id}</b>\n━━━━━━━━━━━━━━━━\n\n{user_info}\n━━━━━━━━━━━━━━━━"
    keyboard_rows = []
    if ticket["status"] == "pending":
        keyboard_rows.append([
            premium_button(lang_data['ticket_approve'], "status", callback_data=f"ticket_approve_{ticket_id}", style="success"),
            premium_button(lang_data['ticket_reject'], "cross", callback_data=f"ticket_reject_{ticket_id}", style="danger")
        ])
    keyboard_rows.append([premium_button(lang_data['back'], "back", callback_data="admin_tickets", style="danger")])
    keyboard = InlineKeyboardMarkup(keyboard_rows)
    try:
        await update.callback_query.message.delete()
    except Exception:
        pass
    receipt_file_id = ticket.get("receipt_file_id")
    receipt_type = ticket.get("receipt_type")
    if receipt_file_id and receipt_type == "photo":
        await context.bot.send_photo(chat_id=user_id, photo=receipt_file_id, caption=text, reply_markup=keyboard, parse_mode="HTML")
    elif receipt_file_id and receipt_type == "document":
        await context.bot.send_document(chat_id=user_id, document=receipt_file_id, caption=text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await context.bot.send_message(chat_id=user_id, text=text, reply_markup=keyboard, parse_mode="HTML")

async def ticket_approve_handler(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.callback_query.answer("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён", show_alert=True)
        return
    data = update.callback_query.data
    ticket_id = int(data.split("_")[-1])
    lang = get_user_lang(user_id)
    lang_data = LANGUAGES.get(lang, LANGUAGES["ru"])
    ticket = await asyncio.to_thread(get_ticket, ticket_id)
    if not ticket:
        await update.callback_query.answer("Ticket not found" if lang == "en" else "Заявка не найдена", show_alert=True)
        return
    if ticket["status"] != "pending":
        await update.callback_query.answer("Ticket already processed" if lang == "en" else "Заявка уже обработана", show_alert=True)
        return
    await asyncio.to_thread(update_ticket_status, ticket_id, "approved")
    uid = ticket["user_id"]
    user_lang = get_user_lang(uid)
    user_lang_data = LANGUAGES.get(user_lang, LANGUAGES["ru"])
    notify_text = user_lang_data['ticket_notify_approved'].format(ticket_id=ticket_id)
    notify_keyboard = InlineKeyboardMarkup([[premium_button("Подключиться" if user_lang == "ru" else "Connect", "connect", callback_data="show_connection_types", style="success")]])
    receipt_file_id = ticket.get("receipt_file_id")
    receipt_type = ticket.get("receipt_type")
    try:
        if receipt_file_id and receipt_type == "photo":
            await context.bot.send_photo(chat_id=uid, photo=receipt_file_id, caption=notify_text, reply_markup=notify_keyboard, parse_mode="HTML")
        elif receipt_file_id and receipt_type == "document":
            await context.bot.send_document(chat_id=uid, document=receipt_file_id, caption=notify_text, reply_markup=notify_keyboard, parse_mode="HTML")
        else:
            await context.bot.send_message(chat_id=uid, text=notify_text, reply_markup=notify_keyboard, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Failed to notify user {uid}: {e}")
    await update.callback_query.answer("Ticket approved" if lang == "en" else "Заявка одобрена", show_alert=True)
    await ticket_view_handler(update, context)

async def ticket_reject_handler(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.callback_query.answer("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён", show_alert=True)
        return
    data = update.callback_query.data
    ticket_id = int(data.split("_")[-1])
    lang = get_user_lang(user_id)
    lang_data = LANGUAGES.get(lang, LANGUAGES["ru"])
    ticket = await asyncio.to_thread(get_ticket, ticket_id)
    if not ticket:
        await update.callback_query.answer("Ticket not found" if lang == "en" else "Заявка не найдена", show_alert=True)
        return
    if ticket["status"] != "pending":
        await update.callback_query.answer("Ticket already processed" if lang == "en" else "Заявка уже обработана", show_alert=True)
        return
    await asyncio.to_thread(update_ticket_status, ticket_id, "rejected")
    uid = ticket["user_id"]
    user_lang = get_user_lang(uid)
    user_lang_data = LANGUAGES.get(user_lang, LANGUAGES["ru"])
    notify_text = user_lang_data['ticket_notify_rejected'].format(ticket_id=ticket_id)
    try:
        await context.bot.send_message(chat_id=uid, text=notify_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Failed to notify user {uid}: {e}")
    await update.callback_query.answer("Ticket rejected" if lang == "en" else "Заявка отклонена", show_alert=True)
    await ticket_view_handler(update, context)

async def toggle_black_list_source(update, context):
    global BLACK_LIST_SOURCE
    user_id = update.effective_user.id
    if not is_admin(user_id):
        if update.callback_query:
            await update.callback_query.answer("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён", show_alert=True)
        return
    if BLACK_LIST_SOURCE == "all":
        BLACK_LIST_SOURCE = "my_lk"
        await update.callback_query.answer("Switched to MY LK (100% working)" if get_user_lang(user_id) == "en" else "Переключено на MY LK (100% рабочие)", show_alert=True)
    else:
        BLACK_LIST_SOURCE = "all"
        await update.callback_query.answer("Switched to ALL (with check)" if get_user_lang(user_id) == "en" else "Переключено на ALL (все с проверкой)", show_alert=True)
    await asyncio.to_thread(save_status_to_db)
    await send_photo(update, "main", "Updating Black List..." if get_user_lang(user_id) == "en" else "Обновление Black List...", None, edit=True)
    await update_vless_status()
    await fetch_and_save_black()
    now = get_moscow_time()
    STATUS['vless_last'] = now
    STATUS['vless_next'] = now + timedelta(hours=1)
    await asyncio.to_thread(save_status_to_db)
    await admin_command(update, context)

async def send_maintenance_notification(bot, start, text=""):
    users = await asyncio.to_thread(get_all_users)
    if not users:
        return
    async with BROADCAST_SEMAPHORE:
        for user_id in users:
            if user_id in blacklist:
                continue
            lang = get_user_lang(user_id)
            if start:
                message = f"Maintenance mode\n\n{text}\n\nWe'll be back soon!" if lang == "en" else f"Технический перерыв\n\n{text}\n\nСкоро всё заработает!"
            else:
                message = f"Service working\n\n{text}\n\nEnjoy!" if lang == "en" else f"Сервис работает\n\n{text}\n\nПриятного использования!"
            keyboard = InlineKeyboardMarkup([[premium_button("Open bot" if lang == "en" else "Открыть бота", "connect", url=f"https://t.me/{BOT_USERNAME}", style="success")]])
            try:
                await safe_send_message(bot, user_id, message, reply_markup=keyboard)
                await asyncio.sleep(0.05)
            except Exception:
                pass

async def start_news_creation(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        if update.callback_query:
            await update.callback_query.answer("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён", show_alert=True)
        else:
            await update.message.reply_text("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён")
        return ConversationHandler.END
    lang = get_user_lang(user_id)
    context.user_data['news_step'] = 'title'
    context.user_data['news_data'] = {}
    if lang == "en":
        text = "Create news (Step 1/3)\n\nEnter NEWS TITLE:\n\nExample: \"Server Update!\" or \"Important Announcement\"\n\nSend a text message with the title."
        keyboard = InlineKeyboardMarkup([[premium_button("Cancel", "cancel", callback_data="cancel_news", style="danger")]])
    else:
        text = "Создание новости (Шаг 1/3)\n\nВведите ЗАГОЛОВОК новости:\n\nПример: \"Обновление серверов!\" или \"Важное объявление\"\n\nОтправьте текстовое сообщение с заголовком."
        keyboard = InlineKeyboardMarkup([[premium_button("Отмена", "cancel", callback_data="cancel_news", style="danger")]])
    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Error editing news start: {e}")
            await update.callback_query.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)
    return NEWS_TITLE

async def news_get_title(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    title = update.message.text.strip()
    if not title:
        await update.message.reply_text("Title cannot be empty. Enter title:" if lang == "en" else "Заголовок не может быть пустым. Введите заголовок:")
        return NEWS_TITLE
    context.user_data['news_data']['title'] = title
    context.user_data['news_step'] = 'text'
    safe_title = escape(title)
    if lang == "en":
        text = f"Create news (Step 2/3)\n\nTitle: <b>{safe_title}</b>\n\nEnter MAIN TEXT of the news:\n\nHTML markup supported:\n• <b>bold</b>\n• <i>italic</i>\n• <a href=\"link\">text</a>\n\nSend a text message with the news text."
        keyboard = InlineKeyboardMarkup([[premium_button("Back to title", "back_title", callback_data="news_back_title", style="primary")], [premium_button("Cancel", "cancel", callback_data="cancel_news", style="danger")]])
    else:
        text = f"Создание новости (Шаг 2/3)\n\nЗаголовок: <b>{safe_title}</b>\n\nВведите ОСНОВНОЙ ТЕКСТ новости:\n\nПоддерживается HTML разметка:\n• <b>жирный</b>\n• <i>курсив</i>\n• <a href=\"ссылка\">текст</a>\n\nОтправьте текстовое сообщение с текстом новости."
        keyboard = InlineKeyboardMarkup([[premium_button("Назад к заголовку", "back_title", callback_data="news_back_title", style="primary")], [premium_button("Отмена", "cancel", callback_data="cancel_news", style="danger")]])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)
    return NEWS_TEXT

async def news_get_text(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    text_content = update.message.text.strip()
    if not text_content:
        await update.message.reply_text("Text cannot be empty. Enter text:" if lang == "en" else "Текст не может быть пустым. Введите текст:")
        return NEWS_TEXT
    context.user_data['news_data']['text'] = text_content
    context.user_data['news_step'] = 'image'
    safe_title = safe_html(context.user_data['news_data']['title'])
    safe_text = safe_html(text_content)
    if lang == "en":
        preview = f"News Preview\n\n<b>{safe_title}</b>\n\n{safe_text}\n\n---\nStep 3/3: Attach image\nSend PHOTO (optional) or press button."
        keyboard = InlineKeyboardMarkup([[premium_button("Publish with photo", "photo", callback_data="news_send_with_image", style="success")], [premium_button("Publish without photo", "skip", callback_data="news_send_without_image", style="primary")], [premium_button("Back to text", "back_text", callback_data="news_back_text", style="primary")], [premium_button("Cancel", "cancel", callback_data="cancel_news", style="danger")]])
    else:
        preview = f"Предпросмотр новости\n\n<b>{safe_title}</b>\n\n{safe_text}\n\n---\nШаг 3/3: Прикрепить изображение\nОтправьте ФОТО (опционально) или нажмите на кнопку."
        keyboard = InlineKeyboardMarkup([[premium_button("Опубликовать с фото", "photo", callback_data="news_send_with_image", style="success")], [premium_button("Опубликовать без фото", "skip", callback_data="news_send_without_image", style="primary")], [premium_button("Назад к тексту", "back_text", callback_data="news_back_text", style="primary")], [premium_button("Отмена", "cancel", callback_data="cancel_news", style="danger")]])
    await update.message.reply_text(preview, parse_mode="HTML", reply_markup=keyboard)
    return NEWS_IMAGE

async def news_get_image(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    if not update.message.photo:
        await update.message.reply_text("Please send a photo or press button to publish without photo." if lang == "en" else "Пожалуйста, отправьте фото или нажмите кнопку для публикации без фото.")
        return NEWS_IMAGE
    photo = update.message.photo[-1]
    context.user_data['news_data']['image'] = photo.file_id
    safe_title = safe_html(context.user_data['news_data']['title'])
    safe_text = safe_html(context.user_data['news_data']['text'])
    if lang == "en":
        preview = f"News Preview with Image\n\n<b>{safe_title}</b>\n\n{safe_text}\n\n---\nReady! Press \"Send\" or \"Cancel\"."
        keyboard = InlineKeyboardMarkup([[premium_button("Send News", "send", callback_data="news_send_final", style="success")], [premium_button("Cancel", "cancel", callback_data="cancel_news", style="danger")]])
    else:
        preview = f"Предпросмотр новости с изображением\n\n<b>{safe_title}</b>\n\n{safe_text}\n\n---\nГотово! Нажмите \"Отправить\" или \"Отмена\"."
        keyboard = InlineKeyboardMarkup([[premium_button("Отправить новость", "send", callback_data="news_send_final", style="success")], [premium_button("Отмена", "cancel", callback_data="cancel_news", style="danger")]])
    await update.message.reply_photo(photo=photo.file_id, caption=preview, parse_mode="HTML", reply_markup=keyboard)
    return NEWS_IMAGE

async def cancel_news(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    context.user_data.pop('news_step', None)
    context.user_data.pop('news_data', None)
    await update.callback_query.message.edit_text("News creation cancelled" if lang == "en" else "Создание новости отменено", reply_markup=InlineKeyboardMarkup([[premium_button("Main Menu" if lang == "en" else "Главное меню", "back", callback_data="back_to_admin", style="danger")]]))
    return ConversationHandler.END

async def news_back_title(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.callback_query.answer("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён", show_alert=True)
        return
    lang = get_user_lang(user_id)
    context.user_data['news_step'] = 'title'
    if lang == "en":
        text = f"Create news (Step 1/3)\n\nEnter NEWS TITLE:\n\nCurrent title:\n<b>{safe_html(context.user_data.get('news_data', {}).get('title', 'not set'))}</b>\n\nSend a text message with the new title."
        keyboard = InlineKeyboardMarkup([[premium_button("Cancel", "cancel", callback_data="cancel_news", style="danger")]])
    else:
        text = f"Создание новости (Шаг 1/3)\n\nВведите ЗАГОЛОВОК новости:\n\nТекущий заголовок:\n<b>{safe_html(context.user_data.get('news_data', {}).get('title', 'не задан'))}</b>\n\nОтправьте текстовое сообщение с новым заголовком."
        keyboard = InlineKeyboardMarkup([[premium_button("Отмена", "cancel", callback_data="cancel_news", style="danger")]])
    await update.callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    return NEWS_TITLE

async def news_back_text(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.callback_query.answer("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён", show_alert=True)
        return
    lang = get_user_lang(user_id)
    context.user_data['news_step'] = 'text'
    if lang == "en":
        text = f"Create news (Step 2/3)\n\nTitle: <b>{safe_html(context.user_data['news_data'].get('title', ''))}</b>\n\nEnter MAIN TEXT of the news:\n\nHTML markup supported.\n\nSend a text message with the news text."
        keyboard = InlineKeyboardMarkup([[premium_button("Back to title", "back_title", callback_data="news_back_title", style="primary")], [premium_button("Cancel", "cancel", callback_data="cancel_news", style="danger")]])
    else:
        text = f"Создание новости (Шаг 2/3)\n\nЗаголовок: <b>{safe_html(context.user_data['news_data'].get('title', ''))}</b>\n\nВведите ОСНОВНОЙ ТЕКСТ новости:\n\nПоддерживается HTML разметка.\n\nОтправьте текстовое сообщение с текстом новости."
        keyboard = InlineKeyboardMarkup([[premium_button("Назад к заголовку", "back_title", callback_data="news_back_title", style="primary")], [premium_button("Отмена", "cancel", callback_data="cancel_news", style="danger")]])
    await update.callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    return NEWS_TEXT

async def news_send_with_image(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.callback_query.answer("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён", show_alert=True)
        return
    lang = get_user_lang(user_id)
    if lang == "en":
        text = f"Step 3/3: Send image\n\nTitle: <b>{safe_html(context.user_data['news_data']['title'])}</b>\n\nSend PHOTO for the news.\n\nYou can also press the button to skip this step."
        keyboard = InlineKeyboardMarkup([[premium_button("Skip photo", "skip", callback_data="news_send_without_image", style="primary")], [premium_button("Back", "back_text", callback_data="news_back_text", style="primary")], [premium_button("Cancel", "cancel", callback_data="cancel_news", style="danger")]])
    else:
        text = f"Шаг 3/3: Отправьте изображение\n\nЗаголовок: <b>{safe_html(context.user_data['news_data']['title'])}</b>\n\nОтправьте ФОТО для новости.\n\nВы также можете нажать кнопку, чтобы пропустить этот шаг."
        keyboard = InlineKeyboardMarkup([[premium_button("Пропустить фото", "skip", callback_data="news_send_without_image", style="primary")], [premium_button("Назад", "back_text", callback_data="news_back_text", style="primary")], [premium_button("Отмена", "cancel", callback_data="cancel_news", style="danger")]])
    await update.callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)

async def news_send_without_image(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.callback_query.answer("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён", show_alert=True)
        return
    lang = get_user_lang(user_id)
    data = context.user_data.get('news_data', {})
    title = data.get('title', 'News' if lang == "en" else "Новость")
    text_content = data.get('text', '')
    if not text_content:
        await update.callback_query.message.edit_text("Error: news text not found" if lang == "en" else "Ошибка: текст новости не найден")
        return
    if lang == "en":
        preview = f"News Preview (without photo)\n\n<b>{safe_html(title)}</b>\n\n{safe_html(text_content)}\n\n---\nReady to send! Press \"Send\"."
        keyboard = InlineKeyboardMarkup([[premium_button("Send News", "send", callback_data="news_send_final", style="success")], [premium_button("Add photo", "photo", callback_data="news_send_with_image", style="primary")], [premium_button("Cancel", "cancel", callback_data="cancel_news", style="danger")]])
    else:
        preview = f"Предпросмотр новости (без фото)\n\n<b>{safe_html(title)}</b>\n\n{safe_html(text_content)}\n\n---\nГотово к отправке! Нажмите \"Отправить\"."
        keyboard = InlineKeyboardMarkup([[premium_button("Отправить новость", "send", callback_data="news_send_final", style="success")], [premium_button("Добавить фото", "photo", callback_data="news_send_with_image", style="primary")], [premium_button("Отмена", "cancel", callback_data="cancel_news", style="danger")]])
    await update.callback_query.message.edit_text(preview, parse_mode="HTML", reply_markup=keyboard)

async def news_send_final(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.callback_query.answer("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён", show_alert=True)
        return ConversationHandler.END
    lang = get_user_lang(user_id)
    data = context.user_data.get('news_data', {})
    title = data.get('title', 'News' if lang == "en" else "Новость")
    text_content = data.get('text', '')
    image = data.get('image', None)
    if not text_content:
        await update.callback_query.message.edit_text("Error: news text not found" if lang == "en" else "Ошибка: текст новости не найден")
        return ConversationHandler.END
    await update.callback_query.message.edit_text("Sending news to users..." if lang == "en" else "Отправка новости пользователям...")
    try:
        sent_count = await send_news_to_all(context.bot, title, text_content, image)
        if lang == "en":
            result_text = f"News sent!\n\n<b>{safe_html(title)}</b>\n\n{safe_html(text_content)}\n\nSent: {sent_count} users"
        else:
            result_text = f"Новость отправлена!\n\n<b>{safe_html(title)}</b>\n\n{safe_html(text_content)}\n\nОтправлено: {sent_count} пользователей"
        keyboard = InlineKeyboardMarkup([[premium_button("Main Menu" if lang == "en" else "Главное меню", "back", callback_data="back_to_admin", style="danger")]])
        await update.callback_query.message.edit_text(result_text, parse_mode="HTML", reply_markup=keyboard)
    except Exception as e:
        logger.error(f"News send error: {e}")
        await update.callback_query.message.edit_text(f"News send error: {e}" if lang == "en" else f"Ошибка отправки новости: {e}", reply_markup=InlineKeyboardMarkup([[premium_button("Main Menu" if lang == "en" else "Главное меню", "back", callback_data="back_to_admin", style="danger")]]))
    context.user_data.pop('news_step', None)
    context.user_data.pop('news_data', None)
    return ConversationHandler.END

async def send_news_to_all(bot, title, text_content, image_file_id=None):
    users = await asyncio.to_thread(get_all_users)
    if not users:
        logger.warning("No users found to send news")
        return 0
    message = f"<b>{title}</b>\n\n{text_content}"
    sent = 0
    async with BROADCAST_SEMAPHORE:
        for user_id in users:
            if user_id in blacklist:
                continue
            lang = get_user_lang(user_id)
            keyboard = InlineKeyboardMarkup([[premium_button("Open bot" if lang == "en" else "Открыть бота", "connect", url=f"https://t.me/{BOT_USERNAME}", style="success")], [premium_button("Channel" if lang == "en" else "Канал", "channel", url=CHANNEL_URL, style="primary")]])
            try:
                if image_file_id:
                    if await safe_send_photo(bot, user_id, image_file_id, message, reply_markup=keyboard):
                        sent += 1
                else:
                    if await safe_send_message(bot, user_id, message, reply_markup=keyboard):
                        sent += 1
                if sent % 10 == 0:
                    logger.info(f"News sent to {sent} users")
                await asyncio.sleep(0.05)
            except Exception as e:
                logger.warning(f"Failed to send news to {user_id}: {e}")
    logger.info(f"News sent to {sent} users successfully")
    return sent

async def handle_callback(update, context):
    query = update.callback_query
    await query.answer()
    if not query.message:
        return
    data = query.data
    user_id = update.effective_user.id
    user_name = escape(update.effective_user.username or update.effective_user.first_name or "Guest")
    logger.info(f"Callback: {data} from user {user_id}")
    await asyncio.to_thread(save_user_interaction, user_id)
    if data == "check_sub":
        ok, subscribed = await is_subscribed_cached(context.bot, user_id)
        if not ok:
            lang = get_user_lang(user_id)
            await query.answer("Check error" if lang == "en" else "Ошибка проверки", show_alert=True)
            return
        if subscribed:
            subscription_cache[user_id] = {"status": True, "time": time.time()}
            try:
                await query.message.delete()
            except Exception as e:
                logger.error(f"Delete message error: {e}")
            if await asyncio.to_thread(user_has_accepted, user_id):
                lang = get_user_lang(user_id)
                await send_photo(update, "main", get_menu_text(user_name, lang), get_main_keyboard(lang), edit=False)
            else:
                await show_agreement(update, context, user_name, user_id)
        else:
            lang = get_user_lang(user_id)
            await query.answer("Subscription not found" if lang == "en" else "Подписка не найдена", show_alert=True)
        return
    if data == "maintenance_info":
        lang = get_user_lang(user_id)
        await query.answer("Maintenance. Back soon!" if lang == "en" else "Тех.перерыв. Скоро заработает!", show_alert=True)
        return
    if data == "check_servers":
        if not await require_subscription(update, context):
            return
        await check_servers_now(update, context)
        return
    if data == "admin_news":
        if is_admin(user_id):
            await start_news_creation(update, context)
        return
    if data == "admin_blacklist":
        if is_admin(user_id):
            await admin_blacklist(update, context)
        return
    if data == "cancel_news":
        if not is_admin(user_id):
            await query.answer("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён", show_alert=True)
            return
        await cancel_news(update, context)
        return
    if data == "news_send_final":
        if not is_admin(user_id):
            await query.answer("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён", show_alert=True)
            return
        if not context.user_data.get('news_data', {}).get('text'):
            await query.answer("Error: news data lost" if get_user_lang(user_id) == "en" else "Ошибка: данные новости потеряны", show_alert=True)
            return
        await news_send_final(update, context)
        return
    if data == "news_send_with_image":
        if not is_admin(user_id):
            await query.answer("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён", show_alert=True)
            return
        if not context.user_data.get('news_data', {}).get('title'):
            await query.answer("Error: news data lost" if get_user_lang(user_id) == "en" else "Ошибка: данные новости потеряны", show_alert=True)
            return
        await news_send_with_image(update, context)
        return
    if data == "news_send_without_image":
        if not is_admin(user_id):
            await query.answer("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён", show_alert=True)
            return
        if not context.user_data.get('news_data', {}).get('text'):
            await query.answer("Error: news data lost" if get_user_lang(user_id) == "en" else "Ошибка: данные новости потеряны", show_alert=True)
            return
        await news_send_without_image(update, context)
        return
    if data == "news_back_title":
        if not is_admin(user_id):
            await query.answer("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён", show_alert=True)
            return
        await news_back_title(update, context)
        return
    if data == "news_back_text":
        if not is_admin(user_id):
            await query.answer("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён", show_alert=True)
            return
        await news_back_text(update, context)
        return
    if data == "select_lang":
        await select_language(update, context)
        return
    if data in ("set_lang_ru", "set_lang_en"):
        await set_language(update, context)
        return
    if not await require_subscription(update, context):
        return
    if data == "show_connection_types":
        await show_connection_types(update, context)
        return
    if data == "back_to_connection_types":
        await show_connection_types(update, context)
        return
    if data == "show_premium_sub":
        await show_premium_subscription(update, context)
        return
    if data == "show_free_sub":
        await show_free_subscription(update, context)
        return
    if data == "create_ticket":
        lang = get_user_lang(user_id)
        await query.answer("Please send a receipt screenshot first" if lang == "en" else "Сначала отправьте скриншот чека", show_alert=True)
        return
    if data == "show_status":
        await show_status(update, context)
        return
    if data == "show_donate":
        await show_donate(update, context)
        return
    if data == "donate_snooze":
        await asyncio.to_thread(save_donate_reminder, user_id)
        lang = get_user_lang(user_id)
        await query.answer("Hidden for 24h" if lang == "en" else "Скрыто на 24 часа", show_alert=True)
        try:
            await query.message.delete()
        except Exception:
            pass
        return
    if data.startswith("accept_"):
        try:
            target_user_id = int(data.split("_")[1])
        except (ValueError, IndexError):
            return
        if user_id == target_user_id:
            ok, subscribed = await is_subscribed_cached(context.bot, user_id)
            if not ok:
                lang = get_user_lang(user_id)
                await query.answer("Check error" if lang == "en" else "Ошибка проверки", show_alert=True)
                return
            if not subscribed:
                lang = get_user_lang(user_id)
                await query.answer("Subscription not found" if lang == "en" else "Подписка не найдена", show_alert=True)
                return
            await asyncio.to_thread(save_user_accept, user_id, user_name)
            try:
                await query.message.delete()
            except Exception:
                pass
            lang = get_user_lang(user_id)
            await send_photo(update, "main", get_menu_text(user_name, lang), get_main_keyboard(lang), edit=False)
        return
    if data == "decline_agreement":
        lang = get_user_lang(user_id)
        if lang == "en":
            await send_photo(update, "main", "Access denied\n\n/start to retry", get_back_keyboard(lang), edit=True)
        else:
            await send_photo(update, "main", "Доступ запрещён\n\n/start для повтора", get_back_keyboard(lang), edit=True)
        return
    if data == "back_to_menu":
        await show_menu(update, context)
        return
    if data == "back_to_admin":
        await admin_command(update, context)
        return
    if data == "admin_stats":
        if is_admin(user_id):
            await admin_stats(update, context)
        return
    if data == "admin_maintenance_toggle":
        if is_admin(user_id):
            await toggle_maintenance(update, context)
        return
    if data == "admin_toggle_black":
        if is_admin(user_id):
            await toggle_black_list_source(update, context)
        return
    if data == "admin_tickets":
        if is_admin(user_id):
            await admin_tickets_handler(update, context)
        return
    if data.startswith("ticket_view_"):
        if is_admin(user_id):
            await ticket_view_handler(update, context)
        return
    if data.startswith("ticket_approve_"):
        if is_admin(user_id):
            await ticket_approve_handler(update, context)
        return
    if data.startswith("ticket_reject_"):
        if is_admin(user_id):
            await ticket_reject_handler(update, context)
        return
    if data == "admin_update":
        if is_admin(user_id):
            lang = get_user_lang(user_id)
            await send_photo(update, "main", "Обновление..." if lang == "en" else "Обновление...", None, edit=True)
            black_ok, white_ok = await update_all_simple()
            if black_ok and white_ok:
                await send_photo(update, "main", "Обновлено" if lang == "en" else "Обновлено", get_admin_keyboard(lang), edit=True)
            elif black_ok:
                await send_photo(update, "main", "Black List обновлён" if lang == "en" else "Black List обновлён", get_admin_keyboard(lang), edit=True)
            elif white_ok:
                await send_photo(update, "main", "White List обновлён" if lang == "en" else "White List обновлён", get_admin_keyboard(lang), edit=True)
            else:
                await send_photo(update, "main", "Ошибка обновления" if lang == "en" else "Ошибка обновления", get_admin_keyboard(lang), edit=True)
        return
    if data == "admin_update_proxies":
        if is_admin(user_id):
            lang = get_user_lang(user_id)
            await send_photo(update, "main", "Updating proxies..." if lang == "en" else "Обновление прокси...", None, edit=True)
            ok, added = await update_proxies_with_timeout()
            if ok:
                await send_photo(update, "main", f"Proxies updated\nAdded: {added}" if lang == "en" else f"Прокси обновлены\nДобавлено: {added}", get_admin_keyboard(lang), edit=True)
            else:
                await send_photo(update, "main", "Update error" if lang == "en" else "Ошибка обновления", get_admin_keyboard(lang), edit=True)
        return
    if data == "show_proxies_info":
        await show_proxies_info(update, context)
        return
    if data == "show_proxies_list":
        await send_proxy_list(update, context, 0)
        return
    if data == "show_docs":
        await show_docs(update, context)
        return
    if data == "show_instruction":
        await show_instruction(update, context)
        return
    if data == "show_tips":
        await show_tips(update, context)
        return
    if data == "show_faq":
        await show_faq(update, context)
        return
    if data.startswith("proxy_page_"):
        parts = data.split("_")
        if len(parts) == 3:
            try:
                await send_proxy_list(update, context, int(parts[2]))
            except ValueError:
                pass
        return

async def background_updater():
    global is_background_updating, donate_reminder_last, bot_instance
    if is_background_updating:
        return
    is_background_updating = True
    try:
        await asyncio.sleep(10)
        logger.info("Starting background updates...")
        try:
            if not maintenance_mode:
                ok, _ = await update_proxies_with_timeout()
                if not ok:
                    logger.warning("Initial proxies update failed")
                await update_all_simple()
        except Exception as e:
            logger.error(f"Initial background update error: {e}")
        donate_reminder_last = get_moscow_time()
        last_server_check = get_moscow_time()
        last_session_refresh = get_moscow_time()
        last_cleanup = get_moscow_time()
        last_wal_checkpoint = get_moscow_time()
        while True:
            try:
                now = get_moscow_time()
                if (now - last_session_refresh).total_seconds() >= 1800:
                    await close_session()
                    last_session_refresh = now
                    gc.collect()
                    logger.info("Session refreshed, memory cleaned")
                if (now - last_cleanup).total_seconds() >= 3600:
                    await asyncio.to_thread(cleanup_inactive_data)
                    last_cleanup = now
                if (now - last_wal_checkpoint).total_seconds() >= 7200:
                    try:
                        with get_db_connection() as conn:
                            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                        last_wal_checkpoint = now
                        logger.info("WAL checkpoint completed")
                    except Exception as e:
                        logger.error(f"WAL checkpoint error: {e}")
                if not maintenance_mode:
                    if (now - last_server_check).total_seconds() >= VLESS_CHECK_INTERVAL:
                        logger.info("Running scheduled server check...")
                        prev_working = STATUS.get('vless_working', 0)
                        await update_vless_status()
                        curr_working = STATUS.get('vless_working', 0)
                        if prev_working == 0 and curr_working > 0 and bot_instance:
                            await send_recovery_notification(bot_instance, prev_working, curr_working)
                        last_server_check = now
                    vless_next = STATUS.get('vless_next')
                    if vless_next and now >= vless_next:
                        logger.info("Auto-updating VPN...")
                        await update_all_simple()
                    proxies_next = STATUS.get('proxies_next')
                    if proxies_next and now >= proxies_next:
                        logger.info("Auto-updating proxies...")
                        await update_proxies_with_timeout()
                    if donate_reminder_last and (now - donate_reminder_last).total_seconds() >= DONATE_REMINDER_INTERVAL:
                        logger.info("Sending donate reminder...")
                        if bot_instance:
                            await send_donate_reminder(bot_instance)
                        donate_reminder_last = now
                await asyncio.sleep(BACKGROUND_INTERVAL)
            except asyncio.CancelledError:
                logger.info("Background updater stopped")
                break
            except Exception as e:
                logger.error(f"Background error: {e}")
                await asyncio.sleep(BACKGROUND_INTERVAL)
    finally:
        is_background_updating = False

async def post_init(app):
    global background_task, bot_instance
    bot_instance = app.bot
    await asyncio.to_thread(load_blacklist)
    await asyncio.to_thread(load_user_langs)
    if background_task is None or background_task.done():
        background_task = asyncio.create_task(background_updater())

async def post_shutdown(app):
    global background_task
    if background_task and not background_task.done():
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            pass
    await close_session()

async def admin_broadcast(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("Access denied" if get_user_lang(user_id) == "en" else "Доступ запрещён")
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <text>" if get_user_lang(user_id) == "en" else "Использование: /broadcast <текст>")
        return
    text = " ".join(context.args)
    users = await asyncio.to_thread(get_all_users)
    if not users:
        await update.message.reply_text("No users" if get_user_lang(user_id) == "en" else "Нет пользователей")
        return
    sent = 0
    async with BROADCAST_SEMAPHORE:
        for uid in users:
            if uid in blacklist:
                continue
            try:
                if await safe_send_message(context.bot, uid, text):
                    sent += 1
                await asyncio.sleep(0.05)
            except Exception:
                pass
    await update.message.reply_text(f"Sent to {sent} users" if get_user_lang(user_id) == "en" else f"Отправлено {sent} пользователям")

async def help_command(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    if lang == "en":
        text = "<b>XolirX Bot</b>\n\n<b>Commands:</b>\n/start - Start bot\n/status - Server status\n/check - Check servers\n/ping - Latency\n/help - This message"
    else:
        text = "<b>XolirX Bot</b>\n\n<b>Команды:</b>\n/start - Запуск бота\n/status - Статус серверов\n/check - Проверка серверов\n/ping - Задержка\n/fact - Случайный факт\n/secret - Секретная команда\n/help - Эта справка"
    await update.message.reply_text(text, parse_mode="HTML")

def get_random_fact():
    return random.choice(VPN_FACTS)

def get_fact_text(lang="ru"):
    fact = get_random_fact()
    if lang == "en":
        return f"<b>Random Fact</b>\n\nDid you know?\n\n{fact}"
    return f"<b>  Факт дня</b>\n\nЗнаете ли вы?\n\n{fact}"

def get_secret_text(lang="ru"):
    cat = random.choice(SECRET_CATS)
    tip = random.choice(SECRET_TIPS)
    safe_cat = escape(cat)
    if lang == "en":
        return f"<b>Secret Command Activated!</b>\n\nYou found an easter egg. Here's a cat:\n\n<pre>{safe_cat}</pre>\n\nTip: {tip}\n\n(c) XolirX"
    return f"<b>  Секретная команда активирована!</b>\n\nТы нашёл пасхалку. Вот тебе котик:\n\n<pre>{safe_cat}</pre>\n\nСовет: {tip}\n\n(c) XolirX"

def get_status_bar(working, total):
    if total == 0:
        return "[----]"
    percent = working / total
    filled = int(percent * 4)
    empty = 4 - filled
    return "[" + "=" * filled + "-" * empty + "]"

def get_status_text(lang="ru"):
    vless_count = STATUS.get('vless_count', 0)
    vless_working = STATUS.get('vless_working', 0)
    proxies_count = STATUS.get('proxies_count', 0)
    vless_status = get_vpn_status()
    bar = get_status_bar(vless_working, vless_count)
    if vless_count > 0:
        working_percent = vless_working / vless_count * 100
        server_detail = f"{vless_working}/{vless_count} ({working_percent:.1f}%)"
    else:
        server_detail = "Нет данных" if lang == "ru" else "No data"
    if lang == "en":
        return (
            f"<b>System Status</b>\n\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"{bar} Protection: {vless_status}\n\n"
            f"Servers: {server_detail}\n"
            f"Proxy: {proxies_count}\n"
            f"Updated: {format_time(STATUS.get('vless_last'))}\n"
            f"Next: {format_time_until(STATUS.get('vless_next'))}\n"
            f"━━━━━━━━━━━━━━━━"
        )
    return (
        f"<b>Статус системы</b>\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"{bar} Защита: {vless_status}\n\n"
        f"Серверы: {server_detail}\n"
        f"Прокси: {proxies_count}\n"
        f"Обновлено: {format_time(STATUS.get('vless_last'))}\n"
        f"След.: {format_time_until(STATUS.get('vless_next'))}\n"
        f"━━━━━━━━━━━━━━━━"
    )

async def fact_command(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    text = get_fact_text(lang)
    keyboard = InlineKeyboardMarkup([[premium_button("Ещё факт" if lang == "ru" else "Another fact", "status", callback_data="random_fact", style="success")], [premium_button("Главное меню" if lang == "ru" else "Main Menu", "back", callback_data="back_to_menu", style="danger")]])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)

async def random_fact_callback(update, context):
    lang = get_user_lang(update.effective_user.id)
    text = get_fact_text(lang)
    keyboard = InlineKeyboardMarkup([[premium_button("Ещё факт" if lang == "ru" else "Another fact", "status", callback_data="random_fact", style="success")], [premium_button("Главное меню" if lang == "ru" else "Main Menu", "back", callback_data="back_to_menu", style="danger")]])
    try:
        await update.callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    except Exception:
        await update.callback_query.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)

async def secret_command(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    text = get_secret_text(lang)
    await update.message.reply_text(text, parse_mode="HTML")

def signal_handler(sig, frame):
    logger.info(f"Received signal {sig}, cleaning up...")
    try:
        if session and not session.closed:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(close_session())
            else:
                loop.run_until_complete(close_session())
    except Exception:
        pass
    try:
        with get_db_connection() as conn:
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    except Exception:
        pass
    sys.exit(0)

def load_images():
    for key, path in IMAGES.items():
        if os.path.exists(path):
            try:
                with open(path, 'rb') as f:
                    image_cache[key] = f.read()
                logger.info(f"Loaded image: {key}")
            except Exception as e:
                logger.error(f"Failed to load image {key}: {e}")
                image_cache[key] = None
        else:
            image_cache[key] = None
            logger.warning(f"Image not found: {path}")

def main():
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)
    if not TOKEN:
        logger.error("BOT_TOKEN env var not set")
        sys.exit(1)
    if not ADMIN_ID:
        logger.warning("ADMIN_ID env var not set, admin features disabled")
    if not GITHUB_TOKEN:
        logger.warning("GITHUB_TOKEN env var not set, GitHub upload disabled")
    if not os.path.exists("images"):
        os.makedirs("images", exist_ok=True)
        logger.warning("Images folder created, please add image files")
    
    init_db()
    
    load_images()
    load_status_from_db()
    global cached_proxies
    cached_proxies = load_proxies_from_db()
    app = Application.builder().token(TOKEN).post_init(post_init).post_shutdown(post_shutdown).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CommandHandler("block", block_user))
    app.add_handler(CommandHandler("unblock", unblock_user))
    app.add_handler(CommandHandler("broadcast", admin_broadcast))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("fact", fact_command))
    app.add_handler(CommandHandler("secret", secret_command))
    news_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_news_creation, pattern="^admin_news$")],
        states={NEWS_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, news_get_title)], NEWS_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, news_get_text)], NEWS_IMAGE: [MessageHandler(filters.PHOTO, news_get_image)]},
        fallbacks=[CallbackQueryHandler(cancel_news, pattern="^cancel_news$"), CallbackQueryHandler(news_back_title, pattern="^news_back_title$"), CallbackQueryHandler(news_back_text, pattern="^news_back_text$"), CallbackQueryHandler(news_send_with_image, pattern="^news_send_with_image$"), CallbackQueryHandler(news_send_without_image, pattern="^news_send_without_image$"), CallbackQueryHandler(news_send_final, pattern="^news_send_final$")],
        name="news_conversation",
        persistent=False,
        per_message=False,
        per_chat=True,
    )
    app.add_handler(news_conv_handler)
    ticket_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(create_ticket_handler, pattern="^create_ticket$")],
        states={TICKET_RECEIPT: [MessageHandler(filters.PHOTO | filters.Document.ALL, ticket_get_receipt)]},
        fallbacks=[CommandHandler("cancel", cancel_ticket)],
        name="ticket_conversation",
        persistent=False,
        per_message=False,
        per_chat=True,
    )
    app.add_handler(ticket_conv_handler)
    app.add_handler(CallbackQueryHandler(random_fact_callback, pattern="^random_fact$"))
    app.add_handler(CallbackQueryHandler(handle_callback))
    logger.info("XolirX VPN Bot started")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
