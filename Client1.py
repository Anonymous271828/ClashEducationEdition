import pygame
import numpy as np
import pandas as pd
import time
import csv
import random
import requests
from Network import Network
from io import BytesIO
#from Units import *

# Represent students
# Represent political characters
# Mini-pekka (4), dart-goblin (3), hog-rider (4), musketeer (4), minion (3), mega-knight (7), zap (2), fireball (4), inferno tower (5),


# Constants
win_height = 800
win_width = 1100
url = "" # Insert Student 1s deck. Must be in spreadsheet.

# Initialization
pygame.init()
pygame.font.init()

# Basic setup
win = pygame.display.set_mode((win_width, win_height))


class Player():
    def __init__(self, currency, team):
        self.currency = currency
        self.team = team
    def ask_question(self, chosen_row):
        win.fill((255, 255, 255))
        pygame.draw.rect(win, (255, 0, 0), (0, 280, 550, 260))
        pygame.draw.rect(win, (0, 255, 0), (550, 540, 550, 260))
        pygame.draw.rect(win, (0, 0, 255), (0, 540, 550, 260))
        pygame.draw.rect(win, (0, 255, 255), (550, 280, 550, 260))
        for i in range(1, 5):
            font = pygame.font.SysFont("comicsans", 20)
            text = font.render(chosen_row[i], 1, (0, 0, 0))
            pos_dict_x = {1:0, 2:1, 3:0, 4:1}
            pos_dict_y = {1: 0, 2: 0, 3: 1, 4: 1}
            win.blit(text, (550 * pos_dict_x[i], 280 + 260 * pos_dict_y[i]))
        font = pygame.font.SysFont("comicsans", 25)
        text = font.render(chosen_row[0], 1, (0, 0, 0))
        win.blit(text, (10, 10))
        return int(chosen_row[5])

class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, id, speed, mode, range, agro_range, health, damage, reload, area_damage, count):
        super().__init__()
        self.x = x
        self.y = y
        self.width= width
        self.height = height
        self.id = id
        self.speed = speed
        self.mode = mode
        self.range = range
        self.agro_range = agro_range
        self.health = health
        self.max_health = health
        self.damage = damage
        self.reload = reload
        self.area_damage = area_damage
        self.count = count
        self.location_of_bridges = {"w":348, "b": 477}
        #dist_dict = {abs(self.x - 141): self.x - 141, abs(self.x - 690): self.x - 700}
        #print("AAAAAAA", dist_dict[min(abs(self.x - 141), abs(self.x - 700))])
        self.target_current_distance = (min(abs(self.x - 141), abs(self.x - 700)), self.y - self.location_of_bridges[self.id[0]])
        self.vel_x, self.vel_y = determine_vel(self.target_current_distance, self.speed)
        self.image = None
        #self.image = self.image(pygame.Color(255, 255, 255))
        #self.image = pygame.transform.scale(self.image, (50, 50))
        #self.rect = self.image.get_rect()
        #self.rect_center = [self.x, self.y]
        self.rect = (self.x, self.y, self.width, self.height)
        self.last_reload = 0
    def load(self):
        self.image = pygame.image.load("{}.png".format(self.id))
        # self.image = self.image(pygame.Color(255, 255, 255))
        self.image = pygame.transform.scale(self.image, (50, 50))
        #self.rect = self.image.get_rect()
        #self.rect_center = [self.x, self.y]
    def unload(self):
        self.image = None

    def update(self):
        keys = pygame.key.get_pressed()
        if self.id == 1:
            if keys[pygame.K_RIGHT]:
                self.x = self.x + self.speed*10
            elif keys[pygame.K_LEFT]:
                self.x = self.x - self.speed*10
        else:
            if keys[pygame.K_d]:
                self.x = self.x + self.speed*10
            elif keys[pygame.K_a]:
                self.x = self.x - self.speed*10
            if keys[pygame.K_w]:
                self.y = self.y - self.speed*10
            elif keys[pygame.K_s]:
                self.y = self.y + self.speed*10

        if self.health < 0:
            self.kill()

        for i in game.char_group:
            if i.id[0] != self.id[0] and (self.x - i.x)**2 + (self.y - i.y)**2 < self.agro_range**2:
                if i.x - self.range <= self.x <= i.x + self.range and i.y - self.range <= self.y <= i.y + self.range:
                    self.vel_x, self.vel_y = determine_vel(self.target_current_distance, 0)
                    if time.time() - self.last_reload > self.reload:
                        #print("bbb")
                        self.last_reload = time.time()
                        i.health = i.health - self.damage
                        game.proj_group.add(Projectile(self.x, self.y, 0, 0, 10, "cannon_ball", i.id, i.x, i.y))
                    break
                self.target_current_distance = (self.x - i.x, self.y - i.y)
                self.vel_x, self.vel_y = determine_vel(self.target_current_distance, self.speed)
                break
        else:
            for i in game.tower_group:
                #print(i.id[0] != self.id[0], (self.x - i.x) ** 2 + (self.y - i.y) ** 2 < (self.agro_range+600)**2)
                if i.id[0] != self.id[0] and (self.x - i.x) ** 2 + (self.y - i.y) ** 2 < (self.agro_range+300)**2:
                    #print('a')
                    if i.x - 120 - self.range <= self.x <= i.x + 120 + self.range and i.y - 120 - self.range <= self.y <= i.y + 120 + self.range:
                        self.vel_x, self.vel_y = determine_vel(self.target_current_distance, 0)
                        if time.time() - self.last_reload > self.reload:
                            self.last_reload = time.time()
                            #print('a')
                            i.health = i.health - self.damage
                            game.proj_group.add(Projectile(self.x, self.y, 0, 0, 10, "cannon_ball", i.id, i.x, i.y))
                        break
                    #print('b')
                    self.target_current_distance = (self.x - i.x, self.y - i.y)
                    self.vel_x, self.vel_y = determine_vel(self.target_current_distance, self.speed)
                    break
            else:
                dist_dict = {abs(self.x - 141): self.x - 141, abs(self.x - 700): self.x - 700}
                #print(self.id)
                self.target_current_distance = (min(abs(self.x - 141), abs(self.x - 700)),self.y - self.location_of_bridges[self.id[0]])
                self.vel_x, self.vel_y = determine_vel(self.target_current_distance, self.speed)
                self.last_reload = 0

        self.x = self.x + self.vel_x
        self.y = self.y + self.vel_y
        self.rect = (self.x, self.y, self.width, self.height)

