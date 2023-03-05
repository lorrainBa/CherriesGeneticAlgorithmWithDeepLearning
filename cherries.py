import pygame
from sys import exit
import random
import math
import copy
import tensorflow as tf
from tensorflow import keras
import numpy as np

pygame.init()

random.seed()

frameRate = 60
numberOfSurvivor = 10
numberOfFruit = 30
#Variables of the screen and hud
#screen variables
screenWidth = 1800
screenHeight = 800

gameWidth = screenWidth - 400
gameHeight = screenHeight

genomeScreenWidth = screenWidth - gameWidth
genomeScreenHeight = screenHeight

#hud variables
textFont = pygame.font.Font(None,50)




screen = pygame.display.set_mode((screenWidth,screenHeight))
pygame.display.set_caption('Runner')
clock = pygame.time.Clock()

gameBackground = pygame.Surface((screenWidth,screenHeight))
gameBackground.fill("Black")
genomeBackground = pygame.Surface((genomeScreenWidth,genomeScreenHeight))
genomeBackground.fill("Grey")

#Variable of the props
survivorGroup = pygame.sprite.Group()
fruitGroup = pygame.sprite.Group()

meanGenome=None

#Neural network variables
widthNormalization = 1/gameWidth
heightNormalization = 1/gameHeight

class Survivor(pygame.sprite.Sprite):
    def __init__(self,xPosition,yPosition,genome = {"speed" : 0.5, "size" : 1, "fieldOfView" : 3}):
        super().__init__()
        #Init the genome of the survivor
        self.genome = genome
        #Variable that describe his comportment and score
        self.score = 0
        self.stamina=20
        self.currentStamina = self.stamina
        #Comportment of the survivor
        self.state = "normal"


        #Initialisation of the variable that describe our survivor
        self.image = pygame.transform.scale( pygame.image.load('graphics/player/player_stand.png').convert_alpha()  ,  (30*self.genome["size"],30*self.genome["size"])  )
        self.rect = self.image.get_rect(center = (xPosition,yPosition))

        
        
        
        #Get direction and speed
        xSpeed = random.uniform(-1,1)
        if random.random() < 0.5:
            ySpeed = -(1-abs(xSpeed))
        else:
            ySpeed = (1-abs(xSpeed))
        self.direction = (xSpeed,ySpeed)


    #Update function
    def update(self):
        fruitsInSight,survivorInSight = self.visionOfTheEnvironment()
        self.moove(fruitsInSight,survivorInSight)
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
                """survivor.destroy()
                self.score += 3 """

    def visionOfTheEnvironment(self):
        #Divide by the size because de circle scale on the size of the surviror, that we don't want
        fruitsInSight = pygame.sprite.spritecollide(self, fruitGroup, False, pygame.sprite.collide_circle_ratio(self.genome["fieldOfView"]/math.sqrt(self.genome["size"])))
        survivorInSight = pygame.sprite.spritecollide(self, survivorGroup, False, pygame.sprite.collide_circle_ratio(self.genome["fieldOfView"]))
        return(fruitsInSight,survivorInSight)


    #Moove function
    def moove(self,fruitsInSight,survivorInSight):
    

        if self.state == "exhausted":
            self.currentStamina += 0.5
            if self.currentStamina >= self.stamina:
                self.state = "normal"
                

        elif  fruitsInSight :
            xToGo,yToGo=self.findNearestFruit(fruitsInSight)
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
            coefDirecteur = abs((self.rect.centery-yToGo)/(abs(self.rect.centerx-xToGo)+0.000001))

            xSpeed = self.genome["speed"]/(1+coefDirecteur)
            ySpeed = self.genome["speed"] - xSpeed

            ySpeed *= signY
            xSpeed *= signX
            
            #Moove the charactezr along his speed but if the speed is too slow it still moove on the x or y randomly
            if (abs(xSpeed) > 0.1 or abs(ySpeed) > 0.1):
                self.rect.centerx += xSpeed*10
                self.rect.centery += ySpeed*10
            else:
                if abs(xSpeed) > abs(ySpeed):
                    self.rect.centerx += signX
                else:
                    self.rect.centery += signY



            
            #Reduce stamina
            # Multiply by ten to get the real speed / Power to make the speed more important maybe exponential  and divide to make it like a variation
            self.currentStamina = self.currentStamina - math.exp((abs(xSpeed) + abs(ySpeed))*10)/1000
            if self.currentStamina < 0:
                self.currentStamina = 0
                self.state = "exhausted"


                
        #Moove randomly
        else:

            self.rect.centerx += self.direction[0]*2.5
            self.rect.centery += self.direction[1]*2.5

            if self.rect.centerx <= 0:
                self.rect.centerx = gameWidth 
            elif self.rect.centerx > gameWidth:
                self.rect.centerx = 0 

            elif self.rect.centery <= 0:
                self.rect.centery = gameHeight 
            elif self.rect.centery > gameHeight:
                self.rect.centery = 0 

    def findNearestFruit(self,fruitsInSight):
        if fruitsInSight:
            distanceNearestFruit = 10000
            xToGo,yToGo = 0,0
            #Find the nearest fruit
            for fruit in fruitsInSight:
                distanceFruitSprite = distanceBetweenSprites(self,fruit)
                if distanceFruitSprite < distanceNearestFruit:
                    xToGo,yToGo = fruit.rect.centerx,fruit.rect.centery
                    distanceNearestFruit = distanceFruitSprite
        return(xToGo,yToGo)
    """
    def neuralNetworkDecision(self):
        global widthNormalization
        global heightNormalization
        xN = self.rect.centerx * widthNormalization
        yN = self.rect.centery * heightNormalization 
        xFruitN=0
        yFruitN=0
        fruitsInSight,survivorInSight=self.visionOfTheEnvironment()

        if fruitsInSight:
            xFruitN,yFruitN=self.findNearestFruit(self,fruitsInSight)
            xFruitN *= widthNormalization
            yFruitN *= heightNormalization
        
        model = tf.keras.models.Sequential()
        model.add(tf.keras.layers.Dense(5,activation="relu"))
        model.add(tf.keras.layers.Dense(2,activation="softmax"))

        model.compile(
            loss="sparse_categorical_crossentropy",
            optimizer="sgd",
            metrics=["accuracy"]
        )"""
        
    

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


    

