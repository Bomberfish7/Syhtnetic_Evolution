#-------------------------------------------------------------------------------
# Name:        Synthetic Evolution 2.2.1
# Purpose:
#
# Author:      The Throngler & co.
#
# Created:     05/12/2023
#-------------------------------------------------------------------------------

import pygame
import math
import numpy as np
import random
import traceback
import sys

from Globals import *
from Statics import *
from Food_Types import *





#TO DO:
#   Make Move method for Prey Foods
#   Make Method to scale foods natural color to Poison or Medicinal color based on poison value (Purple(-) -> Base Color(0) -> Blue(+))
#   Make better collision algorithm
#   Add error try/exception




def UpdateTime():
    #Updates everything time-related
    Globals.day_percent=np.clip(Globals.day_percent,0,1)

    Globals.time+=Globals.timescale
    t=Globals.time%Globals.day_length
    a=((1-Globals.day_percent)*1.7*Globals.day_length-0.35*Globals.day_length)/2.0
    if(t<=Globals.day_length/2):
        Globals.light=round(80.0*(1.0/(1+math.exp((t-(Globals.day_length/2.0-a))/(Globals.day_length*0.03))))+20)
    else:
        Globals.light=round(80.0*(1.0/(1+math.exp((t-(Globals.day_length/2.0+a))/(Globals.day_length*-0.03))))+20)


    FoodUpdate()
    CollisionHandler()
    ClearRemoves()

def CreateBaseFood(pos,angle,size,food_type):
    #Creates a food object given parameters
    global Base_Foods

    food_type=np.clip(food_type,0,len(Base_Foods))
    if(food_type<=3):
        #Grass, Bushes, Trees, and Kelp
        new_food=Plant()
    elif(food_type==4):
        #Fruits
        new_food=Fruit()
    elif(food_type==5):
        #Mushrooms
        new_food=Mushroom()
    elif(food_type==6 or food_type==7):
        #Meat and Bones
        new_food=Food()
    elif(food_type==8 or food_type==9):
        #Bugs and Fish
        new_food=PreyFood()
    else:
        #Eggs
        new_food=Food()
    new_food.setFoodCopy(Base_Foods[food_type].getFoodCopy())
    new_food.setPos(Point(pos.getA(),pos.getB()))
    new_food.setShape(shapes[Base_Foods[food_type].getId()][0])
    new_food.setAngle(angle)
    new_food.setSize(size)
    new_food.UpdateHitbox()
    new_food.setOutline((np.clip(new_food.getColor()[0]+random.randint(-25,25),0,255),np.clip(new_food.getColor()[1]+random.randint(-25,25),0,255),np.clip(new_food.getColor()[2]+random.randint(-25,25),0,255)))
    return new_food

def CreateFood(pos,angle,size,energy,food):
    #Creates a food object from another food
    shapeIndex = 1 if type(food) in cluster_classes else 0
    if isinstance(food,Plant):
        new_food=Plant()
    elif isinstance(food,Fruit):
        new_food=Fruit()
    elif isinstance(food,Mushroom):
        new_food=Mushroom()
    elif isinstance(food,PreyFood):
        new_food=PreyFood()
    elif isinstance(food,Egg):
        new_food=Egg()
    else:
        new_food=Food()

    new_food.setFoodCopy(food.getFoodCopy())
    new_food.setPos(Point(pos.getA(),pos.getB()))
    new_food.setShape(shapes[food.getId()][0])
    new_food.setAngle(angle)
    new_food.setSize(size)
    new_food.UpdateHitbox()
    new_food.setEnergy(energy)
    new_food.setOutline((np.clip(new_food.getColor()[0]+random.randint(-25,25),0,255),np.clip(new_food.getColor()[1]+random.randint(-25,25),0,255),np.clip(new_food.getColor()[2]+random.randint(-25,25),0,255)))
    return new_food

