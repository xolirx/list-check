import asyncio, aiohttp, re, ssl, json, base64, time, logging, sys, socket, random, os, tempfile, zipfile, io, platform
from urllib.parse import unquote

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("update_servers")

VLESS_BLACK_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS_mobile.txt"
VLESS_WHITE_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt"
BLACK_STD_OUT = "wi-fi(black).txt"
BLACK_PREM_OUT = "wi-fi(black)prem.txt"
WHITE_STD_OUT = "lte(white).txt"
WHITE_PREM_OUT = "lte(white)prem.txt"
MAX_WORKERS = 50
CHECK_TIMEOUT = 5
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
    for prefix in ('vless://', 'trojan://', 'hysteria2://', 'VLESS://', 'TROJAN://', 'HYSTERIA2://'):
        if config.startswith(prefix):
            rest = config[len(prefix):]
            break
    else:
        return None
    if '@' in rest:
        parts = rest.rsplit('@', 1)
        addr_part = parts[1]
    else:
        addr_part = rest
    if '#' in addr_part:
        addr_part = addr_part.split('#')[0]
    if '?' in addr_part:
        addr_part = addr_part.split('?')[0]
    if addr_part.startswith('['):
        ipv6_match = re.match(r'^\[(.+)\]:(\d+)$', addr_part)
        if ipv6_match:
            return {'address': ipv6_match.group(1), 'port': int(ipv6_match.group(2))}
        return None
    if ':' not in addr_part:
        return None
    addr_parts = addr_part.split(':')
    if len(addr_parts) < 2:
        return None
    address = addr_parts[0]
    port_match = re.match(r'^(\d+)', addr_parts[1])
    if not port_match:
        return None
    return {'address': address, 'port': int(port_match.group(1))}

async def check_server(parsed):
    address = parsed["address"]
    port = parsed["port"]
    for attempt in range(2):
        for use_tls in [True, False]:
            writer = None
            try:
                ctx = None
                if use_tls:
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                start = time.monotonic()
                _, writer = await asyncio.wait_for(
                    asyncio.open_connection(address, port, ssl=ctx),
                    timeout=CHECK_TIMEOUT
                )
                elapsed = time.monotonic() - start
                try:
                    await asyncio.wait_for(
                        writer.reader.read(1),
                        timeout=0.5
                    )
                except Exception:
                    pass
                logger.debug(f"Server {address}:{port} OK ({elapsed*1000:.0f}ms, tls={use_tls})")
                return True
            except Exception:
                continue
            finally:
                if writer:
                    try:
                        writer.close()
                        await writer.wait_closed()
                    except Exception:
                        pass
    return False

def parse_vless_url(url):
    for prefix in ("vless://", "VLESS://"):
        if url.startswith(prefix):
            rest = url[len(prefix):]
            break
    else:
        return None
    fragment = ""
    if "#" in rest:
        rest, fragment = rest.split("#", 1)
    qs = {}
    if "?" in rest:
        rest, qstr = rest.split("?", 1)
        for part in qstr.split("&"):
            if "=" in part:
                k, v = part.split("=", 1)
                qs[k] = unquote(v)
    user_id = ""
    if "@" in rest:
        user_id, rest = rest.split("@", 1)
    host = rest
    port = 443
    if ":" in rest:
        host, port_str = rest.rsplit(":", 1)
        try:
            port = int(port_str)
        except ValueError:
            pass
    return {"id": user_id, "host": host, "port": port, "fragment": unquote(fragment) if fragment else "", "query": qs}

def vless_to_xray_json(parsed, socks_port=10808):
    q = parsed["query"]
    security = q.get("security", "none")
    network = q.get("type", "tcp")
    outbound = {
        "protocol": "vless",
        "settings": {
            "vnext": [{
                "address": parsed["host"],
                "port": parsed["port"],
                "users": [{"id": parsed["id"], "encryption": q.get("encryption", "none")}]
            }]
        },
        "streamSettings": {"network": network, "security": security}
    }
    if security == "reality":
        outbound["streamSettings"]["realitySettings"] = {
            "serverName": q.get("sni", parsed["host"]),
            "fingerprint": q.get("fp", "chrome"),
            "publicKey": q.get("pbk", ""),
            "shortId": q.get("sid", ""),
            "spiderX": q.get("spx", "")
        }
        if q.get("flow"):
            outbound["settings"]["vnext"][0]["users"][0]["flow"] = q["flow"]
    if network == "grpc" and q.get("serviceName"):
        outbound["streamSettings"]["grpcSettings"] = {"serviceName": q["serviceName"]}
    return {
        "log": {"loglevel": "warning"},
        "inbounds": [{"listen": "127.0.0.1", "port": socks_port, "protocol": "socks", "settings": {"udp": False}}],
        "outbounds": [outbound],
        "policy": {"levels": {"0": {"connIdle": 5, "handshake": 5}}}
    }

