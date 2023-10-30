#-------------------------------------------------------------------------------
# Name:        Synthetic Evolution 2
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
    CheckIfDead()
    CollisionHandler()

def CreateBaseFood(pos,angle,size,food_type):
    #Creates a food object given parameters
    global Base_Foods

    food_type=np.clip(food_type,0,len(Base_Foods))
    if(food_type<=3):
        #Grass, Bushes, Trees, and Kelp
        new_food=Plant()
##        new_seed=Plant()
    elif(food_type==4):
        #Fruits
        new_food=Fruit()
##        new_seed=Fruit()
    elif(food_type==5):
        #Mushrooms
        new_food=Mushroom()
##        new_seed=Mushroom()
    elif(food_type==6 or food_type==7):
        #Meat and Bones
        new_food=Food()
##        new_seed=Food()
    elif(food_type==8 or food_type==9):
        #Bugs and Fish
        new_food=PreyFood()
##        new_seed=PreyFood()
    else:
        #Eggs
        new_food=Food()
##        new_seed=Food()
    new_food.setFoodCopy(Base_Foods[food_type].getFoodCopy())
##    new_seed.setFoodCopy(Base_Foods[food_type].getFoodCopy())
    new_food.setPos(Point(pos.getA(),pos.getB()))
    new_food.setShape(shapes[Base_Foods[food_type].getId()][0])
    new_food.setAngle(angle)
    new_food.setSize(size)
    new_food.UpdateHitbox()
    new_food.setOutline((np.clip(new_food.getColor()[0]+random.randint(-25,25),0,255),np.clip(new_food.getColor()[1]+random.randint(-25,25),0,255),np.clip(new_food.getColor()[2]+random.randint(-25,25),0,255)))
##    new_food.setSeed(new_seed)
##    print(new_seed)

    return new_food

def CreateFood(pos,angle,size,energy,food):
    #Creates a food object from another food
##    print(food)
##    print(food.getSeed())
##    print(type(food.getSeed()))
##    print(food.getSeed().getFoodCopy())
    shapeIndex = 1 if type(food) in cluster_classes else 0
    if isinstance(food,Plant):
        new_food=Plant()
##        new_seed=Plant()
    elif isinstance(food,Fruit):
        new_food=Fruit()
##        new_seed=Fruit()
    elif isinstance(food,Mushroom):
        new_food=Mushroom()
##        new_seed=Mushroom()
    elif isinstance(food,PreyFood):
        new_food=PreyFood()
##        new_seed=PreyFood()
    elif isinstance(food,Egg):
        new_food=Egg()
##        new_seed=Egg()
    else:
        new_food=Food()
##        new_seed=Food()

    new_food.setFoodCopy(food.getFoodCopy())
##    new_seed.setFoodCopy(food.getSeed().getFoodCopy())
##    new_seed.setAquatic(food.getAquatic())
##    new_seed.setPoison(food.getPoison())
    new_food.setPos(Point(pos.getA(),pos.getB()))
    new_food.setShape(shapes[food.getId()][0])
    new_food.setAngle(angle)
    new_food.setSize(size)
    new_food.UpdateHitbox()
    new_food.setEnergy(energy)
    new_food.setOutline((np.clip(new_food.getColor()[0]+random.randint(-25,25),0,255),np.clip(new_food.getColor()[1]+random.randint(-25,25),0,255),np.clip(new_food.getColor()[2]+random.randint(-25,25),0,255)))
##    new_food.setSeed(new_seed)
    print(new_food)

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
        if(i.getAquatic()==0):
            drowning=False
        elif(i.getAquatic()==1):
            drowning=True
        else:
            drowning=False
        for j in test_terrain:
            if(i.getAquatic()==0):
                if(PointInRect(i.getPos(),j.getDim())):
                    drowning=True
            elif(i.getAquatic()==1):
                if(PointInRect(i.getPos(),j.getDim())):
                    drowning=False
        if(drowning):
            i.Drown()
