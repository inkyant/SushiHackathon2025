
import torch
from torch.nn import Softmax
from model import MaintananceNN

model = MaintananceNN()
sm = Softmax(dim=0)

model.load_state_dict(torch.load("multiclass_model.pt", weights_only=True))


def getEngineFault(engine_stats):
    '''These are the inputs:
    'Engine rpm'
    'Lube oil pressure'
    'Fuel pressure'
    'Coolant pressure'
    'lub oil temp'
    'Coolant temp'
    And the output is a probability vector, ordered 'No Issue', 'Engine RPM too low', 'Engine RPM too high', so on
    '''
    return sm(model(torch.tensor(engine_stats))).detach().numpy()

if __name__ == "__main__":
    # Engine rpm, Lub oil pressure, Fuel pressure, Coolant pressure, lub oil temp, Coolant temp
    # d = [791.23, 3.30, 4.65, 2.33, 77.64, 78.42]
    d = [791.23, 3.30, 4.65, 2.33, 77.64, 78.42]
    print(model(torch.tensor(d)))

    print(getEngineFault(d))
    
    print(torch.argmax(model(torch.tensor(d))).item())