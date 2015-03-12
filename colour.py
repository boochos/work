# import webrImport as web
# web


def rgbConversion(rgb=[]):
    '''
    convert 0-255 rgb to 0.0-1.0 rgb
    '''
    newrgb = []
    if len(rgb) == 3:
        for i in rgb:
            newrgb.append(float(i) / 255.0)
        return newrgb
    else:
        pass


# print rgbConversion(rgb=[86, 146, 184])


class Get():

    def __init__(self):
        '''
        get colors for maya ui
        '''
        self.neutral = [0.38, 0.38, 0.38]
        self.darkbg = [0.17, 0.17, 0.17]
        self.grey = [0.5, 0.5, 0.5]
        self.greyD = [0.2, 0.2, 0.2]
        self.red = [0.5, 0.2, 0.2]
        self.redD = [0.4, 0.2, 0.2]
        self.blue = [0.2, 0.3, 0.5]
        self.green = [0.2, 0.5, 0.0]
        self.teal = [0.0, 0.5, 0.5]
        self.purple = [0.35, 0.35, 0.5]
        self.purple2 = [0.28, 0.28, 0.39]
        self.orange = [0.5, 0.35, 0.0]
        self.pink = [0.8, 0.4, 0.4]
        self.blue2 = [0.23, 0.36, 0.49]
