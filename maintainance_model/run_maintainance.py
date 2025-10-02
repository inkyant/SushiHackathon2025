import torch
from torch.nn import Softmax
from model import MaintananceNN
import os

# Define your class labels in the order your model outputs them
CLASS_LABELS = [
    "No Issue",
    "Engine RPM too low",
    "Engine RPM too high",
    "Lub oil pressure too low",
    "Lub oil pressure too high",
    "Fuel pressure too low",
    "Fuel pressure too high",
    "Coolant pressure too low",
    "Coolant pressure too high",
    "Lub oil temp abnormal",
    "Coolant temp abnormal",
]


def load_model(model_path="multiclass_model.pt"):
    model = MaintananceNN()
    # Resolve path relative to this file's directory if not absolute
    if not os.path.isabs(model_path):
        here = os.path.dirname(__file__)
        candidate = os.path.join(here, model_path)
        model_path = candidate if os.path.exists(candidate) else model_path
    # Fallback: try loading without weights_only for older torch
    try:
        state = torch.load(model_path, weights_only=True)
    except TypeError:
        state = torch.load(model_path)
    model.load_state_dict(state)
    model.eval()
    return model


def get_engine_fault(engine_stats, model=None):
    """
    Given engine_stats (list or array of 6 floats), returns (label, confidence, all_probs)
    """
    if model is None:
        model = load_model()
    sm = Softmax(dim=0)
    x = torch.tensor(engine_stats, dtype=torch.float32)
    with torch.no_grad():
        logits = model(x)
        probs = sm(logits)
        probs_np = probs.detach().cpu().numpy()
        idx = probs.argmax().item()
        label = CLASS_LABELS[idx]
        confidence = probs_np[idx]
    return label, confidence, probs_np


if __name__ == "__main__":
    # Example input: Engine rpm, Lub oil pressure, Fuel pressure, Coolant pressure, lub oil temp, Coolant temp
    d = [791.23, 3.30, 4.65, 2.33, 77.64, -78.42]
    model = load_model()
    label, confidence, probs = get_engine_fault(d, model)
    print(f"Predicted fault: {label}")
    print(f"Confidence: {confidence:.3f}")
    print(f"All probabilities: {probs}")
