import os
import re
import win32api

CATEGORY_RULES = {
    "01. Разработка и Код": {
        "icon": "💻",
        "keywords": [
            "code", "studio", "develop", "compiler", "ide", "git", "bash", "debug", "sdk", 
            "docker", "wsl", "python", "node", "java", "jadx", "apk", "vcpkg", "postman", 
            "sublime", "pycharm", "intellij", "clion", "webstorm", "terminal", "powershell", 
            "sandbox", "rust", "golang", "gradle", "llvm", "visual studio", "assembly", 
            "cargo", "cmake", "ninja", "msbuild", "windbg", "ghidra", "ida", "rider", 
            "goland", "datagrip", "rubymine", "phpstorm", "eclipse", "netbeans", "unity", 
            "unreal", "godot"
        ],
        "default_desc": "Среда разработки, компилятор или инструмент программирования"
    },
    "02. Базы данных": {
        "icon": "🗄️",
        "keywords": [
            "sql", "database", "dbeaver", "postgres", "mysql", "mariadb", "sqlite", "redis", 
            "mongodb", "pgadmin", "heidisql", "db browser", "navicat", "data grip", "workbench", 
            "dbms", "субд", "couchbase", "cassandra", "clickhouse", "dbshell", "psql", 
            "compass", "redisinsight", "tableplus", "robo 3t"
        ],
        "default_desc": "Инструмент управления и клиент баз данных (СУБД)"
    },
    "03. Нейросети и ИИ": {
        "icon": "🤖",
        "keywords": [
            "ai", "gpt", "llm", "neural", "antigravity", "lm studio", "opencode", "ollama", 
            "chatgpt", "claude", "gemini", "perplexity", "comet", "diffusion", "copilot", 
            "cursor", "deepseek", "jan", "anythingllm", "stable diffusion", "comfyui", 
            "webui", "whisper", "open-webui", "lora", "fooocus", "invokeai", "chatbox", 
            "gpt4all", "continue"
        ],
        "default_desc": "AI-ассистент, локальная нейросеть или инструмент работы с LLM"
    },
    "04. Интернет и Браузеры": {
        "icon": "🌐",
        "keywords": [
            "browser", "chrome", "firefox", "edge", "opera", "brave", "vivaldi", "tor", 
            "yandex", "waterfox", "librewolf", "интернет", "браузер", "chromium", "safari", 
            "arc", "sidekick", "gx"
        ],
        "default_desc": "Веб-браузер для доступа в сеть Интернет"
    },
    "05. Связь и Мессенджеры": {
        "icon": "💬",
        "keywords": [
            "telegram", "discord", "zoom", "teams", "teamspeak", "skype", "slack", "viber", 
            "whatsapp", "signal", "element", "voice", "мессенджер", "видеосвязь", "mattermost", 
            "icq", "tox", "session", "viber"
        ],
        "default_desc": "Мессенджер, голосовой чат или сервис видеоконференций"
    },
    "06. Удаленный доступ и Сеть": {
        "icon": "🔒",
        "keywords": [
            "vpn", "wireguard", "amnezia", "netbird", "anydesk", "teamviewer", "rustdesk", 
            "termius", "mobaxterm", "putty", "ssh", "rdp", "remote desktop", "ftp", "sftp", 
            "filezilla", "airexplorer", "syncthing", "wireshark", "fiddler", "proxy", "openvpn", 
            "zerotier", "tailscale", "cloud", "onedrive", "dropbox", "v2ray", "xray", "shadowsocks", 
            "clash", "nekoray", "sing-box", "winscp", "ultraviewer", "proxifier"
        ],
        "default_desc": "Удалённое управление ПК, сетевой протокол или VPN клиент"
    },
    "07. Мультимедиа и Звук": {
        "icon": "🎨",
        "keywords": [
            "vlc", "player", "music", "audio", "video", "sound", "media", "jellyfin", "plex", 
            "encoder", "shutter", "downloader", "zona", "sonarr", "jackett", "torrent", 
            "utorrent", "qbittorrent", "clipchamp", "premiere", "audacity", "fl studio", 
            "reaper", "obs", "stream", "komi", "музыка", "плеер", "potplayer", "mpv", 
            "aimp", "foobar", "photoshop", "lightroom", "gimp", "figma", "blender", "davinci", 
            "handbrake", "audition", "яндекс музыка", "spotify", "after effects", "illustrator", 
            "capcut", "ableton", "cubase", "krita", "paint.net", "inkscape"
        ],
        "default_desc": "Воспроизведение, обработка аудио/видео или графический редактор"
    },
    "08. Офис и Документы": {
        "icon": "📄",
        "keywords": [
            "word", "excel", "powerpoint", "onenote", "outlook", "access", "publisher", 
            "office", "acrobat", "pdf", "reader", "obsidian", "notion", "todo", "calendar", 
            "alarm", "clock", "документ", "заметки", "таблицы", "презентации", "будильник", 
            "libreoffice", "foxit", "sumatra", "evernote", "calibre", "typora", "logseq"
        ],
        "default_desc": "Офисный редактор, работа с документами или планировщик"
    },
    "09. Компьютерные игры": {
        "icon": "🕹️",
        "keywords": [
            "game", "genshin", "poe", "path of exile", "dota", "manor lords", "subnautica", 
            "sky", "alters", "forest", "flipper", "singularity", "lineage", "dark dusk", 
            "l2", "destorus", "craft", "minecraft", "survivor", "cyberpunk", "witcher", 
            "counter-strike", "cs2", "valorant", "gta", "baldurs", "elden ring", "roblox"
        ],
        "default_desc": "Компьютерная игра"
    },
    "10. Игровой софт и Лаунчеры": {
        "icon": "🎮",
        "keywords": [
            "launcher", "overwolf", "dotaplus", "poe overlay", "pob", "path of building", 
            "ludusavi", "crafter", "cheat engine", "nexus mods", "vortex", "gog galaxy", 
            "epic games", "hydra", "hoyoplay", "battle.net", "ea app", "ubisoft", "playnite", 
            "steam", "mod organizer", "razer cortex", "curseforge"
        ],
        "default_desc": "Игровой лаунчер, оверлей или утилита для моддинга игр"
    },
    "11. Железо и Мониторинг": {
        "icon": "⚙️",
        "keywords": [
            "aida", "crystaldisk", "fancontrol", "samsung magician", "kies", "tuning", 
            "logitech", "ghub", "logitune", "capture", "hyperx", "ngenuity", "nvidia", 
            "geforce", "broadcast", "afterburner", "hwinfo", "cpu-z", "gpu-z", "radeon", 
            "benchmark", "температура", "железо", "вентиляторы", "corsair", "icue", "furmark", 
            "core temp", "speccy", "asrock", "cinebench"
        ],
        "default_desc": "Диагностика компонентов ПК, кулеров, дисков и периферии"
    },
    "12. Система и Обслуживание": {
        "icon": "🛠️",
        "keywords": [
            "windhawk", "powertoys", "flow launcher", "bcuninstaller", "uninstaller", 
            "patch my pc", "shutup", "oldnewexplorer", "windirstat", "7-zip", "zip", 
            "rar", "stellar", "recovery", "doff", "terminal", "regedit", "taskmgr", 
            "diskmgmt", "services", "tweaker", "cleaner", "оптимизация", "реестр", 
            "диспетчер", "powershell", "cmd", "explorer", "rufus", "bleachbit", "autoruns", 
            "process hacker", "everything", "peazip", "total commander", "far manager", 
            "etcher", "ventoy"
        ],
        "default_desc": "Системная утилита, оптимизация, твикер или инструмент Windows"
    }
}

