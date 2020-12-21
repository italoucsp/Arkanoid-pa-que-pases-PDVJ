import pygame
import utilities
from utilities import *

pg = pygame

global W
global H

W = 450
H = 550

class Limit:
    def __init__(self, image_path, x, y):
        self.x = x
        self.y = y
        self.image = pg.image.load(image_path)
        self.hb = HitBox(self.image, x, y, 1, 1)

    def show(self, app):
        app.blit(self.image, (self.x, self.y))
        self.hb.showHitbox(app)

class Brick:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.broken = False
        self.anim0 = copy.copy(animations["brick_stand1"])
        self.anim1 = copy.copy(animations["brick_stand2"])
        self.anim2 = copy.copy(animations["brick_destroy"])
        self.currentAnimation = self.anim0
        self.currentAnimation.setPosition(self.x, self.y)
        self.hb = HitBox(self.currentAnimation.source, self.x, self.y, self.currentAnimation.rows_, self.currentAnimation.cols_)

    def destroyBrick(self):
        if not self.broken:
            self.broken = True
            self.currentAnimation = self.anim2
            self.currentAnimation.setPosition(self.x, self.y)

    def show(self,app):
        if not self.broken and self.currentAnimation.anim_finished:
            anim_rand = random.randint(0,100)
            if anim_rand <= 95:
                self.currentAnimation = self.anim0
                self.currentAnimation.restart()
                self.currentAnimation.setPosition(self.x, self.y)
            else:
                self.currentAnimation = self.anim1
                self.currentAnimation.restart()
                self.currentAnimation.setPosition(self.x, self.y)
        self.currentAnimation.show(app)
        self.hb.showHitbox(app)

class Paddle:
    def __init__(self):
        self.x = W / 2 - 32
        self.y = H - H / 10
        self.currentAnimation = copy.copy(animations["paddle_anim"])
        self.currentAnimation.setPosition(self.x, self.y)
        self.hb = HitBox(self.currentAnimation.source, self.x, self.y, self.currentAnimation.rows_, self.currentAnimation.cols_)

    def move(self,x, wall1, wall2):
        if self.hb.check_BallVsBrick_Collision(wall1) == 1:
            if x < 0:
                x = 0
        if self.hb.check_BallVsBrick_Collision(wall2) == 1:
            if x > 0:
                x = 0
        self.x += x * deltaTime(tickness)
        self.currentAnimation.setPosition(self.x, self.y)
        self.hb.refreshPosition(self.x,self.y)

    def show(self,app):
        self.currentAnimation.show(app)
        self.hb.showHitbox(app)

class Ball:
    def __init__(self):
        self.x = W / 2 - 10
        self.y = H - H / 10 - 20
        self.velx = 0
        self.vely = -64
        self.currentAnimation = copy.copy(animations["ball_anim"])
        self.currentAnimation.setPosition(self.x, self.y)
        self.hb = HitBox(self.currentAnimation.source, self.x, self.y, self.currentAnimation.rows_, self.currentAnimation.cols_)

    def checkCollisions(self, paddle, brickList, limits):
        self.x += self.velx * deltaTime(tickness)
        self.y += self.vely * deltaTime(tickness)
        self.currentAnimation.setPosition(self.x, self.y)
        self.hb.refreshPosition(self.x,self.y)
        padCol = self.hb.check_BallVsPaddle_Collision(paddle)
        if padCol[0]:
            self.velx = padCol[1]
            self.vely = -abs(padCol[2])
        for brick in brickList:
            if not brick.broken:
                col = self.hb.check_Collision(self,brick)
                if col == 1:
                    self.velx = -(self.velx)
                    brick.destroyBrick()
                elif col == 2:
                    self.vely = -(self.vely)
                    brick.destroyBrick()
        for limit in limits:
            col = self.hb.check_Collision(self,limit)
            if col == 1:
                self.velx = -(self.velx)
            elif col == 2:
                self.vely = -(self.vely)

    def show(self,app):
        self.currentAnimation.show(app)
        self.hb.showHitbox(app)

class Arkanoid:
    def __init__(self):
        pg.init()
        self.app = pg.display.set_mode((W,H))
        pg.display.set_caption("Arkanoid!")
        self.FramerateLimit = pg.time.Clock()
        self.appClosed = False
        self.paddle = Paddle()
        self.ball = Ball()
        self.brickList = []
        self.bGround = pg.image.load("imgs/background_dark.png")
        self.wall1 = Limit("imgs/wall.png", 0, 32)
        self.wall2 = Limit("imgs/wall.png", W - 32, 32)
        self.top = Limit("imgs/top.png", 0, 0)
        self.limits = [self.wall1,self.wall2,self.top]
        self.startGame = False

    def buildLevel(self, level_path):
        lvl_file = open(level_path, "r")
        map_lvl = lvl_file.readlines()
        lvl_file.close()
        for y in range(len(map_lvl)):
            for x in range(len(map_lvl[y])):
                temp = map_lvl[y]
                x0 = x + 1
                y0 = y + 2
                if temp[x] == "0" and x0 * 32 < W and y0 * 16 < H:
                    newBrick = Brick(x0 * 32, y0 * 16)
                    self.brickList.append(newBrick)

    def show(self):
        self.app.fill((0,0,0))
        self.app.blit(self.bGround, (0, 0))
        self.ball.show(self.app)
        self.paddle.show(self.app)
        b = 0
        while b < len(self.brickList):
            self.brickList[b].show(self.app)
            if self.brickList[b].broken and self.brickList[b].currentAnimation.anim_finished:
                self.brickList.pop(b)
                b -= 1
            b += 1
        for l in self.limits:
            l.show(self.app)
        pg.display.update()

    def update(self):
        if self.startGame:
            key = pg.key.get_pressed()
            if key[pg.K_LEFT]:
                self.paddle.move(-100, self.limits[0], self.limits[1])
            elif key[pg.K_RIGHT]:
                self.paddle.move(100, self.limits[0], self.limits[1])
            self.ball.checkCollisions(self.paddle,self.brickList,self.limits)

    def run(self):
        self.buildLevel("levels/lvl3.txt")
        while not self.appClosed:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.appClosed = True
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_h:
                        utilities.visibleHitbox = ~utilities.visibleHitbox
                    if event.key == pg.K_SPACE:
                        self.startGame = True
            self.update()
            self.show()
            self.FramerateLimit.tick(60)

demo = Arkanoid()
demo.run()

pg.quit()
quit()
