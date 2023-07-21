#from sys import platform
import platform
import requests
import os
import zipfile
from shutil import rmtree

def _overwriting_extract_archive(zippath, outpath): 
    if os.path.exists(outpath) == True:
        rmtree(outpath)
    os.mkdir(outpath)
    with zipfile.ZipFile(zippath, mode='r') as file:
        file.extractall(outpath)
    
def _set_permission(executable_dir):
    for root, dirs, files in os.walk(executable_dir, topdown=False):
        for name in files:
            os.chmod(os.path.join(root, name), 0o0777)
        for name in dirs:
            os.chmod(os.path.join(root, name), 0o0777)


def _download_and_extract(link,downloaded_file_name,executable_dir):
    r = requests.get(link, allow_redirects=True)
    open(downloaded_file_name, 'wb').write(r.content)
    print(f"Downloaded Unity Build")
    _overwriting_extract_archive(downloaded_file_name, executable_dir)
    print("Unzipped Download")
    os.remove(downloaded_file_name)
    _set_permission(executable_dir)
    print("Set permissions to 777")

def download(downloaded_file_name : str = "solution.zip", executable_dir :str = "./EMR_Executable"):

    if (platform.system() == 'Darwin'):
        print("Downloading executable for mac")
        link = "https://www.mn.uio.no/ifi/english/research/groups/robin/events/Tutorials/Tutorial%20-%20Artificial%20Life%20-%202023/unity-builds/macos_evolving_modular_robots_v001.zip" 
        _download_and_extract(link,downloaded_file_name, executable_dir)
        
    elif (platform.system() == 'Linux'):
        print("Downloading executable for linux")
        link = "https://www.mn.uio.no/ifi/english/research/groups/robin/events/Tutorials/Tutorial%20-%20Artificial%20Life%20-%202023/unity-builds/linux_evolving_modular_robots_v001.zip" 
        _download_and_extract(link,downloaded_file_name, executable_dir)
    elif (platform.system() == 'Windows'):
        print("Downloading executable for windows")
        link = "https://www.mn.uio.no/ifi/english/research/groups/robin/events/Tutorials/Tutorial%20-%20Artificial%20Life%20-%202023/unity-builds/windows_evolving_modular_robots_v001.zip" 
        _download_and_extract(link,downloaded_file_name, executable_dir)

    print("Finished download EMR executable build")

if __name__ =="__main__":
    download()
    