def SortTiles():
    #Sorts terrain tiles first by y value, then x
    global test_terrain

    test_terrain.sort(key=lambda i: i.getPos().getB())
    i=0
    while i<len(test_terrain)-1:
        if(test_terrain[i].getPos().getB()==test_terrain[i+1].getPos().getB() and test_terrain[i].getPos().getA()>test_terrain[i+1].getPos().getA()):
            IndexSwap(test_terrain,i,i+1)
            i-=1
        else:
            i+=1

def IndexSwap(edit_list,i,j):
    #Swaps the indexes of 2 items in a list
    edit_list[i],edit_list[j]=edit_list[j],edit_list[i]

def MergeTiles():
    #Merges like tiles to make computing easier
    global test_terrain
    global tile_size
    global tile_offset
    SortTiles()

    a=[]
    b=[]

    for i in range(len(test_terrain)):
        a.append(Tile())
        b.append(Tile())
        a[i].setTileCopy(test_terrain[i].getTileCopy())
        b[i].setTileCopy(test_terrain[i].getTileCopy())

    # Check H then V
    a=MergeTilesV(MergeTilesH(a))
    # Check V then H
    b=MergeTilesH(MergeTilesV(b))

    if len(a)<=len(b):
        test_terrain=a.copy()
    else:
        test_terrain=b.copy()

def MergeTilesH(edit_list):
    #Horizontally merges tiles
    new_list=edit_list.copy()
    i=len(new_list)-1
    while i>0:
        j=i-1
        while j>=0:
            if(i!=j and PointInRect(Point(new_list[i].getDim().midleft[0]-tile_offset,new_list[i].getPos().getB()),new_list[j].getDim()) and new_list[i].getDim().h==new_list[j].getDim().h):
                new_list[i].setShapePoint(Point(new_list[i].getShapePoint(1).getA()-new_list[j].getDim().w,new_list[i].getShapePoint(1).getB()),1)
                new_list[i].setShapePoint(Point(new_list[i].getShapePoint(2).getA()-new_list[j].getDim().w,new_list[i].getShapePoint(2).getB()),2)
                new_list[i].UpdateHitbox()
                new_list.pop(j)
                i-=1
            j-=1
        i-=1
    return new_list.copy()

def MergeTilesV(edit_list):
    #Vertically merges tiles
    new_list=edit_list.copy()
    i=len(new_list)-1
    while i>0:
        j=i-1
        while j>=0:
            if(i!=j and PointInRect(Point(new_list[i].getPos().getA(),new_list[i].getDim().midtop[1]-tile_offset),new_list[j].getDim()) and new_list[i].getDim().w==new_list[j].getDim().w):
                new_list[i].setShapePoint(Point(new_list[i].getShapePoint(2).getA(),new_list[i].getShapePoint(2).getB()-new_list[j].getDim().h),2)
                new_list[i].setShapePoint(Point(new_list[i].getShapePoint(3).getA(),new_list[i].getShapePoint(3).getB()-new_list[j].getDim().h),3)
                new_list[i].UpdateHitbox()
                new_list.pop(j)
                i-=1
            j-=1
        i-=1
    return new_list.copy()

def FoodInWater():
    #Hurts foods outside of their correct area
    global Foods
    global test_terrain

    for i in Foods:
        if(Entities[i].getAquatic()==0):
            drowning=False
        elif(Entities[i].getAquatic()==1):
            drowning=True
        else:
            drowning=False
        for j in test_terrain:
            if(Entities[i].getAquatic()==0):
                if(PointInRect(Entities[i].getPos(),j.getDim())):
                    drowning=True
            elif(Entities[i].getAquatic()==1):
                if(PointInRect(Entities[i].getPos(),j.getDim())):
                    drowning=False
        if(drowning):
            Entities[i].Drown()
#^^  Unfinished  (good collisions are not done yet)^^

