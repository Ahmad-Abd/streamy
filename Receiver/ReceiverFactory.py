import pathlib

from Receiver.YoutubeReceiver import YoutubeReceiver


class ReceiverFactory:
    '''
    shhhhhhhhhhh
    '''
    def get_receiver(self, url):
        url = url.replace('.', '').lower()
        if 'youtube' in url:
            return YoutubeReceiver()
        else:
            print('Unsupported')
            return None
