import re
import argparse
import os
from urllib.parse import urlparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 尝试导入 requests，用于 HTTP 探测
try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
except ImportError:
    requests = None

# 默认源代码文件扩展名（更全面的列表）
DEFAULT_SOURCE_EXTENSIONS = {
    # Web前端
    '.html', '.htm', '.xhtml', '.shtml', '.dhtml',
    '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs',
    '.css', '.scss', '.sass', '.less', '.styl', '.stylus',
    '.vue', '.svelte', '.astro',

    # Web后端
    '.php', '.php3', '.php4', '.php5', '.phtml',
    '.asp', '.aspx', '.ascx', '.ashx', '.asmx',
    '.jsp', '.jspx', '.jhtml',
    '.cgi', '.pl', '.pm',

    # 编程语言
    '.py', '.pyw', '.pyi', '.pyc',
    '.java', '.class', '.jar',
    '.c', '.h', '.cpp', '.cxx', '.cc', '.hpp', '.hxx',
    '.cs', '.vb', '.fs', '.fsx',
    '.go', '.rs',
    '.rb', '.rake', '.rbw',
    '.swift', '.kt', '.kts',
    '.scala', '.groovy',
    '.lua', '.r',

    # 脚本和配置
    '.sh', '.bash', '.zsh', '.fish',
    '.bat', '.cmd', '.ps1', '.psm1',
    '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.config',
    '.json', '.json5', '.jsonc',
    '.xml', '.xsl', '.xslt', '.xsd',

    # 模板文件
    '.tmpl', '.tpl', '.template',
    '.ejs', '.pug', '.jade', '.hbs', '.handlebars',
    '.erb', '.haml', '.slim',
    '.ftl', '.vm', '.twig',

    # 文档和说明
    '.md', '.markdown', '.mdown', '.mkd',
    '.rst', '.txt', '.text',
    '.adoc', '.asciidoc',

    # 数据和其他
    '.sql', '.db', '.sqlite',
    '.csv', '.tsv',
    '.log',
    '.env', '.env.local', '.env.production',
    '.properties', '.gradle', '.maven',
    '.dockerfile', '.makefile', '.cmake',
    '.htaccess', '.htpasswd', '.nginx'
}

# 黑链关键词（常见的黑链相关词汇）——默认就会参与“命中黑名单关键字”判断
BLACKLINK_KEYWORDS = [
    'casino', 'poker', 'viagra', 'cialis', 'porn', 'xxx', 'sex',
    'gambling', 'loan', 'credit', 'pharmacy', 'pills',
    '博彩', '赌博', '色情', '成人', '贷款', '办证', '发票', '代开',
    '六合彩', '时时彩', '彩票', '私服', '外挂', '游戏币','代理','Telegram','VPN','区块链','体育','直播','棋牌','赌场','娱乐城','提款','洗钱','黑网','黑产','黑客','破解','木马','病毒','钓鱼','诈骗'
]

