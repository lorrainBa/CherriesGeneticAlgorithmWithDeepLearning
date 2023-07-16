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
np.random.seed()

#Parameter of the simulation
frameRate = 60
numberOfSurvivor = 10
numberOfFruit = 200

generationNumber=0

showSimultation = True
ownEvent=None
#Variables of the screen and hud
#screen variables
screenWidth = 1400
screenHeight = 700

gameWidth = screenWidth - 400
gameHeight = screenHeight

genomeScreenWidth = screenWidth - gameWidth
genomeScreenHeight = screenHeight

#hud variables
textFont = pygame.font.Font(None,50)



#Interface -------
screen = pygame.display.set_mode((screenWidth,screenHeight))
pygame.display.set_caption('Runner')
clock = pygame.time.Clock()

gameBackground = pygame.Surface((screenWidth,screenHeight))
gameBackground.fill("Black")
genomeBackground = pygame.Surface((genomeScreenWidth,genomeScreenHeight))
genomeBackground.fill("Grey")
#Button
class Button:
    """Create a button, then blit the surface in the while loop"""
 
    def __init__(self, text,  pos, font, bg="black", feedback=""):
        self.x, self.y = pos
        self.font = pygame.font.SysFont("Arial", font)
        self.name = text
        if feedback == "":
            self.feedback = "text"
        else:
            self.feedback = feedback
        self.change_text(text, bg)
 
    def change_text(self, text, bg="black"):
        """Change the text whe you click"""
        self.text = self.font.render(text, 1, pygame.Color("White"))

        self.size = self.text.get_size()
        self.surface = pygame.Surface(self.size)
        self.surface.fill(bg)
        self.surface.blit(self.text, (0, 0))
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])
 
    def show(self):
        screen.blit(self.surface, (self.x, self.y))
 
    def click(self, event):
        global showSimultation
        global ownEvent
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(x, y):
                    if self.name == "Stop drawing":
                        if showSimultation:
                            showSimultation = False
                        else:
                            showSimultation = True
                    elif self.name == "NextRound":
                        ownEvent ="newRound"


button1 = Button(
    "Stop drawing",
    (screenWidth-300, screenHeight/2),
    font=30,
    bg="black",
    feedback="You clicked me")
button2 = Button(
    "NextRound",
    (screenWidth-300, screenHeight/3),
    font=30,
    bg="black",
    feedback="You clicked me")


#Variable of the props
survivorGroup = pygame.sprite.Group()
fruitGroup = pygame.sprite.Group()

meanGenome=None

#Neural network variables
factorWidthByHeight = gameWidth/gameHeight
widthNormalization = 1/gameWidth
heightNormalization = 1/gameHeight

class Brain():
    #Number of neuron on first layer
    n1 = 3
    #Numer of neuron on last layer to get the x and y coord
    n2 = 2
    #Numer of neuron on last layer to get the output (coef,xspeed,ypseed)
    n3 = 3

    def __init__(self,numberOfBrainCaptor, brainParameters = False):
        #Get the number of parameters
        n0 = numberOfBrainCaptor+2
        #Number of neuron on first layer
        n1 = self.n1
        #Numer of neuron on last layer to get the x and y coord
        n2 = self.n3
        #Number of parameters on the second layer
        n3 = self.n1
        self.brainParameters = {}

        if brainParameters == False:
            W1 = np.random.randn(n1,n0)
            b1 = np.random.randn(n1,1)

            W2 = np.random.randn(n3,n1)
            b2 = np.random.randn(n3,1)

            W3 = np.random.randn(n2,n3)
            b3 = np.random.randn(n2,1)

            
            #Important variables
            self.brainParameters = {
                'W1' : W1,
                'b1' : b1,
                'W2' : W2,
                'b2' : b2,
                'W3' : W3,
                'b3' : b3
            }

        else:
            self.brainParameters = brainParameters

    def prediction(self,X):

        
        """print("parametres",self.brainParameters)"""
        W1 = self.brainParameters['W1']
        b1 = self.brainParameters['b1']
        W2 = self.brainParameters['W2']
        b2 = self.brainParameters['b2']
        W3 = self.brainParameters['W3']
        b3 = self.brainParameters['b3']
        
        
        Z1 = W1.dot(X) + b1
        


        #relu activation
        """A1 = 1 / (1+np.exp(-Z1))"""
        """print(" A1", A1)"""

        Z2 = W2.dot(Z1) + b2
        

        """A2 = 1 / (1+np.exp(-Z2))"""
        """print(" A2", A2)"""

        Z3 = W3.dot(Z2) + b3
        
        A3=Z3
        #Softmax activation
        """A3 = np.tanh(Z3)"""
        
        """A20 = A3[0][0] /2
        A21 = A3[1][0] /2"""
        temp = abs(A3[0][0])
        if temp >1:
            A20 = 1
        else:
            A20 = abs(A3[0][0])
        
        A21 = A3[1][0] / (abs(A3[1][0])+abs(A3[2][0]))
        A22 = A3[2][0] / (abs(A3[1][0])+abs(A3[2][0]))
        A3[0][0] = A20
        A3[1][0]= A21
        A3[2][0]= A22

        """print("entrée", X)
        print("w1 dot",W1.dot(X))
        print("b1", b1)
        print(" som", Z1)
        print(" Z2", Z2)
        print(" Z3", Z3)
        print("sortieNormalised", A3)"""
        return(A3)

    def updateNeuralNetworks(self,parameters,mutation):
        W1 = self.brainParameters['W1']
        b1 = self.brainParameters['b1']
        W2 = self.brainParameters['W2']
        b2 = self.brainParameters['b2']

        W1 = W1 + mutation
        b1 = b1 + mutation
        W2 = W2 + mutation
        b2 = b2 + mutation

        self.brainParameters = {
            'W1' : W1,
            'b1' : b1,
            'W2' : W2,
            'b2' : b2
        }


    def softmax(self,X):


        return(np.exp(X)/np.exp(X).sum())

    def getBrainParameters(self):
        return(self.brainParameters)



