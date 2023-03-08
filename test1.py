import pygame
from sys import exit
import random
import math
import copy

pygame.init()

random.seed()

frameRate = 200

#Variables of the screen and hud
#screen variables
screenWidth = 1000
screenHeight = 700

gameWidth = screenWidth - 400
gameHeight = screenHeight

genomeScreenWidth = screenWidth - gameWidth
genomeScreenHeight = screenHeight

#hud variables
textFont = pygame.font.Font(None,50)




screen = pygame.display.set_mode((screenWidth,screenHeight))
pygame.display.set_caption('Runner')
clock = pygame.time.Clock()

backGround_surface = pygame.Surface((screenWidth,screenHeight))
backGround_surface.fill("Black")

#Variable of the props
survivorGroup = pygame.sprite.Group()
fruitGroup = pygame.sprite.Group()
numberOfSurvivor = 12
numberOfFruit = 50
meanGenome=None


class Survivor(pygame.sprite.Sprite):
    def __init__(self,xPosition,yPosition,genome = {"speed" : 0.5, "size" : 1}):
        super().__init__()
        #Init the genome of the survivor
        self.genome = genome

        #Initialisation of the variable that describe our survivor
        self.image = pygame.transform.scale( pygame.image.load('graphics/player/player_stand.png').convert_alpha()  ,  (30*self.genome["size"],30*self.genome["size"])  )
        self.rect = self.image.get_rect(center = (xPosition,yPosition))
        #Comportment of the survivor
        self.typeOfMovement = "nearestFruit"
        #Variable that describe his comportment and score
        self.score = 0
        self.stamina=20
        self.currentStamina = self.stamina

        
        #Get direction and speed
        xSpeed = random.uniform(-1,1)
        if random.random() < 0.5:
            ySpeed = -(1-abs(xSpeed))
        else:
            ySpeed = (1-abs(xSpeed))
        self.direction = (xSpeed,ySpeed)


    #Update function
    def update(self):
        self.moove()
        self.checkCollision()
    
    def destroy(self):
        self.kill()
    
    def checkCollision(self):
        #Collision with fruit
        listOfFruitInCollision = pygame.sprite.spritecollide(self,fruitGroup,False)
        if listOfFruitInCollision:
            for fruit in listOfFruitInCollision:
                fruit.destroy()
                self.score += 1

        #Collision with survivor
        listOfSurvivorToEat = []
        for survivor in pygame.sprite.spritecollide(self,survivorGroup,False):
            if self.genome["size"] > 1.3*survivor.genome["size"]:
                listOfSurvivorToEat.append(survivor)

        if listOfSurvivorToEat:
            for survivor in listOfSurvivorToEat:
                survivor.destroy()
                self.score += 10 

    #Moove function
    def moove(self):
        if self.typeOfMovement == "nearestFruit":
            distanceNearestFruit = 10000
            xToGo,yToGo = 0,0
            #Find the nearest fruit
            for fruit in fruitGroup:

                distanceFruitSprite = distanceBetweenSprites(self,fruit)
                if distanceFruitSprite < distanceNearestFruit:
                    xToGo,yToGo = fruit.rect.centerx,fruit.rect.centery
                    distanceNearestFruit = distanceFruitSprite

            #Will evaluate the sign of the deplacement
            if self.rect.centerx < xToGo:
                signX=1
            else:
                signX=-1
                
            if self.rect.centery < yToGo:
                signY=1
            else:
                signY=-1

            #Evalue the proportion in speed for x and y      
            # 1 = a + b with avec le coef directeur on obtient pour 1 x on monte de y donc 1 = a + C * a  et a = 1/(1+x) et b = 1-a
            coefDirecteur = abs((self.rect.y-yToGo)/(abs(self.rect.x-xToGo)+1))
            
            xSpeed = self.genome["speed"]/(1+coefDirecteur)
            ySpeed = self.genome["speed"] - xSpeed

            ySpeed *= signY
            xSpeed *= signX
            #Moove the charactezr along his speed but if the speed is too slow it still moove on the x or y randomly
            if (abs(xSpeed) > 0.1 or abs(ySpeed) > 0.1):
                self.rect.centerx += xSpeed*10
                self.rect.centery += ySpeed*10
            else:
                if random.randint(0,1) == 0:
                    self.rect.centerx += signX
                else:
                    self.rect.centery += signY


            
            #Reduce stamina
            # Multiply by ten to get the real speed / Power to make the speed more important maybe exponential  and divide to make it like a variation
            self.currentStamina = self.currentStamina - math.exp((abs(xSpeed) + abs(ySpeed))*10)/1000
            if self.currentStamina < 0:
                self.currentStamina = 0
                self.typeOfMovement = "rest"

        # If he used all his stamina then rest for 10 times
        elif self.typeOfMovement == "rest":
            self.currentStamina += 0.5
            if self.currentStamina >= self.stamina:
                self.typeOfMovement = "nearestFruit"

            """if xDistance > yDistance:
                xSpeed = 1/(xDistance+yDistance) * xDistance/(yDistance)
                ySpeed = 1 - xSpeed
                #Put the real sign
                xSpeed *= signX
                ySpeed *= signY
            else:
                ySpeed = 1/(xDistance+yDistance) * yDistance/(xDistance)
                xSpeed = 1 - ySpeed
                #Put the real sign
                xSpeed *= signX
                ySpeed *= signY"""
            #Moove character
            
            

                

        if type == "random":
            self.rect.centerx += self.direction[0]*2.5
            self.rect.centery += self.direction[1]*2.5

            if self.rect.centerx <= 0:
                self.rect.centerx = gameWidth
            elif self.rect.centerx > gameWidth+25:
                self.rect.centerx = 0

            elif self.rect.centery <= 0:
                self.rect.centery = gameHeight
            elif self.rect.centery > gameHeight:
                self.rect.centery = 0

    

