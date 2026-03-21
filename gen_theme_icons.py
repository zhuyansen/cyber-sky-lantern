"""Generate 6 theme icon images via apimart.ai Gemini image generation."""
import requests, base64, os, re, time

API_KEY = "sk-FuTq0PhYpqC6yIoJnY3PoJq14y3HpZzstZE4Lz9pQvrAR2jh"
MODEL = "gemini-3.1-flash-image-preview"
URL = f"https://api.apimart.ai/v1beta/models/{MODEL}:generateContent"
OUT_DIR = os.path.join(os.path.dirname(__file__), "static", "images")

STYLE = "Warm glowing Yi Peng Thai sky lantern floating in dark night sky. The lantern is a translucent paper cylinder shape glowing warm amber/gold from within. Seamless dark background color #020308, no borders, no frames, no white edges. Painterly digital art style, soft warm lighting."

THEMES = {
    "love": f"A {STYLE} The lantern has a soft glowing red heart symbol visible through the paper. Square composition, filling the frame.",
    "career": f"A {STYLE} The lantern has a small rocket silhouette visible through the glowing paper, launching upward with a flame trail. Square composition, filling the frame.",
    "health": f"A {STYLE} The lantern has a fresh green leaf/sprout symbol visible through the glowing paper. Square composition, filling the frame.",
    "studies": f"A {STYLE} The lantern has an open book symbol visible through the glowing paper. Square composition, filling the frame.",
    "fortune": f"A {STYLE} The lantern has golden coins symbol visible through the glowing paper. Square composition, filling the frame.",
    "joy": f"A {STYLE} The lantern has a happy smiling sun face visible through the glowing paper. Square composition, filling the frame.",
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

def generate(name, prompt):
    print(f"[{name}] Generating...")
    resp = requests.post(URL, headers=headers, json={
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
    }, timeout=120)

    if resp.status_code != 200:
        print(f"[{name}] Error {resp.status_code}: {resp.text[:200]}")
        return False

    data = resp.json()
    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    for part in parts:
        text = part.get("text", "")
        match = re.search(r'data:image/(jpeg|png);base64,([A-Za-z0-9+/=]+)', text)
        if match:
            fmt = match.group(1)
            b64 = match.group(2)
            img_data = base64.b64decode(b64)
            ext = "jpg" if fmt == "jpeg" else "png"
            out_path = os.path.join(OUT_DIR, f"theme-{name}.{ext}")
            with open(out_path, "wb") as f:
                f.write(img_data)
            print(f"[{name}] Saved: {out_path} ({len(img_data)} bytes)")
            return True
        if "inlineData" in part:
            b64 = part["inlineData"]["data"]
            mime = part["inlineData"].get("mimeType", "image/png")
            ext = "jpg" if "jpeg" in mime else "png"
            img_data = base64.b64decode(b64)
            out_path = os.path.join(OUT_DIR, f"theme-{name}.{ext}")
            with open(out_path, "wb") as f:
                f.write(img_data)
            print(f"[{name}] Saved: {out_path} ({len(img_data)} bytes)")
            return True

    print(f"[{name}] No image found in response")
    return False


if __name__ == "__main__":
    for name, prompt in THEMES.items():
        ok = generate(name, prompt)
        if not ok:
            print(f"[{name}] Failed!")
        time.sleep(1)
    print("\nDone.")