def FoodUpdate():
    #Updates various functions for all foods

    FoodRegen()
    FoodInWater()
    FoodReproduce()

def FoodRegen():
    #Regenerates foods health and energy
    global Foods
    global Entities

    for i in Foods:
        if type(Entities[i]) in [Plant,PlantCluster]:
            Entities[i].RegenHealth()
            Entities[i].Grow()
        Entities[i].RegenEnergy()
        Entities[i].HurtOnLowEnergy()
        Entities[i].UpdateHitbox()
        if Entities[i].getHealth()<=0:
            Entities[i]._remove=True

def PointInRect(point,rect):
    #Finds if a point is inside a bounding box
    return rect.collidepoint(point.getPoint())

def PointInPolygon(point,poly):
    #Finds if a point is inside a polygon
    pass
#^^  Unfinished  ^^

def CollisionHandler():
    #Handles collision between all objects
    global Foods
    global Entities

    for i in Foods:
        if(type(Entities[i]) in [Plant,PlantCluster]):
            Entities[i].setNbr(0.0)
    #ToDo1: MergeClusters and old on-collision behavior relies on order and behavior of original collision checking to ensure array bounds and non-skipping.  Breaks with SAP.
    SweepAndPrune(Entities)

def PolyToLine(poly):
    #Takes a set of points from a polygon and converts it into a set of lines that define the polygon

    lines=[]
    poly_len=len(poly)
##    print([str(i) for i in poly])

    for i in range(poly_len):
        lines.append(Line(Point(poly[i][0],poly[i][1]),Point(poly[(i+1)%poly_len][0],poly[(i+1)%poly_len][1])))

    return lines

def PolyPolyCollison(a,b):
    #Detects collisions between 2 polygons

    a1=PolyToLine(a)
    b1=PolyToLine(b)

    for i in b1:
        if PolyLineCollision(a1,i):
            return True

    return False

def PolyLineCollision(p,l):
    #Detects collisions between a polygon and a line

    for i in p:
        if LineLineCollision(i.getA()[0],i.getA()[1],i.getB()[0],i.getB()[1],l.getA()[0],l.getA()[1],l.getB()[0],l.getB()[1]):
            return True

    return False

def LineLineCollision(Ax1,Ay1,Ax2,Ay2,Bx1,By1,Bx2,By2):
    #Detects collisions between 2 lines

    d=(By2-By1)*(Ax2-Ax1)-(Bx2-Bx1)*(Ay2-Ay1)
    if d:
        uA=((Bx2-Bx1)*(Ay1-By1)-(By2-By1)*(Ax1-Bx1))/d
        uB=((Ax2-Ax1)*(Ay1-By1)-(Ay2-Ay1)*(Ax1-Bx1))/d
    else:
        return False
    if not(0<=uA<=1 and 0<=uB<=1):
        return False
    return True

def SweepAndPrune(obj_list):
    #Better collision between objects

    if len(obj_list)<=0:
        return

    horizontal=SAPListEdges(obj_list,True)
    vertical=SAPListEdges(obj_list,False)

    h_var=SAPEdgeVariance(horizontal)
    v_var=SAPEdgeVariance(vertical)

    if(h_var>v_var):
        SAPCheckEdges(horizontal)
    else:
        SAPCheckEdges(vertical)

def SAPListEdges(obj_list,axis):
    #Creates a list for SAP of all edges of objects

    edges=[]

    if axis:
        for key in obj_list:
            i=obj_list[key]
            l=Edge(i.getDim().left,False,key)
            r=Edge(i.getDim().right,True,key)

            edges.append(l)
            edges.append(r)

    else:
        for key in obj_list:
            i=obj_list[key]
            t=Edge(i.getDim().top,False,key)
            b=Edge(i.getDim().bottom,True,key)

            edges.append(t)
            edges.append(b)

    edges.sort(key=Edge.getPos)
    return edges

