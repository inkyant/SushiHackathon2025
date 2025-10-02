"""
Author: Kamran Hussain
Date: 2025-10-01

LLM.py

Description:
Load a pretrained Qwen-VL model, and use it to generate
instructions/responses from the user. Includes the large
system prompt and integration with other front-ends for
multi-modal AR output.
"""

import torch
from transformers import AutoProcessor
from transformers import Gemma3ForConditionalGeneration
from typing import Any, Optional
from PIL import Image


class LLMBackbone:
    def __init__(self, model_name=None):
        # Load a text-only instruction model (default: google/gemma-3-4b-it)
        import os

        selected = model_name or os.getenv("LLM_MODEL_NAME", "google/gemma-3-4b-it")
        self.selected_model_name = selected

        # Hugging Face auth via env token
        hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
        if hf_token:
            try:
                # Best effort: log in for this process so downstream hub calls work
                from huggingface_hub import login as hf_login

                hf_login(token=hf_token, add_to_git_credential=False)
            except Exception:
                pass
            # Also expose to subprocess/lib calls
            os.environ.setdefault("HUGGING_FACE_HUB_TOKEN", hf_token)

        self.hf_token = hf_token
        # Load Gemma-3 vision model and processor
        self.model = Gemma3ForConditionalGeneration.from_pretrained(
            self.selected_model_name,
            device_map="auto",
            token=self.hf_token,
        ).eval()
        self.processor = AutoProcessor.from_pretrained(
            self.selected_model_name,
            token=self.hf_token,
        )
        self.system_prompt = self._load_system_prompt()
        self.vision_capable = True

    def _load_system_prompt(self):
        try:
            # Try local dir first
            here = __file__.rsplit("/", 1)[0]
            local_path = f"{here}/system_prompt.md"
            if torch.cuda.is_available():
                pass  # no-op; ensures torch import used
            try:
                with open(local_path, "r") as f:
                    return f.read()
            except FileNotFoundError:
                # Fallback to CWD
                with open("system_prompt.md", "r") as f:
                    return f.read()
        except FileNotFoundError:
            return ""

    def build_messages(self, image=None, text=None, pred_context=None):
        """
        Build a Qwen-VL chat message list.
        If image is a path or PIL.Image, include it as the image.
        If text is provided, include it as the user text.
        """
        content = []
        if image is not None:
            content.append({"type": "image", "image": image})
        if text is not None:
            content.append({"type": "text", "text": text})
        if pred_context is not None:
            content.append({"type": "text", "text": pred_context})
        # Optionally prepend system prompt
        if self.system_prompt:
            # Qwen-VL expects system prompt as a message with role "system"
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": content},
            ]
        else:
            messages = [{"role": "user", "content": content}]
        return messages

    def _load_image(self, image: Any) -> Any:
        """Text-only model: keep image reference as-is for prompt context."""
        return image

    def _has_sentencepiece(self) -> bool:
        try:
            import sentencepiece  # type: ignore

            return True
        except Exception:
            return False

    def _load_tokenizer_with_strategies(self, model_name: str, token: Optional[str]):
        try:
            return AutoTokenizer.from_pretrained(model_name, token=token)
        except Exception:
            pass
        try:
            return AutoTokenizer.from_pretrained(
                model_name, trust_remote_code=True, token=token
            )
        except Exception:
            pass
        try:
            return AutoTokenizer.from_pretrained(
                model_name, trust_remote_code=True, use_fast=False, token=token
            )
        except Exception:
            return None

    def _select_tokenizer_and_model(self, preferred_model: str, token: Optional[str]):
        candidates = []
        if self._has_sentencepiece():
            candidates.extend(
                [preferred_model, "google/gemma-2-2b-it", "google/gemma-2-9b-it"]
            )
        # Always include non-sentencepiece fallbacks
        candidates.extend(["mistralai/Mistral-7B-Instruct-v0.2", "gpt2"])
        seen = set()
        deduped = []
        for c in candidates:
            if c not in seen:
                deduped.append(c)
                seen.add(c)
        for name in deduped:
            tok = self._load_tokenizer_with_strategies(name, token)
            if tok is not None:
                return tok, name
        raise ValueError(
            "Failed to load any compatible tokenizer. Install `pip install -U transformers sentencepiece` or set LLM_MODEL_NAME to a supported model."
        )

    def _build_prompt(self, image=None, text=None, pred_context=None) -> str:
        parts = []
        if self.system_prompt:
            parts.append(self.system_prompt.strip())
        if pred_context:
            parts.append(f"Context:\n{pred_context}")
        if image:
            parts.append(f"[Image reference: {image}]")
        user = (
            text or "Provide a concise sonar interpretation and engine health summary."
        )
        parts.append(f"User:\n{user}")
        return "\n\n".join(parts).strip()

    def infer(self, image=None, text=None, pred_context=None, max_new_tokens=512):
        """
        Run inference on the Qwen-VL model.
        image: path, PIL.Image, or URL of Sonar bounding box image from model.
        text: user text prompt
        pred_context: predicted context from the maintainance model and location/time/etc for sonar pred.
        Returns: output text (list of strings, one per input)
        """
        # Gemma-3 vision generation using processor chat template
        messages = self.build_messages(
            image=image, text=text, pred_context=pred_context
        )
        inputs = self.processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.model.device, dtype=torch.bfloat16)

        input_len = inputs["input_ids"].shape[-1]
        with torch.inference_mode():
            generation = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
            )
            generation = generation[0][input_len:]

        decoded = self.processor.decode(generation, skip_special_tokens=True)
        return [decoded]

    # For compatibility with previous interface
    def forward(self, image=None, text=None, pred_context=None, max_new_tokens=512):
        return self.infer(
            image=image,
            text=text,
            pred_context=pred_context,
            max_new_tokens=max_new_tokens,
        )

    def decode(self, image=None, text=None, pred_context=None, max_new_tokens=512):
        """
        Returns the generated text only (first item if batch size 1).
        """
        output = self.infer(
            image=image,
            text=text,
            pred_context=pred_context,
            max_new_tokens=max_new_tokens,
        )
        if isinstance(output, list) and len(output) > 0:
            return output[0]
        return output


# Example usage:
if __name__ == "__main__":
    # Example image URL and prompt
    image_url = "https://example.com/sonar.jpg"
    prompt = "Summarize likely fish species and engine health."
    llm = LLMBackbone()
    result = llm.decode(image=image_url, text=prompt)
    print(result)
