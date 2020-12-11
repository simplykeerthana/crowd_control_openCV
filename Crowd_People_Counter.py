
'''
Name: Keerthana Madhavan
Program: I chose option 2 that is to Create a program where you imagine developing a tool for crowd control and writing codes that 
analyze a video and detect how many people are present in the scene.
Description: utilizing OpenCV, this pyhton program counts the number of people in a given video. 
'''

#importing necessary libraries
import numpy as np
import cv2 as cv
import Person
import time

try:
    log = open('num_people.txt', "w")
except:
    print('Error writing to file')
    
#entry and exiting variables for the video
cnt_up   = 0
cnt_down = 0

#Read the video from current directory
cap = cv.VideoCapture('crowd.mp4')


#printing the propertives captured from opencv to the screen
for i in range(19):
    print( i, cap.get(i))

h = 500
w = 1500
frameArea = h*w
areaTH = frameArea/250
print( 'Area Threshold', areaTH)

#Entry Lines drawing, so red and  blue. 
line_up = int(2*(h/5))
line_down   = int(3*(h/5))

up_limit =   int(1*(h/5))
down_limit = int(4*(h/5))

print( "Red line y:",str(line_down))
print( "Blue line y:", str(line_up))
line_down_color = (255,0,0)
line_up_color = (0,0,255)
pt1 =  [0, line_down];
pt2 =  [w, line_down];
pts_L1 = np.array([pt1,pt2], np.int32)
pts_L1 = pts_L1.reshape((-1,1,2))
pt3 =  [0, line_up];
pt4 =  [w, line_up];
pts_L2 = np.array([pt3,pt4], np.int32)
pts_L2 = pts_L2.reshape((-1,1,2))

pt5 =  [0, up_limit];
pt6 =  [w, up_limit];
pts_L3 = np.array([pt5,pt6], np.int32)
pts_L3 = pts_L3.reshape((-1,1,2))
pt7 =  [0, down_limit];
pt8 =  [w, down_limit];
pts_L4 = np.array([pt7,pt8], np.int32)
pts_L4 = pts_L4.reshape((-1,1,2))

#Substractor de fondo
fgbg = cv.createBackgroundSubtractorMOG2(detectShadows = True)

#Structuring the algorithms 
kernelOp = np.ones((3,3),np.uint8)
kernelOp2 = np.ones((5,5),np.uint8)
kernelCl = np.ones((11,11),np.uint8)

#Variables
font = cv.FONT_HERSHEY_SIMPLEX
persons = []
max_p_age = 5
pid = 1

while(cap.isOpened()):
    #Read image by image from the video source
    ret, frame = cap.read()

    for i in persons:
        i.num_ppl() # find every person one frame
    
    fgmask = fgbg.apply(frame)
    fgmask2 = fgbg.apply(frame)

    #Binarizing each frames to mask and get the shawdows
    try:
        ret,imBin= cv.threshold(fgmask,200,255,cv.THRESH_BINARY)
        ret,imBin2 = cv.threshold(fgmask2,200,255,cv.THRESH_BINARY)
        mask = cv.morphologyEx(imBin, cv.MORPH_OPEN, kernelOp)
        mask2 = cv.morphologyEx(imBin2, cv.MORPH_OPEN, kernelOp)
        mask =  cv.morphologyEx(mask , cv.MORPH_CLOSE, kernelCl)
        mask2 = cv.morphologyEx(mask2, cv.MORPH_CLOSE, kernelCl)
    except:
        print('end of program')
        print ('DOWN:',cnt_down)
        break

    contours0, hierarchy = cv.findContours(mask2,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
    for cnt in contours0:
        area = cv.contourArea(cnt)
        if area > areaTH:
            #tracking each person frame
            
            #conditions to caluclate multi-person frames
            
            M = cv.moments(cnt)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            x,y,w,h = cv.boundingRect(cnt)

            new = True
            if cy in range(up_limit,down_limit):
                for i in persons:
                    if abs(x-i.getX()) <= w and abs(y-i.getY()) <= h:
                        # if the object is too close to another or if it has been detected already, so to avoid double counting
                        new = False
                         #update the coordinated of the object
                        i.updateCoords(cx,cy)  
                        if i.going_UP(line_down,line_up) == True:
                            cnt_up += 1;
                            print( "person", cnt_up)
                        elif i.going_DOWN(line_down,line_up) == True:
                            cnt_down += 1;
                            print( "person", cnt_down)
                            log.write("ID: " + str(cnt_down) + '\n')
                        break
                    if i.getState() == '1':
                        if i.getDir() == 'down' and i.getY() > down_limit:
                            i.setDone()
                        elif i.getDir() == 'up' and i.getY() < up_limit:
                            i.setDone()
                    if i.timedOut():
                        #remove the person from the list
                        index = persons.index(i)
                        persons.pop(index)
                        del i    
                if new == True:
                    p = Person.MyPerson(pid,cx,cy, max_p_age)
                    persons.append(p)
                    pid += 1     

            #drawing the image to the frames
            cv.circle(frame,(cx,cy), 5, (0,0,255), -1)
            img = cv.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)            
        
    #drawing  the trajectories
    for i in persons:
        cv.putText(frame, str(i.getId()),(i.getX(),i.getY()),font,0.3,i.getRGB(),1,cv.LINE_AA)
        
    #draw  the frames and lines to detect people
  
    str_down = ('Total Count: '+ str(cnt_down))
    frame = cv.polylines(frame,[pts_L1],False,line_down_color,thickness=2)
    frame = cv.polylines(frame,[pts_L3],False,(255,255,255),thickness=1)
    frame = cv.polylines(frame,[pts_L4],False,(255,255,255),thickness=1)
    cv.putText(frame, str_down ,(10,90),font,0.5,(255,255,255),2,cv.LINE_AA)
    cv.putText(frame, str_down ,(10,90),font,0.5,(255,0,0),1,cv.LINE_AA)

    cv.imshow('Crowd Counter',frame)
    

#end if interrupted by users using cntrl c 
    k = cv.waitKey(30) & 0xff
    if k == 27:
        break

#close everything after the video is done
log.flush()
log.close()
cap.release()
cv.destroyAllWindows()