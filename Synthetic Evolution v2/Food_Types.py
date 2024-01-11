#-------------------------------------------------------------------------------
# Name:        Food Types
# Purpose:
#
# Author:      The Throngler & co.
#
# Created:     10/23/2023
#-------------------------------------------------------------------------------

import pygame
import pygame_gui as gui
import math
import numpy as np
import random
import Globals
from Statics import *


#Food Types
#   Plants: Grass, Bush, Tree, Fruit, --Poisonous Plant--, Kelp
#   Meats: Animal, Bugs, Bone, Egg, Fish
#   Fungi: Mushroom, --Poisonous Mushroom--

class Food(Object):
    #Anything edible by creatures
    def __init__(self,pos=Point(),delta=Point(),angle=0,shape=[Point(),Point(),Point()],size=1,color=None,outline=None,mass=10,friction=1,obj_id="Undefined",health=None,energy=None,max_health=10,max_energy=10,digestion_speed=1,immortal=False,ui_label=None,energy_regen=1.0,age=0,poison=0,aquatic=0,max_size=1,neighbor=0,nbr_mul=1.5):
        if color is None:
            color=outline
        super().__init__(pos,delta,angle,shape,size,color,outline,mass,friction,obj_id,health,energy,max_health,max_energy,immortal,ui_label)
        self.digestion_speed=digestion_speed
        self.energy_regen=energy_regen
        self.age=age
        self.poison=poison
        self.aquatic=aquatic
        self.max_size=max_size
        self.neighbor=neighbor
        self.nbr_mul=nbr_mul
    def __str__(self):
        return f'Food:\"{self.obj_id}\"\t [Health:{self.health}, Energy:{self.energy}, Regen:{self.energy_regen}, Age:{self.age}, Poison:{self.poison}, Aquatic:{self.aquatic}, UUID:{self.UUID}]'
    def getObjStr(self):
        return super().__str__()

    def getDigest(self):
        return self.digestion_speed
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
    def getNbr(self):
        return self.neighbor
    def getNbrMul(self):
        return self.nbr_mul

    def setDigest(self,digestion_speed):
        self.digestion_speed=digestion_speed
    def setRegen(self,energy_regen):
        self.energy_regen=energy_regen
    def setAge(self,age):
        self.age=age
    def setPoison(self,poison):
        self.poison=poison
    def setAquatic(self,aquatic):
        self.aquatic=aquatic
    def setFoodCopy(self,copy,copyUUID=False):
        self.setObjectCopy(copy[0],copyUUID)
        self.energy_regen=copy[1]
        self.age=copy[2]
        self.poison=copy[3]
        self.aquatic=copy[4]
        self.max_size=copy[5]
    def setMaxSZ(self,max_size):
        print('Max Size should not be changed on non-clusters')
        self.max_size = max_size
    def setNbr(self,neighbor):
        self.neighbor=neighbor
    def setNbrMul(self,nbr_mul):
        self.nbr_mul=nbr_mul


    def RegenEnergy(self):
        if(self.energy<=self.max_energy*self.size and self.energy >=0):
            self.energy+=((self.energy_regen-self.neighbor)/ups)*Globals.timescale
            if(self.energy<=0):
                self.energy=0
        if(self.energy>self.max_energy*self.size):
            self.energy=self.max_energy*self.size
    def HurtOnLowEnergy(self):
        if(self.energy<=self.max_energy*self.size/10):
            if(self.energy==0):
                self.health-=(self.max_health*self.size/20)/ups*Globals.timescale
            else:
                self.health-=(np.clip((self.energy/self.max_energy*self.size)-0.1,0.-1,0.0)/-0.02)/ups*Globals.timescale
    def Drown(self):
        self.health-=(self.max_health*self.size/40)/ups*Globals.timescale

