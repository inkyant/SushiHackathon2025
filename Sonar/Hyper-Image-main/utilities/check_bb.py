import os
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches

dir_path = '/Users/carlosnoyes/Data Storage/Hyper-Image/cfc_train_stack_n3'

im_name = '2018-05-26-JD146_LeftFar_Stratum2_Set1_LO_2018-05-26_181003_1515_1715_058.png'
im_path = os.path.join(dir_path, 'images', im_name)
label_name = im_name.replace('.png', '.txt')
label_path = os.path.join(dir_path, 'labels', label_name)

im = cv2.imread(im_path)

with open(label_path, 'r') as f:
    lines = f.readlines()

fig, ax = plt.subplots(1)
ax.imshow(im)
ax.axis('off')
for line in lines:
    class_id, x, y, w, h = line.split()
    x, y, w, h = float(x), float(y), float(w), float(h)
    x, y, w, h = x*im.shape[1], y*im.shape[0], w*im.shape[1], h*im.shape[0]
    rect = patches.Rectangle((x-w/2, y-h/2), w, h, linewidth=1, edgecolor='r', facecolor='none')
    ax.add_patch(rect)
plt.show()

