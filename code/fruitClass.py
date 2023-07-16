import pygame

class Fruit(pygame.sprite.Sprite):
    def __init__(self,xPosition,yPosition):
        super().__init__()
        #Initialisation of the variable that describe our fruit
        self.image = pygame.transform.scale( pygame.image.load('graphics/characters/cherries.png').convert_alpha()  ,  (20,20)  )
        self.rect = self.image.get_rect(center = (xPosition,yPosition))


    def update(self, fruitGroup, survivorGroup):
        pass
    
    def destroy(self):
        self.kill()


