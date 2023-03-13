import maya.cmds as mc


##################################
#           USER INPUT           #

jnt_in_suffix = 'JNT' 

bind_out_suffix = 'BIND_JNT'
ik_out_suffix = 'IK_JNT'
fk_out_suffix = 'FK_JNT'

IK_start = 'R_leg_JNT'
IK_end = 'R_ankle_JNT'

lock_setup = True
if lock_setup:
    lock_suffix = 'LOCK'
    # order these from top to bottom of chain with the format: (LOCK, JNT)
    lock_pairs = [('R_ankle_LOCK', 'R_ankle_JNT'), ('R_ball_LOCK', 'R_ball_JNT'), ('R_toe_LOCK', 'R_toe_JNT')]
    
# TODO: add custom controls (circles for now and by defoult)    
# TODO: add skin toggle and target. Add other skinning params

#                                #
##################################


attrList = ['translate', 'rotate', 'scale']
dims = 'XYZ'
cols = 'RGB'

# select all joints
jnt_chain = mc.ls('*'+jnt_in_suffix, selection=True)

# dupicate into three chains
bind_chain = mc.duplicate(jnt_chain, rc=True)
fk_chain = mc.duplicate(jnt_chain, rc=True)
ik_chain = mc.duplicate(jnt_chain, rc=True)

#clear selection
mc.select()

# rename each to bind, ik, fk
for bind, fk, ik in zip(bind_chain, fk_chain, ik_chain):
    # TODO: figure out better way than JNT1,2,3. Maybe JNT*?
    mc.select(mc.rename(bind, bind.replace(jnt_in_suffix + '1', bind_out_suffix)), add=True)
    mc.select(mc.rename(fk, fk.replace(jnt_in_suffix + '2', fk_out_suffix)), add=True)
    mc.select(mc.rename(ik, ik.replace(jnt_in_suffix + '3', ik_out_suffix)), add=True)
    
# filter and reselect chains with new names   
bind_chain = mc.ls('*' + bind_out_suffix, selection=True)
fk_chain = mc.ls('*' + fk_out_suffix, selection=True)
ik_chain = mc.ls('*' + ik_out_suffix, selection=True)
chains = [(bind_chain, bind_out_suffix), (fk_chain, fk_out_suffix), (ik_chain, ik_out_suffix)]
    
# generate a BCN for each joint and attr in the chain "L_shoulder_BCN"
for jnt in jnt_chain:
    for attr in attrList[:2]:
        bcn = mc.createNode('blendColors', n=jnt.replace(jnt_in_suffix, attr + '_BCN'))
        
# create a control with IK/FK switch attribute
switch_ctrl = mc.circle(r=2, n=IK_source.replace(jnt_in_suffix, 'IK_FK_Switch_CTRL'))
mc.rotate(0, 90, 0)
mc.addAttr(ln = "IK_FK", at='float', k=True, h=False, min=0, max=1, dv=0)

#### Maybe leave this out? The rigger will want to place the control exactly before locking down I think...
# lockhide_attrList = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
# for attr in lockhide_attrList:
#     mc.setAttr(switch_ctrl[0] + '.' + attr, l=True, k=False, cb=False)

mc.group(switch_ctrl, n=switch_ctrl[0] + '_OFST')
mc.group(switch_ctrl[0] + '_OFST', n=switch_ctrl[0] + '_PAD')

print(chains)    
# connect translate, rotate from IK to BCN in 1 for each IK/FK_JNT/BCN
for chain in chains[1:]:
    for jnt in chain[0]:
        for attr in attrList[:2]:
            for i, dim in enumerate(dims):
                target = jnt.replace(chain[1], attr + '_BCN')
                if chain[1] == fk_out_suffix:
                    input = '1'
                else:
                    input = '2'
                print(jnt + '.' + attr + dim, target + '.color' + input + cols[i])
                mc.connectAttr(jnt + '.' + attr + dim, target + '.color' + input + cols[i])
        
# connect output from BCN to BIND for each BCN/BIND
# then connect IK FK value to blender of each BCN
for jnt in bind_chain:
    for attr in attrList[:2]:
        source = jnt.replace(bind_out_suffix, attr + '_BCN')
        mc.connectAttr(source + '.output', jnt + '.' + attr)
        mc.connectAttr(switch_ctrl[0] + '.IK_FK', source + '.blender')
        
# place IK handle between IK_start and IK_end (seems to always use ikRPsolver?)
ikRP_handle = mc.ikHandle(sj=IK_start.replace(jnt_in_suffix, ik_out_suffix), ee=IK_end.replace(jnt_in_suffix, ik_out_suffix), n=IK_end.replace(jnt_in_suffix, 'IKHandle'), sol='ikRPsolver')
sc_handles = []
for i, pair in enumerate(lock_pairs[:-1]):
    sc = mc.ikHandle(sj=pair[1].replace(jnt_in_suffix, ik_out_suffix), ee=lock_pairs[i+1][1].replace(jnt_in_suffix, ik_out_suffix), n=lock_pairs[i+1][1].replace(jnt_in_suffix, 'IKHandle'), sol='ikSCsolver')
    sc_handles.append(sc)
    mc.hide(sc)

# contstrain all lock joints to their couterparts in the jnt chain            
if lock_setup:    
    mc.pointConstraint(lock_pairs[0][0], ikRP_handle[0], mo=True, weight=1)
    for i, pair in enumerate(lock_pairs[1:]):
        mc.pointConstraint(pair[0], sc_handles[i][0])
        
# TODO: build IK control and contstrain heel lock 
# TODO: build FK controls, orient to joints
# TODO: connectAttr from IKFK switch to visibility on controls

# clean up display   
mc.hide(fk_chain, ik_chain, jnt_chain, ikRP_handle)
#mc.delete(jnt_chain)
