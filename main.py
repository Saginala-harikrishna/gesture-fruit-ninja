import cv2
import time

from hand_tracking import HandTracker
from object_manager import ObjectManager

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)

hand_tracker = HandTracker()
object_manager = ObjectManager()

game_duration = 60

cv2.namedWindow("Gesture Fruit Ninja", cv2.WINDOW_NORMAL)
cv2.setWindowProperty(
    "Gesture Fruit Ninja",
    cv2.WND_PROP_FULLSCREEN,
    cv2.WINDOW_FULLSCREEN
)

game_state = "menu"
start_time = None

start_clicked = False
close_clicked = False


def mouse_click(event,x,y,flags,param):

    global start_clicked, close_clicked, game_state

    if event == cv2.EVENT_LBUTTONDOWN:

        # start button
        if game_state == "menu":
            if 520 < x < 760 and 400 < y < 480:
                start_clicked = True

        # close button
        if game_state == "gameover":
            if 520 < x < 760 and 420 < y < 500:
                close_clicked = True


cv2.setMouseCallback("Gesture Fruit Ninja", mouse_click)


while True:

    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame,1)

    # MENU SCREEN
    if game_state == "menu":

        cv2.putText(frame,"GESTURE FRUIT NINJA",(300,200),
                    cv2.FONT_HERSHEY_SIMPLEX,2,(0,255,255),4)

        # start button
        cv2.rectangle(frame,(520,400),(760,480),(0,200,0),-1)

        cv2.putText(frame,"START",(580,455),
                    cv2.FONT_HERSHEY_SIMPLEX,1.2,(255,255,255),3)

        if start_clicked:
            game_state = "playing"
            start_time = time.time()

    # GAMEPLAY
    elif game_state == "playing":

        elapsed = int(time.time() - start_time)
        remaining = game_duration - elapsed

        if remaining <= 0:
            game_state = "gameover"

        finger_x, finger_y = hand_tracker.detect(frame)
        segment = hand_tracker.get_last_segment()

        frame = object_manager.update(frame,segment)

        hand_tracker.draw_trail(frame)

        cv2.putText(frame,f"Score: {object_manager.score}",(40,60),
                    cv2.FONT_HERSHEY_SIMPLEX,1.2,(0,255,0),3)

        cv2.putText(frame,f"Time: {remaining}",(40,120),
                    cv2.FONT_HERSHEY_SIMPLEX,1.2,(0,255,255),3)

    # GAME OVER
    elif game_state == "gameover":

        cv2.putText(frame,"GAME OVER",(420,250),
                    cv2.FONT_HERSHEY_SIMPLEX,2.5,(0,0,255),5)

        cv2.putText(frame,f"Final Score: {object_manager.score}",
                    (420,350),
                    cv2.FONT_HERSHEY_SIMPLEX,1.5,(255,255,255),3)

        cv2.rectangle(frame,(520,420),(760,500),(0,0,255),-1)

        cv2.putText(frame,"CLOSE",(585,470),
                    cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),3)

        if close_clicked:
            break

    cv2.imshow("Gesture Fruit Ninja",frame)

    key = cv2.waitKey(1)

    if key == 27:
        break


cap.release()
cv2.destroyAllWindows()