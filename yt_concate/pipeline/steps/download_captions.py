import time
import concurrent.futures
# from threading import Thread
# from multiprocessing import Process

from pytube import YouTube
from pytube.exceptions import RegexMatchError

from .step import Step
from .step import StepException


class DownLoadCaptions(Step):
    def process(self, data, inputs, utils):
        start = time.time()
        processes = []
        # 4 better than 8 ,multithreading takes 814.5s, 1389.5s to download 278 videos
        # 4 multiprocessing takes  495.2s to download 278 videos
        # concurrent takes 89.2s to download 278 videos
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for yt in data:
                print('downloading caption for', yt.url)
                if utils.caption_file_exist(yt):
                    print('found existing caption file')
                    continue
                process = executor.submit(self.download_caption_for_thread, yt, utils)
                processes.append(process)

        end = time.time()
        print('took', end - start, 'seconds')
        return data

    def download_caption_for_thread(self, yt, utils):
        try:
            source = YouTube(yt.url)
            en_caption = source.captions.get_by_language_code('a.en')
            en_caption_convert_to_srt = (en_caption.generate_srt_captions())
            text_file = open(yt.caption_filepath, "w", encoding='utf-8')
            text_file.write(en_caption_convert_to_srt)
            text_file.close()
        except (KeyError, AttributeError, RegexMatchError):
            print('Error when downloading caption for', yt.url)

