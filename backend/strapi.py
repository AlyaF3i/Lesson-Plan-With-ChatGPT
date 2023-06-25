import requests
from config import STRAPI_END_POINT
import sys

create_url = STRAPI_END_POINT
# Define the path to the PDF file
def send_dict_to_strapi(pdf_path):
    if STRAPI_END_POINT == "" or STRAPI_END_POINT is None:
        print("Strapi url is not define", file=sys.err)
        return False
    with open(pdf_path, "rb") as file:
        pdf_data = file.read()

    payload = {
        "files": {
            "file": pdf_data
        }
    }

    response = requests.post(STRAPI_END_POINT, files=payload)

    # Check the response status
    if response.status_code == 200:
        print("PDF file uploaded successfully!")
    else:
        print("Failed to upload the PDF file.")

    return True

# Define the Strapi API endpoint for creating a new entry

def send_dict_to_strapi(data):
    if STRAPI_END_POINT == "" or STRAPI_END_POINT is None:
        print("Strapi url is not define", file=sys.err)
    response = requests.post(STRAPI_END_POINT, json=data)

    # Check the response status
    if response.status_code == 200:
        print("New entry created successfully!")
    else:
        print("Failed to create a new entry.")

    return True