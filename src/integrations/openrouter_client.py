"""
OpenRouter client for unified access to all LLM providers
Handles OpenAI, Anthropic, and open source models through one API
"""
import os
import asyncio
import aiohttp
from aiohttp import ClientTimeout
import json
from typing import Dict, Any, List, Optional, AsyncGenerator
from dataclasses import dataclass
from decimal import Decimal
import time
import logging

logger = logging.getLogger(__name__)

@dataclass
class OpenRouterModel:
    """Model information from OpenRouter"""
    id: str
    name: str
    description: str
    context_length: int
    pricing: Dict[str, float]  # per million tokens
    supported_features: List[str]
    
class OpenRouterClient:
    """Client for OpenRouter API"""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    # Popular models with their OpenRouter IDs
    MODELS = {
        # OpenAI Models
        "gpt-5-pro": "openai/gpt-5-pro",  # GPT-5 Pro (for implementation)
        "gpt-5": "openai/gpt-5",  # GPT-5 (confirmed working in our tests)
        "gpt-5-image": "openai/gpt-5-image",  # GPT-5 with vision (for sketch analysis)
        "gpt-4o": "openai/gpt-4o",  # GPT-4o
        "gpt-4-turbo": "openai/gpt-4o",
        "gpt-4": "openai/gpt-4",
        "gpt-3.5-turbo": "openai/gpt-3.5-turbo",
        "gpt-4-vision": "openai/gpt-4-vision-preview",

        # Anthropic Models
        "claude-sonnet-4.5": "anthropic/claude-sonnet-4.5",  # Latest Claude Sonnet 4.5 (for architecture)
        "claude-opus-4.1": "anthropic/claude-opus-4.1",  # Latest Claude 4.1 Opus (for security)
        "claude-4-opus": "anthropic/claude-opus-4",  # Claude 4 Opus
        "claude-4-sonnet": "anthropic/claude-sonnet-4",  # Claude 4 Sonnet
        "claude-3-opus": "anthropic/claude-3-opus",
        "claude-3.5-sonnet": "anthropic/claude-3.5-sonnet",  # Updated to 3.5
        "claude-3-haiku": "anthropic/claude-3-haiku",
        "claude-2.1": "anthropic/claude-2.1",

        # X.AI Models
        "grok-4": "x-ai/grok-4",  # Grok-4 (98% HumanEval) - for testing

        # Open Source Models
        "llama-3-70b": "meta-llama/llama-3-70b-instruct",
        "llama-3-8b": "meta-llama/llama-3-8b-instruct",
        "mixtral-8x7b": "mistralai/mixtral-8x7b-instruct",
        "mistral-7b": "mistralai/mistral-7b-instruct",
        "gemma-7b": "google/gemma-7b-it",
        "nous-hermes-2": "nousresearch/nous-hermes-2-mixtral-8x7b-dpo",

        # Specialized Models
        "perplexity-online": "perplexity/llama-3-sonar-large-32k-online",
        "code-llama-70b": "meta-llama/llama-3-70b-instruct",  # Good for code
        "dolphin-mixtral": "cognitivecomputations/dolphin-mixtral-8x7b",

        # Stealth/Experimental Models
        "horizon-alpha": "openrouter/horizon-alpha",  # Free stealth model (testing phase)
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key not found")
            
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://codeswarm.dev",
            "X-Title": "CodeSwarm"
        }
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        # Add timeout to prevent hanging requests
        # Use 900s (15 minutes) for complex model operations
        timeout = ClientTimeout(total=900, connect=10, sock_read=900)
        # Increase connection limits for parallel execution
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
        self.session = aiohttp.ClientSession(timeout=timeout, connector=connector)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def create_session_if_needed(self):
        """Create session if not exists"""
        if not self.session:
            # Add timeout to prevent hanging requests
            # Use 900s (15 minutes) for complex operations
            timeout = ClientTimeout(total=900, connect=10, sock_read=900)
            # Increase connection limits for parallel execution
            # Read from environment or use defaults
            limit = int(os.getenv("CONNECTION_POOL_LIMIT", "100"))
            limit_per_host = int(os.getenv("CONNECTION_POOL_LIMIT_PER_HOST", "30"))
            connector = aiohttp.TCPConnector(limit=limit, limit_per_host=limit_per_host)
            self.session = aiohttp.ClientSession(timeout=timeout, connector=connector)

    async def close(self):
        """Close the client session"""
        if self.session:
            await self.session.close()
            self.session = None

    def __del__(self):
        """Cleanup on deletion - try to close session if still open"""
        if self.session and not self.session.closed:
            try:
                # Try to get event loop and close
                import warnings
                warnings.warn(
                    "OpenRouterClient session was not properly closed. "
                    "Please use 'async with' or call 'await client.close()' explicitly.",
                    ResourceWarning
                )
            except Exception:
                pass  # Can't do much in __del__

    async def complete(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a chat completion"""
        await self.create_session_if_needed()
        
        # Map model alias to OpenRouter ID
        model_id = self.MODELS.get(model, model)
        
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
            
        start_time = time.time()
        
        # Add retry logic with exponential backoff
        max_retries = kwargs.pop('max_retries', 3)
        retry_delay = 1.0
        last_error = None
        
        for attempt in range(max_retries):
            try:
                if stream:
                    return await self._stream_completion(payload)
                else:
                    return await self._standard_completion(payload, start_time)
                    
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.warning(f"OpenRouter API attempt {attempt + 1} failed: {e}. Retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"OpenRouter API failed after {max_retries} attempts: {e}")
                    
            except Exception as e:
                logger.error(f"OpenRouter API error: {e}")
                raise
                
        # If we get here, all retries failed
        raise last_error if last_error else Exception("All retry attempts failed")
            
    async def _standard_completion(
        self,
        payload: Dict[str, Any],
        start_time: float
    ) -> Dict[str, Any]:
        """Standard non-streaming completion"""
        # Don't auto-close sessions - let the caller manage lifecycle
        # If no session exists, create one that persists
        if not self.session:
            await self.create_session_if_needed()

        try:
            async with self.session.post(
                f"{self.BASE_URL}/chat/completions",
                headers=self.headers,
                json=payload
            ) as response:
                response_data = await response.json()
            
            if response.status != 200:
                error_msg = response_data.get("error", {}).get("message", "Unknown error")
                raise Exception(f"OpenRouter API error: {error_msg}")
                
            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Extract usage information
            usage = response_data.get("usage", {})
            
            # Enhanced handling for GPT-5 and other models with reasoning
            choices = response_data.get("choices", [])
            
            # Check if this is GPT-5 or similar model with reasoning capabilities
            if choices and "message" in choices[0]:
                message = choices[0]["message"]
                
                # CRITICAL: GPT-5 puts complex responses in reasoning field instead of content
                # For complex prompts, GPT-5 returns empty content but detailed reasoning
                content = message.get("content", "")
                reasoning = message.get("reasoning", "")
                
                # If content is empty but reasoning exists (GPT-5 pattern), use reasoning as content
                if not content and reasoning and payload.get("model") == "openai/gpt-5":
                    logger.info(f"GPT-5 returned empty content but {len(reasoning)} chars of reasoning - using reasoning as content")
                    message["content"] = reasoning  # Move reasoning to content field
                    message["original_content"] = ""  # Preserve original empty content
                    message["gpt5_mode"] = "reasoning_as_content"
                
                # Log if we have reasoning data (for debugging)
                if message.get("reasoning") or message.get("reasoning_details"):
                    model_name = payload.get("model", "unknown")
                    logger.info(f"Model {model_name} returned with reasoning data")
                    
                    # Log reasoning summary if available
                    if message.get("reasoning"):
                        logger.debug(f"Reasoning summary: {message['reasoning'][:200]}...")
            
            result = {
                "id": response_data.get("id"),
                "model": response_data.get("model"),
                "choices": choices,  # This includes all fields including reasoning
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                },
                "latency_ms": latency_ms,
                "provider": self._get_provider_from_model(payload["model"])
            }
            
            # Add provider-specific data if present
            if "provider" in response_data:
                result["provider_metadata"] = response_data["provider"]
            
            return result
        except Exception as e:
            logger.error(f"Error in _standard_completion: {e}")
            raise

    async def _stream_completion(
        self, 
        payload: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Streaming completion"""
        payload["stream"] = True
        
        async with self.session.post(
            f"{self.BASE_URL}/chat/completions",
            headers=self.headers,
            json=payload
        ) as response:
            async for line in response.content:
                if line:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith("data: "):
                        data = line_text[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            yield chunk
                        except json.JSONDecodeError:
                            continue
                            
    def _get_provider_from_model(self, model_id: str) -> str:
        """Extract provider from model ID"""
        if "/" in model_id:
            return model_id.split("/")[0]
        return "unknown"
        
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from OpenRouter"""
        await self.create_session_if_needed()
        
        async with self.session.get(
            f"{self.BASE_URL}/models",
            headers=self.headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("data", [])
            else:
                logger.error(f"Failed to fetch models: {response.status}")
                return []
                
    def estimate_cost(
        self, 
        model: str, 
        input_tokens: int, 
        output_tokens: int
    ) -> Decimal:
        """Estimate cost for a completion"""
        # This would use actual OpenRouter pricing
        # For now, use approximate values
        model_id = self.MODELS.get(model, model)
        
        # Pricing per million tokens (approximate)
        pricing = {
            "openai/gpt-5": {"input": 20, "output": 60},  # GPT-5 pricing estimate
            "openai/gpt-4o": {"input": 10, "output": 30},
            "openai/gpt-4": {"input": 30, "output": 60},
            "openai/gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
            "anthropic/claude-opus-4.1": {"input": 15, "output": 75},  # Claude 4.1 Opus
            "anthropic/claude-opus-4": {"input": 15, "output": 75},  # Claude 4 Opus
            "anthropic/claude-3-opus": {"input": 15, "output": 75},
            "anthropic/claude-3.5-sonnet": {"input": 3, "output": 15},
            "anthropic/claude-3-haiku": {"input": 0.25, "output": 1.25},
            "x-ai/grok-4": {"input": 10, "output": 30},  # Grok-4 pricing estimate
            "meta-llama/llama-3-70b-instruct": {"input": 0.8, "output": 0.8},
            "meta-llama/llama-3-8b-instruct": {"input": 0.2, "output": 0.2},
            "openrouter/horizon-alpha": {"input": 0, "output": 0},  # Free during testing
        }
        
        model_pricing = pricing.get(model_id, {"input": 1, "output": 1})
        
        input_cost = Decimal(str(model_pricing["input"])) * input_tokens / 1_000_000
        output_cost = Decimal(str(model_pricing["output"])) * output_tokens / 1_000_000
        
        return input_cost + output_cost

# Removed singleton instance - classes are instantiated where needed

async def test_openrouter():
    """Test OpenRouter connection"""
    try:
        async with OpenRouterClient() as client:
            # Test with a simple completion
            response = await client.complete(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say hello!"}
                ],
                max_tokens=50
            )
            
            print("OpenRouter test successful!")
            print(f"Response: {response['choices'][0]['message']['content']}")
            print(f"Tokens used: {response['usage']['total_tokens']}")
            print(f"Latency: {response['latency_ms']}ms")
            
            # Test model listing
            models = await client.get_available_models()
            print(f"\nAvailable models: {len(models)}")
            
            return True
            
    except Exception as e:
        print(f"OpenRouter test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_openrouter())