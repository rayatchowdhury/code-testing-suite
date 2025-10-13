"""
Phase 8 Task 6 - Phase 3: Tests for editor_ai.py

Tests cover:
- EditorAI initialization
- AI availability checking
- Code optimization and prompt optimization
- All code processing actions (explain, optimize, debug, document, generate, custom)
- Fallback processing
- Configuration management
- Error handling
"""

import pytest
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock

from src.app.core.ai.core.editor_ai import EditorAI


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
    """Valid AI configuration."""
    return {
        "gemini": {
            "enabled": True,
            "api_key": "AIzaSyTest1234567890abcdefghijk",
            "model": "gemini-2.5-flash",
        }
    }


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client."""
    mock = Mock()
    mock.is_available.return_value = True
    mock.generate_response.return_value = "AI response"
    mock.get_model_info.return_value = {"model_name": "gemini-2.5-flash"}
    return mock


# ============================================================================
# Initialization Tests
# ============================================================================


class TestEditorAIInitialization:
    """Test EditorAI initialization."""

    def test_init_with_config_file(self, temp_config_file, valid_config):
        """Test initialization with config file."""
        with open(temp_config_file, "w") as f:
            json.dump(valid_config, f)

        editor_ai = EditorAI(config_file=temp_config_file)

        assert editor_ai.config_file == temp_config_file

    def test_init_without_config_file(self):
        """Test initialization without config file."""
        editor_ai = EditorAI()

        assert editor_ai.config_file is not None

    @patch("src.app.core.ai.core.editor_ai.os.path.exists")
    @patch("src.app.core.ai.core.editor_ai.initialize_gemini")
    def test_init_initializes_gemini_when_config_exists(
        self, mock_init, mock_exists, temp_config_file
    ):
        """Test Gemini initialization when config exists."""
        mock_exists.return_value = True
        mock_init.return_value = True

        editor_ai = EditorAI(config_file=temp_config_file)

        mock_init.assert_called_once_with(temp_config_file)


# ============================================================================
# Availability Tests
# ============================================================================


class TestAvailability:
    """Test AI availability checking."""

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    def test_is_available_true(self, mock_available):
        """Test is_available returns True when Gemini available."""
        mock_available.return_value = True
        editor_ai = EditorAI()

        assert editor_ai.is_available() is True

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    def test_is_available_false(self, mock_available):
        """Test is_available returns False when Gemini unavailable."""
        mock_available.return_value = False
        editor_ai = EditorAI()

        assert editor_ai.is_available() is False

    @patch("src.app.core.ai.core.editor_ai.get_gemini_client")
    def test_get_gemini_client(self, mock_get_client):
        """Test _get_gemini_client returns client."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        editor_ai = EditorAI()
        client = editor_ai._get_gemini_client()

        assert client == mock_client


# ============================================================================
# Prompt Optimization Tests
# ============================================================================


class TestPromptOptimization:
    """Test prompt optimization methods."""

    def test_optimize_prompt_removes_whitespace(self):
        """Test optimize_prompt removes excess whitespace."""
        editor_ai = EditorAI()
        prompt = "Line 1\n\n\nLine 2\n  \nLine 3"

        optimized = editor_ai._optimize_prompt(prompt)

        assert "Line 1\nLine 2\nLine 3" in optimized

    def test_optimize_prompt_adds_concise_hint(self):
        """Test optimize_prompt adds concise response hint."""
        editor_ai = EditorAI()
        prompt = "Explain this code"

        optimized = editor_ai._optimize_prompt(prompt)

        assert "concise" in optimized.lower()

    def test_optimize_code_input_short_code(self):
        """Test optimize_code_input preserves short code."""
        editor_ai = EditorAI()
        code = "int main() { return 0; }"

        optimized = editor_ai._optimize_code_input(code)

        assert optimized == code

    def test_optimize_code_input_long_code(self):
        """Test optimize_code_input truncates long code."""
        editor_ai = EditorAI()
        code = "x = 1\n" * 10000  # Very long code

        optimized = editor_ai._optimize_code_input(code)

        assert len(optimized) < len(code)
        assert "truncated" in optimized.lower()

    def test_optimize_code_input_empty_code(self):
        """Test optimize_code_input handles empty code."""
        editor_ai = EditorAI()

        optimized = editor_ai._optimize_code_input("")

        assert optimized == ""


# ============================================================================
# AI Response Tests
# ============================================================================


