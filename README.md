# Computer Vision - Assignment 1

Using Python's OpenCV Library, images were made adjustable for in terms of their Contrast and Brightness.

This is performed by using `convertScaleAbs()` using the `alpha` parameter to adjust Constrast and the `beta` parameter to adjust Brightness.

Additionally, with `matplotlib.pyplot`, histograms showing Frequency over Pixel Intensity are displayed for the original and processed image.

___

The assignment features an interface made with Tom Schimansky's [`customtkinter`](https://customtkinter.tomschimansky.com) library. 
The GUI allows users to upload a desired image and alter the image using sliders, one for contrast and the other for brightness.
Edited images can then be saved to the user's local files, if desired.
