import cv2
import random
import time
import math
import pygame

pygame.mixer.init()

slice_sound = pygame.mixer.Sound("assets/sounds/slice.wav")
explosion_sound = pygame.mixer.Sound("assets/sounds/explosion.wav")


def draw_png(frame,img,x,y):

    h_img,w_img = img.shape[:2]

    x1 = int(x - w_img/2)
    y1 = int(y - h_img/2)

    x2 = x1 + w_img
    y2 = y1 + h_img

    if x1<0 or y1<0 or x2>frame.shape[1] or y2>frame.shape[0]:
        return

    alpha = img[:,:,3]/255.0

    for c in range(3):

        frame[y1:y2,x1:x2,c] = (
            alpha*img[:,:,c] +
            (1-alpha)*frame[y1:y2,x1:x2,c]
        )


def split_fruit(img):

    h,w = img.shape[:2]

    return img[:,:w//2],img[:,w//2:]


class ObjectManager:

    def __init__(self):

        self.apple = cv2.imread("assets/fruits/apple.png",cv2.IMREAD_UNCHANGED)
        self.banana = cv2.imread("assets/fruits/banana.png",cv2.IMREAD_UNCHANGED)
        self.orange = cv2.imread("assets/fruits/orange.png",cv2.IMREAD_UNCHANGED)
        self.watermelon = cv2.imread("assets/fruits/watermelon.png",cv2.IMREAD_UNCHANGED)

        self.bomb = cv2.imread("assets/bombs/bomb.png",cv2.IMREAD_UNCHANGED)

        self.juice = cv2.imread("assets/effects/juice.png",cv2.IMREAD_UNCHANGED)
        self.explosion = cv2.imread("assets/effects/explosion.png",cv2.IMREAD_UNCHANGED)

        self.fruits=[self.apple,self.banana,self.orange,self.watermelon]

        self.current_object=None
        self.spawn_time=None
        self.pause_time=None

        self.slices=[]
        self.splashes=[]
        self.explosions=[]

        self.score=0


    def spawn_object(self):

        obj_type=random.choices(["fruit","bomb"],weights=[85,15])[0]

        img=random.choice(self.fruits) if obj_type=="fruit" else self.bomb

        self.current_object={
            "type":obj_type,
            "img":img,
            "x":random.randint(200,1000),
            "y":random.randint(200,600)
        }

        self.spawn_time=time.time()


    def update(self,frame,segment):

        now=time.time()

        # faster spawn rate
        if self.current_object is None:

            if self.pause_time is None or now-self.pause_time>0.12:
                self.spawn_object()

        # update fruit halves
        for piece in self.slices:

            piece["x"] += piece["vx"]
            piece["y"] += piece["vy"]

            piece["vy"] += 0.4

            draw_png(frame,piece["img"],piece["x"],piece["y"])

        # splash effect
        for splash in self.splashes:

            if now - splash["time"] < 1:
                draw_png(frame,self.juice,splash["x"],splash["y"])

        # explosion effect
        for blast in self.explosions:

            if now - blast["time"] < 1:
                draw_png(frame,self.explosion,blast["x"],blast["y"])

        if self.current_object is None:
            return frame

        obj=self.current_object

        draw_png(frame,obj["img"],obj["x"],obj["y"])

        if segment is not None:

            (x1,y1),(x2,y2)=segment

            speed = math.hypot(x2-x1,y2-y1)

            if speed > 30:

                d=math.hypot(obj["x"]-x2,obj["y"]-y2)

                h,w=obj["img"].shape[:2]

                if d < w//2:

                    if obj["type"]=="fruit":

                        left,right = split_fruit(obj["img"])

                        # faster slice motion
                        self.slices.append({"img":left,"x":obj["x"],"y":obj["y"],"vx":-8,"vy":-9})
                        self.slices.append({"img":right,"x":obj["x"],"y":obj["y"],"vx":8,"vy":-9})

                        self.splashes.append({"x":obj["x"],"y":obj["y"],"time":now})

                        slice_sound.play()

                        self.score+=1

                    else:

                        self.explosions.append({"x":obj["x"],"y":obj["y"],"time":now})

                        explosion_sound.play()

                        self.score-=3

                    self.current_object=None
                    self.pause_time=now

        if now-self.spawn_time>3:

            self.current_object=None
            self.pause_time=now

        return frame