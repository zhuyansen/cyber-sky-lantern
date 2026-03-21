"""赛博点天灯 - FastAPI + Socket.IO 主服务"""

import os
import json
import time
import uuid
import base64
import logging

import socketio
import uvicorn
import yaml
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from ai_text import beautify_wish
from ai_image import generate_lantern_image

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --- 加载配置 ---
with open(os.path.join(os.path.dirname(__file__), "config.yaml")) as f:
    CONFIG = yaml.safe_load(f)

# --- 持久化计数器 ---
STATE_FILE = os.path.join(os.path.dirname(__file__), "data", "state.json")


def load_state():
    try:
        with open(STATE_FILE) as f:
            data = json.load(f)
            return data.get("wish_counter", 0), data.get("recent_wishes", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return 0, []


MAX_RECENT = 50


def save_state(count: int, wishes: list):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump({"wish_counter": count, "recent_wishes": wishes[-MAX_RECENT:]}, f, ensure_ascii=False)


wish_counter, recent_wishes = load_state()


# --- generated/ 自动清理（保留最近 200 张）---
def cleanup_generated(max_keep: int = 200):
    gen_dir = os.path.join(os.path.dirname(__file__), "generated")
    if not os.path.isdir(gen_dir):
        return
    files = sorted(
        (os.path.join(gen_dir, f) for f in os.listdir(gen_dir) if f.endswith(".png")),
        key=os.path.getmtime,
    )
    if len(files) > max_keep:
        for f in files[: len(files) - max_keep]:
            try:
                os.remove(f)
            except OSError:
                pass


# --- 安全头中间件 ---
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

# --- Socket.IO ---
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*", max_http_buffer_size=10 * 1024 * 1024)  # 10MB for screenshots

# --- FastAPI ---
api = FastAPI(title="赛博点天灯")
api.add_middleware(SecurityHeadersMiddleware)
api.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
api.mount("/print", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "print-materials"), html=True), name="print")


@api.get("/", response_class=HTMLResponse)
async def index():
    return '<meta http-equiv="refresh" content="0;url=/wish">'


@api.get("/wish", response_class=HTMLResponse)
async def serve_wish():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "wish.html"))


@api.get("/display", response_class=HTMLResponse)
async def serve_display():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "display.html"))


@api.get("/qr", response_class=HTMLResponse)
async def serve_qr():
    """动态 QR 码页面，兼容微信/Telegram/WhatsApp 扫码"""
    # 优先使用配置的域名，否则自动检测 LAN IP
    domain = CONFIG.get("server", {}).get("domain", "")
    if domain:
        wish_url = f"https://{domain}/wish"
    else:
        import socket as sock
        try:
            s = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except Exception:
            ip = "localhost"
        port = CONFIG["server"]["port"]
        wish_url = f"http://{ip}:{port}/wish"

    import qrcode, io
    # 高容错 QR 码，兼容所有扫码 App
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # 30% 容错
        box_size=12,
        border=3,
    )
    qr.add_data(wish_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="white", back_color="black")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode()

    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Scan to Make a Wish</title>
