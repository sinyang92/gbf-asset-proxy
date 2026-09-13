import os
import json
import time
import hashlib
import logging
from mitmproxy import http
import requests

from config import LOCAL_ROOT, TARGET_DOMAIN_PATTERN, REQUEST_TIMEOUT, CACHE_LOG_FILE

_handler = logging.FileHandler(CACHE_LOG_FILE, mode="w", encoding="utf-8")
_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))

logger = logging.getLogger("gbf_cache")
logger.setLevel(logging.INFO)
logger.addHandler(_handler)
logger.addHandler(logging.StreamHandler())


def is_target(host: str) -> bool:
    return bool(TARGET_DOMAIN_PATTERN.search(host))


def get_paths(url_path: str):
    rel_path = url_path.lstrip("/")
    local_file = os.path.join(LOCAL_ROOT, rel_path)
    meta_file = local_file + ".ext"
    return local_file, meta_file


def load_meta(meta_file: str):
    if os.path.exists(meta_file):
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def save_meta(meta_file: str, headers, content: bytes):
    meta = {
        "LastModified": headers.get("Last-Modified"),
        "ETag": headers.get("ETag"),
        "at": int(time.time()),
        "md5": hashlib.md5(content).hexdigest(),
        "ct": headers.get("Content-Type", "application/octet-stream"),
        "v": 1,
    }
    os.makedirs(os.path.dirname(meta_file), exist_ok=True)
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(meta, f)


def request(flow: http.HTTPFlow) -> None:
    host = flow.request.pretty_host
    if not is_target(host):
        return

    local_file, meta_file = get_paths(flow.request.path.split("?")[0])
    meta = load_meta(meta_file)

    if not (meta and os.path.exists(local_file)):
        return

    headers = {}
    if meta.get("ETag"):
        headers["If-None-Match"] = meta["ETag"]
    if meta.get("LastModified"):
        headers["If-Modified-Since"] = meta["LastModified"]

    try:
        real_url = flow.request.pretty_url
        resp = requests.get(real_url, headers=headers, timeout=REQUEST_TIMEOUT, stream=True)

        if resp.status_code == 304:
            with open(local_file, "rb") as f:
                content = f.read()
            flow.response = http.Response.make(
                200, content,
                {"Content-Type": meta.get("ct", "application/octet-stream")}
            )
            logger.info(f"[命中,304确认未变] {flow.request.path}")
        else:
            new_content = resp.content
            os.makedirs(os.path.dirname(local_file), exist_ok=True)
            with open(local_file, "wb") as f:
                f.write(new_content)
            save_meta(meta_file, resp.headers, new_content)

            flow.response = http.Response.make(
                200, new_content,
                {"Content-Type": resp.headers.get("Content-Type", "application/octet-stream")}
            )
            logger.info(f"[已更新] {flow.request.path}")

    except requests.RequestException as e:
        with open(local_file, "rb") as f:
            content = f.read()
        flow.response = http.Response.make(
            200, content,
            {"Content-Type": meta.get("ct", "application/octet-stream")}
        )
        logger.info(f"[网络异常,降级用本地] {flow.request.path} ({e})")


def response(flow: http.HTTPFlow) -> None:
    host = flow.request.pretty_host
    if not is_target(host) or flow.response is None:
        return

    local_file, meta_file = get_paths(flow.request.path.split("?")[0])

    if not os.path.exists(local_file) and flow.response.status_code == 200:
        content = flow.response.content
        os.makedirs(os.path.dirname(local_file), exist_ok=True)
        with open(local_file, "wb") as f:
            f.write(content)
        save_meta(meta_file, flow.response.headers, content)
        logger.info(f"[首次缓存] {flow.request.path}")