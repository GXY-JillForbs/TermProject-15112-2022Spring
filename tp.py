import sys
from cmu_cs3_graphics import *
from PIL import Image, ImageDraw
import math, random
# all image resources are created by myself, not online resources

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
    # initialize avatar information
    avatarInitialization(app)
    # initialize platforms information
    platformInitialization(app)
    # initialize avatar movement values
    avatarMovementValues(app)
    app.stepsPerSecond=60 # general timer
    # all game status values
    gameStatusValues(app)
    # difficulty level button drawing information
    difficultyButtonInfo(app)
    app.difficulty=None

    app.skip=100 # used in generating platforms
    app.upwardVolocity=1 # speed of moving upward (init)
    # initialize top margin info
    app.topStab=Image.open('topMargin.png')
    app.topMargin=app.topStab.height
    app.topStab=CMUImage(app.topStab)

    app.levelCounter=400 # level developed by time
    app.onStab=False # avatar is standing on Stab Platform

    firstScreenGenerate(app) # this is to generate platforms when game starts
    # prop definition
    app.propList=[]
    app.propGeneral=Image.open('bomb.png')
    app.propWidth,app.propHeight=app.propGeneral.width, app.propGeneral.height
    # bomb status
    app.haveBomb=False
    # generate background whenever game starts
    backgroundGeneration(app)

def avatarInitialization(app):
    # draw avatar Image using local directory
    app.avatar= Image.open('character-idle.png')
    app.avatarWidth,app.avatarHeight=app.avatar.width, app.avatar.height 
    # get avatar facing left and right 
    app.avatarLeft = app.avatar.transpose(Image.FLIP_LEFT_RIGHT)
    app.avatarRight=app.avatarLeft.transpose(Image.FLIP_LEFT_RIGHT)
    # convert to CMU image
    app.avatar = CMUImage(app.avatar)
    app.avatarLeft=CMUImage(app.avatarLeft)
    app.avatarRight=CMUImage(app.avatarRight)

def platformInitialization(app):
    # get platform uniformed size
    app.platformStandard=Image.open('platform.png')
    app.platformWidth,app.platformHeight=app.platformStandard.width, app.platformStandard.height
    # a list of randomly generated platform, initialize the first one
    app.platformList=[Platform('normal', app.width/2,app.height/2+app.avatarHeight/2)] 
    app.platformTypes=['normal','normal','normal','break', 
                            'bounce','bounce','belt-left','belt-right','stab']

def avatarMovementValues(app):
    app.cx=app.width/2 # start avatar position x
    app.cy=app.height/2 # start avatar position y
    app.direction=1 # x direction
    app.speed=0 # x direction 
    app.maxSpeed=4 # maximum x direction speed for avatar
    app.lastDirection=app.direction # for flip image track the direction change
    app.xVelocity=0 
    app.yVelocity=0
    app.accel=0.5 # x direction accelration 
    app.friction=0.5 # x direction friction
    app.gravity=0.4 # y direction accelration / gravity
    app.grounded=False # detect whether stay on ground 
    app.jumpSpeed=5 # initial jump speed
    app.move=False # detect whether should move
    app.jump=False # detect whether should jump

def gameStatusValues(app):
    app.gameOver=False # game over status
    app.gameStart=False # if game started
    app.gameSuccess=False # if game is succeeded
    app.life=1000 # life system count
    app.level=1 # count the levels of current location
    app.lifeBar=app.life

# reference generating worley noice: https://pastebin.com/0U0rCKee
# following a tutorial of the algorithm https://thebookofshaders.com/12/
def backgroundGeneration(app):
    # initialize background image size
    bgWidth, bgHeight = app.width//4, app.height//4 
    image = Image.new("RGB", (bgWidth, bgHeight))
    draw = ImageDraw.Draw(image)
    pixels = image.load()
    totalSeeds = 100 # the number of seed points
    m = 0 # random.randrange(0, totalSeeds) 
    # generate all the seed positions into lists
    seedsX = []
    seedsY = []
    for i in range(totalSeeds):
        seedsX.append(random.randrange(0,bgWidth))
        seedsY.append(random.randrange(0,bgHeight))

    # find max distance
    maxDistance = 0.0
    for y in range(bgHeight):
        for x in range(bgWidth):
            # create a sorted list of distances to all seed points
            dists = []
            for i in range(totalSeeds):
                distance=((seedsX[i]-x)**2+ (seedsY[i] - y)**2)**0.5
                dists.append(distance)
            dists.sort()
            if dists[m] > maxDistance: 
                maxDistance = dists[m]

    # paint
    for y in range(bgHeight):
        for x in range(bgWidth):
            # create a sorted list of distances to all seed points
            dists = []
            for i in range(totalSeeds):
                distance=((seedsX[i]-x)**2+ (seedsY[i] - y)**2)**0.5
                dists.append(distance)
            dists.sort()
            c = int(round(255 * dists[m] / maxDistance))
            pixels[x, y] = (190, 130, c) 
    # save the image to local directory and for redrawAll
    image.save("background.png", "PNG")

