# This project may break as the Kaggle website changes

To solve this issue I will move the project calls to the [official Kaggle API](https://github.com/Kaggle/kaggle-api) in the future.

# Kaggle-data-downloader
An unofficial Kaggle datasets downloader very much inspired by [kaggle-cli](https://github.com/floydwch/kaggle-cli)

## Installation

```
$ pip install -U kaggle_data
```

Depending on the format of your archive you may need to install some tools
on your computer.

 - For 7-zip archives: You need the `7za` program from p7zip. 
    - On macOS: `brew install p7zip`
    - On Ubuntu: `sudo apt-get install p7zip-full`

## Usage
Please note that accepting the competition rules before your commands is mandatory.

Usage example:
```
from kaggle_data.downloader import KaggleDataDownloader

destination_path = "input/"

downloader = KaggleDataDownloader("Ekami", "somePassword", "planet-understanding-the-amazon-from-space")
output_path = downloader.download_dataset("test-jpg-additional.tar.7z", destination_path)
downloader.decompress(output_path, destination_path)
downloader.decompress(destination_path + "test-jpg-additional.tar", destination_path)
```

## Packaging the project for Pypi deploy

```
pip install twine
pip install wheel
python setup.py sdist
python setup.py bdist_wheel
```

[Create a pypi account](https://packaging.python.org/tutorials/distributing-packages/#id76) and create `$HOME/.pypirc` with:
```
[pypi]
username = <username>
password = <password>
```

Then upload the packages with:
```
twine upload dist/*
```
