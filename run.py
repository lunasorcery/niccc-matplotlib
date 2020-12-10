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

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)

palette = [(1,0,1)]*16

file = open("scene1.bin", "rb")

def animate(frameIndex):
	global file, palette

	flags = readByte(file)
	frameNeedsScreenClear = (flags & 1) != 0
	frameHasPaletteData   = (flags & 2) != 0
	frameIsIndexed        = (flags & 4) != 0

	ax.clear() # clear every frame as prior frame draws will linger otherwise
	ax.set_xlim(0,256)
	ax.set_ylim(200,0)
	ax.set_aspect(1)
	plt.title(f"{frameIndex}")
	if frameNeedsScreenClear:
		plt.fill([0,256,256,0],[0,0,200,200],color='#000')

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
		xs=[]
		ys=[]
		if frameIsIndexed:
			for i in range(0,numPolyVerts):
				index=readByte(file)
				xy=vertBuffer[index]
				xs.append(xy[0])
				ys.append(xy[1])
		else:
			for i in range(0,numPolyVerts):
				xs.append(readByte(file))
				ys.append(readByte(file))
		plt.fill(xs, ys, color=palette[colorIndex])

ani = animation.FuncAnimation(fig, animate, fargs=None, interval=10)
plt.show()