def SAPEdgeVariance(edge_list):
    #Finds the variance between spacing of edges

    length=len(edge_list)
    mean=0.0
    variance=0.0

    for i in edge_list:
        mean+=i.getPos()
    mean/=length
    for i in edge_list:
        variance+=math.pow(i.getPos()-mean,2)
    variance=math.sqrt(variance/length)

    return variance

def SAPCheckEdges(edge_list):
    #Calculates which shapes are possibly colliding
    global Entities

    check=[]

    for i in edge_list:
        if Entities.get(i.getParent(),False)==False or Entities[i.getParent()]._remove:
            continue
        else:
            if i.getStop():
                if i.getParent() in check:
                    check.remove(i.getParent())
            else:
                if len(check)>0:
                    SAPCollison(i.getParent(),check)
                check.append(i.getParent())

def SAPCollison(a,check_list):
    #Checks if current object is colliding with any objects in check_list
    global Entities

    for i in check_list:
        if(Entities[a].getDim().colliderect(Entities[i].getDim())):
            if PolyPolyCollison(Entities[a].getHitbox(),Entities[i].getHitbox()):
                SAPCollide(a,i)

def SAPCollide(a,b):
    #Runs what happens when 2 objects collide
    global Entities

    if(Entities.get(a,False)==False or Entities.get(b,False)==False):
        return
    if type(Entities[a]) in [Food,Plant,Mushroom,FoodCluster,PlantCluster,MushroomCluster] and type(Entities[b]) in [Food,Plant,Mushroom,FoodCluster,PlantCluster,MushroomCluster]:

        if type(Entities[a]) in [FoodCluster,PlantCluster,MushroomCluster]:
            MergeClusters(a,b)
            return
        elif type(Entities[b]) in [FoodCluster,PlantCluster,MushroomCluster]:
            MergeClusters(b,a)
            return
        else:
            MergeClusters(a,b)
            return

    if (type(Entities[a]) in [Plant,PlantCluster] and type(Entities[b]) in [Plant,PlantCluster] and Entities[a]._remove==False and Entities[b]._remove==False):
        if (Entities[a].getId()=="Tree" and Entities[b].getId()=="Tree"):
            Entities[a].setNbr(Entities[a].getNbr()+Entities[b].getMaxEN()/2400)
            Entities[b].setNbr(Entities[b].getNbr()+Entities[a].getMaxEN()/2400)
        else:
            if Entities[a].getId()=="Tree":
                Entities[a].setNbr(FoodsEntities[a].getNbr()+FoodsEntities[b].getMaxEN()/900)
            else:
                Entities[a].setNbr(Entities[a].getNbr()+FoodsEntities[b].getMaxEN()/450)
            if Entities[b].getId()=="Tree":
                Entities[b].setNbr(Entities[b].getNbr()+Entities[a].getMaxEN()/900)
            else:
                Entities[b].setNbr(Entities[b].getNbr()+Entities[a].getMaxEN()/450)

def ClearRemoves():
    #Deletes objects from list tagged with _remove
    global Foods
    global Creatures
    global Entities

    for key in Foods:
        if key in Entities:
            if Entities[key]._remove==True:
                Foods.remove(key)
                del Entities[key]

    for key in Creatures:
        if key in Entities:
            if Entities[key]._remove==True:
                Creatures.remove(key)
                del Entities[key]

def MergeClusters(a,b):
    #Merges like foods into clusters
    global Entities

    if(Entities[a].getId()==Entities[b].getId() and type(Entities[b]) in [Food,Plant,Mushroom]):
        if not type(Entities[a]) in [FoodCluster,PlantCluster,MushroomCluster]:
            if type(Entities[a]) is Food:
                c=FoodCluster()
                c.setClusterFood(Entities[a])
                c.setShape(shapes[Entities[a].getId()][1])
                Entities[a]=c
            if type(Entities[a]) is Plant:
                c=PlantCluster()
                c.setClusterFood(Entities[a])
                c.setShape(shapes[Entities[a].getId()][1])
                Entities[a]=c
            if type(Entities[a]) is Mushroom:
                c=MushroomCluster()
                c.setClusterFood(Entities[a])
                c.setShape(shapes[Entities[a].getId()][1])
                Entities[a]=c
        if(Entities[a].getMaxSZ()<4):
            Entities[a].Merge(Entities[b])
            Entities[b]._remove=True
            return True
    return False









