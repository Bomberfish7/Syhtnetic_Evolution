#-------------------------------------------------------------------------------
# Name:        Synthetic Evolution 2.2.5
# Purpose:
#
# Author:      The Throngler & co.
#
# Created:     05/12/2023
#-------------------------------------------------------------------------------

import pygame
import pygame_gui as gui
import math
import numpy as np
import random
import traceback
import sys
import json
from perlin_noise import PerlinNoise
import matplotlib.pyplot as plt
from types import SimpleNamespace

from Globals import *
from Statics import *
from Food_Types import *




#TO DO:
#   Make Method to scale foods natural color to Poison or Medicinal color based on poison value (Purple(-) -> Base Color(0) -> Blue(+))




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


    if Globals.cam_move_up:
        camera.setB(camera.getB()+50/ups)
    if Globals.cam_move_down:
        camera.setB(camera.getB()-50/ups)
    if Globals.cam_move_left:
        camera.setA(camera.getA()+50/ups)
    if Globals.cam_move_right:
        camera.setA(camera.getA()-50/ups)
    if Globals.cam_drag:
        mouse_rel=pygame.mouse.get_rel()
        camera.setPoint([camera.getA()+mouse_rel[0]/zoom.getA(),camera.getB()+mouse_rel[1]/zoom.getB()])

    TileUpdate()
    FoodUpdate()
    CollisionHandler()
    ClearRemoves()

def CreateBaseFood(pos,angle,size,food_type):
    #Creates a food object given parameters
    global Base_Foods

    food_type=np.clip(food_type,0,len(Base_Foods))
    if(food_type<=1 or food_type==3):
        #Grass, Bushes, and Kelp
        new_food=Plant()
    elif(food_type==2):
        #Trees
        new_food=Plant(nbr_mul=3)
    elif(food_type==4):
        #Fruits
        new_food=Fruit(seed=CreateBaseFood(Point(0,0),0,1,2))
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
    #new_food.toggleLabel()
##    new_food.setLabel()
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

def TileUpdate():
    #Updates all terrain tiles
    global test_terrain
    global Entities
    global Terrain

    for i in Terrain:
        Entities[i].UpdateDimensions()

    for i in test_terrain:
        i.UpdateDimensions()

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
        if type(Entities[i]) in [Plant,PlantCluster,Mushroom,MushroomCluster,PreyFood]:
            Entities[i].RegenHealth()
            Entities[i].Grow()
            if type(Entities[i]) in [Mushroom,MushroomCluster]:
                Entities[i].getAura().UpdateDimensions()
        if type(Entities[i]) is PreyFood:
            FoodMove(i)
            if Entities[i].getMemoryLen()>0:
                if random.uniform(0,100)<=(0.1/ups)*Globals.timescale:
                    Entities[i].removeMemory()

        Entities[i].RegenEnergy()
        Entities[i].HurtOnLowEnergy()
        Entities[i].UpdateHitbox()
        if Globals.devtest_mode and i in Display_Info:
            Entities[i].generateLabel()
            Entities[i].setLabelVis(1)
        if Entities[i].getHealth()<=0:
            Entities[i]._remove=True

def PointInRect(point,rect):
    #Finds if a point is inside a bounding box
    return rect.collidepoint(point.getPoint())

def PointInCircle(point,circle):
    #Checks to see if a point is inside a circle

    d=math.sqrt(math.pow(point.getA()-circle.getPos().getA(),2)+math.pow(point.getB()-circle.getPos().getB(),2))
    if d<circle.getRadius():
        return True
    return False

def PointInPolygon(point,poly):
    #Finds if a point is inside a polygon
    pass
#^^  Unfinished  ^^

def CollisionHandler():
    #Handles collision between all objects
    global Foods
    global Entities

    for i in Foods:
        Entities[i].setNbr(0.0)

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
            i_A=(type(Entities[i]) is Aura)
            a_A=(type(Entities[a]) is Aura)
            if((not i_A and a_A) or (i_A and not a_A)):
                SAPCollide(a,i)
            elif(not i_A and not a_A):
                if PolyPolyCollison(Entities[a].getHitbox(),Entities[i].getHitbox()):
                    SAPCollide(a,i)

