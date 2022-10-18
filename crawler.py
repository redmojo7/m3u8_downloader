import os
import pathlib
import random
import string
import sys
import threading
import time
import requests
import shutil


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class M3U8Downloader:
    """M3U8 Downloader Class"""
    work_dir = os.getcwd()
    # all ts in m3u8 file
    playlists = []

    def __init__(self, url):
        """Initialize a M3U8 Downloader."""
        self.url = url
        self.url_last_part = url.split('/')[-1]
        self.url_front_part = url.replace(self.url_last_part, "")
        self.temp_id = id_generator()
        self.temp_dir = os.path.join(self.work_dir, self.temp_id)
        self.m3u8_file_path = os.path.join(self.temp_dir, self.temp_id + ".txt")
        # create an event
        self.thread_event = threading.Event()
        # create temp dir
        print(f"temp_dir : {self.temp_dir}")
        if not os.path.exists(self.temp_dir):
            os.mkdir(self.temp_dir)

    def save_ts_file(self, file_url, file_name):
        # mock up headers
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
        }
        response = requests.get(file_url, headers=headers)
        if response.status_code == 200:
            with open(file_name, 'wb') as ts_file:
                ts_file.write(response.content)
        else:
            print(f"[Error] failed to download {file_name}. response code : {response.status_code}")
        # set the event
        self.thread_event.set()

    def download_all_ts(self):
        """ Download all ts with multiple thread """
        total = len(self.playlists)
        for ts in self.playlists:
            index = self.playlists.index(ts)
            ts_file_name = ts.split('-')[-1]
            # save ts file
            ts_url = self.url_front_part + ts
            ts_file_path = os.path.join(self.temp_dir, ts_file_name)
            # create a thread to download it
            thread = threading.Thread(name='Worker-' + str(index), target=self.save_ts_file,
                                      args=(ts_url, ts_file_path,))
            # just run 10 threads at one time
            if threading.active_count() <= 10:  # block
                thread.start()
            else:
                # wait for the event to be set
                self.thread_event.wait()
                thread.start()
                self.thread_event.clear()
                # show the process of downloading
                percentage = round((index + 1) / total, 4) * 100
                sys.stdout.write('\rDownloading %.2f percent ' % percentage)
                sys.stdout.flush()
                time.sleep(0.1)

    def merge_ts(self):
        # Wait for all of them to finish
        for x in threading.enumerate():
            if x.name.startswith("Worker-"):
                x.join()

        file_list = [file.__str__() for file in list(pathlib.Path(self.temp_dir).glob('*.ts'))]
        # join file name together
        file_list.sort()
        filepath_cat = ' '.join(file_list)
        cmd_str = 'cat ' + filepath_cat + ' > ' + self.temp_id + '.ts'
        # cat 1.ts 2.ts > combine.ts
        os.system(cmd_str)
        print("\nSave '%s.ts' successfully" % self.temp_id)

        # delete temp dir
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        print("Deleted '%s' directory successfully" % self.temp_dir)

    def download(self):
        # send request to get m3u8 file
        res = requests.get(self.url)
        res.encoding = 'utf-8'
        if res.status_code == 200:
            print(f"Downloaded {self.url}")
            # save response as txt
            f = open(self.m3u8_file_path, "a")
            f.writelines(res.text)
            f.close()
            print(f"Save m3u8 file at : {self.m3u8_file_path}")
            #
            self.load_all_ts_url()
            self.download_all_ts()
            self.merge_ts()
        else:
            print(f"[Error] When downloading {self.url}")

    def load_all_ts_url(self):
        # open m3u8 file
        all_lines = []
        with open(self.m3u8_file_path, "r") as f:
            all_lines = f.readlines()
        # load all ts to playlists
        for line in all_lines:
            # skip lines without '#'
            if "#" not in line:
                self.playlists.append(line.strip('\n'))


def main():

    url_m3u8 = 'https://****.m3u8'

    downloader = M3U8Downloader(url_m3u8)
    downloader.download()


if __name__ == '__main__':
    print("Run main")
    main()
    print("Finished")
