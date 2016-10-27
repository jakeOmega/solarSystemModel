from tkinter import *
from world import *

#constants
initRunTime = 32           # How often to advance by one timestep in the simulation initially
initWidth = 800            # default view width
initHeight = 600           # default view height
drawTime = 1000/10         # How often (in ms) to refresh the screen
zoomAmount = 1.1           # how much to zoom in/out by
buttonSize = 3             # How big to make the buttons
distanceToVelocity = 3E-4  # Conversion factor between arrow length and world velocity
newWorldMass = 10          # mass (in earth masses) of user-added worlds
newWorldSize = 0.05        # size (in AU) of user-added worlds
newWorldMChange = 1.6
newWorldRChange = 1.1
collisionGridSize = 0.01
minMassForGlobal = 50.0


class system(object):
    '''
    A system of world objects, and methods for drawing and updating them and handling events
    '''
    def __init__(self, master, dt, worlds=[]):
        '''
        Constucts a new system object.

        Args:
            master (systemApp): The containing systemApp
            dt (float): The time step (in years) to use in simulation
            worlds (optional, a list of world objects): A set of worlds to begin with
        '''
        self.master = master
        self.worlds = worlds
        self.cameraPos = (0, 0)
        self.scale = 1.0
        self.runTime = initRunTime
        self.tracked = None
        self.canvas = Canvas(master, width=initWidth, 
                             height=initHeight, bg="black")
        self.canvas.pack()
        self.play = True
        self.dt = dt
        self.dt_init = dt
        self.velocityLine = None
        self.newWorld = None
        self.collisionGrid = {}

    def initialize(self):
        '''
        Set up events handling hard-coded mouse functions,
        including click-and-drag movement, selecting object,
        zooming with the mouse wheel, and adding new  worlds
        with right click
        '''
        self.canvas.bind('<Button-1>', self.mouseLeftDown)
        self.canvas.bind('<B1-Motion>', self.mouseLeftMove)
        self.canvas.bind('<Button-3>', self.mouseRightDown)
        self.canvas.bind('<B3-Motion>', self.mouseRightMove)
        self.canvas.bind('<ButtonRelease-3>', self.mouseRightUp)
        self.canvas.bind_all('<MouseWheel>', self.mouseWheel)
        self.slowDown(1.0)
        for w in self.worlds:
            self.canvas.tag_bind(w.image, '<Button-1>',  w.onWorldClick)

    def realToDraw(self, x, y):
        '''
        Converts physical coordiantes (in AU) to draw canvas coordinates (pixels).

        Args:
            x (float): The x position to convert, in AU.
            y (float): The y position to convert, in AU.

        Returns:
            A tuple containing the x and y coordinates in the drawing canvas 
            corresponding to the input location.
        '''
        drawX = self.scale * (x - self.cameraPos[0]) + self.canvas.winfo_width()/2
        drawY = self.scale * (y - self.cameraPos[1]) + self.canvas.winfo_height()/2
        return (drawX, drawY)

    def drawToReal(self, drawX, drawY):
        '''
        Converts draw canvas coordinates (pixels) to physical coordiantes (in AU).

        Args:
            drawX (float): The x position to convert.
            drawY (float): The y position to convert.

        Returns:
            A tuple containing the x and y coordinates in physical coordinate (in AU) 
            corresponding to the input location.
        '''
        x = (drawX - self.canvas.winfo_width()/2)/self.scale + self.cameraPos[0]
        y = (drawY - self.canvas.winfo_height()/2)/self.scale + self.cameraPos[1]
        return (x, y)

    def pushWorlds(self):
        '''
        Applies graviational forces pairwise to all world objects, performs stupid collision
        detection, advances their location by one time step.
        '''
        newWorldList = []
        deleteWorldList = []
        alreadyGravList = []
        #applies gravity for massive worlds to all other worlds
        for firstWorldNum in range(len(self.worlds)):
            firstWorld = self.worlds[firstWorldNum]
            if firstWorld.m > minMassForGlobal:
                for secondWorldNum in range(firstWorldNum + 1, len(self.worlds)):
                    secondWorld = self.worlds[secondWorldNum]
                    firstWorld.grav(secondWorld, self.dt)
                    secondWorld.grav(firstWorld, self.dt)
                alreadyGravList += [firstWorld]
        #look for collisions for grid cells with multiple worlds
        for key in self.collisionGrid:
            if len(self.collisionGrid[key]) > 1:
                worlds = self.collisionGrid[key]
                for firstWorldNum in range(len(worlds)):
                    firstWorld = worlds[firstWorldNum]
                    if firstWorld not in deleteWorldList:
                        for secondWorldNum in range(firstWorldNum + 1, len(worlds)):
                            secondWorld = worlds[secondWorldNum]
                            if secondWorld not in deleteWorldList:
                                #If they collide, merge them
                                if firstWorld.collide(secondWorld):
                                    newM = firstWorld.m + secondWorld.m
                                    newX = (firstWorld.x * firstWorld.m + secondWorld.x * secondWorld.m)/newM
                                    newY = (firstWorld.y * firstWorld.m + secondWorld.y * secondWorld.m)/newM
                                    newVX = (firstWorld.vx * firstWorld.m + secondWorld.vx * secondWorld.m)/newM
                                    newVY = (firstWorld.vy * firstWorld.m + secondWorld.vy * secondWorld.m)/newM
                                    newWorld = world(self, newM, newX, newY, newVX, newVY, (firstWorld.size**3 + secondWorld.size**3)**0.33)
                                    deleteWorldList += [firstWorld, secondWorld]
                                    newWorldList = [newWorld]
                                    if self.tracked == firstWorld or self.tracked == secondWorld:
                                        self.tracked = newWorld
                                #apply gravity to nearby worlds, if we haven't already handled them
                                elif firstWorld not in alreadyGravList and secondWorld not in alreadyGravList:
                                    firstWorld.grav(secondWorld, self.dt)
                                    secondWorld.grav(firstWorld, self.dt)
        #delete worlds that merged
        for w in deleteWorldList:
            try:
                self.worlds.remove(w)
                w.delete()
            except:
                print w.x, w.y
        #add in merged worlds
        for w in newWorldList:
            self.worlds += [w]
            self.canvas.tag_bind(w.image, '<Button-1>',  w.onWorldClick)
        #add world to collision grid locations that they can potentially
        #be overlapping with 
        self.collisionGrid = {}
        for w in self.worlds:
            w.step(self.dt)
            gridCoordX = int(w.x/collisionGridSize)
            gridCoordY = int(w.y/collisionGridSize)
            worldGridSize = int(collisionGridSize/w.size) + 1
            keys = [(gridCoordX+i, gridCoordY+j) for i in range(-worldGridSize, worldGridSize + 1) 
                    for j in range(-worldGridSize, worldGridSize + 1)]
            for key in keys:
                if key in self.collisionGrid:
                    self.collisionGrid[key] += [w]
                else:
                    self.collisionGrid[key] = [w]
        

    def updateWorlds(self):
        '''
        Handles setting events for simulating bodies based on simulation speed.
        '''
        self.pushWorlds()
        if self.play:
            if self.runTime <= 1:
                for i in range(int(1/self.runTime)):
                    self.pushWorlds()
                self.master.after(1, lambda: self.updateWorlds())
            else:
                self.master.after(int(self.runTime), lambda: self.updateWorlds())

    def updateDraw(self):
        '''
        Updates canvas with new positions, camera location, or scale and sets events for
        future updates.
        '''
        if self.tracked is not None:
            self.cameraPos = (self.tracked.x, self.tracked.y)
        for w in self.worlds:
            w.updateDraw(self.cameraPos, self.scale)
        self.master.after(drawTime, self.updateDraw)

    def moveLeft(self, amount):
        '''
        Moves the camera left by a specified amount.

        Args:
            amount (float): The distance in pixels to move the camera.
        '''
        self.cameraPos = (self.cameraPos[0] - amount/self.scale, self.cameraPos[1])
        self.tracked = None

    def moveRight(self, amount):
        '''
        Moves the camera right by a specified amount.

        Args:
            amount (float): The distance in pixels to move the camera.
        '''
        self.cameraPos = (self.cameraPos[0] + amount/self.scale, self.cameraPos[1])
        self.tracked = None

    def moveUp(self, amount):
        '''
        Moves the camera up by a specified amount.

        Args:
            amount (float): The distance in pixels to move the camera.
        '''
        self.cameraPos = (self.cameraPos[0], self.cameraPos[1] - amount/self.scale)
        self.tracked = None

    def moveDown(self, amount):
        '''
        Moves the camera down by a specified amount.

        Args:
            amount (float): The distance in pixels to move the camera.
        '''
        self.cameraPos = (self.cameraPos[0], self.cameraPos[1] + amount/self.scale)
        self.tracked = None

    def zoomIn(self):
        '''
        Moves the camera in by a specified amount.

        Args:
            amount (float): The fractional increase in scale 
                (e.g. a value of 2 doubles displace distance's sizes).
        '''
        self.scale = self.scale * zoomAmount

    def zoomOut(self):
        '''
        Moves the camera out by a specified amount.

        Args:
            amount (float): The fractional decrease in scale
                (e.g. a value of 2 halves displace distance's sizes).
        '''
        self.scale = self.scale / zoomAmount

    def speedUp(self, amount):
        '''
        Speeds up the simulation by a specified amount.

        Args:
            amount (float): The fractional increase in simulation speed.
        '''
        self.runTime = self.runTime / amount
        # If the smaller step size is no longer needed, restore old step size
        if self.runTime < drawTime and self.dt != self.dt_init:
            self.runTime = self.runTime * self.dt_init / self.dt
            self.dt = self.dt_init
        # If the simulation speed is slower than the refresh rate, decrease the step size
        # so the user can maintain a smooth experience 
        if self.runTime > drawTime:
            self.dt = self.dt * drawTime / self.runTime
            self.runTime = drawTime
        

    def slowDown(self, amount):
        '''
        Slows down the simulation by a specified amount.

        Args:
            amount (float): The fractional decrease in simulation speed.
        '''
        self.runTime = self.runTime * amount
        # If the smaller step size is no longer needed, restore old step size
        if self.runTime < drawTime and self.dt != self.dt_init:
            self.runTime = self.runTime * self.dt_init / self.dt
            self.dt = self.dt_init
        # If the simulation speed is slower than the refresh rate, decrease the step size
        # so the user can maintain a smooth experience 
        if self.runTime > drawTime:
            self.dt = self.dt * drawTime / self.runTime
            self.runTime = drawTime

    def pause(self, pauseButton = None):
        '''
        Handles a pause button press, including handling  pause button relief.

        Args:
            pauseButton (Button widget): The button to handle relief for.
        '''
        self.play = not self.play
        if pauseButton is not None:
            if self.play:
                pauseButton.config(relief = RAISED)
            else:
                pauseButton.config(relief = SUNKEN)
        if self.play:
            self.updateWorlds()
    
    def mouseLeftDown(self, event):
        '''
        Handles mouse presses for click-and-drag movement
        '''
        self.mouseLeftDown = (event.x, event.y)
        self.oldCamPos = self.cameraPos

    def mouseLeftMove(self, event):
        '''
        Handles mouse movements for click-and-drag movement
        '''
        mouseChange = (event.x - self.mouseLeftDown[0], event.y - self.mouseLeftDown[1])
        self.cameraPos = (self.oldCamPos[0] - 1.0*mouseChange[0]/self.scale, 
                          self.oldCamPos[1] - 1.0*mouseChange[1]/self.scale)
        self.tracked = None

    def mouseRightDown(self, event):
        '''
        Handles the addition of a new world by user right-click
        '''
        self.tracked = None
        if self.velocityLine is None:
            self.mouseRightDown = (event.x, event.y)
            self.velocityLine = self.canvas.create_line(event.x, event.y, event.x, event.y, arrow=LAST, fill='red')
            newWorldPos = self.drawToReal(event.x, event.y)
            self.newWorld = world(self, newWorldMass, newWorldPos[0], newWorldPos[1], 0, 0, newWorldSize)
            self.newWorld.fixed = True
            self.newWorld.setColor('#ff3232')
            self.canvas.tag_bind(self.newWorld.image, '<Button-1>',  self.newWorld.onWorldClick)
            self.worlds += [self.newWorld]

    def mouseRightMove(self, event):
        '''
        Draws an arrow indicating new world velocity when user moves mouse after right clicking
        '''
        if self.velocityLine is not None:
            self.canvas.coords(self.velocityLine, self.mouseRightDown[0], self.mouseRightDown[1],
                               event.x, event.y)

    def mouseRightUp(self, event):
        '''
        Allows newly added world to move and removes arrow.
        '''
        self.canvas.delete(self.velocityLine)
        self.velocityLine = None
        self.newWorld.vx = distanceToVelocity * self.scale * (event.x - self.mouseRightDown[0])
        self.newWorld.vy = distanceToVelocity * self.scale * (event.y - self.mouseRightDown[1])
        self.newWorld.fixed = False
        self.newWorld.setColor('#0064ff')
        self.newWorld = None

    def mouseWheel(self, event):
        '''
        Zooms in or out if we're not making a new world.
        Increases or decrease new world mass/size if we are
        making a new world.
        '''
        if self.velocityLine is None:
            if event.delta > 0:
                self.zoomIn()
            else:
                self.zoomOut()
        else:
            if event.delta > 0:
                self.newWorld.m = self.newWorld.m * newWorldMChange
                self.newWorld.size = self.newWorld.size * newWorldRChange
            else:
                self.newWorld.m = self.newWorld.m / newWorldMChange
                self.newWorld.size = self.newWorld.size / newWorldRChange