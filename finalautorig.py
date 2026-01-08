import maya.api.OpenMaya as om2
import maya.cmds as cmds
import pymel.core as pm


window = pm.window(title="Skeleton Rig Window")
layout = pm.columnLayout(adjustableColumn=True)
sliderGrp2 = pm.intSliderGrp(label="Step1: Spine Length", min=3, max = 7, field=True)
button = pm.button(label="Step1: create_spine", command='spine(pm.intSliderGrp(sliderGrp2, q=True, value=True), pm.intSliderGrp(sliderGrp2, q=True, value=True))')
maya.cmds.separator(h=10)
sliderGrp1 = pm.intSliderGrp(label="Step2: Arm Length", min=3, max=20, field=True)
button = pm.button(label="Step2: create_arms", command='arms(pm.intSliderGrp(sliderGrp1, q=True, value=True))')
pm.showWindow( window )

def locator():
    pm.curve(n='locator1', d=1, p=[(1, 0, -3), (1, 0, -3), (1, 0, -1), (3, 0, -1), (3, 0, 1), (1, 0, 1), (1, 0, 3), (-1, 0, 3), (-1, 0, 1), (-3, 0, 1), (-3, 0, -1), (-1, 0, -1), (-1, 0, -3)])

def makeOval():
    pm.curve(n='oval', d=3, p=[(0, 0, -1), (-2, 0, -1), (-3, 0, 0), (-2, 0, 1), (0, 0, -1), (2, 0, -1), (3, 0, 0), (2, 0, 1), (0, 0, 1)])

def makeArrow():
    pm.curve(n='arrow', d=1, p=[(0, 0, -1), (1, 0, -1), (1, 0, -2), (3, 0, 0), (1, 0, 2), (1, 0, 1), (0, 0, 1)])
   
def quadArrow():
    #drawing the character control
    firstArrow = makeArrow()
    secondArrow = makeArrow()
    thirdArrow = makeArrow()
    fourthArrow = makeArrow()
    pm.setAttr('arrow' + '.tx', 1)
    pm.setAttr('arrow1' + '.tx', -1)
    pm.setAttr('arrow1' + '.sx', -1)
    pm.setAttr('arrow1' + '.sz', -1)
    pm.setAttr('arrow2' + '.ry', 90)
    pm.setAttr('arrow2' + '.tz', -1)
    pm.setAttr('arrow3' + '.ry', -90)
    pm.setAttr('arrow3' + '.tz', 1)
    
    pm.attachCurve('arrow', 'arrow1', 'arrow2', 'arrow3', rpo=False, n='root')
    pm.xform('root', cp=True, s=(7, 7, 7), t=(7, 0, 0), ro=(0, 0, 0))
    
def freezeTransformsOnJoints():
    # funtion I can call real quikc to freeze transforms on joints real fast
    selectedJoint = pm.select('hip', replace=True)
    joints = pm.ls(type='joint')
    pm.select(joints, replace=True)

    for item in joints:
        pm.makeIdentity(item, apply=True, jo=True)

def legs():
    #create leg
    pm.select( d=True )
    pm.joint( name='hip', p=(0, 27, 0) )
    pm.joint( name='right_leg1', p=(8, 20, 0) )
    pm.joint( name='right_leg2', p=(8, 10, 1)  )
    pm.joint( name='right_leg3', p=(8, 0, 0) )

    pm.select( d=True )
    pm.joint( name='left_leg1', p=(-8, 20, 0) )
    pm.joint( name='left_leg2', p=(-8, 10, 1)  )
    pm.joint( name='left_leg3', p=(-8, 0, 0) )
    #create foot
    pm.select('right_leg3', replace=True)
    k = 3
    for i in range(0, 3):
        k = k + 2
        pm.joint(name='right_foot{0}'.format(i+1), p=(8, 0, k))
    
    k = 3
    pm.select('left_leg3', replace=True)
    for i in range(0, 3):
        k = k + 2
        pm.joint(name='left_foot{0}'.format(i+1), p=(-8, 0, k))
    pm.parent('left_leg1', 'hip')

    pm.parent('spine1', 'hip')

    freezeTransformsOnJoints()
    
    
def spine(joints, tweenspinelength):
    pm.select( d=True )
    k = 27
    for i in range(0, joints):
        k = k + tweenspinelength
        pm.joint(name='spine{0}'.format(i+1), p=(0, k, 0))
        
