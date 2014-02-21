#get shot specs from Jabuka if they exist
try:

    #get job and show data
    workingPath = Jabuka.getWorkingPathLocation(onlyBase=False, throwException=False, createEntity=True)
    shotInfo = ShotgunDatabase.ShotInfo( workingPath[0].name, workingPath[1].name, workingPath[2].name ).asDict()

    job = os.environ['QUBE_CLUSTER'].strip('/')
    jobInfo = ShotgunDatabase.JobInfo(job).asDict()

    jobWidth = int(jobInfo['defaultResolutionWidth'])
    jobHeight= int(jobInfo['defaultResolutionHeight']/jobInfo['defaultPixelAspectRatio'])
    shotWidth = int(shotInfo['defaultResolutionWidth'])
    shotHeight= int(shotInfo['defaultResolutionHeight']/shotInfo['defaultPixelAspectRatio'])
    if shotWidth and shotHeight:
        if shotWidth != 0 and shotHeight != 0:
            print 'using job width and height', jobWidth, ',', jobHeight, 'at ', playblastSizeMultiplier*100, '%'
            height = jobHeight
            width = jobWidth
except:
    pass
