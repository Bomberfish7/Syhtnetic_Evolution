#-------------------------------------------------------------------------------
# Name:        Food Types
# Purpose:
#
# Author:      The Throngler & co.
#
# Created:     10/23/2023
#-------------------------------------------------------------------------------

import pygame
import math
import numpy as np
import Globals
from Statics import *


#Food Types
#   Plants: Grass, Bush, Tree, Fruit, --Poisonous Plant--, Kelp
#   Meats: Animal, Bugs, Bone, Egg, Fish
#   Fungi: Mushroom, --Poisonous Mushroom--

class Food(Object):
    #Anything edible by creatures
    def __init__(self,pos=Point(),delta=Point(),angle=0,shape=[Point(),Point(),Point()],size=1,color=None,outline=None,mass=10,friction=1,obj_id="Undefined",health=None,energy=None,max_health=10,max_energy=10,digestion_speed=1,immortal=False,energy_regen=1.0,age=0,poison=0,aquatic=0,max_size=1):
        if color is None:
            color=outline
        super().__init__(pos,delta,angle,shape,size,color,outline,mass,friction,obj_id,health,energy,max_health,max_energy,immortal)
        self.energy_regen=energy_regen
        self.age=age
        self.poison=poison
        self.aquatic=aquatic
        self.max_size = max_size
    def __str__(self):
        return f'Food:\"{self.obj_id}\"\t [Health:{self.health}, Energy:{self.energy}, Regen:{self.energy_regen}, Age:{self.age}, Poison:{self.poison}, Aquatic:{self.aquatic}, UUID:{self.UUID}]'
    def getObjStr(self):
        return super().__str__()

    def getRegen(self):
        return self.energy_regen*self.size
    def getAge(self):
        return self.age
    def getPoison(self):
        return self.poison
    def getAquatic(self):
        return self.aquatic
    def getFoodCopy(self):
        return[self.getObjectCopy(),self.energy_regen,self.age,self.poison,self.aquatic,self.max_size]
    def getMaxSZ(self):
        return self.max_size
    def getSeed(self):
        return self.seed

    def setRegen(self,energy_regen):
        self.energy_regen=energy_regen
    def setAge(self,age):
        self.age=age
    def setPoison(self,poison):
        self.poison=poison
    def setAquatic(self,aquatic):
        self.aquatic=aquatic
    def setFoodCopy(self,copy,copyId=False):
        self.setObjectCopy(copy[0],copyId)
        self.energy_regen=copy[1]
        self.age=copy[2]
        self.poison=copy[3]
        self.aquatic=copy[4]
        self.max_size=copy[5]
    def setMaxSZ(self,max_size):
        print('Max Size should not be changed on non-clusters')
        self.max_size = max_size
    def setSeed(self, seed):
        self.seed = seed


    def RegenEnergy(self):
        if(self.energy<=self.max_energy*self.size and self.energy >=0):
            self.energy+=(self.energy_regen*self.size/Globals.fps)*Globals.timescale
            if(self.energy<=0):
                self.energy=0
        if(self.energy>self.max_energy*self.size):
            self.energy=self.max_energy*self.size
    def HurtOnLowEnergy(self):
        if(self.energy<=self.max_energy*self.size/10):
            if(self.energy==0):
                self.health-=(self.max_health*self.size/20)/Globals.fps*Globals.timescale
            else:
                self.health-=(np.clip((self.energy/self.max_energy*self.size)-0.1,0.-1,0.0)/-0.02)/Globals.fps*Globals.timescale
    def Drown(self):
        self.health-=(self.max_health*self.size/40)/Globals.fps*Globals.timescale

