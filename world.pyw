#contants
G = 1.184*10**-4           # AU^3/Earth mass/year^2

class world(object):
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
                                               fill="#0064ff")
        self.fixed = False

    def step(self, dt):
        '''
        Advance the world's position by one time step

        Args:
            dt (float): The duration of the time step in years
        '''
        if not self.fixed:
            self.x += self.vx*dt
            self.y += self.vy*dt

    def setColor(self, color):
        '''
        Changes the color of the drawn image of this world

        Args:
            color (string): color name accepted by tkinter
        '''
        self.master.canvas.itemconfig(self.image, fill=color)

    def grav(self, other, dt):
        '''
        Apply a gravitational force from another world onto this world for a specified period of time

        Args:
            other (world): The world exerting a gravitational force upon this world
            dt (float): The duration of the force in years
        '''
        if not self.fixed and not other.fixed:
            dist = ( (self.x - other.x)**2 + (self.y - other.y)**2 )**0.5
            accl = -G * other.m / dist**2
            acclX = (self.x - other.x) * accl / dist
            acclY = (self.y - other.y) * accl / dist
            self.vx += acclX * dt
            self.vy += acclY * dt

    def collide(self, other):
        '''
        Check if two worlds collide. Returns true if they have collided, otherwise returns false.

        Args:
            other (world): the other world to check if we collided with.

        Returns:
            Boolean, whether we collided.
        '''
        dist = ( (self.x - other.x)**2 + (self.y - other.y)**2 )**0.5
        if dist < self.size + other.size and not self.fixed and not other.fixed:
            return True
        else:
            return False

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

    def delete(self):
        '''
        Stops drawing of this world
        '''
        self.master.canvas.delete(self.image)