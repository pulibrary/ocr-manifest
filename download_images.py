# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
import logging
import tempfile
from shutil import copyfileobj
from pathlib import Path
from collections import namedtuple
import argparse
import requests
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


base_dir = Path("/tmp/images")

Image = namedtuple('Image', ['label', 'uri'])

def create_image_cache() -> tempfile.TemporaryDirectory:
    """Creates temporary directory for image files."""
    tmp_dir = tempfile.TemporaryDirectory()
    logging.info(f"Image cache created: {tmp_dir}")
    return tmp_dir


def manifest_from_uri(uri) -> dict:
    try:
        response = requests.get(uri)
        if response.status_code != 200:
            response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"{e}")
        


def tiff_from_canvas(canvas:dict) -> Image:
    renderings = canvas['rendering']
    label = canvas['label']
    tiff_renderings = [rendering for rendering in renderings
                       if rendering['format'] == 'image/tiff']

    try:
        uri = tiff_renderings[0]['@id']
        return Image(label, uri)
    
    except IndexError as e:
        raise IndexError(f"No tiffs: {e}")



def tiff_images(manifest:dict) -> list:
    return [tiff_from_canvas(canvas) for canvas in
            manifest['sequences'][0]['canvases']]


def download_image(image:Image, target_dir) -> Path | None:
    if image.uri:
        fname = Path(f"{image.label}.tif")
        logging.info(f"Downloading {image.uri} as {fname}")
        try:
            response = requests.get(image.uri, stream=True)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.info("Download failed.")
            raise SystemExit(e)
    
        response.raw.decode_content = True
        try:
            image_path = target_dir / fname
            image_file = image_path.open("wb")
            copyfileobj(response.raw, image_file)
            image_file.close()
            logging.info(f"Downloaded {fname}.")
            return image_path
        except OSError as e:
            logging.exception(f"An OSError occured: {e}")


def download_images(manifest_uri:dict, target_dir:Path):
    manifest = manifest_from_uri(manifest_uri)
    if manifest:
        for tiff_image in tiff_images(manifest):
            download_image(tiff_image, target_dir)
            

def ocr_images(manifest_uri:dict, target_dir:Path):
    manifest = manifest_from_uri(manifest_uri)
    for tiff_image in tiff_images(manifest):
        img_path = download_image(tiff_image, Path("/tmp"))
        ocr_image(img_path, target_dir)



def ocr_image(image_path, target_dir):
    
    outfile = f"{target_dir}/{image_path.stem}.txt"
    command = [
        "kraken",
        "-i",
        image_path,
        outfile,
        "segment",
        "-bl",
        "ocr",
        "-m",
        "catmus-print-fondue-large.mlmodel"
    ]
    
    try:
        logging.info(f"Beginning OCR of {image_path}")
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        logging.info("OCR complete.")
    except subprocess.CalledProcessError as e:
        print(e.stderr)

    
            
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("uri", help="URI of the manifest")
    parser.add_argument("target_dir", help="directory in which to store image files")
    

    args = parser.parse_args()
    uri = args.uri
    target_dir = args.target_dir

    image_cache = create_image_cache()

    try:
        manifest = manifest_from_uri(uri)
        tiff_uris = tiff_images(manifest)
        for tiff in tiff_uris:
            tiff_file_path = download_image(tiff, image_cache.name)
            ocr_image(tiff_file_path, target_dir)

    finally:
        image_cache.cleanup()
        logging.info("Image cache cleaned up.")


            
if __name__ == "__main__":
    main()