class Plant(Food):
    #Food source that uses Globals.light to gain energy
    def __init__(self,pos=Point(),delta=Point(),angle=0,shape=[Point(),Point(),Point()],size=1,color=None,outline=None,mass=10,friction=1,obj_id="Undefined",health=None,energy=None,max_health=10,max_energy=10,digestion_speed=1,immortal=False,energy_regen=1,age=0,poison=0,aquatic=0,max_size=1,neighbor=0):
        super().__init__(pos,delta,angle,shape,size,color,outline,mass,friction,obj_id,health,energy,max_health,max_energy,digestion_speed,immortal,energy_regen,age,poison,aquatic,max_size)
        self.neighbor=neighbor
    def __str__(self):
        return f'Plant:\"{self.obj_id}\"\t [Health:{self.health}, Energy:{self.energy}, Regen:{self.energy_regen}, Age:{self.age}, Poison:{self.poison}, Aquatic:{self.aquatic}, UUID:{self.UUID}]'

    def getNbr(self):
        return self.neighbor
    def getRegen(self):
        return self.energy_regen*self.size-self.neighbor

    def setNbr(self,neighbor):
        self.neighbor=neighbor

    def Grow(self):
        if((self.energy_regen*self.size-self.neighbor)>0):
            if(self.energy>=self.max_energy*self.size*0.75 and self.size<1.5):
                if(self.health<self.max_health*self.size):
                    self.size+=(0.05*((self.energy_regen*self.size-self.neighbor)*0.25*(Globals.light*0.0125)))/Globals.fps*Globals.timescale
                else:
                    self.size+=(0.05*((self.energy_regen*self.size-self.neighbor)*0.5*(Globals.light*0.0125)))/Globals.fps*Globals.timescale
                self.energy-=((self.energy_regen*self.size-self.neighbor)*0.5*(Globals.light*0.0125))/Globals.fps*Globals.timescale
    def RegenEnergy(self):
        if(self.energy<=self.max_energy*self.size):
            self.energy+=((self.energy_regen*self.size-self.neighbor)/Globals.fps)*Globals.timescale*(Globals.light*0.0125)
        if(self.energy>self.max_energy*self.size):
            self.energy=self.max_energy*self.size
    def RegenHealth(self):
        if(self.energy>=self.max_energy*self.size/2 and self.health<self.max_health*self.size):
            self.health+=((self.energy_regen*self.size-self.neighbor)*0.75*(Globals.light*0.0125))/Globals.fps*Globals.timescale
            self.energy-=abs((self.energy_regen*self.size-self.neighbor)*0.75*(Globals.light*0.0125))/Globals.fps*Globals.timescale
        if(self.health>self.max_health*self.size):
            self.energy+=self.health-self.max_health*self.size
            if(self.energy>self.max_energy*self.size):
                self.energy=self.max_energy*self.size
            self.health=self.max_health*self.size

class Fruit(Food):
    def __init__(self,pos=Point(),delta=Point(),angle=0,shape=[Point(),Point(),Point()],size=1,color=None,outline=None,mass=10,friction=1,obj_id="Undefined",health=None,energy=None,max_health=10,max_energy=10,digestion_speed=1,immortal=False,energy_regen=1,age=0,poison=0,aquatic=0,max_size=1,seed=Plant()):
        super().__init__(pos,delta,angle,shape,size,color,outline,mass,friction,obj_id,health,energy,max_health,max_energy,digestion_speed,immortal,energy_regen,age,poison,aquatic,max_size)
        self.seed=seed
    def __str__(self):
        return f'Fruit:\"{self.obj_id}\"\t [Health:{self.health}, Energy:{self.energy}, Regen:{self.energy_regen}, Age:{self.age}, Poison:{self.poison}, Aquatic:{self.aquatic}, UUID:{self.UUID}]'

    def getSeed(self):
        return self.seed
    def getFruitCopy(self):
        return[self.getFoodCopy(),self.seed]

    def setSeed(self,seed):
        self.seed=seed
    def setFruitCopy(self,copy):
        self.setFoodCopy(copy[0])
        self.seed=copy[1]

class Mushroom(Food):
    #Food source that consumes meat and boosts plants
    def __init__(self,pos=Point(),delta=Point(),angle=0,shape=[Point(),Point(),Point()],size=1,color=None,outline=None,mass=10,friction=1,obj_id="Undefined",health=None,energy=None,max_health=10,max_energy=10,digestion_speed=1,immortal=False,energy_regen=1,age=0,poison=0,aquatic=0,max_size=1):
        super().__init__(pos,delta,angle,shape,size,color,outline,mass,friction,obj_id,health,energy,max_health,max_energy,digestion_speed,immortal,energy_regen,age,poison,aquatic,max_size)

    def __str__(self):
        return f'Mushroom:\"{self.obj_id}\"\t [Health:{self.health}, Energy:{self.energy}, Regen:{self.energy_regen}, Age:{self.age}, Poison:{self.poison}, Aquatic:{self.aquatic}, UUID:{self.UUID}]'

    #def RegenEnergy(self):
        #pass
    def RegenHealth(self):
        if(self.energy>=self.max_energy*self.size/2 and self.health<self.max_health*self.size):
            self.health+=(self.energy_regen*self.size*0.75*(Globals.light*0.0125))/Globals.fps*Globals.timescale
            self.energy-=(self.energy_regen*self.size*0.75*(Globals.light*0.0125))/Globals.fps*Globals.timescale
        if(self.health>self.max_health*self.size):
            self.energy+=self.health-self.max_health*self.size
            if(self.energy>self.max_energy*self.size):
                self.energy=self.max_energy*self.size
            self.health=self.max_health*self.size

