import cv2
import numpy as np

im_path_1 = '/Users/carlosnoyes/Data Storage/Hyper-Image/cfc_channel_test/2018-08-16-JD228_Channel_Stratum1_Set1_CH_2018-08-16_060006_532_732/2018-08-16-JD228_Channel_Stratum1_Set1_CH_2018-08-16_060006_532_732_100.jpg'
im_1 = cv2.imread(im_path_1)

A1 = im_1[:,:,0]
B1 = im_1[:,:,1]
C1 = im_1[:,:,2]

im = np.hstack((A1, B1, C1))
cv2.imshow('A1 - B1 - C1', im)
cv2.waitKey(0)
cv2.destroyAllWindows()

im_path_2 = '/Users/carlosnoyes/Data Storage/Hyper-Image/cfc_channel_test/2018-08-16-JD228_Channel_Stratum1_Set1_CH_2018-08-16_060006_532_732/2018-08-16-JD228_Channel_Stratum1_Set1_CH_2018-08-16_060006_532_732_101.jpg'
im_2 = cv2.imread(im_path_2)

A2 = im_2[:,:,0]
B2 = im_2[:,:,1]
C2 = im_2[:,:,2]

im = np.hstack((A2, B2, C2))
cv2.imshow('A2 - B2 - C2', im)
cv2.waitKey(0)
cv2.destroyAllWindows()

# im_a is the absolute value of the difference between the two C images using cv2.absdiff
a = cv2.absdiff(C1, C2)
im = np.hstack((A1, A2, a))
cv2.imshow('A1 - A2 - a: absdiff(C1, C2)', im)
cv2.waitKey(0)
cv2.destroyAllWindows()


im_path_base = '/Users/carlosnoyes/Data Storage/Hyper-Image/cfc_channel_test/2018-08-16-JD228_Channel_Stratum1_Set1_CH_2018-08-16_060006_532_732/2018-08-16-JD228_Channel_Stratum1_Set1_CH_2018-08-16_060006_532_732_'

mean_im = np.zeros(C2.shape)
frame_num = 199
for f in range(0,frame_num):
    frame_number = str(f).zfill(3)
    im_path = im_path_base + frame_number + '.jpg'
    im = cv2.imread(im_path)
    C = im[:,:,2].astype(np.float32)
    mean_im += C/frame_num


# create hyper image
frame_nums = [99, 100, 101]
identifiers_bgr = ['b', 'g', 'r']
identifiers_bw = ['1', '2', '3']
hyper_im = np.zeros((C2.shape[0], C2.shape[1], 3), dtype=np.uint8)

#save the middle image


for i, f in enumerate(frame_nums):

    frame_number = str(f).zfill(3)
    im_path = im_path_base + frame_number + '.jpg'
    im = cv2.imread(im_path)

    im_bgr = np.zeros(im.shape)
    im_bgr[:,:,i] = im[:,:,2]
    im_save_name = 'saved_images/hyper_image_' + identifiers_bgr[i] + '.png'
    cv2.imwrite(im_save_name, im_bgr)

    im_bw = im[:,:,2]
    im_save_name = 'saved_images/hyper_image_' + identifiers_bw[i] + '.png'
    cv2.imwrite(im_save_name, im_bw)

    hyper_im[:,:,i] = im[:,:,2]

cv2.imwrite('saved_images/hyper_image.png', hyper_im)

mean_im = mean_im.astype(np.uint8)
b = (C1.astype(np.float32) - mean_im.astype(np.float32)) / 2 + 127  # Normalize to 0-255 range
b = np.clip(b, 0, 255).astype(np.uint8)  # Clip to ensure valid range and convert to uint8
im = np.hstack((B1, mean_im, b))
cv2.imshow('B1 - mean - b: normalizeddiff(C1, mean)', im)
cv2.waitKey(0)









