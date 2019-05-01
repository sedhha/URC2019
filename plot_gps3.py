import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import random



 
class liveplot:
	def __init__(self):
		self.fig = plt.figure() 
		self.ax1 = self.fig.add_subplot(1,1,1)
		
		self.lat = [] 
		self.lon = []
		ani = animation.FuncAnimation(self.fig, self.animate, interval=1000)
		plt.show() 
		
	
	def initial(self):
		n = int(input('Enter number of checkpoints : '))
		for i in range(n):
			x = input('Enter lat : ')
			y = input('Enter lon : ')
			

	def getdata(self):
		fs = open('gps.txt', 'r')
		data = fs.readlines()
		#print(data)
		data = data[-1]
		print(data)
		fs.close()
		x,y = data.split(',')
		return x,y

	def animate(self, i):		
		#self.lat.append(x)  
		#self.lon.append(y)
		self.x, self.y = self.getdata()
		self.lat.append(self.x)
		self.lon.append(self.y)
		
	    	self.ax1.clear() 
	    	self.ax1.plot(self.lat,self.lon)
 
obj = liveplot()