EXACT_DESCRIPTIONS = {
    # 01. Разработка
    "Visual Studio Code": "Популярный расширяемый редактор исходного кода от Microsoft",
    "Android Studio": "Официальная IDE от Google для разработки приложений под Android",
    "Docker Desktop": "Платформа для сборки, запуска и контейнеризации приложений",
    "Git Bash": "Командная оболочка Bash с поддержкой системы контроля версий Git",
    "Git GUI": "Графический интерфейс для управления репозиториями Git",
    "Postman": "Мощная среда для тестирования, отладки и документирования API",
    "JADX GUI": "Декомпилятор APK и DEX-файлов Android в исходный читаемый Java-код",
    "APK Editor Studio": "Визуальный редактор манифестов, иконок и ресурсов Android APK",
    "Android Explorer": "Менеджер файловой системы и установленных пакетов Android",
    "WSL (Linux)": "Подсистема Windows для запуска полноценного дистрибутива Linux",
    "WSL Settings": "Графическая панель настройки виртуализации и памяти для WSL",
    "Windows Sandbox": "Изолированная безопасная песочница для тестирования подозрительных файлов",
    "Python 3.13": "Интерпретатор языка программирования Python 3.13",
    "IDLE (Python 3.13)": "Встроенная легковесная среда разработки Python",
    "Developer Command Prompt for VS": "Командная строка с переменными окружения компилятора C/C++ Visual Studio",
    "Developer PowerShell for VS": "PowerShell с настроенными путями к инструментам сборки Visual Studio",
    "Visual Studio Installer": "Установщик и менеджер компонентов и рабочих нагрузок Visual Studio",
    "PyCharm": "Профессиональная IDE для разработки на Python от JetBrains",
    "IntelliJ IDEA": "Мощная среда разработки для Java и Kotlin от JetBrains",
    "Sublime Text": "Легковесный и сверхбыстрый текстовый редактор с подсветкой кода",
    "Cursor": "Современный редактор кода со встроенным ИИ-ассистентом на базе VS Code",
    "Unity": "Движок для разработки 2D и 3D игр и интерактивных приложений",
    "Godot": "Свободный и легковесный кроссплатформенный игровой движок",

    # 02. Базы данных
    "DBeaver": "Универсальный SQL-клиент для любых баз данных (PostgreSQL, MySQL, SQLite, Oracle)",
    "HeidiSQL": "Быстрый и удобный графический менеджер для MySQL, MariaDB, PostgreSQL и SQLite",
    "pgAdmin 4": "Официальная веб-панель администрирования баз данных PostgreSQL",
    "SQL Shell (psql)": "Интерактивная консольная утилита для работы с PostgreSQL",
    "SQLiteStudio": "Интуитивный менеджер и редактор локальных баз данных SQLite",
    "DataGrip": "Интеллектуальная IDE для разработчиков баз данных и администраторов от JetBrains",
    "Navicat": "Премиальный графический инструмент для проектирования и управления базами данных",
    "MongoDB Compass": "Официальный GUI для визуального исследования и запросов к базам MongoDB",
    "RedisInsight": "Графический интерфейс для визуализации данных и мониторинга Redis",

    # 03. Нейросети и ИИ
    "Antigravity": "Интеллектуальная среда разработки и агентный ИИ-помощник от DeepMind",
    "LM Studio": "Запуск и офлайн-чат с любыми открытыми большими языковыми моделями (LLM)",
    "Comet (Perplexity AI Browser)": "Умный браузер со встроенным поисковым интеллектом Perplexity AI",
    "OpenCode": "AI-инструмент для глубокого анализа, рефакторинга и генерации кода",
    "Ollama": "Быстрый запуск и управление локальными нейросетями в терминале и по API",
    "Jan": "Открытая локальная альтернатива ChatGPT с офлайн-моделями",
    "AnythingLLM": "Полнофункциональный приватный AI-чат с поддержкой RAG и документов",
    "ChatGPT": "Официальное настольное приложение ChatGPT от OpenAI",

    # 04. Интернет и Браузеры
    "Google Chrome": "Самый популярный быстрый веб-браузер от компании Google",
    "Mozilla Firefox": "Независимый браузер с акцентом на приватность и блокировку трекеров",
    "Firefox (Приватный режим)": "Запуск Firefox в режиме инкогнито без сохранения истории и куки",
    "Microsoft Edge": "Современный браузер на движке Chromium с функциями безопасности Microsoft",
    "Brave": "Защищенный браузер со встроенной блокировкой рекламы и трекеров",
    "Opera": "Веб-браузер со встроенным VPN, блокировщиком рекламы и боковой панелью",
    "Opera GX": "Специализированный браузер для геймеров с контролем нагрузки на CPU и RAM",
    "Tor Browser": "Анонимный браузер для безопасного серфинга через луковую маршрутизацию",

    # 05. Связь и Мессенджеры
    "Telegram Desktop": "Быстрый защищенный мессенджер с облачным хранением и каналами",
    "Discord": "Платформа для голосового, текстового и видеообщения с сообществами",
    "Zoom": "Популярный сервис для проведения видеоконференций и онлайн-звонков",
    "Microsoft Teams": "Корпоративный коммуникатор для совместной работы и совещаний",
    "TeamSpeak": "Низколатентный голосовой чат для командных онлайн-игр",
    "WhatsApp": "Официальный клиент популярного мобильного мессенджера для ПК",
    "Skype": "Программа для видеозвонков и чатов от компании Microsoft",

    # 06. Удаленный доступ и Сеть
    "AnyDesk": "Сверхбыстрое подключение к удаленному рабочему столу с минимальной задержкой",
    "AmneziaVPN": "Клиент персонального VPN с защитой от блокировок и обходом цензуры",
    "Netbird (VPN)": "P2P-сеть и приватный VPN на базе WireGuard с нулевой настройкой",
    "AirExplorer (Облака и WebDAV)": "Единый файловый менеджер для облачных дисков (Google Drive, Mega, WebDAV)",
    "Syncthing (Синхронизация)": "Децентрализованная синхронизация файлов между ПК и смартфонами",
    "Termius (SSH)": "Современный SSH/SFTP клиент с синхронизацией сессий и красивым терминалом",
    "MobaXterm": "Многофункциональный терминал со встроенным X11-сервером, SSH, RDP и VNC",
    "FileZilla FTP Client": "Надежный двухпанельный FTP/SFTP клиент для передачи файлов на сервер",
    "Подключение к удаленному рабочему столу": "Встроенный Windows клиент для протокола RDP",
    "OneDrive": "Облачное хранилище файлов от Microsoft, интегрированное с Windows",
    "Wireshark": "Профессиональный сниффер и анализатор пакетов сетевых протоколов",
    "RustDesk": "Бесплатная открытая альтернатива TeamViewer для удаленного доступа к ПК",
    "WinSCP": "Популярный SFTP/FTP клиент для передачи файлов и удаленного управления",

    # 07. Мультимедиа и Звук
    "VLC media player": "Универсальный медиаплеер, воспроизводящий любые форматы видео и аудио",
    "Shutter Encoder": "Профессиональный транскодер и конвертер любых аудио и видео форматов",
    "Jellyfin Media Player": "Настольный плеер для подключения к домашнему серверу Jellyfin",
    "Jellyfin Server (Tray)": "Фоновая служба медиасервера для стриминга библиотеки фильмов и музыки",
    "Jackett": "Прокси-сервер поиска торрентов, агрегирующий десятки трекеров для Sonarr/Radarr",
    "Sonarr": "Автоматизированная система мониторинга, скачивания и каталогизации сериалов",
    "Open Video Downloader": "Графическая утилита (yt-dlp) для скачивания видео с YouTube и сотен сайтов",
    "uTorrent Web": "Веб-интерфейс торрент-клиента для скачивания файлов через браузер",
    "Zona": "Каталог и онлайн-кинотеатр для просмотра фильмов и сериалов",
    "Komi-Store (Медиа каталог)": "Приложение для каталогизации и просмотра медиа-контента",
    "Яндекс Музыка": "Официальный клиент стриминга треков, подкастов и персональной Моей Волны",
    "Clipchamp (Видеоредактор)": "Легковесный видеоредактор от Microsoft с шаблонами и эффектами",
    "Blender": "Мощнейший бесплатный 3D-редактор, визуализатор и анимационный пакет",
    "Figma": "Профессиональный редактор интерфейсов и векторной графики для дизайнеров",
    "Photoshop": "Мировой стандарт растровой графики и ретуши фотографий от Adobe",
    "Audacity": "Бесплатный аудиоредактор и мультитрековый рекордер звука",
    "OBS Studio": "Профессиональная программа для записи видео и прямых трансляций",
    "DaVinci Resolve": "Профессиональный видеомонтаж, визуальные эффекты и цветокоррекция",
    "qBittorrent": "Быстрый торрент-клиент без рекламы с поиском и контролем скорости",

    # 08. Офис и Документы
    "Microsoft Word": "Текстовый процессор для создания и форматирования документов",
    "Microsoft Excel": "Мощная программа для работы с электронными таблицами и аналитикой",
    "Microsoft PowerPoint": "Создание и демонстрация интерактивных презентаций",
    "Microsoft Access": "Система управления реляционными базами данных из пакета Office",
    "Microsoft OneNote": "Цифровая записная книжка для ведения заметок и конспектов",
    "Microsoft Outlook": "Почтовый клиент, органайзер, календарь и менеджер контактов",
    "Microsoft Publisher": "Приложение для верстки макетов буклетов, визиток и брошюр",
    "Adobe Acrobat": "Профессиональный инструмент для создания, редактирования и подписи PDF",
    "Free Alarm Clock (Будильник)": "Простой настраиваемый будильник и таймер для Windows",
    "Obsidian": "Локальная база знаний и система ведения заметок на базе Markdown",
    "Notion": "Универсальное рабочее пространство для заметок, баз данных и задач",

    # 10. Игровой софт и Лаунчеры
    "Steam": "Крупнейшая платформа цифровой дистрибуции игр и сообщества от Valve",
    "Epic Games Launcher": "Игровой лаунчер от Epic Games с магазином и Unreal Engine",
    "GOG GALAXY": "Игровой клиент от CD Projekt RED для игр без DRM-защиты",
    "Playnite": "Универсальный менеджер и лаунчер всей библиотеки игр с разных платформ",
    "Hydra Launcher": "Альтернативный лаунчер для поиска и каталогизации игр",
    "HoYoPlay (Лаунчер Genshin)": "Единый официальный лаунчер игр HoYoverse (Genshin, Star Rail, ZZZ)",
    "Path of Building (PoE 1)": "Глубокий калькулятор пассивного дерева и билдов для Path of Exile 1",
    "Path of Building (PoE 2)": "Калькулятор билдов, характеристик и экипировки для Path of Exile 2",
    "PoE Overlay": "Внутриигровой оверлей для быстрой оценки цен предметов в Path of Exile",
    "PoE Overlay II": "Оверлей нового поколения для трейда и подсказок в Path of Exile",
    "Overwolf": "Платформа для запуска внутриигровых оверлеев и игровых модов",
    "DotaPlus": "Оверлей от Overwolf с подсказками по пикам и статистике игроков в Dota 2",
    "Ludusavi (Бэкап сохранений)": "Автоматическое резервное копирование игровых сохранений для сотен игр",
    "Crafter (Калькулятор крафта L2)": "Утилита для расчета рецептов и стоимости крафта в Lineage 2",
    "Crafter Editor": "Редактор базы предметов и ресурсов для калькулятора Crafter",

    # 11. Железо и Мониторинг
    "AIDA64 Extreme": "Комплексная диагностика аппаратной части ПК, стресс-тесты и сенсоры",
    "CrystalDiskInfo": "Мониторинг здоровья, температуры и S.M.A.R.T. параметров SSD и жестких дисков",
    "FanControl (Управление вентиляторами)": "Продвинутая настройка кривых скорости вращения вентиляторов корпуса и GPU",
    "Logitech G HUB": "Настройка подсветки, DPI и макросов для игровых мышей и клавиатур Logitech",
    "Logitech Capture": "Программа для видеозаписи и настройки вебкамер Logitech",
    "LogiTune": "Управление и обновление гарнитур, наушников и веб-камер Logitech",
    "HyperX NGENUITY": "Панель настройки RGB-подсветки и профилей девайсов HyperX",
    "NVIDIA App": "Современный центр управления видеокартой GeForce, драйверами и оптимизацией",
    "NVIDIA Broadcast": "ИИ-шумоподавление микрофона и замена фона вебкамеры на базе RTX",
    "Панель управления NVIDIA": "Классическая панель тонкой настройки параметров 3D и дисплея",
    "Samsung Magician": "Утилита для тестирования скорости, оптимизации и обновления прошивок SSD Samsung",
    "Samsung Kies": "Синхронизация данных и управление старыми смартфонами Samsung",
    "A-Tuning (ASRock)": "Фирменная утилита ASRock для разгона, мониторинга и настройки материнской платы",
    "MSI Afterburner": "Разгон видеокарты, мониторинг температур и оверлей FPS в играх",
    "CPU-Z": "Точные технические характеристики процессора, материнской платы и ОЗУ",
    "GPU-Z": "Детальная информация о характеристиках, частотах и датчиках видеокарты",

    # 12. Система и Обслуживание
    "Windhawk": "Платформа модульной кастомизации интерфейса и панели задач Windows",
    "PowerToys": "Набор мощных утилит от Microsoft (FancyZones, ColorPicker, Text Extractor и др.)",
    "Flow Launcher": "Быстрый лаунчер для поиска файлов, приложений и веб-запросов",
    "BCUninstaller (Деинсталлятор софта)": "Массовое удаление программ с поиском мусора и очисткой реестра",
    "Patch My PC Home Updater": "Автоматическое обновление установленного бесплатного софта в 1 клик",
    "O&O ShutUp10++ (Приватность)": "Отключение шпионской телеметрии и настройка приватности Windows",
    "OldNewExplorer (Настройка проводника)": "Возврат классического удобного вида папок и проводника Windows",
    "WinDirStat (Анализ занятого места)": "Визуальная карта диска для поиска самых больших файлов и папок",
    "7-Zip File Manager": "Быстрый архиватор с высокой степенью сжатия (.7z, .zip, .rar, .tar)",
    "Stellar Phoenix Data Recovery": "Программа для глубокого восстановления удаленных файлов с дисков и флешек",
    "Windows Terminal": "Современное окно терминала с вкладками для PowerShell, CMD и WSL",
    "Winstep Nexus": "Анимированная панель быстрого запуска в стиле macOS Dock",
    "Выключение монитора (doff)": "Мгновенное погашение экранов мониторов горячей клавишей без спящего режима",
    "Диспетчер задач": "Мониторинг запущенных процессов, нагрузки на CPU/RAM/диск и автозагрузки",
    "Диспетчер устройств": "Управление драйверами и подключенными аппаратными устройствами ПК",
    "Монитор производительности": "Глубокий системный анализ метрик производительности Windows",
    "Проверка работоспособности ПК": "Утилита проверки совместимости оборудования и состояния системы",
    "Редактор реестра": "Просмотр и редактирование ключей системного реестра Windows",
    "Службы Windows": "Управление фоновыми службами и системными демонами Windows",
    "Управление дисками": "Разметка томов, форматирование и управление разделами накопителей"
}

