from algorithms.GestureClassifer import GestureClassifer
import numpy as np
import cv2 as cv

class MeanShift(GestureClassifer):
    def __init__(self, first_frame, init_loc: tuple):
        super().__init__()
        self.loc = init_loc
        self.last_rois = [self.loc]
        # get first frame
        self.roi = self.prepare_first_frame(first_frame)
        self.roi_hist = self.get_histogram()
        # Setup the termination criteria, either 10 iteration or move by atleast 1 pt
        self.term = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 1)

    def prepare_first_frame(self, frame):
        # read first frame and set roi - region of interest with given location
        tracked = frame[self.loc[1]:self.loc[1] + self.loc[3], self.loc[0]:self.loc[0] + self.loc[2]]
        return tracked

    def get_histogram(self):
        hsv_roi = cv.cvtColor(self.roi, cv.COLOR_BGR2HSV)
        # get histogram of hue
        mask = cv.inRange(hsv_roi, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
        hist = cv.calcHist([hsv_roi], [0], mask, [180], [0, 180])  # TODO poczytać o mask w calcHist and normalization
        return cv.normalize(hist, hist, 0, 255, cv.NORM_MINMAX)

    def run(self, frame):
        hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        # find the same object with Back Projection based on histogram
        dst = cv.calcBackProject([hsv_frame], [0], self.roi_hist, [0, 180], 1)
        # apply meanshift to get the new location
        _, self.loc = cv.meanShift(dst, self.loc, self.term)
        self.last_rois.append(self.loc)
        color = self.classify(self.last_rois)
        # show rectangle with mean that is working
        img = cv.rectangle(frame, (self.loc[0], self.loc[1]), (self.loc[0] + self.loc[2], self.loc[1] + self.loc[3]), 255, 2)
        cv.imshow('img', img)
        cv.waitKey(30) & 0xff
        return color
