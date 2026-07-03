import pygame

import math
import random

import pyRecorder

#initialize pygame window
pygame.init()
screenWidth = 600
screenHeight = 600
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('Satisfying Collisions')

#fps display
clock = pygame.time.Clock()
def displayFPS(screen, font_size):
    font = pygame.font.SysFont(None, font_size)
    fps = round(clock.get_fps(), 1)
    fps_text = font.render(f"{fps}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))

#initialise pyrecorder
#pyrecorder = pyRecorder.Recorder()
t = 0

#CLASS DEFINITION -----------------------------------------------------------------------------------------------------------------------------------------

class Ball():
    def __init__(self, pos, radius, drag):
        balls.append(self)

        self.pos = pos
        self.radius = radius

        self.vel = (0, 0)
        self.drag = drag

    def draw_top(self):
        pygame.draw.circle(screen, (255, 255, 255), self.pos, self.radius, 1)
    
    def draw_shadow(self):
        pygame.draw.circle(screen, (0, 0, 0), (self.pos[0] + shadowOffsetX, self.pos[1] + shadowOffsetY), self.radius)

    def applyForce(self, force):
        self.vel = (self.vel[0] + force[0], self.vel[1] + force[1])

    def move(self, dTs):
        #apply drag
        self.vel = (self.vel[0] * self.drag, self.vel[1] * self.drag)

        #apply movement
        self.pos = (self.pos[0] + self.vel[0] * dTs * 60, self.pos[1] + self.vel[1] * dTs * 60)

        #bounce of screen edges
        if self.pos[0] + self.radius > screenWidth:
            self.vel = (self.vel[0] * -1, self.vel[1])
            self.pos = (screenWidth - self.radius, self.pos[1])

        if self.pos[0] - self.radius < 0:
            self.vel = (self.vel[0] * -1, self.vel[1])
            self.pos = (self.radius, self.pos[1])

        if self.pos[1] + self.radius > screenHeight:
            self.vel = (self.vel[0], self.vel[1] * -1)
            self.pos = (self.pos[0], screenHeight - self.radius)

        if self.pos[1] - self.radius < 0:
            self.vel = (self.vel[0], self.vel[1] * -1)
            self.pos = (self.pos[0], self.radius)

    def doBallCollision(self, balls):
        #check if coliding with any ball
        for ball in balls:
            otherBall = ball
            if otherBall != self:
                #get dist to other
                vecTo = (self.pos[0] - otherBall.pos[0], self.pos[1] - otherBall.pos[1])
                mag = math.sqrt(vecTo[0] ** 2 + vecTo[1] ** 2)
                if mag < self.radius * 2:
                    #do overlap adjustments
                    #adjustment of one ball = 1/2 of overlap; overlap = radius - mag
                    overlap = (self.radius * 2) - mag + 1e-12   # + 1e-12 to avoid double collision (both balls procces a collision) which prevents sticking
                    normalizedVecTo = (vecTo[0] / (mag + 1e-12), vecTo[1] / (mag + 1e-12))  # + 1e-12 to avoid division by zero

                    self.pos = (self.pos[0] + normalizedVecTo[0] * (overlap * 0.5), self.pos[1] + normalizedVecTo[1] * (overlap * 0.5))
                    otherBall.pos = (otherBall.pos[0] - normalizedVecTo[0] * (overlap * 0.5), otherBall.pos[1] - normalizedVecTo[1] * (overlap * 0.5))

                    #readjust vector to other ball to adjusted lenght
                    vecTo = (normalizedVecTo[0] * (self.radius * 2), normalizedVecTo[1] * (self.radius * 2))
                    mag = self.radius * 2

                    #math for getting the new velocities - The Coding Train "Elastic Collision in 2D": https://www.youtube.com/watch?v=dJNFPv9Mj-Y
                    vDiff = vSub(otherBall.vel, self.vel)

                    #self
                    numerator = vDot(vDiff, vecTo)
                    denominator = mag ** 2
                    dVA = vMul(vecTo, numerator / denominator)
                    self.vel = vSum(self.vel, dVA)

                    #other
                    dVB = vMul(vecTo, -numerator / denominator)
                    otherBall.vel = vSum(otherBall.vel, dVB)

    def doEdgeCollision(self, edges):
        for edge in edges:
            
            #get closest point on edge to center
            AB = (edge[1][0] - edge[0][0], edge[1][1] - edge[0][1])
            AP = (self.pos[0] - edge[0][0], self.pos[1] - edge[0][1])

            #project ball center to segment
            dot = AP[0]*AB[0] + AP[1]*AB[1]
            len_sq = AB[0]*AB[0] + AB[1]*AB[1]

            #clamp to line segment
            t = dot / len_sq
            t = max(0, min(1, t))
            
            closestPoint = (edge[0][0] + t * AB[0], edge[0][1] + t * AB[1])
            """pygame.draw.circle(screen, (255, 0, 0), closestPoint, 5)"""

            #check if ball close enough to be colliding
            vecTo = (self.pos[0] - closestPoint[0], self.pos[1] - closestPoint[1])
            distance_sq = vecTo[0] ** 2 + vecTo[1] ** 2

            if distance_sq <= self.radius ** 2:
                """pygame.draw.circle(screen, (0, 0, 255), closestPoint, 5)"""
                
                #adjust overlap
                dx = self.pos[0] - closestPoint[0]
                dy = self.pos[1] - closestPoint[1]
                dist = math.hypot(dx, dy)

                #check if center on edge (math errors)
                if dist == 0:
                    vecTo = (1, 0)
                else:
                    vecTo = (vecTo[0] / dist, vecTo[1] / dist)

                penetration = self.radius - dist

                if penetration > 0:
                    self.pos = (self.pos[0] + vecTo[0] * penetration, self.pos[1] + vecTo[1] * penetration)

                #deflect over normal
                length = math.hypot(vecTo[0], vecTo[1])
                vecTo = (vecTo[0] / length, vecTo[1] / length)

                dot = self.vel[0] * vecTo[0] + self.vel[1] * vecTo[1]
                self.vel = (self.vel[0] - 2 * dot * vecTo[0], self.vel[1] - 2 * dot * vecTo[1])

class Shape():
    def __init__(self, center, points, width, drawPolygon, finishLoop):
        shapes.append(self)

        self.center = center
        self.points = points
        self.width = width

        self.extra = 0
        if finishLoop:
            self.extra = 1

        self.drawPolygon = drawPolygon  #fill or nofill
        #also generate shadow points if drawing polygon
        self.shadowPoints = []
        if self.drawPolygon:
            for point in points:
                self.shadowPoints.append((point[0] + shadowOffsetX, point[1] + shadowOffsetY))

        #generate edges
        self.edges = []
        for i in range(len(self.points) - 1 + self.extra):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % len(self.points)]
            self.edges.append((p1, p2))
        
        #append to all edges    NOTE: edges != self.edges
        for edge in self.edges:
            edges.append(edge)

    def draw_top(self):
        if not self.drawPolygon:
            for edge in self.edges:
                pygame.draw.aaline(screen, (255, 255, 255), edge[0], edge[1])
        else:
            pygame.draw.polygon(screen, (255, 255, 255), self.points)
    
    def draw_shadow(self):
        if not self.drawPolygon:
            for edge in self.edges:
                pygame.draw.line(screen, (0, 0, 0), (edge[0][0] + shadowOffsetX, edge[0][1] + shadowOffsetY), (edge[1][0] + shadowOffsetX, edge[1][1] + shadowOffsetY), self.width)
        else:
            pygame.draw.polygon(screen, (0), self.shadowPoints)

    def rotate(self, angleDeg):
        self.points = rotatePointsAroundCenter(self.points, self.center, angleDeg)

        #update shadow points
        if self.drawPolygon:
            self.shadowPoints = [
                (p[0] + shadowOffsetX, p[1] + shadowOffsetY)
                for p in self.points
            ]

        #edges
        self.edges = []
        for i in range(len(self.points) - 1 + self.extra):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % len(self.points)]
            self.edges.append((p1, p2))

