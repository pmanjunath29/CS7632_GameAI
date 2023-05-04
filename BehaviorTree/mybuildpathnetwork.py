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

import sys, pygame, math, numpy, random, time, copy, operator
from pygame.locals import *

from constants import *
from utils import *
from core import *

# Creates the path network as a list of lines between all path nodes that are traversable by the agent.
def myBuildPathNetwork(pathnodes, world, agent = None):
    lines = []
    ### YOUR CODE GOES BELOW HERE ###
    print(pathnodes, world, agent)
    agentradius = world.agent.getRadius()
    for n1 in pathnodes:
        for n2 in pathnodes:
            if n1 is n2:
                continue # trivial path
            if insideObstacle(n1, world.getObstacles()):
                continue # invalid path node
            if insideObstacle(n2, world.getObstacles()):
                continue # invalid path node
            pline = (n1, n2)
            worldlines = world.getLinesWithoutBorders()
            dist = numpy.inf # distance to nearest obstacle
            for wline in worldlines:
                if rayTrace(n1, n2, wline) is not None:
                    dist = 0.
                    break
                pwlines = (pline, wline)
                for i in (0, 1):
                    for j in (0, 1):
                        # get distance from one of the lines to one of the other
                        # line endpoints
                        curdist = minimumDistance(pwlines[i], pwlines[(i+1)%2][j])
                        dist = min(curdist, dist)
            if dist >= agentradius:
                lines.append(pline)
    ### YOUR CODE GOES ABOVE HERE ###
    return lines
