
import torch
from torch.nn import Sigmoid
from model import MaintananceNN

model = MaintananceNN()
sig = Sigmoid()

model.load_state_dict(torch.load("working_model.pt", weights_only=True))


def IsEngineFine(engine_stats):
    ''' 1 if the engine is fine. Input array of Engine rpm, Lube oil pressure, Fuel pressure, Coolant pressure, lube oil temp, Coolant temp'''
    return round(sig(model(torch.tensor(engine_stats))).item())

if __name__ == "__main__":
    # Engine rpm  Lub oil pressure  Fuel pressure  Coolant pressure  lub oil temp  Coolant temp
    d = [791.23, 3.30, 4.65, 2.33, 77.64, 78.42]
    print(sig(model(torch.tensor(d))))

    print(IsEngineFine(d))