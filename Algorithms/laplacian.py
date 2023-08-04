import cv2
import matplotlib.pyplot as plt

# Open the image
img = cv2.imread('image.webp')

# Apply gray scale
gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply gaussian blur
blur_img = cv2.GaussianBlur(gray_img, (3, 3), 0)

# Positive Laplacian Operator
laplacian = cv2.Laplacian(blur_img, cv2.CV_64F)

plt.figure()
plt.title('Edge Detection')
plt.imsave('result(laplacian).webp', laplacian, cmap='gray', format='png')
plt.imshow(laplacian, cmap='gray')
plt.show()