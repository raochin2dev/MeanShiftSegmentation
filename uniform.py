import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import random
import sys,time
from scipy import misc, uint8

#from numpngw import write_png
# file = 'butterfly.jpg';
file = 'hill_house.jpg';
# file = 'house.jpg';
img = mpimg.imread(os.path.dirname(os.path.realpath(__file__))+'/'+file,0)

showBorder = 1
borderColor = [0,0,0]
#plt.subplot(111),plt.imshow(img,cmap=plt.cm.jet)
#plt.title('Butterfly'), plt.xticks([]), plt.yticks([])
#plt.show()
if(isinstance(img[0][0], uint8)):
    img = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)

# print img[0][0]
# sys.exit()
row = img.shape[0]
col = img.shape[1]
size = row*col
H = 60
ITER = 20
featMat = np.zeros((size,5),dtype=int)
markedPts = np.zeros((size,3),dtype=int)
seeds = {}
ptsDict = {}
#print markedPts.shape

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
    #cluster.append(meanPt)
    #indexes.append(meanIndex)    
    temp = np.array([0,0,0])
    for i in seeds.keys():
        if ((markedPts[i]==temp).all()):
            curPt = featMat[i]
            dist = np.sqrt(sum(np.square(meanPt-curPt)))
            if(dist <= H):
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
            dist = np.sqrt(sum(np.square(meanPt-curPt)))
            if(dist <= H):
                cluster.append(curPt)            
                indexes.append(i)
                ptsDict[arrToStr(curPt[3:5])] = 1
    
    cluster = np.array(cluster)    
    
    return sum(cluster)/cluster.shape[0],np.array(indexes)


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
            meanShift = np.sqrt(sum(np.square(newMean-prevMean)))
            prevMean = newMean        

        totalCnt += indexes.shape[0]
        print "Mean:",meanShift,indexes.shape[0]," Total:",totalCnt       
        markPts(indexes)
        


startProcess()
cnt = 0
newImg = np.full((row,col,3),255)
for i in range(row):
    for j in range(col):
        newImg[i][j] = markedPts[cnt]
        cnt += 1
    
plt.subplot(111),plt.imshow(newImg)
plt.title('Butterfly'), plt.xticks([]), plt.yticks([])
#cv2.imwrite(os.path.dirname(os.path.realpath(__file__))+"/res"+str(H)+"_"+str(ITER)+".jpg",newImg)
#write_png("res.jpg",newImg)
path = os.path.dirname(os.path.realpath(__file__))+"/res"+str(H)+"_"+str(ITER)+".jpg"
misc.imsave(path, newImg)

plt.show()
