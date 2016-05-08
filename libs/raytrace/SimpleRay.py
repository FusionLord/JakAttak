import math

class SimpleRay(object):
    def __init__(self, start_pos, end_pos):
        self.start_pos = start_pos
        self.end_pos = end_pos

        self.original_dif = ((end_pos[0] - start_pos[0]), (end_pos[1] - start_pos[1]))

        dist = math.sqrt((self.original_dif[0])**2+(self.original_dif[1])**2)
        self.normalized = (self.original_dif[0]/dist, self.original_dif[1]/dist)

    def extend(self):
        """
        #whenever a ray extends, it is gurenteed that the longest axis will
        #increase/decrease by a value of 1. The other axis will simply increase/
        #decrease proportionally. If the ray is diaginal, both axes will increase/
        #decrease by a value of 1.
        """

        if self.normalized[0]>0.0:
            dif_x = round(math.ceil(self.end_pos[0])-self.end_pos[0], 5)
        else:
            dif_x = round(self.end_pos[0]-math.floor(self.end_pos[0]), 5)

        if self.normalized[1]>0.0:
            dif_y = round(math.ceil(self.end_pos[1])-self.end_pos[1], 5)
        else:
            dif_y = round(self.end_pos[1]-math.floor(self.end_pos[1]), 5)

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
                        self.end_pos = [self.end_pos[0], round(math.ceil(self.end_pos[1]), 5)]
                else:
                    #print "UP"
                    if dif_y==1.0:
                        self.end_pos = [self.end_pos[0], round(self.end_pos[1]-1, 5)]
                    else:
                        self.end_pos = [self.end_pos[0], round(math.floor(self.end_pos[1]), 5)]
            elif self.normalized[1]==0.0:
                #print "X"
                if self.normalized[0]>0:
                    #print "RIGHT"
                    if dif_x==1.0:
                        self.end_pos = [round(self.end_pos[0]+1, 5), self.end_pos[1]]
                    else:
                        self.end_pos = [round(math.ceil(self.end_pos[0]), 5), self.end_pos[1]]
                else:
                    #print "LEFT"
                    if dif_x==1.0:
                        self.end_pos = [round(self.end_pos[0]-1, 5), self.end_pos[1]]
                    else:
                        self.end_pos = [round(math.floor(self.end_pos[0]), 5), self.end_pos[1]]
            else:
                raise "ERROR?!"
            return
        else:
            #This is the most likely case, where both the x and the y axis have to be tested.
            #In this case, we have to find where on the grid the ray would immediately cross
            #over a horizontal or vertical line on the grid for both the y and the x.
            #HOWEVER, it will pick the one that is closest, UNLESS it lands on the point
            #where the ray ended. In that case, it will pick the other axis.

            if (dif_x*abs(self.normalized[1])<dif_y*abs(self.normalized[0])):
                #print 1
                #we are going to extend to the nearest point on the grid using the X axis
                if self.normalized[0]>0.0:
                    #print "a"
                    if dif_x==1.0:
                        x = round(self.end_pos[0]+1, 5)
                    else:
                        x = round(math.ceil(self.end_pos[0]), 5)
                    y = round(self.start_pos[1]+(self.normalized[1]*(x-self.start_pos[0]))/abs(self.normalized[0]), 5)
                else:
                    #print "b"
                    if dif_x==1.0:
                        x = round(self.end_pos[0]-1, 5)
                    else:
                        x = round(math.floor(self.end_pos[0]), 5)
                    y = round(self.start_pos[1]+(self.normalized[1]*(self.start_pos[0]-x))/abs(self.normalized[0]), 5)
            elif  (dif_x*abs(self.normalized[1])>dif_y*abs(self.normalized[0])):
                #print 2
                #we are going to extend to the nearest point on the grid using the Y axis
                if self.normalized[1]>0.0:
                    #print "a"
                    if dif_y==1.0:
                        y = round(self.end_pos[1]+1, 5)
                    else:
                        y = round(math.ceil(self.end_pos[1]), 5)
                    x = round(self.start_pos[0]+(self.normalized[0]*(y-self.start_pos[1]))/abs(self.normalized[1]), 5)
                else:
                    #print "b"
                    if dif_y==1.0:
                        y = round(self.end_pos[1]-1, 5)
                    else:
                        y = round(math.floor(self.end_pos[1]), 5)
                    x = round(self.start_pos[0]+(self.normalized[0]*(self.start_pos[1]-y))/abs(self.normalized[1]), 5)
            else:
                #print 3
                if self.normalized[0]>0:
                    if dif_x==1.0:
                        x = round(self.end_pos[0]+1, 5)
                    else:
                        x = round(math.ceil(self.end_pos[0]), 5)
                else:
                    if dif_x==1.0:
                        x = round(self.end_pos[0]-1, 5)
                    else:
                        x = round(math.floor(self.end_pos[0]), 5)
                                            
                if self.normalized[1]>0:
                    if dif_y==1.0:
                        y = round(self.end_pos[1]+1, 5)
                    else:
                        y = round(math.ceil(self.end_pos[1]), 5)
                else:
                    if dif_y==1.0:
                        y = round(self.end_pos[1]-1, 5)
                    else:
                        y = round(math.floor(self.end_pos[1]), 5)

            #repeats dif test
            if self.normalized[0]>0.0:
                dif_x = round(math.ceil(x)-x, 5)
            else:
                dif_x = round(x-math.floor(x), 5)

            if self.normalized[1]>0.0:
                dif_y = round(math.ceil(y)-y, 5)
            else:
                dif_y = round(y-math.floor(y), 5)

            if dif_x==0.0:
                dif_x=1.0
            if dif_y==0.0:
                dif_y=1.0

            if dif_x==1.0 and dif_y==1.0:
                x = float(int(x))
                y = float(int(y))

            self.end_pos = [x,y]
            return