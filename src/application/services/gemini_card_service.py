import base64
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import httpx
from src.core.config import settings

logger = logging.getLogger(__name__)


class GeminiCardService:
    """
    Servicio de Transformación Mágica de Cromos Digitales mediante la API multimodal de Google Gemini.
    Toma la foto de una figura de Masters of the Universe (incluso dentro de su blíster o empaque),
    extrae al personaje de forma coherente con sus accesorios/armas reales y lo recrea fuera del blíster
    en una postura de acción épica en Eternia, en 4 estilos de ilustradores legendarios de MOTU.
    """

    STYLES_CONFIG = {
        "obrero_norem_80s": {
            "name": "🎨 Box-Art Óleo 80s (Rudy Obrero & Earl Norem)",
            "artist": "Rudy Obrero, Earl Norem, William George",
            "prompt": (
                "Look at the Masters of the Universe action figure / toy in the reference image. "
                "Identify the specific character, its costume, face/helmet, color scheme, and any weapons/accessories (swords, axes, staves, blasters). "
                "CRITICAL INSTRUCTION: Remove and ignore all plastic blister bubbles, cardboard packaging, pegs, and stands. "
                "Recreate and paint this character as a living, heroic fantasy warrior liberated from any packaging, "
                "depicted in a powerful dynamic battle action pose in the rugged fantasy world of Eternia near Castle Grayskull, "
                "with atmospheric stormy skies and glowing lightning. "
                "The character is actively wielding their authentic weapons and accessories. "
                "Art style: Authentic 1980s Mattel toy box art oil-on-canvas painting style by Rudy Obrero, Earl Norem, and William George. "
                "Rich painterly oil textures, dramatic chiaroscuro lighting, visceral muscular heroic fantasy anatomy, vivid saturated 80s palette."
            )
        },
        "alcala_texeira_minicomic": {
            "name": "⚔️ Mini-Cómic Vintage 80s (Alfredo Alcala & Mark Texeira)",
            "artist": "Alfredo Alcala, Mark Texeira, Bruce Timm",
            "prompt": (
                "Look at the Masters of the Universe action figure in the reference image. "
                "Identify the exact character and its weapons/accessories. "
                "CRITICAL INSTRUCTION: Completely extract the character outside of any blister packaging, toy card, or background. "
                "Illustrate the character in a ferocious, dynamic combat action pose battling amidst the perilous rocks of Snake Mountain or Eternian Lava Falls, "
                "brandishing their iconic weapons and gear with heroic intensity. "
                "Art style: Vintage 1980s Masters of the Universe mini-comic book illustration by Alfredo Alcala, Mark Texeira, and Bruce Timm. "
                "Dense handcrafted cross-hatching, heavy expressive black ink shadows, vintage four-color printing with subtle Ben-Day halftone dots, "
                "classic barbarian sword-and-sorcery comic aesthetic."
            )
        },
        "gimenez_santalucia_modern": {
            "name": "✨ Cardback Moderno (Axel Gimenez & Emiliano Santalucia)",
            "artist": "Axel Gimenez, Emiliano Santalucia",
            "prompt": (
                "Look at the Masters of the Universe toy character in the reference image. "
                "Identify the character design and its signature accessories. "
                "CRITICAL INSTRUCTION: Free the character completely from any toy packaging, plastic bubble, or blister card. "
                "Illustrate the character leaping into an epic battle stance outside the Royal Palace of Eternia or the Mystic Mountains, "
                "unleashing the glowing energy of their signature weapons and magical gear with radiant light effects. "
                "Art style: Modern official Masters of the Universe Origins, Classics, and Masterverse packaging art by Axel Gimenez and Emiliano Santalucia. "
                "Crisp hyper-clean ink linework, vibrant digital cel-shading, rich atmospheric lighting gradients, dynamic superhero action perspective."
            )
        },
        "heavy_metal_dark_eternia": {
            "name": "🌌 Dark Fantasy Épico (Kenneth Rocafort & Simon Bisley)",
            "artist": "Kenneth Rocafort, Simon Bisley, Mondo MOTU",
            "prompt": (
                "Look at the Masters of the Universe action figure in the reference image. "
                "Extract the character and its weapons/accessories completely out of any blister bubble or packaging. "
                "Reimagine the character in a gritty, high-stakes life-or-death battle in the mystical Dark Lands or Subternia of Eternia, "
                "wielding their weapons with glowing arcane runes, flying sparks, and atmospheric battle dust. "
                "Art style: Hyper-detailed Heavy Metal dark fantasy illustration inspired by Kenneth Rocafort, Simon Bisley, and Mondo MOTU art. "
                "Intricate battle-worn armor textures, volumetric fog, dramatic backlit highlights, intense cinematic mood, dark mature sword-and-sorcery masterpiece."
            )
        }
    }

    # Aliases para compatibilidad hacia atrás
    STYLE_ALIASES = {
        "oil_vintage": "obrero_norem_80s",
        "comic_retro": "alcala_texeira_minicomic",
        "cinematic_4k": "heavy_metal_dark_eternia",
        "rpg_lore": "gimenez_santalucia_modern"
    }

    @classmethod
    def _resolve_style_key(cls, style: str) -> str:
        canonical = cls.STYLE_ALIASES.get(style, style)
        return canonical if canonical in cls.STYLES_CONFIG else "obrero_norem_80s"

    @classmethod
    async def enhance_card(
        cls,
        product_name: str,
        sub_category: Optional[str] = "MOTU Origins",
        style: str = "obrero_norem_80s",
        condition: str = "MOC",
        grading: float = 10.0,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta la transmutación mágica del cromo mediante Gemini multimodal (Flash Image).
        """
        sub_cat = sub_category or "MOTU Origins"
        resolved_style = cls._resolve_style_key(style)
        style_info = cls.STYLES_CONFIG[resolved_style]

        # 1. Generación de Lore canónico & Stats RPG con Gemini Flash
        lore_data = await cls._generate_lore_and_stats(product_name, sub_cat, condition, grading, style_info["name"])

        # 2. Generación o Adaptación Visual con Gemini Flash Image (Nano Banana)
        image_data = await cls._generate_ai_art(
            product_name=product_name,
            sub_category=sub_cat,
            style=resolved_style,
            image_url=image_url,
            image_base64=image_base64
        )

        return {
            "style": resolved_style,
            "style_name": style_info["name"],
            "image_base64": image_data,
            "lore": lore_data.get("lore"),
            "stats": lore_data.get("stats"),
            "special_move": lore_data.get("special_move"),
            "rarity_class": lore_data.get("rarity_class")
        }

    @classmethod
    async def _resolve_image_bytes(
        cls,
        image_url: Optional[str],
        image_base64: Optional[str]
    ) -> Optional[Tuple[str, str]]:
        """
        Resuelve la imagen de entrada a (mime_type, base64_data).
        """
        # Caso 1: image_base64 proporcionado directamente
        if image_base64:
            if image_base64.startswith("data:"):
                try:
                    header, data = image_base64.split(",", 1)
                    mime = header.split(";")[0].replace("data:", "")
                    return (mime or "image/jpeg", data)
                except Exception:
                    return ("image/jpeg", image_base64)
            return ("image/jpeg", image_base64)

        # Caso 2: image_url proporcionado
        if image_url:
            if image_url.startswith("data:"):
                try:
                    header, data = image_url.split(",", 1)
                    mime = header.split(";")[0].replace("data:", "")
                    return (mime or "image/jpeg", data)
                except Exception:
                    pass

            if image_url.startswith("http://") or image_url.startswith("https://"):
                try:
                    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                        resp = await client.get(image_url)
                        if resp.status_code == 200:
                            content_type = resp.headers.get("content-type", "image/jpeg").split(";")[0]
                            b64 = base64.b64encode(resp.content).decode("utf-8")
                            return (content_type, b64)
                except Exception as e:
                    logger.warning(f"No se pudo descargar imagen desde {image_url}: {e}")

            # Intentar leer desde caché de imagen local si es ruta relativa
            try:
                local_candidates = [
                    Path(image_url),
                    Path(settings.IMAGE_CACHE_DIR) / Path(image_url).name,
                    Path("data/image_cache") / Path(image_url).name
                ]
                for path in local_candidates:
                    if path.exists() and path.is_file():
                        with open(path, "rb") as f:
                            data_bytes = f.read()
                            suffix = path.suffix.lower().replace(".", "")
                            mime = f"image/{suffix}" if suffix in ["png", "jpeg", "jpg", "webp"] else "image/jpeg"
                            b64 = base64.b64encode(data_bytes).decode("utf-8")
                            return (mime, b64)
            except Exception as e:
                logger.warning(f"Error comprobando archivo local {image_url}: {e}")

        return None

    @classmethod
    async def _generate_ai_art(
        cls,
        product_name: str,
        sub_category: str,
        style: str,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None
    ) -> Optional[str]:
        """
        Invoca la API multimodal de Gemini (gemini-2.5-flash-image / nano-banana) para extraer
        al muñeco del blíster y pintarlo en Eternia con su estilo artístico seleccionado.
        """
        if not settings.GEMINI_API_KEY:
            logger.info("Sin GEMINI_API_KEY: devolviendo modo determinista.")
            return None

        resolved_style = cls._resolve_style_key(style)
        style_cfg = cls.STYLES_CONFIG[resolved_style]
        prompt_text = (
            f"Masters of the Universe figure: '{product_name}' ({sub_category}).\n"
            f"{style_cfg['prompt']}"
        )

        img_data = await cls._resolve_image_bytes(image_url, image_base64)

        parts = [{"text": prompt_text}]
        if img_data:
            mime_type, b64_str = img_data
            parts.append({
                "inlineData": {
                    "mimeType": mime_type,
                    "data": b64_str
                }
            })
            logger.info(f"Enviando imagen de referencia ({mime_type}, {len(b64_str)} chars b64) para estilo {resolved_style}")

        payload = {
            "contents": [{
                "parts": parts
            }],
            "generationConfig": {
                "responseModalities": ["IMAGE"]
            }
        }

        models_to_try = [
            "gemini-2.5-flash-image",
            "gemini-3.1-flash-image",
            "gemini-3-pro-image",
            "gemini-3.1-flash-lite-image"
        ]

        async with httpx.AsyncClient(timeout=60.0) as client:
            for model in models_to_try:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.GEMINI_API_KEY}"
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            resp_parts = candidates[0].get("content", {}).get("parts", [])
                            for part in resp_parts:
                                if "inlineData" in part:
                                    mime = part["inlineData"].get("mimeType", "image/png")
                                    b64 = part["inlineData"].get("data")
                                    if b64:
                                        logger.info(f"Arte MOTU generado con éxito usando {model} ({len(b64)} bytes base64)")
                                        return f"data:{mime};base64,{b64}"
                    else:
                        logger.warning(f"Modelo {model} respondió {resp.status_code}: {resp.text[:140]}")
                except Exception as e:
                    logger.warning(f"Error generando arte con modelo {model}: {e}")

        return None

    @classmethod
    async def _generate_lore_and_stats(
        cls,
        product_name: str,
        sub_category: str,
        condition: str,
        grading: float,
        style_name: str = ""
    ) -> Dict[str, Any]:
        """
        Genera el trasfondo canónico épico y estadísticas RPG con Gemini Flash.
        """
        if settings.GEMINI_API_KEY:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
            prompt = (
                f"Genera una ficha canónica de combate y coleccionismo en JSON para la figura de Masters of the Universe '{product_name}' "
                f"({sub_category}, estado {condition}, grado {grading}/10, estilo visual '{style_name}'). "
                "Responde ÚNICAMENTE un JSON válido con este formato exacto:\n"
                "{\n"
                '  "lore": "Texto épico canónico de 2 frases sobre la figura en la batalla por Eternia.",\n'
                '  "stats": {\n'
                '    "fuerza": 92,\n'
                '    "magia": 85,\n'
                '    "defensa": 90,\n'
                '    "agilidad": 88\n'
                "  },\n"
                '  "special_move": "Nombre del Ataque Definitivo o Técnica Legendaria",\n'
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

