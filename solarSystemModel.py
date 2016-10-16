from tkinter import *
import thread

#global contants
G = 1.184*10**-4        #AU^3/Earth mass/year^2
drawTime = 1000/60      #How often (in ms) to refresh the screen
initRunTime = 10        #How often to advance by one timestep in the simulation initially
initWidth = 800         #default view width
initHeight = 600        #default view height
moveAmount = 10.0       #how many pixels to move when hitting move buttons
zoomAmount = 1.1        #how much to zoom in/out by
speedChangeAmount = 1.5 #how much to speed up/slow down simulation per button press
buttonSize = 3          #How big to make the buttons


class world:
    '''
    A gravitating body obeying Newtonian mechanics. 
    '''
    def __init__(self, master, m, x, y, vx, vy, size):
        '''
        Constucts a world object. 

        Args:
            master (system): The system of worlds this world belongs to.
            m (float): The mass of the world in earth masses
            x (float): The x position of the world in AU
            y (float): The y position of the world in AU
            vx (float): The x component of the world's velocity
            vy (float): The y component of the world's velocity
            size (float): The radius of the world in AU
        '''
        self.master = master
        self.m = m
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.image = master.canvas.create_oval(x - size, y - size, 
                                               x + size, y + size,
                                               fill="blue")

    def step(self, dt):
        '''
        Advance the world's position by one time step

        Args:
            dt (float): The duration of the time step in years
        '''
        self.x += self.vx*dt
        self.y += self.vy*dt

    def grav(self, other, dt):
        '''
        Apply a gravitational force from another world onto this world for a specified period of time

        Args:
            other (world): The world exerting a gravitational force upon this world
            dt (float): The duration of the force in years
        '''
        dist = ( (self.x - other.x)**2 + (self.y - other.y)**2 )**0.5
        accl = -G * other.m / dist**2
        acclX = (self.x - other.x) * accl / dist
        acclY = (self.y - other.y) * accl / dist
        self.vx += acclX * dt
        self.vy += acclY * dt

    def updateDraw(self, cameraPos, scale):
        '''
        Update the location and size of the drawn image

        Args:
            cameraPos (tuple): A physical (x, y) location of the center of the drawing canvas
            scale (float): The number of pixels per AU of physical distance
        '''
        drawCoords = self.master.realToDraw(self.x, self.y)
        drawX = drawCoords[0]
        drawY = drawCoords[1]
        drawRadius = self.master.scale * self.size
        self.master.canvas.coords(self.image,
                                  (drawX - drawRadius, drawY - drawRadius,
                                   drawX + drawRadius, drawY + drawRadius))

    def onWorldClick(self, event):
        '''
        Handling of user clicking on world. Currently enables camera tracking of clicked world.

        Args:
            event: The mouse click event, not used
        '''
        self.master.tracked = self
        self.master.cameraPos = (self.x, self.y)