#^^  Unfinished  (good collisions are not done yet)^^
def CheckIfDead():
    #Checks to see if Objects have died
    global Foods

    i=len(Foods)-1
    while i>=0:
        if(Foods[i].DeathTest()):
            Foods.pop(i)
        i-=1

def FoodUpdate():
    #Updates various functions for all foods

    FoodRegen()
    FoodInWater()
    FoodReproduce()

def FoodRegen():
    #Regenerates foods health and energy
    global Foods

    for i in Foods:
        if type(i) in [Plant,PlantCluster]:
            i.RegenHealth()
            i.Grow()
        i.RegenEnergy()
        i.HurtOnLowEnergy()
        i.UpdateHitbox()

def PointInRect(point,rect):
    #Finds if a point is inside a bounding box
    return rect.collidepoint(point.getPoint())

def PointInPolygon(point,poly):
    #Finds if a point is inside a polygon
    pass
#^^  Unfinished  ^^
def MergeClusters(i,j):
    #Merges like foods into clusters
    global Foods

    if(Foods[i].getId()==Foods[j].getId() and type(Foods[j]) in [Food,Plant,Mushroom]):
        a=Foods[i]
        if not type(Foods[i]) in [FoodCluster,PlantCluster,MushroomCluster]:
            if type(Foods[i]) is Food:
                a=FoodCluster()
                a.setClusterFood(Foods[i])
##                a.setSeed(Foods[i].getSeed())
                if(Foods[i].getId()=="Meat"):
                    a.setShape(shapes[Foods[i].getId()][1])
                elif(Foods[i].getId()=="Bone"):
                    a.setShape(shapes[Foods[i].getId()][1])
##                    a.setShape(cluster_Bone)
                Foods[i]=a
            if type(Foods[i]) is Plant:
                a=PlantCluster()
                a.setClusterFood(Foods[i])
##                if(Foods[i].getId()!="Tree"):
##                    a.setSeed(Foods[i].getSeed())
                if(Foods[i].getId()=="Grass"):
                    a.setShape(shapes[Foods[i].getId()][1])
##                    a.setShape(cluster_Grass)
                elif(Foods[i].getId()=="Bush"):
                    a.setShape(shapes[Foods[i].getId()][1])
##                    a.setShape(cluster_Bush)
                elif(Foods[i].getId()=="Tree"):
                    a.setShape(shapes[Foods[i].getId()][1])
##                    a.setShape(cluster_Tree)
                elif(Foods[i].getId()=="Kelp"):
                    a.setShape(shapes[Foods[i].getId()][1])
##                    a.setShape(cluster_Kelp)
                Foods[i]=a
            if type(Foods[i]) is Mushroom:
                a=MushroomCluster()
                a.setClusterFood(Foods[i])
##                a.setSeed(Foods[i].getSeed())
                if(Foods[i].getId()=="Mushroom"):
                    a.setShape(shapes[Foods[i].getId()][1])
##                    a.setShape(cluster_Mushroom)
                Foods[i]=a
        if(Foods[i].getMaxSZ()<3):
            Foods[i].Merge(Foods[j])
            Foods.pop(j)
            print("Check")
            return True
    return False

def CollisionHandler():
    #Handles collision between all objects
    global Foods

    for i in Foods:
        if(type(i) in [Plant,PlantCluster]):
            i.setNbr(0.0)

    i=len(Foods)-1
    while i>=0:
        j=len(Foods)-1
        while j>i:
            if(pygame.Rect.colliderect(Foods[i].getDim(),Foods[j].getDim())):
                if type(Foods[i]) in [FoodCluster,PlantCluster,MushroomCluster]:
                    if(MergeClusters(i,j)):
                        j-=1
                        continue
                elif type(Foods[j]) in [FoodCluster,PlantCluster,MushroomCluster]:
                    if(MergeClusters(j,i)):
                        j-=1
                        continue
                else:
                    if(MergeClusters(i,j)):
                        j-=1
                        continue




            if(type(Foods[i]) in [Plant,PlantCluster] and type(Foods[j]) in [Plant,PlantCluster]):
                if(pygame.Rect.colliderect(Foods[i].getDim(),Foods[j].getDim())):
                    Foods[j].setNbr(Foods[j].getNbr()+Foods[i].getMaxEN()/300)
                    Foods[i].setNbr(Foods[i].getNbr()+Foods[j].getMaxEN()/300)
            j-=1
        i-=1