<style>
  body {{ background: #020308; color: #FFE18C; font-family: -apple-system, sans-serif;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    min-height: 100vh; margin: 0; padding: 20px; text-align: center; }}
  h1 {{ font-size: 32px; color: #FFD700; letter-spacing: 3px; margin-bottom: 8px;
    text-shadow: 0 0 20px rgba(255,179,71,0.5); }}
  .sub {{ font-size: 18px; color: rgba(255,200,100,0.6); margin-bottom: 28px; }}
  .qr-wrap {{ background: white; padding: 16px; border-radius: 20px;
    box-shadow: 0 0 50px rgba(255,179,71,0.3); display: inline-block; }}
  .qr-wrap img {{ display: block; border-radius: 8px; }}
  .url {{ margin-top: 20px; font-size: 15px; color: rgba(255,200,100,0.5); letter-spacing: 1px;
    font-family: monospace; }}
  .apps {{ margin-top: 16px; font-size: 13px; color: rgba(255,200,100,0.35); }}
</style></head><body>
  <h1>Cyber Sky Lantern</h1>
  <p class="sub">Scan QR code to make a wish<br>扫码许愿 · สแกนเพื่ออธิษฐาน</p>
  <div class="qr-wrap">
    <img src="data:image/png;base64,{qr_b64}" width="260" height="260" alt="QR Code">
  </div>
  <p class="url">{wish_url}</p>
  <p class="apps">WeChat · Telegram · WhatsApp · Camera</p>
</body></html>"""


@api.post("/api/wish")
async def submit_wish(request: Request):
    global wish_counter

    body = await request.json()
    wish_text = body.get("wish", "").strip()[:50]
    theme = body.get("theme", "爱情")
    name = body.get("name", "").strip()[:20]

    if not wish_text:
        return JSONResponse({"error": "许愿内容不能为空"}, status_code=400)

    if theme not in CONFIG["themes"]:
        theme = "爱情"

    logger.info(f"收到心愿: [{theme}] {wish_text} (by {name or 'anonymous'})")

    # 1. AI 文字润色
    beautified = await beautify_wish(wish_text, CONFIG)
    logger.info(f"润色结果: {beautified}")

    # 2. AI 图片生成
    image_bytes, image_source = await generate_lantern_image(beautified, theme, CONFIG)
    image_b64 = base64.b64encode(image_bytes).decode()
    logger.info(f"图片生成: {image_source}, {len(image_bytes)} bytes")

    # 3. 计数 + 幸运判定 + 持久化
    wish_counter += 1
    wish_id = str(uuid.uuid4())[:8]
    is_lucky = wish_counter % CONFIG["display"]["lucky_interval"] == 0

    # 4. 广播到大屏
    lantern_data = {
        "id": wish_id,
        "text": beautified,
        "name": name,
        "theme": theme,
        "emoji": CONFIG["themes"][theme]["emoji"],
        "is_lucky": is_lucky,
        "counter": wish_counter,
    }
    await sio.emit("new_lantern", lantern_data)

    # 缓存最近心愿并持久化
    recent_wishes.append(lantern_data)
    if len(recent_wishes) > MAX_RECENT:
        recent_wishes.pop(0)
    save_state(wish_counter, recent_wishes)

    # 5. 保存图片到 generated/
    os.makedirs(os.path.join(os.path.dirname(__file__), "generated"), exist_ok=True)
    img_path = os.path.join(os.path.dirname(__file__), "generated", f"{wish_id}.png")
    with open(img_path, "wb") as f:
        f.write(image_bytes)

    # 6. 清理旧图片
    if wish_counter % 50 == 0:
        cleanup_generated()

    # 7. 返回给手机
    return JSONResponse({
        "wish_id": wish_id,
        "original": wish_text,
        "beautified": beautified,
        "name": name,
        "image_b64": image_b64,
        "theme": theme,
        "emoji": CONFIG["themes"][theme]["emoji"],
        "is_lucky": is_lucky,
        "counter": wish_counter,
    })


@api.get("/api/counter")
async def get_counter():
    return {"counter": wish_counter}


@api.get("/api/themes")
async def get_themes():
    return {k: {"emoji": v["emoji"], "example": v["example"]} for k, v in CONFIG["themes"].items()}


# --- Socket.IO 事件 ---

@sio.event
async def connect(sid, environ):
    logger.info(f"大屏连接: {sid}")
    await sio.emit("sync_counter", {"counter": wish_counter}, to=sid)
    # 发送最近心愿让大屏恢复
    if recent_wishes:
        await sio.emit("recent_wishes", recent_wishes, to=sid)


@sio.event
async def disconnect(sid):
    logger.info(f"大屏断开: {sid}")


# 实时截图机制
import asyncio
screenshot_futures = {}  # request_id -> asyncio.Future


@sio.event
async def display_screenshot(sid, data):
    """大屏回传截图"""
    req_id = data.get("request_id", "")
    image = data.get("image", "")
    if req_id and req_id in screenshot_futures:
        screenshot_futures[req_id].set_result(image)
        logger.info(f"收到大屏截图: {req_id} ({len(image)} chars)")


@api.get("/api/screenshot")
async def get_screenshot():
    """手机请求实时截图：通知大屏截图，等待回传"""
    req_id = str(uuid.uuid4())[:8]
    loop = asyncio.get_event_loop()
    future = loop.create_future()
    screenshot_futures[req_id] = future

    # 通知大屏截图
    await sio.emit("take_screenshot", {"request_id": req_id})

    try:
        image = await asyncio.wait_for(future, timeout=8.0)
        del screenshot_futures[req_id]
        if image:
            return JSONResponse({"image": image})
        return JSONResponse({"image": ""}, status_code=500)
    except asyncio.TimeoutError:
        screenshot_futures.pop(req_id, None)
        return JSONResponse({"image": ""}, status_code=504)


# --- 启动 ---
app = socketio.ASGIApp(sio, other_asgi_app=api)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", CONFIG["server"]["port"]))
    host = CONFIG["server"]["host"]
    logger.info(f"赛博点天灯启动: http://{host}:{port}")
    logger.info(f"手机许愿页: http://localhost:{port}/wish")
    logger.info(f"大屏展示页: http://localhost:{port}/display")
    uvicorn.run(app, host=host, port=port)
