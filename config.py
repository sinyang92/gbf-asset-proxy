import re

LOCAL_ROOT = r"D:\gbf_cache"

TARGET_DOMAIN_PATTERN = re.compile(r"prd-game-a\d*-(granbluefantasy|gbf)\.akamaized\.net$")

REQUEST_TIMEOUT = 5

CACHE_LOG_FILE = "cache_log.txt"