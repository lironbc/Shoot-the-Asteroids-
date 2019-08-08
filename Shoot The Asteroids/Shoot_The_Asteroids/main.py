'''
Created on Jun 25, 2019

@author: Liron

Main file for Shoot The Asteriods. This file contains all game logic to run
the game. It provides classes for objects used in the game such as the 
player, asteroids, bullets, powerups, and buttons used inside of the game.
It contains the main game loop and manages transitions between menus
in the game.
'''

import pygame
import random
from os import path
from operator import itemgetter
from sys import exit
import json
from pygame.constants import K_BACKSPACE

#Game screen dimensions
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

def prompt_high_score_screen(blinking, screen, score):
    """
    
    Displays screen after player dies prompting them to enter their name
    so that their score can be recorded in the high scores.
    
    Args:
        blinking: A blinking rectangle to indicate cursor location
        screen: The display to show all images on
        score: Player score at end of game
    
    """
    waiting = True
    backspace_last_updated = pygame.time.get_ticks()
    name = ""
    while waiting:
        now = pygame.time.get_ticks()
        clock.tick(FPS)
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            #Exit game if player clicks X in top right corner
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                #Submit name once player presses enter
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    waiting = False
                else:
                    unicode = event.unicode
                    #Append letter to the name
                    if unicode.isalpha() and len(name) < 10:
                        name = name + unicode.upper()
        #Case where user is pressing backspace to delete what they've
        #written
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_BACKSPACE] and len(name) > 0 and \
            now - backspace_last_updated > 200:
            
            backspace_last_updated = now
            name = name[:-1] #Remove last letter from name
            
        #Display prompt text and background
        screen.blit(background, background_rect)
        draw_text(screen, "Enter your name to record your score",
                  WHITE, 32, 20, HEIGHT /4)
        draw_text(screen, "Press enter when finished",
                  WHITE, 32, WIDTH / 6, HEIGHT / 2)
        draw_user_input_text(blinking, screen, name, WHITE, 32,
                             WIDTH / 6, HEIGHT - HEIGHT / 4)
        pygame.display.flip()
        
    update_high_scores(name, score)
    
def update_high_scores(name, score):
    """
        Updates 'highscores.txt' file to include the new score just
        submitted. 
        
        Args:
            name: User submitted name to record in file
            score: Player's score to record in file
    """
    
    #Add new score to the set of scores
    global high_scores
    high_scores["people"].append({
        "name" : name,
        "score": score
    })
    
    #Sort high scores and write back at most the top 5 scores
    high_scores["people"] = sorted(high_scores["people"], key = lambda i: \
                                   i["score"], reverse = True)
    
    if len(high_scores["people"]) > 5:
        high_scores["people"] = high_scores["people"][0:5]
        
    #Write top 5 scores to the file and create the file if it does not exist
    with open("highscores.txt", 'w') as outfile:
        json.dump(high_scores, outfile)
        
    
def draw_user_input_text(blinking, surface, text, color, font_size, x, y):
    """
        Displays the text box where the player types in their name to submit
        their high score. This is an invisible rectangle with a blinking
        rectangle to the right of it acting as a cursor location.
        
        Args:
            blinking: A blinking rectangle to indicate cursor location
            surface: The surface to display the text box on.
            text: The text to be displayed in the text box
            color: The color of the text
            font_size: The font size of the text
            x: x coordinate of rectangle showing text box
            y: y coordinate of rectangle showing text box
    """
    
    text_rect = draw_text(surface,text,color,font_size,x,y)
    blinking.rect = pygame.Rect(text_rect.right, text_rect.top, 5, text_rect.height)
    blinking.update(surface, color)
    
def draw_main_menu():
    """
       Displays the text, background image, and buttons on the game's main menu.
        
        Args:
            None
    """
    screen.blit(background, background_rect)
    draw_text(screen, "SHOOT THE ASTEROIDS!", WHITE, 32, WIDTH / 6, HEIGHT / 4)
    draw_text(screen, "Arrow keys to move, Space to fire", \
               WHITE, 22, WIDTH / 5, HEIGHT / 2)

    draw_menu_buttons()
    pygame.display.flip()
    
