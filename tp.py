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

# create a class that define all random props in game
class Props(object):
    def __init__(self, name, ppx, ppy):
        self.name=name
        self.ppx=ppx
        self.ppy=ppy

def onAppStart(app):
    app.avatar = 'character-idle.png'# load the avatar image
    # app.platform = 'platform.png'# load the normal platform image
    app.platformWidth,app.platformHeight=140,20
    app.avatarWidth,app.avatarHeight=64,64 # initialize avatar size
    # a list of randomly generated platform, initialize the first one
    app.platformList=[Platform('normal', app.width/2,app.height/2+app.avatarHeight/2)] 
    app.platformTypes=['normal','normal','normal','break', 
                            'bounce','bounce','belt-left','belt-right','stab']
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
    app.jumpSpeed=5 # initial jump speed
    app.move=False # detect whether should move
    app.jump=False # detect whether should jump
    app.gameOver=False # game over status
    app.gameStart=False # if game started
    app.skip,app.skipInit=100,100 # used in generating platforms
    app.difficulty=None
    # if app.difficulty=='easy':
    #     app.skip,app.skipInit=100,100
    # elif app.difficulty=='medium':
    #     app.skip,app.skipInit=80,80
    # elif app.difficulty=='hard':
    #     app.skip,app.skipInit=60,60
    app.life=100 # life system count
    app.level=1 # count the levels of current location
    app.levelCounter=400 # level developed by time
    app.onStab=False # avatar is standing on Stab Platform
    app.gameSuccess=False # if game is succeeded
    # selectDifficultyLevel(app)
    app.upwardVolocity=1
    firstScreenGenerate(app) # this is to generate platforms when game starts
    app.mousePressed=False
    # prop definition
    app.propList=[]
    app.propWidth,app.propHeight=30,30
    app.bulletSpeed=3
    app.haveGun=False
    app.gx=app.cx
    app.gy=app.cy
    # gun bullet direction
    app.dxGun=1

def selectDifficultyLevel(app):
    if app.difficulty=='easy':
        app.upwardVolocity=1 # the everything going upwards speed
    if app.difficulty=='medium':
        app.upwardVolocity=2
    elif app.difficulty=='hard':
        app.upwardVolocity=3

def onKeyPress(app, key):
    if key=='left' or key=='a':
        app.direction=-1
        app.move=True 
    if key=='right' or key=='d':
        app.direction=1
        app.move=True
    if key=="space": # jump 
        jumpMotion(app)
    
def onKeyRelease(app,key):
    if key=='left'or key=='a':
        app.move=False
    if key=='right'or key=='d':
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
                if app.onStab==False:
                    app.life-=5
                    app.onStab==True

            elif(platform.type=='bounce'):
                jumpMotion(app)
                app.life+=1
            elif(platform.type=='break'):
                app.platformList.remove(platform)
                app.life+=1
            elif(platform.type=='belt-left'):
                app.cx-=1
                app.life+=1
            elif(platform.type=='belt-right'):
                app.cx+=1
                app.life+=1
            else:
                app.life+=1
            

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
    for yPos in range(app.height//2+app.avatarWidth//2+app.platformHeight+100, 
                        app.height, app.platformHeight+100):
        # randomly choose a platform type
        randomType=random.choice(app.platformTypes)
        # randomly choose a x location for a platform
        randomX=random.randrange(app.platformWidth/2,app.width-app.platformWidth/2) 
        app.platformList.append(Platform(randomType,randomX, yPos))

# to generate random platforms from bottom when moving upwards
def generatePlatforms(app):
    if app.level>10 and app.level<25:
        app.platformTypes=['normal','normal','break','break', 
                            'bounce','bounce','belt-left','belt-right','stab']
    elif app.level>=25 and app.level<37:
        app.platformTypes=['normal','normal','break','break', 
                            'bounce','bounce','belt-left','belt-right','stab','stab']
    elif app.level>=37:
        app.platformTypes=['normal','bounce','break','break', 
                            'bounce','bounce','belt-left','belt-right','stab','stab']
    randomType=random.choice(app.platformTypes)
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
    # define image sources for each type of platform
    platformNormal='platform.png'
    platformBreak='platform-break.png'
    platformStab='platform-stab.png'
    platformBounce='platform-bounce.png'
    platformBeltLeft='platform-belt-left.png'
    platformBeltRight='platform-belt-right.png'
    # draw different types of platforms
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
        elif platform.type=='belt-left':
            drawImage(platformBeltLeft, platform.px-app.platformWidth/2, 
                        platform.py-app.platformHeight/2)
        elif platform.type=='belt-right':
            drawImage(platformBeltRight, platform.px-app.platformWidth/2, 
                        platform.py-app.platformHeight/2)

def generateProps(app): 
    randomShow=random.choice([True, False,False, False, False])
    if randomShow==True:
        randomType=random.choice(['gun','heart','heart','death'])
        randomX=random.randrange(app.propWidth/2,app.width-app.propWidth/2)
        # randomY=random.randrange(app.height/2,app.height-app.propHeight/2)
        yPos=app.height+app.propHeight
        app.propList.append(Props(randomType,randomX,yPos))

def propCollision(app,prop):
    distance=((prop.ppx-app.cx)**2+(prop.ppy-app.cy)**2)**0.5
    if distance<=app.avatarWidth/2+app.propWidth/2:
        return prop.name
    return None

