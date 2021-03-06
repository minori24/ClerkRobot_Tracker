import cv2
import numpy as np
import servo
import time
import threading

class Tracker:

    def __init__(self):
        self.srv = servo.ServoController()
        self.trackerThread = threading.Thread(target=self.track, name="tracker")
        self.trackingState = False
        self.trackerThread.setDaemon(True)
        self.event_stopTracking = threading.Event()
        self.capture = cv2.VideoCapture(0)

    def startTracking(self):
        self.trackingState = True
        self.event_stopTracking.clear()
        self.trackerThread.start()

        print "start tracking"

    def stopTracking(self):
        self.trackingState = False
        self.event_stopTracking.set()

    def track(self):

        while not self.event_stopTracking.is_set():
            if self.capture.isOpened:
                _, frame = self.capture.read()
                height, width = frame.shape[:2]
                center_x = width / 2
                center_y = height / 2
                rects = self.trackRed(frame)

                if len(rects) > 0:
                    # pick one largest rect
                    rect = max(rects, key=(lambda x: x[2] * x[3]))

                    x = rect[0]
                    y = rect[1]
                    w = rect[2]
                    h = rect[3]

                    dx = (x + w / 2) - center_x
                    dy = (y + h / 2) - center_y
                    self.srv.update(dx * 0.1, dy * 0.1)

        self.capture.release()

    def trackRed(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV_FULL)
        h = hsv[:, :, 0]
        s = hsv[:, :, 1]
        mask = np.zeros(h.shape, dtype=np.uint8)
        mask[((h < 20) | (h > 200)) & (s > 128)] = 255
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        rects = []

        for contour in contours:
            approx = cv2.convexHull(contour)
            rect = cv2.boundingRect(approx)
            rects.append(np.array(rect))
        return rects

    def getCurrentPosition(self):
        pass

    def getTrackingState(self):
        return self.trackingState

if __name__ == "__main__":

    tracker = Tracker()
    tracker.startTracking()
    while True:
        print "wait"
        i = raw_input()
        if i == "c":
            tracker.stopTracking()
            break
