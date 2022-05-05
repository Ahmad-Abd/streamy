import pathlib

from Receiver.YoutubeReceiver import YoutubeReceiver
from Sender.RTMPSender import RTMPSender


class SenderFactory:

    def get_sender(self, url):
        url = url.replace('.', '').lower()
        if 'rtmp' in url:
            return RTMPSender()
        else:
            print('Unsupported')
            return None
