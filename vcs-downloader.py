import sys
import urllib.request
import ssl
from joblib import Parallel, delayed
import subprocess
import os

ts_list = list()
context = ssl._create_unverified_context()
phpSessId = "abjkl556"
prefix = ""


def download_part(file):
    context = ssl._create_unverified_context()
    url = prefix + "/" + file
    try:
        with open(file, "wb") as ts_file:
            request = urllib.request.Request(url)
            # Add login Cookie
            if (phpSessId):
                request.add_header("Cookie", "PHPSESSID=" + phpSessId)
            response = urllib.request.urlopen(request, context=context)
            ts_file.write(response.read())
    except urllib.error.HTTPError as e:
        print('HTTP Error at', url, '| Code:', e.code)
    return


if (len(sys.argv) > 1 and sys.argv[1]):
    downloadUrl = sys.argv[1]
else:
    downloadUrl = input("Please enter the Download URL of m3u file: ")

print("Parsing your link...")
prefix = downloadUrl.rsplit("/", 1)[0]

with open("playlist.m3u", 'wb') as m3u_file:
    try:
        request = urllib.request.Request(downloadUrl)
        request.add_header("Cookie", "PHPSESSID=" + phpSessId)
        response = urllib.request.urlopen(request, context=context)
        m3u_file.write(response.read())
    except urllib.error.HTTPError as e:
        print('HTTP Error at', downloadUrl, '| Code:', e.code)

with open("playlist.m3u", 'r') as m3u_file:
    line = m3u_file.readline().rstrip()
    while line:
        if line.endswith(".ts"):
            ts_list.append(line)
        line = m3u_file.readline().rstrip()

print(f"File consists of {len(ts_list)} parts.\n")

if (len(sys.argv) > 2 and sys.argv[2]):
    filename = sys.argv[2]
else:
    filename = input("Output name: ")

print("Starting download. Might take some time...")
Parallel(n_jobs=16)(delayed(download_part)(file) for file in ts_list)

with open("ts_file.txt", "w", encoding='utf-8') as ts_file:
    for line in ts_list:
        ts_file.write(f"file {line}\n")

ffmpeg = ["ffmpeg", "-f", "concat", "-vaapi_device", "/dev/dri/renderD128", "-i", "ts_file.txt", "-vf", 'format=nv12,hwupload', "-map", "0", "-c:a", "copy", "-c:v", "hevc_vaapi", "-crf", "25", "-preset", "slow", filename]
subprocess.run(ffmpeg)

# clean up
dir_list = os.listdir(".")
for file in dir_list:
    if file.endswith(".ts"):
        os.remove(file)
