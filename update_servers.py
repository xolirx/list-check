import asyncio, aiohttp, re, ssl, json, base64, time, logging, sys
from urllib.parse import unquote

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("update_servers")

VLESS_BLACK_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS_mobile.txt"
VLESS_WHITE_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt"
BLACK_OUT = "bla.txt"
WHITE_OUT = "white.txt"
BLACK_STD_OUT = "wi-fi(black).txt"
BLACK_PREM_OUT = "wi-fi(black)prem.txt"
WHITE_STD_OUT = "lte(white).txt"
WHITE_PREM_OUT = "lte(white)prem.txt"
MAX_WORKERS = 50
VLESS_CHECK_TIMEOUT = 3
MAX_RETRIES = 3

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

GEO_CACHE = {}

async def fetch_text(url, timeout=15):
    for attempt in range(MAX_RETRIES):
        try:
            async with aiohttp.ClientSession() as sess:
                async with sess.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        if text and len(text.strip()) >= 10:
                            return text
            logger.warning(f"Attempt {attempt+1} failed for {url}, retrying...")
        except Exception as e:
            logger.warning(f"Attempt {attempt+1} error for {url}: {e}")
        if attempt < MAX_RETRIES - 1:
            await asyncio.sleep(2)
    return None

def parse_config(config):
    for prefix in ('vless://', 'trojan://', 'hysteria2://'):
        if config.startswith(prefix):
            rest = config[len(prefix):]
            break
    else:
        return None
    if '@' not in rest:
        return None
    parts = rest.split('@')
    if len(parts) != 2:
        return None
    uuid = parts[0]
    addr_part = parts[1]
    if ':' not in addr_part:
        return None
    addr_parts = addr_part.split(':')
    if len(addr_parts) < 2:
        return None
    address = addr_parts[0]
    port_segment = addr_parts[1]
    port_match = re.match(r'^(\d+)', port_segment)
    if not port_match:
        return None
    port = int(port_match.group(1))
    params = {}
    if '?' in port_segment:
        params_str = port_segment.split('?')[1]
        if '#' in params_str:
            params_str = params_str.split('#')[0]
        for param in params_str.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key] = value
    return {'uuid': uuid, 'address': address, 'port': port, 'params': params}

async def check_server(parsed):
    address = parsed["address"]
    port = parsed["port"]
    for use_ssl in [False, True]:
        try:
            ctx = ssl.create_default_context() if use_ssl else None
            if ctx:
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(address, port, ssl=ctx),
                timeout=VLESS_CHECK_TIMEOUT
            )
            writer.close()
            await writer.wait_closed()
            return True
        except Exception:
            continue
    return False

