import os
import pathlib
import random
import string
import sys
import threading
import time
import requests
import shutil

work_dir = os.getcwd()


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


temp_id = id_generator()
temp_dir = os.path.join(work_dir, temp_id)
print(f"temp_dir : {temp_dir}")

if not os.path.exists(temp_dir):
    os.mkdir(temp_dir)


def savefile(file_url, file_name, event):
    # 配置headers防止被墙，一般问题不大
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    }

    r = requests.get(file_url, headers=headers)

    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(r.content)
    else:
        print(f"[failed] {file_name}")
    # set the event
    event.set()


# 这个是源m3u8文件，不带hls
url_m3u8 = 'https://****.m3u8'

r = requests.get(url_m3u8)
r.encoding = 'utf-8'
# print(r.text)

last_part = url_m3u8.split('/')[-1]
header_part = url_m3u8.replace(last_part, "")

file_name = temp_id + ".txt"
f = open(temp_dir + "/" + file_name, "a")
f.writelines(r.text)
f.close()

with open(temp_dir + "/" + file_name, "r") as f:
    all_lines = f.readlines()

# 去掉前面没用的信息
ts_list = []
count = 0
for line in all_lines:
    if "#" not in line:
        ts_list.append(line.strip('\n'))

total = len(ts_list)
event = threading.Event()

for ts in ts_list:
    file_name = ts.split('-')[-1]
    # print(f"downloading : {file_name} {ts_list.index(ts)}/{total}")
    # save file
    ts_url = header_part + ts
    ts_file_name = temp_dir + "/" + file_name
    thread = threading.Thread(target=savefile, args=(ts_url, ts_file_name, event,))
    # print(ts_url)
    # print(ts_file_name)
    if threading.active_count() <= 10:  # block
        thread.start()
    else:
        # wait for the event to be set
        # print(f"thread {ts_list.index(ts)} wait")
        event.wait()
        # get the result from the new thread
        thread.start()
        event.clear()
        percentage = round((ts_list.index(ts) + 1) / total, 4) * 100
        sys.stdout.write('\rDownloading %.2f percent ' % (percentage))
        sys.stdout.flush()
        time.sleep(0.1)

# Wait for all of them to finish
for x in threading.enumerate():
    if x.name.startswith("Thread-"):
        # print(x.name)
        x.join()

file_list = [file.__str__() for file in list(pathlib.Path(temp_dir).glob('*.ts'))]
# join file name together
file_list.sort()
filepath_cat = ' '.join(file_list)
cmd_str = 'cat ' + filepath_cat + ' > ' + temp_id + '.ts'
# print(cmd_str)
# cat 1.ts 2.ts > combine.ts
os.system(cmd_str)

# delete temp dir
shutil.rmtree(temp_dir, ignore_errors=True)
print("\nDeleted '%s' directory successfully" % temp_dir)
