import cv2
import mediapipe as mp


class HandTracker:

    def __init__(self):

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        self.trail_points = []

        self.prev_x = None
        self.prev_y = None
        self.alpha = 0.6


    def detect(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        finger_x = None
        finger_y = None

        if results.multi_hand_landmarks:

            for hand_landmarks in results.multi_hand_landmarks:

                h,w,_ = frame.shape
                tip = hand_landmarks.landmark[8]

                finger_x = int(tip.x * w)
                finger_y = int(tip.y * h)

                if self.prev_x is not None:

                    finger_x = int(self.alpha*self.prev_x + (1-self.alpha)*finger_x)
                    finger_y = int(self.alpha*self.prev_y + (1-self.alpha)*finger_y)

                self.prev_x = finger_x
                self.prev_y = finger_y

                self.trail_points.append((finger_x,finger_y))

                if len(self.trail_points) > 15:
                    self.trail_points.pop(0)

        return finger_x,finger_y


    def draw_trail(self, frame):

        for i in range(1,len(self.trail_points)):

            thickness = int(20*(i/len(self.trail_points)))

            cv2.line(frame,
                     self.trail_points[i-1],
                     self.trail_points[i],
                     (0,255,255),
                     thickness)

            cv2.line(frame,
                     self.trail_points[i-1],
                     self.trail_points[i],
                     (255,255,255),
                     3)


    def get_last_segment(self):

        if len(self.trail_points) < 2:
            return None

        return self.trail_points[-2],self.trail_points[-1]