'''
Created on Jun 25, 2019

@author: Liron
'''

import pygame
import random
from os import path
from operator import itemgetter
import pickle

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
AUTO_FIRE_COLOR = (237, 240, 96) #Color of text when player gets autofire powerup
HEALTH_COLOR = (151, 255, 110) #Color of text when player gets a health powerup

# Asset folders
game_folder = path.dirname(__file__)
img_dir = path.join(game_folder, "img")
sounds_dir = path.join(game_folder, "sounds")

font_name = pygame.font.match_font("arial")

def show_game_over_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "SHOOT THE ASTEROIDS!", WHITE, 32, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Arrow keys to move, Space to fire", \
               WHITE, 22, WIDTH / 2, HEIGHT / 2)
#     draw_text(screen, "Press any key to begin", WHITE, 22, WIDTH / 2, HEIGHT - HEIGHT / 4)
    draw_menu_buttons()
    pygame.mixer.music.load(background_music["menu"])
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1) #-1 indicates to loop forever
    pygame.display.flip()
    waiting = True
    pos = (0,0) #Track position of mouse to see if buttons are clicked
    high_scores = []
    scores_dir = path.join(game_folder, "scores")

#     with open(path.join(scores_dir, "highscores.txt"), 'r') as f:
#         high_scores = pickle.load(f)
        
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos() #Used to see if button has been clicked
        
        #Check to see if button has been clicked
        for button in main_menu_buttons:
            if button.rect.collidepoint(pos):
                if button.type == "start":
                    waiting = False
                elif button.type == "high scores":
                    pass
                elif button.type == "quit":
                    pygame.quit()
                    exit() 
            
    
def draw_menu_buttons():
    for button in main_menu_buttons:
        image = pygame.transform.scale(button.image, (121, 60))
        screen.blit(image, (button.rect.x, button.rect.y))

def draw_text(surface, text, color, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x,y)
    surface.blit(text_surface, text_rect)
    
def newMob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)
    
def new_powerup():
    p = Powerup()
    all_sprites.add(p)
    powerups.add(p)

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
        self.hit_frame = 1
        self.num_cycles = 0 #Tracks how many times invincibility frames have been cycled
        self.last_updated = pygame.time.get_ticks()
        self.num_lives = 3
        self.respawning = False
        self.respawn_frame = 0
        self.powerup_type = None
        self.powerup_time = -1 #Used as a timer for how long shield and auto fire are active
        self.powerup_shot_time = pygame.time.get_ticks() #regulates how fast auto fire shoots
        self.display_health_text = False
    
    def update (self):
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
            
        if self.powerup_type:
            self.powerup_effect()
            
        if self.hit:
            self.invincibility_animation()
        
        if self.shield <= 0:
            self.lose_life()
            
        if self.respawning:
            self.respawn_animation()

    def powerup_effect(self):
        now = pygame.time.get_ticks()
            
        if self.powerup_type == "extra health":
            #powerup_time being -1 indicates first time powerup is active
            if self.powerup_time == -1:
                #give player health. health caps at 100
                self.shield = min(self.shield + 25, 100)
                health_power_up_sound.play()
                self.powerup_time = now
                self.display_health_text = True
            
            #stop displaying message after 500 ms
            if now - self.powerup_time > 500:
                self.display_health_text = False
                self.powerup_time = -1
                self.powerup_type = None
                
            
        elif self.powerup_type == "auto fire":
            #powerup_time being -1 indicates first time powerup is active       
            if self.powerup_time == -1:
                self.powerup_time = now    
            
            if now - self.powerup_time > 5000 or self.respawning:
                self.powerup_type = None
                self.powerup_time = -1
            
            #Shoot a bullet automatically every 100 ms
            if now - self.powerup_shot_time > 100:
                self.powerup_shot_time = now
                self.shoot()
            
    def invincibility_animation(self):
        now = pygame.time.get_ticks()
        if self.num_cycles == 2:
            self.hit = False
            self.num_cycles = 0
            self.image = pygame.transform.scale(player_images[0], (50,38))
            self.image.set_colorkey(BLACK)
        elif now - self.last_updated > 100:
            self.last_updated = now
            self.image = pygame.transform.scale(player_images[abs(self.hit_frame)], (50,38))
            self.image.set_colorkey(BLACK)
            if self.hit_frame == 0:
                self.num_cycles += 1
            if self.hit_frame == 4:
                self.hit_frame = -4
            self.hit_frame += 1
            
    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        shoot_sound.play()
        
    def got_hit(self):
        player.shield -= hit.radius
        if not player.hit and player.shield > 0:
            player.hit = True
            player_hit_sound.play()
    
    def lose_life(self):
        global game_over
        player.num_lives -= 1
        player_death_sound.play()
        if player.num_lives == 0:
            game_over = True
        else:
            player.shield = 100
            self.respawning = True
            
    def respawn_animation(self):
        now = pygame.time.get_ticks()
        if self.respawn_frame == 8:
            self.rect.y += 62
            self.rect.x += 25
            self.image = pygame.transform.scale(player_images[0], (50,38))
            self.image.set_colorkey(BLACK)
            self.shield = 100
            self.respawning = False
            self.hit = True #To give player invincibility frames once they respawn
            self.respawn_frame = 0
        
        elif now - self.last_updated > 250:
            if self.respawn_frame == 0:
                self.rect.x -= 25
                self.rect.y -= 62
            self.last_updated = now
            self.image = pygame.transform.scale(respawn_images[self.respawn_frame], (100, 100))
            self.image.set_colorkey(BLACK)
            self.respawn_frame += 1
            
