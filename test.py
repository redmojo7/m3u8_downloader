import os
import threading
import time
import urllib.parse as urlparse
import pathlib

import requests

url_m3u8 = 'https://vodaliyun.kyfsj.com/a27e93f8180749108eb7f2e8f6c9b25f/086f81be6a2946d6ac72c3a40b9872a1-9c2b98dcba470d4a5fcb0bf71f3e0d8d-od-S00000001-100000.m3u8'

last_part = url_m3u8.split('/')[-1]
header_part = url_m3u8.replace(last_part, "")
print(header_part)

parsed_uri = urlparse.urlparse(url_m3u8)
result = "{uri.scheme}://{uri.netloc}/".format(uri=parsed_uri)
print(parsed_uri.path.split('/')[1])
print(result)


def running(index, event):
    print(f"thread-{index} start")
    time.sleep(4)
    print(f"thread-{index} finished")
    # set the event
    event.set()


event = threading.Event()
for i in range(20):
    thread = threading.Thread(target=running, args=(i, event,))
    if threading.active_count() <= 10:  # block
        thread.start()
    else:
        # wait for the event to be set
        print(f"thread {i} wait")
        event.wait()
        # get the result from the new thread
        thread.start()
        event.clear()
'''
headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    }
file_url = "https://vodaliyun.kyfsj.com/a27e93f8180749108eb7f2e8f6c9b25f/086f81be6a2946d6ac72c3a40b9872a1-8c38d79ff57f6d82e465b93566486667-od-S00000001-100000-00447.ts"
file_name = "temp.ts"
r = requests.get(file_url, headers=headers)

if r.status_code == 200:
    with open(file_name, 'wb') as f:
        f.write(r.content)
'''

# Wait for all of them to finish
print(threading.enumerate())
for x in threading.enumerate():
    if x.name.startswith("Thread-"):
        print(x.name)
        x.join()

ss = '086f81be6a2946d6ac72c3a40b9872a1-8c38d79ff57f6d82e465b93566486667-od-S00000001-100000-00001.ts\n'
print(ss)
ss = ss.strip('\n')
print(ss)


file_list = [file.__str__() for file in list(pathlib.Path("./8CXURR").glob('*.ts'))]
# join file name together
file_list.sort()
filepath_cat = ' '.join(file_list)
print(filepath_cat)
cmd_str = 'cat ' + filepath_cat + '> ./8CXURR/8CXURR.ts'
print(cmd_str)
# cat 1.ts 2.ts > combine.ts
os.system(cmd_str)