class PreyFood(Food):
    #Food source that can move and has limited AI
    def __init__(self,pos=Point(),delta=Point(),angle=0,shape=[Point(),Point(),Point()],size=1,color=None,outline=None,mass=10,friction=1,obj_id="Undefined",health=None,energy=None,max_health=10,max_energy=10,digestion_speed=1,immortal=False,energy_regen=1,age=0,poison=0,aquatic=0,max_size=1):
        super().__init__(pos,delta,angle,shape,size,color,outline,mass,friction,obj_id,health,energy,max_health,max_energy,digestion_speed,immortal,energy_regen,age,poison,aquatic,max_size)
    def __str__(self):
        return f'PreyFood:\"{self.obj_id}\"\t [Health:{self.health}, Energy:{self.energy}, Regen:{self.energy_regen}, Age:{self.age}, Poison:{self.poison}, Aquatic:{self.aquatic}, UUID:{self.UUID}]'

    def Move(self):
        return None

class Egg(Food):
    #Food that holds Creature data
    def __init__(self,pos=Point(),delta=Point(),angle=0,shape=[Point(),Point(),Point()],size=1,color=None,outline=None,mass=10,friction=1,obj_id="Undefined",health=None,energy=None,max_health=10,max_energy=10,digestion_speed=1,immortal=False,energy_regen=1,age=0,poison=0,aquatic=0,max_size=1):
        super().__init__(pos,delta,angle,shape,size,color,outline,mass,friction,obj_id,health,energy,max_health,max_energy,digestion_speed,immortal,energy_regen,age,poison,aquatic,max_size)
    def __str__(self):
        return f'Egg:\"{self.obj_id}\"\t [Health:{self.health}, Energy:{self.energy}, Regen:{self.energy_regen}, Age:{self.age}, Poison:{self.poison}, Aquatic:{self.aquatic}, UUID:{self.UUID}]'

    #def RegenEnergy(self):
        #pass



class FoodCluster(Food):
    def __init__(self,pos=Point(),delta=Point(),angle=0,shape=[Point(),Point(),Point()],size=1,color=None,outline=None,mass=10,friction=1,obj_id="Undefined",health=None,energy=None,max_health=10,max_energy=10,digestion_speed=1,immortal=False,energy_regen=1,age=0,poison=0,aquatic=0,max_size=1):
        super().__init__(pos,delta,angle,shape,size,color,outline,mass,friction,obj_id,health,energy,max_health,max_energy,digestion_speed,immortal,energy_regen,age,poison,aquatic)
        self.max_size=max_size

    def getMaxSZ(self):
        return self.max_size
    def getClusterCopy(self):
        return [self.getFoodCopy(),self.max_size]

    def setMaxSZ(self,max_size):
        self.max_size=max_size
    def setClusterCopy(self,copy):
        self.setFoodCopy(copy[0])
        self.max_size=copy[1]
        self.setSeed(self.getFoodCopy())
    def setClusterFood(self,food):
        self.setFoodCopy(food.getFoodCopy(),copyId=True)
        self.max_size=1

    def Merge(self,food):
        self.max_size+=1
        self.pos=Point((self.pos.getA()+food.getPos().getA())*(1-self.getSize()/(self.getSize()+food.getSize())),(self.pos.getB()+food.getPos().getB())*(1-self.getSize()/(self.getSize()+food.getSize())))
        self.size+=food.getSize()
        self.max_energy+=food.getMaxEN()
        self.max_health+=food.getMaxHP()
        self.energy+=food.getEnergy()
        self.health+=food.getHealth()
        self.outline=((self.outline[0]+food.getOutline()[0])/2,(self.outline[1]+food.getOutline()[1])/2,(self.outline[2]+food.getOutline()[2])/2)