def selectDifficultyLevel(app):
# to select difficulty level from game beginning
    if app.difficulty=='easy':
        app.upwardVolocity=1 # the everything going upwards speed
    elif app.difficulty=='medium':
        app.upwardVolocity=1.5
    elif app.difficulty=='hard':
        app.upwardVolocity=2
        
# press left / a to move left, press right / d to move right
# press space to jump
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

# for space jump and bounce platform
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
            # if avatar is in bomb status
            if app.haveBomb:
                app.platformList.remove(platform)
                app.haveBomb=False
            # each types of platforms has different effects
            if (platform.type=='stab'):
                app.onStab=True
                app.life-=3
            
            elif(platform.type=='bounce'):
                jumpMotion(app)
                app.life+=1
            elif(platform.type=='break'):
                if app.haveBomb==False:
                    app.platformList.remove(platform)
                app.life+=1
            elif(platform.type=='belt-left'):
                app.cx-=1
            elif(platform.type=='belt-right'):
                app.cx+=1
            else:
                app.life+=1
            
def checkLifeStatus(app):
    if app.life>1000:
        app.life=1000
    elif app.life<0:
        app.life=0  

def imageFlip(app): # flip the avatar when changing direction
    if app.lastDirection == app.direction * -1:
        if app.lastDirection==1:
            app.avatar=app.avatarLeft
            app.lastDirection=app.direction
        elif app.lastDirection==-1:
            app.avatar=app.avatarRight
            app.lastDirection=app.direction

def borderCollision(app):
    # check horizontal border collision
    if (app.cx-app.avatarWidth/2<0):
        app.cx=app.avatarWidth/2
    elif app.cx+app.avatarWidth/2> app.width:
        app.cx=app.width-app.avatarWidth/2
    # check upper and lower border collision, affect game over status
    if app.cy<app.avatarHeight/2+app.topMargin-10 or app.cy>app.height+app.avatarHeight/2:
        app.gameOver=True

# generate all platforms when initial screen (called on appStart)
def firstScreenGenerate(app):
    for yPos in range(app.height//2+app.avatarWidth//2+app.platformHeight+100, 
                        app.height, app.platformHeight+80):
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
    platformNormal=Image.open('platform.png')
    platformBreak=Image.open('platform-break.png')
    platformStab=Image.open('platform-stab.png')
    platformBounce=Image.open('platform-bounce.png')
    platformBeltLeft=Image.open('platform-belt-left.png')
    platformBeltRight=Image.open('platform-belt-right.png')
    platformNormal=CMUImage(platformNormal)
    platformBreak=CMUImage(platformBreak)
    platformStab=CMUImage(platformStab)
    platformBounce=CMUImage(platformBounce)
    platformBeltLeft=CMUImage(platformBeltLeft)
    platformBeltRight=CMUImage(platformBeltRight)
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
    # create less appearance of props
    randomShow=random.choice([True, False,False, False, False])
    if randomShow==True:
        randomType=random.choice(['bomb','heart','heart','death'])
        randomX=random.randrange(app.propWidth/2,app.width-app.propWidth/2)
        yPos=app.height+app.propHeight+40
        app.propList.append(Props(randomType,randomX,yPos))

def propCollision(app,prop):
# if collide with a prop, return the name of the prop, else return None
    distance=((prop.ppx-app.cx)**2+(prop.ppy-app.cy)**2)**0.5
    if distance<=app.avatarWidth/2+app.propWidth/2:
        return prop.name
    return None

def collectProp(app):
# all effects of colliding with a type of prop
    for prop in app.propList:
        if propCollision(app,prop)=='bomb':
            app.propList.remove(prop)
            app.haveBomb=True
        if propCollision(app,prop)=='heart':
            app.propList.remove(prop)
            app.life*=1.25
        if propCollision(app,prop)=='death':
            app.propList.remove(prop)
            app.life*=0.5

def drawBomb(app):
# when hitting with a bomb, there is a bomb image effect behind the avatar
    bombGlow=Image.open('bombGlow.png')
    bombGlowWidth,bombGlowHeight=bombGlow.width,bombGlow.height
    bombGlow=CMUImage(bombGlow)
    if app.haveBomb:
        drawImage('bombGlow.png',app.cx-bombGlowWidth/2,app.cy-bombGlowHeight/2)

