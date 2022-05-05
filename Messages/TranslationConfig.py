from Messages.Message import Message


class TranslationConfig(Message):
    def __init__(self,
                 src_language,
                 dst_language):
        self.src_language = src_language
        self.dst_language = dst_language

    def from_json(self, json_object):
        self.src_language = json_object['src_language']
        self.dst_language = json_object['src_language']

    def __str__(self):
        return f'source language : {self.src_language}, ' \
               f'destination language : {self.dst_language}, '
