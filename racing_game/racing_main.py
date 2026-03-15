import pygame
import cv2
import mediapipe as mp
import numpy as np
import json

pygame.init()

# -----------------------------
# WINDOW
# -----------------------------

WIDTH = 900
HEIGHT = 700

GAME_HEIGHT = int(HEIGHT * 0.7)
CAM_HEIGHT = HEIGHT - GAME_HEIGHT

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gesture Racing")

clock = pygame.time.Clock()

# -----------------------------
# CAMERA
# -----------------------------

cap = cv2.VideoCapture(0)

# -----------------------------
# MEDIAPIPE
# -----------------------------

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)
draw = mp.solutions.drawing_utils

# -----------------------------
# LOAD ASSETS
# -----------------------------

road = pygame.image.load("assets/racing/road.png").convert()
road = pygame.transform.scale(road,(WIDTH,GAME_HEIGHT))

car = pygame.image.load("assets/racing/player_car.png").convert_alpha()
car = pygame.transform.scale(car,(80,120))

steering_img = pygame.image.load("assets/racing/steering.png").convert_alpha()
steering_img = pygame.transform.scale(steering_img,(120,120))

font = pygame.font.SysFont("Arial",28)
big_font = pygame.font.SysFont("Arial",48)

# -----------------------------
# ROAD MOVEMENT
# -----------------------------

road_y1 = 0
road_y2 = -GAME_HEIGHT

speed = 8

# -----------------------------
# GAME VARIABLES
# -----------------------------

car_x = WIDTH//2
car_y = GAME_HEIGHT-150

distance = 0
score = 0

start_game = False
game_finished = False

start_button = pygame.Rect(WIDTH//2-100,GAME_HEIGHT+20,200,50)
close_button = pygame.Rect(WIDTH//2-100,HEIGHT//2+80,200,60)

# -----------------------------
# STEERING
# -----------------------------

steer_raw = 0
steer_smooth = 0

velocity = 0

# lane boundaries
LEFT_BOUND = 250
RIGHT_BOUND = WIDTH-250

# -----------------------------
# GAME LOOP
# -----------------------------

running = True

while running:

    clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running=False

        if event.type == pygame.MOUSEBUTTONDOWN:

            if not start_game and start_button.collidepoint(event.pos):
                start_game=True

            if game_finished and close_button.collidepoint(event.pos):
                running=False

    # -----------------------------
    # CAMERA FRAME
    # -----------------------------

    ret,frame = cap.read()

    if ret:

        frame = cv2.flip(frame,1)
        rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

        results = hands.process(rgb)

        hands_points=[]

        if results.multi_hand_landmarks:

            for hand in results.multi_hand_landmarks:

                draw.draw_landmarks(frame,hand,mp_hands.HAND_CONNECTIONS)

                h,w,_ = frame.shape

                x = int(hand.landmark[0].x*w)
                y = int(hand.landmark[0].y*h)

                hands_points.append((x,y))

        if len(hands_points)==2:

            (x1,y1),(x2,y2)=hands_points

            if x1 < x2:
                left=(x1,y1)
                right=(x2,y2)
            else:
                left=(x2,y2)
                right=(x1,y1)

            lx,ly = left
            rx,ry = right

            steer_raw = (ry - ly) * 0.2

        else:
            steer_raw = 0

        if abs(steer_raw) < 5:
            steer_raw = 0

        steer_raw = max(-40,min(40,steer_raw))

        steer_smooth = 0.85*steer_smooth + 0.15*steer_raw

        frame = cv2.resize(frame,(WIDTH,CAM_HEIGHT))
        frame = np.rot90(frame)
        frame = pygame.surfarray.make_surface(frame)

    # -----------------------------
    # GAME UPDATE
    # -----------------------------

    if start_game and not game_finished:

        # speed boost after halfway
        if distance > 250:
            speed = 11
        else:
            speed = 8

        road_y1 += speed
        road_y2 += speed

        if road_y1 >= GAME_HEIGHT:
            road_y1 = -GAME_HEIGHT

        if road_y2 >= GAME_HEIGHT:
            road_y2 = -GAME_HEIGHT

        distance += 0.35

        # steering physics
        velocity += steer_smooth * 0.001
        velocity = max(-1.5,min(1.5,velocity))
        velocity *= 0.94

        car_x += velocity*15

        # -----------------------------
        # LANE BOUNDARY COLLISION
        # -----------------------------

        if car_x < LEFT_BOUND:
            car_x = LEFT_BOUND
            score -= 2

        if car_x > RIGHT_BOUND:
            car_x = RIGHT_BOUND
            score -= 2

        score = max(score,0)

        # score increases while driving
        score += 1

        # finish line
        if distance >= 500:
            game_finished=True

    # -----------------------------
    # DRAW GAME AREA
    # -----------------------------

    screen.blit(road,(0,road_y1))
    screen.blit(road,(0,road_y2))

    rotation = velocity * -60
    rotation = max(-15,min(15,rotation))

    rotated_car = pygame.transform.rotate(car,rotation)

    rect = rotated_car.get_rect(center=(car_x,car_y))

    screen.blit(rotated_car,rect)

    score_text = font.render(f"Score: {score}",True,(255,255,255))
    screen.blit(score_text,(20,20))

    dist_text = font.render(f"Distance: {int(distance)} / 500 m",True,(255,255,255))
    screen.blit(dist_text,(20,60))

    # -----------------------------
    # WEBCAM AREA
    # -----------------------------

    if ret:
        screen.blit(frame,(0,GAME_HEIGHT))

    wheel = pygame.transform.rotate(steering_img,-steer_smooth)

    wheel_rect = wheel.get_rect(center=(WIDTH//2,GAME_HEIGHT+120))

    screen.blit(wheel,wheel_rect)

    # -----------------------------
    # START BUTTON
    # -----------------------------

    if not start_game:

        pygame.draw.rect(screen,(0,200,0),start_button,border_radius=10)

        txt = font.render("START GAME",True,(255,255,255))
        screen.blit(txt,(start_button.x+25,start_button.y+10))

    # -----------------------------
    # FINISH SCREEN
    # -----------------------------

    if game_finished:

        overlay = pygame.Surface((WIDTH,HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0,0,0))
        screen.blit(overlay,(0,0))

        finish_text = big_font.render("FINISH!",True,(255,255,255))
        screen.blit(finish_text,(WIDTH//2-90,HEIGHT//2-120))

        final_score = big_font.render(f"Score: {score}",True,(255,255,255))
        screen.blit(final_score,(WIDTH//2-90,HEIGHT//2-60))

        pygame.draw.rect(screen,(200,50,50),close_button,border_radius=10)

        close_txt = font.render("CLOSE",True,(255,255,255))
        screen.blit(close_txt,(close_button.x+50,close_button.y+15))

    pygame.display.update()

# -----------------------------
# SAVE SCORE
# -----------------------------

data={"score":score}

with open("last_score.json","w") as f:
    json.dump(data,f)

pygame.quit()
cap.release()