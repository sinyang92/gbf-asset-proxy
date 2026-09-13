# gbf-local-cache

一个基于 [mitmproxy](https://mitmproxy.org/) 的本地资源缓存代理,用于减少网页游戏《碧蓝幻想 / Granblue Fantasy》重复下载相同静态资源(图片、音频、脚本等)所消耗的流量与加载时间。

## 原理

游戏客户端每次请求资源时,本工具会拦截请求并按以下逻辑处理:

1. **本地无缓存** → 放行请求,正常从游戏服务器下载,下载完成后将文件内容与响应头中的 `ETag` / `Last-Modified` / `Content-Type` 等信息保存到本地(元数据以 `<文件名>.ext` 的 JSON 文件形式存放在资源文件旁)。
2. **本地已有缓存** → 不会直接无条件复用旧文件,而是携带上次保存的 `ETag` / `Last-Modified` 向服务器发起 [HTTP 条件请求](https://developer.mozilla.org/en-US/docs/Web/HTTP/Conditional_requests):
   - 服务器返回 `304 Not Modified` → 说明资源未变化,直接使用本地文件,几乎不产生下载流量。
   - 服务器返回新内容(`200`) → 说明资源已更新,重新下载并覆盖本地缓存与元数据。
3. **网络异常**(如条件请求失败)→ 自动降级,直接使用本地旧文件,避免因网络波动导致游戏卡死或报错。

本工具**不修改、不绕过游戏本身的任何验证或业务逻辑**,只是在 HTTP 层面复用了浏览器/CDN 早已支持的标准协商缓存机制,效果类似于给指定资源手动做了一层更可控的本地 CDN 缓存。

## 环境依赖

- **Python 3.8+**:访问 [python.org/downloads](https://www.python.org/downloads/) 下载并安装对应系统的安装包(安装时建议勾选 "Add Python to PATH")。
- **mitmproxy**:访问 [mitmproxy.org](https://mitmproxy.org/) 下载对应系统的安装包并安装。

## 配置

打开 `config.py` 按需修改:

```python
import os
import re

# 脚本自身所在目录,用于把缓存目录/日志文件固定到这里,避免相对路径受工作目录影响
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 本地缓存存放目录(默认在脚本所在目录下的 cache 文件夹)
LOCAL_ROOT = os.path.join(BASE_DIR, "cache")

# 需要拦截的资源域名规则(正则表达式),默认匹配碧蓝幻想的多个CDN镜像域名
TARGET_DOMAIN_PATTERN = re.compile(r"prd-game-a\d*-(granbluefantasy|gbf)\.akamaized\.net$")

# 条件请求超时时间(秒)
REQUEST_TIMEOUT = 5
```

## 使用方法

1. 启动代理,有两种方式:

   **方式一:直接用命令行启动(可以实时看到日志)**

   ```bash
   mitmdump -s main.py -p 8888
   ```

   **方式二:双击 `start_proxy.bat`(推荐日常使用)**

   该脚本会以隐藏窗口的方式在后台启动代理,不会弹出黑框命令行窗口。mitmproxy 自身的连接日志会写入脚本同目录下的 `proxy_console.log` 文件,便于事后查看运行状况。

   端口等配置可在 `start_proxy.bat` 顶部的变量区修改:

   ```bat
   set PROXY_PORT=8888
   ```

   **关闭隐藏运行的代理**:由于隐藏模式下没有可见窗口,需要通过任务管理器结束 `mitmdump.exe` 进程,或在命令行中执行:

   ```bash
   netstat -ano | findstr :8888
   taskkill /PID <对应的PID> /F
   ```

   **开机自动启动**:将 `start_proxy.bat`(或其快捷方式)放入 `Win+R` → 输入 `shell:startup` 打开的启动文件夹,即可在每次开机后自动静默运行。

2. 让浏览器(建议使用专门跑该游戏的独立浏览器实例，这里推荐SRWare Iron)走这个代理:

   ```bash
   chrome.exe --proxy-server="127.0.0.1:8888"
   ```

3. 首次启动代理后,访问 `http://mitm.it`,下载并安装对应系统的 mitmproxy CA 证书(用于解密 HTTPS 流量),安装到"受信任的根证书颁发机构"。

4. 重启浏览器,正常游玩游戏。cache_log.txt(位于脚本所在目录)会打印以下几种状态,便于确认工作情况:
   - `[首次缓存]`:本地无缓存,已从服务器下载并保存
   - `[命中,304确认未变]`:本地缓存有效,服务器确认无变化,未重新下载
   - `[已更新]`:服务器资源已变化,已重新下载并更新本地缓存
   - `[网络异常,降级用本地]`:条件请求失败,已降级使用本地旧文件

## 注意事项

- 仅建议在独立的浏览器实例/用户配置目录中启用该代理,避免影响日常上网及其他网站的正常访问。
- 部分强制证书校验(Certificate Pinning)的应用可能无法被 mitmproxy 正常拦截,但网页游戏通常不受此限制。
- 本工具仅用于减少个人重复下载流量、加快本地加载速度,不涉及修改游戏数据、破解验证或任何形式的作弊行为。

## License

MIT