def show_game_over_screen():
    """
       Shows the game over / main menu screen. Loads the main menu music,
       Displays all visuals, and waits for user to click one of the
       menu buttons.
        
        Args:
            None
    """
    draw_main_menu()

    pygame.mixer.music.load(background_music["menu"])
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1) #-1 indicates to loop forever
    waiting = True
    pos = (0,0) #Track position of mouse to see if buttons are clicked
        
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
                    show_high_score_screen(high_scores)
                    #move clicked position away from button so game doesn't
                    #immediately go back into hi-score menu
                    pos = (0, 0) 
                    draw_main_menu()
                elif button.type == "quit":
                    pygame.quit()
                    exit() 
 
def show_high_score_screen(high_scores):
    """
       Shows the high score screen. Displays the top 5 scores and provides a
       back button to return to the main menu.
        
        Args:
            high_scores: A dictionary holding a list of people with high scores
    """
    x = WIDTH / 5
    y = HEIGHT / 4
    screen.blit(background, background_rect)
    draw_text(screen, "HIGH SCORES", WHITE, 40, WIDTH / 4, 30)
    draw_text(screen, "Name", WHITE, 40, x - 30, y - 60)
    draw_text(screen, "Score", WHITE, 40, x + WIDTH / 2, y - 60)
    for people in high_scores["people"]:
        draw_text(screen, people.get("name"), WHITE, 32, x - 30, y)
        draw_text(screen, str(people.get("score")), WHITE, 32, x + WIDTH / 2, y)
        y += 60
    
    back_not_clicked = True
    pos = (0,0) #Track position of mouse to see if buttons are clicked
    #Draw back button
    back_image = pygame.image.load(path.join(img_dir, "back.png")).convert()
    back_button = Button(back_image, WIDTH / 3, HEIGHT - 140)
    image = pygame.transform.scale(back_button.image, (121, 60))
    screen.blit(image, (back_button.rect.x, back_button.rect.y))
    pygame.display.flip()
    
    while back_not_clicked:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos() #Used to see if button has been clicked
                
        #Back button has been clicked
        if back_button.rect.collidepoint(pos):
            back_not_clicked = False
            

def draw_menu_buttons():
    """
        Draws the "play", "hi-scores", and "quit" buttons on the main menu
        
        Args:
            None
    """
    for button in main_menu_buttons:
        image = pygame.transform.scale(button.image, (121, 60))
        screen.blit(image, (button.rect.x, button.rect.y))

def draw_text(surface, text, color, size, x, y):
    """
       Creates a text box and displays it on the screen.
        
        Args:
            surface: The surface to display the text box on.
            text: The text to be displayed in the text box
            color: The color of the text
            size: The font size of the text
            x: x coordinate of rectangle showing text box
            y: y coordinate of rectangle showing text box
        
        Returns:
            The Rectangle object that the text is inside of
    """
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x,y)
    surface.blit(text_surface, text_rect)
    return text_rect
    
def newMob():
    """
       Creates a new meteor and adds it to the appropriate sprite groups.
        
        Args:
            None
    """
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)
    
def new_powerup():
    """
       Creates a new powerup and adds it to the appropriate sprite groups.
        
        Args:
            None
    """
    p = Powerup()
    all_sprites.add(p)
    powerups.add(p)

