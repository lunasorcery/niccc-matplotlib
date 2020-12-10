#!/usr/bin/env python3
import math
import struct
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def readByte(file):
	return struct.unpack('B', file.read(1))[0]

def readWord(file):
	return struct.unpack('>H', file.read(2))[0]

def convertColor(rgb):
	r=((rgb>>8)&0x7)/7
	g=((rgb>>4)&0x7)/7
	b=(rgb     &0x7)/7
	return (r,g,b)

# set up matplotlib
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)

# prepare polygon buffers
maxPolysPerFrame = 200
polyBuffer=[]
for i in range(0,maxPolysPerFrame):
	buf,=ax.fill([],[])
	polyBuffer.append(buf)

palette = [(1,0,1)]*16

file = open("scene1.bin", "rb")

ax.clear()
ax.set_xlim(0,256)
ax.set_ylim(200,0)
ax.set_aspect(1)

def animate(frameIndex):
	global file, palette

	polysThisFrame=0

	flags = readByte(file)
	frameNeedsScreenClear = (flags & 1) != 0
	frameHasPaletteData   = (flags & 2) != 0
	frameIsIndexed        = (flags & 4) != 0

	if frameNeedsScreenClear:
		polyBuffer[0].set_xy([[0,0],[256,0],[256,200],[0,200]])
		polyBuffer[0].set_color('#000')
		polysThisFrame+=1

	if frameHasPaletteData:
		paletteMask = readWord(file)
		for i in range(0,16):
			if (paletteMask & (0x8000 >> i)) != 0:
				palette[i] = convertColor(readWord(file))

	if frameIsIndexed:
		numVerts = readByte(file)
		vertBuffer = [(0,0)]*numVerts
		for i in range(0,numVerts):
			x = readByte(file)
			y = readByte(file)
			vertBuffer[i] = (x,y)

	while True:
		polyDescriptor = readByte(file)
		if polyDescriptor == 0xff:
			break
		if polyDescriptor == 0xfe:
			file.seek(math.ceil(file.tell()/65536)*65536)
			break
		if polyDescriptor == 0xfd:
			quit()
		colorIndex = polyDescriptor>>4
		numPolyVerts = polyDescriptor&0xf
		xys=[]
		if frameIsIndexed:
			for i in range(0,numPolyVerts):
				index=readByte(file)
				xys.append(vertBuffer[index])
		else:
			for i in range(0,numPolyVerts):
				x=readByte(file)
				y=readByte(file)
				xys.append((x,y))
		polyBuffer[polysThisFrame].set_xy(xys)
		polyBuffer[polysThisFrame].set_color(palette[colorIndex])
		polysThisFrame+=1
	return polyBuffer[0:polysThisFrame]

ani = animation.FuncAnimation(fig, animate, fargs=None, interval=1, blit=True)
plt.show()
