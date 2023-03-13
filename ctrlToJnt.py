#ctrlToJnt.py

import maya.cmds as mc

def ctrlToJnt(jSelect):
    try:
        if mc.objectType(jSelect) != "joint":
            raise Exception("Error: Cannot bind control to " + jSelect + " with type " + mc.objectType(jSelect))
    except Exception as e:
        print(e)
        return
    
    jControl = mc.circle(n=jSelect+'_ctrl')
    mc.color(jControl, rgb=[1, 1, 0])
    mc.rotate(90, 0, 0)
    mc.makeIdentity(a=True)
    cPositionConstraint = mc.pointConstraint(jSelect, jControl)
    mc.delete(cPositionConstraint)
    mc.makeIdentity(a=True)
    cOffset = mc.group(jControl, n=jControl[0]+'_offset')
    cOffsetConstraint = mc.parentConstraint(jSelect, cOffset)
    mc.delete(cOffsetConstraint)
    #attrToLock = ["tx", "ty", "tz", "rx", "ry", "rz" ,"sx", "sy", "sz"]
    #for attr in attrToLock:
    #    mc.setAttr(cOffset+'.'+attr, lock=True, keyable=False, channelBox=False)
    mc.parentConstraint(jControl, jSelect)
    mc.controller(jControl)
    #mc.select(jControl)
        
        
joints = mc.ls(os=True)
if len(joints) < 1:
    print("Error: Please select at least one joint")
for j in joints:
    ctrlToJnt(j)

#////////////////////////////////////////////////////////////#
