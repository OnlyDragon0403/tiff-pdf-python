# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 09:39:29 2022

@author: James
"""
"""
convert tiff to jpg project.
"""

import os
import re
from os.path import exists
from datetime import datetime
import xml.etree.ElementTree as ET
import sys
sys.path.append('../../py_modules')

from wand.image import Image
from wand.color import Color

## init constant 
filein = "../../tif/"
fileout = "./output/"
jpgin = "./jpg_path/"
jpgout = "./jpg_path/"

## get XML root 
tree = ET.parse('record.xml')
root = tree.getroot()

### set start time
time = root.find('process').find('time')
time_start = time.find('start')
time_start.text = datetime.now().strftime("%H:%M:%S")

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

files = os.listdir(filein)

# Filter out non-desired files
files = filter(lambda x: re.match(r"^\w+(.tiff|.tif)$", x) is not None,
               files)
total_no = 0

for filename in files:
    print(filename)
    total_no += 1
    no = 1
    n_step = ET.SubElement(n_stepgroup, "step")         # gen new step
    n_no, n_name , n_status = getNewStep(n_step, total_no , no , "converting tiff to grayscale image")
    no += 1
    try:
        with Image(filename=filein + filename, resolution=150) as img:
            img.type = 'grayscale';                 # convert image to grayscale color
            #img.type = 'truecolor';                 # convert image to true color
            img.format = 'jpeg'                      # convert image format from tiff to jpg.
            img.save(filename=fileout + filename[0:-4] + '.jpg')        # save file as jpg
        n_status.text = "convertion success"
    except:
        n_status.text = "convertion failed"

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
