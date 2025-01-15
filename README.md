# OCR-Manifest

A package to perform OCR on the pages in a IIIF Manifest.

**ocr-manifest~** is a Python package that provides a script,
ocr-manifest, to download OCR files from a Manifest URI and write them
to a specified directory.

## Installation

To install the ocr-manifest package, ensure you have uv installed to
manage your project dependencies. Then, follow these steps:

1.  Clone the repository or download the source code.

2.  Install the package and its dependencies using uv:

    ``` bash
    uv install
    ```

3.  Verify that the ocr-manifest script is installed and available in
    your PATH:

    ``` bash
    ocr-manifest --help
    ```

## Usage

The ocr-manifest script processes a Manifest URI and downloads the
corresponding OCR files to a specified directory.

### Syntax

``` bash
ocr-manifest <manifest_uri> <output_directory>
```

-   \<manifest~uri~\>: The URI of the Manifest to process.
-   \<output~directory~\>: The directory where OCR files will be
    written.

### Example

``` bash
ocr-manifest https://example.com/manifest.json output_files
```

After execution, all the OCR files will be available in the
output_files directory.
