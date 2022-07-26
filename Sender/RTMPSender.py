'''
! ffmpeg -re -f lavfi -i "smptehdbars=rate=30:size=1920x1080" \
-f lavfi -i "sine=frequency=1000:sample_rate=48000" \
-vf drawtext="text='ِAhmad Tahan:timecode=01\:00\:00\:00':rate=30:x=(w-tw)/2:y=(h-lh)/2:fontsize=48:fontcolor=white:box=1:boxcolor=black" \
-f flv -c:v h264 -profile:v baseline -pix_fmt yuv420p -preset ultrafast -tune zerolatency -crf 28 -g 60 -c:a aac \
"rtmp://a.rtmp.youtube.com/live2/3wgb-cv03-ckyy-jmxc-cw42"
'''
from Sender.Sender import Sender


class RTMPSender(Sender):
    def __init__(self):
        super().__init__()

    def set_config(self, request):
        super(RTMPSender, self).set_config(request)
        self.dst = request.rtmp_server_url

    def send(self):
        return self.dst + self.request.rtmp_server_key
