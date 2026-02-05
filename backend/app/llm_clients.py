import os
from typing import List, Dict, Any, Optional
import ollama
import litellm
from sentence_transformers import SentenceTransformer, util

class OllamaUnavailable(Exception):
    """Custom exception for when Ollama is unavailable."""
    pass

class LLMClient:
    def __init__(self, use_ollama: bool = True, ollama_model: str = "llama3", cloud_model: str = "gpt-4o-mini"):
        self.use_ollama = use_ollama
        self.ollama_model = os.getenv("OLLAMA_MODEL", ollama_model)
        self.cloud_model = os.getenv("CLOUD_LLM_MODEL", cloud_model)
        self.ollama_client = None
        
        if self.use_ollama:
            try:
                self.ollama_client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
                # Verify Ollama connection and model existence
                # This call can fail if Ollama server is down or model is not pulled
                self.ollama_client.show(self.ollama_model) 
                print(f"Ollama '{self.ollama_model}' client initialized.")
            except Exception as e:
                print(f"Warning: Ollama connection or model '{self.ollama_model}' check failed: {e}. Defaulting to cloud LLM.")
                self.use_ollama = False
        
        if not self.use_ollama:
            print(f"Using cloud LLM: {self.cloud_model}")

    async def translate_or_clarify(self, script_language_input: str, context: Optional[str] = None) -> str:
        messages = [{"role": "user", "content": f"You are a translator from a formulaic Script Language to a Basque-based Hive Code. If the Script Language is ambiguous or incomplete, ask a single, clear clarifying question. If it is well-formed, provide ONLY the Hive Code. Context: {context if context else 'None'}. Script: {script_language_input}"}]
        
        if self.use_ollama and self.ollama_client:
            try:
                # Actual Ollama client call
                response = self.ollama_client.chat(model=self.ollama_model, messages=messages)
                return response["message"]["content"]
            except Exception as e:
                print(f"Ollama call failed: {e}. Falling back to cloud model.")
                # Fallthrough to cloud
        
        # Use LiteLLM for cloud fallback
        try:
            # Actual LiteLLM call
            response = await litellm.acompletion(model=self.cloud_model, messages=messages)
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Cloud LLM call failed: {e}")


class EmbeddingClient:
    def __init__(self, model_name: str = "ixa-ehu/berteus-base-cased"):
        self.model_name = os.getenv("EMBEDDING_MODEL", model_name)
        self.model = None
        try:
            # The model will be downloaded the first time it's initialized
            self.model = SentenceTransformer(self.model_name)
            print(f"Embedding model '{self.model_name}' loaded successfully.")
        except Exception as e:
            print(f"Warning: Could not load SentenceTransformer model '{self.model_name}'. Embeddings will be mocked. Error: {e}")

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if self.model:
            print(f"EmbeddingClient: Generating embeddings for {len(texts)} texts using '{self.model_name}'...")
            embeddings = self.model.encode(texts, convert_to_numpy=False, normalize_embeddings=True)
            return embeddings.tolist()
        else:
            # Fallback to mock embeddings if model loading failed
            print(f"EmbeddingClient: Simulating embeddings for texts: {texts}")
            # Mock 768-dim embeddings. Assuming normalize_embeddings=True for consistency.
            return [[float(hash(text) % 1000) / 1000.0] * 768 for text in texts]