class Fruit(pygame.sprite.Sprite):
    def __init__(self,xPosition,yPosition):
        super().__init__()
        #Initialisation of the variable that describe our fruit
        self.image = pygame.transform.scale( pygame.image.load('graphics/characters/cherries.png').convert_alpha()  ,  (20,20)  )
        self.rect = self.image.get_rect(center = (xPosition,yPosition))


    def update(self):
        pass
    
    def destroy(self):
        self.kill()


    

def initGame(typeOfInit):
    global numberOfSurvivor
    global numberOfFruit
    global meanGenome

    #Spawn survivor and fruits with the old genome depends on their capacity to survive last round
    if typeOfInit == "newRound":
        survivorsGenome=[]
        #Spawn survivor
        #Get more chance to pass your genome when your score is higher

        for OldSurvivor in survivorGroup:
            for i in range (OldSurvivor.score):
                survivorsGenome.append(OldSurvivor.genome)
            OldSurvivor.destroy()

        #Spawn the new survivor with modified genome
        for i in range (numberOfSurvivor):
            xSpawn = random.randint(0,gameWidth)
            ySpawn = random.randint(0,gameHeight)
            genome = random.choice(survivorsGenome)
            mutation = random.uniform(-0.02,0.02)

            newSpeed = genome["speed"] + mutation
            newSize = genome["size"] - mutation*2

            newGenome = {"speed" : newSpeed}
            newGenome["size"] = newSize


            survivorGroup.add(Survivor(xSpawn,ySpawn,newGenome))
    

        
        for j in range(numberOfFruit):
            xSpawn = random.randint(0,gameWidth)
            ySpawn = random.randint(0,gameHeight)
            fruitGroup.add(Fruit(xSpawn,ySpawn))

            
    #Spawn survivor and fruits for the first time randomly
    elif typeOfInit == "firstTime":
        for i in range(numberOfSurvivor):
            xSpawn = random.randint(0,gameWidth)
            ySpawn = random.randint(0,gameHeight)
            survivorGroup.add(Survivor(xSpawn,ySpawn))

        #Spawn fruits
        for j in range(numberOfFruit):
            xSpawn = random.randint(0,gameWidth)
            ySpawn = random.randint(0,gameHeight)
            fruitGroup.add(Fruit(xSpawn,ySpawn))

    #Update the mean genome
    meanGenome = getMeanGenome()




    

def play():
    global frameRate
    ownEvent=None
    while True:

        

        
        

        #If fruits are all gone then set new round
        if len(fruitGroup) == 0:
            ownEvent = "newRound"

        if ownEvent == "newRound":
            pygame.time.wait(200)
            initGame("newRound")
            ownEvent = None


        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                
            
        
        drawGame()
        clock.tick(frameRate)

def drawGame():
    #Background
    screen.blit(backGround_surface, (0,0))
    #Props
    fruitGroup.update()
    fruitGroup.draw(screen)
    survivorGroup.update()
    survivorGroup.draw(screen)
    displayMeanGenome()

    pygame.display.update()

def displayMeanGenome():
    global textFont
    global screenWidth
    global screenHeight
    global genomeScreenWidth
    global genomeScreenHeight

    global meanGenome
    numberOfGen = len(meanGenome)
    pixelForEachGenome = genomeScreenWidth / numberOfGen

    for iterator,(key,value) in enumerate(meanGenome.items()):
        screen.blit(textFont.render( key,True,"White")                  , (screenWidth - genomeScreenWidth + iterator * pixelForEachGenome +50 , genomeScreenHeight -30))
        screen.blit(textFont.render( str(round(value,1)) ,True,"White") , (screenWidth - genomeScreenWidth + iterator * pixelForEachGenome +50 , genomeScreenHeight -80) )
    

def getMeanGenome():
    firstSurvivor = True
    numberOfGenome = 0
    meanOfTheGenome = {}

    for survivor in survivorGroup:
        numberOfGenome += 1
        #Copy the first genom then add all the other one
        if firstSurvivor:
            meanOfTheGenome = copy.deepcopy(survivor.genome)
            firstSurvivor = False
        else:
            for key,value in survivor.genome.items():
                meanOfTheGenome[key] += value


    #Then get the mean of the genome and display it
    for key,value in  meanOfTheGenome.items():
        meanOfTheGenome[key] = value / numberOfGenome

    return(meanOfTheGenome)

    



            



def distanceBetweenSprites(sprite1,sprite2):
    return(math.sqrt((sprite1.rect.centerx-sprite2.rect.centerx)**2+(sprite1.rect.centery-sprite2.rect.centery)**2))








def main():
    
    initGame("firstTime")
    play()

main()





