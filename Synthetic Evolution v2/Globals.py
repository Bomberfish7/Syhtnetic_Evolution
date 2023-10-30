#-------------------------------------------------------------------------------
# Name:        Globals
# Purpose:
#
# Author:      The Throngler & co.
#
# Created:     10/23/2023
#-------------------------------------------------------------------------------

import pygame
import math
import numpy as np
from Statics import *
from Food_Types import Food,Plant,Fruit,Mushroom,PreyFood,Egg,FoodCluster,PlantCluster,MushroomCluster
##import FoodCluster,PlantCluster,MushroomCluster


camera=Point(0,0)
zoom=1
scale=1
temperature=75
timescale=1
camera=Point(0,0)
light=100
time=0
day_length=10000
day_percent=0.5
cluster_classes=[FoodCluster,PlantCluster,MushroomCluster]

Base_Foods=[]

##Foods
#Plants
base_Grass=Plant(shape=[Point(-5,0),Point(5,0),Point(0,-18)],outline=c_grass,obj_id="Grass",max_health=45,max_energy=30,digestion_speed=5.0,energy_regen=0.25)
base_Bush=Plant(shape=[Point(-10,0),Point(0,10),Point(10,0),Point(0,-10)],outline=c_bush,obj_id="Bush",max_health=100,max_energy=100,digestion_speed=3.0,energy_regen=0.75)
base_Tree=Plant(shape=[Point(-25,0),Point(-18,18),Point(0,25),Point(18,18),Point(25,0),Point(18,-18),Point(0,-25),Point(-18,-18)],outline=c_tree,obj_id="Tree",max_health=650,max_energy=400,digestion_speed=1.5,energy_regen=1.5)
base_Kelp=Plant(shape=[Point(-5,0),Point(0,-5),Point(5,0),Point(0,-18)],outline=c_kelp,obj_id="Kelp",max_health=30,max_energy=20,digestion_speed=6.5,energy_regen=0.5,aquatic=1)
base_Fruit=Fruit(shape=[Point(-5,0),Point(0,5),Point(5,0),Point(0,-5)],outline=c_fruit,obj_id="Fruit",max_health=10,max_energy=200,digestion_speed=25.0,energy_regen=-1.95,aquatic=2,seed=base_Tree)
#Mushrooms
base_Mushroom=Mushroom(shape=[Point(0,0),Point(11,-6),Point(-11,-6)],outline=c_mushroom,obj_id="Mushroom",max_health=75,max_energy=30,digestion_speed=3.0,energy_regen=0.05)
#Meats
base_Meat=Food(shape=[Point(-7,0),Point(0,7),Point(7,0),Point(0,-7)],outline=c_meat,obj_id="Meat",max_health=20,max_energy=100,digestion_speed=40.0,energy_regen=-1.667,aquatic=2)
base_Bone=Food(shape=[Point(-3,-7),Point(-3,7),Point(3,7),Point(3,-7)],outline=c_bone,obj_id="Bone",max_health=200,max_energy=250,digestion_speed=0.5,energy_regen=-0.05,aquatic=2)
#Prey
base_Bug=PreyFood(shape=[Point(-5,-2),Point(-5,2),Point(5,2),Point(5,-2)],outline=c_bug,obj_id="Bug",max_health=2,max_energy=15,digestion_speed=25.0,energy_regen=0.0)
base_Fish=PreyFood(shape=[Point(-8,-4),Point(-8,4),Point(8,4),Point(8,-4)],outline=c_fish,obj_id="Fish",max_health=50,max_energy=125,digestion_speed=32.5,energy_regen=0.0,aquatic=1)
#Egg (Unfinished)
base_Egg=Food(shape=[Point(-5,1),Point(0,3),Point(5,1),Point(0,-8)],outline=c_egg,obj_id="Egg",max_health=3,max_energy=150,digestion_speed=50.0,energy_regen=0.0,aquatic=2)