# 在任意位置匹配“疑似域名”的正则（不要求 http:// 前缀）
DOMAIN_REGEX = re.compile(
    r'\b((?:[a-z0-9-]+\.)+(?:AAA|AARP|ABB|ABBOTT|ABBVIE|ABC|ABLE|ABOGADO|ABUDHABI|AC|ACADEMY|ACCENTURE|ACCOUNTANT|ACCOUNTANTS|ACO|ACTOR|AD|ADS|ADULT|AE|AEG|AERO|AETNA|AF|AFL|AFRICA|AG|AGAKHAN|AGENCY|AI|AIG|AIRBUS|AIRFORCE|AIRTEL|AKDN|AL|ALIBABA|ALIPAY|ALLFINANZ|ALLSTATE|ALLY|ALSACE|ALSTOM|AM|AMAZON|AMERICANEXPRESS|AMERICANFAMILY|AMEX|AMFAM|AMICA|AMSTERDAM|ANALYTICS|ANDROID|ANQUAN|ANZ|AO|AOL|APARTMENTS|APP|APPLE|AQ|AQUARELLE|AR|ARAB|ARAMCO|ARCHI|ARMY|ARPA|ART|ARTE|AS|ASDA|ASIA|ASSOCIATES|AT|ATHLETA|ATTORNEY|AU|AUCTION|AUDI|AUDIBLE|AUDIO|AUSPOST|AUTHOR|AUTO|AUTOS|AW|AWS|AX|AXA|AZ|AZURE|BA|BABY|BAIDU|BANAMEX|BAND|BANK|BAR|BARCELONA|BARCLAYCARD|BARCLAYS|BAREFOOT|BARGAINS|BASEBALL|BASKETBALL|BAUHAUS|BAYERN|BB|BBC|BBT|BBVA|BCG|BCN|BD|BE|BEATS|BEAUTY|BEER|BERLIN|BEST|BESTBUY|BET|BF|BG|BH|BHARTI|BI|BIBLE|BID|BIKE|BING|BINGO|BIO|BIZ|BJ|BLACK|BLACKFRIDAY|BLOCKBUSTER|BLOG|BLOOMBERG|BLUE|BM|BMS|BMW|BN|BNPPARIBAS|BO|BOATS|BOEHRINGER|BOFA|BOM|BOND|BOO|BOOK|BOOKING|BOSCH|BOSTIK|BOSTON|BOT|BOUTIQUE|BOX|BR|BRADESCO|BRIDGESTONE|BROADWAY|BROKER|BROTHER|BRUSSELS|BS|BT|BUILD|BUILDERS|BUSINESS|BUY|BUZZ|BV|BW|BY|BZ|BZH|CA|CAB|CAFE|CAL|CALL|CALVINKLEIN|CAM|CAMERA|CAMP|CANON|CAPETOWN|CAPITAL|CAPITALONE|CAR|CARAVAN|CARDS|CARE|CAREER|CAREERS|CARS|CASA|CASE|CASH|CASINO|CAT|CATERING|CATHOLIC|CBA|CBN|CBRE|CC|CD|CENTER|CEO|CERN|CF|CFA|CFD|CG|CH|CHANEL|CHANNEL|CHARITY|CHASE|CHAT|CHEAP|CHINTAI|CHRISTMAS|CHROME|CHURCH|CI|CIPRIANI|CIRCLE|CISCO|CITADEL|CITI|CITIC|CITY|CK|CL|CLAIMS|CLEANING|CLICK|CLINIC|CLINIQUE|CLOTHING|CLOUD|CLUB|CLUBMED|CM|CN|CO|COACH|CODES|COFFEE|COLLEGE|COLOGNE|COM|COMMBANK|COMMUNITY|COMPANY|COMPARE|COMPUTER|COMSEC|CONDOS|CONSTRUCTION|CONSULTING|CONTACT|CONTRACTORS|COOKING|COOL|COOP|CORSICA|COUNTRY|COUPON|COUPONS|COURSES|CPA|CR|CREDIT|CREDITCARD|CREDITUNION|CRICKET|CROWN|CRS|CRUISE|CRUISES|CU|CUISINELLA|CV|CW|CX|CY|CYMRU|CYOU|CZ|DAD|DANCE|DATA|DATE|DATING|DATSUN|DAY|DCLK|DDS|DE|DEAL|DEALER|DEALS|DEGREE|DELIVERY|DELL|DELOITTE|DELTA|DEMOCRAT|DENTAL|DENTIST|DESI|DESIGN|DEV|DHL|DIAMONDS|DIET|DIGITAL|DIRECT|DIRECTORY|DISCOUNT|DISCOVER|DISH|DIY|DJ|DK|DM|DNP|DO|DOCS|DOCTOR|DOG|DOMAINS|DOT|DOWNLOAD|DRIVE|DTV|DUBAI|DUPONT|DURBAN|DVAG|DVR|DZ|EARTH|EAT|EC|ECO|EDEKA|EDU|EDUCATION|EE|EG|EMAIL|EMERCK|ENERGY|ENGINEER|ENGINEERING|ENTERPRISES|EPSON|EQUIPMENT|ER|ERICSSON|ERNI|ES|ESQ|ESTATE|ET|EU|EUROVISION|EUS|EVENTS|EXCHANGE|EXPERT|EXPOSED|EXPRESS|EXTRASPACE|FAGE|FAIL|FAIRWINDS|FAITH|FAMILY|FAN|FANS|FARM|FARMERS|FASHION|FAST|FEDEX|FEEDBACK|FERRARI|FERRERO|FI|FIDELITY|FIDO|FILM|FINAL|FINANCE|FINANCIAL|FIRE|FIRESTONE|FIRMDALE|FISH|FISHING|FIT|FITNESS|FJ|FK|FLICKR|FLIGHTS|FLIR|FLORIST|FLOWERS|FLY|FM|FO|FOO|FOOD|FOOTBALL|FORD|FOREX|FORSALE|FORUM|FOUNDATION|FOX|FR|FREE|FRESENIUS|FRL|FROGANS|FRONTIER|FTR|FUJITSU|FUN|FUND|FURNITURE|FUTBOL|FYI|GA|GAL|GALLERY|GALLO|GALLUP|GAME|GAMES|GAP|GARDEN|GAY|GB|GBIZ|GD|GDN|GE|GEA|GENT|GENTING|GEORGE|GF|GG|GGEE|GH|GI|GIFT|GIFTS|GIVES|GIVING|GL|GLASS|GLE|GLOBAL|GLOBO|GM|GMAIL|GMBH|GMO|GMX|GN|GODADDY|GOLD|GOLDPOINT|GOLF|GOO|GOODYEAR|GOOG|GOOGLE|GOP|GOT|GOV|GP|GQ|GR|GRAINGER|GRAPHICS|GRATIS|GREEN|GRIPE|GROCERY|GROUP|GS|GT|GU|GUCCI|GUGE|GUIDE|GUITARS|GURU|GW|GY|HAIR|HAMBURG|HANGOUT|HAUS|HBO|HDFC|HDFCBANK|HEALTH|HEALTHCARE|HELP|HELSINKI|HERE|HERMES|HIPHOP|HISAMITSU|HITACHI|HIV|HK|HKT|HM|HN|HOCKEY|HOLDINGS|HOLIDAY|HOMEDEPOT|HOMEGOODS|HOMES|HOMESENSE|HONDA|HORSE|HOSPITAL|HOST|HOSTING|HOT|HOTELS|HOTMAIL|HOUSE|HOW|HR|HSBC|HT|HU|HUGHES|HYATT|HYUNDAI|IBM|ICBC|ICE|ICU|ID|IE|IEEE|IFM|IKANO|IL|IM|IMAMAT|IMDB|IMMO|IMMOBILIEN|IN|INC|INDUSTRIES|INFINITI|INFO|ING|INK|INSTITUTE|INSURANCE|INSURE|INT|INTERNATIONAL|INTUIT|INVESTMENTS|IO|IPIRANGA|IQ|IR|IRISH|IS|ISMAILI|IST|ISTANBUL|IT|ITAU|ITV|JAGUAR|JAVA|JCB|JE|JEEP|JETZT|JEWELRY|JIO|JLL|JM|JMP|JNJ|JO|JOBS|JOBURG|JOT|JOY|JP|JPMORGAN|JPRS|JUEGOS|JUNIPER|KAUFEN|KDDI|KE|KERRYHOTELS|KERRYPROPERTIES|KFH|KG|KH|KI|KIA|KIDS|KIM|KINDLE|KITCHEN|KIWI|KM|KN|KOELN|KOMATSU|KOSHER|KP|KPMG|KPN|KR|KRD|KRED|KUOKGROUP|KW|KY|KYOTO|KZ|LA|LACAIXA|LAMBORGHINI|LAMER|LAND|LANDROVER|LANXESS|LASALLE|LAT|LATINO|LATROBE|LAW|LAWYER|LB|LC|LDS|LEASE|LECLERC|LEFRAK|LEGAL|LEGO|LEXUS|LGBT|LI|LIDL|LIFE|LIFEINSURANCE|LIFESTYLE|LIGHTING|LIKE|LILLY|LIMITED|LIMO|LINCOLN|LINK|LIVE|LIVING|LK|LLC|LLP|LOAN|LOANS|LOCKER|LOCUS|LOL|LONDON|LOTTE|LOTTO|LOVE|LPL|LPLFINANCIAL|LR|LS|LT|LTD|LTDA|LU|LUNDBECK|LUXE|LUXURY|LV|LY|MA|MADRID|MAIF|MAISON|MAKEUP|MAN|MANAGEMENT|MANGO|MAP|MARKET|MARKETING|MARKETS|MARRIOTT|MARSHALLS|MATTEL|MBA|MC|MCKINSEY|MD|ME|MED|MEDIA|MEET|MELBOURNE|MEME|MEMORIAL|MEN|MENU|MERCKMSD|MG|MH|MIAMI|MICROSOFT|MIL|MINI|MINT|MIT|MITSUBISHI|MK|ML|MLB|MLS|MM|MMA|MN|MO|MOBI|MOBILE|MODA|MOE|MOI|MOM|MONASH|MONEY|MONSTER|MORMON|MORTGAGE|MOSCOW|MOTO|MOTORCYCLES|MOV|MOVIE|MP|MQ|MR|MS|MSD|MT|MTN|MTR|MU|MUSEUM|MUSIC|MV|MW|MX|MY|MZ|NA|NAB|NAGOYA|NAME|NAVY|NBA|NC|NE|NEC|NET|NETBANK|NETFLIX|NETWORK|NEUSTAR|NEW|NEWS|NEXT|NEXTDIRECT|NEXUS|NF|NFL|NG|NGO|NHK|NI|NICO|NIKE|NIKON|NINJA|NISSAN|NISSAY|NL|NO|NOKIA|NORTON|NOW|NOWRUZ|NOWTV|NP|NR|NRA|NRW|NTT|NU|NYC|NZ|OBI|OBSERVER|OFFICE|OKINAWA|OLAYAN|OLAYANGROUP|OLLO|OM|OMEGA|ONE|ONG|ONL|ONLINE|OOO|OPEN|ORACLE|ORANGE|ORG|ORGANIC|ORIGINS|OSAKA|OTSUKA|OTT|OVH|PA|PAGE|PANASONIC|PARIS|PARS|PARTNERS|PARTS|PARTY|PAY|PCCW|PE|PET|PF|PFIZER|PG|PH|PHARMACY|PHD|PHILIPS|PHONE|PHOTO|PHOTOGRAPHY|PHOTOS|PHYSIO|PICS|PICTET|PICTURES|PID|PIN|PING|PINK|PIONEER|PIZZA|PK|PL|PLACE|PLAY|PLAYSTATION|PLUMBING|PLUS|PM|PN|PNC|POHL|POKER|POLITIE|PORN|POST|PR|PRAXI|PRESS|PRIME|PRO|PROD|PRODUCTIONS|PROF|PROGRESSIVE|PROMO|PROPERTIES|PROPERTY|PROTECTION|PRU|PRUDENTIAL|PS|PT|PUB|PW|PWC|PY|QA|QPON|QUEBEC|QUEST|RACING|RADIO|RE|READ|REALESTATE|REALTOR|REALTY|RECIPES|RED|REDUMBRELLA|REHAB|REISE|REISEN|REIT|RELIANCE|REN|RENT|RENTALS|REPAIR|REPORT|REPUBLICAN|REST|RESTAURANT|REVIEW|REVIEWS|REXROTH|RICH|RICHARDLI|RICOH|RIL|RIO|RIP|RO|ROCKS|RODEO|ROGERS|ROOM|RS|RSVP|RU|RUGBY|RUHR|RUN|RW|RWE|RYUKYU|SA|SAARLAND|SAFE|SAFETY|SAKURA|SALE|SALON|SAMSCLUB|SAMSUNG|SANDVIK|SANDVIKCOROMANT|SANOFI|SAP|SARL|SAS|SAVE|SAXO|SB|SBI|SBS|SC|SCB|SCHAEFFLER|SCHMIDT|SCHOLARSHIPS|SCHOOL|SCHULE|SCHWARZ|SCIENCE|SCOT|SD|SE|SEARCH|SEAT|SECURE|SECURITY|SEEK|SELECT|SENER|SERVICES|SEVEN|SEW|SEX|SEXY|SFR|SG|SH|SHANGRILA|SHARP|SHELL|SHIA|SHIKSHA|SHOES|SHOP|SHOPPING|SHOUJI|SHOW|SI|SILK|SINA|SINGLES|SITE|SJ|SK|SKI|SKIN|SKY|SKYPE|SL|SLING|SM|SMART|SMILE|SN|SNCF|SO|SOCCER|SOCIAL|SOFTBANK|SOFTWARE|SOHU|SOLAR|SOLUTIONS|SONG|SONY|SOY|SPA|SPACE|SPORT|SPOT|SR|SRL|SS|ST|STADA|STAPLES|STAR|STATEBANK|STATEFARM|STC|STCGROUP|STOCKHOLM|STORAGE|STORE|STREAM|STUDIO|STUDY|STYLE|SU|SUCKS|SUPPLIES|SUPPLY|SUPPORT|SURF|SURGERY|SUZUKI|SV|SWATCH|SWISS|SX|SY|SYDNEY|SYSTEMS|SZ|TAB|TAIPEI|TALK|TAOBAO|TARGET|TATAMOTORS|TATAR|TATTOO|TAX|TAXI|TC|TCI|TD|TDK|TEAM|TECH|TECHNOLOGY|TEL|TEMASEK|TENNIS|TEVA|TF|TG|TH|THD|THEATER|THEATRE|TIAA|TICKETS|TIENDA|TIPS|TIRES|TIROL|TJ|TJMAXX|TJX|TK|TKMAXX|TL|TM|TMALL|TN|TO|TODAY|TOKYO|TOOLS|TOP|TORAY|TOSHIBA|TOTAL|TOURS|TOWN|TOYOTA|TOYS|TR|TRADE|TRADING|TRAINING|TRAVEL|TRAVELERS|TRAVELERSINSURANCE|TRUST|TRV|TT|TUBE|TUI|TUNES|TUSHU|TV|TVS|TW|TZ|UA|UBANK|UBS|UG|UK|UNICOM|UNIVERSITY|UNO|UOL|UPS|US|UY|UZ|VA|VACATIONS|VANA|VANGUARD|VC|VE|VEGAS|VENTURES|VERISIGN|VERSICHERUNG|VET|VG|VI|VIAJES|VIDEO|VIG|VIKING|VILLAS|VIN|VIP|VIRGIN|VISA|VISION|VIVA|VIVO|VLAANDEREN|VN|VODKA|VOLVO|VOTE|VOTING|VOTO|VOYAGE|VU|WALES|WALMART|WALTER|WANG|WANGGOU|WATCH|WATCHES|WEATHER|WEATHERCHANNEL|WEBCAM|WEBER|WEBSITE|WED|WEDDING|WEIBO|WEIR|WF|WHOSWHO|WIEN|WIKI|WILLIAMHILL|WIN|WINDOWS|WINE|WINNERS|WME|WOLTERSKLUWER|WOODSIDE|WORK|WORKS|WORLD|WOW|WS|WTC|WTF|XBOX|XEROX|XIHUAN|XIN|XXX|XYZ|YACHTS|YAHOO|YAMAXUN|YANDEX|YE|YODOBASHI|YOGA|YOKOHAMA|YOU|YOUTUBE|YT|YUN|ZA|ZAPPOS|ZARA|ZERO|ZIP|ZM|ZONE|ZUERICH|ZW))\b',
    re.IGNORECASE
)

