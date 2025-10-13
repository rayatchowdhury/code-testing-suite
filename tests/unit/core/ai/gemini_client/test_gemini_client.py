"""
Phase 8 Task 6 - Phase 3: Tests for gemini_client.py

Tests cover:
- GeminiAI initialization and configuration
- Environment variable loading
- JSON config file loading (new and legacy formats)
- Availability and readiness checking
- Cache management
- API request handling
- Error handling (HTTP errors, connection errors)
- Global client management functions
- Response generation with caching
"""

import pytest
import json
import os
import tempfile
import urllib.error
from unittest.mock import Mock, patch, MagicMock, mock_open

from src.app.core.ai.gemini_client.gemini_client import (
    GeminiAI,
    get_gemini_client,
    initialize_gemini,
    is_gemini_available,
    is_gemini_ready,
)


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def temp_config_file():
    """Create temporary config file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        config_path = f.name
    yield config_path
    if os.path.exists(config_path):
        os.unlink(config_path)


@pytest.fixture
def valid_config():
    """Valid Gemini configuration (new format)."""
    return {
        "gemini": {
            "enabled": True,
            "api_key": "AIzaSyTest1234567890abcdefghijk",
            "model": "gemini-2.5-flash",
        }
    }


@pytest.fixture
def legacy_config():
    """Legacy AI settings configuration."""
    return {
        "ai_settings": {
            "gemini_api_key": "AIzaSyTest1234567890abcdefghijk",
            "preferred_model": "gemini-2.5-flash",
            "enabled": True,
        }
    }


# ============================================================================
# Initialization Tests
# ============================================================================


class TestGeminiAIInitialization:
    """Test GeminiAI initialization."""

    def test_init_without_config(self):
        """Test initialization without config file."""
        client = GeminiAI()

        assert client._api_key is None
        assert client._enabled is False

    def test_init_with_config_file(self, temp_config_file, valid_config):
        """Test initialization with config file."""
        with open(temp_config_file, "w") as f:
            json.dump(valid_config, f)

        client = GeminiAI(config_file=temp_config_file)

        assert client._api_key == "AIzaSyTest1234567890abcdefghijk"
        assert client._model_name == "gemini-2.5-flash"
        assert client._enabled is True

    @patch.dict(
        "os.environ",
        {
            "GEMINI_API_KEY": "env_key",
            "GEMINI_MODEL": "env_model",
            "GEMINI_ENABLED": "true",
        },
    )
    def test_init_from_environment(self):
        """Test initialization from environment variables."""
        client = GeminiAI()

        assert client._api_key == "env_key"
        assert client._model_name == "env_model"
        assert client._enabled is True


# ============================================================================
# Configuration Loading Tests
# ============================================================================


class TestConfigurationLoading:
    """Test load_config method."""

    def test_load_config_new_format(self, temp_config_file, valid_config):
        """Test loading config with new gemini format."""
        with open(temp_config_file, "w") as f:
            json.dump(valid_config, f)

        client = GeminiAI()
        client.load_config(temp_config_file)

        assert client._api_key == "AIzaSyTest1234567890abcdefghijk"
        assert client._model_name == "gemini-2.5-flash"
        assert client._enabled is True

    def test_load_config_legacy_format(self, temp_config_file, legacy_config):
        """Test loading config with legacy ai_settings format."""
        with open(temp_config_file, "w") as f:
            json.dump(legacy_config, f)

        client = GeminiAI()
        client.load_config(temp_config_file)

        assert client._api_key == "AIzaSyTest1234567890abcdefghijk"
        assert client._model_name == "gemini-2.5-flash"
        assert client._enabled is True

    def test_load_config_file_not_found(self):
        """Test loading nonexistent config file."""
        client = GeminiAI()
        client.load_config("/nonexistent/config.json")

        # Should not crash, just log and disable
        assert client._enabled is False

    def test_load_config_invalid_json(self, temp_config_file):
        """Test loading config with invalid JSON."""
        with open(temp_config_file, "w") as f:
            f.write("{invalid json")

        client = GeminiAI()
        client.load_config(temp_config_file)

        assert client._enabled is False

    def test_load_config_empty_file(self, temp_config_file):
        """Test loading config with empty data."""
        with open(temp_config_file, "w") as f:
            json.dump({}, f)

        client = GeminiAI()
        client.load_config(temp_config_file)

        assert client._api_key is None
        assert client._enabled is False


# ============================================================================
# Availability Tests
# ============================================================================


class TestAvailability:
    """Test is_available and is_ready methods."""

    def test_is_available_false_when_disabled(self):
        """Test is_available returns False when disabled."""
        client = GeminiAI()
        client._enabled = False
        client._api_key = "key"

        assert client.is_available() is False

    def test_is_available_false_when_no_key(self):
        """Test is_available returns False when no API key."""
        client = GeminiAI()
        client._enabled = True
        client._api_key = None

        assert client.is_available() is False

    def test_is_available_true_when_configured(self):
        """Test is_available returns True when properly configured."""
        client = GeminiAI()
        client._enabled = True
        client._api_key = "AIzaSyTest1234567890abcdefghijk"

        assert client.is_available() is True

    def test_is_ready_disabled(self):
        """Test is_ready when service disabled."""
        client = GeminiAI()
        client._enabled = False

        ready, message = client.is_ready()

        assert ready is False
        assert "disabled" in message.lower()

    def test_is_ready_no_key(self):
        """Test is_ready when API key not configured."""
        client = GeminiAI()
        client._enabled = True
        client._api_key = None

        ready, message = client.is_ready()

        assert ready is False
        assert "key" in message.lower()

    def test_is_ready_configured(self):
        """Test is_ready when properly configured."""
        client = GeminiAI()
        client._enabled = True
        client._api_key = "key"

        ready, message = client.is_ready()

        assert ready is True
        assert "ready" in message.lower()


# ============================================================================
# Cache Management Tests
# ============================================================================


class TestCacheManagement:
    """Test cache key generation and management."""

    def test_get_cache_key_same_prompt(self):
        """Test cache key is same for identical prompts."""
        client = GeminiAI()

        key1 = client._get_cache_key("prompt")
        key2 = client._get_cache_key("prompt")

        assert key1 == key2

    def test_get_cache_key_different_prompts(self):
        """Test cache key differs for different prompts."""
        client = GeminiAI()

        key1 = client._get_cache_key("prompt1")
        key2 = client._get_cache_key("prompt2")

        assert key1 != key2

    def test_get_cache_key_with_kwargs(self):
        """Test cache key includes kwargs."""
        client = GeminiAI()

        key1 = client._get_cache_key("prompt", param1="value1")
        key2 = client._get_cache_key("prompt", param1="value2")

        assert key1 != key2

    def test_manage_cache_removes_old_entries(self):
        """Test manage_cache removes old entries when full."""
        client = GeminiAI()
        client._max_cache_size = 10

        # Fill cache beyond limit
        for i in range(15):
            client._response_cache[f"key{i}"] = f"value{i}"

        client._manage_cache()

        # Should be reduced
        assert len(client._response_cache) < 15


# ============================================================================
# API Request Tests
# ============================================================================


class TestAPIRequests:
    """Test _make_api_request method."""

    @patch("urllib.request.urlopen")
    def test_make_api_request_success(self, mock_urlopen):
        """Test successful API request."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {"candidates": [{"content": {"parts": [{"text": "AI response"}]}}]}
        ).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = False
        mock_urlopen.return_value = mock_response

        client = GeminiAI()
        client._api_key = "test_key"
        client._model_name = "gemini-2.5-flash"

        response = client._make_api_request("Test prompt")

        assert response == "AI response"

    @patch("urllib.request.urlopen")
    def test_make_api_request_empty_response(self, mock_urlopen):
        """Test API request with empty response."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"candidates": []}).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = False
        mock_urlopen.return_value = mock_response

        client = GeminiAI()
        client._api_key = "test_key"
        client._model_name = "gemini-2.5-flash"

        response = client._make_api_request("Test prompt")

        assert "Empty response" in response

    @patch("urllib.request.urlopen")
    def test_make_api_request_http_400(self, mock_urlopen):
        """Test API request with HTTP 400 error."""
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="test", code=400, msg="Bad Request", hdrs={}, fp=None
        )

        client = GeminiAI()
        client._api_key = "test_key"
        client._model_name = "gemini-2.5-flash"

        response = client._make_api_request("Test prompt")

        assert "Invalid request" in response
        assert "❌" in response

    @patch("urllib.request.urlopen")
    def test_make_api_request_http_403(self, mock_urlopen):
        """Test API request with HTTP 403 error (invalid key)."""
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="test", code=403, msg="Forbidden", hdrs={}, fp=None
        )

        client = GeminiAI()
        client._api_key = "invalid_key"
        client._model_name = "gemini-2.5-flash"

        response = client._make_api_request("Test prompt")

        assert "Invalid API key" in response or "access denied" in response.lower()

    @patch("urllib.request.urlopen")
    def test_make_api_request_http_429(self, mock_urlopen):
        """Test API request with HTTP 429 error (rate limit)."""
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="test", code=429, msg="Too Many Requests", hdrs={}, fp=None
        )

        client = GeminiAI()
        client._api_key = "test_key"
        client._model_name = "gemini-2.5-flash"

        response = client._make_api_request("Test prompt")

        assert "Too many requests" in response or "try again" in response.lower()

    @patch("urllib.request.urlopen")
    def test_make_api_request_connection_error(self, mock_urlopen):
        """Test API request with connection error."""
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        client = GeminiAI()
        client._api_key = "test_key"
        client._model_name = "gemini-2.5-flash"

        response = client._make_api_request("Test prompt")

        assert "Connection error" in response or "internet" in response.lower()

    @patch("urllib.request.urlopen")
    def test_make_api_request_generic_exception(self, mock_urlopen):
        """Test API request with generic exception."""
        mock_urlopen.side_effect = Exception("Unexpected error")

        client = GeminiAI()
        client._api_key = "test_key"
        client._model_name = "gemini-2.5-flash"

        response = client._make_api_request("Test prompt")

        assert "Error" in response
        assert "❌" in response


# ============================================================================
# Response Generation Tests
# ============================================================================


class TestResponseGeneration:
    """Test generate_response method."""

    def test_generate_response_unavailable(self):
        """Test generate_response when service unavailable."""
        client = GeminiAI()
        client._enabled = False

        response = client.generate_response("Test prompt")

        assert "not available" in response.lower()

    @patch.object(GeminiAI, "_make_api_request")
    def test_generate_response_uses_cache(self, mock_request):
        """Test generate_response uses cached responses."""
        client = GeminiAI()
        client._enabled = True
        client._api_key = "test_key"
        mock_request.return_value = "AI response"

        # First call
        response1 = client.generate_response("Test prompt")
        # Second call should use cache
        response2 = client.generate_response("Test prompt")

        assert response1 == response2
        assert mock_request.call_count == 1  # Only called once

    @patch.object(GeminiAI, "_make_api_request")
    def test_generate_response_caches_successful_only(self, mock_request):
        """Test generate_response only caches successful responses."""
        client = GeminiAI()
        client._enabled = True
        client._api_key = "test_key"
        mock_request.return_value = "❌ Error occurred"

        response = client.generate_response("Test prompt")

        # Error response should not be cached
        cache_key = client._get_cache_key("Test prompt")
        assert cache_key not in client._response_cache

    @patch.object(GeminiAI, "_make_api_request")
    def test_generate_response_manages_cache_size(self, mock_request):
        """Test generate_response manages cache size."""
        client = GeminiAI()
        client._enabled = True
        client._api_key = "test_key"
        client._max_cache_size = 5
        mock_request.return_value = "Response"

        # Generate many responses
        for i in range(10):
            client.generate_response(f"Prompt {i}")

        # Cache should be managed
        assert len(client._response_cache) <= client._max_cache_size + 1


# ============================================================================
# Cleanup Tests
# ============================================================================


class TestCleanup:
    """Test cleanup method."""

    def test_cleanup_clears_cache(self):
        """Test cleanup clears response cache."""
        client = GeminiAI()
        client._response_cache = {"key": "value"}

        client.cleanup()

        assert len(client._response_cache) == 0

    def test_cleanup_handles_missing_cache(self):
        """Test cleanup handles missing cache attribute."""
        client = GeminiAI()
        delattr(client, "_response_cache")

        # Should not raise
        client.cleanup()


# ============================================================================
# Global Client Management Tests
# ============================================================================


class TestGlobalClientManagement:
    """Test global client management functions."""

    def teardown_method(self):
        """Reset global client after each test."""
        import src.app.core.ai.gemini_client.gemini_client as module

        module._gemini_client = None

    def test_get_gemini_client_creates_singleton(self):
        """Test get_gemini_client creates singleton instance."""
        client1 = get_gemini_client()
        client2 = get_gemini_client()

        assert client1 is client2

    def test_get_gemini_client_with_custom_config(self, temp_config_file, valid_config):
        """Test get_gemini_client with custom config file."""
        import src.app.core.ai.gemini_client.gemini_client as module

        module._gemini_client = None

        with open(temp_config_file, "w") as f:
            json.dump(valid_config, f)

        client = get_gemini_client(config_file=temp_config_file)

        assert client is not None
        assert client._api_key == "AIzaSyTest1234567890abcdefghijk"

    def test_initialize_gemini(self, temp_config_file, valid_config):
        """Test initialize_gemini function."""
        with open(temp_config_file, "w") as f:
            json.dump(valid_config, f)

        result = initialize_gemini(temp_config_file)

        assert result is True

    def test_is_gemini_available_true(self, temp_config_file, valid_config):
        """Test is_gemini_available returns True when configured."""
        with open(temp_config_file, "w") as f:
            json.dump(valid_config, f)

        initialize_gemini(temp_config_file)
        result = is_gemini_available()

        assert result is True

    def test_is_gemini_available_false_when_not_initialized(self):
        """Test is_gemini_available returns False when not initialized."""
        import src.app.core.ai.gemini_client.gemini_client as module

        module._gemini_client = None

        result = is_gemini_available()

        assert result is False

    def test_is_gemini_ready(self, temp_config_file, valid_config):
        """Test is_gemini_ready function."""
        with open(temp_config_file, "w") as f:
            json.dump(valid_config, f)

        initialize_gemini(temp_config_file)
        ready, message = is_gemini_ready()

        assert ready is True
        assert isinstance(message, str)

    def test_is_gemini_ready_not_initialized(self):
        """Test is_gemini_ready when not initialized."""
        import src.app.core.ai.gemini_client.gemini_client as module

        module._gemini_client = None

        ready, message = is_gemini_ready()

        assert ready is False
        assert "not initialized" in message.lower()


# ============================================================================
# Integration Tests
# ============================================================================


class TestGeminiAIIntegration:
    """Integration tests for complete workflows."""

    def teardown_method(self):
        """Reset global client after each test."""
        import src.app.core.ai.gemini_client.gemini_client as module

        module._gemini_client = None

    @patch("urllib.request.urlopen")
    def test_full_workflow_with_config(
        self, mock_urlopen, temp_config_file, valid_config
    ):
        """Test complete workflow from config to response."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {"candidates": [{"content": {"parts": [{"text": "AI response"}]}}]}
        ).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = False
        mock_urlopen.return_value = mock_response

        # Write config
        with open(temp_config_file, "w") as f:
            json.dump(valid_config, f)

        # Initialize and use
        initialize_gemini(temp_config_file)
        assert is_gemini_available()

        client = get_gemini_client()
        response = client.generate_response("Test prompt")

        assert response == "AI response"

    def test_config_loading_fallback_to_legacy(self, temp_config_file, legacy_config):
        """Test configuration falls back to legacy format."""
        with open(temp_config_file, "w") as f:
            json.dump(legacy_config, f)

        client = GeminiAI(config_file=temp_config_file)

        assert client._api_key == "AIzaSyTest1234567890abcdefghijk"
        assert client.is_available()