class Hand():
    def __init__(self, forceFactor, targetRadius, selectedRadius, selectedThickness):
        self.selectedBall = None
        self.forceFactor = forceFactor

        self.targetRadius = targetRadius
        
        self.selectedRadius = selectedRadius
        self.selectedThickness = selectedThickness

        self.pressDownPosition = None

        self.shooting = False   #is the player in the procces of shooting/dragging

    def searchForSelectedBall(self, balls):
        #get all balls within target radius
        closeEnough = []
        distances = []      #store distances in first check to reduce calculations in the second check
        mousePos = pygame.mouse.get_pos()

        for ball in balls:
            #get dist to
            vecTo = (ball.pos[0] - mousePos[0], ball.pos[1] - mousePos[1])
            mag = math.sqrt(vecTo[0] ** 2 + vecTo[1] ** 2)
            if mag <= self.targetRadius:
                closeEnough.append(ball)
                distances.append(mag)

        #if none found set selected as None
        if len(closeEnough) == 0:
            self.selectedBall = None
            return

        #otherwise set closest ball as selected
        closestBall = closeEnough[0]
        closestDistance = distances[0]

        for i in range(1, len(closeEnough)):
            if closestDistance > distances[i]:
                closestDistance = distances[i]
                closestBall = closeEnough[i]
            
        self.selectedBall = closestBall

    def draw_top(self):
        if self.selectedBall != None:
            pygame.draw.circle(screen, (255, 255, 255), self.selectedBall.pos, self.selectedRadius, self.selectedThickness)

    def draw_shadow(self):
        if self.selectedBall != None:
            pygame.draw.circle(screen, (0, 0, 0), (self.selectedBall.pos[0] + shadowOffsetX, self.selectedBall.pos[1] + shadowOffsetY), self.selectedRadius, self.selectedThickness)