async def socks5_connect(test_host, test_port, proxy_port=10808, timeout=10):
    reader, writer = await asyncio.wait_for(
        asyncio.open_connection("127.0.0.1", proxy_port), timeout=timeout
    )
    try:
        writer.write(b"\x05\x01\x00")
        await writer.drain()
        resp = await asyncio.wait_for(reader.read(2), timeout=3)
        if resp != b"\x05\x00":
            raise ConnectionError(f"SOCKS5 handshake failed: {resp}")
        host_bytes = test_host.encode()
        if len(host_bytes) > 255:
            raise ValueError("Hostname too long for SOCKS5")
        req = b"\x05\x01\x00\x03" + bytes([len(host_bytes)]) + host_bytes + test_port.to_bytes(2, "big")
        writer.write(req)
        await writer.drain()
        resp = await asyncio.wait_for(reader.read(10), timeout=3)
        if len(resp) < 2 or resp[1] != 0x00:
            raise ConnectionError(f"SOCKS5 connect failed: {resp[1] if len(resp) > 1 else resp}")
        return reader, writer
    except Exception:
        writer.close()
        raise

async def test_vless_with_xray(vless_url, xray_path, socks_port=10809):
    parsed = parse_vless_url(vless_url)
    if not parsed:
        return False, 0
    config = vless_to_xray_json(parsed, socks_port)
    config_path = os.path.join(tempfile.gettempdir(), f"xray_test_{socks_port}.json")
    proc = None
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, separators=(",", ":"))
        proc = await asyncio.create_subprocess_exec(
            xray_path, "run", "-c", config_path,
            stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
        )
        await asyncio.sleep(0.4)
        start = time.monotonic()
        try:
            _, writer = await socks5_connect("www.google.com", 443, proxy_port=socks_port, timeout=8)
            elapsed = time.monotonic() - start
            writer.close()
            return True, elapsed
        except Exception:
            return False, 0
    finally:
        if proc and proc.returncode is None:
            try:
                proc.kill()
                await proc.wait()
            except Exception:
                pass
        try:
            os.unlink(config_path)
        except Exception:
            pass

async def resolve_domains(domains):
    if not domains:
        return {}
    loop = asyncio.get_event_loop()
    resolved = {}
    for domain in domains:
        try:
            addrs = await loop.getaddrinfo(domain, None, type=socket.SOCK_STREAM)
            for family, type_, proto, canonname, sockaddr in addrs:
                ip = sockaddr[0]
                resolved[domain] = ip
                break
        except Exception as e:
            logger.debug(f"DNS resolve failed for {domain}: {e}")
    return resolved

async def batch_detect_country(ips):
    if not ips:
        return {}
    results = {}
    async with aiohttp.ClientSession() as sess:
        for batch_start in range(0, len(ips), 100):
            batch = ips[batch_start:batch_start + 100]
            try:
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

def is_ipv4(address):
    return re.match(r'^\d+\.\d+\.\d+\.\d+$', address) is not None

def is_ipv6(address):
    return ':' in address

async def format_config(line, list_type):
    if '#' in line:
        base_url, fragment = line.split('#', 1)
        fragment_decoded = unquote(fragment)
        if 'anycast' in fragment_decoded.lower():
            return f"{base_url}#Обход XOL"
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
            return f"{base_url}#{flag} {rest if rest else 'Обход XOL'}"
    else:
        base_url = line
    parsed = parse_config(line)
    if parsed:
        address = parsed['address']
        if address in GEO_CACHE:
            country, flag = GEO_CACHE[address]
        else:
            country, flag = "Anycast", "🌍"
        if country != "Anycast":
            return f"{base_url}#{flag} {country}"
    return f"{base_url}#Обход XOL"

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

