import os
import json
import re
from typing import Dict, Any
import httpx
import asyncio
try:
    from dotenv import load_dotenv
    # Load repository backend .env so tests and scripts pick up GROQ_MODEL/GROQ_API_KEY
    _env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    load_dotenv(_env_path)
except Exception:
    pass


class LLMService:
    """Interface with Groq API for clinical reasoning."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        self.base_url = "https://api.groq.com/openai/v1"
        # Allow model override via env var; otherwise try auto-detection
        env_model = os.getenv("GROQ_MODEL")
        if env_model:
            self.model = env_model
        else:
            self.model = self._auto_detect_model()
        self.client = httpx.AsyncClient(timeout=60.0)
        # Use smaller defaults to reduce token pressure on free-tier quotas.
        self.extract_max_tokens = int(os.getenv("GROQ_EXTRACT_MAX_TOKENS", "320"))
        self.analysis_max_tokens = int(os.getenv("GROQ_ANALYSIS_MAX_TOKENS", "650"))
        self.max_prompt_chars = int(os.getenv("GROQ_MAX_PROMPT_CHARS", "5000"))

    def _auto_detect_model(self) -> str:
        """Query the Groq API for available models and pick a sensible default.

        Returns a model id string. Falls back to a reasonable default if detection fails.
        """
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.get(f"{self.base_url}/models", headers=headers)
                resp.raise_for_status()
                data = resp.json()
                # Try common response shapes
                models_list = None
                if isinstance(data, dict):
                    models_list = data.get("data") or data.get("models")
                if models_list is None and isinstance(data, list):
                    models_list = data

                candidates = []
                if isinstance(models_list, list):
                    for item in models_list:
                        if isinstance(item, dict):
                            mid = item.get("id") or item.get("model")
                        else:
                            mid = str(item)
                        if mid:
                            candidates.append(mid)

                # Prefer mixtral variants, then any groq model, otherwise first candidate
                for pref in ("mixtral-8x7b-32768", "mixtral-8x7b", "mixtral", "mixtral-instruct", "groq-"):
                    for c in candidates:
                        if pref in c:
                            print(f"[Model Detect] selected model: {c}")
                            return c

                if candidates:
                    print(f"[Model Detect] selected fallback model: {candidates[0]}")
                    return candidates[0]
        except Exception as e:
            print(f"[Model Detect] detection failed: {e}")

        # Final fallback
        fallback = os.getenv("GROQ_MODEL", "mixtral-8x7b")
        print(f"[Model Detect] using fallback model: {fallback}")
        return fallback

    async def extract_case_data(self, case_data: str) -> Dict[str, Any]:
        """Stage 1: Extract structured clinical elements from case data."""
        
        # Read extraction prompt
        prompt_path = os.path.join(
            os.path.dirname(__file__), "..", "prompts", "extraction_prompt.txt"
        )
        with open(prompt_path, "r") as f:
            prompt_template = f.read()
        
        # Use replace instead of format to avoid parsing JSON braces as format specifiers
        prompt = prompt_template.replace("{case_data}", case_data)
        prompt = self._trim_prompt(prompt)
        
        response = await self._call_groq(prompt, max_tokens=self.extract_max_tokens)
        return self._parse_json_response(response)

    async def analyze_case(
        self,
        case_data: str,
        training_cases: str,
        approval_criteria: str
    ) -> Dict[str, Any]:
        """Stage 2: Generate clinical reasoning and recommendation."""
        
        # Read reasoning prompt
        prompt_path = os.path.join(
            os.path.dirname(__file__), "..", "prompts", "reasoning_prompt.txt"
        )
        with open(prompt_path, "r") as f:
            prompt_template = f.read()
        
        # Use replace instead of format to avoid parsing JSON braces as format specifiers
        prompt = prompt_template.replace("{case_data}", case_data)
        prompt = prompt.replace("{training_cases}", training_cases)
        prompt = prompt.replace("{approval_criteria}", approval_criteria)
        prompt = self._trim_prompt(prompt)
        
        response = await self._call_groq(prompt, max_tokens=self.analysis_max_tokens)
        return self._parse_json_response(response)

    async def _call_groq(self, prompt: str, max_tokens: int = 900, retries: int = 1) -> str:
        """Make async API call to Groq."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a healthcare pre-authorization clinical reviewer. Respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,  # Low temperature for consistent, factual responses
            "max_tokens": max_tokens,
            "top_p": 0.9
        }
        
        attempt = 0
        while True:
            try:
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
            except httpx.HTTPError as e:
            # Include response body if available for easier debugging
                resp = getattr(e, "response", None)
                body = None
                try:
                    if resp is not None:
                        body = await resp.aread() if hasattr(resp, "aread") else resp.text
                except Exception:
                    body = None

                status = getattr(resp, "status_code", None)
                error_str = str(e)
                print(f"[LLM] HTTP Error: Status {status if status is not None else '?'} - {error_str}")
                if body:
                    print(f"[LLM] Response body: {body[:300]}")

                # Retry once for transient errors and reduce completion size on retry.
                if attempt < retries and status in (429, 500, 502, 503, 504):
                    attempt += 1
                    payload["max_tokens"] = max(350, int(payload["max_tokens"] * 0.7))
                    wait_seconds = 1.5 * attempt
                    if status == 429 and body:
                        try:
                            body_text = body.decode("utf-8", errors="ignore") if isinstance(body, (bytes, bytearray)) else str(body)
                            match = re.search(r"try again in\s*([0-9]+(?:\.[0-9]+)?)s", body_text, re.IGNORECASE)
                            if match:
                                wait_seconds = max(wait_seconds, float(match.group(1)) + 0.5)
                        except Exception:
                            pass
                    await asyncio.sleep(wait_seconds)
                    continue

                if body:
                    raise Exception(f"Groq API error: {error_str}; body: {body}")
                raise Exception(f"Groq API error: {error_str}")

    def _trim_prompt(self, prompt: str) -> str:
        """Hard-cap prompt size to avoid oversized requests on free-tier quotas."""
        if len(prompt) <= self.max_prompt_chars:
            return prompt
        tail = prompt[-self.max_prompt_chars:]
        return "[Prompt truncated for token safety]\n" + tail

    @staticmethod
    def _parse_json_response(response: str) -> Dict[str, Any]:
        """Extract and parse JSON from LLM response."""
        def ensure_shape(data: Dict[str, Any]) -> Dict[str, Any]:
            if not isinstance(data, dict):
                data = {}
            data.setdefault("recommendation", "NEED_MORE_INFO")
            data.setdefault("clinical_summary", "Analysis completed with partial structured output")
            data.setdefault("supporting_evidence", [])
            data.setdefault("missing_documentation", [])
            data.setdefault("provider_questions", [])
            data.setdefault("denial_risks", [])
            return data

        def try_load_json(text: str):
            try:
                return json.loads(text)
            except Exception:
                return None

        try:
            # Try direct parsing
            parsed = try_load_json(response)
            if parsed is not None:
                return ensure_shape(parsed)
        except json.JSONDecodeError as e:
            print(f"[DEBUG] JSON parse error: {e}")
            print(f"[DEBUG] Response: {response[:500]}")
            
            # Try to extract JSON from markdown code blocks
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                if end > start:
                    json_str = response[start:end].strip()
                    parsed = try_load_json(json_str)
                    if parsed is not None:
                        return ensure_shape(parsed)
                    else:
                        print(f"[DEBUG] Failed to parse markdown JSON block")
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                if end > start:
                    json_str = response[start:end].strip()
                    parsed = try_load_json(json_str)
                    if parsed is not None:
                        return ensure_shape(parsed)
                    else:
                        print(f"[DEBUG] Failed to parse code block")
            
            # Try to find JSON-like structures using regex
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                parsed = try_load_json(json_match.group())
                if parsed is not None:
                    return ensure_shape(parsed)
                else:
                    print(f"[DEBUG] Failed to parse regex-matched JSON")

            # Try to repair truncated JSON by balancing braces on the first object.
            first = response.find("{")
            if first != -1:
                candidate = response[first:]
                open_count = candidate.count("{")
                close_count = candidate.count("}")
                if open_count > close_count:
                    candidate = candidate + ("}" * (open_count - close_count))
                last = candidate.rfind("}")
                if last != -1:
                    repaired = candidate[: last + 1]
                    parsed = try_load_json(repaired)
                    if parsed is not None:
                        print("[DEBUG] Recovered JSON by balancing braces")
                        return ensure_shape(parsed)
            
            # Fallback: return structured error with raw response
            return {
                "error": f"Failed to parse JSON response: {str(e)}",
                "raw_response": response[:1000],
                "recommendation": "NEED_MORE_INFO",
                "clinical_summary": "Unable to process case due to response parsing error",
                "supporting_evidence": [],
                "missing_documentation": [],
                "provider_questions": [],
                "denial_risks": []
            }

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
