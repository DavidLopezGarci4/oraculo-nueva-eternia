
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from src.domain.models import OfferModel, PriceHistoryModel, ProductModel

class MarketIntelligenceService:
    def __init__(self, db: Session):
        self.db = db

    def get_monthly_price_evolution(self, product_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        Calcula la evolución mensual del precio medio para un producto, 
        segregando por Retail y P2P.
        """
        # Obtenemos datos de los últimos 6 meses
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        now = datetime.utcnow()
        current_month_key = f"{now.year}-{now.month:02d}"
        
        results = {
            "Retail": [],
            "Peer-to-Peer": []
        }
        
        for source_type in ["Retail", "Peer-to-Peer"]:
            # Query consolidada: Precio medio por mes/año
            stats = self.db.query(
                func.extract('year', PriceHistoryModel.recorded_at).label('year'),
                func.extract('month', PriceHistoryModel.recorded_at).label('month'),
                func.avg(PriceHistoryModel.price).label('avg_price')
            ).join(OfferModel).filter(
                OfferModel.product_id == product_id,
                OfferModel.source_type == source_type,
                PriceHistoryModel.recorded_at >= six_months_ago
            ).group_by('year', 'month').order_by('year', 'month').all()
            
            for s in stats:
                results[source_type].append({
                    "date": f"{int(s.year)}-{int(s.month):02d}",
                    "avg_price": round(s.avg_price, 2)
                })

            # FALLBACK: Si no hay historial, usamos el precio medio actual de las ofertas activas
            if not results[source_type]:
                current_avg = self.db.query(func.avg(OfferModel.price)).filter(
                    OfferModel.product_id == product_id,
                    OfferModel.source_type == source_type,
                    OfferModel.is_available == True
                ).scalar()
                
                if current_avg:
                    results[source_type].append({
                        "date": current_month_key,
                        "avg_price": round(current_avg, 2)
                    })
        
        return results

    def calculate_ideal_bid(self, product_id: int) -> Dict[str, Any]:
        """
        Calcula el precio idóneo para pujar basándose en el percentil 25 
        de los items vendidos recientemente, con fallback a items activos.
        """
        # 1. Intentamos obtener precios de items VENDIDOS (Realidad de mercado)
        sold_prices = self.db.query(OfferModel.price).filter(
            OfferModel.product_id == product_id,
            OfferModel.source_type == "Peer-to-Peer",
            OfferModel.is_sold == True
        ).all()
        
        prices = [p[0] for p in sold_prices if p[0] > 0]
        confidence = "high" if len(prices) > 5 else "medium"
        reason = "Basado en transacciones reales (P2P Sold)"

        if not prices:
            # 2. FALLBACK TÁCTICO: Percentil 25 de items ACTIVOS
            # (Si no hay ventas, buscamos el precio más competitivo de lo que hay ahora)
            active_prices = self.db.query(OfferModel.price).filter(
                OfferModel.product_id == product_id,
                OfferModel.source_type == "Peer-to-Peer",
                OfferModel.is_available == True
            ).all()
            prices = [p[0] for p in active_prices if p[0] > 0]
            confidence = "low"
            reason = "Basado en el percentil 25 de ofertas activas (Cálculo Táctico)"

        if not prices:
            # 3. ÚLTIMO RECURSO: Precio de lanzamiento o 0
            retail = self.db.query(ProductModel.retail_price).filter(ProductModel.id == product_id).scalar()
            return {
                "ideal_bid": retail or 0.0,
                "confidence": "minimum",
                "reason": "Sin datos de mercado P2P. Se usa precio de venta sugerido (Retail)."
            }
            
        prices.sort()
        # Percentil 25: Un precio competitivo pero realista
        idx = int(len(prices) * 0.25)
        ideal = prices[idx]
        
        return {
            "ideal_bid": round(ideal, 2),
            "confidence": confidence,
            "avg_sold": round(sum(prices) / len(prices), 2),
            "total_samples": len(prices),
            "reason": reason
        }

    def get_market_summary(self, product_id: int) -> Dict[str, Any]:
        """
        Resumen ejecutivo para el dashboard de inteligencia.
        """
        product = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            return {}
            
        evolution = self.get_monthly_price_evolution(product_id)
        bid_strategy = self.calculate_ideal_bid(product_id)
        
        # Segregated Market Lows
        retail_low = self.db.query(func.min(OfferModel.price)).filter(
            OfferModel.product_id == product_id,
            OfferModel.source_type == "Retail",
            OfferModel.is_available == True
        ).scalar()
        
        p2p_low = self.db.query(func.min(OfferModel.price)).filter(
            OfferModel.product_id == product_id,
            OfferModel.source_type == "Peer-to-Peer",
            OfferModel.is_available == True
        ).scalar()
        
        return {
            "product_name": product.name,
            "retail_price_official": product.retail_price,
            "evolution": evolution,
            "bid_strategy": bid_strategy,
            "current_retail_low": retail_low,
            "current_p2p_low": p2p_low,
            # Fallback for old UI
            "current_market_low": retail_low or p2p_low
        }

    def sync_product_statistics(self, product_id: int):
        """
        Calcula y persiste las estadísticas segregadas en el ProductModel.
        """
        # 1. Retail Stats
        retail_avg = self.db.query(func.avg(OfferModel.price)).filter(
            OfferModel.product_id == product_id,
            OfferModel.source_type == "Retail",
            OfferModel.is_available == True
        ).scalar()
        
        # 2. P2P Stats (Using Sold prices if available, otherwise Active)
        p2p_prices = self.db.query(OfferModel.price).filter(
            OfferModel.product_id == product_id,
            OfferModel.source_type == "Peer-to-Peer",
            OfferModel.is_sold == True
        ).all()
        
        if not p2p_prices:
             p2p_prices = self.db.query(OfferModel.price).filter(
                OfferModel.product_id == product_id,
                OfferModel.source_type == "Peer-to-Peer",
                OfferModel.is_available == True
            ).all()
            
        p2p_vals = [float(p[0]) for p in p2p_prices if p[0] > 0]
        p2p_avg = sum(p2p_vals) / len(p2p_vals) if p2p_vals else 0.0
        
        p2p_vals.sort()
        p2p_p25 = p2p_vals[int(len(p2p_vals) * 0.25)] if p2p_vals else 0.0

        # Update Product
        product = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if product:
            product.avg_retail_price = retail_avg or 0.0
            product.avg_p2p_price = p2p_avg
            product.p25_p2p_price = p2p_p25
            # Legacy sync
            product.avg_market_price = retail_avg or p2p_avg
            self.db.add(product)
            self.db.commit()
            return True
        return False
