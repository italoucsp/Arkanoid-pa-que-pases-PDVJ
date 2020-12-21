import pygame
import time
import math
import copy
import random

pg = pygame

global visibleHitbox

visibleHitbox = False

global tickness
tickness = pg.time.Clock().tick(60)

get_spped = lambda fps : 25 * float(fps)*0.01 / math.sqrt(fps) * math.log2(fps)
deltaTime = lambda dt : 1 / float(dt)
paddleCol = lambda x : 2 * x - 64

animations = {}

bg_dark = pg.Color(255,0,0,50)

class Vector2f:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class HitBox:
    def __init__(self, image, x, y, rows, cols):
        self.rect = image.get_rect()
        self.rect.width /= cols
        self.rect.height /= rows
        self.sl = Vector2f(x, y)
        self.sr = Vector2f(x + self.rect.width, y)
        self.il = Vector2f(x, y + self.rect.height)
        self.ir = Vector2f(x + self.rect.width, y + self.rect.height)
        self.left = Vector2f(x, y + self.rect.height / 2)
        self.right = Vector2f(x  + self.rect.width, y + self.rect.height / 2)
        self.top = Vector2f(x + self.rect.width / 2, y)
        self.bottom = Vector2f(x + self.rect.width / 2, y + self.rect.height)
        self.x = x
        self.y = y

    def refreshPosition(self, x, y):
        self.x = x
        self.y = y
        self.sl = Vector2f(x, y)
        self.sr = Vector2f(x + self.rect.width, y)
        self.il = Vector2f(x, y + self.rect.height)
        self.ir = Vector2f(x + self.rect.width, y + self.rect.height)
        self.left = Vector2f(x, y + self.rect.height / 2)
        self.right = Vector2f(x  + self.rect.width, y + self.rect.height / 2)
        self.top = Vector2f(x + self.rect.width / 2, y)
        self.bottom = Vector2f(x + self.rect.width / 2, y + self.rect.height)

    def showHitbox(self, app):
        if visibleHitbox:
            pg.draw.rect(app,(255,0,0),(self.x,self.y,self.rect.width,self.rect.height),2)

    def check_BallVsPaddle_Collision(self, paddle):
        #if self.y + self.rect.height >= paddle.hb.y and self.x >= paddle.x and self.x <= paddle.x + paddle.hb.rect.width:
        if self.collidePoint(paddle, self.x, self. y + self.rect.height) or self.collidePoint(paddle, self.x + self.rect.width, self. y + self.rect.height):
            velx = paddleCol(self.x - paddle.hb.x)
            if (velx > 64):
                velx = 55
            if (velx < -64):
                velx = -55
            vely = (74 - abs(velx))
            return [True, velx, vely]
        return [False, 0, 0]

    def collidePoint(self, brick, x, y):
        p1x = brick.hb.x
        p2x = brick.hb.x + brick.hb.rect.width
        p1y = brick.hb.y
        p2y = brick.hb.y + brick.hb.rect.height
        if (x >= p1x) and (x <= p2x) and (y >= p1y) and (y <= p2y):
            return True
        return False

    def check_Collision(self, obj1, obj2):
        hb1 = obj1.hb
        if self.collidePoint(obj2, hb1.left.x, hb1.left.y):
            obj1.x += abs(obj2.hb.right.x - hb1.left.x)
            return 1
        if self.collidePoint(obj2, hb1.right.x, hb1.right.y):
            obj1.x -= abs(obj2.hb.left.x - hb1.right.x)
            return 1
        if self.collidePoint(obj2, hb1.top.x, hb1.top.y):
            obj1.y += abs(obj2.hb.bottom.y - hb1.top.y)
            return 2
        if self.collidePoint(obj2, hb1.bottom.x, hb1.bottom.y):
            obj1.y -= abs(obj2.hb.top.y - hb1.bottom.y)
            return 2
        return 0

    def check_BallVsBrick_Collision(self, brick):
        if self.collidePoint(brick, self.x, self.y + self.rect.height / 2) or self.collidePoint(brick, self.x + self.rect.width, self.y + self.rect.height / 2):
            return 1
        if self.collidePoint(brick, self.x + self.rect.width / 2, self.y) or self.collidePoint(brick, self.x + self.rect.width / 2, self.y + self.rect.height):
            return 2
        return 0

class Animation:
    def __init__(self,image_path,fps,frames,w,h,rows,cols,inLoop):
        self.source = pg.image.load(image_path)
        self.imgPath = image_path
        self.FRAMES = []
        self.repeteable = inLoop
        self.c_draw = True
        self.fps = fps
        self.x0 = 0
        self.y0 = 0
        self.frame_ind = 0
        self.it = 0.0
        self.calc_dtime = get_spped(fps)
        self.checkpoint = 20.0
        self.rows_ = rows
        self.cols_ = cols
        self.anim_finished = False
        for y in range(rows):
            for x in range(cols):
                if frames != 0:
                    n_frame = (x * w, y * h, w, h)
                    self.FRAMES.append(n_frame)
                    frames -= 1

    def setPosition(self, x, y):
        self.x0 = x
        self.y0 = y

    def restart(self):
        self.anim_finished = False
        self.c_draw = True
        self.frame_ind = 0
        self.it = 0.0

    def update(self):
        if self.it < self.checkpoint:
            self.it += self.calc_dtime
        else:
            self.it = 0.0
            self.frame_ind = (self.frame_ind + 1) % len(self.FRAMES)

    def show(self, app):
        self.update()
        if self.repeteable == True:
            app.blit(self.source, (self.x0, self.y0), (self.FRAMES[self.frame_ind]))
        else:
            if self.c_draw:
                app.blit(self.source, (self.x0, self.y0), (self.FRAMES[self.frame_ind]))
            else:
                app.blit(self.source, (self.x0, self.y0), (self.FRAMES[-1]))
            if self.frame_ind == len(self.FRAMES) - 1:
                self.c_draw = False
                self.anim_finished = True

animations["brick_stand1"] = Animation("imgs/brick_0.png", 30, 4, 32, 16, 4, 1, False)
animations["brick_stand2"] = Animation("imgs/brick_1.png", 45, 9, 32, 16, 1, 9, False)
animations["brick_destroy"] = Animation("imgs/brick_2.png", 20, 4, 32, 16, 1, 4, False)
animations["paddle_anim"] = Animation("imgs/paddle.png", 30, 4, 64, 16, 1, 4, True)
animations["ball_anim"] = Animation("imgs/ball.png", 60, 4, 20, 20, 1, 4, True)