def collectProp(app):
    for prop in app.propList:
        if propCollision(app,prop)=='gun':
            app.propList.remove(prop)
            app.haveGun=True
        if propCollision(app,prop)=='heart':
            app.propList.remove(prop)
            app.life+=5
        if propCollision(app,prop)=='death':
            app.propList.remove(prop)
            app.life-=15

# this is to draw the bullet of the gun
def drawBubble(app):
    drawCircle(app.gx, app.gy, 10,fill='yellow')

def drawProps(app):
    gun='gun.png'
    heart='heart.png'
    death='death.png'  
    for prop in app.propList:
        if prop.name=='gun':
            drawImage(gun, prop.ppx-app.propWidth/2, prop.ppy-app.propHeight/2)
            if app.haveGun:
                drawBubble(app)
        elif prop.name=='heart':
            drawImage(heart, prop.ppx-app.propWidth/2, prop.ppy-app.propHeight/2)
        elif prop.name=='death':
            drawImage(death, prop.ppx-app.propWidth/2, prop.ppy-app.propHeight/2)

def everythingMoveUpward(app):
    # avatar moves upwards
    selectDifficultyLevel(app)
    if app.level>2:
        acceleration = 0.5
        app.upwardVolocity += acceleration 
    app.cy -= app.upwardVolocity
    #  platforms and props moves upwards
    for platform in app.platformList:
        platform.py-= app.upwardVolocity
    for prop in app.propList:
        prop.ppy -= app.upwardVolocity

# count the level currently in
def levelCount(app):
    app.level+=1
    if app.level>=50:
        app.gameSuccess=True

def onStep(app): # timer event
    if app.gameOver==False or app.gameSuccess==False:
        # imageFlip(app)
        avatarMovement(app)
        borderCollision(app)
        platformCollision(app)
        everythingMoveUpward(app)
        collectProp(app)
        app.skip-=1
        if app.skip==0:
            generatePlatforms(app)
            generateProps(app)
            app.skip=100
        deletePlatforms(app)
        # if app.life<=0:
        #     app.gameOver=True
        app.levelCounter-=1
        if app.levelCounter==0:
            if app.level<10:
                levelCount(app)
                app.levelCounter=300
            elif app.level>=10 and app.level<25:
                levelCount(app)
                app.levelCounter=350
            elif app.level>=25 and app.level<37:
                levelCount(app)
                app.levelCounter=400
            elif app.level>=37:
                levelCount(app)
                app.levelCounter=450
        if app.haveGun and app.mousePressed:
            app.gx+=app.dxGun*app.bulletSpeed

def onMousePress(app,mouseX,mouseY):
    # click the start/restart button to start the game
    if not app.gameStart or  app.gameOver==True or app.gameSuccess==True:
        if(mouseX>app.width/2 and mouseX<app.width/2+50 and
            mouseY>app.height/2+50 and mouseY<app.height/2+70):
            onAppStart(app)
            app.difficulty='medium'
            app.gameStart=True
        if (mouseX>app.width/2-60 and mouseX<app.width/2-10 and
            mouseY>app.height/2+50 and mouseY<app.height/2+70):
            onAppStart(app)
            app.difficulty='easy'
            app.gameStart=True
        if (mouseX>app.width/2+60 and mouseX<app.width/2+110 and
            mouseY>app.height/2+50 and mouseY<app.height/2+70):
            onAppStart(app)
            app.difficulty='hard'
            app.gameStart=True
    else:
        if app.haveGun:
            if mouseX>app.width/2:
                app.dxGun=1
            if mouseX<=app.width/2:
                app.dxGun=-1
            # app.haveGun=False
            app.mousePressed=True

def drawDifficultyButtons(app):
    drawRect(app.width/2, app.height/2+50,50,20,fill='red')
    drawRect(app.width/2-60, app.height/2+50,50,20,fill='red')
    drawRect(app.width/2+60, app.height/2+50,50,20,fill='red')
    drawLabel('Medium',app.width/2+25, app.height/2+60)
    drawLabel('Easy',app.width/2-35, app.height/2+60)
    drawLabel('Hard',app.width/2+85, app.height/2+60)

def drawGameStartUI(app): # game start UI
    drawLabel('Name TBD created by Xinyi Guo', app.width/2, app.height/2)
    drawDifficultyButtons(app)

def drawGameEndUI(app): # game over UI
    drawLabel('you Lost', app.width/2, app.height/2)
    drawDifficultyButtons(app)

def drawGameSuccessUI(app): # game success UI
    drawLabel('you Win!!!', app.width/2, app.height/2)
    drawDifficultyButtons(app)

# temp write the current life value
def drawLife(app):
    drawLabel(f'Life: {app.life}', 50,20, size=20)

# temp write the current level
def drawLevel(app):
    drawLabel(f'Level: {app.level}',app.width/2,30,size=50)

def drawBackground(app):
    background='backgroundDemo.png'
    drawImage(background, app.bgX,app.bgY)

# draw platforms and avatar and score and props and level
def redrawAll(app):
    if app.gameStart==False:
        drawGameStartUI(app)
    else: 
        if app.gameOver==False:
            drawRect(0,0, app.width, app.height, fill='blue')
            drawLife(app)
            drawLevel(app)
            drawPlatforms(app)
            drawProps(app)
            drawImage(app.avatar,app.cx-app.avatarWidth/2,app.cy-app.avatarHeight/2)
        elif app.gameOver==True:
            drawGameEndUI(app)
        if app.gameSuccess==True:
            drawGameSuccessUI(app)
    
# define canvas size
def main():
    runApp(width=480, height=800)

main()