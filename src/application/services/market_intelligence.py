
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
        
        results = {
            "Retail": [],
            "Peer-to-Peer": []
        }
        
        for source_type in ["Retail", "Peer-to-Peer"]:
            # Query consolidada: Precio medio por mes/año
            # Usamos PriceHistory si existe, o el precio actual de la oferta como fallback
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
        
        return results

    def calculate_ideal_bid(self, product_id: int) -> Dict[str, Any]:
        """
        Calcula el precio idóneo para pujar basándose en el percentil 25 
        de los items vendidos recientemente.
        """
        # Obtenemos los precios de items marcados como "Vendidos" (o el min_price histórico)
        sold_prices = self.db.query(OfferModel.price).filter(
            OfferModel.product_id == product_id,
            OfferModel.source_type == "Peer-to-Peer",
            OfferModel.is_sold == True
        ).all()
        
        prices = [p[0] for p in sold_prices if p[0] > 0]
        
        if not prices:
            # Fallback a min histórico de items activos si no hay registros de venta
            active_min = self.db.query(func.min(OfferModel.min_price)).filter(
                OfferModel.product_id == product_id,
                OfferModel.source_type == "Peer-to-Peer"
            ).scalar()
            return {
                "ideal_bid": active_min or 0.0,
                "confidence": "low",
                "reason": "Basado en precio mínimo activo (sin datos de venta real)"
            }
            
        prices.sort()
        # Percentil 25: Un precio competitivo pero realista
        idx = int(len(prices) * 0.25)
        ideal = prices[idx]
        
        return {
            "ideal_bid": round(ideal, 2),
            "confidence": "high" if len(prices) > 5 else "medium",
            "avg_sold": round(sum(prices) / len(prices), 2),
            "total_samples": len(prices)
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