def IKspline():
    IKspinelist = []
    FKspinelist = []
    # create IK spine
    pm.duplicate('spine1', n='IKspine1', rc=True)
    IKsplinejoints = pm.listRelatives('IKspine1')
    joints = pm.ls(pm.listRelatives('IKspine1', ad=True))
    
    k = 1
    for i in joints[::-1]:
        print(i.name())
        k = k + 1
        newname = 'IK' + ''.join([i for i in i.name() if not i.isdigit()]) + str(k)
        
        pm.rename(i, newname)
    
   #create FKspine   
    pm.duplicate('spine1', n='FKspine1', rc=True)
    pm.select('FKspine1', replace=True)
    pm.select(pm.listRelatives('FKspine1', ad=True))
    FKjoints = pm.ls(pm.listRelatives('FKspine1', ad=True))
    
    k = 1
    for i in FKjoints[::-1]:
        print(i.name())
        k = k + 1
        newname = 'FK' + ''.join([i for i in i.name() if not i.isdigit()]) + str(k)
        pm.rename(i, newname)  
          
    #create IK handle
    joints = pm.ls(type='joint')
    for item in joints:
        if 'IKspine' in item.name():
            IKspinelist.append(item)
    IKhandle = pm.ikHandle(n='IKhandle_spine', sol='ikSplineSolver', ee=IKspinelist[-1].name(), createCurve=True, sj='IKspine1', ns=4)
 
    pm.selectMode(component=True)
   
    sel_vtx = cmds.ls('curve1' + '.cv[*]', fl=True)
    
    
    #create a cube centered at cv[0], cv[-1], and cv[middle]
    middle = (len(sel_vtx) - 1)/2
    for i in sel_vtx:
        if i == sel_vtx[0]:
            shape = pm.polyCube(i,n='IKctrlspine1', d=3, h=3, w=10)
            ctrl = pm.cluster(i)
            pm.matchTransform(shape, ctrl)
            contrlcurve = pm.listRelatives(shape, c=True)
            pm.parentConstraint(shape, ctrl)
        if i == sel_vtx[int(middle)]:
            shape = pm.polyCube(i, n='IKctrlspine2', d=3, h=3, w=10)
            ctrl = pm.cluster(i)
            pm.matchTransform(shape, ctrl)
            contrlcurve = pm.listRelatives(shape, c=True)
            pm.parentConstraint(shape, ctrl)
        if i == sel_vtx[-1]:
            shape = pm.polyCube(i, n='IKctrlspine3', d=3, h=3, w=10)
            ctrl = pm.cluster(i)
            pm.matchTransform(shape, ctrl)
            contrlcurve = pm.listRelatives(shape, c=True)
            pm.parentConstraint(shape, ctrl)
    
  
    #get list of FK spine, IKspine, and SCspine to orient contraint
    FKspinelist.append(pm.listRelatives('FKspine1')) 
    FKspinelist.append('FKspine1')
    IKspinelist.append('IKspine1')       
    for item in IKspinelist:
        #will not include spine1
        IKspineitems = item.name()[2:]
        for FKitem in FKspinelist:
            pm.orientConstraint(IKspineitems, FKitem, item)
        
    pm.orientConstraint('IKspine1', 'FKspine1', 'spine1')
    pm.orientConstraint('IKspine2', 'FKspine2', 'spine2')
    pm.orientConstraint('IKspine3', 'FKspine3', 'spine3')

