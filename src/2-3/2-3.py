# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 09:39:29 2022

@author: James
"""

import os
import re
from os.path import exists
from io import BytesIO
from datetime import datetime
import xml.etree.ElementTree as ET
import sys
sys.path.append('../../py_modules')

import pyvips
from wand.image import Image as WImage
from wand.color import Color
from PyPDF2.pdf import PdfFileReader , PdfFileWriter
from PyPDF2.utils import b_
from PyPDF2.merger import PdfFileMerger 
from PIL import Image as PImage
from reportlab.pdfgen.canvas import Canvas


## init constant 
filein = "../../tif/"
fileout = "./output/"
jpgin = "./jpg_path/"
jpgout = "./jpg_path/"

#metadata = {
#    u'/Version': 'PDF-1.7'
#}

metadata = {
    '/Title': 'Jorge\'s Grade',
    '/Subject': 'Jorge\'s updated performance report',
    '/Author': 'Jorge'
}

## get XML root 
tree = ET.parse('record.xml')
root = tree.getroot()

### set start time
time = root.find('process').find('time')
time_start = time.find('start')
time_start.text = datetime.now().strftime("%H:%M:%S")

files = os.listdir(filein)

# Filter out non-desired files
files = filter(lambda x: re.match(r"^\w+(.tiff|.tif)$", x) is not None,
               files)

## function definition
def convToJpg(filename):
    with WImage(filename=filein + filename, resolution=150) as img:
        img.format = 'jpeg'                      # convert image format from tiff to jpg.
        img.save(filename=jpgout + filename[0:-4] + '.jpg')        # save file as jpg
    return

def getNewStep(n_step , total_no , no , name):
    n_step.set("No", str( total_no ))
    n_no = ET.SubElement(n_step, "sub_no")
    n_no.text = str( no )
    n_name = ET.SubElement(n_step, "description")
    n_name.text = name
    n_status = ET.SubElement(n_step, "status")
    return (n_no , n_name, n_status)

## set process attr name 
## get process
n_stepgroup = root.find('process').find('stepgroup')
n_stepgroup.clear()

writer = PdfFileWriter()

img_list = []
index = 0
total_no = 0
for filename in files:
    print(filename)
    total_no += 1   
    no = 1
    n_step = ET.SubElement(n_stepgroup, "step")         # gen new step
    n_no, n_name , n_status = getNewStep(n_step, total_no , no , "saving image into pdf")
    no += 1

    try:
        convToJpg(filename)
        image1 = PImage.open(jpgin + filename[0:-4] + '.jpg' , 'r')        # open PIF.Image object
        im1 = image1.convert('RGB')                         # Image format
        print(index)
        if( index == 0):                                    # first Image
            img = im1
            print(img)
        else:
            img_list.append(im1)
        index = index + 1
        n_status.text = "saving image success"
    except:
        n_status.text = "saving image failed"
        
img.save(jpgin + 'output' + '.pdf', save_all=True, append_images=img_list )

reader = PdfFileReader(open(jpgin + 'output.pdf', 'rb')) 
for page in reader.pages:
    writer.addPage(page)
writer.addMetadata(metadata)  
writer._header = writer._header.replace(writer._header,b_("PDF-1.4")) 
output = open(fileout + 'NewGrades.pdf','wb') 
writer.write(output) 
output.close() 
#._header.replace(b_("PDF-1.3"),b_("PDF-1.5"))

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


