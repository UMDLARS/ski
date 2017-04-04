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

    ROBOT_CRASH_RESPONSES = ["OOF!", "OWWWIE!", "THAT'S GONNA LEAVE A MARK!", "BONK!"]
    ROBOT_HEART_RESPONSES = ["Wow, I feel a lot better!", "Shazam!", "That's the ticket!", "Yes!!!"]
    ROBOT_COIN_RESPONSES = ["Cha-ching!", "Badabing!", "Bling! Bling!", "Wahoo!"]
    ROBOT_FLYING_RESPONSES = ["I'm free as a bird now!", "It's a bird, it's a plane...", "Cowabunga!"]

    NUM_OF_ROCKS_START = 30
    NUM_OF_TREES_START = 30
    NUM_OF_SPIKES_START = 30
    NUM_OF_SNOWMAN_START = 30
    NUM_OF_COINS_START = 1
    NUM_OF_HEARTS_START = 1
    NUM_OF_JUMPS_START = 1
    MAX_TURNS = 300
    MAX_FLYING = 10

    PLAYER = '@'
    EMPTY = '\0'
    HEART = chr(3)
    COIN = chr(4)
    ROCK = chr(15)
    SPIKE = chr(16)
    SNOWMAN = chr(17)
    TRACKS = chr(29)
    TREE = chr(30)
    JUMP = chr(31)
    DEAD = chr(1)
    FLY = chr(2)
    CRASH = chr(8)
    HOUSE = chr(10)


    def __init__(self, random):
        self.sensor_coords = [] # variables for adjustable sensors from LP
        self.random = random
        self.running = True
        self.colliding = False
        self.on_top_of = None # stores a map item we're "on top of"
        self.flying = 0 # set to some value and decrement (0 == on ground)
        self.hp = 3
        self.player_pos = [self.MAP_WIDTH / 2, self.MAP_HEIGHT - 4]
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
        self.place_objects(self.TREE, self.NUM_OF_ROCKS_START)
        self.place_objects(self.ROCK, self.NUM_OF_TREES_START)
        self.place_objects(self.SNOWMAN, self.NUM_OF_SNOWMAN_START)
        self.place_objects(self.COIN, self.NUM_OF_COINS_START)
        self.place_objects(self.HEART, self.NUM_OF_HEARTS_START)
        self.place_objects(self.JUMP, self.NUM_OF_JUMPS_START)
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

    def place_objects(self, char, count, replace=False):
        placed_objects = 0
        while placed_objects < count:
            x = self.random.randint(0, self.MAP_WIDTH - 1)
            y = self.random.randint(0, self.MAP_HEIGHT - 1)

            if self.map[(x, y)] == self.EMPTY:
                self.map[(x, y)] = char
                placed_objects += 1
            elif replace == True:
                # we can replace objects that exist
                self.map[(x, y)] = char
                placed_objects += 1

    def make_new_row(self, level):
        for x in range(self.MAP_WIDTH):
            here = self.random.randint(0, self.MAX_TURNS)
            if here <= self.turns:
                which = self.random.randint(0,2)
                if which == 0:
                    self.map[(x, 1)] = self.ROCK
                elif which == 1:
                    self.map[(x, 1)] = self.TREE
                elif which == 2:
                    self.map[(x, 1)] = self.SNOWMAN

        if self.random.randint(0,100) > 33:
            self.map[(self.random.randint(0,self.MAP_WIDTH - 1), 1)] = self.HEART

        if self.random.randint(0,100) > 33:
            self.map[(self.random.randint(0,self.MAP_WIDTH - 1), 1)] = self.COIN

        if self.random.randint(0,100) > 33:
            self.map[(self.random.randint(0,self.MAP_WIDTH - 1), 1)] = self.JUMP

    def shift_map(self):
        # shift all rows down
        dx = (self.MAP_WIDTH / 2) - self.player_pos[0]
        self.map.shift_all((dx, 1), wrap_x=True)
        self.player_pos[0] += dx

        self.make_new_row(self.level)

        if self.on_top_of:
            self.map[(self.player_pos[0], self.player_pos[1] + 1)] = self.on_top_of
        elif self.flying < 1:
            if self.map[(self.player_pos[0], self.player_pos[1] + 1)] == self.EMPTY:
                self.map[(self.player_pos[0], self.player_pos[1] + 1)] = self.TRACKS

    def handle_key(self, key):
        self.turns += 1
        self.score += 1
        if self.flying > 0:
            self.flying -= 1
            self.msg_panel += ["In flight for " + str(self.flying) + " turns..."]
            if self.flying == 0:
                self.msg_panel += ["Back on the ground!"]

        if self.turns % 30 == 0:
            self.level += 1

        self.map[(self.player_pos[0], self.player_pos[1])] = self.EMPTY
        if key == "a":
            self.player_pos[0] -= 1
        if key == "d":
            self.player_pos[0] += 1
        if key == "w":
            None
        if key == "t":
            # horizontal-only teleporting code
            self.msg_panel += ["TELEPORT! (-1 HP)"]
            self.hp -= 1
            self.player_pos[0] = self.random.randint(0, self.MAP_WIDTH - 1)

        if key == "Q":
            self.running = False
            return

        # shift the map
        self.shift_map()
        
        self.colliding = False # reset colliding variable
        self.on_top_of = None

        if self.flying == 0:
            # check for various types of collisions (good and bad)
            if self.map[(self.player_pos[0], self.player_pos[1])] == self.ROCK:
                self.colliding = True
                self.on_top_of = self.ROCK
                self.hp -= 10
                self.msg_panel += [self.random.choice(list(set(self.ROBOT_CRASH_RESPONSES) - set(self.msg_panel.get_current_messages())))]

            elif self.map[(self.player_pos[0], self.player_pos[1])] == self.TREE:
                self.colliding = True
                self.on_top_of = self.TREE
                self.hp -= 2
                self.msg_panel += [self.random.choice(list(set(self.ROBOT_CRASH_RESPONSES) - set(self.msg_panel.get_current_messages())))]

            elif self.map[(self.player_pos[0], self.player_pos[1])] == self.SNOWMAN:
                self.colliding = True
                self.hp -= 1
                self.msg_panel += [self.random.choice(list(set(self.ROBOT_CRASH_RESPONSES) - set(self.msg_panel.get_current_messages())))]

            elif self.map[(self.player_pos[0], self.player_pos[1])] == self.HEART:
                if self.hp < 10:
                    self.hp += 1
                    self.msg_panel += [self.random.choice(list(set(self.ROBOT_HEART_RESPONSES) - set(self.msg_panel.get_current_messages())))]
                else:
                    self.msg_panel += ["Your HP is already full!"]

            elif self.map[(self.player_pos[0], self.player_pos[1])] == self.COIN:
                self.score += 25
                self.msg_panel += [self.random.choice(list(set(self.ROBOT_COIN_RESPONSES) - set(self.msg_panel.get_current_messages())))]

            elif self.map[(self.player_pos[0], self.player_pos[1])] == self.JUMP:
                self.on_top_of = self.JUMP
                self.flying += self.random.randint(2, self.MAX_FLYING)
                self.msg_panel += [self.random.choice(list(set(self.ROBOT_FLYING_RESPONSES) - set(self.msg_panel.get_current_messages())))]

        # draw player
        if self.flying < 1:
            if self.colliding:
                self.map[(self.player_pos[0], self.player_pos[1])] = self.CRASH
            else:
                self.map[(self.player_pos[0], self.player_pos[1])] = self.PLAYER

        else:
            self.map[(self.player_pos[0], self.player_pos[1])] = self.FLY

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

    def read_bot_state(self, state):
        # state.get('foo','') <-- set this to a default value that makes
        # sense
        # need to get LP values for:
        # s1x-s7x and s1y-s7y
        self.sensor_coords = []
        for i in range(7):
            x_name = "s" + str(i + 1) + "x"
            y_name = "s" + str(i + 1) + "y"
            self.sensor_coords.append((state.get(x_name, "0"), state.get(y_name, "0")))

    def get_vars_for_bot(self):
        bot_vars = {}

        # get x_dir and y_dir to direct player towards COIN / HP
        # self.map.get_x_y_dist_to_foo(self.player_pos, self.HEART)

        x_dir_to_char = {-1: ord("a"), 1: ord("d"), 0: 0}
        y_dir_to_char = {-1: ord("w"), 1: ord("s"), 0: 0}

        bot_vars = {"jump_x": 0, "jump_y": 0, "hp_x": 0, "hp_y": 0,
                "coin_x": 0, "coin_y": 0, "hp": 0, "flying": 0,
                "s1":0, "s2":0, "s3":0, "s4":0, "s5":0, "s6":0, "s7":0}

        (bot_vars["heart_x"], bot_vars["heart_y"]) = self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.HEART)
        (bot_vars["jump_x"], bot_vars["jump_y"]) = self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.JUMP)
        (bot_vars["coin_x"], bot_vars["coin_y"]) = self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.COIN)

        # go through self.sensor_coords and retrieve the map item at the
        # position relative to the player

        for i in range(7):
            if (i < len(self.sensor_coords)):
                sensor = "s" + str(i + 1)
                x_offset = self.sensor_coords[i][0]
                y_offset = self.sensor_coords[i][1]

                bot_vars[sensor] = ord(self.map[(self.player_pos[0] + int(x_offset), self.player_pos[1] + int(y_offset))])
                if bot_vars[sensor] == 64:
                    bot_vars[sensor] = 0

        bot_vars['hp'] = self.hp
        bot_vars['flying'] = self.flying

        x_dir_to_str = {-1: "w", 1: "e", 0: ""}
        y_dir_to_str = {-1: "n", 1: "s", 0: ""}

        if DEBUG:
            print(bot_vars)

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
        consts.update({"heart": 3})
        consts.update({"heart": 3})
        consts.update({"coin": 4})
        consts.update({"rock": 15})
        consts.update({"spikes": 16})
        consts.update({"snowman": 17})
        consts.update({"tracks": 29})
        consts.update({"tree": 30})
        consts.update({"jump": 31})
        consts.update({"house": 10})
        return consts

    @staticmethod
    def get_move_names():
        names = Game.get_move_names()
        names.update({ord("t"): "teleport"})
        names.update({3: "heart"})
        names.update({4: "coin"})
        names.update({15: "rock"})
        names.update({16: "spikes"})
        names.update({17: "snowman"})
        names.update({29: "tracks"})
        names.update({30: "tree"})
        names.update({31: "jump"})
        names.update({10: "house"})
        return names

    def get_score(self):
        return self.score

    def draw_screen(self, libtcod, console):
        # End of the game
        if self.turns >= self.MAX_TURNS:
            self.running = False
            self.msg_panel.add("You are out of moves.")
        elif self.hp <= 0:
            self.running = False
            self.msg_panel += ["You sustained too much damage!"]
            self.map[(self.player_pos[0], self.player_pos[1])] = self.DEAD

        if not self.running:
            self.msg_panel += ["GAME 0VER: Score:" + str(self.score)]

        libtcod.console_set_default_foreground(console, libtcod.white)

        # Update Status
        self.status_panel["Score"] = self.score
        self.status_panel["Move"] = str(self.turns) + " of " + str(self.MAX_TURNS)
        self.status_panel["HP"] = self.HEART * self.hp

        for panel in self.panels:
            panel.redraw(libtcod, console)


if __name__ == '__main__':
    from CYLGame import run
    run(Ski)