def arms(armlength):
    #create arms
    spine = pm.ls(type='joint')
    spinelist = []
    for obj in spine:
        if obj.name().startswith('spine'):
            spinelist.append(obj)
    
   
    pm.select('spine3', replace=True)
    x = 0
    y = 45
    
    for i in range(0, 3):
        x = x - armlength
        y = y - 3
        pm.joint(name='left_arm{0}'.format(i+1), p=(x, y, 0), oj='yzx', sao='xup')
        pm.joint( 'left_arm1', e=True, zso=True, oj='yzx' )
        pm.makeIdentity(jo=True)
       
    pm.select('spine3', replace=True)
    x = 0
    y = 45
    for i in range(0, 3):
        x = x - armlength
        y = y - 3
        pm.joint(name='right_arm{0}'.format(i+1), p=(-x, y, -0), oj='yzx', sao='xup')
        pm.joint( 'right_arm1', e=True, zso=True, oj='yzx' )
        pm.makeIdentity(jo=True) 

    pm.joint( 'left_arm2', e=True, oj='yxz' )
    pm.joint( 'right_arm2', e=True, oj='yxz' )
    pm.joint( 'left_arm3', e=True, oj='yzx' )
    pm.joint( 'right_arm3', e=True, oj='yzx' )
    
    pm.select( 'right_arm2', r=True )
    pm.rotate(0, 1, 0)
    pm.select( 'left_arm2', r=True )
    pm.rotate(0, 1, 0)
    selectedJoint = pm.select('spine1', replace=True)
    joints = pm.ls(type='joint')
    pm.select(joints, replace=True)   
                
def parentjoints():
    #parenting joints to individual controls
    value = pm.intSliderGrp(sliderGrp2, q=True, value=True)
    selectedJoint = pm.select('spine1', replace=True)
    joints = pm.ls(type='joint')
    pm.select(joints, replace=True)

    for item in joints:
        #create control for each joint
        contrl = pm.circle(n='ctrl ' + item.name())
        pm.matchTransform(contrl, item)
        pm.xform(contrl, s=(3, 3, 3), cp=True)
        pm.rotate(0, 90, 0)
        contrlcurve = pm.listRelatives(contrl)[0]
        #rotate joints that need to be rotatted
        if item.name()[:-1].endswith("arm"):
            pm.rotate(0, 0, 90)
            pm.makeIdentity(contrl, apply=True)
            pm.orientConstraint(contrl, item, mo=True)
        if item.name().endswith("arm1"):
            pm.makeIdentity(contrl, apply=True)
            pm.orientConstraint(contrl, item, mo=True)
            
        if item.name().startswith("hip"):
            pm.makeIdentity(contrl, apply=True)
            pm.parentConstraint(contrl, item, mo=True)
        
        if item.name().startswith("spine"):
            pm.scale(7, 7, 7)
            pm.makeIdentity(contrl, apply=True)
            pm.parentConstraint(contrl, item, mo=True)
            
        if item.name()[:-1].endswith("foot"):
            pm.rotate(0, 0, 0)
            pm.makeIdentity(contrl, apply=True)
            pm.orientConstraint(contrl, item, mo=True)
            
        if item.name()[:-1].endswith("leg"):
            pm.rotate(0, 90, 0)
            pm.makeIdentity(contrl, apply=True)
            pm.orientConstraint(contrl, item, mo=True)
    #parent joints
    pm.parent('ctrl_left_foot3', 'ctrl_left_foot2')
    pm.parent('ctrl_right_foot3', 'ctrl_right_foot2')
            
    pm.parent('ctrl_left_foot2', 'ctrl_left_foot1')
    pm.parent('ctrl_right_foot2', 'ctrl_right_foot1')
    
    pm.parent('ctrl_left_foot1', 'ctrl_left_leg3')
    pm.parent('ctrl_right_foot1', 'ctrl_right_leg3')
    
    pm.parent('ctrl_left_leg3', 'ctrl_left_leg2')
    pm.parent('ctrl_right_leg3', 'ctrl_right_leg2')
    
    pm.parent('ctrl_left_leg2', 'ctrl_left_leg1')
    pm.parent('ctrl_right_leg2', 'ctrl_right_leg1')
    
    pm.parent('ctrl_left_leg1', 'ctrl_hip')
    pm.parent('ctrl_right_leg1', 'ctrl_hip')
    #parent spine
    pm.parent('ctrl_spine2', 'ctrl_spine1')
    pm.parent('ctrl_spine3', 'ctrl_spine2')
    if pm.objExists('ctrl_spine4'):
        pm.parent('ctrl_spine4', 'ctrl_spine3')
    if pm.objExists('ctrl_spine5'):
        pm.parent('ctrl_spine5', 'ctrl_spine4')
    if pm.objExists('ctrl_spine6'):
        pm.parent('ctrl_spine6', 'ctrl_spine5')
    if pm.objExists('ctrl_spine7'):
        pm.parent('ctrl_spine7', 'ctrl_spine6')
    pm.parent('ctrl_left_arm3', 'ctrl_left_arm2')
    pm.parent('ctrl_right_arm3', 'ctrl_right_arm2')
    
    pm.parent('ctrl_left_arm2', 'ctrl_left_arm1')
    pm.parent('ctrl_right_arm2', 'ctrl_right_arm1')  
    
    pm.parent('ctrl_left_arm1', 'ctrl_spine3') 
    pm.parent('ctrl_right_arm1', 'ctrl_spine3') 
    
    pm.parent('ctrl_spine1', 'ctrl_hip') 
    

    if pm.objExists('ctrl_spine7'):
        pm.parent('ctrl_left_arm1', 'ctrl_spine7')
    if pm.objExists('ctrl_spine6'):
        pm.parent('ctrl_left_arm1', 'ctrl_spine6')
    if pm.objExists('ctrl_spine5'):
        pm.parent('ctrl_left_arm1', 'ctrl_spine5')
    if pm.objExists('ctrl_spine4'):
        pm.parent('ctrl_left_arm1', 'ctrl_spine4')
    if pm.objExists('ctrl_spine3'):
        pm.parent('ctrl_left_arm1', 'ctrl_spine3')


    
