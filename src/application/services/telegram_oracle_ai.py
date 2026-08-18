import re
from typing import Dict, Any, List, Optional
import httpx
from loguru import logger

from src.core.config import settings
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import (
    ProductModel,
    CollectionItemModel,
    PendingMatchModel,
    OfferModel,
    UserModel
)
from src.application.services.logistics_service import LogisticsService

class OracleAssistantAI:
    """
    Asistente Conversacional Inteligente para Telegram ("El Ojo del Oráculo").
    Permite responder preguntas en lenguaje natural sobre la colección, precios y chollos
    mediante llamadas de función seguras (de solo lectura).
    Funciona tanto con la API de Google Gemini Flash como con un motor semántico determinista de reserva.
    """

    @classmethod
    async def process_user_query(cls, text: str, user_id: int = 2) -> str:
        """Procesa una consulta en lenguaje natural y devuelve la respuesta formateada para Telegram."""
        text_clean = text.strip()
        if not text_clean:
            return "🗡️ Saludos, Soberano. ¿En qué puedo iluminarte hoy sobre el inventario y mercado de Nueva Eternia?"

        # 1. Si hay clave de Gemini, intentamos Function Calling con Gemini Flash
        if settings.GEMINI_API_KEY:
            try:
                ai_response = await cls._query_gemini_flash(text_clean, user_id)
                if ai_response:
                    return ai_response
            except Exception as ex:
                logger.warning(f"Fallback a motor semántico local tras error en Gemini: {ex}")

        # 2. Motor semántico determinista local (100% offline, 0€ de coste)
        return cls._process_with_local_brain(text_clean, user_id)

    @classmethod
    async def _query_gemini_flash(cls, text: str, user_id: int) -> Optional[str]:
        """Consulta a Gemini Flash mediante Function Calling estructurado."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={settings.GEMINI_API_KEY}"
        
        tools = [{
            "function_declarations": [
                {
                    "name": "get_collection_summary",
                    "description": "Obtiene el resumen financiero de la colección del usuario: número de figuras, valor total de mercado, dinero invertido y beneficio/ROI."
                },
                {
                    "name": "get_top_opportunities",
                    "description": "Obtiene las mejores oportunidades y gangas activas en tiendas y plataformas P2P ordenadas por Landed Price real.",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "limit": {"type": "INTEGER", "description": "Número de ofertas a devolver (def: 5)"}
                        }
                    }
                },
                {
                    "name": "search_figure_price",
                    "description": "Busca el precio medio, precio de salida (MSRP), suelo P25 y estado de una figura concreta en el catálogo.",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "figure_name": {"type": "STRING", "description": "Nombre de la figura (ej: 'He-Man', 'Skeletor', 'Teela')"}
                        },
                        "required": ["figure_name"]
                    }
                },
                {
                    "name": "get_missing_wishlist",
                    "description": "Muestra las figuras que el usuario tiene en seguimiento o le faltan en su colección."
                }
            ]
        }]

        system_instruction = {
            "parts": [{
                "text": (
                    "Eres 'El Ojo del Oráculo', el asistente sabio de inteligencia patrimonial y coleccionismo MOTU "
                    "de Nueva Eternia. Tu tono es respetuoso, heroico y conciso. Responde en español con formato HTML "
                    "para Telegram (usa <b>, <i>, <code>). Utiliza siempre las herramientas para obtener datos verídicos."
                )
            }]
        }

        payload = {
            "system_instruction": system_instruction,
            "contents": [{"role": "user", "parts": [{"text": text}]}],
            "tools": tools
        }

        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                logger.warning(f"Gemini API error {resp.status_code}: {resp.text}")
                return None

            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return None

            first_part = candidates[0].get("content", {}).get("parts", [{}])[0]
            
            # Si Gemini solicitó una llamada a función
            if "functionCall" in first_part:
                fn_name = first_part["functionCall"]["name"]
                fn_args = first_part["functionCall"].get("args", {})
                
                # Ejecutar la función de solo lectura
                fn_result = cls._execute_tool(fn_name, fn_args, user_id)
                
                # Segunda llamada a Gemini con el resultado de la función
                second_payload = {
                    "system_instruction": system_instruction,
                    "contents": [
                        {"role": "user", "parts": [{"text": text}]},
                        {"role": "model", "parts": [first_part]},
                        {
                            "role": "function",
                            "parts": [{
                                "functionResponse": {
                                    "name": fn_name,
                                    "response": {"result": fn_result}
                                }
                            }]
                        }
                    ]
                }
                
                resp2 = await client.post(url, json=second_payload)
                if resp2.status_code == 200:
                    cand2 = resp2.json().get("candidates", [])
                    if cand2:
                        return cand2[0].get("content", {}).get("parts", [{}])[0].get("text")

            return first_part.get("text")

    @classmethod
    def _execute_tool(cls, fn_name: str, args: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Ejecuta de forma segura funciones de solo lectura."""
        if fn_name == "get_collection_summary":
            return cls._tool_collection_summary(user_id)
        elif fn_name == "get_top_opportunities":
            return cls._tool_top_opportunities(args.get("limit", 5))
        elif fn_name == "search_figure_price":
            return cls._tool_figure_price(args.get("figure_name", ""))
        elif fn_name == "get_missing_wishlist":
            return cls._tool_missing_wishlist(user_id)
        return {"error": "Función no reconocida"}

    @classmethod
    def _process_with_local_brain(cls, query: str, user_id: int) -> str:
        """Motor semántico de reserva basado en patrones de lenguaje natural."""
        import unicodedata
        q_norm = "".join(c for c in unicodedata.normalize('NFD', query.lower()) if unicodedata.category(c) != 'Mn')

        # 1. Consulta de valor de colección / resumen financiero
        if any(w in q_norm for w in ["cuanto vale", "valor", "patrimonio", "coleccion", "invertido", "resumen", "total", "roi", "beneficio"]):
            data = cls._tool_collection_summary(user_id)
            return (
                "🏰 <b>[Informe Patrimonial de La Fortaleza]</b>\n\n"
                f"• 📦 <b>Figuras Custodiadas:</b> {data['total_items']}\n"
                f"• 💰 <b>Inversión Total:</b> {data['total_invested']:.2f} €\n"
                f"• 📈 <b>Valor de Mercado:</b> {data['market_value']:.2f} €\n"
                f"• 💎 <b>Plusvalía / ROI:</b> <b>{data['profit']:+.2f} €</b> ({data['roi_pct']:+.1f}%)\n\n"
                f"🛡️ <i>{data['moc_count']} en blister (MOC) | {data['loose_count']} sueltas (Loose)</i>"
            )

        # 2. Consulta de chollos / mejores oportunidades activas
        if any(w in q_norm for w in ["chollos", "gangas", "oportunidades", "ofertas", "mas barato", "comprar"]):
            data = cls._tool_top_opportunities(5)
            deals = data.get("deals", [])
            if not deals:
                return "🛡️ <i>No hay chollos extremos registrados en este momento. El Centinela sigue vigilando.</i>"
            
            lines = [
                f"• <b>{d['name']}</b> a <b>{d['price']:.2f}€</b> (Landed: {d['landed_price']:.2f}€ | 💰 <b>-{d['savings_pct']:.0f}%</b>) en {d['shop']}\n  ↳ <a href=\"{d['url']}\">Ver Oferta</a>"
                for d in deals
            ]
            return "🏹 <b>[Mejores Oportunidades por Landed Price]</b>\n\n" + "\n\n".join(lines)

        # 3. Consulta de precio de una figura concreta
        # Extraer nombre potencial
        match_search = re.search(r'(?:precio|cuanto cuesta|valor de|busca a|hay algun|tienes a)\s+([a-zA-Z0-9\-\s]+)', q_norm)
        search_term = match_search.group(1).strip() if match_search else q_norm
        
        # Limpiar palabras vacías
        for noise in ["por menos de", "en vinted", "en wallapop", "que me falta", "origins", "masterverse"]:
            search_term = search_term.replace(noise, "").strip()

        if len(search_term) >= 3:
            data = cls._tool_figure_price(search_term)
            if data.get("found"):
                fig = data["figure"]
                in_coll = "✅ <i>En tu Fortaleza</i>" if fig["in_collection"] else "⏳ <i>Pendiente de conseguir</i>"
                return (
                    f"🔍 <b>[Ficha de Mercado: {fig['name']}]</b>\n\n"
                    f"• 🏷️ <b>Precio Salida (MSRP):</b> {fig['retail_price']:.2f} €\n"
                    f"• ⚖️ <b>Suelo Mercado (P25):</b> {fig['p25_price']:.2f} €\n"
                    f"• 📦 <b>Línea / Subcategoría:</b> {fig['sub_category']}\n"
                    f"• 🛡️ <b>Estado en tu Colección:</b> {in_coll}\n"
                    f"{'• 🔥 <b>Mejor Oferta Actual:</b> ' + str(fig['best_offer']) + ' €' if fig.get('best_offer') else ''}"
                )

        # 4. Respuesta general
        return (
            "🔮 <b>[El Ojo del Oráculo]</b>\n\n"
            "Puedo ayudarte con consultas como:\n"
            "• <i>'¿Cuánto vale mi colección hoy?'</i>\n"
            "• <i>'¿Cuáles son las mejores gangas de Vinted o tiendas?'</i>\n"
            "• <i>'¿Cuál es el precio de mercado de Skeletor o Teela?'</i>\n"
            "• <i>'¿Qué figuras tengo pendientes en mi lista de deseos?'</i>"
        )

    # --- FUNCIONES DE ACCESO A BASE DE DATOS (SOLO LECTURA) ---

    @classmethod
    def _tool_collection_summary(cls, user_id: int) -> Dict[str, Any]:
        with SessionCloud() as db:
            items = db.query(CollectionItemModel).filter(
                CollectionItemModel.owner_id == user_id,
                CollectionItemModel.acquired == True
            ).all()

            total_invested = sum(i.purchase_price or 0.0 for i in items)
            market_value = sum(
                (i.product.p25_price or i.product.retail_price or i.purchase_price or 0.0)
                for i in items if i.product
            )
            profit = market_value - total_invested
            roi_pct = (profit / total_invested * 100) if total_invested > 0 else 0.0
            
            moc_count = sum(1 for i in items if (i.condition or "").upper() == "MOC")
            loose_count = len(items) - moc_count

            return {
                "total_items": len(items),
                "total_invested": total_invested,
                "market_value": market_value,
                "profit": profit,
                "roi_pct": roi_pct,
                "moc_count": moc_count,
                "loose_count": loose_count
            }

    @classmethod
    def _tool_top_opportunities(cls, limit: int = 5) -> Dict[str, Any]:
        with SessionCloud() as db:
            matches = db.query(PendingMatchModel).filter(
                PendingMatchModel.validation_status == "PENDING",
                PendingMatchModel.is_blocked == False,
                PendingMatchModel.price > 0
            ).order_by(PendingMatchModel.price.asc()).limit(30).all()

            deals = []
            for m in matches:
                landed = m.price + (5.0 + m.price * 0.02 if m.shop_name == "Vinted" else 5.0)
                deals.append({
                    "name": m.scraped_name,
                    "price": m.price,
                    "landed_price": landed,
                    "shop": m.shop_name,
                    "url": m.url,
                    "savings_pct": 25.0
                })
            
            deals.sort(key=lambda x: x["landed_price"])
            return {"deals": deals[:limit]}

    @classmethod
    def _tool_figure_price(cls, figure_name: str) -> Dict[str, Any]:
        with SessionCloud() as db:
            term = f"%{figure_name.strip()}%"
            prod = db.query(ProductModel).filter(
                ProductModel.name.ilike(term),
                ProductModel.is_vintage == False
            ).first()

            if not prod:
                return {"found": False}

            in_coll = db.query(CollectionItemModel).filter(
                CollectionItemModel.product_id == prod.id,
                CollectionItemModel.owner_id == 2,
                CollectionItemModel.acquired == True
            ).count() > 0

            best_offer = db.query(OfferModel.price).filter(
                OfferModel.product_id == prod.id,
                OfferModel.is_available == True
            ).order_by(OfferModel.price.asc()).first()

            return {
                "found": True,
                "figure": {
                    "name": prod.name,
                    "sub_category": prod.sub_category or "Origins",
                    "retail_price": prod.retail_price or 19.99,
                    "p25_price": prod.p25_price or prod.retail_price or 19.99,
                    "in_collection": in_coll,
                    "best_offer": best_offer[0] if best_offer else None
                }
            }

    @classmethod
    def _tool_missing_wishlist(cls, user_id: int) -> Dict[str, Any]:
        with SessionCloud() as db:
            owned_ids = {
                i.product_id for i in db.query(CollectionItemModel.product_id).filter(
                    CollectionItemModel.owner_id == user_id,
                    CollectionItemModel.acquired == True
                ).all()
            }
            missing = db.query(ProductModel.name).filter(
                ProductModel.id.notin_(owned_ids),
                ProductModel.is_vintage == False
            ).limit(10).all()

            return {"missing_figures": [m[0] for m in missing]}

