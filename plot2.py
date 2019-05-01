import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
fig=plt.figure()
ax1=fig.add_subplot(121)
ax2=fig.add_subplot(122)
def animate(i):
    pullData=open('atm_data.txt','r').read()
    dataArray=pullData.split('\n')
    xar=[]
    yar=[]
    zar=[]
    time=[]
    for eachLine in dataArray:
        if len(eachLine)>1:
            x,y,z,t=eachLine.split(',')
            xar.append(int(x))
            yar.append(int(x))
            zar.append(int(x))
        ax1.clear()
        ax1.plot(xar,t)
        #ax2.plot(yar,t)
ani=animation.FuncAnimation(fig,animate,1000)
plt.show()
            
