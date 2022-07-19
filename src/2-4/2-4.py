# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 09:39:29 2022

@author: James
"""
""" 
 Should make one tiff image with multi layers.
"""

import os
import re
from io import BytesIO
from wand.image import Image as WIMAGE
from wand.api import library
import pyvips

### Python pdf
from PyPDF2.pdf import PdfFileReader , PdfFileWriter
from PyPDF2.merger import PdfFileMerger 

###  load image file to save pdf
from PIL import Image as PIMAGE
from reportlab.pdfgen.canvas import Canvas
from ctypes import c_void_p, c_size_t

from datetime import datetime
import xml.etree.ElementTree as ET
import sys
sys.path.append('../../py_modules')


        
## init constant 
filein = "../../tif/"
fileout = "./output/"
jpgin = "./jpg_path/"
jpgout = "./jpg_path/"


# variable image list and index
img_list = []
index = 0
scaled_rate = 0.3          # width for scaling rate

# pdf metadata information
metadata = {
    u'/Version': 'PDF-1.4'
}

# Tell Python's wand library about the MagickWand Compression Quality (not Image's Compression Quality)
library.MagickSetCompressionQuality.argtypes = [c_void_p, c_size_t]

## get XML root 
tree = ET.parse('record.xml')
root = tree.getroot()

### set start time
time = root.find('process').find('time')
time_start = time.find('start')
time_start.text = datetime.now().strftime("%H:%M:%S")

files = os.listdir(filein)

def getNewStep(n_step , total_no , no , name):
    n_step.set("No", str( total_no ))
    n_no = ET.SubElement(n_step, "sub_no")
    n_no.text = str( no )
    n_name = ET.SubElement(n_step, "description")
    n_name.text = name
    n_status = ET.SubElement(n_step, "status")
    return (n_no , n_name, n_status)

# Filter out non-desired files
files = filter(lambda x: re.match(r"^\w+(.tiff|.tif)$", x) is not None, files)

## set process attr name 
## get process
n_stepgroup = root.find('process').find('stepgroup')
n_stepgroup.clear()

total_no = 0

for filename in files:
    print(filename)
    total_no += 1
    no = 1
    n_step = ET.SubElement(n_stepgroup, "step")         # gen new step
    n_no, n_name , n_status = getNewStep(n_step, total_no , no , "saving processed image into file")
    no += 1
    ### save processed image into file
    try:
        with WIMAGE(filename=filein + filename) as w_img:
            w_img.resize(width=int( w_img.width * scaled_rate ), height=int( w_img.height * scaled_rate) )
        # Set the optimization level through the linked resources of 
        # the image instance. (i.e. `wand.image.Image.wand`)
            library.MagickSetCompressionQuality(w_img.wand, 75)
            w_img.save(filename=fileout + filename)
        n_status.text = "saving image success"
    except:
        n_status.text = "saving image failed"
    
    n_step = ET.SubElement(n_stepgroup, "step")         # gen new step
    n_no, n_name , n_status = getNewStep(n_step, total_no , no , "loading processed image into list")
    no += 1
    ### load processed image.
    try:
        p_image = PIMAGE.open(fileout + filename , 'r')        # open PIF.Image object
        im1 = p_image.convert('RGB')                         # Image format
        if( index == 0):                                    # first Image
            p_img = im1
        else:
            img_list.append(im1)
        index = index + 1
        n_status.text = "filling in list success"
    except:
        n_status.text = "filling in list failed"
    
    
#p_img.save(fileout + 'output' + '.pdf', save_all=True, append_images=img_list )

### set end time
time = root.find('process').find('time')
time_end = time.find('end')
time_end.text = datetime.now().strftime("%H:%M:%S")

### set end time
time = root.find('process').find('time')
time_interval = time.find('internal')
time_interval.text = str( datetime.strptime(time_end.text , "%H:%M:%S") - datetime.strptime(time_start.text , "%H:%M:%S") )

## write xml content into record.xml
tree.write('record.xml')
        