def createaimconstraint(ctrl1, ctrl2, ctrl3, number):
    #program to create aim constraint
    loc1 = pm.curve(n='locator1', d=1, p=[(1, 0, -3), (1, 0, -3), (1, 0, -1), (3, 0, -1), (3, 0, 1), (1, 0, 1), (1, 0, 3), (-1, 0, 3), (-1, 0, 1), (-3, 0, 1), (-3, 0, -1), (-1, 0, -1), (-1, 0, -3),(1, 0, -3)])

    pm.matchTransform(loc1, ctrl2, pos=True)  

    pm.move(loc1, number, z=True)
    pm.rotate(0, 90, 0)

    IKcontrol = pm.polyCube(n='IKcontrol_' + ctrl1, h=3, d=3, w=3)
    
    pm.matchTransform(IKcontrol, ctrl3)
    pm.makeIdentity(IKcontrol, s=True)
    
    IKhandle = pm.ikHandle(n='IKhandle' + ctrl1, sol='ikRPsolver', sj=ctrl1, ee=ctrl3, snc=True)
    pm.parentConstraint('IKcontrol_' + ctrl1, 'IKhandle' + ctrl1)
   
    pm.poleVectorConstraint(loc1, 'IKhandle' + ctrl1)
    
    pm.addAttr(IKcontrol, longName='FK', at='bool' , k=True, h=False)
    pm.addAttr(IKcontrol, longName='IK', at='bool', k=True, h=False)
        
