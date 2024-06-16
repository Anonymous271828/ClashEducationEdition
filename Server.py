import socket
from _thread import *
from Game import Game
from Units import *
import time
import pygame
import pickle
import struct
import numpy as np

#win = 0
#game = 0
pygame.init()


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
# Original IP is 10.0.0.202
server = "192.168.1.152"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)


s.listen(2)
print("Waiting for a connection. Server Started")

connected = set()
games = {}
idCount = 0

def threaded_client(connection, p, gameId):
    global idCount
    connection.send(str.encode(str(p)))

    reply = ""
    while True:
        try:
            #data = connection.recv(4096).decode()
            data = pickle.loads(connection.recv(2048*2))
            #print("A")
            if gameId in games:
                global game
                game = games[gameId]

                if not data:
                    pass
                else:
                    if data == "get":
                        #print("b")
                        pickled_data = pickle.dumps(game)
                        data_size = struct.pack("I", len(pickled_data))
                        #data_size = pickle.dumps("{}".format(len(pickled_data)))
                        #print("A")
                        connection.sendall(data_size)
                        #connection.recv(1024)
                        #print("2")
                        connection.sendall(pickled_data)
                        #print(pickled_data)
                        #connection.sendall(pickle.dumps("A"))
                        #print(p)
                        #print("1")


                        # connection.send(data_size)
                        #for i in range(int(np.floor(len(pickled_data) / 1024))):
                             #print("thtrh")
                             #print(pickled_data[1024 * (i - 1):1024 * i])
                            #connection.send(pickled_data[1024*(i-1):1024*i])
                        #if len(pickled_data) % 1024 != 0:
                            #connection.send(pickled_data[int(np.floor(len(pickled_data) / 1024)) * 1024:])
                        #print(pickled_data)



                        #if p == 0:
                            #game.p1received = True
                        #else:
                            #game.p2received = True
                    elif data == "Done drawing":
                        #print('c')
                        # DON'T NEED TO LOAD AND UNLOAD?
                        #for i in game.char_group:
                        #    i.load()
                        #for i in game.tower_group:
                        #    i.load()
                        #for i in game.proj_group:
                        #    i.load()
                        game.update()
                        #for i in game.char_group:
                        #    i.unload()
                        #for i in game.tower_group:
                        #    i.unload()
                        #for i in game.proj_group:
                        #    i.unload()

                        #pickled_data = pickle.dumps(game)
                        #data_size = struct.pack("I", len(pickled_data))
                        #connection.sendall(data_size)
                        #connection.sendall(pickled_data)


                        #pickled_data = pickle.dumps(game)
                        #data_size = struct.pack("I", len(pickled_data))
                        #print("2 ", len(pickled_data))
                        #connection.send(data_size)
                        #for i in range(1, int(np.floor(len(pickled_data) / 1024)) + 1):
                            #connection.send(pickled_data[1024 * (i - 1):1024 * i])
                            #print(pickled_data[1024 * (i - 1):1024 * i])
                        #if len(pickled_data) % 1024 != 0:
                            #connection.send(pickled_data[int(np.floor(len(pickled_data) / 1024)) * 1024:])

                    else:
                        #data.load()
                        #print(game.char_group)
                        game.char_group.add(data)
                        #connection.send(b"rgrththrtjhdtjhtrsjsrtjsrjdsrjyytjy")

                        #pickled_data = pickle.dumps(game)
                        #data_size = struct.pack("I", len(pickled_data))
                        #connection.sendall(data_size)
                        #connection.sendall(pickled_data)
                        #print("Oh no")
                        #print(pickled_data)



                        # pickled_data = pickle.dumps(game)
                        # data_size = struct.pack("I", len(pickled_data))
                        # #print("3 ", len(pickled_data))
                        # connection.send(data_size)
                        # for i in range(1, int(np.floor(len(pickled_data) / 1024)) + 1):
                        #     connection.send(pickled_data[1024 * (i - 1):1024 * i])
                        #     print(pickled_data[1024 * (i - 1):1024 * i])
                        # if len(pickle nt(np.floor(len(pickled_data) / 1024)) * 1024:])
                        #     print("A", pickled_data[int(np.floor(len(pickled_data) / 1024)) * 1024:])






                #if game.p1went and game.p2went:
                    #game.update()
                    #game.restart()
                    #else:
                        #pass
                #if game.p1received and game.p2received:
                    #print("a")
                    #connection.sendall(pickle.dumps(game))
                    #game.restart_recv()
            else:
                print("AAAAA")
                break
        except Exception as e:
            print("abc", e)
            break

    print("Lost connection")
    try:
        del games[gameId]
        print("Closing game, {}".format(gameId))
    except:
        pass
    idCount = idCount - 1
    connection.close()


towers = [Tower(114, 64, 100, 100, 0, "white_sub_tower", 200, 2000, 67, 0.8), Tower(624, 60, 100, 100, 0, "white_sub_tower", 200, 2000, 67, 0.8), Tower(119, 644, 100, 100, 0, "black_sub_tower", 200, 2000, 67, 0.8), Tower(632, 640, 100, 100, 0, "black_sub_tower", 200, 2000, 67, 0.8), Tower(355, 11, 100, 100, 0, "white_main_tower", 200, 4000, 120, 1), Tower(355, 672, 100, 100, 0, "black_main_tower", 200, 4000, 120, 1)]
while True:
    conn, addr = s.accept()
    print("Connection successful, connected to {}".format(addr))

    idCount = idCount + 1
    gameId = (idCount - 1)//2
    print(idCount)
    if idCount % 2 == 1:
        p = 0
        games[gameId] = Game(pygame.sprite.Group(), pygame.sprite.Group(towers), pygame.sprite.Group(), gameId)
        print("Creating a new game...")
        #start_new_thread(threaded_client, (conn, p, gameId))
    else:
        games[gameId].ready = True
        p = 1


    start_new_thread(threaded_client, (conn, p, gameId))