class TestAIResponse:
    """Test _get_ai_response method."""

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    def test_get_ai_response_unavailable(self, mock_available):
        """Test AI response when service unavailable."""
        mock_available.return_value = False
        editor_ai = EditorAI()

        response = editor_ai._get_ai_response("Test prompt")

        assert "unavailable" in response.lower()
        assert "❌" in response

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    @patch("src.app.core.ai.core.editor_ai.get_gemini_client")
    def test_get_ai_response_success(
        self, mock_get_client, mock_available, mock_gemini_client
    ):
        """Test successful AI response."""
        mock_available.return_value = True
        mock_get_client.return_value = mock_gemini_client
        mock_gemini_client.generate_response.return_value = "  AI response  "

        editor_ai = EditorAI()
        response = editor_ai._get_ai_response("Test prompt")

        assert response == "AI response"

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    @patch("src.app.core.ai.core.editor_ai.get_gemini_client")
    def test_get_ai_response_client_not_available(
        self, mock_get_client, mock_available
    ):
        """Test AI response when client not available."""
        mock_available.return_value = True
        mock_client = Mock()
        mock_client.is_available.return_value = False
        mock_get_client.return_value = mock_client

        editor_ai = EditorAI()
        response = editor_ai._get_ai_response("Test prompt")

        assert "unavailable" in response.lower()
        assert "❌" in response

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    @patch("src.app.core.ai.core.editor_ai.get_gemini_client")
    def test_get_ai_response_empty_response(
        self, mock_get_client, mock_available, mock_gemini_client
    ):
        """Test AI response when client returns empty."""
        mock_available.return_value = True
        mock_get_client.return_value = mock_gemini_client
        mock_gemini_client.generate_response.return_value = None

        editor_ai = EditorAI()
        response = editor_ai._get_ai_response("Test prompt")

        assert "Failed" in response
        assert "❌" in response

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    @patch("src.app.core.ai.core.editor_ai.get_gemini_client")
    def test_get_ai_response_exception(self, mock_get_client, mock_available):
        """Test AI response handles exceptions."""
        mock_available.return_value = True
        mock_get_client.side_effect = Exception("Test error")

        editor_ai = EditorAI()
        response = editor_ai._get_ai_response("Test prompt")

        assert "error" in response.lower()
        assert "❌" in response


# ============================================================================
# Configuration Tests
# ============================================================================


class TestConfiguration:
    """Test configuration methods."""

    @patch("src.app.core.ai.core.editor_ai.os.path.exists")
    @patch("src.app.core.ai.core.editor_ai.initialize_gemini")
    def test_configure_success(self, mock_init, mock_exists, temp_config_file):
        """Test successful configuration."""
        mock_exists.return_value = True
        mock_init.return_value = True

        editor_ai = EditorAI(config_file=temp_config_file)
        result = editor_ai.configure()

        assert result is True

    @patch("src.app.core.ai.core.editor_ai.os.path.exists")
    def test_configure_no_config_file(self, mock_exists):
        """Test configuration without config file."""
        mock_exists.return_value = False

        editor_ai = EditorAI()
        result = editor_ai.configure()

        assert result is False

    @patch("src.app.core.ai.core.editor_ai.os.path.exists")
    @patch("src.app.core.ai.core.editor_ai.initialize_gemini")
    def test_configure_exception(self, mock_init, mock_exists):
        """Test configuration handles exceptions."""
        # Don't raise on __init__, only on configure call
        editor_ai = EditorAI()

        mock_exists.return_value = True
        mock_init.side_effect = Exception("Test error")

        result = editor_ai.configure()

        assert result is False

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    @patch("src.app.core.ai.core.editor_ai.get_gemini_client")
    def test_get_current_model_name_available(
        self, mock_get_client, mock_available, mock_gemini_client
    ):
        """Test get_current_model_name when available."""
        mock_available.return_value = True
        mock_get_client.return_value = mock_gemini_client

        editor_ai = EditorAI()
        model = editor_ai.get_current_model_name()

        assert model == "gemini-2.5-flash"

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    def test_get_current_model_name_unavailable(self, mock_available):
        """Test get_current_model_name when unavailable."""
        mock_available.return_value = False

        editor_ai = EditorAI()
        model = editor_ai.get_current_model_name()

        assert model is None


# ============================================================================
# Code Action Tests
# ============================================================================