def FoodReproduce():
    #Creates more food from the other foods in the simulation
    global Foods
    global Entities

    for key in Foods:
        i=Entities[key]
        if(i.getSize()>=1):
            r=random.uniform(0,100)
            if(i.getId()=="Grass" and i.getEnergy()>=i.getMaxEN()*0.9 and r<=(i.getMaxSZ()*0.1/Globals.fps)*Globals.timescale):
                size=random.uniform(0.45,0.55)
                radius=random.uniform(16,48)*i.getSize()
                direction=random.uniform(0,360)
                pos=Point(i.getPos().getA()+radius*math.cos(math.radians(direction)),i.getPos().getB()+radius*math.sin(math.radians(direction)))
                spawn=True
                for key2 in Entities:
                    j=Entities[key2]
                    if(PointInRect(Point(pos.getA(),pos.getB()-6),j.getDim())):
                        grass_r=random.uniform(0,100)
                        if(grass_r>=25):
                            spawn=False
                if(spawn):
                    newfood=CreateFood(pos,0,size,size*i.getMaxEN()*0.2,i)
                    Entities[newfood.UUID]=newfood
                    Foods.append(newfood.UUID)
                    i.setEnergy(i.getEnergy()*(1-0.5*(1+(size-0.5))))
            elif(i.getId()=="Bush" and i.getEnergy()>=i.getMaxEN()*0.9 and r<=(i.getMaxSZ()*0.05/Globals.fps)*Globals.timescale):
                size=random.uniform(0.15,0.25)
                radius=random.uniform(32,80)*i.getSize()
                direction=random.uniform(0,360)
                pos=Point(i.getPos().getA()+radius*math.cos(math.radians(direction)),i.getPos().getB()+radius*math.sin(math.radians(direction)))

                newfood=CreateFood(pos,0,size,size*i.getMaxEN()*0.1,i)
                Entities[newfood.UUID]=newfood
                Foods.append(newfood.UUID)
                i.setEnergy(i.getEnergy()*(1-0.6*(1+(size-0.2))))
            elif(i.getId()=="Tree" and i.getEnergy()>=i.getMaxEN()*0.975 and r<=(i.getMaxSZ()*0.15/Globals.fps)*Globals.timescale):
                f=random.randrange(1,round(5*(math.pow(i.getSize(),0.75))))
                for j in range(f):
                    size=random.uniform(0.90,1.10)
                    radius=random.uniform(32,80)*(math.pow(3*i.getSize(),(1/3)))
                    direction=random.uniform(0,360)
                    pos=Point(i.getPos().getA()+radius*math.cos(math.radians(direction)),i.getPos().getB()+radius*math.sin(math.radians(direction)))

                    new_fruit=CreateFood(pos,0,size,size*(i.getMaxEN()/i.getMaxSZ())*1,Base_Foods[4])
                    new_seed=Plant()
                    new_seed.setFoodCopy(i.getFoodCopy())
                    new_fruit.setSeed(new_seed)
                    Entities[new_fruit.UUID]=new_fruit
                    Foods.append(new_fruit.UUID)
                    i.setEnergy(i.getEnergy()-(i.getEnergy()/i.getMaxSZ())*(0+0.1*(1+(size-1.0))))#FIXME fruit energy cost/starting value fuckery here up
            elif(i.getId()=="Kelp" and i.getEnergy()>=i.getMaxEN()*0.75 and r<=(i.getMaxSZ()*0.15/Globals.fps)*Globals.timescale):
                size=random.uniform(0.05,0.15)
                radius=random.uniform(16,32)*i.getSize()
                direction=random.uniform(0,360)
                pos=Point(i.getPos().getA()+radius*math.cos(math.radians(direction)),i.getPos().getB()+radius*math.sin(math.radians(direction)))
                spawn=True
                for key2 in Entities:
                    j=Entities[key2]
                    if(PointInRect(Point(pos.getA(),pos.getB()-6),Foods[j].getDim())):
                        kelp_r=random.uniform(0,100)
                        if(kelp_r>=25):
                            spawn=False
                if(spawn):
                    newfood=CreateFood(pos,0,size,size*i.getMaxEN()*0.1,i)
                    Entities[newfood.UUID]=newfood
                    Foods.append(newfood.UUID)
                    i.setEnergy(i.getEnergy()*(1-0.25*(1+(size-0.1))))
            elif(i.getId()=="Fruit" and i.getEnergy()<=i.getMaxEN()*0.1 and r<=(i.getMaxSZ()*4.0/Globals.fps)*Globals.timescale):
                size=random.uniform(0.05,0.15)
                radius=random.uniform(0,32)*i.getSize()
                direction=random.uniform(0,360)
                pos=Point(i.getPos().getA()+radius*math.cos(math.radians(direction)),i.getPos().getB()+radius*math.sin(math.radians(direction)))
                newfood=CreateFood(pos,0,size,i.getEnergy()+40*size,i.getSeed())
                Entities[newfood.UUID]=newfood
                Foods.append(newfood.UUID)
                i.setHealth(0)
            elif(i.getId()=="Mushroom"):
                pass
            elif(i.getId()=="Meat"):
                pass
            elif(i.getId()=="Bone"):
                pass
            elif(i.getId()=="Bug"):
                pass
            elif(i.getId()=="Fish"):
                pass
            elif(i.getId()=="Egg"):
                pass





