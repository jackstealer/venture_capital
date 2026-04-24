# LLM API Client
# Wrapper for OpenRouter, Grok, Gemini and OpenAI APIs

import os
from openai import OpenAI
from config import Config

class LLMClient:
    """
    Unified client for LLM APIs (OpenRouter/Grok/Gemini/OpenAI)
    Handles API calls, prompt formatting, and response parsing
    """
    
    def __init__(self, provider='openrouter'):
        """
        Initialize LLM client
        Args:
            provider (str): 'openrouter', 'grok', 'gemini' or 'openai'
        """
        self.provider = provider
        
        if provider == 'openrouter':
            # OpenRouter provides access to multiple models
            self.client = OpenAI(
                api_key=Config.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )
            # Using Google's Gemini via OpenRouter (free tier)
            self.model_id = 'google/gemini-flash-1.5'
        elif provider == 'grok':
            # Grok uses OpenAI-compatible API
            self.client = OpenAI(
                api_key=Config.GROK_API_KEY,
                base_url="https://api.x.ai/v1"
            )
            # X.AI's actual model name
            self.model_id = 'grok-2-latest'  # Correct X.AI model name
        elif provider == 'gemini':
            from google import genai
            from google.genai import types
            self.genai_types = types
            # Using new google.genai package
            self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
            self.model_id = 'gemini-1.5-flash-latest'
        elif provider == 'openai':
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            self.model_id = 'gpt-3.5-turbo'
    
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
            if self.provider in ['openrouter', 'grok', 'openai']:
                return self._generate_openai_compatible(prompt, temperature, max_tokens)
            elif self.provider == 'gemini':
                return self._generate_gemini(prompt, temperature)
        except Exception as e:
            print(f"LLM generation error: {e}")
            return f"Error generating response: {str(e)}"
    
    def _generate_openai_compatible(self, prompt, temperature, max_tokens):
        """Generate using OpenAI-compatible API (OpenRouter, Grok, OpenAI)"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": "You are an expert venture capital analyst specializing in technology evaluation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"{self.provider.upper()} API error: {e}")
            return f"Error: {str(e)}"
    
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
                    config=self.genai_types.GenerateContentConfig(
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
        """Generate using OpenAI GPT - kept for backwards compatibility"""
        return self._generate_openai_compatible(prompt, temperature, max_tokens)
    
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
        import re
        
        # Add JSON formatting instruction to prompt
        structured_prompt = f"""{prompt}

IMPORTANT: Respond with ONLY valid JSON. No additional text before or after the JSON.
{f"Follow this structure: {json.dumps(schema, indent=2)}" if schema else ""}

JSON Response:"""
        
        response_text = self.generate(structured_prompt, temperature=0.3, max_tokens=2000)
        
        # Check if response is an error
        if response_text.startswith("Error:"):
            print(f"LLM Error in generate_structured: {response_text}")
            # Return default schema with N/A values
            if schema:
                return {key: "N/A" if isinstance(value, str) else 0 for key, value in schema.items()}
            return {"error": response_text}
        
        try:
            # Try to find JSON in the response
            # Look for JSON object
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                return parsed
            
            # If no JSON found, try direct parse
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            print(f"Response text: {response_text[:500]}...")
            
            # Return default schema with N/A values
            if schema:
                return {key: "N/A" if isinstance(value, str) else 0 for key, value in schema.items()}
            return {"error": "Failed to parse JSON", "raw_response": response_text[:500]}
        except Exception as e:
            print(f"Unexpected error in generate_structured: {e}")
            if schema:
                return {key: "N/A" if isinstance(value, str) else 0 for key, value in schema.items()}
            return {"error": str(e)}
    
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