class TestCodeActions:
    """Test code action methods (explain, optimize, debug, document)."""

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    def test_explain_code_unavailable(self, mock_available):
        """Test explain_code when AI unavailable."""
        mock_available.return_value = False
        editor_ai = EditorAI()

        result = editor_ai.explain_code("int main() {}")

        assert "not available" in result.lower()

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    @patch.object(EditorAI, "_get_ai_response")
    def test_explain_code_success(self, mock_response, mock_available):
        """Test successful code explanation."""
        mock_available.return_value = True
        mock_response.return_value = "This is an explanation"

        editor_ai = EditorAI()
        result = editor_ai.explain_code("int main() {}")

        assert result == "This is an explanation"

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    @patch.object(EditorAI, "_get_ai_response")
    def test_suggest_optimizations_success(self, mock_response, mock_available):
        """Test successful optimization suggestions."""
        mock_available.return_value = True
        mock_response.return_value = "Optimization suggestions"

        editor_ai = EditorAI()
        result = editor_ai.suggest_optimizations("int main() {}")

        assert result == "Optimization suggestions"

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    @patch.object(EditorAI, "_get_ai_response")
    def test_debug_code_with_error_message(self, mock_response, mock_available):
        """Test debug_code with error message."""
        mock_available.return_value = True
        mock_response.return_value = "Debug suggestions"

        editor_ai = EditorAI()
        result = editor_ai.debug_code(
            "int main() {}", error_message="Segmentation fault"
        )

        assert result == "Debug suggestions"
        mock_response.assert_called_once()

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    @patch.object(EditorAI, "_get_ai_response")
    def test_debug_code_without_error_message(self, mock_response, mock_available):
        """Test debug_code without error message."""
        mock_available.return_value = True
        mock_response.return_value = "Potential issues found"

        editor_ai = EditorAI()
        result = editor_ai.debug_code("int main() {}")

        assert result == "Potential issues found"

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    @patch.object(EditorAI, "_get_ai_response")
    def test_generate_documentation_success(self, mock_response, mock_available):
        """Test successful documentation generation."""
        mock_available.return_value = True
        mock_response.return_value = "Generated documentation"

        editor_ai = EditorAI()
        result = editor_ai.generate_documentation("int main() {}")

        assert result == "Generated documentation"

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    @patch.object(EditorAI, "_get_ai_response")
    def test_generate_code_suggestion_success(self, mock_response, mock_available):
        """Test successful code suggestion generation."""
        mock_available.return_value = True
        mock_response.return_value = "Code suggestion"

        editor_ai = EditorAI()
        result = editor_ai.generate_code_suggestion("sorting algorithm")

        assert result == "Code suggestion"


# ============================================================================
# Process Code Tests
# ============================================================================


class TestProcessCode:
    """Test process_code method with different actions."""

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    def test_process_code_unavailable(self, mock_available):
        """Test process_code when AI unavailable."""
        mock_available.return_value = False
        editor_ai = EditorAI()

        result = editor_ai.process_code("explain", "int main() {}")

        assert "not available" in result.lower()

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    @patch.object(EditorAI, "_get_ai_response")
    def test_process_code_explain(self, mock_response, mock_available):
        """Test process_code with explain action."""
        mock_available.return_value = True
        mock_response.return_value = "Explanation"

        editor_ai = EditorAI()
        result = editor_ai.process_code("explain", "int main() {}")

        assert result == "Explanation"

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    @patch.object(EditorAI, "_get_ai_response")
    def test_process_code_optimize(self, mock_response, mock_available):
        """Test process_code with optimize action."""
        mock_available.return_value = True
        mock_response.return_value = "Optimizations"

        editor_ai = EditorAI()
        result = editor_ai.process_code("optimize", "int main() {}")

        assert result == "Optimizations"

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    @patch.object(EditorAI, "_get_ai_response")
    def test_process_code_debug_with_error(self, mock_response, mock_available):
        """Test process_code with debug action and error message."""
        mock_available.return_value = True
        mock_response.return_value = "Debug info"

        editor_ai = EditorAI()
        result = editor_ai.process_code("debug", "int main() {}", error_message="Error")

        assert result == "Debug info"

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    @patch.object(EditorAI, "_get_ai_response")
    def test_process_code_document(self, mock_response, mock_available):
        """Test process_code with document action."""
        mock_available.return_value = True
        mock_response.return_value = "Documentation"

        editor_ai = EditorAI()
        result = editor_ai.process_code("document", "int main() {}")

        assert result == "Documentation"

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    @patch.object(EditorAI, "_get_ai_response")
    def test_process_code_generate(self, mock_response, mock_available):
        """Test process_code with generate action."""
        mock_available.return_value = True
        mock_response.return_value = "Generated code"

        editor_ai = EditorAI()
        result = editor_ai.process_code(
            "generate", "template", requirements="Sort array"
        )

        assert result == "Generated code"

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    @patch.object(EditorAI, "_get_ai_response")
    def test_process_code_custom(self, mock_response, mock_available):
        """Test process_code with custom action."""
        mock_available.return_value = True
        mock_response.return_value = "Custom response"

        editor_ai = EditorAI()
        result = editor_ai.process_code("custom", "code", command="Custom command")

        assert result == "Custom response"

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    def test_process_code_unknown_action(self, mock_available):
        """Test process_code with unknown action."""
        mock_available.return_value = True

        editor_ai = EditorAI()
        result = editor_ai.process_code("unknown", "code")

        assert "Unknown action" in result

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    @patch.object(EditorAI, "_process_code_fallback")
    def test_process_code_fallback_on_exception(self, mock_fallback, mock_available):
        """Test process_code uses fallback on template exception."""
        mock_available.return_value = True
        mock_fallback.return_value = "Fallback response"

        with patch("src.app.core.ai.core.editor_ai.PromptTemplates") as mock_templates:
            mock_templates.get_explanation_prompt.side_effect = Exception(
                "Template error"
            )

            editor_ai = EditorAI()
            result = editor_ai.process_code("explain", "code")

            assert result == "Fallback response"


