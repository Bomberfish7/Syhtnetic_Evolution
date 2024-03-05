#-------------------------------------------------------------------------------
# Name:        Statics
# Purpose:
#
# Author:      The Throngler & co.
#
# Created:     10/24/2023
#-------------------------------------------------------------------------------

import pygame
import pygame_gui as gui
import math
import numpy as np
import uuid

class Point:
    #A simple 2D point in space. Can also act as a 2D Vector if needed
    def __init__(self,a=0,b=0):
        self.a=a
        self.b=b
    def __str__(self):
        return f'({self.a}, {self.b})'

    def getA(self):
        return self.a
    def getB(self):
        return self.b
    def getPoint(self):
        return [self.a,self.b]

    def setA(self,a):
        self.a=a
    def setB(self,b):
        self.b=b
    def setPoint(self,p):
        self.a=p[0]
        self.b=p[1]

class Line:
    #A simple 2D line
    def __init__(self,a=Point(),b=Point()):
        self.a=a
        self.b=b
        self.calcSlope()#(self.b.getB()-self.a.getB())/(self.b.getA()-self.a.getA())
    def __str__(self):
        return f'[{self.a} , {self.b}], slope: {self.slope}'

    def getA(self):
        return self.a.getPoint()
    def getB(self):
        return self.b.getPoint()
    def getLine(self):
        return [self.a.getPoint(),self.b.getPoint(),self.slope]
    def getSlope(self):
        return self.slope

    def setA(self,a):
        self.a=a.setPoint()
        self.calcSlope()
    def setB(self,b):
        self.b=b.setPoint()
        self.calcSlope()
    def setLine(self,line):
        self.a=line[0].getPoint()
        self.b=line[1].getPoint()
        self.slope=line[2]

    def calcSlope(self):
        x_comp = (self.b.getA()-self.a.getA())
        y_comp = (self.b.getB()-self.a.getB())
        if x_comp != 0:
            self.slope = y_comp/x_comp#(self.b.getA()-self.a.getA())
        elif y_comp == 0:
            self.slope = 0
        else:
            self.slope = float("inf") if y_comp > 0 else float("-inf")

class Circle:
    #A simple 2D circle
    def __init__(self,pos=Point(),radius=1):
        self.pos=pos
        self.radius=radius
    def __str__(self):
        return f'[{self.pos} , r={self.radius}]'

    def getPos(self):
        return self.pos
    def getRadius(self):
        return self.radius
    def getCircle(self):
        return [self.pos,self.radius]

    def setPos(self,pos):
        self.pos=pos
    def setRadius(self,radius):
        self.radius=radius
    def setCircle(self,circle):
        self.pos=circle[0]
        self.radius=circle[1]

