import cv2
import matplotlib.pyplot as plt
img = cv2.imread('./img/first_frame.jpg') # Read the test img
plt.imshow(img) # Show results
plt.show()