class Plant(Food):
    #Food source that uses Globals.light to gain energy
    def __init__(self,pos=Point(),delta=Point(),angle=0,shape=[Point(),Point(),Point()],size=1,color=None,outline=None,mass=10,friction=1,obj_id="Undefined",health=None,energy=None,max_health=10,max_energy=10,digestion_speed=1,immortal=False,ui_label=None,energy_regen=1,age=0,poison=0,aquatic=0,max_size=1,neighbor=0,nbr_mul=1):
        super().__init__(pos,delta,angle,shape,size,color,outline,mass,friction,obj_id,health,energy,max_health,max_energy,digestion_speed,immortal,ui_label,energy_regen,age,poison,aquatic,max_size,neighbor,nbr_mul)
    def __str__(self):
        return f'Plant:\"{self.obj_id}\"\t [Health:{self.health}, Energy:{self.energy}, Regen:{self.energy_regen}, Age:{self.age}, Poison:{self.poison}, Aquatic:{self.aquatic}, UUID:{self.UUID}]'

    def getRegen(self):
        return self.energy_regen*self.size-self.neighbor

    def Grow(self):
        if((self.energy_regen*self.size-self.neighbor)>0):
            if(self.energy>=self.max_energy*self.size*0.75 and self.size<1.5):
                if(self.health<self.max_health*self.size):
                    self.size+=(0.05*((self.energy_regen*self.size-self.neighbor)*0.25*(Globals.light*0.0125)))/ups*Globals.timescale
                else:
                    self.size+=(0.05*((self.energy_regen*self.size-self.neighbor)*0.5*(Globals.light*0.0125)))/ups*Globals.timescale
                self.energy-=((self.energy_regen*self.size-self.neighbor)*0.5*(Globals.light*0.0125))/ups*Globals.timescale
    def RegenEnergy(self):
        if(self.energy<=self.max_energy*self.size):
            self.energy+=((self.energy_regen*self.size-self.neighbor)/ups)*Globals.timescale*(Globals.light*0.0125)
        if(self.energy>self.max_energy*self.size):
            self.energy=self.max_energy*self.size
    def RegenHealth(self):
        if(self.energy>=self.max_energy*self.size/2 and self.health<self.max_health*self.size):
            self.health+=((self.energy_regen*self.size-self.neighbor)*0.75*(Globals.light*0.0125))/ups*Globals.timescale
            self.energy-=abs((self.energy_regen*self.size-self.neighbor)*0.75*(Globals.light*0.0125))/ups*Globals.timescale
        if(self.health>self.max_health*self.size):
            self.energy+=self.health-self.max_health*self.size
            if(self.energy>self.max_energy*self.size):
                self.energy=self.max_energy*self.size
            self.health=self.max_health*self.size

class Fruit(Food):
    def __init__(self,pos=Point(),delta=Point(),angle=0,shape=[Point(),Point(),Point()],size=1,color=None,outline=None,mass=10,friction=1,obj_id="Undefined",health=None,energy=None,max_health=10,max_energy=10,digestion_speed=1,immortal=False,ui_label=None,energy_regen=1,age=0,poison=0,aquatic=0,max_size=1,neighbor=0,nbr_mul=1.75,seed=Plant()):
        super().__init__(pos,delta,angle,shape,size,color,outline,mass,friction,obj_id,health,energy,max_health,max_energy,digestion_speed,immortal,ui_label,energy_regen,age,poison,aquatic,max_size,neighbor,nbr_mul)
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
    def __init__(self,pos=Point(),delta=Point(),angle=0,shape=[Point(),Point(),Point()],size=1,color=None,outline=None,mass=10,friction=1,obj_id="Undefined",health=None,energy=None,max_health=10,max_energy=10,digestion_speed=1,immortal=False,ui_label=None,energy_regen=1,age=0,poison=0,aquatic=0,max_size=1,neighbor=0,nbr_mul=1.5):
        super().__init__(pos,delta,angle,shape,size,color,outline,mass,friction,obj_id,health,energy,max_health,max_energy,digestion_speed,immortal,ui_label,energy_regen,age,poison,aquatic,max_size,neighbor,nbr_mul)
        self.aura=Aura()
    def __str__(self):
        return f'Mushroom:\"{self.obj_id}\"\t [Health:{self.health}, Energy:{self.energy}, Regen:{self.energy_regen}, Age:{self.age}, Poison:{self.poison}, Aquatic:{self.aquatic}, UUID:{self.UUID}]'

    def getAura(self):
        return self.aura

    def setAura(self,aura):
        self.aura=aura

    def Grow(self):
        if((self.energy_regen*self.size-self.neighbor)>0):
            if(self.energy>=self.max_energy*self.size*0.75 and self.size<1.5):
                if(self.health<self.max_health*self.size):
                    self.size+=(0.05*((self.energy_regen*self.size-self.neighbor)*0.25*((120-Globals.light)*0.0125)))/ups*Globals.timescale
                else:
                    self.size+=(0.05*((self.energy_regen*self.size-self.neighbor)*0.5*((120-Globals.light)*0.0125)))/ups*Globals.timescale
                self.energy-=((self.energy_regen*self.size-self.neighbor)*0.5*((120-Globals.light)*0.0125))/ups*Globals.timescale
    def RegenEnergy(self):
        if(self.energy<=self.max_energy*self.size):
            self.energy+=((self.energy_regen*self.size-self.neighbor)/ups)*Globals.timescale*((120-Globals.light)*0.0125)
        if(self.energy>self.max_energy*self.size):
            self.energy=self.max_energy*self.size
    def RegenHealth(self):
        if(self.energy>=self.max_energy*self.size/2 and self.health<self.max_health*self.size):
            self.health+=(self.energy_regen*self.size*0.75*(120-Globals.light))/ups*Globals.timescale
            self.energy-=(self.energy_regen*self.size*0.75*(120-Globals.light))/ups*Globals.timescale
        if(self.health>self.max_health*self.size):
            self.energy+=self.health-self.max_health*self.size
            if(self.energy>self.max_energy*self.size):
                self.energy=self.max_energy*self.size
            self.health=self.max_health*self.size
    def GenerateAura(self):
        self.aura=Aura(self.pos,min(self.size,1.5),self.poison,self.UUID)