def initRound(typeOfInit):
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
            #Get actual value
            xSpawn = random.randint(0,gameWidth)
            ySpawn = random.randint(0,gameHeight)
            genome = random.choice(survivorsGenome)

            #Generate mutation
            mutationSpeedSize = random.uniform(-0.15,0.15)
            mutationFieldOfView = random.uniform(-0.15,0.15)

            newSpeed = genome["speed"] + mutationSpeedSize
            newSize = genome["size"] - mutationSpeedSize*2
            newFieldOfView = genome["fieldOfView"] + mutationFieldOfView

            #Create new genome with the old one and the mutation
            newGenome = {"speed" : abs(newSpeed), "size" : abs(newSize), "fieldOfView" : newFieldOfView}
            


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
            pygame.time.wait(0)
            initRound("newRound")
            ownEvent = None


        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                
            
        
        drawGame()
        clock.tick(frameRate)

def drawGame():
    #Background
    screen.blit(gameBackground, (0,0))
    screen.blit(genomeBackground, (gameWidth,0))
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
    
    initRound("firstTime")
    play()

class Brain():
    #Number of neuron on first layer
    n1 = 4
    #Numer of neuron on last layer to get the x and y coord
    n2 = 2


    def __init__(self,genome):
        #Get the 
        n0 = len(genome)
        #Number of neuron on first layer
        n1 = 4
        #Numer of neuron on last layer to get the x and y coord
        n2 = 2

        W1 = np.random.randn(n1,n0)
        b1 = np.random.randn(n1,1)
        W2 = np.random.randn(n2,n1)
        b2 = np.random.randn(n2,1)

        #Important variables
        self.parameters = {
            'W1' : W1,
            'b1' : b1,
            'W2' : W2,
            'b2' : b2
        }
        

    def prediction(self,X):

        W1 = self.parameters['W1']
        b1 = self.parameters['b1']
        W2 = self.parameters['W2']
        b2 = self.parameters['b2']

        Z1 = W1.dot(X) + b1
        #relu activation
        A1 = np.maximum(0, Z1)
        Z2 = W2.dot(A1) + b2
        A2 = self.softmax(Z2)

        return(A2)

    def updateNeuralNetworks(self,parameters,mutation):
        W1 = parameters['W1']
        b1 = parameters['b1']
        W2 = parameters['W2']
        b2 = parameters['b2']

        W1 = W1 + mutation
        b1 = b1 + mutation
        W2 = W2 + mutation
        b2 = b2 + mutation

        parameters = {
            'W1' : W1,
            'b1' : b1,
            'W2' : W2,
            'b2' : b2
        }

        return(parameters)

    def softmax(self,X):
        return(np.exp(X)/np.exp(X).sum())



main()