#Food Reproduction
#   Grass: Random chance to spawn another Grass within range of itself [Cost=50%, Requirement=90%-100%, Size=~0.5]
#   Bush: Random chance to spawn another Bush within range of itself [Cost=60%, Requirement=90%-100%, Size=~0.2]
#   Tree: Random chance to spawn Fruit within range of itself [Cost=10%, Requirement=97.5%-100%, Size=~1]
#   Kelp: Random chance to spawn another Kelp within range of itself [Cost=25%, Requirement=75%-100%, Size=~0.1]
#
#   Fruit: Random chance to spawn Tree withing range of itself [Cost=100%, Requirement=0%-10%, Size=~0.1]
#
#   Mushrooms: Random chance to spawn Mushrooms in large range of itself [Cost=40%, Requirement=55%-100%, Size=~0.1]
#
#   Meat: Random chance to spawn Bugs and Mushrooms in small range of itself [Cost=10%, Requirement=0%-100%, Size=~0.25]
#   Bone: Nothing
#
#   Bug: Random chance to spawn multiple Bugs in small range of itself [Cost=25%, Requirement=90%-100%, Size=~0.1]
#   Fish: Random chance to spawn multiple Fish in small range of itself [Cost=45%, Requirement=80%-100%, Size=~0.25]
#
#   Egg: Spawn Creature when hatch timer finishes
#
#   Creature: Spawn as much Meat/Bones in range of death location to equal energy left+max energy/3






#Genes
#   Sight: View Distance, FOV, Light Sensitivity, Color (R,G,B)
#   Physical: Size, Density, Color, Water/Land Movement, Lung Capacity, Water Retention, Metabolism, Damage, Poison Resistance, Speed, Sleep Amount
#   Reproduction: Reproduction Age, Reproduction Energy, Offspring Average, Offspring Energy, Growth Speed, Growth Energy, Waterproof Eggs
#   Pheromone: "Color" Sensing, Sense Radius, Pheromone Production

