import subprocess
import tarfile
import zipfile


def get_archive_type(file_path):
    """
    Returns the type of archive passed to file_path
    :param file_path: string
        The path of the archive
    :return: string
        Returns either: "gz", "bz2", "zip", "7z", "tar"
    """
    file_type = None
    magic_dict = {
        b"\x1f\x8b\x08": "gz",
        b"\x42\x5a\x68": "bz2",
        b"\x50\x4b\x03\x04": "zip",
        b"\x37\x7A\xBC\xAF\x27\x1C": "7z"
    }
    max_len = max(len(x) for x in magic_dict)

    if tarfile.is_tarfile(file_path):
        return "tar"

    with open(file_path, "rb") as f:
        file_start = f.read(max_len)
        for magic, filetype in magic_dict.items():
            if file_start.startswith(magic):
                file_type = filetype

    return file_type


def extract_7_zip(file_path, destination_path):
    command = ['7za', 'x', file_path, '-o' + destination_path, '-aoa']

    print("Extracting {} to {} ...".format(file_path, destination_path))
    subprocess.run(command)
    print("Extraction finished")


def extract_tar(file_path, destination_path):
    print("Extracting {} to {} ...".format(file_path, destination_path))
    with tarfile.open(file_path) as tar:
        
        import os
        
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar, path=destination_path)
    print("Extraction finished")


def extract_zip(file_path, destination_path):
    print("Extracting {} to {} ...".format(file_path, destination_path))
    with zipfile.ZipFile(file_path) as archive:
        archive.extractall(path=destination_path)
    print("Extraction finished")