class Object:
    #Base object type for anything interactable in the simulation
    def __init__(self,pos=Point(),delta=Point(),angle=0,shape=[Point(),Point(),Point()],size=1,color=None,outline=None,mass=10,friction=1,obj_id="Undefined",health=None,energy=None,max_health=10,max_energy=10,immortal=False,ui_label=None):
        if color is None:
            color=c_debug1
        if outline is None:
            outline=black
        if health is None:
            health=max_health
        if energy is None:
            energy=max_energy
        self.pos=pos
        self.delta=delta
        self.angle=math.radians(angle)
        self.shape=shape
        self.size=size
        self.hitbox=None
        self.visuals=None
        self.ui_label=ui_label
        self.color=color
        self.outline=outline
        self.mass=mass
        self.friction=friction
        self.obj_id=obj_id
        self.health=health
        self.energy=energy
        self.max_health=max_health
        self.max_energy=max_energy
        self.immortal=immortal
        self.dimensions=pygame.Rect(0,0,0,0)
        self.vis_dimensions=pygame.Rect(0,0,0,0)
        if self.ui_label == None:
            self.ui_label = gui.elements.ui_text_box.UITextBox(html_text="<font face='freesansbold' color='#1932e1' size=16px><b>Lorem Ipsum</b></font>",relative_rect=pygame.Rect(self.vis_dimensions.x-80,self.vis_dimensions.y-45,160,75),visible=0)
        self.UpdateHitbox()

        self._update_lable_timer=5
        self._remove=False
        self.UUID=str(uuid.uuid4())
    def __str__(self):
        if(self.immortal):
            return f'Object:\"{self.obj_id}\"🗹\t [Pos:{self.pos}, Speed:{self.delta}, Size:{self.size}, Health:{self.health}/{self.max_health}, Energy:{self.energy}/{self.max_energy}, Mass:{self.mass}, Friction:{self.friction}, UUID:{self.UUID}]'
        return f'Object:\"{self.obj_id}\"☐\t [Pos:{self.pos}, Speed:{self.delta}, Size:{self.size}, Health:{self.health}/{self.max_health}, Energy:{self.energy}/{self.max_energy}, Mass:{self.mass}, Friction:{self.friction}, UUID:{self.UUID}]'

    def getPos(self):
        return self.pos
    def getDelta(self):
        return self.delta
    def getAngle(self):
        return math.degrees(self.angle)
    def getDim(self):
        return self.dimensions
    def getSize(self):
        return self.size
    def getShape(self):
        return self.shape
    def getShapePoint(self,index):
        return self.shape[index]
    def getHitbox(self):
        return self.hitbox
    def getVisuals(self):
        return self.visuals
    def getVisDim(self):
        return self.vis_dimensions
    def getColor(self):
        return self.color
    def getOutline(self):
        return self.outline
    def getMass(self):
        return self.mass
    def getFric(self):
        return self.friction
    def getId(self):
        return self.obj_id
    def getHealth(self):
        return self.health
    def getEnergy(self):
        return self.energy
    def getImmo(self):
        return self.immortal
    def getMaxHP(self):
        return self.max_health*self.size
    def getMaxEN(self):
        return self.max_energy*self.size
    def getLabel(self):
        return self.ui_label
    def getLabelCopy(self):
        return [self.ui_label.html_text,self.ui_label.relative_rect,self.ui_label.visible]
    def getObjectCopy(self):
        return [self.pos,self.delta,self.angle,self.shape,self.size,self.hitbox,self.dimensions,self.color,self.outline,self.mass,self.friction,self.obj_id,self.health,self.energy,self.max_health,self.max_energy,self.immortal,[self.ui_label.html_text,self.ui_label.relative_rect,self.ui_label.visible],self.UUID]

    def setPos(self,pos):
        self.pos=pos
    def setDelta(self,delta):
        self.delta=delta
    def setAngle(self,angle):
        self.angle=math.radians(angle)
    def setDim(self,dimensions):
        self.dimensions=dimensions
    def setSize(self,size):
        self.size=size
    def setShape(self,shape):
        self.shape=shape
    def setShapePoint(self,point,index):
        self.shape[index]=point
    def setColor(self,color):
        self.color=color
    def setOutline(self,outline):
        self.outline=outline
    def setMass(self,mass):
        self.mass=mass
    def setFric(self,friction):
        self.friction=friction
    def setId(self,obj_id):
        self.obj_id=obj_id
    def setHealth(self,health):
        self.health=health
    def setEnergy(self,energy):
        self.energy=energy
    def setImmo(self,immortal):
        self.immortal=immortal
    def setMaxHP(self,max_health):
        self.max_health=max_health
    def setMaxEN(self,max_energy):
        self.max_energy=max_energy
    def setLabel(self,ui_label):
        self.ui_label.html_text=ui_label[0]
        self.ui_label.relative_rect=ui_label[1]
        self.ui_label.visible=ui_label[2]
    def setLabelVis(self,visible):
        self.ui_label.visible=visible
    def setObjectCopy(self,copy,copyUUID=False):
        self.pos=Point(copy[0].getA(),copy[0].getB())
        self.delta=Point(copy[1].getA(),copy[1].getB())
        self.angle=copy[2]
        self.shape=[]
        for i in copy[3]:
            self.shape.append(Point(i.getA(),i.getB()))
        self.size=copy[4]
        self.hitbox=None
        self.dimensions=pygame.Rect(0,0,0,0)
        self.UpdateHitbox()
        self.color=(copy[7][0],copy[7][1],copy[7][2])
        self.outline=(copy[8][0],copy[8][1],copy[8][2])
        self.mass=copy[9]
        self.friction=copy[10]
        self.obj_id=copy[11]
        self.health=copy[12]
        self.energy=copy[13]
        self.max_health=copy[14]
        self.max_energy=copy[15]
        self.immortal=copy[16]
        self.ui_label.html_text=copy[17][0]
        self.ui_label.relative_rect=copy[17][1]
        self.ui_label.visible=copy[17][2]
        if(copyUUID):
            self.UUID=copy[18]

    def DeathTest(self):
        if(self.immortal or self.health>0):
            return False
        return True
    def UpdateHitbox(self):
        global camera
        global zoom
        a=[]
        b=[]
        rad=math.radians(self.angle)
        cosang,sinang=math.cos(rad),math.sin(rad)
        for i in range(len(self.shape)):
            x,y=self.shape[i].getA(),self.shape[i].getB()
            a.append([(x*cosang+y*sinang)*self.size+self.pos.getA(),(-x*sinang+y*cosang)*self.size+self.pos.getB()])
            b.append([((x*cosang+y*sinang)*self.size+self.pos.getA()+camera.getA())*zoom.getA()+s_width/2,((-x*sinang+y*cosang)*self.size+self.pos.getB()+camera.getB())*zoom.getB()+s_height/2])
        self.hitbox=a
        self.visuals=b
        self.UpdateDimensions()
    def UpdateDimensions(self):
        global camera
        global zoom
        min_x=self.hitbox[0][0]
        min_y=self.hitbox[0][1]
        max_x=self.hitbox[0][0]
        max_y=self.hitbox[0][1]

        for i in self.hitbox:
            if(i[0]<min_x):
                min_x=i[0]
            if(i[1]<min_y):
                min_y=i[1]
            if(i[0]>max_x):
                max_x=i[0]
            if(i[1]>max_y):
                max_y=i[1]
        self.dimensions.x=min_x
        self.dimensions.y=min_y
        self.dimensions.w=max_x-min_x
        self.dimensions.h=max_y-min_y

        self.vis_dimensions.x=(min_x+camera.getA())*zoom.getA()+s_width/2
        self.vis_dimensions.y=(min_y+camera.getB())*zoom.getB()+s_height/2
        self.vis_dimensions.w=(max_x-min_x)*zoom.getA()
        self.vis_dimensions.h=(max_y-min_y)*zoom.getB()

    def generateLabel(self):
        self._update_lable_timer+=1
        energy_str="Energy: "+str("%.2f" % round(self.energy,2))+"/"+str("%.2f" % round(self.max_energy*self.size,2))
        box_len=len(energy_str)
        box_len*=10


        self.ui_label.set_position(((self.vis_dimensions.x+self.vis_dimensions.w/2)-box_len/2+2,(self.vis_dimensions.top)-75))
        if self._update_lable_timer>=5:

            self.ui_label.set_dimensions((box_len,85))
            self.ui_label.set_text("<font face='freesansbold' color='#1932e1' size=16px><b>Size: "+str("%.2f" % round(self.size,2))+"</b></font><br><font face='freesansbold' color='#e13232' size=16px><b>Health: "+str("%.2f" % round(self.health,2))+"/"+str("%.2f" % round(self.max_health*self.size,2))+"</b></font><br><font face='freesansbold' color='#19c819' size=16px><b>"+energy_str+"&nbsp</b></font>")
            self._update_lable_timer=0

