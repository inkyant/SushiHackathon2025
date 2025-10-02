import numpy as np
path = "/Users/carlosnoyes/Data Storage/Hyper-Image/cfc_train_stack_n1/images/2018-05-29-JD149_LeftFar_Stratum1_Set1_LO_2018-05-29_180004_2871_3086_165.npy"
im = np.load(path)
print(im.shape)  # Should be (H, W, C) where C=3
print(im.max(), im.min())  # Check pixel value ranges