def SAPCollide(a,b):
    #Runs what happens when 2 objects collide
    global Entities

    if (Entities.get(a,False)==False or Entities.get(b,False)==False) or (Entities[a]._remove==True or Entities[b]._remove==True):
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
    if (Entities[a]._remove==False and Entities[b]._remove==False):
        if (type(Entities[a]) in [Plant,PlantCluster] and type(Entities[b]) in [Plant,PlantCluster]):
            Entities[a].setNbr(Entities[a].getNbr()+Entities[b].getMaxEN()/(1350/Entities[b].getNbrMul()))
            Entities[b].setNbr(Entities[b].getNbr()+Entities[a].getMaxEN()/(1350/Entities[a].getNbrMul()))
        elif(type(Entities[a]) in [Plant,PlantCluster] and type(Entities[b]) in [Mushroom,MushroomCluster]):
            Entities[a].setNbr(Entities[a].getNbr()-Entities[b].getMaxEN()/(1350/Entities[b].getNbrMul()))
        elif(type(Entities[a]) in [Mushroom,MushroomCluster] and type(Entities[b]) in [Plant,PlantCluster]):
            Entities[b].setNbr(Entities[b].getNbr()-Entities[a].getMaxEN()/(1350/Entities[a].getNbrMul()))
        elif(type(Entities[a]) in [Mushroom,MushroomCluster] and type(Entities[b]) in [Food,FoodCluster,Fruit]):
            Entities[a].setNbr(Entities[a].getNbr()-Entities[b].getMaxEN()/(1350/Entities[b].getNbrMul()))
            Entities[b].setNbr(Entities[b].getNbr()+Entities[a].getMaxEN()/(1350/Entities[a].getNbrMul()))
        elif(type(Entities[a]) in [Food,FoodCluster,Fruit] and type(Entities[b]) in [Mushroom,MushroomCluster]):
            Entities[a].setNbr(Entities[a].getNbr()+Entities[b].getMaxEN()/(1350/Entities[a].getNbrMul()))
            Entities[b].setNbr(Entities[b].getNbr()-Entities[a].getMaxEN()/(1350/Entities[a].getNbrMul()))
        elif(type(Entities[a]) in [PreyFood] and type(Entities[b]) in [Food,FoodCluster,Fruit,Plant,PlantCluster,Mushroom,MushroomCluster]):
            if Entities[b].getAquatic()-0.5<=Entities[a].getAquatic()<=Entities[b].getAquatic()+0.5:
                Entities[a].addMemory(Point(Entities[b].getPos().getA(),Entities[b].getPos().getB()))
                if Entities[a].getEatT()<=0:
                    r=random.uniform(0.15,0.25)
                    r=Entities[a].getMaxEN()*r*(Entities[b].getDigest()/5)
                    if Entities[a].getEnergy()+r>=Entities[a].getMaxEN():
                        r=Entities[a].getMaxEN()-Entities[a].getEnergy()
                    if Entities[b].getEnergy()-r<=0:
                        r=Entities[b].getEnergy()
                    Entities[a].setEnergy(Entities[a].getEnergy()+r)
                    Entities[a].setEatT(1.5)
                    Entities[a].setMoveT(Entities[a].getMoveT()*0.25)
                    Entities[b].setEnergy(Entities[b].getEnergy()-r)
        elif(type(Entities[a]) in [Food,FoodCluster,Fruit,Plant,PlantCluster,Mushroom,MushroomCluster] and type(Entities[b]) in [PreyFood]):
            if Entities[a].getAquatic()-0.5<=Entities[b].getAquatic()<=Entities[a].getAquatic()+0.5:
                Entities[b].addMemory(Point(Entities[a].getPos().getA(),Entities[a].getPos().getB()))
                if Entities[b].getEatT()<=0:
                    r=random.uniform(0.15,0.25)
                    r=Entities[b].getMaxEN()*r*(Entities[a].getDigest()/5)
                    if Entities[b].getEnergy()+r>=Entities[b].getMaxEN():
                        r=Entities[b].getMaxEN()-Entities[b].getEnergy()
                    if Entities[a].getEnergy()-r<=0:
                        r=Entities[a].getEnergy()
                    Entities[b].setEnergy(Entities[b].getEnergy()+r)
                    Entities[b].setEatT(1.5)
                    Entities[b].setMoveT(Entities[b].getMoveT()*0.25)
                    Entities[a].setEnergy(Entities[a].getEnergy()-r)

        elif(type(Entities[a]) in [Plant,PlantCluster] and Entities[a].getAquatic()<0.75 and type(Entities[b]) is Aura):
            Entities[a].setNbr(Entities[a].getNbr()-Entities[Entities[b].getParent()].getMaxEN()/(1350/Entities[Entities[b].getParent()].getNbrMul()))
        elif(type(Entities[a]) is Aura and type(Entities[b]) in [Plant,PlantCluster] and Entities[b].getAquatic()<0.75):
            Entities[b].setNbr(Entities[b].getNbr()-Entities[Entities[a].getParent()].getMaxEN()/(1350/Entities[Entities[a].getParent()].getNbrMul()))
        elif(type(Entities[a]) in [Food,FoodCluster,Fruit] and Entities[a].getAquatic()<0.75 and type(Entities[b]) is Aura):
            Entities[a].setNbr(Entities[a].getNbr()+Entities[Entities[b].getParent()].getMaxEN()/(1350/(Entities[Entities[b].getParent()].getNbrMul()*2)))
            Entities[Entities[b].getParent()].setNbr(Entities[Entities[b].getParent()].getNbr()-Entities[a].getMaxEN()/(1350/(Entities[a].getNbrMul()*2)))
        elif(type(Entities[a]) is Aura and type(Entities[b]) in [Food,FoodCluster,Fruit] and Entities[b].getAquatic()<0.75):
            Entities[Entities[a].getParent()].setNbr(Entities[Entities[a].getParent()].getNbr()-Entities[b].getMaxEN()/(1350/(Entities[b].getNbrMul()*2)))
            Entities[b].setNbr(Entities[b].getNbr()+Entities[Entities[a].getParent()].getMaxEN()/(1350/(Entities[Entities[a].getParent()].getNbrMul()*2)))
        elif(type(Entities[a]) in [PreyFood] and Entities[a].getAquatic()<0.75 and type(Entities[b]) is Aura and Entities[b].getStrength()>0):
            Entities[a].setHealth(Entities[a].getHealth()-(Entities[b].getStrength()/fps*Globals.timescale))
        elif(type(Entities[a]) is Aura and Entities[a].getStrength()>0 and type(Entities[b]) in [PreyFood] and Entities[b].getAquatic()<0.75):
            Entities[b].setHealth(Entities[b].getHealth()-(Entities[a].getStrength()/fps*Globals.timescale))

