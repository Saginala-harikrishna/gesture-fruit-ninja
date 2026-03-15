import pygame
import cv2
import mediapipe as mp
import numpy as np
import random
import json
import sys
import time

from screen_recorder import ScreenRecorder

pygame.init()
pygame.mixer.init()

WIDTH = 900
HEIGHT = 700

GAME_HEIGHT = int(HEIGHT*0.7)
CAM_HEIGHT = HEIGHT-GAME_HEIGHT

screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Gesture Racing")

clock = pygame.time.Clock()

player_name="player"
if len(sys.argv)>1:
    player_name=sys.argv[1]

cap=cv2.VideoCapture(0)

mp_hands=mp.solutions.hands
hands=mp_hands.Hands(max_num_hands=2)

# ---------- ASSETS ----------

road=pygame.image.load("assets/racing/road.png").convert()
road=pygame.transform.scale(road,(WIDTH,GAME_HEIGHT))

car_img=pygame.image.load("assets/racing/player_car.png").convert_alpha()
car_img=pygame.transform.scale(car_img,(80,120))

traffic_img=pygame.image.load("assets/racing/traffic_car.png").convert_alpha()
traffic_img=pygame.transform.scale(traffic_img,(70,110))

steering_img=pygame.image.load("assets/racing/steering.png").convert_alpha()
steering_img=pygame.transform.scale(steering_img,(120,120))

crash_img=pygame.image.load("assets/racing/crash.png").convert_alpha()
crash_img=pygame.transform.scale(crash_img,(120,120))

# ---------- SOUNDS ----------

engine_sound=pygame.mixer.Sound("assets/sounds/engine.wav")
crash_sound=pygame.mixer.Sound("assets/sounds/crash.wav")
wall_sound=pygame.mixer.Sound("assets/sounds/wall.wav")

font=pygame.font.SysFont("Arial",28)
big_font=pygame.font.SysFont("Arial",48)

# ---------- ROAD ----------

road_y1=0
road_y2=-GAME_HEIGHT
lane_offset=0
base_speed=11

# ---------- PLAYER ----------

car_x=WIDTH//2
car_y=GAME_HEIGHT-150

velocity=0
steer_raw=0
steer_smooth=0

LEFT_BOUND=250
RIGHT_BOUND=WIDTH-250

distance=0
score=0

start_game=False
game_finished=False

