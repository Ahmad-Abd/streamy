from datetime import datetime
import subprocess
from pafy import pafy
import ffmpeg
import time
from ProcessingSystems.ProcessingSystem import ProcessingSystem
import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_selfie_segmentation = mp.solutions.selfie_segmentation


class SelfieSegmetationBasedCAE(ProcessingSystem):
    def __init__(self,
                 accurate=False,
                 size=(854, 480), # w x h
                 erode_kernel_size=19,
                 blur_kernel_size=13):
        # accurate model 0 (slower but more accurate) use x*x image as input
        # faster model 1 (faster but less accurate) use x*x image as input
        model_index = 0 if accurate is True else 1
        # create mediapipe selfie segmentation model
        self.selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(
            model_selection=model_index)
        # frame size
        self.size = size
        # create erode kernel
        self.kernel = np.ones((erode_kernel_size,) * 2, dtype=np.uint8)
        # previous foreground mask
        self.prev_fgmask = None
        # previous background
        self.prev_bg = None
        # counter
        self.counter = 0
        # blur kernel size
        self.blur_kernel_size = blur_kernel_size

    def resize(self,width ,height):
        self.size = (width ,height)
        self.kernel = np.ones((int(0.04*height,)) * 2, dtype=np.uint8)
        self.blur_kernel_size = int(0.026 * height) + 1

    def get_biggest_contour_mask(self, mask, method=1):
        # create solid rgg black image depending on mask size
        biggest_contour_mask = np.zeros((mask.shape[0], mask.shape[1], 3), np.uint8)
        # extract the contours from the mask
        contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # check about the results
        contours = contours[0] if len(contours) == 2 else contours[1]
        # get the biggest contour
        # Exception if len(contours) == 0 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if len(contours) == 0:
            return biggest_contour_mask
        biggest_contour = max(contours, key=cv2.contourArea)
        # draw the biggest contour
        # color for convex hull
        color = (255, 255, 255)
        cv2.drawContours(biggest_contour_mask, [biggest_contour], -1, (255, 255, 255), -1)
        # calculate convex hull of biggest contour
        # biggest_contour_convex_hull = cv2.convexHull(biggest_contour, False)
        # draw ith convex hull object
        # cv2.drawContours(biggest_contour_mask, [biggest_contour_convex_hull], 0, color, -1)
        # return the result
        return biggest_contour_mask

    def process(self, block):
        # input : bgr as bytes 
        # output : bgr as bytes 
        # convert image from bytes to np.uint8
        image = np.frombuffer(block, dtype=np.uint8).reshape(self.size[1], self.size[0], 3)
        # flip the image on y axis and convert the color from BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        if self.counter % 15 == 0:
            # mark the image as not writable for faster processing
            image.flags.writeable = False
            # extract the body segmentation mask
            results = self.selfie_segmentation.process(image)
            # mark the image as writable
            image.flags.writeable = True
            # get the mask from the results and rescale it
            mask = ((results.segmentation_mask) * 255).astype(np.uint8)
            # apply closing morphological operation on the mask to reduce size of the body
            mask = cv2.morphologyEx(mask, cv2.MORPH_ERODE, self.kernel)
            # get biggest contour mask
            mask = self.get_biggest_contour_mask(mask)
            # restore prev-mask
            self.prev_fgmask = mask.copy()
        else:
            mask = self.prev_fgmask.copy()
        #cv2.imshow('h', cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        #cv2.imshow('hello', mask)
        #if cv2.waitKey(1) & 0xFF == 27:
        #   exit()
        # condition = np.stack((mask,)*3, axis=-1) > 0
        # condition = mask
        if self.counter % 1 == 0:
            bg_image = cv2.GaussianBlur(image, (27,27), 0)
            #bg_image = cv2.GaussianBlur(image, (self.blur_kernel_size, self.blur_kernel_size), 0)
            self.prev_bg = bg_image.copy()
        # else:
        #    bg_image = self.prev_bg.copy()
        output_image = np.where(mask, image, self.prev_bg)
        # output_image = np.where(mask, image, 0)
        #cv2.imshow('mm', cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB))
        #if cv2.waitKey(1) & 0xFF == 27:
        #    exit()
        # b = np.hstack((mask,image))
        self.counter += 1
        return cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB).tobytes()

'''
url = 'news.mp4'
print(ffmpeg.probe(url))
input_stream = ffmpeg.input(url)
video_input_stream = input_stream['v']
video_decoding_process = (
    video_input_stream.output(
        'pipe:',
        format='rawvideo',
        pix_fmt='bgr24'
    ).run_async(pipe_stdout=True)
)
# ffmpeg -i test3.mp4 -c:v libx264 -crf 23 -preset veryslow -c:a copy out.mp4
video_encoding_process = subprocess.Popen(['ffmpeg',
                                           '-y',
                                           '-f', 'rawvideo',
                                           '-s', '854x480',
                                           '-pix_fmt', 'bgr24',
                                           '-i', 'pipe:0',
                                           '-c:v', 'libx264',
                                           # '-maxrate','50k',
                                           # '-bufsize','12000k',
                                           '-color_primaries', 'bt709',
                                           '-profile:v', 'main',
                                           '-pix_fmt', 'yuv420p',
                                           '-crf', '27',
                                           '-preset', 'veryfast',
                                           '-an',
                                           'news-out.mp4'], stdin=subprocess.PIPE)
selfie_seg_based_cae = SelfieSegmetationBasedCAE()
while True:
    video_bytes = video_decoding_process.stdout.read(480 * 854 * 3)
    if video_bytes:
        # in_frame = np.frombuffer(video_bytes, dtype=np.uint8).reshape(480, 854, 3).copy()
        # in_frame = in_frame[:300,:,:]
        # in_frame = cv2.cvtColor(in_frame, cv2.COLOR_BGR2YUV)
        # in_frame[:,:,1:] = cv2.GaussianBlur(in_frame[:,:,1:], (19, 19), 0)
        # in_frame = cv2.cvtColor(in_frame ,cv2.COLOR_YUV2BGR)
        # in_frame[:,:,[0,1]]  = (in_frame[:,:,[0,1]]*0.5).astype(np.uint8)
        # in_frame[:,:,-1]  = (in_frame[:,:,-1]*0.9).astype(np.uint8)
        # in_frame = cv2.cvtColor(in_frame, cv2.COLOR_YUV2BGR)
        # in_frame = cv2.GaussianBlur(in_frame, (13, 13), 0)
        # blurred = cv2.GaussianBlur(in_frame, (5,5), 3);
        # result = cv2.addWeighted(in_frame, 1.9, blurred, -0.9, 0);
        # cv2.imshow('with',cv2.medianBlur(in_frame, 3))
        # cv2.imshow('without',result)
        # if cv2.waitKey(25) & 0xFF == 27:
        #    cv2.destroyAllWindows()
        #    break
        # in_frame[:,:200,:]=0
        # in_frame[:,-200:,:]=0
        # in_frame = cv2.medianBlur(in_frmae, 9)
        # in_frame = cv2.GaussianBlur(in_frame, (9, 9), 0)
        output = selfie_seg_based_cae.process(video_bytes)
        video_encoding_process.stdin.write(output.tobytes())
        # video_encoding_process.stdin.write(video_bytes)
    else:
        print('error')
        break
video_decoding_process.wait()
video_encoding_process.stdin.close()
video_encoding_process.wait()
exit(0)
'''
