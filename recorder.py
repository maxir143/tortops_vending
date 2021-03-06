import os
from datetime import datetime

import numpy as np
import cv2
import pyautogui
from PIL import ImageGrab
import threading
import GPEmu as gp


class Screenwindow:
    def __init__(self, timeout_time=20):
        self.is_running = False
        self.windows = None
        self.last_frames = None
        self.object_detector = cv2.createBackgroundSubtractorMOG2()
        self.triggered = False
        self.timeout = timeout_time * 5
        self.detections = []
        self.gamepad = gp.GamePad()
        self.playSound = True
        self.is_person = 0
        self.audio = 0

    def run_window(self, area_pixels=2000, bounding_box=(0, 0, 400, 400), person_trigger=100):
        sct_img = ImageGrab.grab(bounding_box)
        sct_img = np.array(sct_img)
        img = sct_img
        # mask
        sct_img = self.object_detector.apply(sct_img)
        _, sct_img = cv2.threshold(sct_img, 200, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(sct_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.detections = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            x, y, w, h = cv2.boundingRect(cnt)
            if (area > area_pixels) and (area > (area_pixels/2)) and ((h / 1.7) > w) and ((w * 2) > (h/2)):
                if self.triggered is False and self.is_person > person_trigger:
                    self.is_person = 0
                    self.triggered = True
                    if self.playSound:
                        threading.Thread(target=lambda: gp.play_sound(self.gamepad, self.audio), daemon=True).start()
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)
                self.detections.append([x, y, w, h])
            if self.detections and self.is_running:
                self.is_person += len(self.detections)
            else:
                self.is_person = 0
        self.last_frames = cv2.imencode('.png', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))[1].tobytes()
        return self.last_frames

    def start(self, time_out):
        self.gamepad = gp.GamePad()
        self.is_running = True
        cv2.destroyAllWindows()
        self.reset_trigger(time_out)

    def stop(self, time_out):
        self.gamepad = None
        self.is_running = False
        cv2.destroyAllWindows()
        self.reset_trigger(time_out)

    def reset_trigger(self, time_out=200):
        self.triggered = False
        self.timeout = time_out * 5
        self.is_person = 0

    def switch_play_sound(self, value: bool = None):
        if self.playSound:
            self.playSound = False
        else:
            self.playSound = True

        if value is not None:
            self.playSound = value

        return self.playSound

class Recorder:
    def __init__(self, fps=10, max_length=10000):
        self.recording = False
        self.folder = os.path.expanduser(fr'~\Desktop\WagonWatcher\{datetime.today().strftime("%Y-%m-%d")}')
        os.makedirs(self.folder, exist_ok=True)
        self.screen_size = pyautogui.size()
        self.fps = fps
        self.max_length = max_length
        self.daemon = True

    def set_daemon(self, daemon):
        self.daemon = daemon

    def stop_recording(self):
        if self.recording:
            self.recording = False
            print('Stop Recording')

    def is_recording(self):
        return self.recording

    def start_recording(self):
        if self.is_recording():
            return
        print('Start Recording')

        def record():
            fps = int(self.fps)
            screen_size = self.screen_size
            max_length = self.max_length
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            time = datetime.now().strftime("%H-%M-%S")
            file_name_format = rf'{self.folder}\{time}.avi'
            out = cv2.VideoWriter(file_name_format, fourcc, fps, screen_size)
            max_recording_time = max_length
            for i in range(int(max_recording_time * fps)):  # Recording
                img = pyautogui.screenshot()
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                out.write(frame)
                if self.recording is False:
                    cv2.destroyAllWindows()
                    out.release()
                    print(f'File Saved at {file_name_format}')
                    return
            print(f'File Saved at {file_name_format}')
            self.stop_recording()
        self.recording = True
        threading.Thread(target=record, daemon=self.daemon).start()
