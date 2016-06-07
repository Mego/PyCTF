#!/usr/bin/env python3

from enum import Enum
from subprocess import Popen, PIPE, TimeoutExpired
import os
import random
from itertools import product
import sys

# Only up to 24 players on each team are supported currently.
# I don't foresee that being a huge issue.

class CTFTeam(Enum):
    Red = 0
    Blue = 1
    
    
class CTFMapSquare(Enum):
    Wall = 0
    Space = 1
    RedPlayer = 2
    BluePlayer = 3
    RedFlag = 4
    BlueFlag = 5
    FlagStand = 6
    
    
MAP_SQUARE_SELECTOR = {
    '#': CTFMapSquare.Wall,
    '.': CTFMapSquare.Space,
    '!': CTFMapSquare.FlagStand,
}
    
    
class CTFMap:
    def __init__(self, text, players):
        self.map = []
        self.textmap = [[c for c in line] for line in text.splitlines()]
        self.redspawns = []
        self.bluespawns = []
        self.redflag = None
        self.blueflag = None
        self.redstand = None
        self.bluestand = None
        for y,line in enumerate(text.splitlines()):
            mapline = []
            for x,c in enumerate(line):
                mapline.append(MAP_SQUARE_SELECTOR[c])
                if MAP_SQUARE_SELECTOR[c] == CTFMapSquare.FlagStand:
                    if self.redflag is None:
                        self.redflag = (x,y)
                        self.redstand = (x,y)
                    else:
                        self.blueflag = (x,y)
                        self.bluestand = (x,y)
                    if len(self.redspawns) == 0:
                        self.redspawns.extend([(i,j) for (i,j) in product(range(len(line)),range(len(text))) if abs(y-j) <= 2 and abs(x-i) <= 2 and (x!=i or y!=j)])
                    else:
                        self.bluespawns.extend([(i,j) for (i,j) in product(range(len(line)),range(len(text))) if abs(y-j) <= 2 and abs(x-i) <= 2 and (x!=i or y!=j)])
            self.map.append(mapline)
        self.players = dict()
        if len(players) % 2 != 0:
            players.append(['Caboose', ['python3', 'caboose.py']])
        random.shuffle(players)
        team = CTFTeam.Red
        spawnsused = []
        for name, cmd in players:
            player = CTFPlayer(name, team, cmd)
            spawnlist = self.redspawns if team == CTFTeam.Red else self.bluespawns
            spawn = random.choice([x for x in spawnlist if x not in spawnsused])
            spawnsused.append(spawn)
            player.loc = spawn
            self.players[name] = player
            team = CTFTeam.Blue if team == CTFTeam.Red else CTFTeam.Red
            
    def do_move(self, player, target):
        pass
        
    def do_stab(self, player, target):
        pass
        
    def do_drop(self, player):
        pass
        
    def do_pickup(self, player):
        pass
        
    def render_map(self, player):
        map = [x.copy() for x in self.textmap]
        for p in self.players.values():
            px,py = p.loc
            sym = None
            if p is player:
                if p.flag is None:
                    sym = '@'
                else:
                    sym = '%$'[p.flag == p.team]
            elif p.team == player.team:
                if p.flag is None:
                    sym = 'p'
                else:
                    sym = 'cs'[p.flag == p.team]
            else:
                if p.flag is None:
                    sym = 'P'
                else:
                    sym = 'CS'[p.flag == p.team]
            map[py][px] = sym
        rx,ry = self.redstand
        map[ry][rx] = '!'
        bx,by = self.bluestand
        map[by][bx] = '!'
        if isinstance(self.redflag, tuple):
            rx,ry = self.redflag
            map[ry][rx] = ('Ff'[player.team == CTFTeam.Red])
        if isinstance(self.blueflag, tuple):
            bx,by = self.blueflag
            map[by][bx] = ('fF'[player.team == CTFTeam.Red])
        return '\n'.join([''.join(line) for line in map])

class CTFPlayer:
    def __init__(self, name, team, cmd):
        self.cmd = cmd
        self.name = name
        self.data = name + '.txt'
        self.team = team
        self.loc = None
        self.flag = None
        
    def run(self, bot_input, timeout=None):
        proc = Popen(cmd+[self.data], stdin=PIPE, stdout=PIPE, universal_newlines=True)
        try:
            return proc.communicate(input, timeout)[0]
        except TimeoutExpired:
            proc.kill()
            return None
            
    def check_data_file(self):
        file_size = os.stat(self.data).st_size
        if file_size > 1024**2:
            os.system('tail -c 1048576 {0} > {0}'.format(self.data))
            
    def get_char(self, other):
        if self is other:
            return '@'
        elif self.team is other.team:
            return 'p'
        else:
            return 'P'
    
if __name__ == '__main__':
    with open(sys.argv[1]) as mapfile:
        map = CTFMap(mapfile.read(), [['dummy', ['python3', 'players/caboose.py']], ['Caboose', ['python3', 'players/caboose.py']]])
        print(map.render_map(map.players['dummy']))