# Random Bezier Curve using De Casteljau's algorithm
# http://en.wikipedia.org/wiki/Bezier_curve
# http://en.wikipedia.org/wiki/De_Casteljau%27s_algorithm
# FB - 201111244
import os
import math
from math import sqrt
import random
from PIL import Image, ImageDraw
imgx = 500
imgy = 500
image = Image.new( "RGB", ( imgx, imgy ) )
draw = ImageDraw.Draw( image )

def B( coorArr, i, n, t ):
    '''
    recursive, disects all lines until reaches final point on curve
    Take position A and position B
    multiply posA by weight-1
    multiply posB by weight
    add results to get position of current weight
    coorArr = if n is 0 return coorArr[i]
    i = 0
    n = number of steps iterator
    t =  weight along a line, 0.0-1.0
    '''
    #print i
    if n == 0:
        #last
        #print coorArr[i]
        return coorArr[i]

    first = ( 1 - t ) * B( coorArr, i, n - 1, t )
    #print first, 'frst'
    secnd = t * B( coorArr, i + 1, n - 1, t )
    #print secnd, 'secnd'
    #print first + secnd, 'total'
    return first + secnd


def getControlPoints( p0=[1.0, 0.0], p3=[10.0, 10.0] ):
    #p0 = [x,y]
    #could use multiplier to adjust length of existing weights after key is inserted
    mltp = 0.333333333333333    #multiplier to solve adjacent side, p[1] x coor
    outA = cmds.keyTangent( 'locator1_translateY', q=True, time=( t, t ), outAngle=True )[0]
    adj = ( p3[0] - p0[0] ) * mltp    #tangent coor in x
    opo = math.tan( math.radians( outA ) ) * adj
    p1 = [p0[0] + adj, p0[1] + opo]
    print p1


def getPoint( coorArr, t ):
    '''
    returns 3 points of given weight(t) in given axis
    tangent1 = left tangent position in given axis
    point = point position on curve
    tangent2 = right tangent position in given axis    
    **works for weighted tangents
    **inserting into a weighted tangent means updating existing tangent weights
    '''
    A = coorArr[0]
    B = coorArr[1]
    AB = ( ( 1 - t ) * A ) + ( t * B )

    B = coorArr[1]
    C = coorArr[2]
    BC = ( ( 1 - t ) * B ) + ( t * C )

    C = coorArr[2]
    D = coorArr[3]
    CD = ( ( 1 - t ) * C ) + ( t * D )

    tangent1 = ( ( 1 - t ) * AB ) + ( t * BC )
    tangent2 = ( ( 1 - t ) * BC ) + ( t * CD )

    point = ( ( 1 - t ) * tangent1 ) + ( t * tangent2 )
    return [tangent1, point, tangent2]

def getPointTangents( xList, yList ):
    #dead simple, does not account for pos or neg values
    #does not account for non-weighted tangents
    #solves tangent weights and angles

    #in tangent angle
    xlength = xList[1] - xList[0]    #'adjacent' side in trig speak
    ylength = yList[1] - yList[0]    #'opposite' side in trig speak
    tan = ylength / xlength
    deg = math.degrees( math.atan( tan ) )
    print deg
    #in weighted tangent, length
    hlength = xlength * xlength + ylength * ylength
    hlength = sqrt( hlength )
    print hlength

    #out tangent angle
    xlength = xList[2] - xList[1]    #'adjacent' side in trig speak
    ylength = yList[2] - yList[1]    #'opposite' side in trig speak
    tan = ylength / xlength
    deg = math.degrees( math.atan( tan ) )
    print deg
    #in weighted tangent, length
    hlength = xlength * xlength + ylength * ylength
    hlength = sqrt( hlength )
    print hlength


coorArrX = [1, 4, 7, 10]
coorArrY = [0, 0, 10, 10]

def putPoint():
    #####
    n = 4    # number of control points
    # plot the curve
    steps = 5
    #print range( steps ), 'steps'
    ii = 0
    for k in range( steps ):
        #print k
        t = float( k ) / ( steps - 1 )
        #print t
        x = B( coorArrX, 0, n - 1, t )
        xx = getPoint( coorArrX, t )
        #print x
        print xx, '   XX'
        y = B( coorArrY, 0, n - 1, t )
        yy = getPoint( coorArrY, t )
        print yy, '  yy'
        #print y
        if xx[1] == 3.25:
            getPointTangents( xx, yy )
            #print y, 'here', x    #find tangents in B function maybe
            pass
        try:
            image.putpixel( ( int( x ), int( y ) ), ( 0, 255, 0 ) )
        except:
            pass
        #print x
        #print y
        if ii == 5:
            break
        ii = ii + 1

# plot the control points
cr = 6    # circle radius
for k in range( n ):
    x = coorArrX[k]
    y = coorArrY[k]
    try:
        draw.ellipse( ( x - cr, y - cr, x + cr, y + cr ), ( 255, 0, 0 ) )
    except:
        pass

path = 'C:/Users/Sebastian/Desktop/'
file = path + 'bez1.jpg'
if os.path.isdir( path ):
    i = image.save( file, "JPEG" )
1 - 5