JUNK_KEYWORDS = [
    "uninstall", "unins000", "деинстал", "удалить", "удаление",
    "crashpad", "crashhandler", "feedback", "updater.exe", "update.exe",
    "manual", "readme", "license", "help", "documentation", "справка", 
    "setup.exe", "installer.exe", "download", "helper"
]

def is_junk_or_uninstaller(name, path=""):
    combined = f"{name} {path}".lower()
    for kw in JUNK_KEYWORDS:
        if kw in combined:
            if "patch my pc" in combined or "apk editor" in combined:
                continue
            return True
    return False

def get_pe_file_description(file_path):
    if not file_path or not os.path.exists(file_path):
        return ""
    try:
        sub_block = r"\StringFileInfo\040904b0\FileDescription"
        try:
            desc = win32api.GetFileVersionInfo(file_path, sub_block)
            if desc and desc.strip():
                return desc.strip()
        except Exception:
            pass
        sub_block_ru = r"\StringFileInfo\041904b0\FileDescription"
        try:
            desc = win32api.GetFileVersionInfo(file_path, sub_block_ru)
            if desc and desc.strip():
                return desc.strip()
        except Exception:
            pass
    except Exception:
        pass
    return ""

def classify_app(name, path="", desc=""):
    combined = f"{name} {path} {desc}".lower()
    
    # Check if exact match exists in EXACT_DESCRIPTIONS
    for exact_k in EXACT_DESCRIPTIONS:
        if exact_k.lower() in name.lower():
            for cat, rules in CATEGORY_RULES.items():
                for kw in rules["keywords"]:
                    if kw in exact_k.lower() or kw in combined:
                        pass
    
    scores = {}
    for cat, rules in CATEGORY_RULES.items():
        score = 0
        for kw in rules["keywords"]:
            if kw in combined:
                score += 4 if kw in name.lower() else 1
        if score > 0:
            scores[cat] = score
            
    if scores:
        best_cat = max(scores.items(), key=lambda x: x[1])[0]
        return best_cat
        
    return "12. Система и Обслуживание"