def ClearRemoves():
    #Deletes objects from list tagged with _remove
    global Foods
    global Auras
    global Creatures
    global Entities
    global Terrain

    for key in Foods:
        if key in Entities:
            if Entities[key]._remove==True:
                if type(Entities[key]) in [Mushroom,MushroomCluster]:
                    Auras.remove(Entities[key].getAura().UUID)
                    del Entities[Entities[key].getAura().UUID]
                Entities[key].getLabel().kill()
                Foods.remove(key)
                del Entities[key]

    for key in Auras:
        if key in Entities:
            if Entities[key]._remove==True:
                Auras.remove(key)
                del Entities[key]

    for key in Creatures:
        if key in Entities:
            if Entities[key]._remove==True:
                Entities[key].getLabel().kill()
                Creatures.remove(key)
                del Entities[key]

    for key in Terrain:
        if key in Entities:
            if Entities[key]._remove==True:
                Entities[key].getLabel().kill()
                Terrain.remove(key)
                del Entities[key]
                if(len(Terrain)==0):
                    MapGenerator()
                    break

def MergeClusters(a,b):
    #Merges like foods into clusters
    global Entities

    if(Entities[a].getId()==Entities[b].getId() and type(Entities[b]) in [Food,Plant,Mushroom]):
        if not type(Entities[a]) in [FoodCluster,PlantCluster,MushroomCluster]:
            if type(Entities[a]) is Food:
                c=FoodCluster()
                c.setClusterFood(Entities[a])
                c.setShape(shapes[Entities[a].getId()][1])
                Entities[a].getLabel().kill()
                Entities[a]=c
            if type(Entities[a]) is Plant:
                c=PlantCluster()
                c.setClusterFood(Entities[a])
                c.setShape(shapes[Entities[a].getId()][1])
                Entities[a].getLabel().kill()
                Entities[a]=c
            if type(Entities[a]) is Mushroom:
                c=MushroomCluster()
                c.setClusterFood(Entities[a],Entities[a].getAura())
                c.setShape(shapes[Entities[a].getId()][1])
                Entities[a].getLabel().kill()
                Entities[a]=c
        if(Entities[a].getMaxSZ()<4):
            Entities[a].Merge(Entities[b])
            Entities[b]._remove=True
            if type(Entities[a]) is MushroomCluster:
                Entities[Entities[a].getAura().UUID].UpdateDimensions()
                Entities[Entities[b].getAura().UUID]._remove=True
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
            if(i.getId()=="Grass" and i.getEnergy()>=i.getMaxEN()*0.9 and r<=(i.getMaxSZ()*0.1/ups)*Globals.timescale):
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
            elif(i.getId()=="Bush" and i.getEnergy()>=i.getMaxEN()*0.9 and r<=(i.getMaxSZ()*0.05/ups)*Globals.timescale):
                size=random.uniform(0.15,0.25)
                radius=random.uniform(32,80)*i.getSize()
                direction=random.uniform(0,360)
                pos=Point(i.getPos().getA()+radius*math.cos(math.radians(direction)),i.getPos().getB()+radius*math.sin(math.radians(direction)))

                newfood=CreateFood(pos,0,size,size*i.getMaxEN()*0.1,i)
                Entities[newfood.UUID]=newfood
                Foods.append(newfood.UUID)
                i.setEnergy(i.getEnergy()*(1-0.6*(1+(size-0.2))))
            elif(i.getId()=="Tree" and i.getEnergy()>=i.getMaxEN()*0.975 and r<=(i.getMaxSZ()*0.15/ups)*Globals.timescale):
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
                    i.setEnergy(i.getEnergy()-(i.getEnergy()/i.getMaxSZ())*(0+0.1*(1+(size-1.0))))
            elif(i.getId()=="Kelp" and i.getEnergy()>=i.getMaxEN()*0.75 and r<=(i.getMaxSZ()*0.15/ups)*Globals.timescale):
                size=random.uniform(0.05,0.15)
                radius=random.uniform(16,32)*i.getSize()
                direction=random.uniform(0,360)
                pos=Point(i.getPos().getA()+radius*math.cos(math.radians(direction)),i.getPos().getB()+radius*math.sin(math.radians(direction)))
                spawn=True
                for key2 in Entities:
                    j=Entities[key2]
                    if(PointInRect(Point(pos.getA(),pos.getB()-6),j.getDim())):
                        kelp_r=random.uniform(0,100)
                        if(kelp_r>=25):
                            spawn=False
                if(spawn):
                    newfood=CreateFood(pos,0,size,size*i.getMaxEN()*0.1,i)
                    Entities[newfood.UUID]=newfood
                    Foods.append(newfood.UUID)
                    i.setEnergy(i.getEnergy()*(1-0.25*(1+(size-0.1))))
            elif(i.getId()=="Fruit" and i.getEnergy()<=i.getMaxEN()*0.1 and r<=(i.getMaxSZ()*4.0/ups)*Globals.timescale):
                size=random.uniform(0.05,0.15)
                radius=random.uniform(0,32)*i.getSize()
                direction=random.uniform(0,360)
                pos=Point(i.getPos().getA()+radius*math.cos(math.radians(direction)),i.getPos().getB()+radius*math.sin(math.radians(direction)))
                newfood=CreateFood(pos,0,size,i.getEnergy()+40*size,i.getSeed())
                Entities[newfood.UUID]=newfood
                Foods.append(newfood.UUID)
                i.setHealth(0)
            elif(i.getId()=="Mushroom" and i.getEnergy()>=i.getMaxEN()*0.55 and r<=(i.getMaxSZ()*0.2/ups)*Globals.timescale):
                size=random.uniform(0.1,0.2)
                radius=random.uniform(16,100)*i.getSize()
                direction=random.uniform(0,360)
                pos=Point(i.getPos().getA()+radius*math.cos(math.radians(direction)),i.getPos().getB()+radius*math.sin(math.radians(direction)))

                newfood=CreateFood(pos,0,size,size*i.getMaxEN()*0.1,i)
                Entities[newfood.UUID]=newfood
                Entities[newfood.UUID].GenerateAura()
                Entities[newfood.getAura().UUID]=newfood.getAura()
                Entities[newfood.UUID].setAura(Entities[newfood.getAura().UUID])
                Foods.append(newfood.UUID)
                Auras.append(newfood.getAura().UUID)
                i.setEnergy(i.getEnergy()*(1-0.40*(1+(size-0.1))))
            elif(i.getId()=="Meat" and i.getEnergy()<=i.getMaxEN()*0.1 and r<=(i.getMaxSZ()*4.0/ups)*Globals.timescale):
                f=random.randrange(1,round(6*(math.pow(i.getSize(),0.75))))
                for j in range(f):
                    size=random.uniform(0.25,0.4)
                    f2=random.randrange(0,2)
                    radius=random.uniform(0,48)*(math.pow(3*i.getSize(),(1/3)))
                    direction=random.uniform(0,360)
                    pos=Point(i.getPos().getA()+radius*math.cos(math.radians(direction)),i.getPos().getB()+radius*math.sin(math.radians(direction)))
                    if f2==0:
                        newfood=CreateFood(pos,0,size,size*i.getMaxEN()*0.85,Base_Foods[8])
                        Entities[newfood.UUID]=newfood
                        Foods.append(newfood.UUID)
                    else:
                        newfood=CreateFood(pos,0,size,size*i.getMaxEN()*0.1,Base_Foods[5])
                        Entities[newfood.UUID]=newfood
                        Entities[newfood.UUID].GenerateAura()
                        Entities[newfood.getAura().UUID]=newfood.getAura()
                        Entities[newfood.UUID].setAura(Entities[newfood.getAura().UUID])
                        Foods.append(newfood.UUID)
                        Auras.append(newfood.getAura().UUID)
                i.setHealth(0)
            elif(i.getId()=="Bone"):
                pass
            elif(i.getId()=="Bug" and i.getEnergy()>=i.getMaxEN()*0.35 and r<=(i.getMaxSZ()*0.2/ups)*Globals.timescale):
                f=random.randrange(2,round(7*(math.pow(i.getSize(),0.75))))
                for j in range(f):
                    size=random.uniform(0.2,0.3)
                    pos=Point(i.getPos().getA(),i.getPos().getB())

                    newfood=CreateFood(pos,0,size,size*i.getMaxEN()*0.85,i)
                    Entities[newfood.UUID]=newfood
                    Foods.append(newfood.UUID)
                i.setEnergy(i.getEnergy()*(1-0.25*(1+(size-0.1))))
            elif(i.getId()=="Fish" and i.getEnergy()>=i.getMaxEN()*0.8 and r<=(i.getMaxSZ()*0.1/ups)*Globals.timescale):
                f=random.randrange(1,round(4*(math.pow(i.getSize(),0.75))))
                for j in range(f):
                    size=random.uniform(0.2,0.3)
                    pos=Point(i.getPos().getA(),i.getPos().getB())

                    newfood=CreateFood(pos,0,size,size*i.getMaxEN()*0.35,i)
                    Entities[newfood.UUID]=newfood
                    Foods.append(newfood.UUID)
                i.setEnergy(i.getEnergy()*(1-0.45*(1+(size-0.25))))
            elif(i.getId()=="Egg"):
                pass