#FUNCTION DEFINITION - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def vSum(v1, v2):
    return (v1[0] + v2[0], v1[1] + v2[1])

def vSub(v1, v2):
    return (v1[0] - v2[0], v1[1] - v2[1])

def vMul(v1, f):
    return (v1[0] * f, v1[1] * f)

def vDot(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]

def rotatePointsAroundCenter(points, center, angle_degrees):
    angle = math.radians(angle_degrees)
    cosA = math.cos(angle)
    sinA = math.sin(angle)

    cx, cy = center
    newPoints = []

    for x, y in points:
        #set relative to origin
        tx = x - cx
        ty = y - cy

        #rotate
        rx = tx * cosA - ty * sinA
        ry = tx * sinA + ty * cosA

        #set back from origin and append to final aray
        newPoints.append((rx + cx, ry + cy))

    return newPoints

#VARIABLE INITIALIZATION -----------------------------------------------------------------------------------------------------------------------------------------

physicsSubsteps = 8

shadowOffsetY = 7
shadowOffsetX = 4

hand = Hand(0.05, 40, 15, 2)

balls = []
shapes = []
edges = []

numOfBalls = 10
for i in range(numOfBalls):
    newBall = Ball((screenWidth/2 + random.uniform(0, 0.1), screenHeight/2 + random.uniform(0, 0.1)), random.randint(4, 12), 1)

r = 150
cX = screenWidth/2
cY = screenHeight/2
rotationSpeed1 = 0.5
shape1 = Shape((cX, cY), [(cX + 1 * r, cY + 0 * r),(cX + 0.5 * r, cY + 0.866025 * r),(cX + -0.5 * r, cY + 0.866025 * r),(cX + -1 * r, cY + 0 * r),(cX + -0.5 * r, cY + -0.866025 * r),(cX + 0.5 * r, cY + -0.866025 * r)], 3, False, False)

r = 250
cX = screenWidth/2
cY = screenHeight/2
rotationSpeed2 = -0.5
shape2 = Shape((cX, cY), [(cX + 1 * r, cY + 0 * r),(cX + 0.5 * r, cY + 0.866025 * r),(cX + -0.5 * r, cY + 0.866025 * r),(cX + -1 * r, cY + 0 * r),(cX + -0.5 * r, cY + -0.866025 * r),(cX + 0.5 * r, cY + -0.866025 * r)], 3, False, True)

r = 50
cX = screenWidth/2
cY = screenHeight/2
rotationSpeed3 = -0.5
shape3 = Shape((cX, cY), [(cX + 1 * r, cY + 0 * r),(cX + 0.5 * r, cY + 0.866025 * r),(cX + -0.5 * r, cY + 0.866025 * r),(cX + -1 * r, cY + 0 * r),(cX + -0.5 * r, cY + -0.866025 * r),(cX + 0.5 * r, cY + -0.866025 * r)], 3, False, False)


#get initial ticks
prevT = pygame.time.get_ticks()

#toggle framerate to check if deltaTime works in physics
dtsCheck = True

#WHILE LOOP - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