def IKhookup():
    #LEG FKIK switch
    #duplicating and renaming duplicates of the left legs to create FK and IK legs
    pm.select('left_leg1', replace=True)
    pm.rename('left_leg1', 'FK_left_leg1')
    leg3 = pm.listRelatives('FK_left_leg1', c=True, ad=True)
    for item in leg3:
        newname = item.name().replace("left", "FK_left")
        pm.rename(item.name(), newname)
        pm.rename(item.name(), newname) 
   
    pm.duplicate()
    pm.rename('FK_left_leg4', 'IK_left_leg1')
    pm.duplicate()
    pm.rename('IK_left_leg2', 'left_leg1')
    
    leg1 = pm.listRelatives('IK_left_leg1', c=True, ad=True)
    leg2 = pm.listRelatives('left_leg1', c=True, ad=True)
    
    for item in leg1:
        newname = item.name().replace("FK_left", "IK_left")
        pm.rename(item.name(), newname)
        pm.rename(item.name(), newname)  
    for item in leg2:
        newname = item.name().replace("FK_left", "left")
        pm.rename(item.name(), newname)
         
    #duplicating and renaming duplicates of right legs to create FK and IK legs
    pm.select('right_leg1', replace=True)
    pm.rename('right_leg1', 'FK_right_leg1')
    leg3 = pm.listRelatives('FK_right_leg1', c=True, ad=True)
    for item in leg3:
        newname = item.name().replace("right", "FK_right")
        pm.rename(item.name(), newname)
        pm.rename(item.name(), newname) 
    
    pm.duplicate()
    pm.rename('FK_right_leg4', 'IK_right_leg1')
    pm.duplicate()
    pm.rename('IK_right_leg2', 'right_leg1')
    leg1 = pm.listRelatives('IK_right_leg1', c=True, ad=True)
    leg2 = pm.listRelatives('right_leg1', c=True, ad=True)
    for item in leg1:
        newname = item.name().replace("FK_right", "IK_right")
        pm.rename(item.name(), newname)
    for item in leg2:
        newname = item.name().replace("FK_right", "right")
        pm.rename(item.name(), newname)
   
    #using aim constraint callback
    createaimconstraint('IK_right_leg1', 'IK_right_leg2', 'IK_right_leg3', 7)
    createaimconstraint('IK_left_leg1', 'IK_left_leg2', 'IK_left_leg3', 7)
   
    #create point constraint of legs with last item being the effected
    pm.pointConstraint('IK_left_leg1', 'FK_left_leg1', 'left_leg1', w=1, mo=False)
    pm.pointConstraint('IK_left_leg2', 'FK_left_leg2', 'left_leg2', w=1, mo=False)
    pm.pointConstraint('IK_left_leg3', 'FK_left_leg3', 'left_leg3', w=1, mo=False)


    pm.pointConstraint('IK_left_foot1', 'FK_left_foot1', 'left_foot1', w=1)
    pm.pointConstraint('IK_left_foot2', 'FK_left_foot2', 'left_foot2', w=1)
    pm.pointConstraint('IK_left_foot3', 'FK_left_foot3', 'left_foot3', w=1)

    pm.pointConstraint('IK_right_leg1', 'FK_right_leg1', 'right_leg1', w=1, mo=False)
    pm.pointConstraint('IK_right_leg2', 'FK_right_leg2', 'right_leg2', w=1, mo=False)
    pm.pointConstraint('IK_right_leg3', 'FK_right_leg3', 'right_leg3', w=1, mo=False)
    
    pm.pointConstraint('IK_right_foot1', 'FK_right_foot1', 'right_foot1', w=1)
    pm.pointConstraint('IK_right_foot2', 'FK_right_foot2', 'right_foot2', w=1)
    pm.pointConstraint('IK_right_foot3', 'FK_right_foot3', 'right_foot3', w=1)

    #setting up IK/FK switch with connection editor
    pm.connectAttr('IKcontrol_IK_left_leg1.FK', 'left_leg3_pointConstraint1.FK_left_leg3W1')
    pm.connectAttr('IKcontrol_IK_left_leg1.IK', 'left_leg3_pointConstraint1.IK_left_leg3W0')
    pm.connectAttr('IKcontrol_IK_left_leg1.FK', 'left_leg2_pointConstraint1.FK_left_leg2W1')
    pm.connectAttr('IKcontrol_IK_left_leg1.IK', 'left_leg2_pointConstraint1.IK_left_leg2W0')
    pm.connectAttr('IKcontrol_IK_left_leg1.FK', 'left_leg1_pointConstraint1.FK_left_leg1W1')
    pm.connectAttr('IKcontrol_IK_left_leg1.IK', 'left_leg1_pointConstraint1.IK_left_leg1W0')
    
    pm.connectAttr('IKcontrol_IK_left_leg1.FK', 'left_foot3_pointConstraint1.FK_left_foot3W1')
    pm.connectAttr('IKcontrol_IK_left_leg1.IK', 'left_foot3_pointConstraint1.IK_left_foot3W0')
    pm.connectAttr('IKcontrol_IK_left_leg1.FK', 'left_foot2_pointConstraint1.FK_left_foot2W1')
    pm.connectAttr('IKcontrol_IK_left_leg1.IK', 'left_foot2_pointConstraint1.IK_left_foot2W0')
    pm.connectAttr('IKcontrol_IK_left_leg1.FK', 'left_foot1_pointConstraint1.FK_left_foot1W1')
    pm.connectAttr('IKcontrol_IK_left_leg1.IK', 'left_foot1_pointConstraint1.IK_left_foot1W0')
    
    pm.connectAttr('IKcontrol_IK_right_leg1.FK', 'right_leg3_pointConstraint1.FK_right_leg3W1')
    pm.connectAttr('IKcontrol_IK_right_leg1.IK', 'right_leg3_pointConstraint1.IK_right_leg3W0')
    pm.connectAttr('IKcontrol_IK_right_leg1.FK', 'right_leg2_pointConstraint1.FK_right_leg2W1')
    pm.connectAttr('IKcontrol_IK_right_leg1.IK', 'right_leg2_pointConstraint1.IK_right_leg2W0')
    pm.connectAttr('IKcontrol_IK_right_leg1.FK', 'right_leg1_pointConstraint1.FK_right_leg1W1')
    pm.connectAttr('IKcontrol_IK_right_leg1.IK', 'right_leg1_pointConstraint1.IK_right_leg1W0')
    
    pm.connectAttr('IKcontrol_IK_right_leg1.FK', 'right_foot3_pointConstraint1.FK_right_foot3W1')
    pm.connectAttr('IKcontrol_IK_right_leg1.IK', 'right_foot3_pointConstraint1.IK_right_foot3W0')
    pm.connectAttr('IKcontrol_IK_right_leg1.FK', 'right_foot2_pointConstraint1.FK_right_foot2W1')
    pm.connectAttr('IKcontrol_IK_right_leg1.IK', 'right_foot2_pointConstraint1.IK_right_foot2W0')
    pm.connectAttr('IKcontrol_IK_right_leg1.FK', 'right_foot1_pointConstraint1.FK_right_foot1W1')
    pm.connectAttr('IKcontrol_IK_right_leg1.IK', 'right_foot1_pointConstraint1.IK_right_foot1W0')
    
    #setting up visibility
    pm.connectAttr('IKcontrol_IK_right_leg1.IK', 'IK_right_leg1.visibility')
    pm.connectAttr('IKcontrol_IK_right_leg1.FK', 'FK_right_leg1.visibility')
    pm.setAttr('IKcontrol_IK_right_leg1.IK', 1)
    pm.connectAttr('IKcontrol_IK_left_leg1.IK', 'IK_left_leg1.visibility')
    pm.connectAttr('IKcontrol_IK_left_leg1.FK', 'FK_left_leg1.visibility')
    pm.setAttr('IKcontrol_IK_left_leg1.IK', 1)
    
    
    #ARM FKIK switch
    #duplicating and renaming duplicates of the left arms to create FK and IK arms
    pm.select('left_arm1', replace=True)
    pm.rename('left_arm1', 'FK_left_arm1')
    leg3 = pm.listRelatives('FK_left_arm1', c=True, ad=True)
    for item in leg3:
        newname = item.name().replace("left", "FK_left")
        pm.rename(item.name(), newname)
        pm.rename(item.name(), newname) 
    
    pm.duplicate()
    pm.rename('FK_left_arm4', 'IK_left_arm1')
    pm.duplicate()
    pm.rename('IK_left_arm2', 'left_arm1')
    
    leg1 = pm.listRelatives('IK_left_arm1', c=True, ad=True)
    leg2 = pm.listRelatives('left_arm1', c=True, ad=True)
    
    for item in leg1:
        newname = item.name().replace("FK_left", "IK_left")
        pm.rename(item.name(), newname)
        pm.rename(item.name(), newname)  
    for item in leg2:
        newname = item.name().replace("FK_left", "left")
        pm.rename(item.name(), newname)
   
    #duplicating and renaming duplicates of the right arms to create FK and IK arms   
    pm.select('right_arm1', replace=True)
    pm.rename('right_arm1', 'FK_right_arm1')
    leg3 = pm.listRelatives('FK_right_arm1', c=True, ad=True)
    for item in leg3:
        newname = item.name().replace("right", "FK_right")
        pm.rename(item.name(), newname)
        pm.rename(item.name(), newname) 
    
    pm.duplicate()
    pm.rename('FK_right_arm4', 'IK_right_arm1')
    pm.duplicate()
    pm.rename('IK_right_arm2', 'right_arm1')
    
    leg1 = pm.listRelatives('IK_right_arm1', c=True, ad=True)
    leg2 = pm.listRelatives('right_arm1', c=True, ad=True)
    
    for item in leg1:
        newname = item.name().replace("FK_right", "IK_right")
        pm.rename(item.name(), newname)
        pm.rename(item.name(), newname)  
    for item in leg2:
        newname = item.name().replace("FK_right", "right")
        pm.rename(item.name(), newname)
 
    #call back to create aim constraint for arm
    createaimconstraint('IK_left_arm1', 'IK_left_arm2', 'IK_left_arm3', -7)
    createaimconstraint('IK_right_arm1', 'IK_right_arm2', 'IK_right_arm3', -7)
    
    #point constrain arm
    pm.pointConstraint('IK_left_arm1', 'FK_left_arm1', 'left_arm1', w=1)
    pm.pointConstraint('IK_left_arm2', 'FK_left_arm2', 'left_arm2', w=1)
    pm.pointConstraint('IK_left_arm3', 'FK_left_arm3', 'left_arm3', w=1)
    
    pm.pointConstraint('IK_right_arm1', 'FK_right_arm1', 'right_arm1', w=1)
    pm.pointConstraint('IK_right_arm2', 'FK_right_arm2', 'right_arm2', w=1)
    pm.pointConstraint('IK_right_arm3', 'FK_right_arm3', 'right_arm3', w=1)
   
   #connect FK/IK switch with connection editor
    pm.connectAttr('IKcontrol_IK_left_arm1.FK', 'left_arm3_pointConstraint1.FK_left_arm3W1')
    pm.connectAttr('IKcontrol_IK_left_arm1.IK', 'left_arm3_pointConstraint1.IK_left_arm3W0')
    pm.connectAttr('IKcontrol_IK_left_arm1.FK', 'left_arm2_pointConstraint1.FK_left_arm2W1')
    pm.connectAttr('IKcontrol_IK_left_arm1.IK', 'left_arm2_pointConstraint1.IK_left_arm2W0')
    pm.connectAttr('IKcontrol_IK_left_arm1.FK', 'left_arm1_pointConstraint1.FK_left_arm1W1')
    pm.connectAttr('IKcontrol_IK_left_arm1.IK', 'left_arm1_pointConstraint1.IK_left_arm1W0')
    
    pm.connectAttr('IKcontrol_IK_right_arm1.FK', 'right_arm3_pointConstraint1.FK_right_arm3W1')
    pm.connectAttr('IKcontrol_IK_right_arm1.IK', 'right_arm3_pointConstraint1.IK_right_arm3W0')
    pm.connectAttr('IKcontrol_IK_right_arm1.FK', 'right_arm2_pointConstraint1.FK_right_arm2W1')
    pm.connectAttr('IKcontrol_IK_right_arm1.IK', 'right_arm2_pointConstraint1.IK_right_arm2W0')
    pm.connectAttr('IKcontrol_IK_right_arm1.FK', 'right_arm1_pointConstraint1.FK_right_arm1W1')
    pm.connectAttr('IKcontrol_IK_right_arm1.IK', 'right_arm1_pointConstraint1.IK_right_arm1W0')
 
    pm.connectAttr('IKcontrol_IK_right_arm1.IK', 'IKcontrol_IK_right_arm1.visibility')
    pm.setAttr('IKcontrol_IK_right_arm1.IK', 1)

    pm.connectAttr('IKcontrol_IK_left_arm1.IK', 'IKcontrol_IK_left_arm1.visibility')
    pm.setAttr('IKcontrol_IK_left_arm1.IK', 1)
    
    #set up root charcter control
    quadArrow()
    allitemsinscene = pm.ls(type='transform')
    
    allitemsinscene = pm.ls('|*')
    for item in allitemsinscene:
        if not item.type() == 'mesh' or 'camera':
            pm.listRelatives('root', s=True)[0]
            pm.parent(item, 'root')

def selectall():
    #select all controls and locators and IKcontrols
    pm.select('ctrl_hip', replace=True)
    all = pm.listRelatives('ctrl_hip', ad=True)
    pm.select(all, add=True)
    pm.select('locator1', add=True)
    pm.select('locator2', add=True)
    pm.select('locator3', add=True)
    pm.select('locator4', add=True)
    pm.select('IKcontrol_IK_left_arm1', add=True)
    pm.select('IKcontrol_IK_left_leg1', add=True)
    pm.select('IKcontrol_IK_right_arm1', add=True)
    pm.select('IKcontrol_IK_right_leg1', add=True)
    
           
#setting up buttons   
button = pm.button(label="Step3: create legs", command='legs()')
button = pm.button(label="Step5: create parentjoints", command='parentjoints()')
button = pm.button(label="Step6: create IKhookup", command='IKhookup()')
button = pm.button(label="Step7: select all controls", command='selectall()')


pm.showWindow( window )