import math

import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

from libs.locals import*

class Hull(object):
    def __init__(self, world, start_pos, end_pos, size, disable_debug = False):
        self.world = world

        self.start_pos = start_pos
        self.end_pos = end_pos

        self.disable_debug = disable_debug

        if DEBUG_HULL_TRACE and not disable_debug:
            self.world.debug_data.append(["line",(255,255,0),start_pos,end_pos,1])

        self.size = size

        self.original_dif = ((end_pos[0] - start_pos[0]), (end_pos[1] - start_pos[1]))

        dist = math.sqrt((self.original_dif[0])**2+(self.original_dif[1])**2)
        if dist > 0:
            self.can_extend = True
            self.normalized = (self.original_dif[0]/dist, self.original_dif[1]/dist)
        else:
            self.can_extend = False

        self.impact_horiz = False
        self.impact_verti = False

        self.touch_left = False
        self.touch_right = False
        self.touch_top = False
        self.touch_bottom = False

        self.iterations = 0

    def test_can_extend(self):
        #print "-test_can_extend"
        self.iterations += 1
        if DEBUG_HULL_TRACE and not self.disable_debug:
            self.world.debug_data.append( ["rect", (0,255,0), (self.end_pos[0]-(self.size[0]/2.0),self.end_pos[1]-(self.size[1]/2.0),self.size[0],self.size[1]), 1] )
            self.world.debug_data.append( ["text", self.world.main.fonts.get_font(self.world.main.fonts.DEFAULT,8), str(self.iterations), (255,255,255), (self.end_pos[0]+0.1,self.end_pos[1]+0.1)] )

        if self.can_extend:
            left = self.end_pos[0]-(self.size[0]/2.0)
            right = self.end_pos[0]+(self.size[0]/2.0)
            top = self.end_pos[1]-(self.size[1]/2.0)
            bottom = self.end_pos[1]+(self.size[1]/2.0)

            #print (self.end_pos[0]-(self.size[0]/2.0),self.end_pos[1]-(self.size[1]/2.0),self.size[0],self.size[1])
            #print top-(WALL_THICKNESS/2.0)
            #print left-(WALL_THICKNESS/2.0)

            if (self.normalized[0]>0 and round(right+(WALL_THICKNESS/2.0),3)%1.0 == 0.0) or (self.normalized[0]<0 and round(left-(WALL_THICKNESS/2.0),3)%1.0 == 0.0):
                #checks if the vertical side could be in contact with a vertical wall
                for y in xrange(max(int(math.ceil(top-(WALL_THICKNESS/2.0)))-1,0),min(int(math.floor(bottom+(WALL_THICKNESS/2.0)))+1,self.world.grid_size[1])):
                    if self.normalized[0]>0:
                        #checks the right side
                        pos = (int(math.ceil(right)),y)
                    else:
                        #checks the left side
                        pos = (int(math.floor(left)),y)
                    if pos[0] >= 0 and pos[0]<=self.world.grid_size[0]:
                        #print "TESTING V_WALL AT", pos
                        if self.world.v_walls[pos[1]][pos[0]].is_solid:
                            self.impact_verti = True
                            break

            if (self.normalized[1]>0 and round(bottom+(WALL_THICKNESS/2.0),3)%1.0 == 0.0) or (self.normalized[1]<0 and round(top-(WALL_THICKNESS/2.0),3)%1.0 == 0.0):
                #checks if the horizontal side could be in contact with a horizontal wall
                for x in xrange(max(int(math.ceil(left-(WALL_THICKNESS/2.0)))-1,0),min(int(math.floor(right+(WALL_THICKNESS/2.0)))+1,self.world.grid_size[0])):
                    if self.normalized[1]>0:
                        #checks the bottom side
                        pos = (x,int(math.ceil(bottom)))
                    else:
                        #checks the top side
                        pos = (x,int(math.floor(top)))

                    if pos[1] >= 0 and pos[1]<=self.world.grid_size[1]:
                        #print "TESTING H_WALL AT", pos
                        if self.world.h_walls[pos[1]][pos[0]].is_solid:
                            self.impact_horiz = True
                            break

            if self.impact_horiz or self.impact_verti:
                #print " !! STOP - STOP - STOP !! "
                #print
                if DEBUG_HULL_TRACE and not self.disable_debug:
                    self.world.debug_data.append(["circle",(255,0,0),self.end_pos,0.25,1])
                self.can_extend = False

    def extend(self):
        #print "-extend"

        #print "--"+str(self.end_pos)

        offset = [0,0]

        if self.normalized[0] > 0:
            offset[0] = -((WALL_THICKNESS/2.0)+(self.size[0])/2.0)
        elif self.normalized[0] < 0:
            offset[0] = ((WALL_THICKNESS/2.0)+(self.size[0])/2.0)

        if self.normalized[1] > 0:
            offset[1] = -((WALL_THICKNESS/2.0)+(self.size[1])/2.0)
        elif self.normalized[1] < 0:
            offset[1] = ((WALL_THICKNESS/2.0)+(self.size[1])/2.0)

        if self.normalized[0]>0.0:
            dif_x = round(math.ceil(self.end_pos[0]-offset[0])-(self.end_pos[0]-offset[0]), 5)
        else:
            dif_x = round((self.end_pos[0]-offset[0])-math.floor(self.end_pos[0]-offset[0]), 5)

        if self.normalized[1]>0.0:
            dif_y = round(math.ceil(self.end_pos[1]-offset[1])-(self.end_pos[1]-offset[1]), 5)
        else:
            dif_y = round((self.end_pos[1]-offset[1])-math.floor(self.end_pos[1]-offset[1]), 5)

        if dif_x==0.0:
            dif_x=1.0
        if dif_y==0.0:
            dif_y=1.0

        if self.normalized[0]==0.0 or self.normalized[1]==0.0:
            #print "PERFECT"
            #this greatly simplifies our test, since we won't need to test both axis
            if self.normalized[0]==0.0:
                #print "Y"
                if self.normalized[1]>0:
                    #print "DOWN"
                    if dif_y==1.0:
                        self.end_pos = [self.end_pos[0], round(self.end_pos[1]+1, 5)]
                    else:
                        self.end_pos = [self.end_pos[0], round(math.ceil(self.end_pos[1])+offset[1], 5)]
                else:
                    #print "UP"
                    if dif_y==1.0:
                        self.end_pos = [self.end_pos[0], round(self.end_pos[1]-1, 5)]
                    else:
                        self.end_pos = [self.end_pos[0], round(math.floor(self.end_pos[1])+offset[1], 5)]
            elif self.normalized[1]==0.0:
                #print "X"
                if self.normalized[0]>0:
                    #print "RIGHT"
                    if dif_x==1.0:
                        self.end_pos = [round(self.end_pos[0]+1, 5), self.end_pos[1]]
                    else:
                        self.end_pos = [round(math.ceil(self.end_pos[0])+offset[0], 5), self.end_pos[1]]
                else:
                    #print "LEFT"
                    if dif_x==1.0:
                        self.end_pos = [round(self.end_pos[0]-1, 5), self.end_pos[1]]
                    else:
                        self.end_pos = [round(math.floor(self.end_pos[0])+offset[0], 5), self.end_pos[1]]
            else:
                raise "ERROR?!"
            self.test_can_extend()
            return
        else:
            #This is the most likely case, where both the x and the y axis have to be tested.
            #In this case, we have to find where on the grid the ray would immediately cross
            #over a horizontal or vertical line on the grid for both the y and the x.
            #HOWEVER, it will pick the one that is closest, UNLESS it lands on the point
            #where the ray ended. In that case, it will pick the other axis.

            if (dif_x*abs(self.normalized[1])<dif_y*abs(self.normalized[0])):
                #print 1, dif_x, dif_y
                #we are going to extend to the nearest point on the grid using the X axis
                if self.normalized[0]>0.0:
                    #print "a"
                    if dif_x==1.0:
                        x = self.end_pos[0]+1
                    else:
                        x = math.ceil(self.end_pos[0]-offset[0])+offset[0]
                    y = self.start_pos[1]+(self.normalized[1]*(x-self.start_pos[0]))/abs(self.normalized[0])
                else:
                    #print "b"
                    if dif_x==1.0:
                        x = self.end_pos[0]-1
                    else:
                        x = math.floor(self.end_pos[0]-offset[0])+offset[0]
                    y = self.start_pos[1]+(self.normalized[1]*(self.start_pos[0]-x))/abs(self.normalized[0])
            elif  (dif_x*abs(self.normalized[1])>dif_y*abs(self.normalized[0])):
                #print 2, dif_x, dif_y
                #we are going to extend to the nearest point on the grid using the Y axis
                if self.normalized[1]>0.0:
                    #print "a"
                    if dif_y==1.0:
                        y = self.end_pos[1]+1
                    else:
                        y = math.ceil(self.end_pos[1]-offset[1])+offset[1]
                    x = self.start_pos[0]+(self.normalized[0]*(y-self.start_pos[1]))/abs(self.normalized[1])
                else:
                    #print "b"
                    if dif_y==1.0:
                        y = self.end_pos[1]-1
                    else:
                        y = math.floor(self.end_pos[1]-offset[1])+offset[1]
                    x = self.start_pos[0]+(self.normalized[0]*(self.start_pos[1]-y))/abs(self.normalized[1])
            else:
                #print 3, dif_x, dif_y
                if self.normalized[0]>0:
                    if dif_x==1.0:
                        x = round(self.end_pos[0]+1, 5)
                    else:
                        x = round(math.ceil(self.end_pos[0]-offset[0])+offset[0], 5)
                else:
                    if dif_x==1.0:
                        x = round(self.end_pos[0]-1, 5)
                    else:
                        x = round(math.floor(self.end_pos[0]-offset[0])+offset[0], 5)

                if self.normalized[1]>0:
                    if dif_y==1.0:
                        y = round(self.end_pos[1]+1, 5)
                    else:
                        y = round(math.ceil(self.end_pos[1]-offset[1])+offset[1], 5)
                else:
                    if dif_y==1.0:
                        y = round(self.end_pos[1]-1, 5)
                    else:
                        y = round(math.floor(self.end_pos[1]-offset[1])+offset[1], 5)


            self.end_pos = [x,y]
            self.test_can_extend()
            return
