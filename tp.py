import sys
# print(f'sudo "{sys.executable}" -m pip install pillow')
# print(f'sudo "{sys.executable}" -m pip install requests')
from cmu_cs3_graphics import *
import math, random

# create a class that define the platforms generated (should define type later)
class Platform(object):
    def __init__(self,type,px,py):
        self.type=type
        self.px=px
        self.py=py

def onAppStart(app):
    app.avatar = 'character-idle.png'# load the avatar image
    # app.platform = 'platform.png'# load the normal platform image
    app.platformWidth,app.platformHeight=140,20
    app.avatarWidth,app.avatarHeight=64,64 # initialize avatar size
    app.platformList=[] # a list of randomly generated platform
    app.cx=app.width/2 # start avatar position x
    app.cy=app.height/2 # start avatar position y
    app.direction=1 # x direction
    app.speed=0 # x direction 
    app.maxSpeed=4 # maximum x direction speed for avatar
    app.stepsPerSecond=60 # fps = 100/timer
    # app.lastDirection=app.direction # for flip image track the direction change
    app.xVelocity=0 
    app.yVelocity=0
    app.accel=0.5 # x direction accelration 
    app.friction=0.5 # x direction friction
    app.gravity=0.4 # y direction accelration / gravity
    app.grounded=False # detect whether stay on ground 
    app.ground=app.height/2 # temp ground
    app.jumpSpeed=6 # initial jump speed
    app.move=False # detect whether should move
    app.jump=False # detect whether should jump
    app.gameOver=False # game over status
    app.gameStart=False
    app.skip=50
    app.score=100 # score system count
    app.upwardVolocity=3 # the everything going upwards speed
    firstScreenGenerate(app) # this is to generate platforms when game starts

def onKeyPress(app, key):
    if key=='left':
        app.direction=-1
        app.move=True 
    if key=='right':
        app.direction=1
        app.move=True
    if key=="space": # jump 
        jumpMotion(app)
    
def onKeyRelease(app,key):
    if key=='left':
        app.move=False
    if key=='right':
        app.move=False

def jumpMotion(app):
    if app.grounded:
            app.yVelocity-=app.jumpSpeed # give initial jump speed pointing up
            app.grounded=False # temp

# move left and right with accelration and friction
# give y direction gravity
def avatarMovement(app): 
    app.xVelocity=app.speed*app.direction
    app.cx+=app.xVelocity
    app.cy+=app.yVelocity
    app.yVelocity+=app.gravity # y direction gravity by timer
    #horizontal movement
    if app.move:
        if app.speed<app.maxSpeed:
            # check next speed is larger than the max speed
            if app.speed+app.accel>app.maxSpeed: 
                app.speed=app.maxSpeed # apply constant max speed
            else:
                app.speed+=app.accel # speed up when start moving 
    else: # when moving left/right is not triggered
        if app.speed>0 and app.grounded:
            if app.speed-app.friction<0:
                app.speed=0
            else:
                app.speed-=app.friction # speed down to 0 when stop

def platformCollision(app):
    #temp platform detection
    for platform in app.platformList:
        xDistance = abs(app.cx-platform.px)
        yDistance = platform.py-app.cy
        if (xDistance<=app.platformWidth/2 and yDistance>0 and
            yDistance<=app.platformHeight/2+app.avatarHeight/2):
            app.cy=platform.py-app.platformHeight/2-app.avatarHeight/2
            app.yVelocity=0
            app.grounded=True
            if (platform.type=='stab'):
                app.score-=2
            elif(platform.type=='bounce'):
                jumpMotion(app)
            elif(platform.type=='break'):
                app.platformList.remove(platform)

def imageFlip(app): # flip the avatar when changing direction
    if app.lastDirection==app.direction*-1:
        app.avatar=app.avatar.transpose(Image.FLIP_LEFT_RIGHT)
        app.lastDirection=app.direction

