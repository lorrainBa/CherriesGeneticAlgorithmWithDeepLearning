import pygame
from sys import exit
import random
import math
import copy
import tensorflow as tf
from tensorflow import keras
import numpy as np


from brainClass import Brain
from survivorClass import Survivor
from fruitClass import Fruit
pygame.init()

#Get random seed for rand and numpy
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



#Interface ---------------------------------------------------------------------------
screen = pygame.display.set_mode((screenWidth,screenHeight))
pygame.display.set_caption('Runner')
clock = pygame.time.Clock()

gameBackground = pygame.Surface((screenWidth,screenHeight))
gameBackground.fill("Black")
genomeBackground = pygame.Surface((genomeScreenWidth,genomeScreenHeight))
genomeBackground.fill("Grey")


#Button------------------------------------------------------------------------------
class Button:
    """Create a button, then blit the surface in the while loop"""
 
    def __init__(self,screen , text,  pos, font, bg="black", feedback=""):
        self.screen = screen
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
        self.screen.blit(self.surface, (self.x, self.y))
 
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
    screen,
    "Stop drawing",
    pos = (screenWidth-300, screenHeight/2),
    font=30,
    bg="black",
    feedback="You clicked me")
button2 = Button(
    screen,
    "NextRound",
    pos = (screenWidth-300, screenHeight/3),
    font=30,
    bg="black",
    feedback="You clicked me")


#Variable of the props-------------------------------------------------------------------------------
survivorGroup = pygame.sprite.Group()
fruitGroup = pygame.sprite.Group()

meanGenome=None

#Neural network variables----------------------------------------------------------------------------
factorWidthByHeight = gameWidth/gameHeight
widthNormalization = 1/gameWidth
heightNormalization = 1/gameHeight




















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
            """mutationSpeedSize = 0"""
            mutationFieldOfView = 0
            mutationSpeedSize = random.uniform(-0.05,0.05)
            """mutationFieldOfView = random.uniform(-0.05,0.05)"""

            newSpeed = genome["speed"] + 2 * mutationSpeedSize
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
    fruitGroup.update(fruitGroup,survivorGroup)
    survivorGroup.update(fruitGroup,survivorGroup,widthNormalization,heightNormalization)
    
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

    



            











def main():
    
    initRound("firstTime")
    play()




main()