# ============================================================================
# Fallback Processing Tests
# ============================================================================


class TestFallbackProcessing:
    """Test _process_code_fallback method."""

    @patch.object(EditorAI, "explain_code")
    def test_fallback_explain(self, mock_explain):
        """Test fallback for explain action."""
        mock_explain.return_value = "Explanation"

        editor_ai = EditorAI()
        result = editor_ai._process_code_fallback("explain", "code")

        assert result == "Explanation"

    @patch.object(EditorAI, "suggest_optimizations")
    def test_fallback_optimize(self, mock_optimize):
        """Test fallback for optimize action."""
        mock_optimize.return_value = "Optimizations"

        editor_ai = EditorAI()
        result = editor_ai._process_code_fallback("optimize", "code")

        assert result == "Optimizations"

    @patch.object(EditorAI, "debug_code")
    def test_fallback_debug(self, mock_debug):
        """Test fallback for debug action."""
        mock_debug.return_value = "Debug info"

        editor_ai = EditorAI()
        result = editor_ai._process_code_fallback(
            "debug", "code", error_message="Error"
        )

        mock_debug.assert_called_with("code", "Error")

    @patch.object(EditorAI, "generate_documentation")
    def test_fallback_document(self, mock_doc):
        """Test fallback for document action."""
        mock_doc.return_value = "Documentation"

        editor_ai = EditorAI()
        result = editor_ai._process_code_fallback("document", "code")

        assert result == "Documentation"

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    @patch.object(EditorAI, "_get_ai_response")
    def test_fallback_generate(self, mock_response, mock_available):
        """Test fallback for generate action."""
        mock_available.return_value = True
        mock_response.return_value = "Generated"

        editor_ai = EditorAI()
        result = editor_ai._process_code_fallback(
            "generate", "code", requirements="Sort"
        )

        assert result == "Generated"

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    @patch.object(EditorAI, "_get_ai_response")
    def test_fallback_custom(self, mock_response, mock_available):
        """Test fallback for custom action."""
        mock_available.return_value = True
        mock_response.return_value = "Custom"

        editor_ai = EditorAI()
        result = editor_ai._process_code_fallback("custom", "code", command="Command")

        assert result == "Custom"

    def test_fallback_unknown_action(self):
        """Test fallback for unknown action."""
        editor_ai = EditorAI()
        result = editor_ai._process_code_fallback("unknown", "code")

        assert "Unknown action" in result


# ============================================================================
# Integration Tests
# ============================================================================


class TestEditorAIIntegration:
    """Integration tests for complete workflows."""

    @patch("src.app.core.ai.core.editor_ai.is_gemini_available")
    @patch("src.app.core.ai.core.editor_ai.get_gemini_client")
    def test_complete_workflow_explain(
        self, mock_get_client, mock_available, mock_gemini_client
    ):
        """Test complete workflow for explain action."""
        mock_available.return_value = True
        mock_get_client.return_value = mock_gemini_client
        mock_gemini_client.generate_response.return_value = "Complete explanation"

        editor_ai = EditorAI()
        result = editor_ai.process_code("explain", "int main() { return 0; }")

        assert "explanation" in result.lower()

    def test_process_explanation_wrapper(self):
        """Test process_explanation wrapper method."""
        with patch.object(EditorAI, "explain_code") as mock_explain:
            mock_explain.return_value = "Explanation"

            editor_ai = EditorAI()
            result = editor_ai.process_explanation("explain", "code")

            assert result == "Explanation"