shape_Grass = [Point(-5,0),Point(5,0),Point(0,-18)]
shape_Bush = [Point(-10,0),Point(0,10),Point(10,0),Point(0,-10)]
shape_Tree = [Point(-25,0),Point(-18,18),Point(0,25),Point(18,18),Point(25,0),Point(18,-18),Point(0,-25),Point(-18,-18)]
shape_Kelp = [Point(-5,0),Point(0,-5),Point(5,0),Point(0,-18)]
shape_Fruit = [Point(-5,0),Point(0,5),Point(5,0),Point(0,-5)]
shape_Mushroom = [Point(0,0),Point(11,-6),Point(-11,-6)]
shape_Meat = [Point(-7,0),Point(0,7),Point(7,0),Point(0,-7)]
shape_Bone = [Point(-3,-7),Point(-3,7),Point(3,7),Point(3,-7)]
shape_Bug = [Point(-5,-2),Point(-5,2),Point(5,2),Point(5,-2)]
shape_Fish = [Point(-8,-4),Point(-8,4),Point(8,4),Point(8,-4)]
shape_Egg = [Point(-5,1),Point(0,3),Point(5,1),Point(0,-8)]

##Clusters
cluster_Grass=[Point(-5,0),Point(-6,-12),Point(-4,-6),Point(-2,-18),Point(0,-8),Point(2,-18),Point(4,-6),Point(6,-12),Point(5,0)]
cluster_Bush=[Point(-10,0),Point(-4,-4),Point(0,-10),Point(4,-4),Point(10,0),Point(4,4),Point(0,10),Point(-4,4)]
cluster_Tree=[Point(-25,0),Point(-19,-11),Point(-18,-18),Point(-11,-19),Point(0,-25),Point(11,-19),Point(18,-18),Point(19,-11),Point(25,0),Point(19,11),Point(18,18),Point(11,19),Point(0,25),Point(-11,19),Point(-18,18),Point(-19,11)]
cluster_Kelp=[Point(-5,0),Point(-6,-12),Point(-4,-6),Point(-2,-18),Point(0,-8),Point(2,-18),Point(4,-6),Point(6,-12),Point(5,0),Point(3,-3),Point(0,0),Point(-3,-3)]

cluster_Mushroom=[Point(0,0),Point(-4,-3),Point(-8,0),Point(-11,-6),Point(11,-6),Point(8,0),Point(4,-3)]
cluster_Meat=[Point(-4,0),Point(-7,-6),Point(-6,-7),Point(0,-4),Point(6,-7),Point(7,-6),Point(4,0),Point(7,6),Point(6,7),Point(0,4),Point(-6,7),Point(-7,6)]
cluster_Bone=[Point(-2,-7),Point(-2,-3),Point(-5,-3),Point(-5,-1),Point(-2,-1),Point(-2,1),Point(-6,1),Point(-6,3),Point(-2,3),Point(-2,5),Point(-7,5),Point(-7,7),Point(7,7),Point(7,5),Point(2,5),Point(2,3),Point(6,3),Point(6,1),Point(2,1),Point(2,-1),Point(5,-1),Point(5,-3),Point(2,-3),Point(2,-7)]

shapes={'Grass':[shape_Grass,cluster_Grass],'Bush':[shape_Bush,cluster_Bush],'Tree':[shape_Tree,cluster_Tree],'Kelp':[shape_Kelp,cluster_Kelp],'Fruit':[shape_Fruit,shape_Fruit],'Mushroom':[shape_Mushroom,cluster_Mushroom],'Meat':[shape_Meat,cluster_Meat],'Bone':[shape_Bone,cluster_Bone],'Bug':[shape_Bug,shape_Bug],'Fish':[shape_Fish,shape_Fish],'Egg':[shape_Egg,shape_Egg]}
Base_Foods.append(base_Grass)
Base_Foods.append(base_Bush)
Base_Foods.append(base_Tree)
Base_Foods.append(base_Kelp)
Base_Foods.append(base_Fruit)
Base_Foods.append(base_Mushroom)
Base_Foods.append(base_Meat)
Base_Foods.append(base_Bone)
Base_Foods.append(base_Bug)
Base_Foods.append(base_Fish)
Base_Foods.append(base_Egg)


devtest_foodspawn_type=0
devtest_mode=False
devtest_timeincrease=False
