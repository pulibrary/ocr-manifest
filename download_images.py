# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
import logging
from shutil import copyfileobj
from pathlib import Path
from collections import namedtuple
import argparse
import requests

log = logging.getLogger(__name__)

base_dir = Path("/tmp/images")

Image = namedtuple('Image', ['label', 'uri'])

def download_manifest(uri) -> dict | None:
    response = requests.get(uri)
    if response.status_code == 200:
        return response.json()


def image(canvas:dict) -> Image | None:
    renderings = canvas['rendering']
    label = canvas['label']
    tiff_renderings = [rendering for rendering in renderings
                       if rendering['format'] == 'image/tiff']
    uri = None
    if tiff_renderings:
        uri = tiff_renderings[0]['@id']
    return Image(label, uri=uri)


def tiff_images(manifest:dict) -> list:
    return [image(canvas) for canvas in manifest['sequences'][0]['canvases']]


def download_image(image:Image, target_dir:Path):
    if image.uri:
        try:
            response = requests.get(image.uri, stream=True)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
    
        response.raw.decode_content = True
        try:
            fname = target_dir / Path(f"{image.label}.tif")
            image_file = fname.open("wb")
            copyfileobj(response.raw, image_file)
            image_file.close()
        except OSError as e:
            log.exception(e)


def download_images(manifest_uri:dict, target_dir:Path):
    manifest = download_manifest(manifest_uri)
    if manifest:
        for tiff_image in tiff_images(manifest):
            download_image(tiff_image, target_dir)
            


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("uri", help="URI of the manifest")
    parser.add_argument("target_dir", help="directory in which to store image files")
    

    args = parser.parse_args()
    uri = args.uri
    target_dir = args.target_dir

    download_images(args.uri, Path(args.target_dir))

            
if __name__ == "__main__":
    main()
