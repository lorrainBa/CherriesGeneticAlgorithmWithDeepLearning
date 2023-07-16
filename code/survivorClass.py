from brainClass import Brain
import pygame
import math
import numpy as np

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
        
        self.fruitsInSight = None

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
    def update(self, fruitGroup, survivorGroup,widthNormalization,heightNormalization):
        self.fruitsInSight,self.survivorInSight = self.visionOfTheEnvironment( fruitGroup, survivorGroup)
        """self.mooveRandomNearestFruit(self.fruitsInSight,self.survivorInSight)"""
        self.mooveWithBrain(widthNormalization,heightNormalization,fruitGroup,survivorGroup)
        
        self.checkCollision(fruitGroup,survivorGroup)
    
    def destroy(self):
        self.kill()
    
    def checkCollision(self,fruitGroup,survivorGroup):
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
                survivor.destroy()
                self.score += 3 

    def visionOfTheEnvironment(self,fruitGroup,survivorGroup):
        #Divide by the size because de circle scale on the size of the surviror, that we don't want
        fruitsInSight = pygame.sprite.spritecollide(self, fruitGroup, False, pygame.sprite.collide_circle_ratio(self.genome["fieldOfView"]/math.sqrt(self.genome["size"])))
        survivorInSight = pygame.sprite.spritecollide(self, survivorGroup, False, pygame.sprite.collide_circle_ratio(self.genome["fieldOfView"]))
        return(fruitsInSight,survivorInSight)

 
    def mooveWithBrain(self,widthNormalization,heightNormalization,fruitGroup,survivorGroup):
        currentX,currentY= self.rect.centerx * widthNormalization , self.rect.centery * heightNormalization
        coef,xSpeed, ySpeed = self.neuralNetworkDecision(widthNormalization,heightNormalization,fruitGroup,survivorGroup)
        # *0.5 to slow the survivor maybe 
        xSpeed=xSpeed*coef*0.5 * self.genome["speed"]
        ySpeed=ySpeed*coef*0.5 * self.genome["speed"]

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
        """else:
            if abs(xSpeed) > abs(ySpeed):
                self.rect.centerx += 1 * xSpeed/abs(xSpeed)
            else:
                self.rect.centery += 1 * ySpeed/abs(ySpeed)"""
            
        """if self.rect.centerx <= 0:
            self.rect.centerx = gameWidth 
        elif self.rect.centerx > gameWidth:
            self.rect.centerx = 0 

        elif self.rect.centery <= 0:
            self.rect.centery = gameHeight 
        elif self.rect.centery > gameHeight:
            self.rect.centery = 0 
        """
        

            
    def findNearestFruit(self):
        if self.fruitsInSight:
            distanceNearestFruit = 10000
            xToGo,yToGo = 0,0
            #Find the nearest fruit
            for fruit in self.fruitsInSight:
                distanceFruitSprite = distanceBetweenSprites(self,fruit)
                if distanceFruitSprite < distanceNearestFruit:
                    xToGo,yToGo = fruit.rect.centerx,fruit.rect.centery
                    distanceNearestFruit = distanceFruitSprite
        return(xToGo,yToGo)
    
    def neuralNetworkDecision(self,widthNormalization,heightNormalization,fruitGroup,survivorGroup):

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
        self.fruitsInSight , self.survivorInSight = self.visionOfTheEnvironment(fruitGroup,survivorGroup)
        if self.fruitsInSight:
            xFruit,yFruit=self.findNearestFruit()
            xFruit,yFruit=self.findNearestFruit()
        xFruitN = xFruit * widthNormalization
        yFruitN = yFruit * heightNormalization
        if xFruit >0:
            
            xFruitInput = (xFruit - self.rect.centerx) / (self.genome["fieldOfView"]/math.sqrt(self.genome["size"]))
            yFruitInput = (yFruit - self.rect.centery) / (self.genome["fieldOfView"]/math.sqrt(self.genome["size"]))

        #Different input to make the survivor realise that he's going outside ( didn't work)
        """xInput = (1/((abs(x))**2+0.0001) + 1/((abs(gameWidth-x)+0.0001)**2))/10000
        yInput = (1/((abs(y))**2+0.0001) + 1/((abs(gameHeight-y)+0.0001)**2))/10000"""
        


        """output=self.brain.prediction(np.array([xN,yN,xInput,yInput,xFruitInput,yFruitInput]).reshape(6,1))"""
        output=self.brain.prediction(np.array([xFruitN,yFruitN,xFruitInput,yFruitInput]).reshape(4,1))

        return(output[0][0],output[1][0],output[2][0])
    
def distanceBetweenSprites(sprite1,sprite2):
    return(math.sqrt((sprite1.rect.centerx-sprite2.rect.centerx)**2+(sprite1.rect.centery-sprite2.rect.centery)**2))