class PreyFood(Food):
    #Food source that can move and has limited AI
    def __init__(self,pos=Point(),delta=Point(),angle=0,shape=[Point(),Point(),Point()],size=1,color=None,outline=None,mass=10,friction=1,obj_id="Undefined",health=None,energy=None,max_health=10,max_energy=10,digestion_speed=1,immortal=False,ui_label=None,energy_regen=1,age=0,poison=0,aquatic=0,max_size=1,neighbor=0,nbr_mul=1):
        super().__init__(pos,delta,angle,shape,size,color,outline,mass,friction,obj_id,health,energy,max_health,max_energy,digestion_speed,immortal,ui_label,energy_regen,age,poison,aquatic,max_size,neighbor,nbr_mul)
        self.dx=0
        self.dy=0
        self.move_timer=0
        self.eat_timer=0
        self.memory=list()
        self.target=Point(0,0)
    def __str__(self):
        return f'PreyFood:\"{self.obj_id}\"\t [Health:{self.health}, Energy:{self.energy}, Regen:{self.energy_regen}, Age:{self.age}, Poison:{self.poison}, Aquatic:{self.aquatic}, UUID:{self.UUID}]'

    def getMoveT(self):
        return self.move_timer
    def getEatT(self):
        return self.eat_timer
    def getDx(self):
        return self.dx
    def getDy(self):
        return self.dy
    def getTarget(self):
        return self.target
    def getMemory(self):
        return self.memory
    def getMemoryLen(self):
        return len(self.memory)
    def getIndMemory(self,i):
        if i<0 or i>=len(self.memory):
            return None
        return self.memory[i]
    def getRandMemory(self):
        if(len(self.memory)==0):
            return None
        ran = random.randint(0,len(self.memory)-1)
        return self.memory[ran]

    def setMoveT(self,move_timer):
        self.move_timer=move_timer
    def setEatT(self,eat_timer):
        self.eat_timer=eat_timer
    def setDx(self,dx):
        self.dx=dx
    def setDy(self,dy):
        self.dy=dy
    def setTarget(self,target):
        self.target.setPoint([target.getA(),target.getB()])
    def addMemory(self,pos):
        for i in self.memory:
            if abs(i.getA()-pos.getA())<=7 and abs(i.getB()-pos.getB())<=7:
                self.memory.remove(i)
        self.memory.append(pos)
        if(len(self.memory)>10):
            del self.memory[0]
    def removeMemory(self,i=None):
        if i is None:
            i=random.randint(0,len(self.memory))
        if i>=len(self.memory):
            return
        del self.memory[i]
    def clearMemory(self):
        self.memory.clear()

    def Grow(self):
        if(self.energy>=self.max_energy*self.size*0.75 and self.size<1.5):
            if(self.health<self.max_health*self.size):
                self.size+=(0.05*((self.max_energy*0.05*self.size)*0.25))/ups*Globals.timescale
            else:
                self.size+=(0.05*((self.max_energy*0.05*self.size)*0.5))/ups*Globals.timescale
            self.energy-=((self.max_energy*0.05*self.size)*0.5)/ups*Globals.timescale
    def RegenHealth(self):
        if(self.energy>=self.max_energy*self.size/2 and self.health<self.max_health*self.size):
            self.health+=((self.max_energy*0.05*self.size)*0.75)/ups*Globals.timescale
            self.energy-=abs((self.max_energy*0.05*self.size)*0.75)/ups*Globals.timescale
        if(self.health>self.max_health*self.size):
            self.energy+=self.health-self.max_health*self.size
            if(self.energy>self.max_energy*self.size):
                self.energy=self.max_energy*self.size
            self.health=self.max_health*self.size

    def Move(self):
        tdx=self.target.getA()-self.pos.getA()
        tdy=self.target.getB()-self.pos.getB()
        magnitude=math.sqrt(tdx**2+tdy**2)
        if magnitude<=0.05:
            self.move_timer*=0.75
        if magnitude>20:
            self.dx=(tdx/magnitude)*20/ups*Globals.timescale
            self.dy=(tdy/magnitude)*20/ups*Globals.timescale
        else:
            self.dx=tdx/ups*Globals.timescale
            self.dy=tdy/ups*Globals.timescale
        self.pos.setPoint([self.pos.getA()+self.dx,self.pos.getB()+self.dy])
        self.move_timer-=1/ups*Globals.timescale
        self.eat_timer-=1/ups*Globals.timescale
        self.energy-=(0.075+(0.01*math.sqrt(self.dx**2+self.dy**2)))/ups*Globals.timescale

