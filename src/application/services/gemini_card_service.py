import base64
import json
import logging
from typing import Dict, Any, Optional
import httpx
from src.core.config import settings

logger = logging.getLogger(__name__)


class GeminiCardService:
    """
    Servicio de Transformación Mágica de Cromos Digitales mediante la API de Google Gemini / Imagen 3.
    Permite generar variaciones de arte al óleo retro de los 80, cómic clásico, cine 4K y lore canónico con stats RPG.
    """

    STYLES_CONFIG = {
        "oil_vintage": {
            "name": "Óleo Vintage 80s (Rudy Obrero)",
            "prompt": (
                "Masters of the Universe 1980s vintage toy packaging box art of {name}, "
                "heroic dramatic battle pose in front of Castle Grayskull, storm skies with lightning, "
                "authentic vintage oil on canvas painting illustration style by Rudy Obrero and Earl Norem, "
                "retro Mattel toy art, vibrant saturated colors, 80s fantasy masterpiece"
            )
        },
        "comic_retro": {
            "name": "Cómic Retro 80s (Mini-Comics)",
            "prompt": (
                "Masters of the Universe vintage 1980s mini-comic cover illustration of {name}, "
                "retro vintage comic lineart, dynamic battle action pose in Snake Mountain, "
                "halftone dot patterns, classic 80s comic inks, bold colors, authentic DC/Mattel mini-comic aesthetic"
            )
        },
        "cinematic_4k": {
            "name": "Cine Épico 4K (Live-Action Eternia)",
            "prompt": (
                "Cinematic photorealistic live-action fantasy movie scene of {name} in the world of Masters of the Universe, "
                "intricate battle-worn armor, atmospheric volumetric fog and mystic energy at twilight in Eternia, "
                "8k resolution, IMAX cinematography, highly detailed realistic textures"
            )
        },
        "rpg_lore": {
            "name": "Ficha de Lore & Poder de Grayskull",
            "prompt": (
                "Genera el perfil canónico de combate en español para la figura de Masters of the Universe '{name}' "
                "de la categoría '{sub_category}'. "
                "Devuelve un JSON con:\n"
                "- 'lore': Micro-relato épico de 2 frases sobre su papel en la batalla por Eternia.\n"
                "- 'stats': Objeto con 'fuerza', 'magia', 'defensa', 'agilidad' (enteros de 50 a 99).\n"
                "- 'special_move': Nombre de su técnica o ataque definitivo.\n"
                "- 'rarity_class': Título honorífico de rareza (ej. 'Guardián Sagrado', 'Azote de Snake Mountain', 'Reliquia Legendaria')."
            )
        }
    }

    @classmethod
    async def enhance_card(
        cls,
        product_name: str,
        sub_category: Optional[str] = "MOTU Origins",
        style: str = "oil_vintage",
        condition: str = "MOC",
        grading: float = 10.0
    ) -> Dict[str, Any]:
        """
        Ejecuta la transmutación mágica del cromo mediante Gemini.
        """
        sub_cat = sub_category or "MOTU Origins"
        style_info = cls.STYLES_CONFIG.get(style, cls.STYLES_CONFIG["oil_vintage"])

        # 1. Generación de Lore & Stats con Gemini Flash
        lore_data = await cls._generate_lore_and_stats(product_name, sub_cat, condition, grading)

        # 2. Generación o Adaptación Visual con Imagen 3 / Gemini
        image_data = None
        if style in ["oil_vintage", "comic_retro", "cinematic_4k"]:
            image_data = await cls._generate_ai_art(product_name, sub_cat, style)

        return {
            "style": style,
            "style_name": style_info["name"],
            "image_base64": image_data,
            "lore": lore_data.get("lore"),
            "stats": lore_data.get("stats"),
            "special_move": lore_data.get("special_move"),
            "rarity_class": lore_data.get("rarity_class")
        }

    @classmethod
    async def _generate_ai_art(cls, product_name: str, sub_category: str, style: str) -> Optional[str]:
        """
        Llama al endpoint de generación de imagen multimodal de Gemini (gemini-2.5-flash-image / gemini-3.1-flash-image)
        para generar una pintura real de la figura.
        """
        if not settings.GEMINI_API_KEY:
            logger.info("Sin GEMINI_API_KEY: devolviendo modo determinista.")
            return None

        style_cfg = cls.STYLES_CONFIG.get(style, cls.STYLES_CONFIG["oil_vintage"])
        prompt_text = style_cfg["prompt"].format(name=product_name, sub_category=sub_category)

        models_to_try = [
            "gemini-2.5-flash-image",
            "gemini-3.1-flash-image",
            "gemini-3-pro-image",
            "gemini-3.1-flash-lite-image"
        ]

        payload = {
            "contents": [{
                "parts": [{"text": prompt_text}]
            }],
            "generationConfig": {
                "responseModalities": ["IMAGE"]
            }
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            for model in models_to_try:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.GEMINI_API_KEY}"
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            for part in parts:
                                if "inlineData" in part:
                                    mime = part["inlineData"].get("mimeType", "image/png")
                                    b64 = part["inlineData"].get("data")
                                    if b64:
                                        logger.info(f"Arte generado con éxito usando {model} ({len(b64)} bytes base64)")
                                        return f"data:{mime};base64,{b64}"
                    else:
                        logger.warning(f"Modelo {model} respondió {resp.status_code}: {resp.text[:120]}")
                except Exception as e:
                    logger.warning(f"Error generando arte con modelo {model}: {e}")

        return None

    @classmethod
    async def _generate_lore_and_stats(
        cls,
        product_name: str,
        sub_category: str,
        condition: str,
        grading: float
    ) -> Dict[str, Any]:
        """
        Genera el trasfondo épico y estadísticas RPG con Gemini 1.5 Flash.
        """
        if settings.GEMINI_API_KEY:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={settings.GEMINI_API_KEY}"
            prompt = (
                f"Genera una ficha de coleccionista y estadísticas de combate en JSON para la figura '{product_name}' "
                f"({sub_category}, estado {condition}, grado {grading}/10). "
                "Responde ÚNICAMENTE un JSON válido con este formato exacto:\n"
                "{\n"
                '  "lore": "Texto épico de 2 frases sobre la figura en la batalla por Eternia.",\n'
                '  "stats": {\n'
                '    "fuerza": 92,\n'
                '    "magia": 85,\n'
                '    "defensa": 90,\n'
                '    "agilidad": 88\n'
                "  },\n"
                '  "special_move": "Nombre del Ataque Definitivo",\n'
                '  "rarity_class": "Reliquia Sagrada de Grayskull"\n'
                "}"
            )
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.4, "responseMimeType": "application/json"}
            }

            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        res_json = resp.json()
                        candidates = res_json.get("candidates", [])
                        if candidates:
                            text_content = candidates[0]["content"]["parts"][0]["text"]
                            return json.loads(text_content)
            except Exception as e:
                logger.warning(f"Error generando lore con Gemini Flash: {e}")

        # Fallback determinista local
        base_hash = sum(ord(c) for c in product_name)
        fuerza = 75 + (base_hash % 24)
        magia = 70 + ((base_hash * 3) % 29)
        defensa = 78 + ((base_hash * 7) % 21)
        agilidad = 72 + ((base_hash * 11) % 26)

        return {
            "lore": f"Forjado en los fuegos arcanos de Eternia, {product_name} porta la esencia y el poder ancestral de Grayskull en cada combate.",
            "stats": {
                "fuerza": fuerza,
                "magia": magia,
                "defensa": defensa,
                "agilidad": agilidad
            },
            "special_move": "Impacto de Relámpago Cósmico",
            "rarity_class": "Reliquia Sagrada de Grayskull" if grading >= 9.5 else "Guardián de Nueva Eternia"
        }
