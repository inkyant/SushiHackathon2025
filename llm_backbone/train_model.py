"""
Author: Kamran Hussain
Date: 2025-10-01

Train_model.py

Description:
This script loads a model from hugging face, builds
a datalaoder for whatever data we want, and trains the model.

"""

import torch
import torch.nn as nn
import torch.optim as optim
import transformers
from lightning.pytorch import LightningModule

class LLMBackbone(LightningModule):
    def __init__(self, model_name):
        super(LLMBackbone, self).__init__()
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
    
    def forward(self, x):
        """
        Forward pass for the model. 
        """
        return self.decode(x)

    def decode(self, x):
        pass


        