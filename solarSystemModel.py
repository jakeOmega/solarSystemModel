from tkinter import *

#global contants
G = 1.184*10**-4 #AU^3/Earth mass/year^2
drawTime = 1000/60
runTime = 1000/60
initWidth = 1200
initHeight = 800
moveAmount = 10.0
zoomAmout = 1.1


class world:
    def __init__(self, master, m, x, y, vx, vy, size):
        self.master = master
        self.m = m
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.circle = master.create_oval(x - size/2, y - size/2, x + size/2, y + size/2, fill="black")

    def step(self, dt):
        self.x += self.vx*dt
        self.y += self.vy*dt

    def grav(self, other, dt):
        dist = ( (self.x - other.x)**2 + (self.y - other.y)**2 )**0.5
        accl = -G * other.m / dist**2
        acclX = (self.x - other.x) * accl / dist
        acclY = (self.y - other.y) * accl / dist
        self.vx += acclX * dt
        self.vy += acclY * dt

    def updateDraw(self, cameraPos, scale):
        drawX = scale * (self.x - cameraPos[0]) + self.master.winfo_width()/2
        drawY = scale * (self.y - cameraPos[1]) + self.master.winfo_height()/2
        self.master.coords(self.circle, (drawX - self.size/2, drawY - self.size/2, drawX + self.size/2, drawY + self.size/2))

class system:
    def __init__(self, master, worlds=[]):
        self.master = master
        self.worlds = worlds
        self.cameraPos = (0, 0)
        self.scale = 1

    def updateWorlds(self, dt):
        for firstWorldNum in range(len(self.worlds)):
            firstWorld = self.worlds[firstWorldNum]
            for secondWorldNum in range(firstWorldNum + 1, len(self.worlds)):
                secondWorld = self.worlds[secondWorldNum]
                firstWorld.grav(secondWorld, dt)
                secondWorld.grav(firstWorld, dt)
        for w in self.worlds:
            w.step(dt)
        self.master.after(runTime, lambda: self.updateWorlds(dt))

    def updateDraw(self):
        for w in self.worlds:
            w.updateDraw(self.cameraPos, self.scale)
        self.master.after(drawTime, self.updateDraw)

    def moveLeft(self, amount):
        self.cameraPos = (self.cameraPos[0] - amount/self.scale, self.cameraPos[1])

    def moveRight(self, amount):
        self.cameraPos = (self.cameraPos[0] + amount/self.scale, self.cameraPos[1])

    def moveUp(self, amount):
        self.cameraPos = (self.cameraPos[0], self.cameraPos[1] - amount/self.scale)

    def moveDown(self, amount):
        self.cameraPos = (self.cameraPos[0], self.cameraPos[1] + amount/self.scale)

    def zoomIn(self, amount):
        self.scale = self.scale * zoomAmout

    def zoomOut(self, amount):
        self.scale = self.scale / zoomAmout


root = Tk()
canvas = Canvas(root, width=initWidth, height=initHeight)
canvas.pack()

sys = system(root, [world(canvas, 333000, 0, 0, 0, 0, 30), world(canvas, 1, 1, 0, 0, -2*3.14159, 4), world(canvas, 0.01, 1.002, 0, 0, -2*3.14159 - 0.2, 2)])
sys.cameraPos = (-0.0, -0.0)
sys.scale = 200

frame = Frame(root)

leftButton = Button(frame, text="<", command=lambda: sys.moveLeft(moveAmount))
leftButton.grid(row = 1, column=0)

rightButton = Button(frame, text=">", command=lambda: sys.moveRight(moveAmount))
rightButton.grid(row = 1, column=2)

upButton = Button(frame, text="^", command=lambda: sys.moveUp(moveAmount))
upButton.grid(row = 0, column=1)

downButton = Button(frame, text="v", command=lambda: sys.moveDown(moveAmount))
downButton.grid(row = 2, column=1)

inButton = Button(frame, text="+", command=lambda: sys.zoomIn(moveAmount))
inButton.grid(row = 0, column=4)

outButton = Button(frame, text="-", command=lambda: sys.zoomOut(moveAmount))
outButton.grid(row = 2, column=4)



frame.pack()

sys.updateWorlds(0.001)
sys.updateDraw()

mainloop()