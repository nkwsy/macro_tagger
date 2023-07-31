from pymongo import MongoClient
from PIL import Image, ExifTags
from os.path import isfile, join
from os import listdir, environ
from dotenv import load_dotenv
import os
import time
from datetime import datetime

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(environ.get("MONGO_HOST"))
db = client[environ.get("DATABASE_NAME")]
collection = db[environ.get("COLLECTION_NAME")]

# Specify the folder
folder = environ.get("MACRO_IMAGES_FOLDER")


# Function to get the images from the given folder
def get_images(folder):
    return [f for f in listdir(folder) if isfile(join(folder, f))]

# Function to get the image metadata
def get_metadata(folder, image):
    path = os.path.join(folder, image)
    img = Image.open(path)
    modification_time = os.path.getmtime(path)

    # Initialize default metadata
    metadata = {
        "filename": image,
        "folder": os.path.basename(folder),
        "file_type": os.path.splitext(image)[1][1:],
        "file_size": os.stat(path).st_size,
        "dimensions": f"{img.width}x{img.height}",
        "modification_date": datetime.fromtimestamp(modification_time),
        "creation_date": ""
    }

    if img._getexif() is not None:
        for tag, value in img._getexif().items():
            if ExifTags.TAGS.get(tag) == 'DateTimeOriginal':
                metadata["creation_date"] = value
            # else make datetime from modification_time if it's the same as folder name
            elif metadata["folder"] == time.strftime("%y%m%d", time.localtime(modification_time)):
                metadata["creation_date"] = datetime.fromtimestamp(modification_time)
            # else make datetime from folder name
            else:
                metadata["creation_date"] = datetime.strptime(metadata["folder"], "%y%m%d")
    return metadata


def import_images(folder):
# Get the images from the folder
    images = get_images(folder)

    # Get and store the metadata for each image
    for image in images:
        metadata = get_metadata(folder, image)
        collection.insert_one(metadata)
