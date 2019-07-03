'''
Created on Jun 25, 2019

@author: Liron
'''

import pygame
import random
from os import path

WIDTH = 480
HEIGHT = 600
FPS = 60

#Colors
WHITE = (255,255,255)
RED = (255,0,0)
YELLOW = (255,255,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
BLACK = (0,0,0)

# Asset folders
game_folder = path.dirname(__file__)
img_dir = path.join(game_folder, "img")
sounds_dir = path.join(game_folder, "sounds")

font_name = pygame.font.match_font("arial")
def draw_text(surface,text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x,y)
    surface.blit(text_surface, text_rect)
    
def newMob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

def draw_health_bar(screen, x, y, shield):

    BAR_WIDTH = 100
    BAR_HEIGHT = 10
    percent_full = (shield / 100) * BAR_WIDTH
    if shield < 0: 
        percent_full = 0
        
    outline = pygame.Rect(x, y, BAR_WIDTH, BAR_HEIGHT)
    health = pygame.Rect(x,y, percent_full, BAR_HEIGHT)
    pygame.draw.rect(screen, GREEN, health)
    pygame.draw.rect(screen, WHITE, outline, 2)

def draw_num_lives(screen, x, y, num_lives):
    image = pygame.transform.scale(player_images[0], (25,19))
    image.set_colorkey(BLACK)
    for i in range(player.num_lives):
        screen.blit(image, (x,y))
        x += 40
        
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_images[0], (50,38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.hit = False
        self.frame = 1
        self.num_cycles = 0 #Tracks how many times invincibility frames have been cycled
        self.last_updated = pygame.time.get_ticks()
        self.num_lives = 3
    
    def update (self):
        #TODO: Make an animation when you die
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        
        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        elif keystate[pygame.K_RIGHT]:
            self.speedx = 5 
        self.rect.x += self.speedx
        
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            
        if self.hit:
            self.invincibility_animation()
        
        if self.shield <= 0:
            self.lose_life()

            
    def invincibility_animation(self):
        now = pygame.time.get_ticks()
        if self.num_cycles == 2:
            self.hit = False
            self.num_cycles = 0
            self.image = pygame.transform.scale(player_images[0], (50,38))
            self.image.set_colorkey(BLACK)
        elif now - self.last_updated > 100:
            self.last_updated = now
            self.image = pygame.transform.scale(player_images[abs(self.frame)], (50,38))
            self.image.set_colorkey(BLACK)
            if self.frame == 0:
                self.num_cycles += 1
            if self.frame == 4:
                self.frame = -4
            self.frame += 1
            
    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        shoot_sound.play()
        
    def got_hit(self):
        if not player.hit:
            player.shield -= hit.radius
            player.hit = True
            player_hit_sound.play()
    
    def lose_life(self):
        player.num_lives -= 1
        if player.num_lives == 0:
            running = False
        else:
            player.shield = 100
            
class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.radius = int(self.rect.width * .85 / 2)
        self.speedy = random.randrange(1,4)
        self.speedx = random.randrange(-3,3)
        self.rot = 0
        self.rot_speed = random.randrange(-8,8)
        self.last_updated = pygame.time.get_ticks()
        self.frame = 0
        self.exploded = False
        
    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_updated > 50:
            self.last_updated = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center
            
    
    def update(self):
        if not self.exploded:
            self.rotate()
            self.rect.y += self.speedy
            self.rect.x += self.speedx
            if self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
                self.rect.x = random.randrange(0, WIDTH - self.rect.width)
                self.rect.y = random.randrange(-150, -100)
                self.speedy = random.randrange(1,8)
                self.speedx = random.randrange(-3,3)
        else:
            self.explode()
    
    def explode(self):
        now = pygame.time.get_ticks()
        if self.frame == 8:
            self.kill()
        
        if now - self.last_updated > 100:
            width = height = self.rect.width if self.rect.width < \
                self.rect.height else self.rect.height
            self.image = pygame.transform.scale(explode_images[self.frame], (width,height))
            self.image.set_colorkey(BLACK)
            self.frame += 1
            self.last_updated = now
        
    
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10
        
    def update(self):
        self.rect.y += self.speedy
        
        #remove bullet if it goes off screen
        if self.rect.bottom > HEIGHT:
            self.kill()
        
        

#initialize pygame and create window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shoot_The_Asteroids!")
clock = pygame.time.Clock()

#Load all game sounds
shoot_sound = pygame.mixer.Sound(path.join(sounds_dir, "Laser_Shoot1.wav"))
shoot_sound.set_volume(.4)

explosion_sounds = [pygame.mixer.Sound(path.join(sounds_dir, "Explosion1.wav")),
                    pygame.mixer.Sound(path.join(sounds_dir, "Explosion2.wav"))]
for sounds in explosion_sounds:
    sounds.set_volume(.4)
    
player_hit_sound = pygame.mixer.Sound(path.join(sounds_dir, "Player_Hit.wav"))
player_hit_sound.set_volume(.4)

#Load background music
pygame.mixer.music.load(path.join(sounds_dir, "Background_Music.ogg"))
pygame.mixer.music.set_volume(0.4)


#Load all game graphics
background = pygame.image.load(path.join(img_dir, "space_background.png")).convert()
background_rect = background.get_rect()
bullet_img = pygame.image.load(path.join(img_dir, "laserRed16.png")).convert()

player_images = []

for i in range(0,5):
    player_path = path.join(img_dir, "playerShip0{}.png".format(i))
    player_images.append(pygame.image.load(player_path).convert())

meteor_images = []
meteor_list = ["meteorBrown_big1.png", "meteorBrown_big2.png", 
                "meteorBrown_med1.png", "meteorBrown_med3.png",
                "meteorBrown_small1.png", "meteorBrown_small2.png",
                "meteorBrown_tiny1.png"]

for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert())
    
explode_images = []

for i in range(9):
    explode_path = path.join(img_dir, "regularExplosion0{}.png".format(i))
    explode_images.append(pygame.image.load(explode_path).convert())

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
score = 0
pygame.mixer.music.play(-1) #-1 indicates to loop forever

for i in range(8):
    newMob()

running = True
while running:
    clock.tick(FPS)
    
    #Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()
    
    #Update
    all_sprites.update()
    mobs.update()
    bullets.update()
    
    #Check to see if a bullet hit an enemy
    for bullet in bullets:
        mob = pygame.sprite.spritecollideany(bullet, mobs)
        if mob and not mob.exploded:
            explosion_sounds[random.randrange(0,2)].play()
            mob.exploded = True
            score += 60 - mob.radius
            newMob()
            bullet.kill()
    
    #Check to see if a mob hit the player
    hits = pygame.sprite.spritecollide(player, mobs, False, pygame.sprite.collide_circle)
    for hit in hits:
        if not player.hit:
            hit.exploded = True
            newMob()

        player.got_hit()
    
    #Display
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 35, WIDTH / 2, 10)
    draw_health_bar(screen, 5, 5, player.shield)
    draw_num_lives(screen, WIDTH - 130, 20, player.num_lives)
    pygame.display.flip()
    
pygame.quit()