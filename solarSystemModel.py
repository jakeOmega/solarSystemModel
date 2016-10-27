from tkinter import *
from world import *
from system import *
import thread
import random
import math

#constants
moveAmount = 10.0          # how many pixels to move when hitting move buttons
speedChangeAmount = 1.5    # how much to speed up/slow down simulation per button press
shiftSpeedUp = 3
# format:
# (key, (shift (1 or 0), control (1 or 0), alt (1 or 0))) : ('method to call', [arguments])
keyBinds = {
    (87, (0, 0, 0)) : ('moveUp', [moveAmount]),
    (83, (0, 0, 0)) : ('moveDown', [moveAmount]),
    (65, (0, 0, 0)) : ('moveLeft', [moveAmount]),
    (68, (0, 0, 0)) : ('moveRight', [moveAmount]),
    (87, (1, 0, 0)) : ('moveUp', [shiftSpeedUp*moveAmount]),
    (83, (1, 0, 0)) : ('moveDown', [shiftSpeedUp*moveAmount]),
    (65, (1, 0, 0)) : ('moveLeft', [shiftSpeedUp*moveAmount]),
    (68, (1, 0, 0)) : ('moveRight', [shiftSpeedUp*moveAmount]),
    (187, (0, 0, 0)) : ('speedUp', [speedChangeAmount]),
    (189, (0, 0, 0)) : ('slowDown', [speedChangeAmount]),
    (32, (0, 0, 0)) : ('pause', [])
    }

temp = system.moveRight


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
        sys = system(root, 0.1)
        self.sys = sys
        #sys.worlds = [world(sys, 333000, 0, 0, 0, 0.262, 0.5), 
        #              world(sys, 318, 1.3, 0, 0, 5.5, 0.075),
        #              world(sys, 31800, 5.2, 0, 0, -2.75, 0.15), 
        #              world(sys, 0.025, 5.2+0.7155, 0, 0, -2.75+2.294, 0.05)]
        sys.worlds = [world(sys, 333000, 0, 0, 0, 0, 0.2)]
        for i in range(600):
            rand = random.uniform(0, 2*math.pi)
            rand2 = random.uniform(-0.01, 0.01)
            rand3 = random.uniform(-0.01, 0.01)
            rand4 = random.uniform(-2, 2)
            rand5 = random.uniform(-2, 2)
            sys.worlds += [world(sys, 1, 8*math.sin(rand) + rand4, 8*math.cos(rand) + rand5, 
                                 0.5 * math.pi * math.cos(rand) + rand2, 
                                 -0.5 * math.pi * math.sin(rand) + rand3, 0.03)]
        sys.cameraPos = (-0.0, -0.0)
        sys.scale = 25.0
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
                          command=lambda: sys.zoomIn())
        inButton.grid(row = 0, column=4)

        outButton = Button(zoomFrame, height=buttonSize, 
                           width=2*buttonSize, text="-", 
                           command=lambda: sys.zoomOut())
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

        root.bind('<Key>', self.handleKeys)

        sys.pause(pauseButton)

        sys.updateWorlds()
        sys.updateDraw()

    def handleKeys(self, event):
        modifierState = (event.state % 2, event.state/4 % 2, event.state/2**17 % 2)
        key = (event.keycode, modifierState)
        if key in keyBinds:
            args = keyBinds[key][1]
            getattr(self.sys, keyBinds[key][0])(*args)


root = Tk()
solarSystemApp = systemApp(root)


mainloop()