import google.generativeai as genai
import json
import os
import asyncio
import logging

CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.code_testing_suite')

class EditorAI:
    def __init__(self):
        self._setup_ai()
        
    def _setup_ai(self):
        try:
            # Use CONFIG_DIR for configuration
            config_path = os.path.join(CONFIG_DIR, 'config.json')
            logging.info(f"Looking for config at: {config_path}")
            
            if not os.path.exists(config_path):
                os.makedirs(CONFIG_DIR, exist_ok=True)
                self.model = None
                return

            with open(config_path, 'r') as f:
                config = json.load(f)
                
            api_key = config.get('gemini_api_key')
            if not api_key or not isinstance(api_key, str) or len(api_key) < 10:
                self.model = None
                return
                
            logging.info("Configuring Gemini API...")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            logging.info("Gemini API configured successfully")
            
        except Exception as e:
            logging.error(f"Error setting up AI: {e}")
            self.model = None

    async def explain_code(self, code: str) -> str:
        prompt = f"Explain this code concisely:\n\n{code}"
        return await self._get_ai_response(prompt)

    async def fix_code(self, code: str) -> str:
        prompt = f"Fix any bugs in this code and explain the fixes:\n\n{code}"
        return await self._get_ai_response(prompt)

    async def optimize_code(self, code: str) -> str:
        prompt = f"Optimize this code and explain the optimizations:\n\n{code}"
        return await self._get_ai_response(prompt)

    async def _get_ai_response(self, prompt: str) -> str:
        if not self.model:
            return None
            
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(prompt)
            )
            return response.text
        except Exception as e:
            logging.error(f"AI response error: {e}")
            return None

    async def document_code(self, code: str) -> str:
        prompt = f"""Add documentation comments to this code. 
        Format your response as follows:
        1. Start with '---BEGIN CODE---'
        2. Show the documented code
        3. End with '---END CODE---'
        Here's the code to document:

        {code}"""
        
        response = await self._get_ai_response(prompt)
        if not response:
            return None
            
        # Extract code between markers
        try:
            start = response.find('---BEGIN CODE---')
            end = response.find('---END CODE---')
            if start != -1 and end != -1:
                return response[start + 15:end].strip()
            return response
        except Exception:
            return response

    async def custom_command(self, command: str, code: str) -> str:
        """Handle custom AI command"""
        prompt = f"""Instructions:
        1. Apply this modification to the code: {command}
        2. Show the complete modified code as is, without explanations
        3. Do not add additional comments or explanations
        4. Maintain all existing code structure and formatting
        5. Include all imports and class definitions
        6. Return ONLY the modified code between ---BEGIN CODE--- and ---END CODE--- markers

        Here's the code to modify:

        {code}

        Remember:
        - Return the COMPLETE code, not just the changed parts
        - Keep all existing functionality intact
        - Maintain consistent formatting
        - Include all necessary imports
        """
        
        response = await self._get_ai_response(prompt)
        if not response:
            return None
            
        # Extract code between markers
        try:
            start = response.find('---BEGIN CODE---')
            end = response.find('---END CODE---')
            if start != -1 and end != -1:
                return response[start + 15:end].strip()
            return response  # Return full response if no markers found
        except Exception:
            return response

    # ...existing code for other methods...
