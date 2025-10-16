# -*- coding: utf-8 -*-
"""
Core EditorAI class - Simplified with Gemini client.

Main interface for AI-powered code assistance.
"""

# Suppress urllib3 noise early
import logging
import os
from typing import Optional

from src.app.core.ai.gemini_client import (
    get_gemini_client,
    initialize_gemini,
    is_gemini_available,
)
from src.app.core.ai.templates.prompt_templates import PromptTemplates
from src.app.shared.constants import CONFIG_FILE

logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)


class EditorAI:
    """AI-powered code editor assistant using simplified Gemini client."""

    def __init__(self, config_file: str = None):
        """Initialize the EditorAI."""
        self.config_file = config_file or CONFIG_FILE

        # Initialize AI from config if available
        if os.path.exists(self.config_file):
            initialize_gemini(self.config_file)

    def is_available(self) -> bool:
        """Check if AI is available and configured."""
        return is_gemini_available()

    def _get_gemini_client(self):
        """Get the Gemini client instance."""
        return get_gemini_client()

    def _get_ai_response(self, prompt: str) -> Optional[str]:
        """Get AI response using optimized Gemini client."""
        if not self.is_available():
            return "❌ AI service unavailable: Please configure Gemini API key in settings."

        try:
            client = self._get_gemini_client()
            if not client.is_available():
                return "❌ AI service unavailable: Failed to initialize. Please check your configuration."

            # Add prompt optimization for faster processing
            optimized_prompt = self._optimize_prompt(prompt)
            response = client.generate_response(optimized_prompt)

            if response:
                return response.strip()

            return "❌ Failed to get AI response. Please try again."

        except Exception as e:
            logging.error(f"AI response error: {e}")
            return f"❌ AI error: {str(e)}"

    def _optimize_prompt(self, prompt: str) -> str:
        """Optimize prompt for faster processing without changing content."""
        # Remove excessive whitespace and normalize formatting
        lines = [line.strip() for line in prompt.split("\n") if line.strip()]
        optimized = "\n".join(lines)

        # Add performance hint to the prompt
        if not optimized.startswith("Please provide a concise"):
            optimized = "Please provide a concise response.\n\n" + optimized

        return optimized

    def _optimize_code_input(self, code: str) -> str:
        """Optimize code input for faster AI processing."""
        if not code:
            return code

        # Limit code length for faster processing (keep reasonable size)
        max_chars = 8000  # Reasonable limit for fast processing
        if len(code) > max_chars:
            # Take beginning and end of code with ellipsis
            start_chars = max_chars // 2
            end_chars = max_chars // 2 - 100  # Leave room for ellipsis message

            start_part = code[:start_chars]
            end_part = code[-end_chars:]

            optimized_code = (
                f"{start_part}\n\n"
                f"... [Code truncated for performance - {len(code) - max_chars} characters omitted] ...\n\n"
                f"{end_part}"
            )
            return optimized_code

        return code

    def configure(self) -> bool:
        """Configure and initialize the AI system (for backward compatibility)."""
        try:
            # Try to initialize from config file
            if os.path.exists(self.config_file):
                success = initialize_gemini(self.config_file)
                if success:
                    logging.info("AI configuration successful")
                    return True

            logging.warning("AI configuration failed - no valid config found")
            return False

        except Exception as e:
            logging.error(f"AI configuration error: {e}")
            return False

    def get_current_model_name(self) -> Optional[str]:
        """Get the name of the currently active model."""
        if not self.is_available():
            return None

        client = self._get_gemini_client()
        model_info = client.get_model_info()
        return model_info.get("model_name", "Unknown")

    def generate_code_suggestion(self, context: str) -> str:
        """Generate a code suggestion based on context."""
        if not self.is_available():
            return "❌ AI service not available. Please configure your Gemini API key."

        prompt = f"Generate code suggestion for: {context}"
        return self._get_ai_response(prompt) or "❌ Failed to generate code suggestion."

    def process_code(self, action: str, code: str, **kwargs) -> str:
        """Process code with the specified action using template prompts and optimization."""
        if not self.is_available():
            return "❌ AI service not available. Please configure your Gemini API key."

        # Smart code chunking for large files
        code = self._optimize_code_input(code)

        try:
            # Handle different action types using templates
            if action == "explain":
                prompt = PromptTemplates.get_explanation_prompt("analysis", code)
            elif action == "optimize":
                prompt = PromptTemplates.get_explanation_prompt("tips", code)
            elif action == "debug":
                error_message = kwargs.get("error_message", "")
                if error_message:
                    prompt = (
                        f"Debug this code with error: {error_message}\n\nCode:\n{code}"
                    )
                else:
                    prompt = PromptTemplates.get_explanation_prompt("issues", code)
            elif action == "document":
                prompt = PromptTemplates.get_code_prompt("document", code)
            elif action == "generate":
                # Handle different generation types
                gen_type = kwargs.get("type", "solution")
                if "generator" in gen_type.lower():
                    docs = kwargs.get("docs", "")
                    prompt = PromptTemplates.get_code_prompt(
                        "generate", code, type=gen_type, docs=docs
                    )
                elif "validator" in gen_type.lower():
                    prompt = PromptTemplates.get_code_prompt("validator", code)
                else:
                    requirements = kwargs.get("requirements", "Generate code")
                    prompt = f"Generate code based on requirements: {requirements}\n\nReference code:\n{code}"
            elif action == "custom":
                command = kwargs.get("command", "Analyze this code")
                prompt = PromptTemplates.get_custom_prompt(command, code)
            else:
                return f"❌ Unknown action: {action}"

            return self._get_ai_response(prompt) or f"❌ Failed to {action} code."

        except Exception as e:
            logging.error(f"Template processing error for {action}: {e}")
            # Fallback to simple prompts
            return self._process_code_fallback(action, code, **kwargs)

    def _process_code_fallback(self, action: str, code: str, **kwargs) -> str:
        """Fallback processing without templates."""
        if action == "explain":
            return self.explain_code(code)
        if action == "optimize":
            return self.suggest_optimizations(code)
        if action == "debug":
            error_message = kwargs.get("error_message", "")
            return self.debug_code(code, error_message)
        if action == "document":
            return self.generate_documentation(code)
        if action == "generate":
            requirements = kwargs.get("requirements", "Generate code")
            prompt = f"Generate code based on requirements: {requirements}\n\nReference code:\n{code}"
            return self._get_ai_response(prompt) or "❌ Failed to generate code."
        if action == "custom":
            command = kwargs.get("command", "Analyze this code")
            prompt = f"{command}\n\nCode:\n{code}"
            return (
                self._get_ai_response(prompt) or "❌ Failed to process custom command."
            )

        return f"❌ Unknown action: {action}"

    def process_explanation(self, action: str, code: str) -> str:
        """Process code explanation request."""
        return self.explain_code(code)

    def explain_code(self, code: str, language: str = "cpp") -> str:
        """Provide a detailed explanation of the given code."""
        if not self.is_available():
            return "❌ AI service not available. Please configure your Gemini API key."

        try:
            prompt = PromptTemplates.get_explanation_prompt("analysis", code)
        except Exception:
            prompt = f"Explain this {language} code in detail:\n\n{code}"

        return self._get_ai_response(prompt) or "❌ Failed to explain code."

    def suggest_optimizations(self, code: str, language: str = "cpp") -> str:
        """Suggest optimizations for the given code."""
        if not self.is_available():
            return "❌ AI service not available. Please configure your Gemini API key."

        try:
            prompt = PromptTemplates.get_explanation_prompt("tips", code)
        except Exception:
            prompt = f"Suggest optimizations for this {language} code:\n\n{code}"

        return self._get_ai_response(prompt) or "❌ Failed to suggest optimizations."

    def debug_code(
        self, code: str, error_message: str = "", language: str = "cpp"
    ) -> str:
        """Help debug issues in the given code."""
        if not self.is_available():
            return "❌ AI service not available. Please configure your Gemini API key."

        if error_message:
            prompt = f"Debug this {language} code with error: {error_message}\n\nCode:\n{code}"
        else:
            try:
                prompt = PromptTemplates.get_explanation_prompt("issues", code)
            except Exception:
                prompt = f"Analyze and find potential issues in this {language} code:\n\n{code}"

        return self._get_ai_response(prompt) or "❌ Failed to debug code."

    def generate_documentation(self, code: str, language: str = "cpp") -> str:
        """Generate documentation for the given code."""
        if not self.is_available():
            return "❌ AI service not available. Please configure your Gemini API key."

        try:
            prompt = PromptTemplates.get_code_prompt("document", code)
        except Exception:
            prompt = f"Generate comprehensive documentation for this {language} code:\n\n{code}"

        return self._get_ai_response(prompt) or "❌ Failed to generate documentation."
