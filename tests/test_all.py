import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, Message
from telegram.ext import ContextTypes
from datetime import datetime, timezone
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import start, get_name, cancel, help_command, ask, ask_handler

# -------- UNIT TESTS --------
@pytest.fixture
def mock_update():
    update = MagicMock(spec=Update)
    update.effective_user.id = 12345
    update.message = MagicMock(spec=Message)
    update.message.text = "test"
    update.message.date = datetime.now(timezone.utc)
    update.message.reply_text = AsyncMock()
    return update

@pytest.fixture
def mock_context():
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    return context

@pytest.mark.asyncio
async def test_start_new_user_unit(mock_update, mock_context):
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        result = await start(mock_update, mock_context)
        assert result == 1
        assert mock_update.message.reply_text.call_count >= 2

@pytest.mark.asyncio
async def test_start_existing_user_unit(mock_update, mock_context):
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        result = await start(mock_update, mock_context)
        assert result == -1

@pytest.mark.asyncio
async def test_get_name_unit(mock_update, mock_context):
    mock_update.message.text = "John Doe"
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock()
        result = await get_name(mock_update, mock_context)
        assert result == -1
        assert mock_context.user_data['name'] == "John Doe"

@pytest.mark.asyncio
async def test_cancel_unit(mock_update, mock_context):
    result = await cancel(mock_update, mock_context)
    assert result == -1
    mock_update.message.reply_text.assert_called_once()

@pytest.mark.asyncio
async def test_help_command_unit(mock_update, mock_context):
    await help_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()

# -------- INTEGRATION TESTS --------
@pytest.mark.asyncio
async def test_full_registration_and_ask_integration():
    update = MagicMock(spec=Update)
    update.effective_user.id = 12345
    update.message = MagicMock(spec=Message)
    update.message.text = "John Doe"
    update.message.date = datetime.now(timezone.utc)
    update.message.reply_text = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    with patch('httpx.AsyncClient') as mock_client:
        # 1. start (user not found)
        mock_client.return_value.__aenter__.return_value.get.return_value.status_code = 404
        result = await start(update, context)
        assert result == 1
        # 2. get_name
        mock_client.return_value.__aenter__.return_value.post = AsyncMock()
        result = await get_name(update, context)
        assert result == -1
        assert context.user_data['name'] == "John Doe"

@pytest.mark.asyncio
async def test_ask_and_ask_handler_integration():
    update = MagicMock(spec=Update)
    update.effective_user.id = 12345
    update.message = MagicMock(spec=Message)
    update.message.text = "Как дела?"
    update.message.date = datetime.now(timezone.utc)
    update.message.reply_text = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {'conv_id': 'conv_123'}
    with patch('main.model') as mock_model:
        mock_model.generate_perfect_response = AsyncMock(return_value="Все хорошо!")
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock()
            result = await ask_handler(update, context)
            assert result == 1
            mock_model.generate_perfect_response.assert_called_once_with(question="Как дела?")
            update.message.reply_text.assert_called_once()

@pytest.mark.asyncio
async def test_cancel_clears_conv_id_integration():
    update = MagicMock(spec=Update)
    update.effective_user.id = 12345
    update.message = MagicMock(spec=Message)
    update.message.reply_text = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {'conv_id': 'conv_123'}
    result = await cancel(update, context)
    assert result == -1
    assert 'conv_id' not in context.user_data

@pytest.mark.asyncio
async def test_start_network_error_integration():
    update = MagicMock(spec=Update)
    update.effective_user.id = 12345
    update.message = MagicMock(spec=Message)
    update.message.reply_text = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Network error")
        result = await start(update, context)
        assert result == -1
        update.message.reply_text.assert_called()

@pytest.mark.asyncio
async def test_get_name_network_error_integration():
    update = MagicMock(spec=Update)
    update.effective_user.id = 12345
    update.message = MagicMock(spec=Message)
    update.message.text = "John Doe"
    update.message.reply_text = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.post.side_effect = Exception("Network error")
        result = await get_name(update, context)
        assert result == -1
        update.message.reply_text.assert_called()