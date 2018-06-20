# Draw 3d plots of LUT cube file.
# Usage: python plot_cube.py [lut file] [skip(optional)]
#   -Only LUT_3D type of cube format is supported.
#   -If the generated plot is too messy, try larger skip value (default 4) to generate sparse meshgrid.

import sys
import os.path
import re
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

# Default & Global values
sTitle = ""
sLut_3d_size = 33
sVal_max = 1.0
sVal_min = 0.0
sR_index = 0
sG_index = 0
sB_index = 0
sLut = 0.
sLutSizeSpecified = False
sSkip = 4

def parse_line(line):
    global sTitle
    global sLut_3d_size
    global sVal_max
    global sVal_min
    global sR_index
    global sG_index
    global sB_index
    global sLut
    global sLutSizeSpecified
    
    # Title
    pattern = r"^[ \t]*TITLE[ \t]+\"[\w ]+\""
    match = re.match(pattern , line)
    if match is not None:
        t = re.search(r"\"[\w ]+\"" , match.group())
        sTitle = t.group()
        print("TITLE:",sTitle)
        return
        
    # LUT_3D_SIZE
    pattern = r"^[ \t]*(LUT_3D_SIZE)[ \t]+[\d]+"
    match = re.match(pattern , line)
    if match is not None:
        t = re.search(r"[ \t][\d]+" , match.group())
        sLut_3d_size = int(t.group())
        sR_index = 0
        sG_index = 0
        sB_index = 0
        sLut = np.zeros((sLut_3d_size,sLut_3d_size,sLut_3d_size,3), dtype=np.float64)
        sLutSizeSpecified = True
        print("LUT_3D_SIZE:",sLut_3d_size)
        return
    
    # Reject LUT_1D_SIZE
    pattern = r"^[ \t]*LUT_1D_SIZE[ \t][\d]+"
    match = re.match(pattern , line)
    if match is not None:
        print("Error: LUT_1D_SIZE is not supported.")
        quit()
        
    # LUT values
    # also supports exponential expressions such as 1.23456e-05
    number = r"([\d]*[\.]?[\d]*)(e(\-)?[\d]+)?"
    space = r"[ \t]+"
    pattern = r"^[ \t]*" + number + space + number + space + number
    match = re.match(pattern , line)
    if match is not None:
        t = match.group().split()
        if len(t) != 3:
            print("Error: bad format")
            quit()
        
        if (sB_index >= sLut_3d_size) and (sG_index >= sLut_3d_size) and (sR_index >= sLut_3d_size):
            print("Error: bad format")
            quit()
        
        sLut[sR_index][sG_index][sB_index][0] = np.float64(t[0])
        sLut[sR_index][sG_index][sB_index][1] = np.float64(t[1])
        sLut[sR_index][sG_index][sB_index][2] = np.float64(t[2])
        
        sB_index += 1
        if sB_index >= sLut_3d_size:
            sB_index = 0
            sG_index += 1
            if sG_index >= sLut_3d_size:
                sG_index = 0
                sR_index += 1
        
        return
    
def import_lut(fn):
    f = open(fn)
    lines2 = f.readlines()
    f.close()
    
    l = 1
    for line in lines2:
        parse_line(line)
        l += 1

def draw_outerbox(fig,ax):
    # Draw outer box
    X_start = float(sVal_min)
    X_end   = float(sVal_max)
    Y_start = float(sVal_min)
    Y_end   = float(sVal_max)
    Z_start = float(sVal_min)
    Z_end   = float(sVal_max)
    
    X, Y = np.meshgrid([X_start,X_end], [Y_start,Y_end])
    ax.plot_wireframe(X,Y,Z_start,  color='black')
    ax.plot_wireframe(X,Y,Z_end,    color='black')

    Y, Z = np.meshgrid([Y_start,Y_end],[Z_start,Z_end])
    ax.plot_wireframe(X_start,  Y,Z,color='black')
    ax.plot_wireframe(X_end,    Y,Z,color='black')

    X, Z = np.meshgrid([X_start,X_end],[Z_start,Z_end])
    ax.plot_wireframe(X,Y_start,Z,color='black')
    ax.plot_wireframe(X,Y_end,  Z,color='black')
    
def draw_meshgrid(fig,ax):
    # Draw mesh for each red with skipping
    for i in range(0,sLut_3d_size,sSkip):
        ax.plot_wireframe(sLut[i,0:
            sLut_3d_size:sSkip,0:sLut_3d_size:sSkip,0],
            sLut[i,0:sLut_3d_size:sSkip,0:sLut_3d_size:sSkip,1],
            sLut[i,0:sLut_3d_size:sSkip,0:sLut_3d_size:sSkip,2],
            color=cm.hsv(float(i)/float(sLut_3d_size)))
    
    # Draw last mesh if skipped in the loop above
    if((sLut_3d_size - 1) % sSkip):
        ax.plot_wireframe(sLut[sLut_3d_size - 1,0:
            sLut_3d_size:sSkip,0:sLut_3d_size:sSkip,0],
            sLut[sLut_3d_size - 1,0:sLut_3d_size:sSkip,0:sLut_3d_size:sSkip,1],
            sLut[sLut_3d_size - 1,0:sLut_3d_size:sSkip,0:sLut_3d_size:sSkip,2],
            color=cm.hsv(1.0))

def draw_labels(fig,ax):
    ax.set_xlabel('R')
    ax.set_ylabel('G')
    ax.set_zlabel('B')
    ax.set_title(sTitle)

if __name__ == "__main__":

    argvs = sys.argv
    argc = len(argvs)

    if(argc < 2) or (argc > 3):
        print ("Usage: python plot_cube.py [lut file] [skip(optional)]")
        quit()

    if(argc == 3):
        sSkip = int(argvs[2])
        if(sSkip == 0):
            print("Error: Skip value must be >= 1")
            quit()
            
    if not os.path.exists(argvs[1]):
        print("Error: ",argvs[1]," not exists.")
        quit()
        
    import_lut(argvs[1])
        
    if not sLutSizeSpecified:
        print("Error: LUT size not specified in cube file.")
        quit()

    fig = plt.figure()
    ax = Axes3D(fig)
    
    # Draw outer box
    draw_outerbox(fig,ax)

    # Draw meshgrids
    draw_meshgrid(fig,ax)
    
    # Labelling
    draw_labels(fig,ax)
    
    plt.show()

