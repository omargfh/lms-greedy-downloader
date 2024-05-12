from canvas_selenium import download_multiple

from threading import Thread

def download_multiple_async(driver, entries):
    Thread(target=download_multiple, args=(driver, entries)).start()