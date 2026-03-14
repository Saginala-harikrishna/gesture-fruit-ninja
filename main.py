import cv2
import mediapipe as mp
import random
import math

# Initialize mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

# Start webcam
cap = cv2.VideoCapture(0)

# Load fruit images
apple = cv2.imread("assets/fruits/apple.png", cv2.IMREAD_UNCHANGED)
banana = cv2.imread("assets/fruits/banana.png", cv2.IMREAD_UNCHANGED)
watermelon = cv2.imread("assets/fruits/watermelon.png", cv2.IMREAD_UNCHANGED)
orange = cv2.imread("assets/fruits/orange.png", cv2.IMREAD_UNCHANGED)

fruit_images = [apple, banana, watermelon, orange]

# Game variables
fruits = []
score = 0

while True:

    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    finger_x = None
    finger_y = None

    # Hand detection
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            index_tip = hand_landmarks.landmark[8]

            h, w, c = frame.shape

            finger_x = int(index_tip.x * w)
            finger_y = int(index_tip.y * h)

            cv2.circle(frame, (finger_x, finger_y), 10, (0,0,255), -1)

    # Spawn fruits
    if random.randint(1,20) == 1:

        fruit_img = random.choice(fruit_images)

        x = random.randint(100,500)
        y = 480
        speed = random.randint(4,7)

        fruits.append([x, y, speed, fruit_img])

    # Draw fruits
    for fruit in fruits[:]:

        x, y, speed, img = fruit

        h_img, w_img, _ = img.shape

        x1 = int(x - w_img / 2)
        y1 = int(y - h_img / 2)

        x2 = x1 + w_img
        y2 = y1 + h_img

        # Draw fruit image
        if y1 > 0 and y2 < frame.shape[0] and x1 > 0 and x2 < frame.shape[1]:

            frame[y1:y2, x1:x2] = img[:, :, :3]

        # Move fruit upward
        fruit[1] -= speed

        # Collision detection
        if finger_x is not None and finger_y is not None:

            radius = w_img // 2

            distance = math.sqrt((finger_x - x)**2 + (finger_y - y)**2)

            if distance < radius:

                fruits.remove(fruit)
                score += 1

    # Remove fruits off screen
    fruits = [fruit for fruit in fruits if fruit[1] > 0]

    # Display score
    cv2.putText(
        frame,
        f"Score: {score}",
        (20,50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,255,0),
        2
    )

    cv2.imshow("Gesture Fruit Ninja", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()