class system:
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
        self.scale = 1
        self.runTime = initRunTime
        self.tracked = None
        self.canvas = Canvas(root, width=initWidth, 
                             height=initHeight, bg="black")
        self.canvas.pack()
        self.play = True
        self.dt = dt
        self.dt_init = dt

    def initialize(self):
        '''
        Set up events handling click-and-drag movement and clicking on world objects
        '''
        self.canvas.bind('<Button-1>', self.mouseDown)
        self.canvas.bind('<B1-Motion>', self.mouseMove)
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
        Applies graviational forces pairwise to all world objects and advances their
        location by one time step.
        '''
        for firstWorldNum in range(len(self.worlds)):
            firstWorld = self.worlds[firstWorldNum]
            for secondWorldNum in range(firstWorldNum + 1, len(self.worlds)):
                secondWorld = self.worlds[secondWorldNum]
                firstWorld.grav(secondWorld, self.dt)
                secondWorld.grav(firstWorld, self.dt)
        for w in self.worlds:
            w.step(self.dt)
        

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

    def zoomIn(self, amount):
        '''
        Moves the camera in by a specified amount.

        Args:
            amount (float): The fractional increase in scale 
                (e.g. a value of 2 doubles displace distance's sizes).
        '''
        self.scale = self.scale * zoomAmount

    def zoomOut(self, amount):
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
        self.runTime = self.runTime / speedChangeAmount
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
        self.runTime = self.runTime * speedChangeAmount
        # If the smaller step size is no longer needed, restore old step size
        if self.runTime < drawTime and self.dt != self.dt_init:
            self.runTime = self.runTime * self.dt_init / self.dt
            self.dt = self.dt_init
        # If the simulation speed is slower than the refresh rate, decrease the step size
        # so the user can maintain a smooth experience 
        if self.runTime > drawTime:
            self.dt = self.dt * drawTime / self.runTime
            self.runTime = drawTime

    def pause(self, pauseButton):
        '''
        Handles a pause button press, including handling  pause button relief.

        Args:
            pauseButton (Button widget): The button to handle relief for.
        '''
        self.play = not self.play
        if self.play:
            pauseButton.config(relief = RAISED)
            self.updateWorlds()
        else:
            pauseButton.config(relief = SUNKEN)
    
    def mouseDown(self, event):
        '''
        Handles mouse presses for click-and-drag movement
        '''
        self.mouseDown = (event.x, event.y)
        self.oldCamPos = self.cameraPos

    def mouseMove(self, event):
        '''
        Handles mouse movements for click-and-drag movement
        '''
        mouseChange = (event.x - self.mouseDown[0], event.y - self.mouseDown[1])
        self.cameraPos = (self.oldCamPos[0] - 1.0*mouseChange[0]/self.scale, 
                          self.oldCamPos[1] - 1.0*mouseChange[1]/self.scale)
        self.tracked = None


class systemApp:
    '''
    A app for viewing and interacting with a system object (i.e. a solar system)
    '''
    def __init__(self, root):
        '''
        Begins the simulation and shows the UI to the user.

        Args:
            root (widget): The widget in which to generate the view and UI.
        '''
        sys = system(root, 0.05)
        sys.worlds = [world(sys, 333000, 0, 0, 0, 0.262, 0.5), 
                      world(sys, 318, 1.3, 0, 0, 5.5, 0.075),
                      world(sys, 31800, 5.2, 0, 0, -2.75, 0.15), 
                      world(sys, 0.025, 5.2+0.7155, 0, 0, -2.75+2.294, 0.05),
                      world(sys, 0.025, 7, 0, 0, -0.9, 0.05)]
        sys.cameraPos = (-0.0, -0.0)
        sys.scale = 50
        sys.initialize()

        frame = Frame(root)
        frame.pack()

        moveFrame = Frame(frame)
        moveFrame.grid(row = 0, column = 0)

        bufferFrame = Frame(frame, width=initWidth - buttonSize*5)
        bufferFrame.grid(row = 0, column = 1)

        zoomFrame = Frame(frame)
        zoomFrame.grid(row = 0, column = 2)

        leftButton = Button(moveFrame, height=buttonSize, 
                            width=2*buttonSize, text="<", 
                            command=lambda: sys.moveLeft(moveAmount))
        leftButton.grid(row = 1, column=0)

        rightButton = Button(moveFrame, height=buttonSize, 
                             width=2*buttonSize, text=">", 
                             command=lambda: sys.moveRight(moveAmount))
        rightButton.grid(row = 1, column=2)

        upButton = Button(moveFrame, height=buttonSize, 
                          width=2*buttonSize, text="^", 
                          command=lambda: sys.moveUp(moveAmount))
        upButton.grid(row = 0, column=1)

        downButton = Button(moveFrame, height=buttonSize, 
                            width=2*buttonSize, text="v", 
                            command=lambda: sys.moveDown(moveAmount))
        downButton.grid(row = 2, column=1)

        inButton = Button(zoomFrame, height=buttonSize, 
                          width=2*buttonSize, text="+", 
                          command=lambda: sys.zoomIn(moveAmount))
        inButton.grid(row = 0, column=4)

        outButton = Button(zoomFrame, height=buttonSize, 
                           width=2*buttonSize, text="-", 
                           command=lambda: sys.zoomOut(moveAmount))
        outButton.grid(row = 2, column=4)

        fasterButton = Button(zoomFrame, height=buttonSize, 
                              width=2*buttonSize, text=">>", 
                              command=lambda: sys.speedUp(speedChangeAmount))
        fasterButton.grid(row = 0, column = 0)

        pauseButton = Button(zoomFrame, height=buttonSize, 
                             width=2*buttonSize, text="||", 
                             command=lambda: sys.pause(pauseButton))
        pauseButton.grid(row=1, column=0)

        slowerButton = Button(zoomFrame, height=buttonSize, 
                              width=2*buttonSize, text="<<", 
                              command=lambda: sys.slowDown(speedChangeAmount))
        slowerButton.grid(row = 2, column = 0)

        sys.updateWorlds()
        sys.updateDraw()


root = Tk()
solarSystemApp = systemApp(root)


mainloop()