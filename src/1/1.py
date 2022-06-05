# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 09:39:29 2022

@author: James
"""

import os
import re
from os.path import exists
from wand.image import Image
from wand.color import Color

filein = "./test/"
fileout = "./output/"

files = os.listdir(filein)

# Filter out non-desired files
files = filter(lambda x: re.match(r"^\w+(.tiff|.tif)$", x) is not None,
               files)

for filename in files:
    print(filename)
    with Image(filename=filein + filename, resolution=150) as img:
                format = "PNG"
                img.save(filename=fileout + filename)