def drawProps(app):
# draw every type of props
    bomb='bomb.png'
    heart='heart.png'
    death='death.png'  
    for prop in app.propList:
        if prop.name=='bomb':
            drawImage(bomb, prop.ppx-app.propWidth/2, prop.ppy-app.propHeight/2)
        elif prop.name=='heart':
            drawImage(heart, prop.ppx-app.propWidth/2, prop.ppy-app.propHeight/2)
        elif prop.name=='death':
            drawImage(death, prop.ppx-app.propWidth/2, prop.ppy-app.propHeight/2)

def everythingMoveUpward(app):
    # avatar moves upwards
    if app.level>5:
        acceleration = 0.0001
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
        imageFlip(app)
        avatarMovement(app)
        borderCollision(app)
        platformCollision(app)
        everythingMoveUpward(app)
        checkLifeStatus(app)
        collectProp(app)
        # for prop generation
        app.skip-=1
        if app.skip==0:
            generatePlatforms(app)
            generateProps(app)
            app.skip=100
        deletePlatforms(app)
        if app.life<=0:
            app.gameOver=True
        # to count the levels using timer
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

def onMousePress(app,mouseX,mouseY):
    # click the start/restart button to start the game
    if not app.gameStart or  app.gameOver==True or app.gameSuccess==True:
        if(mouseX>178 and mouseX<178+app.buttonWidth and
            mouseY>643 and mouseY<643+app.buttonHeight):
            onAppStart(app)
            app.difficulty='medium'
            app.gameStart=True
        if (mouseX>26 and mouseX<26+app.buttonWidth and
            mouseY>643 and mouseY<643+app.buttonHeight):
            onAppStart(app)
            app.difficulty='easy'
            app.gameStart=True
        if (mouseX>330 and mouseX<330+app.buttonWidth and
            mouseY>643 and mouseY<643+app.buttonHeight):
            onAppStart(app)
            app.difficulty='hard'
            app.gameStart=True
    # reset all values regarding difficulty
    selectDifficultyLevel(app)

def difficultyButtonInfo(app):
    app.easyButton = Image.open('easyButton.png')
    app.mediumButton = Image.open('mediumButton.png')
    app.hardButton = Image.open('hardButton.png')
    app.buttonWidth, app.buttonHeight=app.easyButton.width, app.easyButton.height
    # convert to CMU image
    app.easyButton = CMUImage(app.easyButton)
    app.mediumButton = CMUImage(app.mediumButton)
    app.hardButton = CMUImage(app.hardButton)

def drawDifficultyButtons(app):
    drawImage(app.easyButton, 26, 643)
    drawImage(app.mediumButton, 178, 643)
    drawImage(app.hardButton, 330, 643)

    
def drawGameStartUI(app): # game start UI
    title = Image.open('title.png')
    # convert to CMU image
    title = CMUImage(title)
    drawImage(title, 0, 0)
    drawDifficultyButtons(app)

def drawGameEndUI(app): # game over UI
    lose = Image.open('lose.png')
    # convert to CMU image
    lose = CMUImage(lose)
    drawImage(lose, 0, 0)
    drawDifficultyButtons(app)

def drawGameSuccessUI(app): # game success UI
    win = Image.open('win.png')
    # convert to CMU image
    win = CMUImage(win)
    drawImage(win, 0, 0)
    drawDifficultyButtons(app)

# temp write the current life value
def drawLife(app):
    drawLabel(f'Life: ', 30,43, size=20)
    drawRect(48,33,100,20,fill='grey')
    drawRect(48,33,app.life*0.1,20,fill='yellow')


# temp write the current level
def drawLevel(app):
    drawLabel(f'Level: {app.level}',app.width-20,40,size=30,align='right')

def drawBackground(app):
    background="background.png"
    drawImage(background, 0,0,width=app.width,height=app.height)

# draw platforms and avatar and score and props and level
def redrawAll(app):
    drawBackground(app)
    if app.gameStart==False:
        drawGameStartUI(app)
    else: 
        if app.gameOver==False and app.gameSuccess==False:
            # drawRect(0,0, app.width, app.height, fill='blue')
            drawPlatforms(app)
            drawProps(app)
            drawBomb(app)
            drawImage(app.avatar,app.cx-app.avatarWidth/2,app.cy-app.avatarHeight/2)
            drawImage(app.topStab,0,0)
            drawLife(app)
            drawLevel(app)
        elif app.gameOver==True:
            drawGameEndUI(app)
        if app.gameSuccess==True:
            drawGameSuccessUI(app)
    
# define canvas size
def main():
    runApp(width=480, height=800)

main()