start_button=pygame.Rect(WIDTH//2-100,GAME_HEIGHT+20,200,50)
close_button=pygame.Rect(WIDTH//2-100,HEIGHT//2+80,200,60)

traffic=[]
spawn_timer=0

recorder=None
recording_stopped=False

def spawn_car():

    lane=random.choices(["left","right"],weights=[70,30])[0]

    if lane=="left":
        x=WIDTH//2-80
        sp=random.randint(7,9)
    else:
        x=WIDTH//2+80
        sp=random.randint(4,6)

    traffic.append({"x":x,"y":-120,"speed":sp,"lane":lane,"counted":False})

crash_timer=0

running=True

while running:

    clock.tick(60)

    for event in pygame.event.get():

        if event.type==pygame.QUIT:
            running=False

        if event.type==pygame.MOUSEBUTTONDOWN:

            if not start_game and start_button.collidepoint(event.pos):

                start_game=True
                engine_sound.play(loops=-1)

                recorder = ScreenRecorder(player_name)
                recorder.start()

            if game_finished and close_button.collidepoint(event.pos):
                running=False

    ret,frame=cap.read()

    if ret:

        frame=cv2.flip(frame,1)
        rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

        results=hands.process(rgb)

        hands_points=[]

        if results.multi_hand_landmarks:

            for hand in results.multi_hand_landmarks:

                h,w,_=frame.shape
                x=int(hand.landmark[0].x*w)
                y=int(hand.landmark[0].y*h)

                hands_points.append((x,y))

        if len(hands_points)==2:

            (x1,y1),(x2,y2)=hands_points

            if x1<x2:
                left=(x1,y1)
                right=(x2,y2)
            else:
                left=(x2,y2)
                right=(x1,y1)

            lx,ly=left
            rx,ry=right

            steer_raw=(ry-ly)*0.2

        else:
            steer_raw=0

        if abs(steer_raw)<5:
            steer_raw=0

        steer_raw=max(-40,min(40,steer_raw))
        steer_smooth=0.85*steer_smooth+0.15*steer_raw

        frame=cv2.resize(frame,(WIDTH,CAM_HEIGHT))
        frame=np.rot90(frame)
        frame=pygame.surfarray.make_surface(frame)

    # ---------- GAME UPDATE ----------

    if start_game and not game_finished:

        speed = base_speed + int(distance//100)*2
        speed = min(speed,30)

        road_y1+=speed
        road_y2+=speed

        if road_y1>=GAME_HEIGHT:
            road_y1=-GAME_HEIGHT

        if road_y2>=GAME_HEIGHT:
            road_y2=-GAME_HEIGHT

        lane_offset=(lane_offset+speed)%40
        distance+=0.35

        velocity+=steer_smooth*0.001
        velocity=max(-1.5,min(1.5,velocity))
        velocity*=0.94

        car_x+=velocity*15

        if car_x<LEFT_BOUND:
            car_x=LEFT_BOUND
            score-=2
            wall_sound.play()

        if car_x>RIGHT_BOUND:
            car_x=RIGHT_BOUND
            score-=2
            wall_sound.play()

        score=max(score,0)
        score+=1

        spawn_timer+=1

        if spawn_timer>90:
            spawn_car()
            spawn_timer=0

        player_rect=pygame.Rect(car_x-20,car_y-30,40,60)

        for car in traffic:

            car["y"]+=car["speed"]

            car_rect=pygame.Rect(car["x"]+20,car["y"]+30,30,50)

            if player_rect.colliderect(car_rect):

                score-=10
                crash_timer=20
                crash_sound.play()

            if car["y"]>car_y and not car["counted"]:
                score+=5
                car["counted"]=True

        traffic=[c for c in traffic if c["y"]<HEIGHT]

        if distance>=200:

            game_finished=True
            engine_sound.stop()

            if recorder and not recording_stopped:

                file_name = f"{player_name}_{score}_{int(time.time())}.mp4"
                recorder.stop(file_name)

                recording_stopped=True

    # ---------- DRAW ----------

    screen.blit(road,(0,road_y1))
    screen.blit(road,(0,road_y2))

    for i in range(-40,GAME_HEIGHT,40):
        pygame.draw.rect(screen,(255,255,255),(WIDTH//2-5,i+lane_offset,10,20))

    rotation=velocity*-60
    rotation=max(-15,min(15,rotation))

    car=pygame.transform.rotate(car_img,rotation)
    rect=car.get_rect(center=(car_x,car_y))
    screen.blit(car,rect)

    for car in traffic:
        screen.blit(traffic_img,(car["x"],car["y"]))

    if crash_timer>0:
        screen.blit(crash_img,(car_x-60,car_y-60))
        crash_timer-=1

    score_text=font.render(f"Score: {score}",True,(255,255,255))
    screen.blit(score_text,(20,20))

    dist_text=font.render(f"Distance: {int(distance)}/1000 m",True,(255,255,255))
    screen.blit(dist_text,(20,60))

    if ret:
        screen.blit(frame,(0,GAME_HEIGHT))

    wheel=pygame.transform.rotate(steering_img,-steer_smooth)
    wheel_rect=wheel.get_rect(center=(WIDTH//2,GAME_HEIGHT-20))
    screen.blit(wheel,wheel_rect)

    if not start_game:

        pygame.draw.rect(screen,(0,200,0),start_button,border_radius=10)
        txt=font.render("START GAME",True,(255,255,255))
        screen.blit(txt,(start_button.x+25,start_button.y+10))

    if game_finished:

        overlay=pygame.Surface((WIDTH,HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0,0,0))
        screen.blit(overlay,(0,0))

        finish_text=big_font.render("FINISH!",True,(255,255,255))
        screen.blit(finish_text,(WIDTH//2-90,HEIGHT//2-120))

        final_score=big_font.render(f"Score: {score}",True,(255,255,255))
        screen.blit(final_score,(WIDTH//2-90,HEIGHT//2-60))

        pygame.draw.rect(screen,(200,50,50),close_button,border_radius=10)
        close_txt=font.render("CLOSE",True,(255,255,255))
        screen.blit(close_txt,(close_button.x+50,close_button.y+15))

    pygame.display.update()

data={"score":score}

with open("last_score.json","w") as f:
    json.dump(data,f)

pygame.quit()
cap.release()