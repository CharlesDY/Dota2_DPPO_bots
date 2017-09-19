#we can use simulator to train the bots
import math
import sys
from .Config import Config
from .Event import Event, EventQueue
from .Creep import Creep
from .Sprite import Sprite

def spawn_fn(engine, t):
    print("spawn")
    engine.sprites += [Creep(engine,"Radiant","MeleeCreep") for i in range(5)]
    engine.sprites += [Creep(engine,"Dire","MeleeCreep") for i in range(5)]
    #engine.event_queue.enqueue(Event(t + 30,spawn_fn,(engine, t + 30)))

class DotaSimulator(object):
    def __init__(self, init_pos, canvas = None):
        self.self_input = [None,None]
        self.pos = init_pos[:]
        self.self_input[-1] = self.pos[-1] / Config.map_div
        self.self_input[-2] = self.pos[-2] / Config.map_div
        self.last_d = self.d()

        self.delta_tick = 1.0 / Config.tick_per_second
        self.tick_time = 0.0
        self.event_queue = EventQueue()
        self.sprites = []

        self.canvas = canvas

        self.event_queue.enqueue(Event(30.0,spawn_fn,(self,30.0)))
    
    def d(self):
        dist2_0_0 = math.hypot(self.pos[0],self.pos[1])
        dist2midline = abs( (self.pos[0] - self.pos[1]) / math.sqrt(2))
        return dist2_0_0

    def reward(self):
        _d = self.d()
        r = (self.last_d - _d) / 100.0 - _d / 10000.0
        self.last_d = _d
        return r

    def draw(self):
        for sprite in self.sprites:
            sprite.draw()
    
    def tick_tick(self):
        self.tick_time += self.delta_tick
    
    def get_time(self):
        return self.tick_time

    def loop(self):
        print("time",self.tick_time)
        #process events
        while True:
            event = self.event_queue.fetch(self.tick_time)
            if event != None:
                event.activate()
                print("activate")
            else:
                break
        
        for sprite in self.sprites:
            sprite.step()
        
        for sprite in self.sprites:
            sprite.move()
        
        dead_sprites = []
        for sprite in self.sprites:
            if sprite.HP <= 0.0:
                dead_sprites.append(sprite)
        
        for d in dead_sprites:
            self.sprites.remove(d)
    
    def step(self,action):
        a  = math.atan2(*action)

        if math.isnan(a):
            print("found nan")
            sys.exit(-1)
        
        if not (action[0] == 0.0 and action[1] == 0.0):
            self.pos[0] += Config.velocity * math.cos(a) * Config.delta_time
            self.pos[1] += Config.velocity * math.sin(a) * Config.delta_time

        if self.pos[0] > Config.bound_length:
            self.pos[0] = Config.bound_length
        if self.pos[1] > Config.bound_length:
            self.pos[1] = Config.bound_length
        if self.pos[0] < -Config.bound_length:
            self.pos[0] = -Config.bound_length
        if self.pos[1] < -Config.bound_length:
            self.pos[1] = -Config.bound_length

        self.self_input[-1] = self.pos[-1] / Config.map_div
        self.self_input[-2] = self.pos[-2] / Config.map_div

        state = {
            "self_input":self.self_input,
            "ally_input":[[0,0,0,0,0,0,0]]
        }

        reward = self.reward()

        done = False

        return (state,reward,done)

    
    def get_nearest_enemy(self, sprite):
        ret_pair = []
        for s in self.sprites:
            if s.side != sprite.side:
                tmp_d = Sprite.S2Sdistance(sprite,s)
                if tmp_d <= sprite.SightRange:
                    ret_pair.append((s,tmp_d))
        return sorted(ret_pair,key=lambda x:x[1])