#Inputs
#   Base: Per Object in View:[Distance to Object, Object Size, Object Type], Health, Energy Level, Thirst, Oxygen, Fullness, Water Level, Speed, Age, Exhaustion, In Water, Pheromone Amount, Light, Angle, Delay1, Delay2, Delay3
#   Color Vision:  Per Object in View:[Object R,G,B channels], Self R,G,B channels
#   Pheromone "Color": Pheromone R,G,B channel sensing

#Outputs
#   Base: Increase/Decrease Forward/Backward Speed, Rotate Left/Right, Grab, Throw, Sleep, Bite, Drink, Pheromone R,G,B Production, Reproduce, Delay1, Delay2, Delay3






#Initialize Pygame
pygame.init()

#Create Screen
screen=pygame.display.set_mode((s_width,s_height))
pygame.display.set_caption("Synth_Evo 2.2.1")
dayscreen = pygame.Surface((s_width,s_height))
dayscreen.set_alpha(0)
dayscreen.fill(c_night)
screen.blit(dayscreen,(0,0))




Terrain=[]
Entities=dict()
Foods=[]
Creatures=[]

Base_Terrain=[]
Base_Creatures=[]





test_terrain=[]
for j in range(3,6):
    for i in range(5,10):
        test_terrain.append(Tile(pos=Point(tile_size*i,tile_size*j),shape=[Point(tile_offset,tile_offset),Point(-tile_offset,tile_offset),Point(-tile_offset,-tile_offset),Point(tile_offset,-tile_offset)],color=c_water,obj_id="Water",tile=1))
test_terrain.append(Tile(pos=Point(tile_size*7,tile_size*2),shape=[Point(tile_offset,tile_offset),Point(-tile_offset,tile_offset),Point(-tile_offset,-tile_offset),Point(tile_offset,-tile_offset)],color=c_water,obj_id="Water",tile=1))
test_terrain.append(Tile(pos=Point(tile_size*8,tile_size*2),shape=[Point(tile_offset,tile_offset),Point(-tile_offset,tile_offset),Point(-tile_offset,-tile_offset),Point(tile_offset,-tile_offset)],color=c_water,obj_id="Water",tile=1))
test_terrain.append(Tile(pos=Point(tile_size*4,tile_size*4),shape=[Point(tile_offset,tile_offset),Point(-tile_offset,tile_offset),Point(-tile_offset,-tile_offset),Point(tile_offset,-tile_offset)],color=c_water,obj_id="Water",tile=1))
test_terrain.append(Tile(pos=Point(tile_size*10,tile_size*5),shape=[Point(tile_offset,tile_offset),Point(-tile_offset,tile_offset),Point(-tile_offset,-tile_offset),Point(tile_offset,-tile_offset)],color=c_water,obj_id="Water",tile=1))
test_terrain.append(Tile(pos=Point(tile_size*9,tile_size*6),shape=[Point(tile_offset,tile_offset),Point(-tile_offset,tile_offset),Point(-tile_offset,-tile_offset),Point(tile_offset,-tile_offset)],color=c_water,obj_id="Water",tile=1))
test_terrain.append(Tile(pos=Point(tile_size*8,tile_size*6),shape=[Point(tile_offset,tile_offset),Point(-tile_offset,tile_offset),Point(-tile_offset,-tile_offset),Point(tile_offset,-tile_offset)],color=c_water,obj_id="Water",tile=1))
test_terrain.append(Tile(pos=Point(tile_size*10,tile_size*6),shape=[Point(tile_offset,tile_offset),Point(-tile_offset,tile_offset),Point(-tile_offset,-tile_offset),Point(tile_offset,-tile_offset)],color=c_water,obj_id="Water",tile=1))

MergeTiles()