class Egg(Food):
    #Food that holds Creature data
    def __init__(self,pos=Point(),delta=Point(),angle=0,shape=[Point(),Point(),Point()],size=1,color=None,outline=None,mass=10,friction=1,obj_id="Undefined",health=None,energy=None,max_health=10,max_energy=10,digestion_speed=1,immortal=False,ui_label=None,energy_regen=1,age=0,poison=0,aquatic=0,max_size=1,neighbor=0,nbr_mul=0):
        super().__init__(pos,delta,angle,shape,size,color,outline,mass,friction,obj_id,health,energy,max_health,max_energy,digestion_speed,immortal,ui_label,energy_regen,age,poison,aquatic,max_size,neighbor,nbr_mul)
    def __str__(self):
        return f'Egg:\"{self.obj_id}\"\t [Health:{self.health}, Energy:{self.energy}, Regen:{self.energy_regen}, Age:{self.age}, Poison:{self.poison}, Aquatic:{self.aquatic}, UUID:{self.UUID}]'

    #def RegenEnergy(self):
        #pass



class FoodCluster(Food):
    def __init__(self,pos=Point(),delta=Point(),angle=0,shape=[Point(),Point(),Point()],size=1,color=None,outline=None,mass=10,friction=1,obj_id="Undefined",health=None,energy=None,max_health=10,max_energy=10,digestion_speed=1,immortal=False,ui_label=None,energy_regen=1,age=0,poison=0,aquatic=0,neighbor=0,nbr_mul=0,max_size=1):
        super().__init__(pos,delta,angle,shape,size,color,outline,mass,friction,obj_id,health,energy,max_health,max_energy,digestion_speed,immortal,ui_label,energy_regen,age,poison,aquatic)
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
        self.setFoodCopy(food.getFoodCopy(),copyUUID=True)
        self.max_size=1

    def Merge(self,food):
        self.max_size+=1
        self.pos=Point((food.getPos().getA()-self.pos.getA())*(1-(self.size/(self.size+food.getSize())))+self.pos.getA(),(food.getPos().getB()-self.pos.getB())*(1-(self.size/(self.size+food.getSize())))+self.pos.getB())
        self.size+=food.getSize()
        self.max_energy+=food.getMaxEN()
        self.max_health+=food.getMaxHP()
        self.energy+=food.getEnergy()
        self.health+=food.getHealth()
        self.poison=((self.max_size-1)*self.poison+food.getPoison())/self.max_size
        self.outline=((self.outline[0]+food.getOutline()[0])/2,(self.outline[1]+food.getOutline()[1])/2,(self.outline[2]+food.getOutline()[2])/2)
        food.ui_label.kill()