# 线程锁用于打印
print_lock = threading.Lock()


def extract_links(source_code, base_domain=None, black_patterns=None):
    """
    从源代码中提取所有链接，并区分外链和可能的暗链，同时提取纯域名字符串并做黑名单匹配

    参数:
        source_code: 源代码字符串
        base_domain: 基础域名，用于判断是否为外链
        black_patterns: 黑链关键字/域名片段列表，做子串匹配

    返回:
        包含所有链接信息的字典
    """
    # 匹配URL的正则表达式模式
    url_patterns = [
        # 完整URL (http://, https://)
        r'https?://[^\s"\'<>\)]+',
        # a标签中的href
        r'href=["\']([^"\']+)["\']',
        r'href=([^\s>]+)',
        # iframe、img、script等标签中的src
        r'src=["\']([^"\']+)["\']',
        r'src=([^\s>]+)',
        # link标签中的href
        r'<link[^>]*href=["\']([^"\']+)["\']',
        # 脚本中的location、window.open等
        r'location\s*[=:]\s*["\']([^"\']+)["\']',
        r'window\.open\(["\']([^"\']+)["\']',
        r'window\.location\s*=\s*["\']([^"\']+)["\']',
        # 带协议的URL (//开头)
        r'//[^\s"\'<>\)]+',
        # action属性（表单提交地址）
        r'action=["\']([^"\']+)["\']',
        # data属性中的URL
        r'data-[a-z-]+=["\']https?://[^"\']+["\']',
        # CSS中的url()
        r'url\(["\']?([^"\'()]+)["\']?\)',
        # JavaScript中的fetch、ajax等
        r'fetch\(["\']([^"\']+)["\']',
        r'ajax\([^)]*url\s*:\s*["\']([^"\']+)["\']',
        # 相对路径URL (/开头，但不是//或注释)
        r'(?<![:/])/[a-zA-Z0-9][^\s"\'<>]*'
    ]

    all_links = set()
    domain_tokens = set()      # 纯域名字符串
    suspicious_set = set()     # 命中黑名单的 URL/域名

    # 统一黑名单比对（全小写）
    if black_patterns:
        black_patterns = [p.lower() for p in black_patterns]

    def check_suspicious(candidate):
        """命中黑名单关键字则加入 suspicious_set（子串匹配）"""
        if not candidate or not black_patterns:
            return
        c = candidate.lower()
        for p in black_patterns:
            if p in c:
                suspicious_set.add(candidate.strip())
                break

    # 提取所有可能的链接
    for pattern in url_patterns:
        matches = re.findall(pattern, source_code, re.IGNORECASE)
        for match in matches:
            # 如果是捕获组的结果，取第一个分组
            if isinstance(match, tuple) and len(match) > 0:
                match = match[0]
            if match:
                all_links.add(match.strip())

    # 在任意位置提取纯域名字符串（非完整URL）
    for m in DOMAIN_REGEX.findall(source_code):
        if m:
            domain_tokens.add(m.strip().lower())

    # 分类链接
    results = {
        'external_links': [],        # 外链
        'possible_hidden_links': [], # 可能的暗链（通过CSS隐藏等）
        'internal_links': [],        # 内链
        'other_links': [],           # 其他链接
        'domain_tokens': [],         # 纯域名字符串（非完整URL也会记录）
        'suspicious_links': []       # 命中黑名单关键字的 URL/域名
    }

    # 查找可能的暗链模式（隐藏的链接）
    hidden_link_patterns = [
        r'display\s*:\s*none[^>]*href=["\']([^"\']+)["\']',
        r'visibility\s*:\s*hidden[^>]*href=["\']([^"\']+)["\']',
        r'width\s*:\s*0[^>]*height\s*:\s*0[^>]*href=["\']([^"\']+)["\']',
        r'opacity\s*:\s*0[^>]*href=["\']([^"\']+)["\']'
    ]

    hidden_links = set()
    for pattern in hidden_link_patterns:
        matches = re.findall(pattern, source_code, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple) and len(match) > 0:
                match = match[0]
            if match:
                hidden_links.add(match.strip())

    # 基础域名解析（避免每次循环重复解析）
    base_host = None    # 例如 www.xxx.com
    if base_domain:
        try:
            parsed_base = urlparse(base_domain)
            base_host = parsed_base.netloc.lower()
        except Exception:
            base_host = None

    # 处理每个链接
    for link in all_links:
        is_hidden = link in hidden_links

        # 处理相对路径
        full_link = link
        if link.startswith('//'):
            full_link = 'https:' + link
        elif link.startswith('/') and base_domain:
            full_link = base_domain.rstrip('/') + link

        # 黑名单匹配（URL 级别）
        check_suspicious(full_link or link)

        # 判断是否为外链
        is_external = False
        if base_host and full_link.startswith(('http://', 'https://')):
            try:
                parsed_link = urlparse(full_link)
                if parsed_link.netloc:
                    is_external = parsed_link.netloc.lower() != base_host
            except Exception:
                pass

        # 分类
        if is_hidden:
            results['possible_hidden_links'].append(link)
        elif is_external:
            results['external_links'].append(link)
        elif link.startswith(('http://', 'https://', '//')):
            results['internal_links'].append(link)
        else:
            results['other_links'].append(link)

    # 处理纯域名字符串
    for domain in domain_tokens:
        results['domain_tokens'].append(domain)
        check_suspicious(domain)

    # 去重 & 排序
    results['external_links'] = sorted(set(results['external_links']))
    results['possible_hidden_links'] = sorted(set(results['possible_hidden_links']))
    results['internal_links'] = sorted(set(results['internal_links']))
    results['other_links'] = sorted(set(results['other_links']))
    results['domain_tokens'] = sorted(set(results['domain_tokens']))
    results['suspicious_links'] = sorted(suspicious_set)

    return results


