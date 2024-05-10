# Canny Edge Detection

> The Canny edge detector is an edge detection operator that uses a multi-stage algorithm to detect a wide range of edges in images. It was developed by John F. Canny in 1986. Canny also produced a computational theory of edge detection explaining why the technique works. (Wikipedia)

The Canny edge detection algorithm is composed of 5 steps:

- Noise reduction
- Gradient calculation
- Non-maximum suppresion
- Double threshold
- Edged tracking by hysteresis

The method uses images only on grayscales. For that reason it is a pre-requisite to convert the image to grayscale (done in the first step of the pre-processing).

## Noise Reduction

Edge detection is highly sensitive to image noise because it uses gradient calculation ([Step 2. Gradient calculation](#gradient-calculation)).

We will be applying _Gaussian Blur (or Gaussian Smoothing)_ to smooth the image. Image convolution technique is applied with a _Gaussian Kernel_ (3x3, 5x5, 7x7, ...). The kernel size depends

## Gradient calculation