class Tile(Object):
    #Any terrain object
    def __init__(self,pos=Point(),delta=Point(),angle=0,shape=[Point(),Point(),Point()],size=1,color=None,outline=None,mass=10,friction=1,obj_id="Undefined",health=None,energy=None,max_health=10,max_energy=10,immortal=True,tile=0,area=0):
        super().__init__(pos,delta,angle,shape,size,color,outline,mass,friction,obj_id,health,energy,max_health,max_energy,immortal)
        self.tile=tile
        self.area=area
        self.ui_label.html_text="<p>Tile</p>"
        self.ui_label.visible=False
    def __str__(self):
        return f'Tile:\"{self.obj_id}\"\t [Pos:{self.pos}, Speed:{self.delta}, Size:{(self.dimensions.w,self.dimensions.h)}, Tile Type:{self.tile}, Area:{self.area}]'
    def getObjStr(self):
        return super().__str__()

    def getTile(self):
        return self.tile
    def getTileCopy(self):
        return [self.getObjectCopy(),self.tile,self.area]

    def setTile(self,tile):
        self.tile=tile
    def setTileCopy(self,copy):
        self.setObjectCopy(copy[0])
        self.tile=copy[1]
        self.area=copy[2]
    def generateLabel(self):
        pass

class Edge:
    #An Edge line for an object
    def __init__(self,pos,stop,parent):
        self.pos=pos
        self.stop=stop
        self.parent=parent
    def __str__(self):
        return f'"{self.parent.getId()}", {self.parent.UUID}: {self.pos}, {self.stop}'

    def getPos(self):
        return self.pos
    def getStop(self):
        return self.stop
    def getParent(self):
        return self.parent
    def getEdgeCopy(self):
        return [self.pos,self.stop,self.parent]

    def setPos(self,pos):
        self.pos=pos
    def setStop(self,stop):
        self.stop=stop
    def setParent(self,parent):
        self.parent=parent
    def setEdgeCopy(self,copy):
        self.pos=copy[0]
        self.stop=copy[1]
        self.parent=copy[2]

