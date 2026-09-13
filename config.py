import re

# 本地缓存根目录
LOCAL_ROOT = r"D:\gbf_cache"

TARGET_DOMAIN_PATTERN = re.compile(r"prd-game-a\d*-(granbluefantasy|gbf)\.akamaized\.net$")

REQUEST_TIMEOUT = 5

PROXY_PORT = 8888