def FoodMove(key):
    #Moves prey foods through the world

    global Entities
    global test_terrain

    target=None

    if Entities[key].getMoveT()<=0:
        if Entities[key].getMemoryLen()>0 and random.uniform(0,100)<=70:
            target=Entities[key].getRandMemory()
            target.setPoint([target.getA()+random.uniform(-7,7),target.getB()+random.uniform(-7,7)])
        else:
            target=Point(Entities[key].getPos().getA()+random.uniform(-64,64),Entities[key].getPos().getB()+random.uniform(-64,64))
        if Entities[key].getAquatic()==1:
            t=False
            for i in test_terrain:
                if PointInRect(target,i.getDim()):
                    t=True
            if not t:
                target=Point(Entities[key].getPos().getA(),Entities[key].getPos().getB())
        Entities[key].setTarget(target)
        Entities[key].setMoveT(random.uniform(5,15))




    Entities[key].Move()

def MakeTile(gridX,gridY,color=c_water,obj_id="water",tile=1):
    newTile=Tile(pos=Point(tile_size*gridX,tile_size*gridY),shape=[Point(tile_offset,tile_offset),Point(-tile_offset,tile_offset),Point(-tile_offset,-tile_offset),Point(tile_offset,-tile_offset)],color=color,obj_id=obj_id,tile=tile)
    return newTile

