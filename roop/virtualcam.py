import cv2
import roop.globals
import ui.globals
import pyvirtualcam
import threading
import time


cam_active = False
cam_thread = None
vcam = None

def virtualcamera(streamobs, cam_num,width,height):
    from roop.core import live_swap
    from roop.filters import fast_quantize_to_palette

    global cam_active

    #time.sleep(2)
    print('Starting capture')
    cap = cv2.VideoCapture(cam_num, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Cannot open camera")
        cap.release()
        del cap
        return

    pref_width = width
    pref_height = height
    pref_fps_in = 30
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, pref_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, pref_height)
    cap.set(cv2.CAP_PROP_FPS, pref_fps_in)
    cam_active = True

    # native format UYVY

    cam = None
    if streamobs:
        print('Detecting virtual cam devices')
        cam = pyvirtualcam.Camera(width=pref_width, height=pref_height, fps=pref_fps_in, fmt=pyvirtualcam.PixelFormat.BGR, print_fps=False)
    if cam:
        print(f'Using virtual camera: {cam.device}')
        print(f'Using {cam.native_fmt}')
    else:
        print(f'Not streaming to virtual camera!')

    while cam_active:
        ret, frame = cap.read()
        if not ret:
            break

        if len(roop.globals.INPUT_FACESETS) > 0:
            frame = live_swap(frame, "all", False, None)
        #frame = fast_quantize_to_palette(frame)
        if cam:
            cam.send(frame)
            cam.sleep_until_next_frame()
        ui.globals.ui_camera_frame = frame

    if cam:
        cam.close()
    cap.release()
    print('Camera stopped')



def start_virtual_cam(streamobs, cam_number, resolution):
    global cam_thread, cam_active

    if not cam_active:
        width, height = map(int, resolution.split('x'))
        cam_thread = threading.Thread(target=virtualcamera, args=[streamobs, cam_number, width, height])
        cam_thread.start()



def stop_virtual_cam():
    global cam_active, cam_thread

    if cam_active:
        cam_active = False
        cam_thread.join()
    

