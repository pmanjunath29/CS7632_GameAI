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
# Author: Pranav Manjunath
# I based my method of sorting the points of the polygon in clockwise order on the following baeldung article: https://www.baeldung.com/cs/sort-points-clockwise. 
# I got the idea for sorting the points in clockwise order from the following response to my Ed Discussion post: https://edstem.org/us/courses/32107/discussion/2428124
# I briefly discussed the idea of using clockwise or counterclockwise order after seeing this response with fellow student Srajan Dube. But we simply agreed it was a good idea and did not exchange any code.
# The repeated use of breaks and continues in this code is meant to provide efficiency and mesh optimization.

import sys, pygame, math, numpy, random, time, copy, operator
from pygame.locals import *

from constants import *
from utils import *
from core import *

# Creates a path node network that connects the midpoints of each nav mesh together
def myCreatePathNetwork(world, agent = None):
    nodes = []
    edges = []
    polys = []
    
    pts = world.getPoints()
    lines = world.getLines()
    obstacles = [obstacle.getPoints() for obstacle in world.getObstacles()]
    radius = world.getAgent().getMaxRadius()
    
    tri_lines = []
    
    for pt1 in pts:
        for pt2 in pts:
            if pt1 is not pt2:
                if rayTraceWorldNoEndPoints(pt1, pt2, lines + tri_lines) is None or ((pt1, pt2) in lines + tri_lines or (pt2, pt1) in lines + tri_lines):
                        for pt3 in pts:
                            if pt1 is not pt3 and pt2 is not pt3:
                                if rayTraceWorldNoEndPoints(pt2, pt3, lines + tri_lines) is None or ((pt2, pt3) in lines + tri_lines or (pt3, pt2) in lines + tri_lines):
                                    if rayTraceWorldNoEndPoints(pt3, pt1, lines + tri_lines) is None or ((pt1, pt3) in lines + tri_lines or (pt3, pt1) in lines + tri_lines):
                                        tri_lines.append((pt1, pt2))
                                        tri_lines.append((pt2, pt3))
                                        tri_lines.append((pt3, pt1))
                                        polys.append([pt1, pt2, pt3])
    filteredOut = []
    for i in range(len(polys)):
        if polys[i] not in filteredOut:
            perms = permutations(polys[i])
            obstacleFound = False
            for obstacle in obstacles:
                if obstacle in perms:
                    filteredOut.append(polys[i])
                    obstacleFound = True
                    break
            if obstacleFound:
                continue
            for j in range(i + 1, len(polys)):
                if polys[j] in perms:
                    filteredOut.append(polys[j])
    polys = [poly for poly in polys if poly not in filteredOut]
    
    filteredOut = []
    for i in range(len(polys)):
        for obstacle in obstacles:
            for pt in obstacle:
                if pointInsidePolygonPoints(pt, polys[i]) and not pointOnPolygon(pt, polys[i]):
                    filteredOut.append(polys[i])
                    break
            midpt1 = ((polys[i][0][0] + polys[i][1][0]) / 2.0, (polys[i][0][1] + polys[i][1][1]) / 2.0)
            midpt2 = ((polys[i][1][0] + polys[i][2][0]) / 2.0, (polys[i][1][1] + polys[i][2][1]) / 2.0)
            midpt3 = ((polys[i][2][0] + polys[i][0][0]) / 2.0, (polys[i][2][1] + polys[i][0][1]) / 2.0)
            if pointInsidePolygonPoints(midpt1, obstacle) and not pointOnPolygon(midpt1, obstacle):
                filteredOut.append(polys[i])
                continue
            if pointInsidePolygonPoints(midpt2, obstacle) and not pointOnPolygon(midpt2, obstacle):
                filteredOut.append(polys[i])
                continue
            if pointInsidePolygonPoints(midpt3, obstacle) and not pointOnPolygon(midpt3, obstacle):
                filteredOut.append(polys[i])
                continue
    polys = [poly for poly in polys if poly not in filteredOut]
    
    #Tried using a for loop here like for i in range(length) but kept running into index out of bounds issues so switched to a while loop instead
    i = 0
    length = len(polys)
    while i < length:
        j = 0
        while j < length:
            mutualPts = polygonsAdjacent(polys[i], polys[j])
            if polys[i] is not polys[j] and polygonsAdjacent(polys[i], polys[j]) is not False:
                jointPoly = polys[i] + polys[j]
                for pt in mutualPts:
                    jointPoly.remove(pt)
                jointPoly = sortPtsClockwiseOrder(jointPoly)
                if isConvex(jointPoly):
                    polys.append(jointPoly)
                    firstShape = polys[i]
                    secondShape = polys[j]
                    polys.remove(firstShape)
                    polys.remove(secondShape)
                    i = i - 1
                    length = length - 1
                    break
            j = j + 1
        i = i + 1
    
    for i in range(len(polys)):
        nodes.append(getCenter(polys[i]))
        for j in range(len(polys)):
            if polys[i] is not polys[j]:
                mutualPts = polygonsAdjacent(polys[i], polys[j])
                if mutualPts is not False:
                    midpoint = ((mutualPts[0][0] + mutualPts[1][0]) / 2.0, (mutualPts[0][1] + mutualPts[1][1]) / 2.0)
                    if midpoint not in nodes:
                        nodes.append(midpoint)
    
    pathNodes = []
    for i in range(len(polys)):
        for j in range(len(nodes)):
            for k in range(len(nodes)):
                if nodes[j] is not nodes[k]:
                    if ((pointOnPolygon(nodes[j], polys[i]) or pointInsidePolygonPoints(nodes[j], polys[i])) and pointOnPolygon(nodes[k], polys[i]) or pointInsidePolygonPoints(nodes[k], polys[i])) \
                    and (nodes[j], nodes[k]) not in edges and (nodes[k], nodes[j]) not in edges:
                        ang = math.atan2(nodes[j][1] - nodes[k][1], nodes[j][0] - nodes[k][0])
                        pt1_radius_dist_above = (nodes[j][0] + radius * math.cos(ang + (math.pi / 2)), nodes[j][1] + radius * math.sin(ang + (math.pi / 2)))
                        pt2_radius_dist_above = (nodes[k][0] + radius * math.cos(ang + (math.pi / 2)), nodes[k][1] + radius * math.sin(ang + (math.pi / 2)))
                        pt1_radius_dist_below = (nodes[j][0] + radius * math.cos(ang - (math.pi / 2)), nodes[j][1] + radius * math.sin(ang - (math.pi / 2)))
                        pt2_radius_dist_below = (nodes[k][0] + radius * math.cos(ang - (math.pi / 2)), nodes[k][1] + radius * math.sin(ang - (math.pi / 2)))
                        if not rayTraceWorld(nodes[j], nodes[k], lines) and not rayTraceWorld(pt1_radius_dist_above, pt2_radius_dist_above, lines) and not rayTraceWorld(pt1_radius_dist_below, pt2_radius_dist_below, lines):
                            edges.append((nodes[j], nodes[k]))
                            if nodes[j] not in pathNodes:
                                pathNodes.append(nodes[j])
                            if nodes[k] not in pathNodes:
                                pathNodes.append(nodes[k])
    nodes = pathNodes           
    return nodes, edges, polys

def permutations(poly):
    return [[poly[0], poly[1], poly[2]], [poly[0], poly[2], poly[1]], [poly[1], poly[0], poly[2]], [poly[1], poly[2], poly[0]], [poly[2], poly[0], poly[1]], [poly[2], poly[1], poly[0]]]

def getCenter(points):
    center = (0, 0)
    for point in points:
        center = (center[0] + point[0], center[1] + point[1])
    center = (center[0] / float(len(points)), center[1] / float(len(points)))
    return center

def sortPtsClockwiseOrder(points):
    center = getCenter(points)
    sortedByAng = []
    sortedPts = []
    for point in points:
        ang = math.atan2(point[1] - center[1], point[0] - center[0])
        sortedByAng.append((point, ang))
    sortedByAng.sort(key = lambda p:p[1])
    for val in sortedByAng:
        sortedPts.append(val[0])
    return sortedPts
        
    
	
