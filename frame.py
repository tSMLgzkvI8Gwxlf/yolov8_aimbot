import threading
import cv2
import dxcam
import time
from screeninfo import get_monitors
from screen import *
from options import *

dx = None
obs_camera = None

def thread_hook(args):
    if 'DXCamera' in str(args.thread) and 'cannot join current thread' in str(args.exc_value):
        print('It looks like the game is currently in fullscreen mode, please switch the game to windowed mode or windowless mode.')

def get_new_frame():
    global dx
    global obs_camera

    threading.excepthook = thread_hook

    if Dxcam_capture and dx is None:
        if native_Windows_capture or Obs_capture:
            print('Use only one capture method!')
            exit(0)
        dx = dxcam.create(device_idx=dxcam_monitor_id, output_idx=dxcam_gpu_id, output_color="BGR", max_buffer_len=dxcam_max_buffer_len)
        if dx.is_capturing == False:
            dx.start(Calculate_screen_offset(), target_fps=dxcam_capture_fps)
    if Dxcam_capture and dx is not None:
        img = dx.get_latest_frame()

    if Obs_capture and obs_camera is None:
        if Dxcam_capture or native_Windows_capture:
            print('Use only one capture method!')
            exit(0)
        obs_camera = cv2.VideoCapture(Obs_camera_id)
        obs_camera.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
        obs_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_height)
        obs_camera.set(cv2.CAP_PROP_FPS, Obs_capture_fps)
    if Obs_capture and obs_camera is not None:
        ret_val, img = obs_camera.read()
        
    if native_Windows_capture:
        if Obs_capture or Dxcam_capture:
            print('Use only one capture method!')
            exit(0)
        img = windows_grab_screen(Calculate_screen_offset())

    return img

def speed(annotated_frame, speed_preprocess, speed_inference, speed_postprocess):
    cv2.putText(annotated_frame, 'preprocess:', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1, cv2.LINE_AA)
    cv2.putText(annotated_frame, str(speed_preprocess), (150, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1, cv2.LINE_AA)

    cv2.putText(annotated_frame, 'inference:', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1, cv2.LINE_AA)
    cv2.putText(annotated_frame, str(speed_inference), (150, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1, cv2.LINE_AA)

    cv2.putText(annotated_frame, 'postprocess:', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1, cv2.LINE_AA)
    cv2.putText(annotated_frame, str(speed_postprocess), (150, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1, cv2.LINE_AA)
    return annotated_frame

def draw_boxes(annotated_frame, xyxy):
    for xys in xyxy:
        if xys is not None:
            annotated_frame = cv2.rectangle(annotated_frame, (int(xys[0].item()), int(xys[1].item())), (int(xys[2].item()), int(xys[3].item())), (0, 200, 0), 0)
    return annotated_frame