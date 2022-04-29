import cv2
import mediapipe as mp
import math


class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.3, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):

        xList = []
        yList = []
        bBox = []
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)

                xList.append(cx)
                yList.append(cy)
                # print(id, cx, cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    if id == 8:  # or id == 12:
                        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
            xMin, xMax = min(xList), max(xList)
            yMin, yMax = min(yList), max(yList)
            bBox = xMin, yMin, xMax, yMax

            if draw:
                # greenBox around hand
                cv2.rectangle(img, (xMin - 20, yMin - 20), (xMax + 20, yMax + 20), (0, 255, 0), 2)

        return self.lmList, bBox

    def fingersUp(self):
        fingers = []

        # for thumb
        if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 2][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # for rest 4 fingers
        for id in range(1, 5):
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def findDistance(self, p1, p2, img, draw=True, r=15, t=3):
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        cx, cy, = (x1 + x2) // 2, (y1 + y2) // 2

        # if draw:
        #    cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
        #    cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
        #    cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
        #    cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)

        return length, img, [x1, y1, x2, y2, cx, cy]
