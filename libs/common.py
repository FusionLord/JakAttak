import os
import random

import pygame

def lerp(a, b, p):
    return a+(b-a)*p

def lerp_lists(a,b,p):
    new_list=[]
    index=0
    while True:
        info = lerp(a[index], b[index], p)
        new_list.append(info)
        index+=1
        if index>len(a)-1 or index>len(b)-1:
            break
    return new_list

def abs_angle(a):
    return a%360

def lerp_angles(a1,a2,p):
    A=float(abs_angle(a1))
    D=float(abs_angle(a2))
    if A==D:
        return a1
    dests=[D-360,D,D+360]
    closest=0,360
    for dest in dests:
        direction=abs(dest-A)/(dest-A)
        distance= dest-A
        if abs(distance)<abs(closest[1]):
            closest=float(direction), float(distance)

    return abs_angle(a1 + closest[1]*p)

def HSVtoRGB(H,S,V):
    H = float(H%360)
    S = float(min(max(S,0),100))
    V = float(min(max(V,0),100))

    if(H<60):
        Color = lerp_lists((255,0,0),(255,255,0),(H-0)/60)
    elif(H<120):
        Color = lerp_lists((255,255,0),(0,255,0),(H-60)/60)
    elif(H<180):
        Color = lerp_lists((0,255,0),(0,255,255),(H-120)/60)
    elif(H<240):
        Color = lerp_lists((0,255,255),(0,0,255),(H-180)/60)
    elif(H<300):
        Color = lerp_lists((0,0,255),(255,0,255),(H-240)/60)
    elif(H<360):
        Color = lerp_lists((255,0,255),(255,0,0),(H-300)/60)

    Color = lerp_lists([Color[0]*V/100.0,Color[1]*V/100.0,Color[2]*V/100.0],[255*V/100.0]*3,1-(S/100.0))

    Color = [int(Color[0]),int(Color[1]),int(Color[2])]

    return Color

def randomChooseFile(folder):
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.sys.path.insert(0,parentdir)

    files = os.listdir(folder)
    choice = random.choice(files)
    return choice

############################

class SuperRect(object):
    def __init__(self, rect):
        if type(rect)==list or type(rect)==tuple:
            if len(rect)!=4:
                raise "Error. Expected list of length 4. Recieved list of length:", len(rect)
            self.left = rect[0]
            self.top = rect[1]
            self.right = rect[0]+rect[2]
            self.bottom = rect[1]+rect[3]

            self.top_left = (self.left, self.top)
            self.top_right = (self.right, self.top)
            self.bottom_left = (self.left, self.bottom)
            self.bottom_right = (self.right, self.bottom)

            self.center = ((self.left+self.right)/2.0,(self.top+self.bottom)/2.0)

            self.width = self.right-self.left
            self.height = self.bottom-self.top

            self.size = (self.width, self.height)

    def __mul__(self, other):
        return SuperRect((self.left*other, self.top*other, self.width*other, self.height*other))

    def get_rect(self):
        return pygame.Rect((self.left, self.top, self.width, self.height))

    def colliderect(self, rect):
        Rleft=self.left-rect.right
        Rtop=self.top-rect.bottom
        Rright=rect.left-self.right
        Rbottom=rect.top-self.bottom

        m = max(Rleft, Rtop, Rright, Rbottom)
        if m<0:
            return True
        else:
            return False

    def contains(self, rect):
        Rleft=self.left-rect.left
        Rtop=self.top-rect.top
        Rright=rect.right-self.right
        Rbottom=rect.bottom-self.bottom

        m = max(Rleft, Rtop, Rright, Rbottom)
        if m<0:
            return True
        else:
            return False

    def collidepoint(self, point):
        return point[0]>self.left and point[0]<self.right and point[1]>self.top and point[1]<self.bottom

    def quad_split(self):
        w = self.width / 2.0
        h = self.height / 2.0
        rl = []
        rl.append(SuperRect((float(self.left), float(self.top), float(w), float(h))))
        rl.append(SuperRect((float(self.left + w), float(self.top), float(w), float(h))))
        rl.append(SuperRect((float(self.left), float(self.top + h), float(w), float(h))))
        rl.append(SuperRect((float(self.left + w), float(self.top + h), float(w), float(h))))

        return rl

