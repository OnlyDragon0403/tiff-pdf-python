# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 03:24:01 2022

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
from PIL import Image as PIL_Image , ExifTags
import sys
sys.path.append('../../py_modules')

import pyexiv2
import pyvips
from wand.image import Image
from tifffile import tifffile
import numpy
        
## init constant 
filein = "../../tif/"
fileout = "./output/"
jpgin = "./jpg_path/"
jpgout = "./jpg_path/"

## variable 
page_rate = 5

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
def convToMultijpg(filename):
    img = pyvips.Image.new_from_file(filein + filename)
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
    
    """
    ### filename get metadata
    img = PIL_Image.open(filein + filename)
    img_exif = img.getexif()
    print(type(img_exif))
    # <class 'PIL.Image.Exif'>
    
    if img_exif is None:
        print('Sorry, image has no exif data.')
    else:
        for key, val in img_exif.items():
            if key in ExifTags.TAGS:
                print(f'{ExifTags.TAGS[key]}:{val}')
    """
    
    """
    with Image(filename=filein + filename) as image:
        for k, v in image.metadata.items():
            print("{}: {}".format(k, v))
    
        image.save(filename='copy.tif')
    """
    original_img = pyexiv2.Image(fileout + filename)
    metadata = original_img.read_exif()
    original_img.close()
    
    print(metadata)
    """
    new_img = pyexiv2.Image(fileout + filename)
    
    banned_list = [
        'Exif.Image.ImageWidth',
        'Exif.Image.ImageLength',
        'Exif.Image.BitsPerSample',
        'Exif.Image.Compression',
        'Exif.Image.XResolution',
        'Exif.Image.YResolution',
        'Exif.Image.ResolutionUnit'
    ]
    
    available_list = [
        'Exif.Image.Software',
        'Exif.Image.DateTime',
        'Exif.Image.Orientation',
        'Exif.Image.PhotometricInterpretation'
    ]
    
    for key , val in metadata.items():
        if key in available_list :
            print(key,val)
            new_img.modify_exif({key : val})
                    
    new_img.close()
    """
    
    
    """
    #exif = piexif.load(fileout + filename[0:-4] + ".tif")
    #print(piexif.ImageIFD().DateTime)
    #zeroth_ifd = exif["0th"][piexif.ImageIFD().Software].decode('utf-8').rstrip('\x00')
    #print(zeroth_ifd)
    
    exif_dict = {
        "0th":{},
        "Exif":{},
        "GPS":{},
        "Interop":{},
        "1st":{},
        "thumbnail":None
    }
    
    #try:
    exif_dict = piexif.load(filein + filename)
    exif_dict["0th"][piexif.ImageIFD.DateTime]=datetime.utcnow().strftime("%Y:%m:%d %H:%M:%S")
    exif_bytes = piexif.dump(exif_dict)
    with  assertRaises(ValueError):
            piexif.insert(exif_bytes, filename + filename)
    """
    except (ValueError, piexif.InvalidImageDataError):
        print(ValueError)
    """
    """

        
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