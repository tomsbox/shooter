import random, time, sys
import pygame, pgzrun
from sys import argv
from datetime import datetime
import requests
import json
from operator import itemgetter

WIDTH, HEIGHT = 1000, 700
RED = 200, 0, 0
BOX = Rect((20, 20), (100, 100))


class Player():
    def __init__(self):
        self.name = 'Matteo'

    def enter_name(self):
        self.name = input("Name:")
        return 0

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name


class Timer():

    def __init__(self):
        self.timer = 3
        self.last_hit = datetime.now()

    def get_last_hit_in_seconds(self):
        last_hit_in_seconds = (datetime.now() - self.last_hit).seconds
        print(last_hit_in_seconds)
        return last_hit_in_seconds

    def set_hit_time(self):
        self.last_hit = datetime.now()


class Counter():
    def __init__(self):
        print("init")
        self.shoot_counter = 0
        self.hit_counter = 0
        self.points = 0
        self.ship_hit = 0
        self.fobj = open("maxpoints.txt", "r")
        self.first = {"player": 'none', "score": 0}
        self.second = {"player": 'none', "score": 0}
        self.third = {"player": 'none', "score": 0}
        self.highscore = []
        self.backend_api_url = 'http://192.168.178.64:8000/games/'
        self.highscore_backendjson = self.get_highscore_from_backend()
        for self.line in self.fobj:
            self.highscore.append(self.line.rstrip())
        self.fobj.close()

    def get_highscore_from_backend(self):

        try:
            highscore_from_backend = requests.get(self.backend_api_url)
            highscore_from_backend = json.loads(highscore_from_backend.text)

            highscore_from_backend = sorted(highscore_from_backend, key=itemgetter('score'), reverse=True)
            self.first = highscore_from_backend[0]
            self.second = highscore_from_backend[1]
            self.third = highscore_from_backend[2]
        except:
            print("get_highscore_from_backend() --> Server not found")

    def set_hit_counter(self):
        self.hit_counter += 1
        self.points += 10
        print("Hit: " + str(self.hit_counter) + " ufo's! Your current points are: " + str(self.points))

    def rocket_counter(self):
        self.shoot_counter += 1
        self.points -= 1
        print("Shoot: " + str(self.shoot_counter) + " rockets! Your current points are: " + str(self.points))

    def ship_hit_counter(self):
        self.ship_hit += 1
        self.points -= 100
        print("You was hit for: " + str(self.ship_hit) + " times! Your current points are: " + str(self.points))

    def get_ship_hit_counter(self):
        return self.ship_hit

    def get_points(self):
        return self.points

    def get_highscore(self):
        return self.highscore

    def get_backend_api_url(self):
        return self.backend_api_url

    def print_result(self):
        file = open("highscore.txt", "a")
        file.write(player.get_name() + " you need: " + str(self.shoot_counter) + " shots to terminate " + str(
            self.hit_counter) + " ufo's! You get " + str(self.points) + " points!")
        file.write("\n")
        print(player.get_name() + " you need: " + str(self.shoot_counter) + " shots to terminate " + str(
            self.hit_counter) + " ufo's! You get " + str(self.points) + " points!")


class Ship(Actor):
    def __init__(self):
        Actor.__init__(self, 'ship')
        self.bottom = HEIGHT
        self.centerx = WIDTH / 2
        self.vel = 6

    def update(self):
        if keyboard.left:
            self.x -= self.vel
        if keyboard.right:
            self.x += self.vel
        if keyboard.up:
            self.y -= self.vel
        if keyboard.down:
            self.y += self.vel
        self.clamp_ip(0, 0, WIDTH, HEIGHT)

    def launch_rocket(self):
        rocket = Rocket(self.x, self.y - 50)
        counter.rocket_counter()
        game.rockets.append(rocket)

    def post_score(self):
        try:
            score = {'player': str(player.get_name()), 'score': int(counter.get_points())}
            x = requests.post(counter.get_backend_api_url(), data=score)
            print(x.text)
        except:
            print("post_score() --> Server not found")

    def hit(self):
        counter.print_result()
        sounds.ship_hit.play()
        if counter.get_ship_hit_counter() > 2:
            if int(counter.get_points()) > int(counter.get_highscore()[1]):
                file = open("maxpoints.txt", "w")
                file.write(player.get_name())
                file.write("\n")
                file.write(str(counter.get_points()))
                file.write("\n")

            time.sleep(3)
            # post result every time
            self.post_score()
            sys.exit()
        else:
            counter.ship_hit_counter()