def GenerateChunk(chunkX, chunkY, noise_values):
    global Entities
    global Terrain
    tile_data=[SimpleNamespace(color=c_land,obj_id="land"),SimpleNamespace(color=c_water,obj_id="water")]
    chunk_tile_types=[[1 if noise_values[chunkX*chunk_size+x][chunkY*chunk_size+y]<-0.125 else 0 for y in range(chunk_size)] for x in range(chunk_size)]
    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in chunk_tile_types]))
    for x in range(chunk_size):
        for y in range(chunk_size):
            noise_X = chunkX*chunk_size+x
            noise_Y = chunkY*chunk_size+y
            tile_type=1 if(noise_values[noise_X][noise_Y]<-0.125) else 0
            newTile=MakeTile(noise_X-tile_boundary/2,noise_Y-tile_boundary/2,tile_data[tile_type].color,tile_data[tile_type].obj_id,tile_type)
            Entities[newTile.UUID]=newTile
            Terrain.append(newTile.UUID)
            Entities[newTile.UUID].UpdateHitbox()

def MapGenerator():
    global Entities
    global Terrain
    global maps_generated
    Terrain_Noise=PerlinNoise(octaves=3)
    noise_values=[[Terrain_Noise([x/tile_boundary,y/tile_boundary]) for y in range(tile_boundary)] for x in range(tile_boundary)]
    if(Globals.devtest_mode or maps_generated==0):
        plt.imshow(noise_values, cmap='gray')
        plt.show()
##    tile_data=[SimpleNamespace(color=c_land,obj_id="land"),SimpleNamespace(color=c_water,obj_id="water")]

    for i in range(chunk_limit):
        for j in range(chunk_limit):
            GenerateChunk(i,j,noise_values)
