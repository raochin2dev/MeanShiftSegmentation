import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import random
import sys,time
from scipy import misc
import math
import datetime
#from numpngw import write_png

file = 'butterfly.jpg';
# file = 'hill_house.jpg';
# file = 'house.jpg';
img = mpimg.imread(os.path.dirname(os.path.realpath(__file__))+'/'+file,0)

showBorder = 1
borderColor = [0,0,0]

now = datetime.datetime.now()
print "Start Time:", now.hour,"H:", now.minute,"m:", now.second,"s"
row = img.shape[0]
col = img.shape[1]
size = row*col
H = 60
Hs = 60
Hr = 60
ITER = 50
featMat = np.zeros((size,5),dtype=int)
markedPts = np.zeros((size,3),dtype=int)
seeds = {}
ptsDict = {}
kRow,kCol = 100,100
HkCol = 30
RangeDif = math.ceil(255/HkCol)

kernalMat = np.zeros((kRow,kCol),dtype=float)
for i in range(0, kernalMat.shape[0]):
    for j in range(0, kernalMat.shape[1]):
        kernalMat[i][j]= 1-(float(i+j)/100)
        # kernalMat[i][j]= math.exp((-0.5)*np.sqrt(np.square(i)+np.square(j)))

# print kernalMat[49][49]
# sys.exit()

kernalRange = np.zeros((HkCol), dtype = float)
for i in range(int(round(HkCol/2))):
    if(1-(0.01*i) > 0):
        kernalRange[i]= 1-(0.01*i)

    # kernalRange[i]= math.exp((-0.3)*((i)))
# print kernalRange[9]
# sys.exit()


def createFeatMatrix(img):
    cnt = 0
    for i in range(row):
        for j in range(col):
            temp = np.insert(img[i][j],3,[i+1,j+1])
            featMat[cnt] = temp
            seeds[cnt] = cnt
            cnt += 1
    return featMat

def calcFirstMean(meanPt,meanIndex,featMat):

    cluster = []
    indexes = []
    cluster.append(meanPt)
    indexes.append(meanIndex)
    temp = np.array([0,0,0])
    for i in seeds.keys():
        if i != meanIndex and ((markedPts[i]==temp).all()):
            curPt = featMat[i]
            # dist = np.sqrt(sum(np.square(meanPt-curPt)))
            # if(dist <= H):
            #     cluster.append(curPt)
            #     indexes.append(i)
            coordDiff = np.abs(meanPt[3:5]-curPt[3:5])
            if(coordDiff[0] < kRow/2 and coordDiff[1] < kCol/2 ):
                wt = kernalMat[coordDiff[0]][coordDiff[1]]
            else:
                wt = 0
            distS = np.sqrt(sum(np.square(meanPt[3:5]-(wt*np.array(curPt[3:5])))))
            # print "Diff:",coordDiff,", wt:",wt

            wtr= kernalRange[int(round(math.ceil((abs(meanPt[0]- curPt[0]))/(RangeDif+1))))]
            distRr = (meanPt[0]-(1*np.array(curPt[0])))
            wtg= kernalRange[int(round(math.ceil((meanPt[1]- curPt[1])/(RangeDif+1))))]
            distRg = (meanPt[1]-(1*np.array(curPt[1])))
            wtb= kernalRange[int(round(math.ceil((meanPt[2]- curPt[2])/(RangeDif+1))))]
            distRb = (meanPt[2]-(1*np.array(curPt[2])))



            #distR = np.sqrt(sum(np.square(meanPt[:3]-(1*np.array(curPt[:3])))))
            if(distS < Hs and distRr < Hr and distRg < Hr and distRb < Hr):
            # if(distS < Hs):
                cluster.append(curPt)
                indexes.append(i)
                ptsDict[arrToStr(curPt[3:5])] = 1

    cluster = np.array(cluster)

    return sum(cluster)/cluster.shape[0],np.array(indexes)


