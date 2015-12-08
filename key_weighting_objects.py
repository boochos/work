class SkinNodeInformation(object):

    '''
    Class to store skinCluster information
    '''

    def __init__(self, infList=[], objTypes=[], dropoffRate=[], polygonSmoothness=[], nurbsSamples=[], useComponents=[]):
        self.dropoffRate = dropoffRate  # list
        self.polygonSmoothness = polygonSmoothness  # list
        self.nurbsSamples = nurbsSamples  # list
        self.useComponents = useComponents  # list
        self.influences = infList  # list
        self.objTypes = objTypes  # list


class SkinPoint(object):

    '''
    Class to store weighted point information
    '''

    def __init__(self, index=0, influenceList=[], weightList=[], world_translate=[]):
        self.index = index
        self.influenceList = influenceList
        self.weightList = weightList
        self.world_translate = world_translate

    def printInfo(self):
        return '[%s, %s, %s, %s]' % (self.index, self.influenceList, self.weightList, self.world_translate)