async def batch_detect_country(ips):
    if not ips:
        return {}
    results = {}
    for batch_start in range(0, len(ips), 100):
        batch = ips[batch_start:batch_start + 100]
        try:
            async with aiohttp.ClientSession() as sess:
                async with sess.post(
                    "http://ip-api.com/batch?fields=status,country,countryCode,query",
                    json=[{"query": ip} for ip in batch],
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for r in data:
                            ip = r.get("query", "")
                            if r.get("status") == "success":
                                country = r.get("country", "Anycast")
                                code = r.get("countryCode", "").lower()
                                if code and len(code) == 2:
                                    flag = chr(0x1F1E6 + ord(code[0].upper()) - 65) + chr(0x1F1E6 + ord(code[1].upper()) - 65)
                                else:
                                    flag = "🌍"
                                results[ip] = (country, flag)
                            else:
                                results[ip] = ("Anycast", "🌍")
        except Exception as e:
            logger.warning(f"IP batch failed: {e}")
            for ip in batch:
                results[ip] = ("Anycast", "🌍")
    return results

async def format_config(line, list_type):
    if '#' in line:
        base_url, fragment = line.split('#', 1)
        fragment_decoded = unquote(fragment)
        if 'anycast' in fragment_decoded.lower():
            return f"{base_url}#🌍 Anycast"
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
    else:
        base_url = line
    parsed = parse_config(line)
    if parsed and re.match(r'^\d+\.\d+\.\d+\.\d+$', parsed['address']):
        ip = parsed['address']
        if ip in GEO_CACHE:
            country, flag = GEO_CACHE[ip]
        else:
            country, flag = "Anycast", "🌍"
        if country != "Anycast":
            return f"{base_url}#{flag} {country}"
    return f"{base_url}#🌍 Anycast"

def generate_routing():
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

COLOR_PROFILE_JSON = """{"backgroundGradientRotationAngle":39.21265661716461,"serverRowChevronColor":"#F3FFFDFF","buttonImageType":"light","buttonTimerColor":"#3B3C3DFF","subscriptionTrafficBackgroundColor":"#00343BFF","subscriptionInfoBackgroundColor":"#006B7AFF","serverRowTitleTextColor":"#D0FFF3FF","serverRowBackgroundColor":"#02424DFF","powerIconColor":"#05525ACA","supportIconColor":"#F3FFF9FF","profileWebPageIconColor":"#F5FFF9FF","selectedServerRowColor":"#006B7BFF","disclosureHeaderTextColor":"#D0FFF3FF","subsHeaderColor":"#007982FF","elipseColors":["#4DFF00CC","#E2FF00FF","#FF6000FF"],"subscriptionInfoTextColor":"#E5FFF7FF","buttonColor":"#8FFFFEFF","serverRowSubTitleTextColor":"#ADD3CBFF","topBarButtonsColor":"#FFFFFFD8","settingsControlsTintColor":"#00C3C1FF","backgroundGradientColorIntensity":1,"disclosureSubHeaderTextColor":"#A4FFE599","additionalOptionsButtonColor":"#FBFFFF99","backgroundImageType":"light","backgroundColors":["#003740FF","#003740FF","#005255FF","#00A6A1FF","#00C9DDFF"],"subHeaderButtonColor":"#BAD7CFFF","buttonTextColor":"#000000FF"}"""
COLOR_PROFILE = base64.b64encode(COLOR_PROFILE_JSON.encode()).decode()

STANDARD_HEADERS = f"""#announce: base64:{base64.b64encode("XolirX VPN — полностью бесплатный сервис. Много серверов, безлимитный трафик. Поддержка: @xolirx".encode()).decode()}
#profile-title: XolirX VPN
#profile-update-interval: 1
#subscription-userinfo: upload=0; download=0; total=0; expire=0
#support-url: https://t.me/xolirx
#profile-web-page-url: https://t.me/xolirx

"""

PREMIUM_HEADERS = f"""#announce: XolirX VPN — полностью бесплатный сервис. Много серверов, безлимитный трафик. Поддержка Happ. Поддержка: @xolirx
#profile-title: XolirX VPN | ⚫ |
#profile-update-interval: 1
#subscription-userinfo: upload=0; download=5368709120; total=10737418240; expire=3085257600
#support-url: https://t.me/xolirx
#profile-web-page-url: https://xolirx-vpn.vercel.app/
#ping-type: proxy
#check-url-via-proxy: https://cp.cloudflare.com/generate_204
#hide-settings: 1
#routing-enable: 1
#sniffing-enable: 1
#app-auto-start: 1
#subscription-pin: true
#sub-expire: 1
#sub-expire-button-link: https://t.me/xolirx
#notification-subs-expire: 1
#color-profile: {COLOR_PROFILE}
#sub-info-text: XolirX VPN — бесплатный VPN без ограничений. Приятного использования!
#sub-info-color: red
#sub-info-button-text: Канал
#sub-info-button-link: https://t.me/vpn_by_xolirx
#change-user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36
#providerid TcP1jBHx
#server-address-resolve-enable: 1
#server-address-resolve-dns-domain: https://common.dot.dns.yandex.net/dns-query
#server-address-resolve-dns-ip: 77.88.8.8

"""

BLACK_STD_HEADER = STANDARD_HEADERS
WHITE_STD_HEADER = STANDARD_HEADERS
BLACK_PREM_HEADER = PREMIUM_HEADERS
WHITE_PREM_HEADER = PREMIUM_HEADERS

async def fetch_and_check(path_black_std, path_black_prem, path_white_std, path_white_prem):
    black_text, white_text = await asyncio.gather(
        fetch_text(VLESS_BLACK_URL),
        fetch_text(VLESS_WHITE_URL)
    )

    results = []

    for source_text, label, protocols in [
        (black_text, "Black", ["vless://"]),
        (white_text, "White", ["vless://", "hysteria2://", "trojan://"]),
    ]:
        if not source_text:
            logger.error(f"{label} source empty")
            results.append(False)
            continue
        candidates = []
        for line in source_text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") or not stripped:
                continue
            for proto in protocols:
                if stripped.startswith(proto):
                    candidates.append(stripped)
                    break
        if not candidates:
            logger.error(f"No {label} candidates found")
            results.append(False)
            continue
        logger.info(f"{label}: {len(candidates)} candidates")
        parsed_list = []
        for line in candidates:
            parsed = parse_config(line)
            if parsed:
                parsed_list.append((line, parsed))
        logger.info(f"{label}: {len(parsed_list)} parsed")
        semaphore = asyncio.Semaphore(MAX_WORKERS)
        async def check_one(parsed):
            async with semaphore:
                return await check_server(parsed)
        tasks = [check_one(parsed) for _, parsed in parsed_list]
        check_results = await asyncio.gather(*tasks, return_exceptions=True)
        working_lines = []
        working_parsed = []
        for (line, parsed), is_ok in zip(parsed_list, check_results):
            if isinstance(is_ok, Exception):
                continue
            if is_ok:
                working_lines.append(line)
                working_parsed.append(parsed)
        logger.info(f"{label}: {len(working_lines)}/{len(candidates)} working")
        if not working_lines:
            logger.error(f"No working {label} servers")
            results.append(False)
            continue
        ip_list = [p['address'] for p in working_parsed if re.match(r'^\d+\.\d+\.\d+\.\d+$', p['address'])]
        ip_geo = await batch_detect_country(list(set(ip_list)))
        GEO_CACHE.update(ip_geo)
        formatted_lines = []
        for line in working_lines:
            try:
                formatted = await format_config(line, label.lower())
                formatted_lines.append(formatted)
            except Exception:
                formatted_lines.append(line)
        clean_content = "\n".join(formatted_lines)
        routing_link = generate_routing()

        std_header = BLACK_STD_HEADER if label == "Black" else WHITE_STD_HEADER
        prem_header = BLACK_PREM_HEADER if label == "Black" else WHITE_PREM_HEADER

        std_path = path_black_std if label == "Black" else path_white_std
        prem_path = path_black_prem if label == "Black" else path_white_prem

        std_content = std_header + clean_content + "\n\n" + routing_link
        with open(std_path, "w", encoding="utf-8") as f:
            f.write(std_content)
        logger.info(f"{label} standard saved to {std_path}")

        prem_content = prem_header + clean_content + "\n\n" + routing_link
        with open(prem_path, "w", encoding="utf-8") as f:
            f.write(prem_content)
        logger.info(f"{label} premium saved to {prem_path}")

        results.append(True)

    return all(results)

async def main():
    if len(sys.argv) > 1:
        black_std_path = sys.argv[1]
        black_prem_path = sys.argv[2] if len(sys.argv) > 2 else BLACK_PREM_OUT
        white_std_path = sys.argv[3] if len(sys.argv) > 3 else WHITE_STD_OUT
        white_prem_path = sys.argv[4] if len(sys.argv) > 4 else WHITE_PREM_OUT
    else:
        black_std_path = BLACK_STD_OUT
        black_prem_path = BLACK_PREM_OUT
        white_std_path = WHITE_STD_OUT
        white_prem_path = WHITE_PREM_OUT
    logger.info(f"Output: {black_std_path}, {black_prem_path}, {white_std_path}, {white_prem_path}")
    ok = await fetch_and_check(black_std_path, black_prem_path, white_std_path, white_prem_path)
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    asyncio.run(main())
