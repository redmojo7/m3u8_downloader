# m3u8_downloader
## Contents
- scrawler.py - 
## Test
- test.py - test file
## Version information
18 Oct 2022 - Initial version of M3U8 Downloader
## How to run the program
Update your url in function main() in `scrawler.py`
```
def main():
    url_m3u8 = 'https://****.m3u8'
    downloader = M3U8Downloader(url_m3u8)
    downloader.download()
```
then run 
```
python3 scrawler.py 
```
## Base on
https://www.cnblogs.com/dataxon/p/12533110.html
