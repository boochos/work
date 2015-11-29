import maya.cmds as cmds
import webrImport as web
# web
place = web.mod('atom_place_lib')


def proxyGeo(name, joint, width, height, ty=0, tz=0, mlt=1, orient=True):
    # create nulls
    jointsGp = place.null2(name + '_Proxy#', joint, orient=orient)[0]
    jointsGpOffset = place.null2(name + 'Offset_Proxy#', joint, orient=orient)[0]
    geo = cmds.polyCube(name=name + '#', sx=1, sy=1, sz=0, ax=(0, 1, 0), cuv=4, ch=1)[0]
    geoShape = cmds.listRelatives(geo, typ='shape')[0]
    geoConnections = cmds.listConnections(geoShape, s=True, d=False)[0]
    # parent
    #cmds.parent(jointsGp, parent)
    cmds.parent(jointsGpOffset, jointsGp)
    cmds.parent(geo, jointsGpOffset, r=True)
    cmds.parentConstraint(joint, jointsGp, mo=True)
    # attributes
    place.hijackAttrs(geoConnections, jointsGpOffset, 'width', 'width', set=False, default=width)
    place.hijackAttrs(geoConnections, jointsGpOffset, 'height', 'height', set=False, default=height)
    place.hijackAttrs(geoConnections, jointsGpOffset, 'depth', 'depth', set=False, default=tz)
    cmds.setAttr(jointsGpOffset + '.tz', (tz / 2) * mlt)
    cmds.setAttr(jointsGpOffset + '.ty', ty)


def proxyGeoList(name, joints, width, height, ty=0, tz=0, mlt=1, orient=True):
    '''\n
    joints = list of joints on which to place proxy geo[]\n
    width  = width of cube\n
    height = height of cube\n
    ty     = translateY offset\n
    '''
    # count
    i = 0
    if type(joints) == list:
        # parent group
        parent = place.null2(name + '_ProxyGp', joints[0])
        for item in joints:
            if item != joints[len(joints) - 1]:
                # print item
                # distance
                pos1 = cmds.xform(joints[i], q=True, rp=True, ws=True)
                pos2 = cmds.xform(joints[i + 1], q=True, rp=True, ws=True)
                distance = place.distance2Pts(pos1, pos2)
                if distance != 0:
                    # create nulls
                    jointsGp = place.null2(name + '_Proxy#', item, orient=orient)[0]
                    jointsGpOffset = place.null2(name + 'Offset_Proxy#', item, orient=orient)[0]
                    geo = cmds.polyCube(name=name + '#', sx=1, sy=1, sz=0, ax=(0, 1, 0), cuv=4, ch=1)[0]
                    geoShape = cmds.listRelatives(geo, typ='shape')[0]
                    geoConnections = cmds.listConnections(geoShape, s=True, d=False)[0]
                    # parent
                    cmds.parent(jointsGp, parent)
                    cmds.parent(jointsGpOffset, jointsGp)
                    cmds.parent(geo, jointsGpOffset, r=True)
                    cmds.parentConstraint(item, jointsGp, mo=True)
                    # distance
                    pos1 = cmds.xform(joints[i], q=True, rp=True, ws=True)
                    pos2 = cmds.xform(joints[i + 1], q=True, rp=True, ws=True)
                    distance = place.distance2Pts(pos1, pos2)
                    # attributes
                    place.hijackAttrs(geoConnections, jointsGpOffset, 'width', 'width', set=False, default=width)
                    place.hijackAttrs(geoConnections, jointsGpOffset, 'height', 'height', set=False, default=height)
                    place.hijackAttrs(geoConnections, jointsGpOffset, 'depth', 'depth', set=False, default=distance)
                    cmds.setAttr(jointsGpOffset + '.tz', (distance / 2) * mlt)
                    cmds.setAttr(jointsGpOffset + '.ty', ty)
                i = i + 1
    else:
        parent = place.null2(name + '_ProxyGp', joints)
        proxyGeo(name, joints, width, height, ty, tz, mlt, orient=orient)