def get_app_description(name, category, path=""):
    for k, desc in EXACT_DESCRIPTIONS.items():
        if k.lower() == name.lower() or k.lower() in name.lower():
            return desc
            
    pe_desc = get_pe_file_description(path) if path else ""
    if pe_desc and len(pe_desc) > 3:
        return f"{pe_desc}"
        
    if category in CATEGORY_RULES:
        return CATEGORY_RULES[category]["default_desc"]
        
    return "Пользовательское приложение Windows"

APP_SEARCH_ALIASES = {
    # 01. Разработка
    "docker": ["докер", "контейнер", "докер десктоп", "контейнеризация", "docker desktop"],
    "visual studio code": ["вс код", "вскод", "код", "студио код", "vscode", "vsc", "вижуал студио код", "редактор кода", "редактор"],
    "visual studio installer": ["установщик студии", "инсталлер студии", "компоненты vs"],
    "developer command prompt": ["командная строка разработчика", "компилятор с++", "компилятор c++", "dev prompt", "vs prompt"],
    "developer powershell": ["павершелл разработчика", "повершелл vs", "vs powershell"],
    "android studio": ["андроид студио", "андроид", "as", "android ide", "студия андроид"],
    "android explorer": ["проводник андроид", "файлы андроид", "девайсы"],
    "apk editor studio": ["редактор апк", "редактор apk", "манифест апк", "apk"],
    "jadx gui": ["джадкс", "декомпилятор", "декомпилятор java", "apk в java", "jadx"],
    "git bash": ["гит баш", "гит", "bash", "git", "терминал гит"],
    "git gui": ["гит гуи", "интерфейс гита", "git"],
    "postman": ["постман", "апи", "api", "запросы", "тестирование апи", "rest", "postman"],
    "python": ["питон", "пайтон", "idle", "интерпретатор python", "пайтон 3", "питон 3"],
    "wsl": ["всл", "линукс", "убунту", "терминал линукс", "linux", "ubuntu", "wsl2"],
    "windows sandbox": ["песочница", "сэндбокс", "изоляция", "безопасная среда", "sandbox"],
    
    # 02. Базы данных
    "dbeaver": ["дбивер", "бивер", "базы данных", "база", "sql клиент", "сглы", "субд", "бд", "dbeaver"],
    "heidisql": ["хейди", "хейди скл", "heidisql", "mysql", "базы"],
    "pgadmin": ["пгадмин", "постгрес", "postgres", "postgresql", "pgadmin4"],
    "sql shell": ["пскл", "psql", "консоль postgres", "терминал postgres"],
    "datagrip": ["датагрип", "дб грип", "jetbrains sql"],
    "mongodb": ["монго", "монгодб", "компас", "mongodb compass"],
    "redis": ["редис", "редисинсайт", "кэш"],
    
    # 03. Нейросети и ИИ
    "antigravity": ["антигравити", "антигравитация", "агент", "deepmind", "ai", "ии", "нейросеть"],
    "lm studio": ["лм студио", "лмка", "локальная нейросеть", "llm", "нейросеть оффлайн"],
    "comet": ["комет", "перплексити", "perplexity", "ии поиск", "нейробраузер"],
    "opencode": ["опенкод", "генерация кода", "ai code"],
    "ollama": ["оллама", "локальные модели", "терминал ии"],
    "cursor": ["курсор", "ai редактор", "курсор код"],
    
    # 04. Интернет и Браузеры
    "chrome": ["хром", "гугл хром", "гугл", "интернет", "браузер", "веб"],
    "google chrome": ["хром", "гугл хром", "гугл", "интернет", "браузер"],
    "firefox": ["файрфокс", "огнелис", "лиса", "мозилла", "мозила"],
    "edge": ["эдж", "майкрософт эдж", "интернет эксплорер"],
    "opera": ["опера", "опера гх", "opera gx"],
    "tor": ["тор", "луковичный", "анонимный"],
    
    # 05. Связь и Мессенджеры
    "discord": ["дискорд", "диск", "дс", "войс", "голосовой чат", "сервер"],
    "telegram": ["телеграм", "телега", "тг", "мессенджер", "чат", "телеграмм"],
    "telegram desktop": ["телеграм", "телега", "тг", "мессенджер", "чат", "телеграмм"],
    "whatsapp": ["ватсап", "вацап", "вотсап"],
    "zoom": ["зум", "видеоконференции", "созвон"],
    "skype": ["скайп"],
    "teams": ["тимс", "майкрософт тимс", "ms teams", "созвоны"],
    "microsoft teams": ["тимс", "майкрософт тимс", "ms teams", "созвоны"],
    "teamspeak": ["тимспик", "тс", "тс3", "голосовая связь"],
    
    # 06. Удаленный доступ и Сеть
    "remote desktop": ["удаленный рабочий стол", "рдп", "rdp", "подключение к удаленному", "десктоп", "удаленка"],
    "подключение к удаленному рабочему столу": ["удаленный рабочий стол", "рдп", "rdp", "удаленка", "mstsc"],
    "termius": ["термиус", "ссш", "ssh", "сервер", "терминал ssh"],
    "mobaxterm": ["мобахтерм", "моба", "ссш", "ssh", "терминал", "сессии"],
    "anydesk": ["энидеск", "удаленное управление", "удаленка"],
    "teamviewer": ["тимвьювер", "тимвивер"],
    "amnezia": ["амнезия", "впн", "vpn", "обход"],
    "wireguard": ["вайргард", "варгуард", "впн", "vpn"],
    "netbird": ["нетберд", "впн", "vpn", "mesh vpn"],
    "filezilla": ["файлзилла", "фтп", "ftp", "sftp"],
    "airexplorer": ["эйрэксплорер", "облачный проводник", "webdav", "облако"],
    "onedrive": ["вандрайв", "облако майкрософт", "облачный диск"],
    "syncthing": ["синктинг", "синхронизация", "бэкап"],
    
    # 07. Мультимедиа и Звук
    "яндекс музыка": ["яндекс", "музыка", "ям", "треки", "песни", "плейлист", "моя волна", "радио"],
    "yandex music": ["яндекс", "музыка", "ям", "треки", "песни", "плейлист", "моя волна"],
    "vlc": ["влс", "влк", "плеер", "видеоплеер", "проигрыватель", "фильмы", "кино"],
    "vlc media player": ["влс", "влк", "плеер", "видеоплеер", "проигрыватель"],
    "utorrent": ["торрент", "юторрент", "качалка", "клиент торрент", "фильмы", "скачать"],
    "utorrent web": ["торрент", "юторрент", "качалка", "клиент торрент", "utorrent"],
    "zona": ["зона", "фильмы", "сериалы", "кино онлайн", "торрент плеер"],
    "jellyfin": ["джеллифин", "медиасервер", "медиаплеер", "фильмы"],
    "jellyfin media player": ["джеллифин", "плеер jellyfin", "фильмы"],
    "spotify": ["спотифай", "споти", "музыка", "треки"],
    "obs": ["обс", "стрим", "запись экрана", "стриминг"],
    "photoshop": ["фотошоп", "фш", "картинки", "редактор фото"],
    "clipchamp": ["клипчамп", "видеоредактор", "монтаж видео"],
    "shutter encoder": ["шаттер", "кодировщик", "конвертер видео", "shutter"],
    "jackett": ["джакет", "индексатор торрентов"],
    "sonarr": ["сонарр", "сериалы", "тв шоу"],
    
    # 08. Офис
    "word": ["ворд", "документ", "текст", "doc", "docx"],
    "excel": ["эксель", "таблицы", "расчеты", "xls", "xlsx"],
    "access": ["аксесс", "базы данных", "ms access"],
    "powerpoint": ["паверпоинт", "поверпоинт", "презентации", "слайды", "ппт"],
    "onenote": ["ванноут", "заметки", "блокнот"],
    "outlook": ["аутлук", "почта", "письма", "email", "клиент почты"],
    "publisher": ["паблишер", "буклеты", "верстка"],
    "to do": ["туду", "задачи", "список дел", "планировщик"],
    "acrobat": ["акробат", "пдф", "pdf", "адобе ридер", "документы pdf"],
    "adobe acrobat": ["акробат", "пдф", "pdf", "адобе"],
    "notion": ["ноут", "нотион", "заметки", "база знаний"],
    "obsidian": ["обсидиан", "заметки", "граф"],
    
    # 09. Игры
    "lineage": ["линейка", "ла2", "л2", "л2десторус", "lineage 2", "l2", "игра"],
    "destorus": ["десторус", "л2", "линейка", "ла2"],
    "multeria": ["мультерия", "л2", "линейка", "ла2"],
    "dark dusk": ["дарк даск", "л2", "линейка"],
    "e-global": ["еглобал", "глобал", "л2", "линейка"],
    "dota 2": ["дота", "дота 2", "дотка", "dota", "valve"],
    "genshin impact": ["геншин", "геншин импакт", "genshin", "аниме игра"],
    "deep rock": ["дипрок", "глубокий рок", "дрг", "deep rock galactic"],
    "house flipper": ["хаус флиппер", "ремонт", "дома"],
    "cell to singularity": ["сингулярность", "эволюция", "кликкер"],
    "conquest dark": ["дарк конквест", "завоевание"],
    "crafter": ["крафтер", "калькулятор крафта", "спойл", "л2 крафт"],
    
    # 10. Игровой софт
    "playnite": ["плайнайт", "плейнайт", "игры", "библиотека игр", "лаунчер игр"],
    "steam": ["стим", "игры", "магазин игр", "валв", "valve"],
    
    # 11. Железо и Мониторинг
    "aida64": ["аида", "аида64", "диагностика", "температура", "железо", "тест железа", "датчики"],
    "aida64 extreme": ["аида", "аида64", "диагностика", "температура", "железо", "сенсоры"],
    "samsung magician": ["самсунг", "магикан", "магик", "ссд", "ssd", "накопитель", "диск"],
    "fancontrol": ["фанконтрол", "вентиляторы", "охлаждение", "кулеры", "скорость кулеров"],
    
    # 12. Система
    "powershell": ["павершелл", "повершелл", "пс", "терминал", "консоль", "командная строка"],
    "командная строка": ["кмд", "cmd", "терминал", "консоль", "шелл"],
    "диспетчер задач": ["диспетчер", "процессы", "задачи", "taskmgr", "task manager", "снять задачу"],
    "редактор реестра": ["реестр", "regedit", "ветки реестра"],
    "выключение монитора": ["погасить экран", "выключить экран", "doff", "монитор", "экран"],
    "службы": ["сервисы", "службы windows", "services.msc"],
    "параметры": ["настройки", "панель управления", "settings", "опции"],
    "powertoys": ["павертойс", "утилиты майкрософт", "power toys"],
    "windhawk": ["виндхавк", "моды windows", "кастомизация проводника"],
    "flow launcher": ["флоу лаунчер", "поиск windows", "лаунчер"],
    "task bar hero": ["таскбар", "панель задач", "герой таскбара"]
}

def get_app_search_aliases(name):
    name_l = name.lower()
    res = set()
    for k, aliases in APP_SEARCH_ALIASES.items():
        if k in name_l or name_l in k:
            res.update(aliases)
    return list(res)
