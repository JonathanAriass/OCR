from PIL import Image

# Open an image file
image_path = "./assets/image.png"
image = Image.open(image_path)

# Get the pixel values as a list of tuples
pixels = list(image.getdata())

# If you need to access individual pixel values, you can do something like this
# This example gets the pixel value at position (x=100, y=50)
pixel_value = image.getpixel((100, 50))

print("Pixel values:", pixels)
print("Pixel value at (100, 50):", pixel_value)