class PlantCluster(Plant):
    def __init__(self,pos=Point(),delta=Point(),angle=0,shape=[Point(),Point(),Point()],size=1,color=None,outline=None,mass=10,friction=1,obj_id="Undefined",health=None,energy=None,max_health=10,max_energy=10,digestion_speed=1,immortal=False,energy_regen=1,age=0,poison=0,aquatic=0,neighbor=0,max_size=1):
        super().__init__(pos,delta,angle,shape,size,color,outline,mass,friction,obj_id,health,energy,max_health,max_energy,digestion_speed,immortal,energy_regen,age,poison,aquatic,neighbor)
        self.max_size=max_size

    def getMaxSZ(self):
        return self.max_size
    def getClusterCopy(self):
        return [self.getFoodCopy(),self.max_size]

    def setMaxSZ(self,max_size):
        self.max_size=max_size
    def setClusterCopy(self,copy):
        self.setFoodCopy(copy[0])
        self.max_size=copy[1]
        self.setSeed(self.getFoodCopy())
    def setClusterFood(self,food):
        self.setFoodCopy(food.getFoodCopy(),copyId=True)
        self.max_size=1

    def Merge(self,food):
        self.max_size+=1
        self.pos=Point((self.pos.getA()+food.getPos().getA())*(1-self.getSize()/(self.getSize()+food.getSize())),(self.pos.getB()+food.getPos().getB())*(1-self.getSize()/(self.getSize()+food.getSize())))
        self.size+=food.getSize()
        self.max_energy+=food.getMaxEN()
        self.max_health+=food.getMaxHP()
        self.energy+=food.getEnergy()
        self.health+=food.getHealth()
        self.outline=((self.outline[0]+food.getOutline()[0])/2,(self.outline[1]+food.getOutline()[1])/2,(self.outline[2]+food.getOutline()[2])/2)
    def Grow(self):
        if((self.energy_regen*self.size-self.neighbor)>0):
            if(self.energy>=self.max_energy*self.size*0.75 and self.size<self.max_size*1.5):
                if(self.health<self.max_health*self.size):
                    self.size+=(0.05*((self.energy_regen*self.size-self.neighbor)*0.25*(Globals.light*0.0125)))/Globals.fps*Globals.timescale
                else:
                    self.size+=(0.05*((self.energy_regen*self.size-self.neighbor)*0.5*(Globals.light*0.0125)))/Globals.fps*Globals.timescale
                self.energy-=((self.energy_regen*self.size-self.neighbor)*0.5*(Globals.light*0.0125))/Globals.fps*Globals.timescale

class MushroomCluster(Mushroom):
    def __init__(self,pos=Point(),delta=Point(),angle=0,shape=[Point(),Point(),Point()],size=1,color=None,outline=None,mass=10,friction=1,obj_id="Undefined",health=None,energy=None,max_health=10,max_energy=10,digestion_speed=1,immortal=False,energy_regen=1,age=0,poison=0,aquatic=0,max_size=1):
        super().__init__(pos,delta,angle,shape,size,color,outline,mass,friction,obj_id,health,energy,max_health,max_energy,digestion_speed,immortal,energy_regen,age,poison,aquatic)
        self.max_size=max_size

    def getMaxSZ(self):
        return self.max_size
    def getClusterCopy(self):
        return [self.getFoodCopy(),self.max_size]

    def setMaxSZ(self,max_size):
        self.max_size=max_size
    def setClusterCopy(self,copy):
        self.setFoodCopy(copy[0])
        self.max_size=copy[1]
        self.setSeed(self.getFoodCopy())
    def setClusterFood(self,food):
        self.setFoodCopy(food.getFoodCopy(),copyId=True)
        self.max_size=1

    def Merge(self,food):
        self.max_size+=1
        self.pos=Point((self.pos.getA()+food.getPos().getA())*(1-self.getSize()/(self.getSize()+food.getSize())),(self.pos.getB()+food.getPos().getB())*(1-self.getSize()/(self.getSize()+food.getSize())))
        self.size+=food.getSize()
        self.max_energy+=food.getMaxEN()
        self.max_health+=food.getMaxHP()
        self.energy+=food.getEnergy()
        self.health+=food.getHealth()
        self.outline=((self.outline[0]+food.getOutline()[0])/2,(self.outline[1]+food.getOutline()[1])/2,(self.outline[2]+food.getOutline()[2])/2)
    def Grow(self):
        if((self.energy_regen*self.size-self.neighbor)>0):
            if(self.energy>=self.max_energy*self.size*0.75 and self.size<self.max_size*1.5):
                if(self.health<self.max_health*self.size):
                    self.size+=(0.05*((self.energy_regen*self.size-self.neighbor)*0.25*(Globals.light*0.0125)))/Globals.fps*Globals.timescale
                else:
                    self.size+=(0.05*((self.energy_regen*self.size-self.neighbor)*0.5*(Globals.light*0.0125)))/Globals.fps*Globals.timescale
                self.energy-=((self.energy_regen*self.size-self.neighbor)*0.5*(Globals.light*0.0125))/Globals.fps*Globals.timescale



