class Button(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rect.width = 121
        self.rect.height = 60
        self.type = None
            
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
        
class Powerup(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        image_chosen = random.randrange(0,2)
        self.image = pygame.transform.scale(powerup_images \
                        [image_chosen], (50, 50))
        if image_chosen == 0:
            self.type = "extra health"
        elif image_chosen == 1:
            self.type = "auto fire"
        elif image_chosen == 2:
            self.type = "shield"
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDTH - 50)
        self.rect.y = random.randrange(-110, -60)
        self.speedy = random.randrange(1, 5)
    
    def update(self):
        self.rect.y += self.speedy
        
        if self.rect.y > HEIGHT:
            self.kill()

    
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
        if self.rect.bottom < 0:
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
    sounds.set_volume(.55)
    
player_hit_sound = pygame.mixer.Sound(path.join(sounds_dir, "Player_Hit.wav"))
player_hit_sound.set_volume(.6)

player_death_sound = pygame.mixer.Sound(path.join(sounds_dir, "Player_Dead.wav"))
player_death_sound.set_volume(0.8)

health_power_up_sound = pygame.mixer.Sound(path.join(sounds_dir, "Health_Power_Up.wav"))
health_power_up_sound.set_volume(0.5)

#Load background music
background_music = {"game" : path.join(sounds_dir, "Background_Music.ogg"),
                    "menu" : path.join(sounds_dir, "Main_Menu.ogg") }



#Load all game graphics
background = pygame.image.load(path.join(img_dir, "space_background.png")).convert()
background_rect = background.get_rect()
bullet_img = pygame.image.load(path.join(img_dir, "laserRed16.png")).convert()

player_images = []

for i in range(0,6):
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
    
respawn_images = []

for i in range(9):
    respawn_path = path.join(img_dir, "sonicExplosion0{}.png".format(i))
    respawn_images.append(pygame.image.load(respawn_path).convert())

powerup_images = []

for i in range(2):
    powerup_path = path.join(img_dir, "powerUp0{}.png".format(i))
    powerup_images.append(pygame.image.load(powerup_path).convert())
    
main_menu_buttons = []

main_menu_x = 20
for i in range(3):
    main_menu_path = path.join(img_dir, "main0{}.png".format(i))
    image = pygame.image.load(main_menu_path).convert()
    main_menu_buttons.append(Button(image, main_menu_x, HEIGHT - HEIGHT / 4))
#     all_sprites.add(main_menu_buttons[i])
#     buttons.add(main_menu_buttons[i])
    main_menu_x += WIDTH / 3
    
main_menu_buttons[0].type = "start"
main_menu_buttons[1].type = "high scores"
main_menu_buttons[2].type = "quit"

running = True
title_screen = True
game_over = True
while running:
    
    if game_over:
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        buttons = pygame.sprite.Group()
        show_game_over_screen()
        game_over = False
        
        player = Player()
        all_sprites.add(player)
        score = 0
        pygame.mixer.music.load(background_music["game"])
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1) #-1 indicates to loop forever
        last_powerup_spawned = pygame.time.get_ticks()

        for i in range(8):
            newMob()
    
    clock.tick(FPS)
    
    #Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not \
                player.powerup_type == "auto fire":
                
                if not player.respawning:
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
            
    #Check to see if a powerup touched the player
    powerups_touched = pygame.sprite.spritecollide(player, powerups, \
        True, pygame.sprite.collide_circle)
    
    for powerup in powerups_touched:
        if powerup.type == "extra health":
            player.powerup_type = "extra health"
        elif powerup.type == "auto fire":
            player.powerup_type = "auto fire"
    
    #Check to see if a mob hit the player
    hits = pygame.sprite.spritecollide(player, mobs, False, pygame.sprite.collide_circle)
    for hit in hits:
        if not player.hit and not player.respawning:
            player.got_hit()
            
            #explode the meteor if the player got hit but is still alive,
            #otherwise just make it disappear without explosion
            if player.shield > 0:
                hit.exploded = True
            else:
                hit.kill()
            newMob()
        
    #Check if it is time for a new powerup to spawn
    if pygame.time.get_ticks() - last_powerup_spawned > 20000:
        new_powerup()
        last_powerup_spawned = pygame.time.get_ticks()
        
    
    #Display
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), WHITE, 35, WIDTH / 2, 10)
    draw_health_bar(screen, 5, 5, player.shield)
    draw_num_lives(screen, WIDTH - 130, 20, player.num_lives)
    if player.powerup_type == "auto fire":
        draw_text(screen, "AUTO FIRE", AUTO_FIRE_COLOR, 50, 235, 50)
        
    if player.display_health_text:
        draw_text(screen, "HEALTH RESTORED", HEALTH_COLOR, 44, 235, 50)
    pygame.display.flip()
    
pygame.quit()