class Rocket(Actor):
    def __init__(self, x, y):
        Actor.__init__(self, 'rocket')
        sounds.rocket_launch.play()
        self.alive = True
        self.x = x
        self.y = y
        self.vel = 10

    def update(self):
        self.y -= self.vel
        if (self.top < 0):
            self.alive = False
        for ufo in game.ufos:
            if self.colliderect(ufo):
                ufo.hit()
                self.alive = False
                return


class UFO(Actor):
    def __init__(self, x, y):
        Actor.__init__(self, 'ufo')
        self.alive = True
        self.x = x
        self.y = y
        self.x_vel = 2
        self.y_vel = 1
        self.bomb_rate = 0.007

    def update(self):
        self.x += self.x_vel
        self.y += self.y_vel

        if self.left < 0 and self.x_vel < 0:
            self.x_vel *= -1
        if self.right > WIDTH and self.x_vel > 0:
            self.x_vel *= -1

        if self.top > HEIGHT:
            self.alive = False

        if decide(self.bomb_rate) and self.top > 0:
            self.drop_bomb()

        if self.colliderect(game.ship):
            game.ship.hit()
            self.alive = False

    def drop_bomb(self):
        game.bombs.append(Bomb(self.center))

    def hit(self):
        sounds.ufo_hit.play()
        counter.set_hit_counter()
        self.alive = False


class Bomb(Actor):
    def __init__(self, center):
        Actor.__init__(self, 'bomb')
        sounds.bomb_drop.play()
        self.alive = True
        self.center = center
        self.vel = 5

    def update(self):
        self.y += self.vel
        if self.top > HEIGHT:
            self.alive = False

        if self.colliderect(game.ship):

            if timer.get_last_hit_in_seconds() > 3:
                game.ship.hit()
                timer.set_hit_time()
            else:
                pass

            self.alive = False


class Game:
    def __init__(self):
        self.ship = Ship()
        self.rockets = []
        self.ufos = []
        self.bombs = []


def make_ufo_squadron(n_ufos):
    return [UFO(i * 40, -i * 40) for i in range(0, n_ufos)]


def decide(chance):
    return random.random() < chance


def on_key_down():
    if keyboard.space:
        game.ship.launch_rocket()


def update():
    for actor in game.rockets + game.bombs + game.ufos:
        actor.update()
    game.ship.update()

    game.rockets = [r for r in game.rockets if r.alive]
    game.ufos = [u for u in game.ufos if u.alive]
    game.bombs = [b for b in game.bombs if b.alive]

    if len(game.ufos) == 0:
        game.ufos = make_ufo_squadron(10)


def draw():
    screen.fill((255, 255, 255))
    # screen.draw.rect(BOX, RED)
    points = myfont.render('Points: ' + str(counter.get_points()) + ' (' + player.get_name() + ')', False, (0, 0, 0))
    screen.blit(points, (0, 0))

    # highscore = myfont.render('Highscore: ' + str(counter.get_highscore()[1]) + ' (' + counter.get_highscore()[0] + ')',
    #                           False, (0, 0, 0))

    highscore_first = myfont.render('1. ' + str(counter.first["player"]) + ' (' + str(counter.first["score"]) + ')',
                              False, (0, 0, 0))

    highscore_second = myfont.render('2. ' + str(counter.second["player"]) + ' (' + str(counter.second["score"]) + ')',
                              False, (0, 0, 0))

    highscore_third = myfont.render('3.  ' + str(counter.third["player"]) + ' (' + str(counter.third["score"]) + ')',
                              False, (0, 0, 0))

    screen.blit(highscore_first, (700, 0))
    screen.blit(highscore_second, (700, 35))
    screen.blit(highscore_third, (700, 70))

    leben = myfont.render('Leben: ' + str(3 - counter.get_ship_hit_counter()), False, (0, 0, 0))
    screen.blit(leben, (0, 35))

    for actor in game.rockets + game.bombs + game.ufos:
        actor.draw()
    game.ship.draw()


name = argv[1]
print('Name' + name)

player = Player()
player.set_name(name)

timer = Timer()

counter = Counter()
game = Game()
pygame.font.init()  # you have to call this at the start,
# if you want to use this module.
myfont = pygame.font.SysFont('Comic Sans MS', 30)
pygame.mixer.quit()
pygame.mixer.init(44100, -16, 2, 1024)
time.sleep(1)
pgzrun.go()