COLOR_PROFILE_JSON = """{"backgroundGradientRotationAngle":45,"serverRowChevronColor":"#FFD6E0FF","buttonImageType":"light","buttonTimerColor":"#2E1018FF","subscriptionTrafficBackgroundColor":"#1A0A0EFF","subscriptionInfoBackgroundColor":"#2E1018FF","serverRowTitleTextColor":"#FFD6E0FF","serverRowBackgroundColor":"#1E0C12FF","powerIconColor":"#FF6B8ACA","supportIconColor":"#FFE6EBFF","profileWebPageIconColor":"#F5FFF9FF","selectedServerRowColor":"#4A1E2CFF","disclosureHeaderTextColor":"#FFD6E0FF","subsHeaderColor":"#2E1018FF","elipseColors":["#FF6B8AFF","#E5506CFF","#C4304EFF"],"subscriptionInfoTextColor":"#FFC4D2FF","buttonColor":"#E5506CFF","serverRowSubTitleTextColor":"#D98A9EFF","topBarButtonsColor":"#FFFFFFD8","settingsControlsTintColor":"#E5506CFF","backgroundGradientColorIntensity":1,"disclosureSubHeaderTextColor":"#FFB8CAFF","additionalOptionsButtonColor":"#FF6B8A99","backgroundImageType":"light","backgroundColors":["#1A0A0EFF","#1A0A0EFF","#2E1018FF","#4B1A28FF","#7A2A3EFF"],"subHeaderButtonColor":"#FF6B8AFF","buttonTextColor":"#FFFFFFFF"}"""
COLOR_PROFILE = base64.b64encode(COLOR_PROFILE_JSON.encode()).decode()

def std_header(title):
    return f"""#announce: base64:{base64.b64encode("XolirX VPN — полностью бесплатный сервис. Много серверов, безлимитный трафик. Поддержка: @xolirx_support_bot".encode()).decode()}
#profile-title: {title}
#profile-update-interval: 1
#subscription-userinfo: upload=0; download=0; total=0; expire=0
#support-url: https://t.me/xolirx
#profile-web-page-url: https://xolirx-vpn.vercel.app/

"""

def prem_header(title):
    return f"""#announce: XolirX VPN — полностью бесплатный сервис. Много серверов, безлимитный трафик. Поддержка Happ. Поддержка: @xolirx_support_bot
#profile-title: {title}
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
#providerid: VKn6TPIQ
#server-address-resolve-enable: 1
#server-address-resolve-dns-domain: https://common.dot.dns.yandex.net/dns-query
#server-address-resolve-dns-ip: 77.88.8.8

"""

BLACK_STD_HEADER = std_header("XolirX VPN | BLACK")
WHITE_STD_HEADER = std_header("XolirX VPN | LTE")
BLACK_PREM_HEADER = prem_header("XolirX VPN | ⚫")
WHITE_PREM_HEADER = prem_header("XolirX VPN | ⚪")

async def write_file(path, content, label, kind):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"{label} {kind} saved to {path}")
        return True
    except OSError as e:
        logger.error(f"Failed to write {path}: {e}")
        return False