##    for x in range(tile_boundary[0]):
##        for y in range(tile_boundary[1]):
##            tile_type=1 if(noise_values[x][y]<-0.125) else 0
##            newTile=MakeTile(x-tile_boundary[0]/2,y-tile_boundary[1]/2,tile_data[tile_type].color,tile_data[tile_type].obj_id,tile_type)
##            Entities[newTile.UUID]=newTile
##            Terrain.append(newTile.UUID)
##            Entities[newTile.UUID].UpdateHitbox()
    maps_generated+=1
##            if((x-tile_boundary[0]/2) % 1 != 0 or (y-tile_boundary[1]/2) % 1 != 0):
##                print(str(x-tile_boundary[0]/2)+" ",str(y-tile_boundary[1]/2))
##    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in noise_values]))


def SaveData():

    saveFile = open("savedata.json",mode='w+',encoding='utf-8')
    entities = json.dump(Entities,saveFile)



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
pygame.display.set_caption("Synth_Evo 2.2.5")
dayscreen = pygame.Surface((s_width,s_height))
dayscreen.set_alpha(0)
dayscreen.fill(c_night)
screen.blit(dayscreen,(0,0))

Terrain_Noise=PerlinNoise(octaves=1)


Terrain=[]
Entities=dict()
Foods=[]
Auras=[]
Creatures=[]
Display_Info=[]

Base_Terrain=[]
Base_Creatures=[]

MapGenerator()

timescale_label=gui.elements.ui_label.UILabel(pygame.rect.Rect(0,15,200,25),"Timescale: "+str(Globals.timescale),visible=0)
food_type_label=gui.elements.ui_label.UILabel(pygame.rect.Rect(0,30,200,25),"Food: ",visible=0)
UPS_label=gui.elements.ui_label.UILabel(pygame.rect.Rect(0,0,100,25),"UPS: "+str("%.2f" % round(time_delta,2)),visible=0)

time_label=gui.elements.ui_label.UILabel(pygame.rect.Rect(0,50,200,25),"Simulation Time: "+str("%.2f" % round(Globals.time,2)),visible=0)

sim_clock_frac=(Globals.time%Globals.day_length)*24
sim_hour=int(sim_clock_frac)
sim_minute=int((sim_clock_frac-sim_hour)*60)
clock_label=gui.elements.ui_label.UILabel(pygame.rect.Rect(0,65,150,25),"Sim Clock: "+str("%02d" % sim_hour)+":"+str("%02d" % sim_minute),visible=0)
light_label=gui.elements.ui_label.UILabel(pygame.rect.Rect(150,65,200,25),"Light: "+str("%.2f" % round(Globals.light,2)),visible=0)


test_terrain=[]
for j in range(3,6):
    for i in range(5,10):
        test_terrain.append(Tile(pos=Point(tile_size*i,tile_size*j),shape=[Point(tile_offset,tile_offset),Point(-tile_offset,tile_offset),Point(-tile_offset,-tile_offset),Point(tile_offset,-tile_offset)],color=c_testwater,obj_id="Water",tile=1))
test_terrain.append(Tile(pos=Point(tile_size*7,tile_size*2),shape=[Point(tile_offset,tile_offset),Point(-tile_offset,tile_offset),Point(-tile_offset,-tile_offset),Point(tile_offset,-tile_offset)],color=c_testwater,obj_id="Water",tile=1))
test_terrain.append(Tile(pos=Point(tile_size*8,tile_size*2),shape=[Point(tile_offset,tile_offset),Point(-tile_offset,tile_offset),Point(-tile_offset,-tile_offset),Point(tile_offset,-tile_offset)],color=c_testwater,obj_id="Water",tile=1))
test_terrain.append(Tile(pos=Point(tile_size*4,tile_size*4),shape=[Point(tile_offset,tile_offset),Point(-tile_offset,tile_offset),Point(-tile_offset,-tile_offset),Point(tile_offset,-tile_offset)],color=c_testwater,obj_id="Water",tile=1))
test_terrain.append(Tile(pos=Point(tile_size*10,tile_size*5),shape=[Point(tile_offset,tile_offset),Point(-tile_offset,tile_offset),Point(-tile_offset,-tile_offset),Point(tile_offset,-tile_offset)],color=c_testwater,obj_id="Water",tile=1))
test_terrain.append(Tile(pos=Point(tile_size*9,tile_size*6),shape=[Point(tile_offset,tile_offset),Point(-tile_offset,tile_offset),Point(-tile_offset,-tile_offset),Point(tile_offset,-tile_offset)],color=c_testwater,obj_id="Water",tile=1))
test_terrain.append(Tile(pos=Point(tile_size*8,tile_size*6),shape=[Point(tile_offset,tile_offset),Point(-tile_offset,tile_offset),Point(-tile_offset,-tile_offset),Point(tile_offset,-tile_offset)],color=c_testwater,obj_id="Water",tile=1))
test_terrain.append(Tile(pos=Point(tile_size*10,tile_size*6),shape=[Point(tile_offset,tile_offset),Point(-tile_offset,tile_offset),Point(-tile_offset,-tile_offset),Point(tile_offset,-tile_offset)],color=c_testwater,obj_id="Water",tile=1))