running = True
while running:

    #update delta time
    currT = pygame.time.get_ticks()
    dTms = currT - prevT
    #dTs = dTms / 1000.0
    dTs = 15 / 1000
    sub_dTs = dTs / physicsSubsteps

    #fill screen
    screen.fill((20, 20, 20))

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  #LMB
                #start shoot attempt of the selected ball
                if hand.selectedBall != None:
                    hand.shooting = True
                    hand.pressDownPosition = pygame.mouse.get_pos()

            if event.button == 3:   #RMB
                dtsCheck = not dtsCheck

            if event.button == 2: #MMB
                print(pygame.mouse.get_pos())

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  #LMB
                if hand.shooting:
                    #get vector to start shooting pos and shoot
                    hand.shooting = False
                    pressUpPosition = pygame.mouse.get_pos()
                    vecTo = (hand.pressDownPosition[0] - pressUpPosition[0], hand.pressDownPosition[1] - pressUpPosition[1])
                    forceNormalizedVec = (vecTo[0] * hand.forceFactor, vecTo[1] * hand.forceFactor)
                    hand.selectedBall.applyForce(forceNormalizedVec)

    #hand search - only when not pressing down (pressing down and dragging for shooting will have the player move the cursor out of selected range so we want to keep the oldest selected ball and not search for a new one)
    mouse_buttons = pygame.mouse.get_pressed()
    """if not mouse_buttons[0]:  #LMB
        hand.searchForSelectedBall(balls)"""

    shape1.rotate(rotationSpeed1 * dTs * 60)
    shape2.rotate(rotationSpeed2 * dTs * 60)
    shape3.rotate(rotationSpeed3 * dTs * 60)
    
    #reload edges
    edges = []
    for shape in shapes:
        for edge in shape.edges:
            edges.append(edge)

    #physics
    for i in range(physicsSubsteps):
        for ball in balls:              #the move and draw is not in the same for loop as the order matters
            #add some gravity
            ball.vel = (ball.vel[0], ball.vel[1] + 0.007)

            ball.move(sub_dTs)

        for ball in balls:
            #ball.doBallCollision(balls)
            ball.doEdgeCollision(edges)

    #draw shadows
    for ball in balls:
        ball.draw_shadow()

    for shape in shapes:
        shape.draw_shadow()

    hand.draw_shadow()

    #draw shooting drag line and ball direction line
    if hand.shooting:
        pygame.draw.line(screen, (0, 0, 0), (hand.pressDownPosition[0] + shadowOffsetX, hand.pressDownPosition[1] + shadowOffsetY), (pygame.mouse.get_pos()[0] + shadowOffsetX, pygame.mouse.get_pos()[1] + shadowOffsetY), 2)
        
        #get direction vector
        vecTo = (hand.pressDownPosition[0] - pygame.mouse.get_pos()[0], hand.pressDownPosition[1] - pygame.mouse.get_pos()[1])
        forceNormalizedVec = (vecTo[0] * 0.5, vecTo[1] * 0.5)   #shorten the line
        pygame.draw.line(screen, (0, 0, 0), (hand.selectedBall.pos[0] + forceNormalizedVec[0] + shadowOffsetX, hand.selectedBall.pos[1] + forceNormalizedVec[1] + shadowOffsetY), (hand.selectedBall.pos[0] + shadowOffsetX, hand.selectedBall.pos[1] + shadowOffsetY), 2)

    #draw tops
    for ball in balls:
        ball.draw_top()

    for shape in shapes:
        shape.draw_top()

    hand.draw_top()

    #draw shooting drag line and ball direction line
    if hand.shooting:
        pygame.draw.line(screen, (255, 255, 255), hand.pressDownPosition, pygame.mouse.get_pos(), 2)

        #get direction vector
        vecTo = (hand.pressDownPosition[0] - pygame.mouse.get_pos()[0], hand.pressDownPosition[1] - pygame.mouse.get_pos()[1])
        forceNormalizedVec = (vecTo[0] * 0.5, vecTo[1] * 0.5)   #shorten the line
        pygame.draw.line(screen, (255, 255, 255), (hand.selectedBall.pos[0] + forceNormalizedVec[0], hand.selectedBall.pos[1] + forceNormalizedVec[1]), (hand.selectedBall.pos[0], hand.selectedBall.pos[1]), 2)

    # Update the display (buffer flip)
    #displayFPS(screen, 25)
    t += 1
    #pyrecorder.takeShot(screen, t)
    pygame.display.flip()

    """
    if t == 600:
        running = False
    """

    clock.tick(120)
    """
    if dtsCheck:
        clock.tick(60)
    else:
        clock.tick(30)
    """

    #update delta time
    prevT = currT

#pyrecorder.compileToVideo(30)

# Quit Pygame
pygame.quit()