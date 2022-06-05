# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 15:14:01 2022

@author: James
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 16:00:42 2022

@author: James
"""

import os
import re
from datetime import datetime
import xml.etree.ElementTree as ET
import sys
sys.path.append('../../py_modules')

import tifftools
import piexif
import pyvips
from wand.image import Image as WImage
from PIL import Image as PImage
from tifffile import tifffile
from libtiff import TIFF
import numpy
        
## init constant 
filein = "../../tif/"
fileout = "./output/"
jpgin = "./jpg_path/"
jpgout = "./jpg_path/"

## variable 
page_rate = 5

###  Image metadata

available_list = [
    piexif.ImageIFD().DateTime,
    piexif.ImageIFD().Software,
    piexif.ImageIFD().Orientation,
    piexif.ImageIFD().PhotometricInterpretation
]


## get XML root 
tree = ET.parse('record.xml')
root = tree.getroot()

### set start time
time = root.find('process').find('time')
time_start = time.find('start')
time_start.text = datetime.now().strftime("%H:%M:%S")


## get input image
files = os.listdir(filein)

# Filter out non-desired files
files = filter(lambda x: re.match(r"^[\w\W]+(.tiff|.tif|.png|.jpg)$", x) is not None,
               files)

## function definition
def convToMultiJPGToTIF(filename):
    with WImage(filename=filein + filename, resolution=150) as img:
        img.format = 'jpeg'                      # convert image format from tiff to jpg.
        img.save(filename=jpgout + filename[0:-4] + '.jpg')        # save file as jpg
    
    img = pyvips.Image.new_from_file(jpgout + filename[0:-4] + '.jpg')
    #img.write_to_file(jpgout + filename[0:-4] + '.jpg')
    width_list = [128,256,512,1024, img.width]
    for index in range( page_rate ):
        #sub_img = pyvips.Image.new_from_file(jpgout + filename[0:-4] + '.jpg')
        sub_img = img.thumbnail_image(width_list[index])
        sub_img.write_to_file(jpgout + filename[0:-4] + str(index) + '.tif')
        
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


index = 0
total_no = 0
# load file list in specific folder
for filename in files:
    print(filename)
    total_no += 1
    no = 1
    n_step = ET.SubElement(n_stepgroup, "step")         # gen new step
    n_no, n_name , n_status = getNewStep(n_step, total_no , no , "converting tiff to tif with multi resolution")
    no += 1
    
    # load metadata

    
    
    # convert image format from tiff to jpg and save file as jpg
    try:
        convToMultiJPGToTIF(filename)
        
        with tifffile.TiffWriter(jpgout + filename[0:-4] + ".tif") as tif:        #, bigtiff=True
            for i in range(page_rate):
                data = tifffile.imread(jpgin + filename[0:-4] + str(i) + '.tif')
                tif.save(data, photometric='rgb', compression='jpeg', description=filename)
        n_status.text = "multi-resolution success"
    except:
        n_status.text = "multi-resolution failed"
    
    
    """
    tag_list = [
        tifftools.Tag.Artist.value,
        tifftools.Tag.Software.value,
        tifftools.Tag.DateTime.value,
        tifftools.Tag.Copyright.value
        #tifftools.Tag.SubjectDistance.value,
        #tifftools.Tag.SubjectArea.value,
        #tifftools.Tag.SubjectLocation.value,
        #tifftools.Tag.SubjectDistanceRange.value
    ]
    
    original_info = tifftools.read_tiff(filein + filename)
    
    
    medium_info = tifftools.read_tiff(jpgout + filename)
    
    for tag_ID in tag_list:
        if tag_ID in original_info['ifds'][0]['tags'].keys():
            medium_info['ifds'][0]['tags'][tag_ID] = original_info['ifds'][0]['tags'][tag_ID]
    
    medium_info['ifds'][0]['tags'][tifftools.Tag.ImageDescription.value] = {
        'data': '',
        'datatype': tifftools.Datatype.ASCII
    }
    
    
    tifftools.write_tiff(medium_info, fileout + filename, allowExisting=True)
    """
    """
    p_medium_open = PImage.open(filein + filename)
    p_medium_open.tag[50735] = 100
    p_medium_open.save(fileout + filename, tiffinfo=p_medium_open.tag)
    """
    tif = TIFF.open( filein + filename )
    tif.SetField("GDAL_NODATA", str('1111'))
    
        
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