def borderCollision(app):
    # check horizontal border collision
    if (app.cx-app.avatarWidth/2<0):
        app.cx=app.avatarWidth/2
    elif app.cx+app.avatarWidth/2> app.width:
        app.cx=app.width-app.avatarWidth/2
    # check upper and lower border collision, affect game over status
    if app.cy<-app.avatarHeight/2 or app.cy>app.height+app.avatarHeight/2:
        app.gameOver=True

# generate all platforms when initial screen (called on appStart)
def firstScreenGenerate(app):
    for i in range(10):
        randomType=random.choice(['normal','break', 'bounce','stab'])
        randomX=random.randrange(app.platformWidth/2,app.width-app.platformWidth/2) 
        randomY=random.randrange(app.platformHeight/2, app.height-app.platformHeight/2,
                                app.avatarHeight+app.platformHeight+20)
        app.platformList.append(Platform(randomType,randomX, randomY))

# to generate random platforms from bottom when moving upwards
def generatePlatforms(app):
    randomType=random.choice(['normal','break', 'bounce','stab'])
    # randomType='normal'
    randomX=random.randrange(app.platformWidth/2,app.width-app.platformWidth/2) 
    yPos=app.height+ app.platformHeight/2
    app.platformList.append(Platform(randomType,randomX, yPos))

# delete platforms from the list if the platform goes outside the canvas
def deletePlatforms(app):
    for platform in app.platformList:
        if platform.py< -app.platformHeight/2:
            app.platformList.remove(platform)

# draw all platforms from platformList
def drawPlatforms(app):
    platformNormal='platform.png'
    platformBreak='platform-break.png'
    platformStab='platform-stab.png'
    platformBounce='platform-bounce.png'
    for platform in app.platformList:
        if platform.type=='normal':
            drawImage(platformNormal, platform.px-app.platformWidth/2, 
                        platform.py-app.platformHeight/2)
        elif platform.type=='break':
            drawImage(platformBreak, platform.px-app.platformWidth/2, 
                        platform.py-app.platformHeight/2)
        elif platform.type=='stab':
            drawImage(platformStab, platform.px-app.platformWidth/2, 
                        platform.py-app.platformHeight/2)
        elif platform.type=='bounce':
            drawImage(platformBounce, platform.px-app.platformWidth/2, 
                        platform.py-app.platformHeight/2)
           

def everythingMoveUpward(app):
    # avatar moves upwards
    acceleration = 0.001
    app.upwardVolocity += acceleration 
    app.cy -= app.upwardVolocity
    # temp platform moves upwards
    for platform in app.platformList:
        platform.py-= app.upwardVolocity

def onStep(app): # timer event
    # if app.gameOver==False:
        # imageFlip(app)
        avatarMovement(app)
        borderCollision(app)
        platformCollision(app)
        everythingMoveUpward(app)
        app.skip-=1
        if app.skip==0:
            generatePlatforms(app)
            app.skip=50
        deletePlatforms(app)
        if app.score<=0:
            app.gameOver=True

def onMousePress(app,mouseX,mouseY):
    if(mouseX>app.width/2 and mouseX<app.width/2+50 and
        mouseY>app.height/2+50 and mouseY<app.height/2+70):
        onAppStart(app)
        app.gameStart=True

def drawGameStartUI(app):
    drawLabel('Name TBD created by Xinyi Guo', app.width/2, app.height/2)
    drawRect(app.width/2, app.height/2+50,50,20,fill='red')
    drawLabel('Start',app.width/2+25, app.height/2+60)

def drawScore(app):
    drawLabel(f'score: {app.score}', 50,20)
# draw platforms and avatar and score
def redrawAll(app):
    drawGameStartUI(app)
    if app.gameStart==True:
        drawRect(0,0,app.width,app.height, fill='blue')
        drawScore(app)
        drawPlatforms(app)
        drawImage(app.avatar,app.cx-app.avatarWidth/2,app.cy-app.avatarHeight/2)
    # print(app.avatar.size)
    
# define canvas size
def main():
    runApp(width=480, height=800)

main()