def FoodReproduce():
    #Creates more food from the other foods in the simulation
    global Foods

    for i in Foods:
        if(i.getSize()>=1):
            r=random.uniform(0,100)
            if(i.getId()=="Grass" and i.getEnergy()>=i.getMaxEN()*0.9 and r<=(i.getMaxSZ()*0.1/Globals.fps)*Globals.timescale):
##                print(i)
##                print(i.getSeed())
##                print(type(i.getSeed()))
##                print(i.getSeed().getFoodCopy())
                size=random.uniform(0.45,0.55)
                radius=random.uniform(16,48)*i.getSize()
                direction=random.uniform(0,360)
                pos=Point(i.getPos().getA()+radius*math.cos(math.radians(direction)),i.getPos().getB()+radius*math.sin(math.radians(direction)))
                spawn=True
                for j in Foods:
                    if(PointInRect(Point(pos.getA(),pos.getB()-6),j.getDim())):
                        grass_r=random.uniform(0,100)
                        if(grass_r>=25):
                            spawn=False
                if(spawn):
                    Foods.append(CreateFood(pos,0,size,size*i.getMaxEN()*0.2,i))
                    i.setEnergy(i.getEnergy()*(1-0.5*(1+(size-0.5))))
            if(i.getId()=="Bush" and i.getEnergy()>=i.getMaxEN()*0.9 and r<=(i.getMaxSZ()*0.05/Globals.fps)*Globals.timescale):
                size=random.uniform(0.15,0.25)
                radius=random.uniform(32,80)*i.getSize()
                direction=random.uniform(0,360)
                pos=Point(i.getPos().getA()+radius*math.cos(math.radians(direction)),i.getPos().getB()+radius*math.sin(math.radians(direction)))

                Foods.append(CreateFood(pos,0,size,size*i.getMaxEN()*0.1,i))
                i.setEnergy(i.getEnergy()*(1-0.6*(1+(size-0.2))))
            if(i.getId()=="Tree" and i.getEnergy()>=i.getMaxEN()*0.975 and r<=(i.getMaxSZ()*0.1/Globals.fps)*Globals.timescale):
                f=random.randrange(1,round(5*i.getSize()))
                for j in range(f):
                    size=random.uniform(0.90,1.10)
                    radius=random.uniform(32,80)*i.getSize()
                    direction=random.uniform(0,360)
                    pos=Point(i.getPos().getA()+radius*math.cos(math.radians(direction)),i.getPos().getB()+radius*math.sin(math.radians(direction)))

                    new_fruit=CreateFood(pos,0,size,size*i.getMaxEN()*1,Base_Foods[4])
                    new_seed=Plant()
                    new_seed.setFoodCopy(i.getFoodCopy())
                    new_fruit.setSeed(new_seed)
                    Foods.append(new_fruit)
                    i.setEnergy(i.getEnergy()*(1-0.1*(1+(size-1.0))))#FIXME fruit energy cost/starting value fuckery here up
            if(i.getId()=="Kelp" and i.getEnergy()>=i.getMaxEN()*0.75 and r<=(i.getMaxSZ()*0.15/Globals.fps)*Globals.timescale):
                size=random.uniform(0.05,0.15)
                radius=random.uniform(16,32)*i.getSize()
                direction=random.uniform(0,360)
                pos=Point(i.getPos().getA()+radius*math.cos(math.radians(direction)),i.getPos().getB()+radius*math.sin(math.radians(direction)))
                spawn=True
                for j in Foods:
                    if(PointInRect(Point(pos.getA(),pos.getB()-6),j.getDim())):
                        kelp_r=random.uniform(0,100)
                        if(kelp_r>=25):
                            spawn=False
                if(spawn):
                    Foods.append(CreateFood(pos,0,size,size*i.getMaxEN()*0.1,i))
                    i.setEnergy(i.getEnergy()*(1-0.25*(1+(size-0.1))))
            if(i.getId()=="Fruit" and i.getEnergy()<=i.getMaxEN()*0.1 and r<=(i.getMaxSZ()*2.5/Globals.fps)*Globals.timescale):
                size=random.uniform(0.05,0.15)
                radius=random.uniform(0,32)*i.getSize()
                direction=random.uniform(0,360)
                pos=Point(i.getPos().getA()+radius*math.cos(math.radians(direction)),i.getPos().getB()+radius*math.sin(math.radians(direction)))

                Foods.append(CreateFood(pos,0,size,i.getEnergy()+40*size,i.getSeed()))
                i.setHealth(0)
            if(i.getId()=="Mushroom"):
                pass
            if(i.getId()=="Meat"):
                pass
            if(i.getId()=="Bone"):
                pass
            if(i.getId()=="Bug"):
                pass
            if(i.getId()=="Fish"):
                pass
            if(i.getId()=="Egg"):
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
pygame.display.set_caption("Synth_Evo 2.0")
dayscreen = pygame.Surface((s_width,s_height))
dayscreen.set_alpha(0)
dayscreen.fill(c_night)
screen.blit(dayscreen,(0,0))




