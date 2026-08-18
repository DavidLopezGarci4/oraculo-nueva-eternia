import pytest
from unittest.mock import patch, MagicMock
from src.application.services.budget_optimizer_service import BudgetOptimizerService
from src.domain.models import ProductModel, OfferModel

def test_budget_optimizer_empty_target():
    """Prueba que el optimizador maneja presupuestos cuando no hay productos candidatos."""
    with patch("src.application.services.budget_optimizer_service.SessionCloud") as mock_session:
        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db
        mock_db.query.return_value.all.return_value = []

        res = BudgetOptimizerService.optimize_cart(budget_limit=100.0, user_id=2)
        assert res["budget_limit"] == 100.0
        assert res["total_spent"] == 0.0
        assert res["items_count"] == 0
        assert res["selected_items"] == []

def test_budget_optimizer_greedy_selection():
    """Prueba la selección voraz y el desglose de tiendas respetando el límite de presupuesto."""
    with patch("src.application.services.budget_optimizer_service.SessionCloud") as mock_session:
        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db
        
        # Simular productos
        p1 = ProductModel(id=1, name="He-Man Origins", retail_price=19.99, p25_price=22.0, is_vintage=False)
        p2 = ProductModel(id=2, name="Skeletor Origins", retail_price=19.99, p25_price=25.0, is_vintage=False)
        
        # Simular ofertas
        o1 = OfferModel(id=101, product_id=1, price=14.0, shop_name="Vinted", is_available=True, url="https://vinted.es/1")
        o2 = OfferModel(id=102, product_id=2, price=18.0, shop_name="Wallapop", is_available=True, url="https://wallapop.es/2")

        # Mock de consultas
        def mock_query(model):
            q = MagicMock()
            if model == ProductModel:
                q.filter.return_value.all.return_value = [p1, p2]
            elif model == OfferModel:
                q.filter.return_value.all.return_value = [o1, o2]
            else:
                q.filter.return_value.all.return_value = []
                q.all.return_value = []
            return q

        mock_db.query.side_effect = mock_query

        res = BudgetOptimizerService.optimize_cart(
            budget_limit=50.0,
            user_id=2,
            target_product_ids=[1, 2]
        )

        assert res["budget_limit"] == 50.0
        assert res["items_count"] == 2
        assert res["total_spent"] <= 50.0
        assert "Vinted" in res["stores_breakdown"]
        assert "Wallapop" in res["stores_breakdown"]