def calcMean(meanPt,featMat):

    cluster = []
    indexes = []
    temp = np.array([0,0,0])
    for i in seeds.keys():
        if ((markedPts[i]==temp).all()):
            curPt = featMat[i]
            # dist = np.sqrt(sum(np.square(meanPt-curPt)))
            # if(dist <= H):
            #     cluster.append(curPt)
            #     indexes.append(i)
            coordDiff = np.abs(meanPt[3:5]-curPt[3:5])
            if(coordDiff[0] < kRow/2 and coordDiff[1] < kCol/2 ):
                wt = kernalMat[coordDiff[0]][coordDiff[1]]
            else:
                wt = 0
            distS = np.sqrt(sum(np.square(meanPt[3:5]-(wt*np.array(curPt[3:5])))))

            wtr= kernalRange[int(round(math.ceil((abs(meanPt[0]- curPt[0]))/(RangeDif+1))))]
            distRr = np.abs(meanPt[0]-(1*np.array(curPt[0])))
            wtg= kernalRange[int(round(math.ceil((meanPt[1]- curPt[1])/(RangeDif+1))))]
            distRg = np.abs(meanPt[1]-(1*np.array(curPt[1])))
            wtb= kernalRange[int(round(math.ceil((meanPt[2]- curPt[2])/(RangeDif+1))))]
            distRb = np.abs(meanPt[2]-(1*np.array(curPt[2])))

            # if(coordDiff[0] < 5 and coordDiff[1] < 5):
            #     print "DistRGB:",distRr,",",distRg,",",distRb," ",coordDiff


            #distR = np.sqrt(sum(np.square(meanPt[:3]-(1*np.array(curPt[:3])))))
            if(distS < Hs and distRr < Hr and distRg < Hr and distRb < Hr):
                cluster.append(curPt)
                indexes.append(i)
                ptsDict[arrToStr(curPt[3:5])] = 1


    cluster = np.array(cluster)
    if(cluster.shape[0] > 0):
        return sum(cluster)/cluster.shape[0],np.array(indexes)
    else:
        return -1,np.array(indexes)


def markPts(ptIndexes):

    color = None
    clusterSize = ptIndexes.shape[0]
    for i in range(clusterSize):
        if(color == None):
            color = featMat[ptIndexes[i]][0:3]
        else:
            color += featMat[ptIndexes[i]][0:3]

    color = color/clusterSize

    for i in range(clusterSize):
        if isBorderPt(featMat[ptIndexes[i]]) and showBorder:
            markedPts[ptIndexes[i]] = borderColor
        else:
            markedPts[ptIndexes[i]] = color
        del seeds[ptIndexes[i]]

def isBorderPt(pt):
    # print pt
    x,y = pt[3:5][0],pt[3:5][1]
    # print x,y,pt[3:5]
    return not(arrToStr([x,y+1]) in ptsDict and arrToStr([x+1,y]) in ptsDict and arrToStr([x-1,y]) in ptsDict and arrToStr([x,y-1]) in ptsDict)
    #     return False
    # return True

def arrToStr(arr):
    return str(arr[0])+','+str(arr[1])


totalCnt = 0
def startProcess():
    global totalCnt
    featMat = createFeatMatrix(img)

    while(totalCnt < size):
        randKey = random.choice(seeds.keys())
        seed = featMat[randKey]
        prevMean,indexes = calcFirstMean(seed,randKey,featMat)
        meanShift = np.sqrt(sum(np.square(seed-prevMean)))
        global ptsDict
        while(meanShift > ITER):
            ptsDict = {}
            newMean,indexes = calcMean(prevMean,featMat)
            if(indexes.shape[0] == 0):
                break
            meanShift = np.sqrt(sum(np.square(newMean-prevMean)))
            print "NewMean:",newMean,"CurMean:",prevMean," MS:",meanShift
            prevMean = newMean

        totalCnt += indexes.shape[0]
        print "Mean:",meanShift," Total:",totalCnt,"  RandK:",randKey
        if(indexes.shape[0] > 0):
            markPts(indexes)



startProcess()
cnt = 0
newImg = np.full((row,col,3),255)
for i in range(row):
    for j in range(col):
        newImg[i][j] = markedPts[cnt]
        cnt += 1

now = datetime.datetime.now()
print "End Time:", now.hour,"H:", now.minute,"m:", now.second,"s"

plt.subplot(111),plt.imshow(newImg)
plt.title('Butterfly'), plt.xticks([]), plt.yticks([])
#cv2.imwrite(os.path.dirname(os.path.realpath(__file__))+"/res"+str(H)+"_"+str(ITER)+".jpg",newImg)
#write_png("res.jpg",newImg)
path = os.path.dirname(os.path.realpath(__file__))+"/res"+str(H)+"_"+str(Hs)+"_"+str(Hr)+"_"+str(ITER)+"_"+str(showBorder)+".jpg"
misc.imsave(path, newImg)

plt.show()

