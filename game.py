from __future__ import print_function
import math
from CYLGame import GameLanguage
from CYLGame import Game
from CYLGame import MessagePanel
from CYLGame import MapPanel
from CYLGame import StatusPanel
from CYLGame import PanelBorder


DEBUG = False


class Ski(Game):
    MAP_WIDTH = 60
    MAP_HEIGHT = 30
    SCREEN_WIDTH = 60
    SCREEN_HEIGHT = MAP_HEIGHT + 6
    MSG_START = 20
    MAX_MSG_LEN = SCREEN_WIDTH - MSG_START - 1
    CHAR_WIDTH = 16
    CHAR_HEIGHT = 16
    GAME_TITLE = "Ski"
    CHAR_SET = "terminal16x16_gs_ro.png"

    SENSE_DIST = 20

    LEVELUP_RESPONSES = ["The forest seems to be getting more dense!", "Are there more trees here or what?", "Watch out!", "Better pay attention!"]

    ROBOT_CRASH_RESPONSES = ["**CRASH!!!***", "KABL00IE!", "*SMASH* CLATTER! *TINKLE*", "KA-B00M!", "!!B00M!!", "BING B0NG CLANK!"]

    NUM_OF_ROCKS_START = 30
    NUM_OF_TREES_START = 30
    MAX_TURNS = 300

    PLAYER = '@'
    STAIRS = '>'
    WRECKAGE = '<'
    EMPTY = ' '
    ROBOT = 'O'
    ROCK = chr(15)
    TREE = chr(30)

    def __init__(self, random):
        self.random = random
        self.running = True
        self.touching_bot = False
        self.touching_wreckage = False
        centerx = self.MAP_WIDTH / 2
        centery = self.MAP_HEIGHT / 2
        self.player_pos = [centerx, centery]
        self.score = 0
        self.objects = []
        self.turns = 0
        self.level = 1
        self.msg_panel = MessagePanel(self.MSG_START, self.MAP_HEIGHT + 1, self.SCREEN_WIDTH - self.MSG_START, 5)
        self.status_panel = StatusPanel(0, self.MAP_HEIGHT + 1, self.MSG_START, 5)
        self.panels = [self.msg_panel, self.status_panel]
        self.msg_panel.add("Velkommen to Robot Backcountry Skiing!")
        self.msg_panel.add("Move left and right! Don't crash!")

        self.__create_map()

    def __create_map(self):
        self.map = MapPanel(0, 0, self.MAP_WIDTH, self.MAP_HEIGHT + 1, self.EMPTY,
                            border=PanelBorder.create(bottom="-"))

        self.panels += [self.map]
        self.place_stairs(1)
        self.place_objects(self.TREE, self.NUM_OF_ROCKS_START)
        self.place_objects(self.ROCK, self.NUM_OF_TREES_START)
        self.map[(self.player_pos[0], self.player_pos[1])] = self.PLAYER
        if DEBUG:
            print(self.get_vars_for_bot())  # need sensors before turn

    def shortest_distance_between(self, x1, y1, x2, y2):
        dists = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                a_x, a_y = x1 + (self.MAP_WIDTH * i), y1 + (self.MAP_HEIGHT * j)
                d_x, d_y = math.abs(a_x - x2), math.abs(a_y - y2)
                dists += [max(d_x, d_y)]
        return min(dists)

    def shortest_distance_and_direction(self, x1, y1, x2, y2):
        dists = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                a_x, a_y = x1 + (self.MAP_WIDTH * i), y1 + (self.MAP_HEIGHT * j)
                d_x, d_y = abs(a_x - x2), abs(a_y - y2)
                direction = [a_x - x2, a_y - y2]
                if direction[0] > 0:
                    direction[0] = 1
                elif direction[0] < 0:
                    direction[0] = -1
                if direction[1] > 0:
                    direction[1] = 1
                elif direction[1] < 0:
                    direction[1] = -1
                dists += [(max(d_x, d_y), direction)]
        dists.sort()
        return dists[0]

    def place_stairs(self, count):
        self.place_objects(self.STAIRS, count)

    def place_bots(self, count):
        self.place_objects(self.ROBOT, count)

    def place_objects(self, char, count):
        placed_objects = 0
        while placed_objects < count:
            x = self.random.randint(0, self.MAP_WIDTH - 1)
            y = self.random.randint(0, self.MAP_HEIGHT - 1)

            if self.map[(x, y)] == self.EMPTY:
                self.map[(x, y)] = char
                placed_objects += 1

    def make_new_row(self, level):
        for x in range(self.MAP_WIDTH):
            here = self.random.randint(0, 9)
            if here == 0:
                which = self.random.randint(0,1)
                if which == 0:
                    self.map[(x, 1)] = self.ROCK
                else:
                    self.map[(x, 1)] = self.TREE

    def shift_map(self):
        # shift all rows down
        for y in reversed(range(self.MAP_HEIGHT - 1)):
            for x in range(self.MAP_WIDTH):
                self.map[(x, y+1)] = self.map[(x, y)]
                self.map[(x, y)] = self.EMPTY

        self.make_new_row(self.level)



    def handle_key(self, key):
        self.turns += 1
        self.score += 1

        if self.turns % 30 == 0:
            self.level += 1

        self.map[(self.player_pos[0], self.player_pos[1])] = self.EMPTY
        if key == "w":
            self.player_pos[1] -= 1
        if key == "s":
            self.player_pos[1] += 1
        if key == "a":
            self.player_pos[0] -= 1
        if key == "d":
            self.player_pos[0] += 1
        if key == "q":
            self.player_pos[1] -= 1
            self.player_pos[0] -= 1
        if key == "e":
            self.player_pos[1] -= 1
            self.player_pos[0] += 1
        if key == "c":
            self.player_pos[1] += 1
            self.player_pos[0] += 1
        if key == "z":
            self.player_pos[1] += 1
            self.player_pos[0] -= 1
        if key == "t":
            self.msg_panel += ["TELEP0RT!"]
            self.player_pos[0] = self.random.randint(0, self.MAP_WIDTH - 1)
            self.player_pos[1] = self.random.randint(0, self.MAP_HEIGHT - 1)

        if key == "Q":
            self.running = False
            return

        self.player_pos[0] %= self.MAP_WIDTH
        self.player_pos[1] %= self.MAP_HEIGHT

        # shift the map
        self.shift_map()

        # if player gets to the stairs, the other robots don't get a
        # chance to take their turn
        if self.map[(self.player_pos[0], self.player_pos[1])] == self.STAIRS:
            self.score += self.level * 10
            self.msg_panel += [self.random.choice(list(set(self.LEVELUP_RESPONSES) - set(self.msg_panel.get_current_messages())))]
            self.level += 1

            # initialize new map
            self.__create_map()

        # if a bot is touching a player, then set touching_bot to TRUE
        # and also update the map to show the attacking robot
        if self.map[(self.player_pos[0], self.player_pos[1])] == self.ROBOT:
            self.touching_bot = True

        elif self.map[(self.player_pos[0], self.player_pos[1])] == self.WRECKAGE:
            # if a player is touching wreckage, set touching_wreckage to
            # true
            self.touching_wreckage = True
        else:
            # in the previous two cases, the player died and we don't
            # want to draw the "live" player over the object that killed
            # them. In *this* case, the move was a success, so we want
            # to draw the player onto the spot.
            self.map[(self.player_pos[0], self.player_pos[1])] = self.PLAYER

        # go through the map and calculate moves for every robot based
        # on player's position

        robots = self.map.get_all_pos(self.ROBOT)

        # sort robots list by closeness to player -- fixes issue #1
        robots = sorted(robots, key=lambda x: self.shortest_distance_and_direction(x[0], x[1], self.player_pos[0], self.player_pos[1])[0])

        # move each robot once
        for x, y in robots:
            if DEBUG:
                print("found robot at (%d,%d)" % (x, y))
            if self.map[(x, y)] == self.WRECKAGE:
                # this robot got wrecked before it could move...
                # next robot please.
                continue

            # find the direction towards the player
            x_dir, y_dir = self.find_closest_player(x, y)

            if DEBUG:
                print("\tI'm going to move (%d,%d) towards player" % (x_dir, y_dir))

            # get new location modulo map size
            newpos = ((x + x_dir) % self.MAP_WIDTH, (y + y_dir) % self.MAP_HEIGHT)

            if self.map[newpos] == self.STAIRS:
                # robot won't step on stairs (7 cycles bad robot luck)
                continue

            # erase robot in prep to move locations
            self.map[(x, y)] = self.EMPTY

            # draw the new robot into position and check for collisions
            if self.map[newpos] == self.ROBOT or self.map[newpos] == self.WRECKAGE:
                # already a robot here -- collision!
                if DEBUG:
                    print("collision with robot at (%s)!" % str(newpos))
                self.map[newpos] = self.WRECKAGE
                self.msg_panel += [self.random.choice(list(set(self.ROBOT_CRASH_RESPONSES) - set(self.msg_panel.get_current_messages())))]
                self.score += 10
            else:
                self.map[newpos] = self.ROBOT

            # if a bot is touching a player, then set touching_bot to TRUE
            # and also update the map to show the attacking robot
            if self.map[(self.player_pos[0], self.player_pos[1])] == self.ROBOT:
                self.touching_bot = True
                break

        # vars should be gotten at the end of handle_turn, because vars
        # affect the *next* turn...
        if DEBUG:
            print(self.get_vars_for_bot())

    def is_running(self):
        return self.running

    # find the closest thing (foo) in the map relative to the given
    # x and y parameter (useful for finding stairs, players, etc.)
    def find_closest_foo(self, x, y, foo):
        foo_pos_dist = []
        for pos in self.map.get_all_pos(foo):
            for i in range(-1, 2):
                for j in range(-1, 2):
                    a_x, a_y = pos[0] + (self.SCREEN_WIDTH * i), pos[1] + (self.SCREEN_HEIGHT * j)
                    dist = math.sqrt((a_x - x)**2 + (a_y - y)**2)
                    direction = [a_x - x, a_y - y]
                    if direction[0] > 0:
                        direction[0] = 1
                    elif direction[0] < 0:
                        direction[0] = -1
                    if direction[1] > 0:
                        direction[1] = 1
                    elif direction[1] < 0:
                        direction[1] = -1
                    foo_pos_dist += [(dist, direction)]

        foo_pos_dist.sort()
        if len(foo_pos_dist) > 0:
            return foo_pos_dist[0][1]
        else:
            raise Exception("We can't find the foo you're looking for!")

    def find_closest_player(self, x, y):
        foo_pos_dist = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                a_x, a_y = self.player_pos[0] + (self.SCREEN_WIDTH * i), self.player_pos[1] + (self.SCREEN_HEIGHT * j)
                dist = math.sqrt((a_x - x)**2 + (a_y - y)**2)
                direction = [a_x - x, a_y - y]
                if direction[0] > 0:
                    direction[0] = 1
                elif direction[0] < 0:
                    direction[0] = -1
                if direction[1] > 0:
                    direction[1] = 1
                elif direction[1] < 0:
                    direction[1] = -1
                foo_pos_dist += [(dist, direction)]

        foo_pos_dist.sort()
        if len(foo_pos_dist) > 0:
            return foo_pos_dist[0][1]
        else:
            raise Exception("We can't find the foo you're looking for!")

    def get_vars_for_bot(self):
        bot_vars = {}

        # get values for x_dir and y_dir to direct player towards stairs
        x_dir, y_dir = self.find_closest_foo(self.player_pos[0], self.player_pos[1], self.STAIRS)

        x_dir_to_char = {-1: ord("a"), 1: ord("d"), 0: 0}
        y_dir_to_char = {-1: ord("w"), 1: ord("s"), 0: 0}

        bot_vars = {"x_dir": x_dir_to_char[x_dir], "y_dir": y_dir_to_char[y_dir],
                    "sense_n": 0, "sense_s": 0, "sense_e": 0, "sense_w": 0,
                    "sense_ne": 0, "sense_nw": 0, "sense_se": 0, "sense_sw": 0,
                    "junk_e": 0, "junk_w": 0, "junk_n": 0, "junk_s": 0,
                    "junk_ne": 0, "junk_se": 0, "junk_sw": 0, "junk_se": 0,
                    "numbots": 0, "level": 0}

        # detect wreckage in the 8 movement directions:

        if self.map[((self.player_pos[0]+1)%self.MAP_WIDTH, self.player_pos[1])] == self.WRECKAGE:
            bot_vars["junk_e"] = 1
            if DEBUG:
                print("junk to east")

        if self.map[((self.player_pos[0]-1)%self.MAP_WIDTH, self.player_pos[1])] == self.WRECKAGE:
            bot_vars["junk_w"] = 1
            if DEBUG:
                print("junk to west")

        if self.map[(self.player_pos[0], (self.player_pos[1]-1)%self.MAP_HEIGHT)] == self.WRECKAGE:
            bot_vars["junk_n"] = 1
            if DEBUG:
                print("junk to north")

        if self.map[(self.player_pos[0], (self.player_pos[1]+1)%self.MAP_HEIGHT)] == self.WRECKAGE:
            bot_vars["junk_s"] = 1
            if DEBUG:
                print("junk to south")

        if self.map[((self.player_pos[0]+1)%self.MAP_WIDTH, (self.player_pos[1]-1)%self.MAP_HEIGHT)] == self.WRECKAGE:
            bot_vars["junk_ne"] = 1
            if DEBUG:
                print("junk to northeast")

        if self.map[((self.player_pos[0]-1)%self.MAP_WIDTH, (self.player_pos[1]-1)%self.MAP_HEIGHT)] == self.WRECKAGE:
            bot_vars["junk_nw"] = 1
            if DEBUG:
                print("junk to northwest")

        if self.map[((self.player_pos[0]+1)%self.MAP_WIDTH, (self.player_pos[1]+1)%self.MAP_HEIGHT)] == self.WRECKAGE:
            bot_vars["junk_se"] = 1
            if DEBUG:
                print("junk to southeast")

        if self.map[((self.player_pos[0]-1)%self.MAP_WIDTH, (self.player_pos[1]+1)%self.MAP_HEIGHT)] == self.WRECKAGE:
            bot_vars["junk_sw"] = 1
            if DEBUG:
                print("junk to southwest")

        robots = self.map.get_all_pos(self.ROBOT)

        bot_vars["numbots"] = len(robots)

        bot_vars["level"] = self.level


        x_dir_to_str = {-1: "w", 1: "e", 0: ""}
        y_dir_to_str = {-1: "n", 1: "s", 0: ""}

        # set sensor value to distance to closest bot in range
        for robot_x, robot_y in robots:
            dist, direction = self.shortest_distance_and_direction(robot_x, robot_y, self.player_pos[0], self.player_pos[1])
            if DEBUG:
                print("dist: %s direction: %s" % (dist, direction))
            dir_x, dir_y = direction
            dir_str = y_dir_to_str[dir_y] + x_dir_to_str[dir_x]
            if dir_str == "":
                continue
            if bot_vars["sense_" + dir_str] == 0:
                bot_vars["sense_" + dir_str] = dist
            elif bot_vars["sense_" + dir_str] > dist:
                bot_vars["sense_" + dir_str] = dist

        return bot_vars

    @staticmethod
    def default_prog_for_bot(language):
        if language == GameLanguage.LITTLEPY:
            return open("bot.lp", "r").read()

    @staticmethod
    def get_intro():
        return open("intro.md", "r").read()

    @staticmethod
    def get_move_consts():
        consts = Game.get_move_consts()
        consts.update({"teleport": ord("t")})
        return consts

    @staticmethod
    def get_move_names():
        names = Game.get_move_names()
        names.update({ord("t"): "Teleport"})
        return names

    def get_score(self):
        return self.score

    def draw_screen(self, libtcod, console):
        # End of the game
        if self.turns >= self.MAX_TURNS:
            self.running = False
            self.msg_panel.add("You are out of moves.")
        elif self.touching_bot:
            self.running = False
            self.msg_panel += ["A robot got you! :( "]
        elif self.touching_wreckage:
            self.running = False
            self.msg_panel += ["You ran into a pile of junk! :("]

        if not self.running:
            self.msg_panel += ["GAME 0VER: Score:" + str(self.score)]

        libtcod.console_set_default_foreground(console, libtcod.white)

        # Update Status
        self.status_panel["Score"] = self.score
        self.status_panel["Move"] = str(self.turns) + " of " + str(self.MAX_TURNS)

        for panel in self.panels:
            panel.redraw(libtcod, console)


if __name__ == '__main__':
    from CYLGame import run
    run(Ski)
