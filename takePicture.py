import picamera, os
from PIL import Image, ImageDraw
camera = picamera.PiCamera()
camera.capture('image1.jpg')
os.system("xdg-open image1.jpg")
