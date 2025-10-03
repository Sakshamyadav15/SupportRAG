"""
LLM service for generating responses using Gemini or OpenAI.
Supports multiple LLM providers with a unified interface.
"""
from typing import Optional
from abc import ABC, abstractmethod
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BaseLLM(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = None, temperature: float = None) -> str:
        """Generate text from a prompt."""
        pass


class GeminiLLM(BaseLLM):
    """Gemini API LLM implementation."""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize Gemini LLM.
        
        Args:
            api_key: Gemini API key
            model: Model name
        """
        try:
            import google.generativeai as genai
            
            self.api_key = api_key or settings.gemini_api_key
            self.model_name = model or settings.llm_model
            
            if not self.api_key:
                raise ValueError("Gemini API key not provided")
            
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Initialized Gemini LLM: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini LLM: {e}")
            raise
    
    def generate(self, prompt: str, max_tokens: int = None, temperature: float = None) -> str:
        """
        Generate text using Gemini.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        try:
            generation_config = {
                'temperature': temperature or settings.llm_temperature,
                'max_output_tokens': max_tokens or settings.max_tokens,
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Error generating text with Gemini: {e}")
            raise


class OpenAILLM(BaseLLM):
    """OpenAI API LLM implementation."""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize OpenAI LLM.
        
        Args:
            api_key: OpenAI API key
            model: Model name
        """
        try:
            from openai import OpenAI
            
            self.api_key = api_key or settings.openai_api_key
            self.model_name = model or "gpt-3.5-turbo"
            
            if not self.api_key:
                raise ValueError("OpenAI API key not provided")
            
            self.client = OpenAI(api_key=self.api_key)
            logger.info(f"Initialized OpenAI LLM: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI LLM: {e}")
            raise
    
    def generate(self, prompt: str, max_tokens: int = None, temperature: float = None) -> str:
        """
        Generate text using OpenAI.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens or settings.max_tokens,
                temperature=temperature or settings.llm_temperature
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {e}")
            raise


class LLMService:
    """Unified LLM service supporting multiple providers."""
    
    def __init__(self, provider: str = None):
        """
        Initialize LLM service.
        
        Args:
            provider: LLM provider ('gemini' or 'openai')
        """
        self.provider = provider or settings.llm_provider
        self.llm = self._create_llm()
    
    def _create_llm(self) -> BaseLLM:
        """Create LLM instance based on provider."""
        if self.provider == "gemini":
            return GeminiLLM()
        elif self.provider == "openai":
            return OpenAILLM()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def generate_answer(
        self,
        question: str,
        context: str,
        max_tokens: int = None,
        temperature: float = None
    ) -> str:
        """
        Generate an answer given a question and context.
        
        Args:
            question: User's question
            context: Retrieved FAQ context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated answer
        """
        prompt = self._build_prompt(question, context)
        return self.llm.generate(prompt, max_tokens, temperature)
    
    def _build_prompt(self, question: str, context: str) -> str:
        """
        Build prompt for the LLM.
        
        Args:
            question: User's question
            context: Retrieved context
            
        Returns:
            Formatted prompt
        """
        prompt = f"""You are a helpful customer support assistant. Answer the user's question based on the provided FAQ context.

FAQ Context:
{context}

User Question: {question}

Instructions:
- Provide a clear, concise, and helpful answer based on the FAQ context
- If the context contains the answer, use it to formulate your response
- Be friendly and professional
- If you need to reference specific information, do so naturally
- Keep the answer focused and relevant

Answer:"""
        
        return prompt


# Global LLM service instance
_llm_service = None


def get_llm_service() -> LLMService:
    """
    Get or create the global LLM service instance.
    
    Returns:
        LLMService instance
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
