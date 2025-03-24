import requests
from PIL import Image
import os

def download_file(file_id, dest):
    """Downloads a file from Google Drive."""
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(URL, params={'id': file_id}, stream=True)
    token = next((v for k, v in response.cookies.items() if k.startswith('download_warning')), None)
    if token:
        response = session.get(URL, params={'id': file_id, 'confirm': token}, stream=True)
    with open(dest, "wb") as f:
        for chunk in response.iter_content(32768):
            f.write(chunk)

def rotate_images(files):
    """Rotates images 90° counterclockwise."""
    for name, file in files.items():
        try:
            Image.open(file).rotate(90, expand=True).save(file)
            print(f"Rotated and saved: {file}")
        except Exception as e:
            print(f"Error with {name}: {e}")

if __name__ == "__main__":
    os.makedirs("viz", exist_ok=True)
    images = {
        "guide": "1_OE1OCuz9N3modIa5zCZrSxA8mfhHP7e",
        "concierge": "13OUxRQxhHulnnMRkna794q7v54C0O4aF"
    }

    for name, file_id in images.items():
        path = f"viz/{name}.jpg"
        download_file(file_id, path)
        print(f"Downloaded: {path}")

    rotate_images({name: f"viz/{name}.jpg" for name in images})
