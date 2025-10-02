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
from transformers import AutoModelForImageTextToText, AutoProcessor


class LLMBackbone:
    def __init__(self, model_name="Qwen/Qwen3-VL-235B-A22B-Instruct"):
        # Load the Qwen-VL model and processor
        self.model = AutoModelForImageTextToText.from_pretrained(
            model_name, dtype="auto", device_map="auto"
        )
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.system_prompt = self._load_system_prompt()

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

    def infer(self, image=None, text=None, pred_context=None, max_new_tokens=512):
        """
        Run inference on the Qwen-VL model.
        image: path, PIL.Image, or URL of Sonar bounding box image from model.
        text: user text prompt
        pred_context: predicted context from the maintainance model and location/time/etc for sonar pred.
        Returns: output text (list of strings, one per input)
        """
        messages = self.build_messages(
            image=image, text=text, pred_context=pred_context
        )
        inputs = self.processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt",
        )
        inputs = inputs.to(self.model.device)
        generated_ids = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        generated_ids_trimmed = [
            out_ids[len(in_ids) :]
            for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )
        return output_text

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
    image_url = (
        "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"
    )
    prompt = "Describe this image."
    llm = LLMBackbone()
    result = llm.decode(image=image_url, text=prompt)
    print(result)
