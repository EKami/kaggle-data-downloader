import os
import sys

sys.path.append('../kaggle_data')
from kaggle_data.downloader import KaggleDataDownloader


class TestKaggleDataDownloader:
    """
    Use with pytest -q -s tests.py
    """

    def test_download_data(self):
        competition_name = "planet-understanding-the-amazon-from-space"
        dataset_name = "test-jpg-additional.tar.7z"
        destination_path = "input/"

        downloader = KaggleDataDownloader(os.getenv("KAGGLE_USER"), os.getenv("KAGGLE_PASSWD"), competition_name)
        output_path = downloader.download_dataset(dataset_name, destination_path)
        downloader.uncompress(output_path, destination_path)
        downloader.uncompress(destination_path + "test-jpg-additional.tar", destination_path)
