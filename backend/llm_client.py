# LLM API Client
# Wrapper for Google Gemini and OpenAI APIs

import os
from google import genai
from google.genai import types
from config import Config

class LLMClient:
    """
    Unified client for LLM APIs (Gemini/OpenAI)
    Handles API calls, prompt formatting, and response parsing
    """
    
    def __init__(self, provider='gemini'):
        """
        Initialize LLM client
        Args:
            provider (str): 'gemini' or 'openai'
        """
        self.provider = provider
        
        if provider == 'gemini':
            # Using new google.genai package
            self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
            # Use models without version prefix for new API
            self.model_id = 'gemini-1.5-flash-latest'  # Latest stable model
        elif provider == 'openai':
            import openai
            openai.api_key = Config.OPENAI_API_KEY
            self.client = openai
    
    def generate(self, prompt, temperature=0.7, max_tokens=1000):
        """
        Generate text using LLM
        Args:
            prompt (str): Input prompt
            temperature (float): Creativity level (0.0-1.0)
            max_tokens (int): Maximum response length
        Returns:
            str: Generated text
        """
        try:
            if self.provider == 'gemini':
                return self._generate_gemini(prompt, temperature)
            elif self.provider == 'openai':
                return self._generate_openai(prompt, temperature, max_tokens)
        except Exception as e:
            print(f"LLM generation error: {e}")
            return f"Error generating response: {str(e)}"
    
    def _generate_gemini(self, prompt, temperature):
        """Generate using Google Gemini with new API"""
        # Try multiple models in order of preference
        models_to_try = [
            'gemini-1.5-flash-latest',
            'gemini-1.5-pro-latest',
            'gemini-pro'
        ]
        
        for model in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        top_p=0.95,
                        top_k=40,
                        max_output_tokens=2048,
                    )
                )
                return response.text
            except Exception as e:
                print(f"Gemini API error with {model}: {e}")
                if model == models_to_try[-1]:  # Last model
                    return f"Error: All Gemini models failed. {str(e)}"
                continue  # Try next model
    
    def _generate_openai(self, prompt, temperature, max_tokens):
        """Generate using OpenAI GPT"""
        response = self.client.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert venture capital analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    def generate_structured(self, prompt, schema=None):
        """
        Generate structured output (JSON)
        Args:
            prompt (str): Input prompt
            schema (dict): Expected output schema
        Returns:
            dict: Parsed JSON response
        """
        import json
        
        # Add JSON formatting instruction to prompt
        structured_prompt = f"""{prompt}

Please respond with valid JSON only, following this structure:
{json.dumps(schema, indent=2) if schema else "{}"}

Response:"""
        
        response_text = self.generate(structured_prompt, temperature=0.3)
        
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            return json.loads(json_str)
        except:
            return {"error": "Failed to parse JSON", "raw_response": response_text}
    
    def analyze_code(self, code_snippet, language='python'):
        """
        Analyze code quality using LLM
        Args:
            code_snippet (str): Code to analyze
            language (str): Programming language
        Returns:
            dict: Analysis results
        """
        prompt = f"""Analyze this {language} code and provide:
1. Code quality score (0-100)
2. Key strengths
3. Potential issues
4. Recommendations

Code:
```{language}
{code_snippet}
```

Respond in JSON format."""
        
        schema = {
            "quality_score": 0,
            "strengths": [],
            "issues": [],
            "recommendations": []
        }
        
        return self.generate_structured(prompt, schema)
    
    def summarize_text(self, text, max_length=200):
        """
        Summarize long text using LLM
        Args:
            text (str): Text to summarize
            max_length (int): Maximum summary length
        Returns:
            str: Summary
        """
        prompt = f"""Summarize the following text in {max_length} words or less:

{text}

Summary:"""
        
        return self.generate(prompt, temperature=0.5)
