#import all the necessary libraries
import cv2
import numpy as np
from PIL import Image, ImageDraw
import pytesseract
import matplotlib.pyplot as plt
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response,FileResponse
import collections

from pyramid.renderers import render_to_response
from datetime import datetime
import mysql.connector as mysql
from dotenv import load_dotenv
import os
import json

load_dotenv()
 
''' Environment Variables '''
db_host = os.environ['MYSQL_HOST']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_name = os.environ['MYSQL_DATABASE']


# JSON which maps photos to ID
plate_photos = [
 {"id":1, "img_src": "Arizona_47.jpg"},
 {"id":2, "img_src": "Contrast.jpg"},
 {"id":3, "img_src": "Delaware_Plate.png"},
]

# function to access data
def get_photo(req):
   # post_id retrieves the value that is sent by the client
   # the -1 is needed because arrays are 0-indexed
   idx = int(req.matchdict['photo_id'])-1
   # we return the value at the given index from plate_photos
   return plate_photos[idx]

# function to return the html page to the client when the user visits the page
def index_page(req):
   return FileResponse("Lab7/Challenges/index.html")

# function to detect the number plate in the image 
# Params: img (input image, NumPy array)
# Returns: roi (cropped section containing the plate, NumPy array) 
#          coord (center of the roi image, NumPy array) 
def detect_plate(img):
    # PART 1: process the image to remove artifacts and stray edges 
    blur = cv2.GaussianBlur(img.copy(), (9, 9), 1)   # Add a Gaussian Blur to smoothen the noise
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]  # Threshold the image to get a binary image

    # PART 2: look for all the contours
    # Get contours: some images might work better with the cv2.RETR_TREE / cv2.RETR_EXTERNAL options
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]    # Find the largest 30 contours

    location = None  # Find best polygon and get location

    # Finds rectangular contour
    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02*peri, True) 
        if len(approx) >= 4:
            if int(np.max(approx)) == img.shape[1] - 1:
                location = approx
                
            else: 
                location = approx
                break            

    # Handle cases when no quadrilaterals are found        
    if type(location) != type(None):
        print("Corners of the plate are: ",location)
    else: 
        arr = np.array([ [-1, -1], [-1, -1], [-1, -1], [-1, -1] ])
        print("No plate found")
        print(arr)

    # PART 3: find cropped image focused on the number plate(roi) and the center (coord)
    roi = None
    coord = None

    if type(location) != type(None):
        #find maximum value along axis=0 (for the columns)
        amax_value = np.amax(location, axis=0)
        maxx = amax_value[0][0]
        maxy = amax_value[0][1]

        #find minimum value along axis=0 (for the columns)
        amin_value = np.amin(location, axis=0)
        print(amin_value)
        minx = amin_value[0][0]
        miny = amin_value[0][1]

        # the resulting image
        roi = img[miny:maxy, minx:maxx]

        # find the center
        centerx = (maxx-minx)/2
        centery = (maxy-miny)/2
        coord = (centerx, centery)
        coord = np.array(coord) # convert tuple to array

    # PART 4: return outputs
    return roi, coord

# function that uses pytesseract to get text from the image
# Params: img (cropped section containing the plate, NumPy array)
# Returns: text (text extracted by the pytesseract library, string)
def get_text(req):
    # read in image
    idx = int(req.matchdict['photo_id'])-1
    spec = plate_photos[idx]
    img = cv2.imread("Lab7/Challenges/public/" + spec["img_src"], cv2.IMREAD_GRAYSCALE) # Default condition or 1 --> RGB
    roi, __ = detect_plate(img)
    text = pytesseract.image_to_string(roi, config='--psm 11')

    # insert data into SQL table
    db = mysql.connect(host=db_host, database=db_name, user=db_user, passwd=db_pass)
    cursor = db.cursor()
    insert_stmt = ("INSERT INTO PlateData (created_at, image_name, text_detected) VALUES (%s, %s, %s);")
    data = (datetime.now(), spec["img_src"], text)
    cursor.execute(insert_stmt, data)
    db.commit()

    return text

# retrieve SQL rows
def get_datarows(req):
  data = json.loads(req.body.decode("utf-8"))
  input = str(data["rows"]) # gets input : 1,2,3
  a = 'just added'
  b = 'last 3'
  c = 'last 5'
  db = mysql.connect(host=db_host, database=db_name, user=db_user, passwd=db_pass)
  cursor = db.cursor()
  if (input == a):
        cursor.execute("SELECT * FROM PlateData ORDER BY id DESC LIMIT 1;" )
        record = cursor.fetchall()
        db.close()
        if record is None:
            return {
                'error': "No data was found for the given ID",
            }

        objects_list = []
        for row in record:
            d = collections.OrderedDict()
            d["id"] = str(row[0])
            d["datetime"] = str(row[1])
            d["image_name"] =str(row[2])
            d["text_detected"] = str(row[3])
            objects_list.append(d)
        response = json.dumps(objects_list)
        return response
  elif input == b:
        cursor.execute("SELECT * FROM PlateData ORDER BY id DESC LIMIT 3;" )
        record = cursor.fetchall()
        db.close()
        if record is None:
            return {
                'error': "No data was found for the given ID",
            }
        objects_list = []
        for row in record:
            d = collections.OrderedDict()
            d["id"] = str(row[0])
            d["datetime"] = str(row[1])
            d["image_name"] =str(row[2])
            d["text_detected"] = str(row[3])
            objects_list.append(d)
        response = json.dumps(objects_list)
        
        return response
  elif input == c:
        cursor.execute("SELECT * FROM PlateData ORDER BY id DESC LIMIT 5;" )
        record = cursor.fetchall()
        db.close()
        if record is None:
            return {
                'error': "No data was found for the given ID",
            }
        objects_list = []
        for row in record:
            d = collections.OrderedDict()
            d["id"] = str(row[0])
            d["datetime"] = str(row[1])
            d["image_name"] =str(row[2])
            d["text_detected"] = str(row[3])
            objects_list.append(d)
        response = json.dumps(objects_list)
        return response


# Main entrypoint
if __name__ == '__main__':
   with Configurator() as config:
       # to use jinja
       config.include('pyramid_jinja2')
       config.add_jinja2_renderer('.html')

       # add routes
       config.add_route('home', '/')
       config.add_view(index_page, route_name='home')
      
       config.add_route('photos', '/photos/{photo_id}')
       config.add_view(get_photo, route_name='photos', renderer='json')
 
       config.add_route('plate', '/plate/{photo_id}')
       config.add_view(get_text, route_name='plate', renderer='json')

       config.add_route('datarows', '/datarows')
       config.add_view(get_datarows, route_name='datarows', renderer='json')

       # Add a static view
       # This command maps the folder “./public” to the URL “/”
       # So when a user requests geisel-1.jpg as img_src, the server knows to look
       # for it in: “public/geisel-1.jpg”
       config.add_static_view(name='/', path='./public', cache_max_age=3600)

       # Create an app with the configuration specified above
       app = config.make_wsgi_app()

   # This line is used to start serving on port 6543 on the localhost
   print("Server started on http://0.0.0.0:6565/")
   server = make_server('0.0.0.0', 6565, app) # Start the application on port 6543
   server.serve_forever()