class Aura():
    #An area of effect around an object
    def __init__(self,pos=Point(),size=1,strength=0,parent=""):
        self.pos=pos
        self.size=size
        self.strength=strength
        self.parent=parent
        self.dimensions=pygame.Rect(0,0,0,0)
        self.vis_dimensions=pygame.Rect(0,0,0,0)
        self.UpdateDimensions()
        self._remove=False
        self.UUID=str(uuid.uuid4())
    def __str__(self):
        return f'"{self.parent.getId()}", {self.parent.UUID}: {self.size}, {self.strength}'

    def getPos(self):
        return self.pos
    def getSize(self):
        return self.size
    def getStrength(self):
        return self.strength
    def getParent(self):
        return self.parent
    def getDim(self):
        return self.dimensions
    def getVisDim(self):
        return self.vis_dimensions
    def getAuraCopy(self):
        return [self.pos,self.size,self.strength,self.parent,self.UUID]

    def setPos(self,pos):
        self.pos=pos
    def setSize(self,size):
        self.size=size
    def setStrength(self,strength):
        self.strength=strength
    def setParent(self,parent):
        self.parent=parent
    def setDim(self,dimensions):
        self.dimensions=dimensions
    def setAuraCopy(self,copy,copyUUID=False):
        self.pos=copy[0]
        self.size=copy[1]
        self.strength=copy[2]
        self.parent=copy[3]
        if copyUUID:
            self.UUID=copy[4]

    def UpdateDimensions(self):

        self.dimensions.center=self.getPos().getPoint()
        self.dimensions.w=3*tile_size*self.size
        self.dimensions.h=3*tile_size*self.size

        self.vis_dimensions.center=[(self.getPos().getA()+camera.getA())*zoom.getA()+s_width/2,(self.getPos().getB()+camera.getB())*zoom.getB()+s_height/2]
        self.vis_dimensions.w=(3*tile_size*self.size)*zoom.getA()
        self.vis_dimensions.h=(3*tile_size*self.size)*zoom.getB()

#Initialize Pygame
pygame.init()

#Screen Constants
s_width=1024
s_height=576
tile_size=32
tile_offset=tile_size/2
chunk_size=12
chunk_limit=6
##tile_screens=1.5
tile_boundary=int(chunk_size*chunk_limit)
coord_limit=(tile_boundary*tile_size)/2
maps_generated=0
running=True
clock=pygame.time.Clock()
fps=60
ups=fps
time_delta=0
UPS_samples=fps
vis_UPS=[0]*UPS_samples
vis_UPS_counter=0
freeze_ups=0
camera=Point(0,0)
zoom=Point(1,1)


manager=gui.UIManager((s_width,s_height))
manager.get_theme().load_theme('textbox_theme.json')

#Colors/Fonts
##Basic default colors
red=(225,50,50)
green=(25,200,25)
blue=(25,50,225)
white=(255,255,255)
black=(15,15,20)

##Base sim colors
c_background=(50,50,50)
c_night=(15,10,25)
c_debug1=(255,25,175)

##Food Colors
c_grass=(125,225,25)
c_bush=(80,155,100)
c_tree=(40,110,45)
c_fruit=(235,175,240)
c_kelp=(25,200,45)
c_poison=(200,15,225)
c_mushroom=(170,145,115)
c_fungus=(145,115,170)
c_meat=(230,60,90)
c_bone=(255,250,245)
c_egg=(240,235,200)
c_bug=(225,225,50)
c_fish=(25,25,40)

##Terrain Colors
c_water=(75,165,240)
c_land=(73, 99, 15)
c_testwater=(95,220,255)
c_error=(237, 9, 188)

font0=pygame.font.Font('freesansbold.ttf',16)
font1=pygame.font.Font('freesansbold.ttf',8)
font2=pygame.font.Font('freesansbold.ttf',5)
font3=pygame.font.Font('freesansbold.ttf',32)