def draw_health_bar(screen, x, y, shield):
    """
       Draws player's health bar by looking at how much shield the player
       has left.
        
        Args:
            screen: The screen to display the health bar on
            x: x coordinate of rectangle showing player's health bar 
            y: y coordinate of rectangle showing player's health bar 
    """

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
    """
       Draws the number of lives that the player has left by drawing smaller versions
       of the player's character model in the top right corner.
        
        Args:
            screen: The screen to display the health bar on
            x: x coordinate of rectangle showing player's lives 
            y: y coordinate of rectangle showing player's lives
            num_lives: the number of lives the player has 
    """
    image = pygame.transform.scale(player_images[0], (25,19))
    image.set_colorkey(BLACK)
    for i in range(player.num_lives):
        screen.blit(image, (x,y))
        x += 40
        
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #Defines player as a sprite
        self.image = pygame.transform.scale(player_images[0], (50,38)) #Player's ship image
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect() #Rectangle around player for collisions
        self.radius = 20 #Circle radius from center of player for collisions
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0 #Velocity in left and right directions
        self.shield = 100 #Player's health starts at 100
        self.hit = False #To see if player is hit so hit animation can play
        self.hit_frame = 1 #Once hit, which image of ship is being shown
        self.num_cycles = 0 #Tracks how many times invincibility frames have been cycled
        self.last_updated = pygame.time.get_ticks() #Last time an invincibility frame has been changed
        self.num_lives = 3 #Number of lives the player has
        self.respawning = False #Whether the player is currently dead or not
        self.respawn_frame = 0 #Which frame of respawn animation is currently being shown
        self.powerup_type = None #Which powerup the player currently has
        self.powerup_time = -1 #Used as a timer for how long shield and auto fire are active
        self.powerup_shot_time = pygame.time.get_ticks() #regulates how fast auto fire shoots
        self.display_health_text = False #Displays message when a health powerup is touched
    
    
    def update (self):
        """
           Used to update player's position if the arrows keys are being pressed,
           display animations if a collision happens in order to trigger a powerup
           response, lose health if a player gets hit, and lose a life if a player
           dies
            
            Args:
                None
        """
        self.speedx = 0 #Stops player from moving if key is not pressed
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
        """
           Provides a powerup effect if the player collides with one
           of the powerups. Health powerup gives the player + 25 health
           and auto fire makes the ship shoot automatically
            
            Args:
                None
        """
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
        """
           When a player respawns or is hit, there are a few seconds of
           invincibility where they cannot be hit again. During this time,
           this method displays an animation where it pulses the ship white
           to indicate the ship cannot be hit
            
            Args:
                None
        """
        
        now = pygame.time.get_ticks()
        #Animation happens twice before restoring original ship color
        if self.num_cycles == 2:
            self.hit = False
            self.num_cycles = 0
            self.image = pygame.transform.scale(player_images[0], (50,38))
            self.image.set_colorkey(BLACK)
        #Change frame of animation every 100 ms
        elif now - self.last_updated > 100:
            self.last_updated = now
            #uses absolute value to cycle from frames 0 to 4 by first going 0 to 4 by adding,
            #then making the frame count -4. Because the absolute value will be 4, this 
            #animation correctly goes from 0 to 4 back to 0. This prevents having seperate logic
            #increasing and decreasing the counter
            self.image = pygame.transform.scale(player_images[abs(self.hit_frame)], (50,38))
            self.image.set_colorkey(BLACK)
            if self.hit_frame == 0:
                self.num_cycles += 1
            if self.hit_frame == 4:
                self.hit_frame = -4
            self.hit_frame += 1
            
    def shoot(self):
        """
           When a player presses the space key, if autofire is not active
           then this method will shoot a new bullet from the front of
           the player's ship and add it to the appropriate sprite groups
           to test for collisions
            
            Args:
                None
        """
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        shoot_sound.play()
        
    def got_hit(self):
        """
           Reduces player's health when they get hit and plays a sound
           provided the hit didn't kill the player
            
            Args:
                None
        """
        player.shield = int(player.shield - (hit.radius * 1.5))
        if not player.hit and player.shield > 0:
            player.hit = True
            player_hit_sound.play()
    
    def lose_life(self):
        """
           Player loses a life and if no lives are left, then the player is directed
           to to enter their name for their score to be recorded
            
            Args:
                None
        """
        global game_over
        player.num_lives -= 1
        player_death_sound.play()
        if player.num_lives == 0:
            game_over = True
            blinking = Blinking() #used to blink cursor as user types in their name
            prompt_high_score_screen(blinking,screen, score)
            blinking.kill()
        else:
            player.shield = 100
            self.respawning = True
            
    def respawn_animation(self):
        """
           Animation that plays when a player is respawning after dying
            
            Args:
                None
        """
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
            