async def fetch_and_check(path_black_std, path_black_prem, path_white_std, path_white_prem, xray_path=None):
    black_text, white_text = await asyncio.gather(
        fetch_text(VLESS_BLACK_URL),
        fetch_text(VLESS_WHITE_URL)
    )

    results = []
    semaphore = asyncio.Semaphore(MAX_WORKERS)
    async def check_one(parsed):
        async with semaphore:
            return await check_server(parsed)

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
                if stripped.lower().startswith(proto):
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

        if xray_path:
            vless_indices = [i for i, l in enumerate(working_lines) if l.lower().startswith("vless://")]
            if vless_indices:
                keep_indices = set(range(len(working_lines)))
                xray_fail = 0
                for idx in vless_indices:
                    ok, latency = await test_vless_with_xray(working_lines[idx], xray_path)
                    if ok:
                        logger.info(f"  Xray OK ({latency*1000:.0f}ms) {working_lines[idx].split('#')[0][:50]}...")
                    else:
                        keep_indices.discard(idx)
                        xray_fail += 1
                        logger.info(f"  Xray FAIL {working_lines[idx].split('#')[0][:50]}...")
                if xray_fail:
                    working_lines = [working_lines[i] for i in sorted(keep_indices)]
                    working_parsed = [working_parsed[i] for i in sorted(keep_indices)]
                    logger.info(f"{label}: Xray rejected {xray_fail} servers")

        seen = set()
        unique_lines = []
        unique_parsed = []
        for line, parsed in zip(working_lines, working_parsed):
            key = (parsed['address'], parsed['port'])
            if key not in seen:
                seen.add(key)
                unique_lines.append(line)
                unique_parsed.append(parsed)
        working_lines, working_parsed = unique_lines, unique_parsed
        logger.info(f"{label}: {len(working_lines)} unique after dedup")

        ip_list = []
        domain_list = []
        for p in working_parsed:
            addr = p['address']
            if is_ipv4(addr):
                ip_list.append(addr)
            elif is_ipv6(addr):
                ip_list.append(addr)
            else:
                domain_list.append(addr)

        if domain_list:
            dns_map = await resolve_domains(list(set(domain_list)))
            for domain, ip in dns_map.items():
                if ip not in GEO_CACHE:
                    ip_list.append(ip)

        ip_geo = await batch_detect_country(list(set(ip_list)))
        GEO_CACHE.update(ip_geo)

        formatted_lines = []
        for line in working_lines:
            try:
                formatted = await format_config(line, label.lower())
                formatted_lines.append(formatted)
            except Exception:
                formatted_lines.append(line)
        eligible = []
        country_flags_set = set(COUNTRY_FLAGS.values())
        for i, fl in enumerate(formatted_lines):
            if "#" not in fl:
                continue
            base, frag = fl.split("#", 1)
            frag = frag.strip()
            for flag_emoji in country_flags_set:
                if frag.startswith(flag_emoji):
                    country_name = frag[len(flag_emoji):].strip()
                    eligible.append((i, base, country_name))
                    break
        if eligible:
            for idx, base, country in random.sample(eligible, min(50, len(eligible))):
                formatted_lines[idx] = f"{base}#\U0001F1EA\U0001F1FA Авто-Обход | {country}"
        clean_content = "\n".join(formatted_lines)
        routing_link = generate_routing()

        std_hdr = BLACK_STD_HEADER if label == "Black" else WHITE_STD_HEADER
        prem_hdr = BLACK_PREM_HEADER if label == "Black" else WHITE_PREM_HEADER
        std_path = path_black_std if label == "Black" else path_white_std
        prem_path = path_black_prem if label == "Black" else path_white_prem

        ok1 = await write_file(std_path, std_hdr + clean_content + "\n\n" + routing_link, label, "standard")
        if not ok1:
            results.append(False)
            continue
        ok2 = await write_file(prem_path, prem_hdr + clean_content + "\n\n" + routing_link, label, "premium")
        if not ok2:
            results.append(False)
            continue

        results.append(True)

    return all(results)

async def main():
    xray_path = None
    paths = [BLACK_STD_OUT, BLACK_PREM_OUT, WHITE_STD_OUT, WHITE_PREM_OUT]
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--xray":
            if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("-"):
                xray_path = sys.argv[i + 1]
                i += 2
            else:
                xray_path = "auto"
                i += 1
        else:
            if i < len(sys.argv):
                paths[0] = sys.argv[i]
            if i + 1 < len(sys.argv):
                paths[1] = sys.argv[i + 1]
            if i + 2 < len(sys.argv):
                paths[2] = sys.argv[i + 2]
            if i + 3 < len(sys.argv):
                paths[3] = sys.argv[i + 3]
            break
    if xray_path and xray_path != "auto" and not os.path.isfile(xray_path):
        logger.warning(f"Xray not found at '{xray_path}', will auto-download")
        xray_path = "auto"
    if xray_path == "auto":
        import platform, zipfile, io
        system = platform.system().lower()
        arch = platform.machine().lower()
        if "linux" in system:
            url = "https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip"
            xray_path = "/tmp/xray"
        elif "windows" in system:
            url = "https://github.com/XTLS/Xray-core/releases/latest/download/Xray-windows-64.zip"
            xray_path = os.path.join(tempfile.gettempdir(), "xray.exe")
        else:
            url = "https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip"
            xray_path = "/tmp/xray"
        if not os.path.isfile(xray_path):
            logger.info(f"Downloading Xray from {url}...")
            async with aiohttp.ClientSession() as sess:
                async with sess.get(url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        with zipfile.ZipFile(io.BytesIO(data)) as zf:
                            for name in zf.namelist():
                                if name.endswith("/xray") or name.endswith("\\xray.exe") or name == "xray.exe" or name == "xray":
                                    with zf.open(name) as src, open(xray_path, "wb") as dst:
                                        dst.write(src.read())
                                    os.chmod(xray_path, 0o755)
                                    break
                            else:
                                logger.error("xray binary not found in zip")
                                xray_path = None
                    else:
                        logger.error(f"Failed to download Xray: {resp.status}")
                        xray_path = None
        else:
            logger.info(f"Xray already at {xray_path}")
    logger.info(f"Output: {paths[0]}, {paths[1]}, {paths[2]}, {paths[3]}, xray={xray_path}")
    ok = await fetch_and_check(paths[0], paths[1], paths[2], paths[3], xray_path=xray_path)
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    asyncio.run(main())
