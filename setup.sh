#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "=== 赛博点天灯 - 安装脚本 ==="
echo ""

# 1. 安装 Python 依赖
echo "[1/4] 安装 Python 依赖..."
pip3 install -r requirements.txt

# 2. 拉取 Ollama 模型
echo ""
echo "[2/4] 拉取 Ollama 模型 (qwen3:0.6b)..."
if command -v ollama &> /dev/null; then
    ollama pull qwen3:0.6b || echo "  ⚠️ Ollama 拉取失败，文字美化将使用原文回退"
else
    echo "  ⚠️ Ollama 未安装，文字美化将使用原文回退"
fi

# 3. 创建目录
echo ""
echo "[3/4] 创建目录..."
mkdir -p static/assets generated

# 4. 生成二维码
echo ""
echo "[4/4] 生成许愿页二维码..."
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || echo "localhost")
PORT=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['server']['port'])" 2>/dev/null || echo "8080")
WISH_URL="http://${LOCAL_IP}:${PORT}/wish"

python3 << PYEOF
import qrcode
url = "${WISH_URL}"
qr = qrcode.make(url)
qr.save("static/assets/qr-wish.png")
print(f"  QR 码已保存: static/assets/qr-wish.png")
print(f"  许愿页地址: {url}")
PYEOF

echo ""
echo "==============================="
echo "  安装完成！"
echo "==============================="
echo ""
echo "  启动 Ollama:  ollama serve"
echo "  启动服务:     python3 server.py"
echo ""
echo "  手机许愿页:   http://${LOCAL_IP}:${PORT}/wish"
echo "  大屏展示页:   http://${LOCAL_IP}:${PORT}/display"
echo "  二维码图片:   static/assets/qr-wish.png"
echo ""
