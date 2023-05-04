'''
 * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.
 * Originally developed by Mark Riedl.
 * Last edited by Mark Riedl 05/2015
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''
#Collaborated with Srajan Dube on the idea of using the location of the hunter and potentially stopping agents when it's invisible
#Collaborated with Pranav Mahesh on the idea of using a random offset
#Author: Pranav Manjunath

import sys, pygame, math, numpy, random, time, copy
from pygame.locals import * 

from constants import *
from utils import *
from core import *
from moba import *

minionCount = 0

class MyMinion(Minion):
    
    def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
        global minionCount
        Minion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)
        self.states = [Idle]
        ### Add your states to self.states (but don't remove Idle)
        ### YOUR CODE GOES BELOW HERE ###
        minionCount += 1
        self.states.append(Move)
        self.states.append(Attack)
        print("Minion Count: " + str(minionCount))
        ### YOUR CODE GOES ABOVE HERE ###

    def start(self):
        Minion.start(self)
        self.changeState(Idle)





############################
### Idle
###
### This is the default state of MyMinion. The main purpose of the Idle state is to figure out what state to change to and do that immediately.

class Idle(State):
    
    def enter(self, oldstate):
        State.enter(self, oldstate)
        # stop moving
        self.agent.stopMoving()
    
    def execute(self, delta = 0):
        State.execute(self, delta)
        ### YOUR CODE GOES BELOW HERE ###
        towers = self.agent.world.getEnemyTowers(self.agent.getTeam())
        self.agent.changeState(Move, towers)
        ### YOUR CODE GOES ABOVE HERE ###
        return None


##############################
### Taunt
###
### This is a state given as an example of how to pass arbitrary parameters into a State.
### To taunt someome, Agent.changeState(Taunt, enemyagent)

class Taunt(State):

    def parseArgs(self, args):
        self.victim = args[0]

    def execute(self, delta = 0):
        if self.victim is not None:
            print("Hey " + str(self.victim) + ", I don't like you!")
        self.agent.changeState(Idle)

##############################
### YOUR STATES GO HERE:

class Move(State):
    
    def parseArgs(self, args):
        self.towers = args[0]
                
    def enter(self, oldstate):
        base = self.agent.world.getEnemyBases(self.agent.getTeam())[0] if len(self.agent.world.getEnemyBases(self.agent.getTeam())) > 0 else None
        if len(self.towers) > 0:
            self.target = sorted(self.towers, key=lambda x: x.getHitpoints())[0]
        elif base:
            self.target = base
        else:
            self.target = None
            self.agent.changeState(Idle)
            
    def execute(self, delta = 0):
        self.hunter = None
        for npc in self.agent.world.getEnemyNPCs(self.agent.getTeam()):
            if not isinstance(npc, Minion):
                self.hunter = npc
                break
        if self.hunter is not None and distance(self.agent.getLocation(), self.hunter.getLocation()) < 450:
            self.agent.stopMoving()
        elif distance(self.agent.position, self.target.position) < 150:
            self.agent.stopMoving()
            self.agent.turnToFace(self.target.getLocation())
            self.agent.shoot()
            self.agent.changeState(Attack, self.target)
        elif not self.agent.isMoving() and self.target.isAlive():
            self.agent.navigateTo((self.target.position[0] + random.randrange(10, 80, 10), self.target.position[1] + random.randrange(10, 80, 10)))
        elif not self.target.isAlive():
            self.agent.changeState(Idle)
        if self.hunter is not None or distance(self.agent.position, self.target.position) >= 150:
            for npc in self.agent.world.getEnemyNPCs(self.agent.getTeam()):
                if distance(self.agent.position, npc.position) < 150:
                    self.agent.turnToFace(npc.position)
                    self.agent.shoot()
            
class Attack(State):
    
    def parseArgs(self, args):
        self.target = args[0]
    
    def execute(self, delta = 0):
        State.execute(self, delta)
        if self.target is not None and self.target.isAlive():
            self.agent.turnToFace(self.target.getLocation())
            self.agent.shoot()
            if not self.agent.isMoving():
                self.agent.navigateTo((self.target.position[0] + 20, self.target.position[1]))
        elif not self.target.isAlive():
            self.agent.changeState(Idle)
        return None