class Survivor(pygame.sprite.Sprite):
    def __init__(self,xPosition,yPosition,genome = {"speed" : 0.5, "size" : 1, "fieldOfView" : 3}, brain = False):
        super().__init__()
        #Init the genome of the survivor
        self.genome = genome
        #Init of the neural network model
        self.brain = Brain(4,brain)
        """
        self.model = tf.keras.models.Sequential()
        self.model.add(tf.keras.layers.Dense(5,activation="relu"))
        self.model.add(tf.keras.layers.Dense(2,activation="softmax"))
        model.compile(
            loss="sparse_categorical_crossentropy",
            optimizer="sgd",
            metrics=["accuracy"]
        )"""

        #Variable that describe his comportment and score
        self.score = 10
        self.stamina=20
        self.currentStamina = self.stamina
        #Comportment of the survivor
        self.state = "normal"


        #Initialisation of the variable that describe our survivor in pygame (image and rect)
        self.image = pygame.transform.scale( pygame.image.load('graphics/player/player_stand.png').convert_alpha()  ,  (30*self.genome["size"],30*self.genome["size"])  )
        self.rect = self.image.get_rect(center = (xPosition,yPosition))

        
        
        
        """
        #Get random direction and speed
        xSpeed = random.uniform(-1,1)
        if random.random() < 0.5:
            ySpeed = -(1-abs(xSpeed))
        else:
            ySpeed = (1-abs(xSpeed))
        self.direction = (xSpeed,ySpeed)"""


    #Update function
    def update(self):
        fruitsInSight,survivorInSight = self.visionOfTheEnvironment()
        """self.mooveRandomNearestFruit(fruitsInSight,survivorInSight)"""
        self.mooveWithBrain()
        
        self.checkCollision()
    
    def destroy(self):
        self.kill()
    
    def checkCollision(self):
        #Collision with fruit
        listOfFruitInCollision = pygame.sprite.spritecollide(self,fruitGroup,False)
        if listOfFruitInCollision:
            for fruit in listOfFruitInCollision:
                fruit.destroy()
                self.score += 50

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
    def mooveRandomNearestFruit(self,fruitsInSight,survivorInSight):
    
    

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
 
    def mooveWithBrain(self):
        currentX,currentY= self.rect.centerx * widthNormalization , self.rect.centery * heightNormalization
        coef,xSpeed, ySpeed = self.neuralNetworkDecision()
        xSpeed=xSpeed*coef*0.5
        ySpeed=ySpeed*coef*0.5
        """xSpeed = (xSpeed - 0.5)*2
        ySpeed = (ySpeed - 0.5)*2"""
        """if xSpeed <0.5:
            xSign = -1
        else:
            xSign =1
        if ySpeed <0.5:
            ySign = -1
        else:
            ySign = 1
        coefDirecteur = ySpeed/(xSpeed+0.000001)

        xSpeed = self.genome["speed"]/(1+coefDirecteur) 
        ySpeed = self.genome["speed"] - xSpeed
        xSpeed *= xSign
        ySpeed *= ySign
"""

        

        #Moove the charactezr along his speed but if the speed is too slow it still moove on the x or y randomly
        if (abs(xSpeed) > 0.1 or abs(ySpeed) > 0.1):
            self.rect.centerx += xSpeed*10
            self.rect.centery += ySpeed*10
        else:
            """if abs(xSpeed) > abs(ySpeed):
                self.rect.centerx += signX
            else:
                self.rect.centery += signY
            """
        """if self.rect.centerx <= 0:
            self.rect.centerx = gameWidth 
        elif self.rect.centerx > gameWidth:
            self.rect.centerx = 0 

        elif self.rect.centery <= 0:
            self.rect.centery = gameHeight 
        elif self.rect.centery > gameHeight:
            self.rect.centery = 0 
        """
        

            
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
    
    def neuralNetworkDecision(self):
        global widthNormalization
        global heightNormalization
        #Get survivor normalized position
        x = self.rect.centerx
        y = self.rect.centery
        xN = self.rect.centerx * widthNormalization
        yN = self.rect.centery * heightNormalization 
        xFruitInput = 0
        yFruitInput = 0
        #Get nearestfruit normalized position
        xFruit=0
        yFruit=0
        fruitsInSight,survivorInSight=self.visionOfTheEnvironment()
        if fruitsInSight:
            xFruit,yFruit=self.findNearestFruit(fruitsInSight)
            xFruit,yFruit=self.findNearestFruit(fruitsInSight)
        xFruitN = xFruit * widthNormalization
        yFruitN = yFruit * heightNormalization
        if xFruit >0:
            
            xFruitInput = (xFruit - self.rect.centerx) / (self.genome["fieldOfView"]/math.sqrt(self.genome["size"]))
            yFruitInput = (yFruit - self.rect.centery) / (self.genome["fieldOfView"]/math.sqrt(self.genome["size"]))

        xInput = (1/((abs(x))**2+0.0001) + 1/((abs(gameWidth-x)+0.0001)**2))/10000
        

        yInput = (1/((abs(y))**2+0.0001) + 1/((abs(gameHeight-y)+0.0001)**2))/10000
        


        """output=self.brain.prediction(np.array([xN,yN,xInput,yInput,xFruitInput,yFruitInput]).reshape(6,1))"""
        output=self.brain.prediction(np.array([xFruitN,yFruitN,xFruitInput,yFruitInput]).reshape(4,1))

        return(output[0][0],output[1][0],output[2][0])
    









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

            #Verify if the survivor is on the screen or outside to change his score
            if OldSurvivor.rect.centerx <= 0:
                OldSurvivor.score =1
            elif OldSurvivor.rect.centerx > gameWidth:
                OldSurvivor.score =1

            elif OldSurvivor.rect.centery <= 0:
                OldSurvivor.score =1
            elif OldSurvivor.rect.centery > gameHeight:
                OldSurvivor.score =1


            for i in range (OldSurvivor.score):
                survivorsGenome.append((OldSurvivor.genome,copy.deepcopy(OldSurvivor.brain.brainParameters)))
            OldSurvivor.destroy()

        #Spawn the new survivor with modified genome

        for i in range (numberOfSurvivor):
            #Get actual value
            xSpawn = random.randint(0,gameWidth)
            ySpawn = random.randint(0,gameHeight)
            genome,brain = random.choice(survivorsGenome)
        
            weightMutated,brainMutation = random.choice(list(brain.items()))
            for i in range (4):
                brainMutation[random.randint(0,len(brainMutation)-1)] += random.uniform(-0.05,0.05)
                brain[weightMutated] = brainMutation
            
            


            #Generate mutation
            mutationSpeedSize = 0
            mutationFieldOfView = 0
            """mutationSpeedSize = random.uniform(-0.15,0.15)
            mutationFieldOfView = random.uniform(-0.15,0.15)"""

            newSpeed = genome["speed"] + mutationSpeedSize
            newSize = genome["size"] - mutationSpeedSize*2
            newFieldOfView = genome["fieldOfView"] + mutationFieldOfView

            #Create new genome with the old one and the mutation
            newGenome = {"speed" : abs(newSpeed), "size" : abs(newSize), "fieldOfView" : newFieldOfView}
            


            survivorGroup.add(Survivor(xSpawn,ySpawn,newGenome,brain))
    

        fruitGroup.empty()
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
    global showSimultation
    global frameRate
    global ownEvent
    global generationNumber
    timeOfRound = 0
    while True:
        timeOfRound += 1
        if timeOfRound > 1000:
            ownEvent = "newRound"

        

        
        

        #If fruits are all gone then set new round
        if len(fruitGroup) == 0:
            ownEvent = "newRound"

        if ownEvent == "newRound":
            generationNumber += 1
            timeOfRound = 0
            pygame.time.wait(0)
            initRound("newRound")
            ownEvent = None


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            button1.click(event)
            button2.click(event)                
        
        updateGame()
        if showSimultation:
            drawGame()
            clock.tick(frameRate)

def updateGame():
    #Props
    fruitGroup.update()
    survivorGroup.update()
    
def drawGame():
    #Background
    screen.blit(gameBackground, (0,0))
    screen.blit(genomeBackground, (gameWidth,0))
    fruitGroup.draw(screen)
    survivorGroup.draw(screen)
    button1.show()
    button2.show()
    displayMeanGenome()
    pygame.display.update()

def displayMeanGenome():
    global textFont
    global screenWidth
    global screenHeight
    global genomeScreenWidth
    global genomeScreenHeight
    global generationNumber

    global meanGenome
    numberOfGen = len(meanGenome)
    pixelForEachGenome = genomeScreenWidth / numberOfGen

    for iterator,(key,value) in enumerate(meanGenome.items()):
        screen.blit(textFont.render( "Generation: "+str(generationNumber) ,True,"White"), (gameWidth+30   ,30))
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




main()