def is_source_file(filename, extensions=None, scan_all=False):
    """
    判断文件是否为源代码文件
    """
    if scan_all:
        return True

    if extensions is None:
        extensions = DEFAULT_SOURCE_EXTENSIONS
    ext = os.path.splitext(filename)[1].lower()
    return ext in extensions


def process_single_file(file_path, base_domain, file_num, total_files, black_patterns=None):
    """
    处理单个文件（供多线程使用）
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            source_code = f.read()

        links = extract_links(source_code, base_domain, black_patterns)

        with print_lock:
            print(f"[{file_num}/{total_files}] 已处理: {file_path}")

        return (file_path, links)
    except Exception as e:
        with print_lock:
            print(f"[{file_num}/{total_files}] 处理文件 {file_path} 时出错: {str(e)}")
        return (file_path, None)


def collect_files(directory, recursive=False, extensions=None, scan_all=False):
    """收集需要处理的所有文件"""
    files_to_process = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if is_source_file(file, extensions, scan_all):
                file_path = os.path.join(root, file)
                files_to_process.append(file_path)

        if not recursive:
            break

    return files_to_process


def process_directory(directory, base_domain=None, recursive=False,
                      extensions=None, scan_all=False, max_workers=4,
                      black_patterns=None):
    """
    处理目录中的所有源代码文件（支持多线程）
    """
    results = {}

    # 收集所有需要处理的文件
    files_to_process = collect_files(directory, recursive, extensions, scan_all)
    total_files = len(files_to_process)

    if total_files == 0:
        return results

    scan_mode = "所有文件" if scan_all else f"指定扩展名的文件"
    print(f"找到 {total_files} 个{scan_mode}需要处理")
    print(f"使用 {max_workers} 个线程进行并行处理...\n")

    # 使用线程池处理文件
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(
                process_single_file,
                file_path,
                base_domain,
                idx + 1,
                total_files,
                black_patterns
            ): file_path
            for idx, file_path in enumerate(files_to_process)
        }

        # 收集结果
        for future in as_completed(future_to_file):
            file_path, links = future.result()
            if links is not None:
                results[file_path] = links

    print(f"\n处理完成！共成功处理 {len(results)} 个文件")
    return results


def normalize_url_for_probe(target):
    """将提取到的字符串归一化为可探测的 URL"""
    if not target:
        return None
    t = target.strip()
    if not t:
        return None

    if t.startswith(('http://', 'https://')):
        return t
    if t.startswith('//'):
        return 'http:' + t
    if t.startswith('/'):
        # 相对路径没办法单独探测，这里直接丢弃
        return None
    # 纯域名或其他：默认加 http://
    return 'http://' + t


def probe_single_url(url, timeout=5.0, black_patterns=None, max_body_len=200000):
    """
    对单个 URL 进行 HTTP 探测，返回状态码、部分响应头，以及页面是否命中黑链关键词
    """
    try:
        resp = requests.get(url, timeout=timeout, allow_redirects=True, verify=False)
        headers = dict(resp.headers)
        interesting_headers = {}
        for key in [
            'Server', 'X-Powered-By', 'Location',
            'Set-Cookie', 'Content-Type',
            'Referrer-Policy', 'Content-Security-Policy'
        ]:
            if key in headers:
                interesting_headers[key] = headers[key]

        # 在页面内容中匹配黑名单关键词
        hits = []
        if black_patterns:
            try:
                body = resp.text
            except UnicodeDecodeError:
                body = resp.content.decode('utf-8', errors='ignore')

            body_lower = body[:max_body_len].lower()
            for p in black_patterns:
                if p and p in body_lower:
                    hits.append(p)

        return {
            'status_code': resp.status_code,
            'final_url': resp.url,
            'headers': interesting_headers,
            'body_keyword_hits': sorted(set(hits)),  # 这里保存命中的关键词
        }
    except Exception as e:
        return {'error': str(e)}



def probe_suspicious_links(all_results, black_patterns, max_workers=8, timeout=5.0):
    """
    对疑似黑链 / 隐藏链接 / 外链 / 域名字符串进行 HTTP 探测

    - 探测对象包括：
        * suspicious_links（静态已经命中的）
        * possible_hidden_links（隐藏链接）
        * external_links（所有外链）
        * domain_tokens（源码中出现的纯域名）
    - 如果页面 Body 中命中黑名单关键词，则把对应链接回填到各文件的 suspicious_links 中
    """
    if requests is None:
        print("\n[!] 未安装 requests 库，无法进行 HTTP 探测。请先安装：pip install requests")
        return None

    # 统一将黑名单转为小写，以便匹配
    lower_black = [p.lower() for p in (black_patterns or [])]

    # URL -> {(file_path, 原始字符串)} 映射，方便回填到具体文件
    url_to_sources = {}
    for file_path, links in all_results.items():
        # 这些字段里的内容都作为探测目标
        for key in ('suspicious_links', 'possible_hidden_links', 'external_links', 'domain_tokens'):
            for item in links.get(key, []):
                u = normalize_url_for_probe(item)
                if not u:
                    continue
                url_to_sources.setdefault(u, set()).add((file_path, item))

    targets = list(url_to_sources.keys())
    if not targets:
        print("\n没有需要进行 HTTP 探测的链接。")
        return {}

    print(f"\n开始对 {len(targets)} 个链接进行 HTTP 探测（超时 {timeout}s，线程 {max_workers}）...")

    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(probe_single_url, url, timeout, lower_black): url
            for url in targets
        }
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            info = future.result()
            results[url] = info

            # 控制台输出
            with print_lock:
                if 'error' in info:
                    print(f"[探测失败] {url} -> {info['error']}")
                else:
                    hits = info.get('body_keyword_hits') or []
                    if hits:
                        print(f"[探测命中关键词] {url} -> {info['status_code']} 命中: {', '.join(sorted(set(hits)))}")
                    else:
                        print(f"[探测成功] {url} -> {info['status_code']} {info.get('final_url', '')}")

            # 如果页面命中黑链关键词，则回填到对应文件的 suspicious_links 中
            hits = info.get('body_keyword_hits') or []
            if hits:
                for file_path, raw in url_to_sources.get(url, []):
                    existing = set(all_results[file_path].get('suspicious_links', []))
                    existing.add(raw)
                    all_results[file_path]['suspicious_links'] = sorted(existing)

    return results



def format_results(all_results, probe_results=None):
    """格式化所有文件的分析结果为字符串（可附带 HTTP 探测结果）"""

    output = []
    total_hidden = 0
    total_external = 0
    total_internal = 0
    total_other = 0
    total_domain_tokens = 0
    total_suspicious = 0

    # 首先统计总数
    for file_path, links in all_results.items():
        total_hidden += len(links['possible_hidden_links'])
        total_external += len(links['external_links'])
        total_internal += len(links['internal_links'])
        total_other += len(links['other_links'])
        total_domain_tokens += len(links.get('domain_tokens', []))
        total_suspicious += len(links.get('suspicious_links', []))

    output.append("=" * 80)
    output.append("URL提取分析报告")
    output.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("=" * 80)
    output.append(f"总结果: 共分析 {len(all_results)} 个文件")
    output.append(f"发现 {total_hidden} 个可能的暗链")
    output.append(f"发现 {total_external} 个外链")
    output.append(f"发现 {total_internal} 个内链")
    output.append(f"发现 {total_other} 个其他链接")
    output.append(f"发现 {total_domain_tokens} 个疑似域名字符串（包括非完整URL形式）")
    if total_suspicious:
        output.append(f"其中 {total_suspicious} 个命中黑名单关键字（疑似黑链）")
    output.append("=" * 80)
    output.append("")

    # 逐个文件显示结果
    for file_path, links in all_results.items():
        output.append(f"文件: {file_path}")

        output.append(f"  可能的暗链 ({len(links['possible_hidden_links'])}):")
        if links['possible_hidden_links']:
            for link in links['possible_hidden_links']:
                output.append(f"    - {link}")
        else:
            output.append("    (无)")

        output.append(f"  外链 ({len(links['external_links'])}):")
        if links['external_links']:
            for link in links['external_links']:
                output.append(f"    - {link}")
        else:
            output.append("    (无)")

        output.append(f"  内链 ({len(links['internal_links'])}):")
        if links['internal_links']:
            for link in links['internal_links']:
                output.append(f"    - {link}")
        else:
            output.append("    (无)")

        output.append(f"  其他链接 ({len(links['other_links'])}):")
        if links['other_links']:
            for link in links['other_links']:
                output.append(f"    - {link}")
        else:
            output.append("    (无)")

        domain_tokens = links.get('domain_tokens', [])
        output.append(f"  代码中疑似域名字符串 ({len(domain_tokens)}):")
        if domain_tokens:
            for d in domain_tokens:
                output.append(f"    - {d}")
        else:
            output.append("    (无)")

        suspicious = links.get('suspicious_links', [])
        output.append(f"  命中黑名单关键字的可疑链接/域名 ({len(suspicious)}):")
        if suspicious:
            for s in suspicious:
                output.append(f"    - {s}")
        else:
            output.append("    (无)")

        output.append("-" * 80)
        output.append("")

    # 附加 HTTP 探测结果
    if probe_results:
        output.append("=" * 80)
        output.append("HTTP 探测结果（按可疑URL归并）")
        output.append("=" * 80)
        for url in sorted(probe_results.keys()):
            info = probe_results[url]
            output.append(f"URL: {url}")
            if 'error' in info:
                output.append(f"  探测失败: {info['error']}")
            else:
                output.append(f"  状态码: {info['status_code']}")
                final_url = info.get('final_url')
                if final_url and final_url != url:
                    output.append(f"  最终跳转URL: {final_url}")
                hits = info.get('body_keyword_hits') or []
                if hits:
                    output.append("  页面命中黑链关键词: " + ", ".join(sorted(set(hits))))
                headers = info.get('headers') or {}
                if headers:
                    output.append("  关键响应头:")
                    for k, v in headers.items():
                        output.append(f"    {k}: {v}")
            output.append("-" * 80)
            output.append("")

    return "\n".join(output)


def print_results(all_results, probe_results=None):
    """打印所有文件的分析结果"""
    output = format_results(all_results, probe_results)
    print(output)


def save_results_to_file(all_results, output_file, probe_results=None):
    """将结果保存到txt文件"""
    try:
        output = format_results(all_results, probe_results)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"\n结果已保存到: {os.path.abspath(output_file)}")
        return True
    except Exception as e:
        print(f"保存文件时出错: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='提取目录中所有源代码文件的暗链和外链地址（支持多线程加速，并可对疑似黑链进行HTTP探测）',
        epilog='示例:\n'
               '  %(prog)s -d /path/to/dir                  # 扫描指定目录\n'
               '  %(prog)s --all                            # 扫描所有文件（不限扩展名）\n'
               '  %(prog)s -e html,php,js                   # 只扫描指定扩展名\n'
               '  %(prog)s -t 8                             # 使用8个线程加速\n'
               '  %(prog)s -b https://example.com           # 指定基础域名识别外链\n'
               '  %(prog)s -bl blacklist.txt                # 在内置关键词基础上追加黑链域名/关键字列表\n'
               '  %(prog)s --probe                          # 对疑似黑链进行HTTP探测\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # 基本选项
    parser.add_argument('-d', '--directory', default='.',
                        help='要处理的目录路径，默认为当前目录')
    parser.add_argument('-b', '--base-domain',
                        help='基础域名，用于判断是否为外链（如 https://example.com）')
    parser.add_argument('-o', '--output',
                        help='输出文件路径，默认自动生成带时间戳的文件名')
    parser.add_argument('--no-timestamp', action='store_true',
                        help='输出文件名不包含时间戳')

    # 递归选项
    parser.add_argument('-r', '--recursive', action='store_true', default=True,
                        help='是否递归处理子目录（默认启用）')
    parser.add_argument('-nr', '--no-recursive', action='store_true',
                        help='不递归处理子目录')

    # 扫描模式选项（互斥）
    scan_group = parser.add_mutually_exclusive_group()
    scan_group.add_argument('-e', '--extensions',
                            help='逗号分隔的文件扩展名（如: html,php,js）或（.html,.php,.js）')
    scan_group.add_argument('-a', '--all', action='store_true',
                            help='扫描所有文件（不限扩展名，可能较慢）')

    # 性能选项
    parser.add_argument('-t', '--threads', type=int, default=4,
                        help='线程数（默认为4，建议范围：1-16）')

    # 黑链关键字 / 域名片段列表文件（追加）
    parser.add_argument('-bl', '--blacklist',
                        help='黑链域名/关键字列表文件，每行一个，支持子串匹配（如：ceshi.xyz、ppp.qr 等），会在内置关键词基础上追加')

    # HTTP 探测相关参数
    parser.add_argument('--probe', action='store_true',
                        help='对命中的疑似黑链/隐藏链接进行HTTP探测（需要安装requests库）')
    parser.add_argument('--probe-timeout', type=float, default=5.0,
                        help='HTTP探测超时时间（秒），默认5秒')
    parser.add_argument('--probe-workers', type=int, default=8,
                        help='HTTP探测并发线程数，默认8')

    args = parser.parse_args()

    # 处理输出文件名，添加时间戳
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if args.no_timestamp:
            output_file = 'url_extraction_results.txt'
        else:
            output_file = f'url_extraction_results_{timestamp}.txt'

    # 验证线程数
    if args.threads < 1:
        args.threads = 1
    elif args.threads > 32:
        print(f"警告：线程数 {args.threads} 过大，已限制为 32")
        args.threads = 32

    # 处理递归选项
    recursive = args.recursive and not args.no_recursive

    # 处理扫描模式
    scan_all = args.all
    extensions = None

    if args.extensions:
        extensions = {ext.strip().lower() for ext in args.extensions.split(',')}
        extensions = {ext if ext.startswith('.') else '.' + ext for ext in extensions}

    # 构造黑名单关键字/域名片段列表：内置 + 文件追加
    black_patterns = list(BLACKLINK_KEYWORDS)
    if args.blacklist:
        try:
            with open(args.blacklist, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        lp = line.lower()
                        if lp not in [p.lower() for p in black_patterns]:
                            black_patterns.append(lp)
        except Exception as e:
            print(f"读取黑名单文件失败: {e}")

    # 打印配置信息
    print("=" * 60)
    print("URL提取工具 - 配置信息")
    print("=" * 60)
    print(f"目标目录: {os.path.abspath(args.directory)}")
    print(f"递归扫描: {'是' if recursive else '否'}")

    if scan_all:
        print("扫描模式: 扫描所有文件（不限扩展名）")
    elif extensions:
        print(f"扫描模式: 指定扩展名 {', '.join(sorted(extensions))}")
    else:
        print(f"扫描模式: 默认扩展名（{len(DEFAULT_SOURCE_EXTENSIONS)} 种）")

    print(f"线程数量: {args.threads}")
    print(f"输出文件: {os.path.abspath(output_file)}")
    if args.base_domain:
        print(f"基础域名: {args.base_domain}")
    print(f"内置黑链关键词数量: {len(BLACKLINK_KEYWORDS)}")
    if args.blacklist:
        print(f"外部黑名单文件: {os.path.abspath(args.blacklist)}")
    print(f"总黑名单关键字/域名片段数量（合并后）: {len(black_patterns)}")
    print(f"HTTP探测: {'开启' if args.probe else '关闭'}")
    if args.probe:
        print(f"  探测线程数: {args.probe_workers}")
        print(f"  探测超时时间: {args.probe_timeout} 秒")
    print("=" * 60)
    print()

    # 开始处理
    all_results = process_directory(
        args.directory,
        base_domain=args.base_domain,
        recursive=recursive,
        extensions=extensions,
        scan_all=scan_all,
        max_workers=args.threads,
        black_patterns=black_patterns
    )

    probe_results = None
    if all_results and args.probe:
        probe_results = probe_suspicious_links(
            all_results,
            black_patterns,
            max_workers=args.probe_workers,
            timeout=args.probe_timeout
        )

    # 显示和保存结果
    if all_results:
        print_results(all_results, probe_results)
        save_results_to_file(all_results, output_file, probe_results)
    else:
        print("未找到任何文件进行处理")


if __name__ == "__main__":
    main()