class Blinking(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.rect = None #rectangle that will blink
        self.last_updated = pygame.time.get_ticks() #last time the rectangle blinked
        self.active = True #Whether the rectangle is currently visible
        
    
    def update(self, surface, color):
        """
           Rectangle will toggle between being visible and invisible every 500
           ms to mimic a blinking cursor after text when typing
            
            Args:
                surface: the surface to display the blinking rectangle
                color: the color of the rectangle
        """
        now = pygame.time.get_ticks()
        if now - player.last_updated < 500: 
            if self.active == False:
                blinking_rect = pygame.Rect(self.rect.right, self.rect.top, 5, self.rect.height)
                pygame.draw.rect(surface, color, self.rect)
        else:
            player.last_updated = now
            self.active = not self.active
        
        
class Button(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image #The image displayed on the rectangle
        image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rect.width = 121
        self.rect.height = 60
        self.type = None #Used to identify which button was clicked
            
class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images) #The meteor image used
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy() #Copy of image used for rotating
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.radius = int(self.rect.width * .85 / 2) #Collision radius
        self.speedy = random.randrange(1,4) #Speed at which meteor goes down
        self.speedx = random.randrange(-3,3) #Speed at which meteor moves l/r
        self.rot = 0 #How many degrees the image has rotated
        self.rot_speed = random.randrange(-8,8) # Speed at which meteor rotates
        self.last_updated = pygame.time.get_ticks() # Last time rotation happened
        self.frame = 0 #Which frame of explosion is currently active
        self.exploded = False #Whether a collision has happened with a player or not
        
    def rotate(self):
        """
           Rotates the meteor image every 50 ms by rotating the image,
           and creating a new rectangle for collision around this
           iamge. Note that two images are used in this process, the
           original image and the new image. Once the rotation is done,
           the new image is now the new image. This is because pygame's
           transform.rotate function handles rotating an already
           rotated image in unexpected ways.
            
            Args:
                None
        """
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
        """
            Moves the meteor. If the meteor goes off stage, then this
            resets the meteor somewhere off-screen.
            
            Args:
                None
        """
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
        """
            When the player and meteor collide or a bullet and a meteor collide,
            the meteor goes through an explosion animation from this method
            and then disappears
            
            Args:
                None
        """
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
        image_chosen = random.randrange(0,2) #A random powerup is chosen
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
        """
            Moves the powerup downwards. If the powerup goes offstage, it
            disapears.
            
            Args:
                None
        """
        self.rect.y += self.speedy
        
        if self.rect.y > HEIGHT:
            self.kill()

    
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img #Sets image of bullet
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10 #Bullet moves up towards meteors
        
    def update(self):
        """
           Bullet moves upwards. If it goes off stage, it disappears.
            
            Args:
                None
        """
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
    main_menu_x += WIDTH / 3
    
#Assign main menu button types
main_menu_buttons[0].type = "start"
main_menu_buttons[1].type = "high scores"
main_menu_buttons[2].type = "quit"

#Load high scores from file
high_scores = {}
high_scores["people"] = []

#Open high scores file if it exists
try:
    with open("highscores.txt", 'r') as json_file:
        high_scores = json.load(json_file)
    
#Case where high scores file doesn't exist. File will be created when
#new high score is recorded
except:
        pass
    
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
            #otherwise just make it disappear without explosion. In both
            #cases meteor is destroyed so a new one is made to replace it
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
    draw_text(screen, str(score), WHITE, 35, WIDTH / 2 - 20, 10)
    draw_health_bar(screen, 5, 5, player.shield)
    draw_num_lives(screen, WIDTH - 130, 20, player.num_lives)
    if player.powerup_type == "auto fire":
        draw_text(screen, "AUTO FIRE", AUTO_FIRE_COLOR, 50, WIDTH / 4 + 20, 50)
        
    if player.display_health_text:
        draw_text(screen, "HEALTH RESTORED", HEALTH_COLOR, 44, WIDTH / 8, 50)
    pygame.display.flip()
    
pygame.quit()