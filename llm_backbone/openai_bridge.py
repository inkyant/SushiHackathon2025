import base64
import io
import mimetypes
import os
from typing import Any, Optional

try:
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover
    Image = None  # type: ignore

try:
    # OpenAI Python SDK v1.x
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


class LLMBackbone:
    def __init__(self, model_name: Optional[str] = None):
        """
        OpenAI-backed LLM backbone, mirroring the interface and behavior of llm.py
        but using OpenAI Chat Completions with vision support.
        Default model is "gpt-5-thinking" (override via arg or OPENAI_MODEL_NAME env).
        """
        selected = (
            model_name
            or os.getenv("OPENAI_MODEL_NAME")
            or os.getenv("LLM_MODEL_NAME")
            or "gpt-5"
        )
        self.selected_model_name = selected

        # Initialize OpenAI client; uses OPENAI_API_KEY from env if present
        if OpenAI is None:
            raise ImportError(
                "OpenAI SDK is not installed. Install with `pip install openai`."
            )
        self.client = OpenAI()

        self.system_prompt = self._load_system_prompt()
        # For feature parity with llm.py
        self.vision_capable = True

    def _load_system_prompt(self) -> str:
        try:
            here = __file__.rsplit("/", 1)[0]
            local_path = f"{here}/system_prompt.md"
            try:
                with open(local_path, "r") as f:
                    return f.read()
            except FileNotFoundError:
                with open("system_prompt.md", "r") as f:
                    return f.read()
        except FileNotFoundError:
            return ""

    def build_messages(
        self,
        image: Any = None,
        text: Optional[str] = None,
        pred_context: Optional[str] = None,
    ):
        """
        Build OpenAI Chat Completions message list with system prompt, a composed
        user text (from _build_prompt), and optional vision content.
        """
        user_text = self._build_prompt(
            image=image, text=text, pred_context=pred_context
        )

        user_content = []
        if user_text:
            user_content.append({"type": "text", "text": user_text})

        if image is not None:
            img_part = self._image_to_openai_content(image)
            if img_part is not None:
                user_content.append(img_part)

        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": user_content})
        return messages

    def _build_prompt(
        self,
        image: Any = None,
        text: Optional[str] = None,
        pred_context: Optional[str] = None,
    ) -> str:
        """
        Compose the user-side textual prompt. The system prompt is injected
        separately as a system message, so this returns only the user content.

        Also appends a concise request for missing context fields so the model
        can ask the user for the minimum required info.
        """
        parts = []

        # Include structured context when present
        if pred_context:
            parts.append(f"Context:\n{pred_context}")

        # Primary user instruction or default
        user_instruction = (
            text or "Provide a concise sonar interpretation and engine health summary."
        )
        parts.append(f"User:\n{user_instruction}")

        # Heuristic check for missing fields in provided context/text
        needed_request = (
            "Please provide location/time, water temperature, sonar detections (counts/sizes), "
            "and engine readings (rpm, oil/fuel/coolant pressures and temps) so I can give a precise one-sentence fishing trip status."
        )

        def _contains_any(s: str, keywords: list[str]) -> bool:
            s_low = s.lower()
            return any(k in s_low for k in keywords)

        combined = "\n".join([pred_context or "", text or ""]).strip()
        has_loc_time = _contains_any(
            combined,
            [
                "lat",
                "lon",
                "location",
                "harbor",
                "bay",
                "gps",
                "time",
                "date",
                "season",
            ],
        )
        has_temp = _contains_any(
            combined, ["water temp", "sea temp", "sst", "temperature"]
        )
        has_detections = _contains_any(
            combined,
            ["detection", "detections", "fish", "school", "count", "size"],
        )
        has_engine = _contains_any(
            combined,
            [
                "rpm",
                "oil pressure",
                "fuel pressure",
                "coolant pressure",
                "oil temp",
                "coolant temp",
                "coolant temperature",
                "oil temperature",
            ],
        )

        if not (has_loc_time and has_temp and has_detections and has_engine):
            parts.append(needed_request)

        return "\n\n".join(parts).strip()

    def _encode_pil_image_to_data_url(self, image_obj: Any) -> str:
        if Image is None:
            raise RuntimeError("PIL is required to encode PIL images. Install pillow.")
        if not isinstance(image_obj, Image.Image):  # type: ignore[attr-defined]
            raise ValueError("image_obj must be a PIL.Image when using PIL encoding")
        buffer = io.BytesIO()
        image_obj.save(buffer, format="PNG")
        base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{base64_image}"

    def _encode_file_image_to_data_url(self, file_path: str) -> str:
        mime, _ = mimetypes.guess_type(file_path)
        if mime is None:
            # Default to PNG if unknown
            mime = "image/png"
        with open(file_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime};base64,{base64_image}"

    def _image_to_openai_content(self, image: Any) -> Optional[dict]:
        """
        Convert input image (URL string, local path, or PIL.Image) into OpenAI
        vision content object for chat messages.
        """
        if image is None:
            return None

        # If it's a string, distinguish URL vs file path
        if isinstance(image, str):
            lower = image.lower()
            if lower.startswith("http://") or lower.startswith("https://"):
                return {
                    "type": "image_url",
                    "image_url": {"url": image},
                }
            # treat as local file path
            if os.path.exists(image) and os.path.isfile(image):
                data_url = self._encode_file_image_to_data_url(image)
                return {
                    "type": "image_url",
                    "image_url": {"url": data_url},
                }
            # Unrecognized string; pass as-is in text to preserve behavior
            return {"type": "text", "text": f"[Image reference: {image}]"}

        # If it's a PIL image
        if Image is not None and isinstance(image, Image.Image):  # type: ignore[attr-defined]
            data_url = self._encode_pil_image_to_data_url(image)
            return {
                "type": "image_url",
                "image_url": {"url": data_url},
            }

        # Fallback: stringified reference
        return {"type": "text", "text": f"[Image reference: {image}]"}

    def infer(
        self,
        image: Any = None,
        text: Optional[str] = None,
        pred_context: Optional[str] = None,
        max_new_tokens: int = 512,
    ):
        """
        Run inference using OpenAI Chat Completions with a reasoning-capable model.
        Returns a list with one string (to mirror llm.py behavior).
        """
        # Build OpenAI message structure via shared builder
        messages = self.build_messages(
            image=image, text=text, pred_context=pred_context
        )

        # Call OpenAI
        completion = self.client.chat.completions.create(
            model=self.selected_model_name,
            messages=messages,
        )

        text_out = ""
        if completion and completion.choices:
            msg = completion.choices[0].message
            if msg and getattr(msg, "content", None):
                text_out = msg.content

        return [text_out]

    # For compatibility with previous interface
    def forward(
        self,
        image: Any = None,
        text: Optional[str] = None,
        pred_context: Optional[str] = None,
        max_new_tokens: int = 512,
    ):
        return self.infer(
            image=image,
            text=text,
            pred_context=pred_context,
            max_new_tokens=max_new_tokens,
        )

    def decode(
        self,
        image: Any = None,
        text: Optional[str] = None,
        pred_context: Optional[str] = None,
        max_new_tokens: int = 512,
    ):
        output = self.infer(
            image=image,
            text=text,
            pred_context=pred_context,
            max_new_tokens=max_new_tokens,
        )
        if isinstance(output, list) and len(output) > 0:
            return output[0]
        return output


if __name__ == "__main__":
    image_url = "https://example.com/sonar.jpg"
    prompt = "Summarize likely fish species and engine health."
    llm = LLMBackbone()
    result = llm.decode(image=image_url, text=prompt)
    print(result)
