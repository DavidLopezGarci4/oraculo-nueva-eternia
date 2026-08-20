import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from src.interfaces.api.routers.system import get_tcg_layouts, save_tcg_layouts
from src.domain.models import UserModel


@pytest.mark.asyncio
async def test_get_tcg_layouts_empty():
    """Verifica que si no hay configuración guardada devuelva dict vacío sin fallar."""
    mock_user = MagicMock(spec=UserModel)
    mock_user.role = "admin"
    mock_user.username = "David"

    with patch("src.interfaces.api.routers.system.SessionCloud") as mock_session_cls:
        mock_db = MagicMock()
        mock_session_cls.return_value.__enter__.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = await get_tcg_layouts(current_user=mock_user)
        assert result == {}


@pytest.mark.asyncio
async def test_save_tcg_layouts_non_admin():
    """Verifica que un usuario no admin reciba 403 Forbidden al intentar guardar."""
    mock_user = MagicMock(spec=UserModel)
    mock_user.role = "user"
    mock_user.username = "Pepe"

    with pytest.raises(HTTPException) as exc_info:
        await save_tcg_layouts(layouts={"castle_grayskull": {}}, current_user=mock_user)
    
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_save_tcg_layouts_admin_success():
    """Verifica que un admin guarde exitosamente la matriz de coordenadas."""
    mock_user = MagicMock(spec=UserModel)
    mock_user.role = "admin"
    mock_user.username = "David"

    with patch("src.interfaces.api.routers.system.SessionCloud") as mock_session_cls:
        mock_db = MagicMock()
        mock_session_cls.return_value.__enter__.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None

        sample_layouts = {
            "castle_grayskull": {
                "header": {"top": "10.4%"},
                "textBox": {"top": "53.5%"}
            }
        }
        res = await save_tcg_layouts(layouts=sample_layouts, current_user=mock_user)
        assert res["status"] == "success"
        assert "guardada exitosamente" in res["message"]
        assert mock_db.commit.called
