import numpy as np
import cv2
from PIL import ImageGrab
import threading
import GPEmu as gp


class Screenwindow:
    def __init__(self, timeout_time=30):
        self.is_running = False
        self.windows = None
        self.last_frames = None
        self.object_detector = cv2.createBackgroundSubtractorMOG2()

        self.triggered = False
        self.timeout_time = timeout_time
        self.timeout = self.timeout_time
        self.detections = []
        self.gamepad = gp.GamePad()
        self.playSound = False

    def run_window(self, area_pixels=800, bounding_box=(0, 0, 100, 100)):
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
            if area > area_pixels:
                if self.triggered is False:
                    self.triggered = True
                    if self.playSound:
                        threading.Thread(target=lambda: gp.play_sound(self.gamepad), daemon=True).start()
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)
                self.detections.append([x, y, w, h])
        self.last_frames = cv2.imencode('.png', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))[1].tobytes()
        return self.last_frames

    def start(self):
        self.is_running = True

    def stop(self):
        self.is_running = False
        cv2.destroyAllWindows()
        self.reset_trigger()

    def reset_trigger(self):
        self.triggered = False
        self.timeout = self.timeout_time

    def switch_play_sound(self, value: bool = None):
        if self.playSound:
            self.playSound = False
        else:
            self.playSound = True

        if value is not None:
            self.playSound = value

        return self.playSound