Terrain=[]
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

test_grass=Plant(pos=Point(50,s_height/2),size=2,shape=cluster_Grass,outline=c_grass,obj_id="Grass")
test_bush=Plant(pos=Point(100,s_height/2),size=2,shape=cluster_Bush,outline=c_bush,obj_id="Bush")
test_tree=Plant(pos=Point(150,s_height/2),size=2,shape=cluster_Tree,outline=c_tree,obj_id="Tree")
test_fruit=Plant(pos=Point(200,s_height/2),shape=[Point(-5,0),Point(0,5),Point(5,0),Point(0,-5)],outline=c_fruit,obj_id="Fruit")
test_kelp=Plant(pos=Point(250,s_height/2),size=2,shape=cluster_Kelp,outline=green,obj_id="Kelp")
test_poison=Plant(pos=Point(300,s_height/2),shape=[Point(-10,0),Point(0,10),Point(10,0),Point(0,-10)],outline=c_poison,obj_id="Poison")

test_mushroom=Food(pos=Point(350,s_height/2),size=2,shape=cluster_Mushroom,outline=c_mushroom,obj_id="Mushroom")
test_fungus=Food(pos=Point(400,s_height/2),shape=[Point(0,0),Point(11,-6),Point(-11,-6)],outline=c_fungus,obj_id="Fungus")

test_meat=Food(pos=Point(450,s_height/2),size=2,shape=cluster_Meat,outline=c_meat,obj_id="Meat")
test_bone=Food(pos=Point(500,s_height/2),size=2,shape=cluster_Bone,outline=white,obj_id="Bone")

test_egg=Food(pos=Point(550,s_height/2),shape=[Point(-5,1),Point(0,3),Point(5,1),Point(0,-8)],outline=c_egg,obj_id="Egg")
test_bug=PreyFood(pos=Point(600,s_height/2),shape=[Point(-5,-2),Point(-5,2),Point(5,2),Point(5,-2)],outline=c_bug,obj_id="Bug")
test_fish=PreyFood(pos=Point(650,s_height/2),shape=[Point(-8,-4),Point(-8,4),Point(8,4),Point(8,-4)],outline=black,obj_id="Fish")


test_shapes=[test_grass,test_bush,test_tree,test_fruit,test_kelp,test_poison,test_mushroom,test_fungus,test_meat,test_bone,test_egg,test_bug,test_fish]

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
                    Foods.append(CreateBaseFood(Point(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]),0,1,Globals.devtest_foodspawn_type))
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
        for i in test_terrain:
            i.UpdateHitbox()

        screen.fill(c_background)

        for i in test_terrain:
            pygame.draw.rect(screen,i.getColor(),i.getDim())
            #pygame.draw.rect(screen,red,i.getDim(),2)

        #for i in test_shapes:
            #pygame.draw.polygon(screen,i.getOutline(),i.getHitbox(),3)

        for i in Foods:
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