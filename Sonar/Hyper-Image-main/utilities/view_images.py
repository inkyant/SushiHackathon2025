import cv2
import numpy as np

im_path = '/Users/carlosnoyes/Data Storage/Hyper-Image/cfc_channel_test/2018-08-16-JD228_Channel_Stratum1_Set1_CH_2018-08-16_060006_532_732/2018-08-16-JD228_Channel_Stratum1_Set1_CH_2018-08-16_060006_532_732_100.jpg'
im = cv2.imread(im_path)

cv2.imshow('image', im)
cv2.waitKey(0)
cv2.destroyAllWindows()

im_1 = im[:,:,0]
im_2 = im[:,:,1]
im_3 = im[:,:,2]

im_all = np.hstack((im_1, im_2, im_3))
cv2.imshow('all channels', im_all)
cv2.waitKey(0)
cv2.destroyAllWindows()