try:
    while running:
        clock.tick(Globals.fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.display.quit()
                pygame.quit()
                exit()

            if(event.type==pygame.MOUSEBUTTONUP):
                if(event.button==1):
                    #Left Click
                    newfood = CreateBaseFood(Point(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]),0,1,Globals.devtest_foodspawn_type)
                    Entities[newfood.UUID] = newfood
                    Foods.append(newfood.UUID)
                if(event.button==2):
                    #Middle Click
                    pass
                if(event.button==3):
                    #Right Click
                    pass
                if(event.button==4):
                    pass
                if(event.button==5):
                    pass

            if(event.type==pygame.KEYDOWN):
                if(event.key==pygame.K_LSHIFT or event.key==pygame.K_RSHIFT):
                    Globals.devtest_timeincrease=True

            if(event.type==pygame.KEYUP):
                if(event.key==pygame.K_UP):
                    if(Globals.devtest_foodspawn_type<10):
                        Globals.devtest_foodspawn_type+=1
                        print("Food placement type is:",Globals.devtest_foodspawn_type)
                elif(event.key==pygame.K_DOWN):
                    if(Globals.devtest_foodspawn_type>0):
                        Globals.devtest_foodspawn_type-=1
                        print("Food placement type is:",Globals.devtest_foodspawn_type)
                elif(event.key==pygame.K_LEFT):
                    if(Globals.devtest_timeincrease):
                        if(Globals.timescale>9):
                            Globals.timescale-=10
                    else:
                        if(Globals.timescale>0):
                            Globals.timescale-=1
                    print("timescale is:",Globals.timescale)
                elif(event.key==pygame.K_RIGHT):
                    if(Globals.devtest_timeincrease):
                        Globals.timescale+=10
                    else:
                        Globals.timescale+=1
                    print("timescale is:",Globals.timescale)
                elif(event.key==pygame.K_r and Globals.devtest_timeincrease):
                    Globals.timescale=1
                    print("timescale was reset to: 1")
                elif(event.key==pygame.K_t):
                    Globals.devtest_mode=not Globals.devtest_mode
                elif(event.key==pygame.K_LSHIFT or event.key==pygame.K_RSHIFT):
                    Globals.devtest_timeincrease=False







        UpdateTime()

        screen.fill(c_background)

        for i in test_terrain:
            pygame.draw.rect(screen,i.getColor(),i.getDim())

        #for i in test_shapes:
            #pygame.draw.polygon(screen,i.getOutline(),i.getHitbox(),3)

        for key in Entities:
            i = Entities[key]
            if(Globals.devtest_mode):
                size_text=font0.render(str("%.2f" % round(i.getSize(),2)),False,blue)
                size_text_rect=size_text.get_rect()
                health_text=font0.render(str("%.2f" % round(i.getHealth(),2))+"/"+str("%.2f" % round(i.getMaxHP(),2)),False,red)
                health_text_rect=health_text.get_rect()
                energy_text=font0.render(str("%.2f" % round(i.getEnergy(),2))+"/"+str("%.2f" % round(i.getMaxEN(),2)),False,green)
                energy_text_rect=energy_text.get_rect()
                size_text_rect.center=(i.getDim().midtop[0],i.getDim().midtop[1]-45)
                screen.blit(size_text,size_text_rect)
                health_text_rect.center=(i.getDim().midtop[0],i.getDim().midtop[1]-27)
                screen.blit(health_text,health_text_rect)
                energy_text_rect.center=(i.getDim().midtop[0],i.getDim().midtop[1]-9)
                screen.blit(energy_text,energy_text_rect)
            pygame.draw.polygon(screen,i.getOutline(),i.getHitbox(),3)


        dayscreen.set_alpha((-2.55*Globals.light+255)*np.clip((135-Globals.timescale)/135,0.35,1))
        dayscreen.fill(c_night)
        screen.blit(dayscreen,(0,0))










        pygame.display.update()
except Exception:
    traceback.print_exc()
finally:
    pygame.quit()
    sys.exit()