# Core
tail = ['tail_jnt_01', 'tail_jnt_02', 'tail_jnt_03',
        'tail_jnt_04', 'tail_jnt_05', 'tail_jnt_06',
        'tail_jnt_07', 'tail_jnt_08', 'tail_jnt_09',
        'tail_jnt_010', 'tail_jnt_011']
spine = ['pelvis_jnt', 'spine_jnt_01', 'spine_jnt_02', 'spine_jnt_03',
         'spine_jnt_04', 'spine_jnt_05', 'spine_jnt_06']
neck = ['neck_jnt_01', 'neck_jnt_02', 'neck_jnt_03',
        'neck_jnt_04', 'neck_jnt_05']
front_R = ['front_shoulder_jnt_L', 'front_knee_jnt_L',
           'front_ankle_jnt_L', 'front_pad_jnt_01_L']
pelvis = ['pelvis_jnt', 'tail_jnt_01']
chest = ['spine_jnt_06', 'neck_jnt_02']
head = 'neck_jnt_06'
scapula = ['scapula_jnt_02_L', 'scapula_jnt_02_R']


proxyGeoList('tail', tail, 2, 2, 0, 0)
proxyGeoList('pelvis', pelvis, 10, 16, -6, 0, -1)
proxyGeoList('spine', spine, 10, 14, -5, 0)
proxyGeoList('chest', chest, 10, 20, -7, 0)
proxyGeoList('neck', neck, 7, 8, 0, 0)
proxyGeoList('head', head, 7, 8, 0, 12, orient=False)

# paws
digits1 = ['_prox_phal_jnt_01_', '_mid_phal_jnt_01_', '_dist_phal_jnt_01_']
digits2 = ['_prox_phal_jnt_02_', '_mid_phal_jnt_02_', '_dist_phal_jnt_02_']
digits3 = ['_prox_phal_jnt_03_', '_mid_phal_jnt_03_', '_dist_phal_jnt_03_']
digits4 = ['_prox_phal_jnt_04_', '_mid_phal_jnt_04_', '_dist_phal_jnt_04_']
end = ['front', 'back', 'front', 'back']
side = ['L', 'L', 'R', 'R']

i = 0
mlt = 1
while i < 4:
    if i >= 2:
        mlt = -1
    for item in digits1:
        proxyGeoList(end[i] + item + side[i], end[i] + item + side[i], 1.5, 1.5, 0, 2, mlt)
    for item in digits2:
        proxyGeoList(end[i] + item + side[i], end[i] + item + side[i], 1.5, 1.5, 0, 2, mlt)
    for item in digits3:
        proxyGeoList(end[i] + item + side[i], end[i] + item + side[i], 1.5, 1.5, 0, 2, mlt)
    for item in digits4:
        proxyGeoList(end[i] + item + side[i], end[i] + item + side[i], 1.5, 1.5, 0, 2, mlt)
    i = i + 1

# legs
legFrnt_L = ['scapula_jnt_02_L', 'front_shoulder_jnt_L', 'front_knee_jnt_L', 'front_ankle_jnt_L', 'front_pad_jnt_01_L']
legBck_L = ['back_hip_jnt_L', 'back_knee_jnt_L', 'back_ankle_jnt_L', 'back_pad_jnt_01_L']
legFrnt_R = ['scapula_jnt_02_R', 'front_shoulder_jnt_R', 'front_knee_jnt_R', 'front_ankle_jnt_R', 'front_pad_jnt_01_R']
legBck_R = ['back_hip_jnt_R', 'back_knee_jnt_R', 'back_ankle_jnt_R', 'back_pad_jnt_01_R']

proxyGeoList('legF_L', legFrnt_L, 5, 5, 0, 10)
proxyGeoList('legB_L', legBck_L, 5, 5, 0, 10)
proxyGeoList('legF_R', legFrnt_R, 5, 5, 0, 10, -1)
proxyGeoList('legB_R', legBck_R, 5, 5, 0, 10, -1)
