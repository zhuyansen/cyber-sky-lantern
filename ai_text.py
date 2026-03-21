"""Ollama 文字润色模块：将许愿文字美化为诗意祝福语"""

import re
import logging
import httpx

logger = logging.getLogger(__name__)


async def beautify_wish(wish_text: str, config: dict) -> str:
    """
    调用 Ollama 本地模型将许愿文字润色为古风祝福语。
    失败时回退返回原文。
    """
    ollama_cfg = config["ollama"]
    prompt = ollama_cfg["prompt_template"].format(wish=wish_text)

    try:
        async with httpx.AsyncClient(timeout=ollama_cfg["timeout"]) as client:
            resp = await client.post(
                f"{ollama_cfg['base_url']}/api/generate",
                json={
                    "model": ollama_cfg["model"],
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 80,
                    },
                },
            )
            resp.raise_for_status()
            result = resp.json()["response"].strip()

            # 去除可能的 <think>...</think> 标签
            result = re.sub(r"<think>.*?</think>", "", result, flags=re.DOTALL).strip()

            # 去除引号包裹
            result = result.strip("\"'「」『』""''")

            if not result or len(result) > 60:
                return wish_text
            return result

    except Exception as e:
        logger.warning(f"Ollama 不可用，使用原文: {e}")
        return wish_text