class PlantCluster(Plant):
    def __init__(self,pos=Point(),delta=Point(),angle=0,shape=[Point(),Point(),Point()],size=1,color=None,outline=None,mass=10,friction=1,obj_id="Undefined",health=None,energy=None,max_health=10,max_energy=10,digestion_speed=1,immortal=False,ui_label=None,energy_regen=1,age=0,poison=0,aquatic=0,neighbor=0,nbr_mul=2,max_size=1):
        super().__init__(pos,delta,angle,shape,size,color,outline,mass,friction,obj_id,health,energy,max_health,max_energy,digestion_speed,immortal,ui_label,energy_regen,age,poison,aquatic,neighbor)
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
        self.setFoodCopy(food.getFoodCopy(),copyUUID=True)
        self.max_size=1

    def Merge(self,food):
        self.max_size+=1
        self.pos=Point((food.getPos().getA()-self.pos.getA())*(1-(self.size/(self.size+food.getSize())))+self.pos.getA(),(food.getPos().getB()-self.pos.getB())*(1-(self.size/(self.size+food.getSize())))+self.pos.getB())
        self.size+=food.getSize()
        self.max_energy+=food.getMaxEN()
        self.max_health+=food.getMaxHP()
        self.energy+=food.getEnergy()
        self.health+=food.getHealth()
        self.poison=((self.max_size-1)*self.poison+food.getPoison())/self.max_size
        self.outline=((self.outline[0]+food.getOutline()[0])/2,(self.outline[1]+food.getOutline()[1])/2,(self.outline[2]+food.getOutline()[2])/2)
        food.ui_label.kill()
    def Grow(self):
        if((self.energy_regen*self.size-self.neighbor)>0):
            if(self.energy>=self.max_energy*self.size*0.75 and self.size<self.max_size*1.5):
                if(self.health<self.max_health*self.size):
                    self.size+=(0.05*((self.energy_regen*self.size-self.neighbor)*0.25*(Globals.light*0.0125)))/ups*Globals.timescale
                else:
                    self.size+=(0.05*((self.energy_regen*self.size-self.neighbor)*0.5*(Globals.light*0.0125)))/ups*Globals.timescale
                self.energy-=((self.energy_regen*self.size-self.neighbor)*0.5*(Globals.light*0.0125))/ups*Globals.timescale

class MushroomCluster(Mushroom):
    def __init__(self,pos=Point(),delta=Point(),angle=0,shape=[Point(),Point(),Point()],size=1,color=None,outline=None,mass=10,friction=1,obj_id="Undefined",health=None,energy=None,max_health=10,max_energy=10,digestion_speed=1,immortal=False,ui_label=None,energy_regen=1,age=0,poison=0,aquatic=0,neighbor=0,nbr_mul=-2,max_size=1):
        super().__init__(pos,delta,angle,shape,size,color,outline,mass,friction,obj_id,health,energy,max_health,max_energy,digestion_speed,immortal,ui_label,energy_regen,age,poison,aquatic)
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
    def setClusterFood(self,food,aura):
        self.setFoodCopy(food.getFoodCopy(),copyUUID=True)
        self.aura=aura
        self.max_size=1

    def Merge(self,food):
        self.max_size+=1
        self.nbr_mul+=food.getNbrMul()
        self.pos=Point((food.getPos().getA()-self.pos.getA())*(1-(self.size/(self.size+food.getSize())))+self.pos.getA(),(food.getPos().getB()-self.pos.getB())*(1-(self.size/(self.size+food.getSize())))+self.pos.getB())
        self.size+=food.getSize()
        self.max_energy+=food.getMaxEN()
        self.max_health+=food.getMaxHP()
        self.energy+=food.getEnergy()
        self.health+=food.getHealth()
        self.poison+=food.getPoison()
        self.outline=((self.outline[0]+food.getOutline()[0])/2,(self.outline[1]+food.getOutline()[1])/2,(self.outline[2]+food.getOutline()[2])/2)
        self.aura.setStrength(self.poison)
        self.aura.setPos(self.pos)
        self.aura.setSize(min(self.size,1.5))
        food.ui_label.kill()
    def Grow(self):
        if((self.energy_regen*self.size-self.neighbor)>0):
            if(self.energy>=self.max_energy*self.size*0.75 and self.size<self.max_size*1.5):
                if(self.health<self.max_health*self.size):
                    self.size+=(0.05*((self.energy_regen*self.size-self.neighbor)*0.25*(Globals.light*0.0125)))/ups*Globals.timescale
                else:
                    self.size+=(0.05*((self.energy_regen*self.size-self.neighbor)*0.5*(Globals.light*0.0125)))/ups*Globals.timescale
                self.energy-=((self.energy_regen*self.size-self.neighbor)*0.5*(Globals.light*0.0125))/ups*Globals.timescale



























