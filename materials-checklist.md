# Cyber Sky Lantern - Booth Materials Checklist
## Thailand Lantern Festival Edition

---

### 1. Display & Screen Setup

| Item | Spec | Qty | Notes |
|------|------|-----|-------|
| Portable monitor / TV | 32"~43", HDMI, high brightness (300+ nits) | 1 | Main display for lantern animation. Consider anti-glare if outdoor |
| Monitor stand / mount | Height-adjustable, stable base | 1 | Eye-level for standing crowd |
| Mini PC / Laptop | MacBook or any laptop running the server | 1 | Runs server.py, connects to monitor |
| HDMI cable | 2m+ length | 1 | Connect laptop to display |
| Power strip | 4+ outlets, with surge protector | 1 | For all electronics |
| Extension cord | 5m+, outdoor-rated | 1~2 | Thailand venues may have distant power |

### 2. Network & Connectivity

| Item | Spec | Qty | Notes |
|------|------|-----|-------|
| Portable WiFi router / hotspot | Supports 20+ devices, 2.4GHz + 5GHz | 1 | Critical - visitors' phones connect to this |
| Thai SIM card with data | Unlimited data plan | 1 | Backup internet for API calls |
| Ethernet cable | Cat6, 3m | 1 | Backup wired connection for laptop |

### 3. Booth Structure (ref: WYSS-style tent booth)

| Item | Spec | Qty | Notes |
|------|------|-----|-------|
| Pop-up tent / canopy | 3m x 3m, dark color (navy/black) | 1 | Matches night sky theme, blocks sunlight on screen |
| Folding table | 1.2m~1.8m | 1 | For laptop, QR stand, decorations |
| Table cloth | Dark navy/black with subtle star pattern | 1 | On-brand with night sky |
| LED string lights | Warm white, battery or USB powered | 2~3 | Drape around tent frame for ambient glow |

### 4. Branding & Signage

| Item | Spec | Qty | Notes |
|------|------|-----|-------|
| Main banner (tent top) | "CYBER SKY LANTERN" + "AI Sky Lantern Experience" | 1 | Bilingual EN/TH if budget allows |
| Roll-up banner | 80cm x 200cm, dark bg with lantern visual + QR code | 1 | Street-facing, like the pink banner in ref image |
| Table front banner | ~1.5m x 0.7m, branded wrap | 1 | Covers table front, shows brand + instructions |
| QR code stand | A4 acrylic stand-up frame | 2 | One on table, one on roll-up banner |
| QR code print | Large format QR linking to /wish page | 2 | Laminated for durability |
| Price sign | A5 acrylic stand | 1 | "XX THB per wish" or "Free to try" |
| How-it-works poster | A3, 3-step visual guide | 1 | "1. Scan QR  2. Write wish  3. Watch it fly" |

### 5. Ambiance & Decoration

| Item | Spec | Qty | Notes |
|------|------|-----|-------|
| Paper sky lanterns (decorative) | Small, non-flying, warm LED inside | 3~5 | Hang from tent frame as decoration |
| LED candles / tea lights | Warm amber flickering | 5~8 | Scatter on table and around booth |
| Fabric backdrop | Dark navy/starry sky print, 2m x 2m | 1 | Behind the monitor for immersive feel |
| Small golden lantern props | Tabletop decorative lanterns | 2~3 | Photo-worthy props |
| Incense or essential oil diffuser | Sandalwood or Thai jasmine scent | 1 | Multi-sensory experience (optional) |

### 6. Operations & Staff

| Item | Spec | Qty | Notes |
|------|------|-----|-------|
| Staff T-shirt / uniform | Dark navy with gold "Cyber Sky Lantern" logo | 2~3 | For booth operators |
| Cash box / QR payment | WeChat Pay, Alipay, PromptPay (Thai), cash | 1 | Thailand tourists may use PromptPay or cash |
| Tablet (backup) | iPad or Android tablet | 1 | Demo device if visitors have phone issues |
| Portable battery pack | 20000mAh+ | 1~2 | Emergency phone charging for visitors |
| Business cards | With QR code to wish page | 50~100 | Visitors can share with friends |

### 7. Printed Takeaways

| Item | Spec | Qty | Notes |
|------|------|-----|-------|
| Wish certificate card | Business card size, gold foil on dark card stock | 100~200 | "Your wish has been released into the sky" + wish ID |
| Stickers | Die-cut lantern emoji sticker | 100~200 | Giveaway, brand recall |
| Photo frame card | Foldable card with QR to their lantern image | 100 | Optional premium upsell |

### 8. Tech Prep (Before Event)

| Task | Status |
|------|--------|
| Run `setup.sh` to install dependencies and generate QR | [ ] |
| Start Ollama with `ollama serve` + `ollama pull qwen3:0.6b` | [ ] |
| Configure SiliconFlow API key in `config.yaml` (if using AI images) | [ ] |
| Test full flow on local WiFi: phone scan → wish → display | [ ] |
| Pre-generate QR code with venue WiFi IP address | [ ] |
| Test with 10+ concurrent connections | [ ] |
| Prepare offline fallback (Pillow images work without internet) | [ ] |
| Charge all devices, pack all cables | [ ] |

### 9. On-Site Setup Checklist

| Step | Task |
|------|------|
| 1 | Set up tent/canopy, secure with weights (outdoor wind) |
| 2 | Position table, attach table cloth and front banner |
| 3 | Mount monitor on stand, connect to laptop via HDMI |
| 4 | Set up portable WiFi router, note SSID and password |
| 5 | Start server: `source .venv/bin/activate && python3 server.py` |
| 6 | Open `/display` on monitor in fullscreen (F11) |
| 7 | Update QR code with correct WiFi IP: `http://<IP>:8080/wish` |
| 8 | Place QR stands, test scan from personal phone |
| 9 | Hang decorative lanterns, set up LED lights |
| 10 | Brief staff on flow: greet → explain → help scan → collect payment |

### 10. Contingency Plan

| Issue | Solution |
|------|----------|
| No internet | Pillow fallback generates images locally, Ollama runs offline |
| WiFi overloaded | Switch to phone hotspot, limit to 5GHz band |
| Monitor dies | Use laptop screen directly, or tablet as backup display |
| Server crashes | `python3 server.py` auto-restarts; keep terminal accessible |
| Rain (outdoor) | Tent covers booth; wrap monitor in plastic sheet |
| Power outage | Battery pack for laptop (2-3 hrs), pause operations |

---

**Budget Estimate (approximate THB)**

| Category | Est. Cost |
|----------|-----------|
| Monitor rental (1 day) | 1,500~3,000 |
| Tent rental | 2,000~4,000 |
| Printing (banners, QR, cards) | 3,000~5,000 |
| Decorations (lanterns, lights) | 1,500~3,000 |
| WiFi router | 800~1,500 (buy) or bring own |
| Misc (table, cloth, extension) | 1,000~2,000 |
| **Total** | **~10,000~18,000 THB** |

*Note: Prices vary by city (Chiang Mai vs Bangkok). Many items can be rented locally near festival venues.*
