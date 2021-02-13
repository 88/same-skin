# same skin

# imports
from PIL import Image, ImageDraw, ImageColor
import random, os, requests

# main script
use_skin_url = True if input("use skin url [y/n]: ").lower() == "y" else False
if use_skin_url:
    skin_url = input("url of skin: ")
    filename = input("filename (without .png): ")
    r = requests.get(skin_url)
    with open(f"{filename}.png", "wb+") as f:
        f.write(r.content)
    base_file = f"{filename}.png"
else:
    base_file = input("name of skin template (e.g skin.png) - must be in same folder: ")
number_of_skins = int(input("how many skins do you want to make? "))

with Image.open(base_file).convert('RGBA') as skin: # open the image file
    for i in range(number_of_skins): # make skins
        for pixelx in range(8):
            for pixely in range(8):
                skin.putpixel((pixelx,pixely), (random.randint(0, 255),random.randint(0, 255),random.randint(0, 255))) # random pixels
        if not os.path.exists(f"{base_file}-sameskin"):
            os.makedirs(f"{base_file}-sameskin")
        skin.save(f"./{base_file}-sameskin/skins-{i}.png") # save the skin
