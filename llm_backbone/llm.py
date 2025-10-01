"""
Author: Kamran Hussain
Date: 2025-10-01

LLM.py

Description:
Load a pretrained LLM model, and use it to generate 
instructions/responses from the user. Includes the large 
system prompt and integration with other front-ends for
multi-modal AR output. 
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class LLMBackbone(nn.Module):
    def __init__(self, model_name):
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        

    def forward(self, x):
        pass

    def decode(self, x, engine_stats):
        pass