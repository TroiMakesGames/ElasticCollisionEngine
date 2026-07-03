import pygame

import math
import random

#initialize pygame window
pygame.init()
screenWidth = 800
screenHeight = 600
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('Elastic Collision Engine')

#fps display
clock = pygame.time.Clock()
def displayFPS(screen, font_size):
    font = pygame.font.SysFont(None, font_size)
    fps = round(clock.get_fps(), 1)
    fps_text = font.render(f"{fps}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))

#CLASS DEFINITION -----------------------------------------------------------------------------------------------------------------------------------------

class Ball():
    def __init__(self, pos, radius, drag, gravity, bounceDamping):
        balls.append(self)

        self.pos = pos
        self.radius = radius

        self.vel = (0, 0)
        self.drag = drag                            #drag through air (usefull for top down view with no gravity)
        self.gravity = gravity                      #gravity (side view)
        self.bounceDamping = bounceDamping          #energy loss on bounce with shape edge or screen edge

    def draw(self):
        pygame.draw.circle(screen, (255, 255, 255), self.pos, self.radius, 1)

    def applyForce(self, force):
        self.vel = (self.vel[0] + force[0], self.vel[1] + force[1])

    def move(self, dTs):
        #apply gravity  (adding to both components for acces to non downward gravity)
        self.vel = (self.vel[0] + self.gravity[0] * dTs, self.vel[1] + self.gravity[1] * dTs)

        #apply drag
        self.vel = (self.vel[0] * self.drag, self.vel[1] * self.drag)

        #apply movement
        self.pos = (self.pos[0] + self.vel[0] * dTs * 60, self.pos[1] + self.vel[1] * dTs * 60)

        #bounce of screen edges
        doDamping = False
        if self.pos[0] + self.radius > screenWidth:
            self.vel = (self.vel[0] * -1, self.vel[1])
            self.pos = (screenWidth - self.radius, self.pos[1])
            doDamping = True

        if self.pos[0] - self.radius < 0:
            self.vel = (self.vel[0] * -1, self.vel[1])
            self.pos = (self.radius, self.pos[1])
            doDamping = True

        if self.pos[1] + self.radius > screenHeight:
            self.vel = (self.vel[0], self.vel[1] * -1)
            self.pos = (self.pos[0], screenHeight - self.radius)
            doDamping = True

        if self.pos[1] - self.radius < 0:
            self.vel = (self.vel[0], self.vel[1] * -1)
            self.pos = (self.pos[0], self.radius)
            doDamping = True
        
        #bounce damping
        if doDamping:
            self.vel = (self.vel[0] * self.bounceDamping, self.vel[1] * self.bounceDamping)

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
                    overlap = (self.radius * 2) - mag
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

                    #apply bounce damping
                    self.vel = (self.vel[0] * self.bounceDamping, self.vel[1] * self.bounceDamping)
                    otherBall.vel = (otherBall.vel[0] * otherBall.bounceDamping, otherBall.vel[1] * otherBall.bounceDamping)

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

                #bounce damping
                self.vel = (self.vel[0] * self.bounceDamping, self.vel[1] * self.bounceDamping)

class Shape():
    def __init__(self, center, points, width, drawPolygon, finishLoop):
        shapes.append(self)

        self.center = center
        self.points = points
        self.width = width

        #do an extra iteration of edge calculations if finishLoop == True (first and last point are connected with an edge)
        self.extra = 0
        if finishLoop:
            self.extra = 1

        #fill or no fill
        self.drawPolygon = drawPolygon 

        #generate edges
        self.edges = []
        self.recalculateEdges()
        
        #append to all edges    NOTE: edges != self.edges
        for edge in self.edges:
            edges.append(edge)

    def draw(self):
        if not self.drawPolygon:
            for edge in self.edges:
                pygame.draw.aaline(screen, (255, 255, 255), edge[0], edge[1])
        else:
            pygame.draw.polygon(screen, (255, 255, 255), self.points)

    def recalculateEdges(self):
        self.edges = []
        for i in range(len(self.points) - 1 + self.extra):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % len(self.points)]
            self.edges.append((p1, p2))

    def rotate(self, angleDeg):
        self.points = rotatePointsAroundCenter(self.points, self.center, angleDeg)
        self.recalculateEdges()

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
targetFrameRate = 60
gravity = (0, 10)               #gravity (side view)
drag = 1                        #drag through air (usefull for top down view with no gravity)
bounceDamping = 0.99             #energy loss on bounce with shape edge or screen edge

balls = []
shapes = []
edges = []

numOfBalls = 25
for i in range(numOfBalls):
    newBall = Ball((screenWidth/2 + random.uniform(0, 0.1), screenHeight/2 + random.uniform(0, 0.1)), random.randint(4, 12), drag, gravity, bounceDamping)

r = 150
cX = screenWidth/2
cY = screenHeight/2
rotationSpeed = 60
shape = Shape((cX, cY), [(cX + 1 * r, cY + 0 * r),(cX + 0.5 * r, cY + 0.866025 * r),(cX + -0.5 * r, cY + 0.866025 * r),(cX + -1 * r, cY + 0 * r),(cX + -0.5 * r, cY + -0.866025 * r),(cX + 0.5 * r, cY + -0.866025 * r)], 3, False, True)

#get initial ticks
prevT = pygame.time.get_ticks()

#WHILE LOOP - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

running = True
while running:

    #update delta time
    currT = pygame.time.get_ticks()
    dTms = currT - prevT
    dTs = dTms / 1000.0

    #if dts is fucked for more than 3 frames reset it to one frame (prevents lag spike weird physics reactions but delays for a couple of frames)
    if dTs > (targetFrameRate / 1000) * 3:
        dTs = targetFrameRate / 1000

    sub_dTs = dTs / physicsSubsteps

    #fill screen
    screen.fill((20, 20, 20))

    #handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 2: #MMB
                print(pygame.mouse.get_pos())

    """
    mouseButtons = pygame.mouse.get_pressed()
    if mouseButtons[0]:
        ...
    """
    
    for i in range(physicsSubsteps):
        shape.rotate(rotationSpeed * sub_dTs)
    
    #reload edges
    edges = []
    for shape in shapes:
        for edge in shape.edges:
            edges.append(edge)

    #physics
    for i in range(physicsSubsteps):
        for ball in balls:              #the move() and draw() are not in the same loop as the order matters (do X iterations of physics substeps, then draw)
            ball.move(sub_dTs)

        for ball in balls:
            ball.doBallCollision(balls)
            ball.doEdgeCollision(edges)

    #draw
    for ball in balls:
        ball.draw()

    for shape in shapes:
        shape.draw()

    # Update the display (buffer flip)
    displayFPS(screen, 25)
    pygame.display.flip()

    clock.tick(targetFrameRate)

    #update delta time
    prevT = currT

#pyrecorder.compileToVideo(30)

# Quit Pygame
pygame.quit()