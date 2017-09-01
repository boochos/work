import alembic as almb

import imathmodule

# list functions
dir(almb)

al = '/VFX/projects/testing/_Sequences/_SeqTemplate/_ShotTemplate/3D/maya/scenes/cache/alembic/Untitled.abc'

iarch = almb.Abc.IArchive(al)
top = iarch.getTop()
numChildren = top.getNumChildren()
print numChildren
print top.getChildHeader(0).getFullName()

'''
print name
meshObj = almb.AbcGeom.IPolyMesh(top, 'lol')
mesh = meshObj.getSchema()
uv = mesh.getUVsParam()
print uv
geoScope = almb.AbcGeom.GeometryScope(top)
print geoScope
dir(geoScope)
'''
