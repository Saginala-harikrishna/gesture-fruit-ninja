import cv2
import mediapipe as mp
import math

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils


class SteeringController:

    def __init__(self):

        self.cap = cv2.VideoCapture(0)

        self.hands = mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7
        )

        self.angle = 0

    def get_steering(self):

        ret, frame = self.cap.read()

        if not ret:
            return None

        frame = cv2.flip(frame,1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.hands.process(rgb)

        h, w, _ = frame.shape

        points = []

        if results.multi_hand_landmarks:

            for hand in results.multi_hand_landmarks:

                mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

                # wrist point
                x = int(hand.landmark[0].x * w)
                y = int(hand.landmark[0].y * h)

                points.append((x,y))

        if len(points) == 2:

            (x1,y1),(x2,y2) = points

            dx = x2-x1
            dy = y2-y1

            angle = math.degrees(math.atan2(dy,dx))

            self.angle = angle

            cv2.line(frame,(x1,y1),(x2,y2),(0,255,0),3)

            cv2.putText(
                frame,
                f"Steering: {int(angle)}",
                (30,50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,255,0),
                2
            )

        cv2.imshow("Steering Camera",frame)

        return self.angle