test_terrain.append(MakeTile(0,0,color=c_testwater))

MergeTiles()

try:
    while running:
        time_delta=clock.tick(Globals.fps)/1000.0
        vis_UPS[vis_UPS_counter]=time_delta
        vis_UPS_counter=(vis_UPS_counter+1)%UPS_samples
        if Globals.devtest_mode:

            ups=1.0/(sum(vis_UPS)/UPS_samples)
            UPS_label.set_text("UPS: "+str("%.2f" % round(ups,2)))
            UPS_label.visible=1

            timescale_label.set_text("Timescale: "+str(Globals.timescale))
            timescale_label.visible=1

            food_multi_text=""
            if(Globals.devtest_spawnMany):
                food_multi_text=" x5"
            food_type_label.set_text("Food: "+Globals.Base_Foods[Globals.devtest_foodspawn_type].getId()+food_multi_text)
            food_type_label.visible=1

            time_format = "%.2f" if Globals.time/ups < 10000 else "%.2e"
            time_label.set_text("Simulation Time: "+str(time_format % round(Globals.time/ups,2)))
            time_label.visible=1

            sim_clock_frac=(Globals.time%Globals.day_length)/Globals.day_length*24
            sim_hour=(int(sim_clock_frac)-10)%24
            sim_minute=int((sim_clock_frac % 1)*60)
            clock_label.set_text("Sim Clock: "+str("%02d" % sim_hour)+":"+str("%02d" % sim_minute))
            clock_label.visible=1

            light_label.set_text("Light: "+str(Globals.light))
            light_label.visible=1
        else:

            UPS_label.visible=0
            timescale_label.visible=0
            food_type_label.visible=0
            time_label.visible=0
            clock_label.visible=0
            light_label.visible=0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.display.quit()
                pygame.quit()
                sys.exit()
                exit()
            manager.process_events(event)

            if(event.type==pygame.MOUSEBUTTONDOWN):
                if(event.button==1):
                    #Left Click
                    pass
                if(event.button==2):
                    #Middle Click
                    Globals.cam_drag=True
                    pygame.mouse.get_rel()
                if(event.button==3):
                    #Right Click
                    pass
                if(event.button==4):
                    pass
                if(event.button==5):
                    pass

            if(event.type==pygame.MOUSEBUTTONUP):
                if(event.button==1):
                    #Left Click
                    numSpawn=1
                    xRand=0
                    yRand=0
                    radRand=50
                    if(Globals.devtest_spawnMany):
                        numSpawn=5
                        if(Globals.devtest_foodspawn_type==2):
                            radRand=100
                    for i in range(numSpawn):
                        if(numSpawn>1):
                            # random angle
                            alpha = 2 * math.pi * random.random()
                            # random radius
                            r = radRand * math.sqrt(random.uniform(0.1,1))
                            # calculating coordinates
                            xRand = r * math.cos(alpha)
                            yRand = r * math.sin(alpha)
                        newfood=CreateBaseFood(Point(((pygame.mouse.get_pos()[0]+xRand)-s_width/2)/zoom.getA()-camera.getA(),((pygame.mouse.get_pos()[1]+yRand)-s_height/2)/zoom.getB()-camera.getB()),0,1,Globals.devtest_foodspawn_type)
                        nf_UUID=newfood.UUID
                        Entities[nf_UUID]=newfood
                        Foods.append(nf_UUID)
                        if Globals.devtest_mode:
                            Entities[nf_UUID].setLabelVis(1)
                        if(Globals.devtest_foodspawn_type==5):
                            Entities[nf_UUID].GenerateAura()
                            Entities[newfood.getAura().UUID]=newfood.getAura()
                            Entities[nf_UUID].setAura(Entities[newfood.getAura().UUID])
                            Auras.append(newfood.getAura().UUID)
                if(event.button==2):
                    #Middle Click
                    Globals.cam_drag=False
                if(event.button==3):
                    #Right Click
                    if Globals.key_shift:
                        for key in Entities:
                            if not key in Auras and PointInRect(Point(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]),Entities[key].getVisDim()):
                                if key in Display_Info:
                                    Entities[key].setLabelVis(0)
                                    Display_Info.remove(key)
                                else:
                                    Display_Info.append(key)

                if(event.button==4):
                    pass
                if(event.button==5):
                    pass

            if(event.type==pygame.MOUSEWHEEL):
                zoom.setPoint([np.clip(event.y/5+zoom.getA(),0.4,10),np.clip(event.y/5+zoom.getB(),0.4,10)])

            if(event.type==pygame.KEYDOWN):
                if(event.key==pygame.K_LSHIFT or event.key==pygame.K_RSHIFT):
                    Globals.key_shift=True
                if(event.key==pygame.K_LCTRL or event.key==pygame.K_RCTRL):
                    Globals.key_ctrl=True
                if(event.key==pygame.K_LALT or event.key==pygame.K_RALT):
                    Globals.key_alt=True

                if(event.key==pygame.K_w):
                    Globals.cam_move_up=True
                if(event.key==pygame.K_s):
                    Globals.cam_move_down=True
                if(event.key==pygame.K_a):
                    Globals.cam_move_left=True
                if(event.key==pygame.K_d):
                    Globals.cam_move_right=True

            if(event.type==pygame.KEYUP):
                if(event.key==pygame.K_UP):
                    Globals.devtest_foodspawn_type=(Globals.devtest_foodspawn_type+1)%11
                elif(event.key==pygame.K_DOWN):
                    Globals.devtest_foodspawn_type=(Globals.devtest_foodspawn_type-1)%11
                elif(event.key==pygame.K_LEFT):
                    if(Globals.key_shift):
                        if(Globals.timescale>9):
                            Globals.timescale-=10
                    else:
                        if(Globals.timescale>0):
                            Globals.timescale-=1
                elif(event.key==pygame.K_RIGHT):
                    if(Globals.key_shift):
                        Globals.timescale+=10
                    else:
                        Globals.timescale+=1
                elif(event.key==pygame.K_r and Globals.key_shift):
                    Globals.timescale=1
                elif(event.key==pygame.K_t):
                    Globals.devtest_mode=not Globals.devtest_mode
                    clearKeys=list()
                    for key in Display_Info:
                        if key not in Entities:
                            clearKeys.append(key)
                            continue
                        Entities[key].setLabelVis(1 if Globals.devtest_mode else 0)
                    for i in clearKeys:
                        Display_Info.remove(i)
                elif(event.key==pygame.K_BACKSLASH):
                    Globals.devtest_spawnMany=not(Globals.devtest_spawnMany)
                elif(event.key==pygame.K_BACKQUOTE):
                    if(Globals.key_ctrl):
                        #save
                        #SaveData()
                        pass
                    elif(Globals.key_alt):
                        #load
                        pass
                elif(event.key==pygame.K_SPACE):
                    if(Globals.key_ctrl and Globals.key_shift and Globals.key_alt):
                        if(len(Terrain)>0):
                            for i in Terrain:
                                Entities[i]._remove=True
                        else:
                            MapGenerator()


                if(event.key==pygame.K_LSHIFT or event.key==pygame.K_RSHIFT):
                    Globals.key_shift=False
                if(event.key==pygame.K_LCTRL or event.key==pygame.K_RCTRL):
                    Globals.key_ctrl=False
                if(event.key==pygame.K_LALT or event.key==pygame.K_RALT):
                    Globals.key_alt=False

                if(event.key==pygame.K_w):
                    Globals.cam_move_up=False
                if(event.key==pygame.K_s):
                    Globals.cam_move_down=False
                if(event.key==pygame.K_a):
                    Globals.cam_move_left=False
                if(event.key==pygame.K_d):
                    Globals.cam_move_right=False

        manager.update(time_delta)





        UpdateTime()

        screen.fill(c_background)

        for i in Terrain:
            pygame.draw.rect(screen,Entities[i].getColor(),Entities[i].getVisDim(),border_radius=0)

##        for i in test_terrain:
##            pygame.draw.rect(screen,i.getColor(),i.getVisDim())

        #for i in test_shapes:
            #pygame.draw.polygon(screen,i.getOutline(),i.getHitbox(),3)

        for key in Entities:
            i = Entities[key]
            if Globals.devtest_mode:
                if key in Display_Info:

                    pass

                elif(key in Auras):
                    pygame.draw.rect(screen,green,i.getVisDim(),1)
            if(key not in Auras and key not in Terrain):
                pygame.draw.polygon(screen,i.getOutline(),i.getVisuals(),3)


        dayscreen.set_alpha((-2.55*Globals.light+255)*np.clip((135-Globals.timescale)/135,0.35,1))
        dayscreen.fill(c_night)
        screen.blit(dayscreen,(0,0))
        manager.draw_ui(screen)








        pygame.display.update()
except Exception:
    traceback.print_exc()
finally:
    pygame.quit()
    sys.exit()