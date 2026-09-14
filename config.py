import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOCAL_ROOT = os.path.join(BASE_DIR, "cache")

TARGET_DOMAIN_PATTERN = re.compile(r"prd-game-a\d*-(granbluefantasy|gbf)\.akamaized\.net$")

UPSTREAM_PROXY = None

REQUEST_TIMEOUT = 5

CACHE_LOG_FILE = os.path.join(BASE_DIR, "cache_log.txt")

TRUST_LOCAL_PATTERN = re.compile(r"/assets/(img|sound)/")