class Cards(pygame.sprite.Sprite):
    def __init__(self, x, y, img, currency, character, selected):
        super().__init__()
        self.x = x
        self.y = y
        self.id = img
        self.img = pygame.image.load("{}.png".format(img))
        self.img = pygame.transform.scale(self.img, (200, 200))
        self.rect = self.img.get_rect()
        self.currency = currency
        self.character = character
        self.selected = selected

    def check_if_selected(self, click):
        #print(self.x, self.y, click)
        if self.x <= click[0] <= self.x + self.rect[2] and self.y <= click[1] <= self.y + self.rect[3]:
            if self.selected == False:
                #print("AAAAAA")
                for i in complete_deck[:4]:
                    i.selected = False
                self.selected = True
            else:
                self.selected = False

    def draw(self):
        win.blit(self.img, (self.x, self.y))
    def update(self):
        pygame.draw.rect(win, (0, 0, 0), (self.x, self.y, self.rect[2], self.rect[3]), 1)
        font = pygame.font.SysFont("comicsans", 20)
        text = font.render(str(int(self.currency)), 1, (0, 0, 0))
        win.blit(text, (self.x + self.rect[2] - text.get_width(), self.y))
        if self.selected:
            pygame.draw.rect(win, (222, 218, 18), (self.x, self.y, self.rect[2], self.rect[3]), 10)


class Tower(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, speed, id, range, health, damage, reload):
        super().__init__()
        self.x = x
        self.y = y
        self.width= width
        self.height = height
        self.speed = speed
        self.id = id
        self.range = range
        self.reload = reload
        self.health = health
        self.max_health = health
        self.damage = damage
        self.image = None
        self.rect = (self.x, self.y, self.width, self.height)
        #self.rect.topleft = [self.x, self.y]
        self.last_reload = 0
    def load(self):
        self.image = pygame.image.load("{}.png".format(self.id))
        if self.id[0] == "w":
            self.image = pygame.transform.flip(self.image, False, True)
        #self.rect = self.image.get_rect()
        #self.rect.topleft = [self.x, self.y]
    def unload(self):
        self.image = None
    def update(self):
        if self.health < 0:
            self.kill()
        if time.time() - self.last_reload > self.reload:
            self.last_reload = time.time()
            for i in game.char_group:
                #print(self.x, self.y, i.x, i.y, self.id, (self.x - i.x)**2 + (self.y - i.y)**2)
                if (self.x - i.x)**2 + (self.y - i.y)**2 < self.range**2 and self.id[0] != i.id[0]:
                    #print("hi2")
                    i.health = i.health - self.damage
                    game.proj_group.add(Projectile(self.x, self.y, 0, 0, 10, "cannon_ball", i.id, i.x, i.y))
                    return game.proj_group
            else:
                self.last_reload = 0
        return game.proj_group

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, speed, id, target_id, target_x, target_y):
        super().__init__()
        self.x = x
        self.y = y
        self.width= width
        self.height = height
        self.speed = speed
        self.id = id
        self.target_id = target_id
        self.target = target_x, target_y
        self.target_current_distance = (self.x - target_x, self.y - target_y)
        self.vel_x, self.vel_y = determine_vel(self.target_current_distance, self.speed)
        #self.image = self.iid
        self.image = None
        self.rect = (self.x, self.y, self.width, self.height)
        #print("hi")
    def load(self):
        self.image = pygame.image.load("{}.png".format(self.id))
        #self.rect = self.image.get_rect()
        #self.rect.topleft = [self.x, self.y]
    def unload(self):
        self.image = None
    def update(self):
        self.x = self.x + self.vel_x
        self.y = self.y + self.vel_y
        self.rect = (self.x, self.y, self.width, self.height)
        if self.target[0] - 5 <= self.x <= self.target[0] + 5 and self.target[1] - 5 <= self.y <= self.target[1] + 5:
            self.kill()
