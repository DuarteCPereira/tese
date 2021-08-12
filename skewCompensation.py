import re


'''
xytan = xyerr/xylen
yztan = yzerr/yzlen
zxtan = zxerr/zxlen

'''

def gSkewer(filename, xytan, yztan, zxtan):
    outname = re.sub(r'.gcode', '-skewed.gcode', filename)
    
    outfile = open(outname, 'a')
    
    xin = 0.0
    yin = 0.0
    zin = 0.0
    
    with open(filename, 'r') as infile:
        for line in infile:
            gmatch = re.match(r'G[0-1]', line, re.I)
            if gmatch:
                print('line was a G0/G1 command!')
                xsrch = re.search(r'[xX]-?\d*\.*\d*', line, re.I)
                if xsrch:
                    xin = float(re.sub(r'[xX]', '', xsrch.group()))
                
                ysrch = re.search(r'[yY]-?\d*\.*\d*', line, re.I)
                if ysrch:
                    yin = float(re.sub(r'[yY]', '', ysrch.group()))
                
                zsrch = re.search(r'[zZ]-?\d*\.*\d*', line, re.I)
                if zsrch:
                    zin = float(re.sub(r'[zZ]', '', zsrch.group()))
    
                
                xout = round(xin - yin * xytan, 3)
                yout = round(yin - zin * yztan, 3)
                xout = round(xout - zin * zxtan, 3)
    
                # z remains the same to prevent layers being tilted
                zout = zin
    
                lineout = line
                print('old line:', lineout)
    
                if xsrch:
                    lineout = re.sub(r'[xX]-?\d*\.*\d*', 'X' + str(xout), lineout)
    
                if ysrch:
                    lineout = re.sub(r'[yY]-?\d*\.*\d*', 'Y' + str(yout), lineout)
    
                if zsrch:
                    lineout = re.sub(r'[zZ]-?\d*\.*\d*', 'Z' + str(zout), lineout)
    
                print('new line: ', lineout)
                outfile.write(lineout)
            else:
                print('Skipping, not a movement.', line)
                outfile.write(line)
gSkewer('UMS5_pre_skewed_cube.gcode', 0.25, 0, 0)