def determine_vel(target_current_distance, speed):
    if target_current_distance[0] > 0 and target_current_distance[1] >= 0:
        vel_x = np.cos(np.arctan(target_current_distance[1] / target_current_distance[0]) + np.pi) * speed
        vel_y = np.sin(np.arctan(target_current_distance[1] / target_current_distance[0]) + np.pi) * speed
    elif target_current_distance[0] < 0 and target_current_distance[1] >= 0:
        vel_x = np.cos(np.arctan(target_current_distance[1] / target_current_distance[0])) * speed
        vel_y = np.sin(np.arctan(target_current_distance[1] / target_current_distance[0])) * speed
    elif target_current_distance[0] < 0 and target_current_distance[1] <= 0:
        vel_x = np.cos(np.arctan(target_current_distance[1] / target_current_distance[0])) * speed
        vel_y = np.sin(np.arctan(target_current_distance[1] / target_current_distance[0])) * speed
    elif target_current_distance[0] > 0 and target_current_distance[1] <= 0:
        vel_x = np.cos(np.arctan(target_current_distance[1] / target_current_distance[0]) + np.pi) * speed
        vel_y = np.sin(np.arctan(target_current_distance[1] / target_current_distance[0]) + np.pi) * speed
    else:
        vel_y = speed
        vel_x = 0
    return vel_x, vel_y

def determine_card_stats(card_id):
    all_characters_stats = {}
    deck = requests.get("") # Insert all cards in game. Must be in a spreadsheet.
    deck = BytesIO(deck.content)
    df = pd.read_csv(deck)
    for i in df.values.tolist():
        all_characters_stats[i[0]] = list(map(lambda x: float(x), i[2:12]))
    card_id_without_tag = card_id[2:]
    char = Character(0, 0, 10, 10, card_id, all_characters_stats[card_id_without_tag][0], all_characters_stats[card_id_without_tag][1], all_characters_stats[card_id_without_tag][2], all_characters_stats[card_id_without_tag][3], all_characters_stats[card_id_without_tag][4], all_characters_stats[card_id_without_tag][5], all_characters_stats[card_id_without_tag][6], all_characters_stats[card_id_without_tag][7], all_characters_stats[card_id_without_tag][8])
    return Cards(0, 0, card_id, all_characters_stats[card_id_without_tag][9], char, False)

def multilines(text, x, y, width):
    text_list = text.split(" ")
    line = []
    line_length = 0
    line_counter = 0
    font = pygame.font.SysFont("comicsans", 10)
    for item in text_list:
        text = font.render(item, 1, (0, 0, 0))
        line_length = line_length + text.get_width()
        print(item, line_length)
        if line_length < width:
            line.append(item)
        else:
            text2 = font.render(" ".join(line), 1, (0, 0, 0))
            win.blit(text2, (x, y + 20 * line_counter))
            line_counter = line_counter + 1
            line = [item]
            line_length = text.get_width()
    else:
        text = font.render(" ".join(line), 1, (0, 0, 0))
        win.blit(text, (x, y + 20 * line_counter))

Player1 = Player(0, "black")
turn = 0
bg = pygame.image.load("map_clash.png")
clock = pygame.time.Clock()
space_button_clicked = False
answer = 0
deck = requests.get(url)
deck = BytesIO(deck.content)
df = pd.read_csv(deck)
complete_deck = []
for i in df:
    complete_deck.append(determine_card_stats(i))
random.shuffle(complete_deck)

questions = requests.get("") # Insert questions here. Must be in question format
questions = BytesIO(questions.content)
df = pd.read_csv(questions)
final_questions = []
for i in df.values.tolist():
    final_questions.append(i)
print("Init done.")
player = int(n.get_p())
print(player)
while True:
    game = n.send("get")
    win.fill((255,255,255))
    win.blit(bg, (0,0))
    pygame.draw.rect(win, (120, 18, 222), (1000, 0, 100, Player1.currency * 40))
    font = pygame.font.SysFont("comicsans", 30)
    text = font.render(str(int(Player1.currency)), 1, (0, 0, 0))
    win.blit(text, (1050 - text.get_width() / 2, 700))

    for event in pygame.event.get():
        if event == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            turn = turn + 1
            mouse_pos = pygame.mouse.get_pos()
            for i in complete_deck[:4]:
                i.check_if_selected(mouse_pos)
            if space_button_clicked:
                if 0 <= mouse_pos[0] <= 550 and 260 <= mouse_pos[1] <= 540:
                    if answer == 1 and Player1.currency < 20:
                        Player1.currency = Player1.currency + 1
                        space_button_clicked = False
                    else:
                        space_button_clicked = False
                elif 0 <= mouse_pos[0] <= 550 and 540 <= mouse_pos[1] <= 800:
                    if answer == 3 and Player1.currency < 20:
                        Player1.currency = Player1.currency + 1
                        space_button_clicked = False
                    else:
                        space_button_clicked = False
                elif 550 <= mouse_pos[0] <= 1100 and 260 <= mouse_pos[1] <= 540:
                    if answer == 2 and Player1.currency < 20:
                        Player1.currency = Player1.currency + 1
                        space_button_clicked = False
                    else:
                        space_button_clicked = False
                elif 550 <= mouse_pos[0] <= 1100 and 540 <= mouse_pos[1] <= 800:
                    if answer == 4 and Player1.currency < 20:
                        Player1.currency = Player1.currency + 1
                        space_button_clicked = False
                    else:
                        space_button_clicked = False
            else:
                for j, i in enumerate(complete_deck[:4]):
                    if i.selected == True and mouse_pos[0] <= 800 and mouse_pos[1] >= 500 and Player1.currency >= i.currency:
                        print(i.id)
                        n.send_without_receive(Character(int(mouse_pos[0]), int(mouse_pos[1]), i.character.width, i.character.height, i.id, i.character.speed, i.character.mode, i.character.range, i.character.agro_range, i.character.health, i.character.damage, i.character.reload, i.character.area_damage, i.character.count))
                        complete_deck.pop(j)
                        complete_deck.append(i)
                        i.selected = False
                        Player1.currency = Player1.currency - i.currency




    clock.tick(60)
    for i in game.char_group:
        i.load()
        if i.id[0] == "b":
            pygame.draw.rect(win, (0, 0, 0), (i.x - 10, i.y + i.height + 10, i.width + 20, 20))
            pygame.draw.rect(win, (255, 0, 0), (i.x - 10, i.y + i.height + 10, i.health/i.max_health * (i.width + 20), 20))
        else:
            pygame.draw.rect(win, (0, 0, 0), (i.x - 10, i.y - 30, i.width + 20, 20))
            pygame.draw.rect(win, (255, 0, 0), (i.x - 10, i.y - 30, i.health / i.max_health * (i.width + 20), 20))
    for i in game.tower_group:
        i.load()
        if i.id[0] == "b":
            pygame.draw.rect(win, (0, 0, 0), (i.x - 10, i.y + i.height + 10, i.width + 20, 20))
            pygame.draw.rect(win, (255, 0, 0), (i.x - 10, i.y + i.height + 10, i.health/i.max_health * (i.width + 20), 20))
        else:
            pygame.draw.rect(win, (0, 0, 0), (i.x - 10, i.y - 30, i.width + 20, 20))
            pygame.draw.rect(win, (255, 0, 0), (i.x - 10, i.y - 30, i.health / i.max_health * (i.width + 20), 20))
    for i in game.proj_group:
        i.load()
    game.char_group.draw(win)
    #char_group.update()
    game.tower_group.draw(win)
    #tower_group.update()
    game.proj_group.draw(win)
    #proj_group.update()
    for i in range(4):
        complete_deck[i].x, complete_deck[i].y = 800, i*200
        complete_deck[i].draw()
        complete_deck[i].update()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        space_button_clicked = True
        chosen_row = random.choice(final_questions)
    if space_button_clicked:
        answer = Player1.ask_question(chosen_row)
    n.send_without_receive("Done drawing")
    pygame.display.flip()