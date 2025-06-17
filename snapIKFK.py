"""
Detalles:
    - Script con funciones para cambiar del modo FK a IK, y viceversa, sin mover los joints de lugar.
    - Se espera que el estado sea completamente IK o FK (0 o 1) al momento de ejecutar cada funcion.
    - Tiene en cuenta los siguientes sistemas:
        - Pole Vector
        - Stretch
    - Los siguientes sistemas que existen en IK no funcionan en FK:
        - (...)_shoulderIKBase_ctl
        - (...)_handIKRot_ctl (funciona de IK a FK, pero no se puede volver al mismo estado luego)

    -Ejemplos de uso
        # CREAR LOCATOR FK EN BRAZOS O PIERNAS
            create_arm_fk_pv_locator(side = "x")    # se cambia x por el lado en el que desea implementar el sistema
            create_leg_fk_pv_locator(side = "x")    # L o R

        # CREAR LOCATOR EN LOS HUESOS
            create_arm_bones_locator(side = "x")    # se cambia x por el lado en el que desea implementar el sistema
            create_leg_bones_locator(side = "x")    # L o R

        # SNAP DE FK A IK BRAZOS Y PIERNAS
            snap_arm_fk_to_ik(side="x")     # se cambia x por el lado en el que desea implementar el sistema
            snap_leg_fk_to_ik(side="x")     # L o R

        # SNAP DE IK A FK BRAZOS Y PIERNAS
            snap_arm_ik_to_fk(side="x")     # se cambia x por el lado en el que desea implementar el sistema
            snap_leg_ik_to_fk(side="x")     # L o R

        # AUTO SNAP
            auto_snap(part="x", side="y")     # se cambia x por que parte se desea afectar  ( arm o leg )
                                              # se cambia y por el lado que se desea que sea afectado (L o R)
Autor:
    - Sofia Ares Fernandez
Fecha de actualizacion:
    12/03/2024 by Sofia:
        -Create script
        -Testing and changing spelling mistake
    14/03/2024 by Sofia:
        -Add leg side to sistem.
        -Testing and changing spelling mistakes
Entorno:
    -Python 2023.2.4
    -Autodesk Maya 2023
    -Windows
"""

import maya.cmds as cmds

def _create_hidden_locator(target=None, name=None, parent=None, lock=None):
    """
    - Creara un locator con el nombre especificado "name" dentro de un grupo,
        oculto bajo el nodo "parent" especificado,
        en la posicion y orientacion del nodo "target" especificado.
    - El nombre del grupo sera <"nombreDelLocator>_root">.
    - Esta funcion devolvera una lista: [locator, root].
    - El locator puede tener sus atributos sin lock, o con lock en base al argumento "lock".
    Keyword Args:
            -name:   <str> El nombre del locator.
                            Default: <nombreDelNodoDondeSeCrea>_loc
            -target:   <str> El nombre del nodo desde donde se quiere crear el locator.
                            Argumento obligatorio.
            - parent:   <str> El nodo en el cual se pondra el grupo con el locator.
                            Default: target.
            - lock:    <bool> Si es True, el locator tendra sus atributos en modo lock (bloqueados).
                            Default: True.

    """

    # Input verification
    if not target:
        raise ValueError("Please specify a target.")
    if not name:
        name = target + "_loc"
    if not parent:
        parent = target

    # -------------------------------
    # Get current values
    if not cmds.objExists(name):
        _currentPos = cmds.xform(target, q=True, ws=True, translation=True)
        _currentRot = cmds.xform(target, q=True, ws=True, rotation=True)

    # -------------------------------
    # Create locator and its group
    locator = cmds.spaceLocator(n=name)
    root= cmds.group(n=locator[0] + "_root")

    # -------------------------------
    # Lock locator if necessary
    if lock:
        for attr in 'trs':
            for ax in 'xyz':
                cmds.setAttr("{}.{}{}".format(locator[0], attr, ax), lock=True)

    # -------------------------------
    #Parent the group under the specified node and lock it
    par = cmds.listRelatives(root, p=True)
    if not par or par[0] != parent :
        cmds.parent(root,parent)
    cmds.parent(root, parent)
    cmds.xform(root, ws=True, translation=_currentPos)
    cmds.xform(root, ws=True, rotation=_currentRot)
    cmds.setAttr("{}.v".format(root),0)
    for attr in 'trs':
        for ax in 'xyz':
            cmds.setAttr("{}.{}{}".format(locator[0], attr, ax), lock=True)

    # -------------------------------
    # Select and return the created nodes
    cmds.select(root,locator[0])
    return[locator[0], root]

def create_arm_fk_pv_locator(side = "L"):
    """
    - Cuidado: Ejecutar esta funcion con el rig en la posicion default.
    - Como el FK no tiene el locator para el pole vector, esta funcion lo agrega.
    - Utilizaran la posicion de L/R_armPoleVector_ctl y guardara el locator
        bajo L/R_elbowFK_ctl.
    - Esta funcion es valida para la configuracion del rig mostrado en este modulo.
        En caso de que la jerarquia de nodos o setup de los sistemas de FK/IK difieron,
        se debe adaptar su contenido.
    -Devolvera una lista: [locator, root]
    Keywords Args:
        side   <str> El lado donde se quiere crear el locator.
                    Default: "L". Posibles valores: "L" o "R".
    """

    ctl = side + "_armPoleVector_ctl"
    par = side + "_elbowFK_ctl"

    if side not in ["L", "R"]:
        print("Please set a side argument: 'L' or 'R'")
        return

    return  _create_hidden_locator(target=ctl, parent=par, lock=False)

def create_arm_bones_locator(side = "L"):
    """
    - Cuidado: Ejecutar esta funcion con el rig en la posicion default.
    - Crear dos locator ocultos en la posicion defual de los joints, para saber el porcentaje de stretch:
        - side + "_elbow_jnt" (bajo side + "_shoulder_jnt")
        - side + "_wrist_jnt" (bajo side + "_elbow_jnt")
    - Devolvera una lista: [elbow_locator, elbow_root,
                            wrist_locator, wrist_root]
    Keywords Args:
        side   <str>  El lado donde se quiere crear el locator.
                        Default: "L". Posible valores: "L" o "R"
    """

    elbow = side + "_elbow_jnt"
    elbow_par = side + "_shoulder_jnt"
    wrist = side + "_wrist_jnt"
    wrist_par = elbow

    if side not in ["L", "R"]:
        print("Please set a side argument: 'L' or ' R'")
        return

    elbow_lst = _create_hidden_locator(target=elbow, parent=elbow_par)
    wrist_lst = _create_hidden_locator(target=wrist, parent=wrist_par)

    result = elbow_lst + wrist_lst

    return result

def _get_stretch_percentage(start=None, end=None):
    """
    - Funcion simple pensada para calcular la diferencia entre dos nodos,
        aplicada al snap FK IK.
    - Esta funcion solo tendra en cuenta la diferencia entre los atributos de translateX.
    Keyword Ags:
        - start  <str>  El nodo que se encuentra en estado inicial (1)
                        Default: None
        - end  <str>    El nodo que se usa para calcular la diferencia con start.
                        Default: None
    """
    if not start:
        raise ValueError("Please specify a start joint.")
    if not end:
        raise ValueError("Please specify an end joint.")

    start_pos = cmds.getAttr("{}.translateX".format(start))
    end_pos = cmds.getAttr("{}.translateX".format(end))

    return end_pos/start_pos

def snap_arm_fk_to_ik(side="L"):
    """
    - Convierte del estado FK a IK (1 a 0).
    - Cuidado respecto a esta funcion:
        - No tiene en cuenta estado intermedios, solo de 1 a 0.
        - No se pueden setear valores de stretch menores a 1 en el sistema IK,
            por lo que si en FK hay valores menores a 1, se seteara 1.
    Keyword Args:
        side   <str>   El lado donde se quiere crear el locator.
                        Default: "L". Posibles valores: ["L","R"]
    """
    if side not in ["L", "R"]:
        print("Please set a side argument: 'L' or ' R'")
        return

    #-----------------------
    # Define arguments
    #-----------------------
    # For translation and rotation
    wrs_lst = [side + "_wristFK_ctl", side + "_handIK_ctl"]
    hand_ik_rot = side + "_handIKRot_ctl"
    # For Pole Vector
    pole_vector_lst = [side + "_armPoleVector_ctl_loc", side + "_armPoleVector_ctl"]
    # For stretch
    shld_fk_stretch_ctl = side + "_shoulderFK_ctl"
    elbow_fk_stretch_ctl = side + "_elbowFK_ctl"
    stretch_attr = "Stretch"
    stretch_ik_ctl = side + "_handIK_ctl"
    stretch_ik_up_attr = "UpperStretchManual"
    stretch_ik_lwr_attr = "LowerStretchManual"

    # Main Switch
    arm_fkik_ctl = side + "_armIKFK_ctl"
    arm_fkik_attr = "IKFK"

    #-----------------------
    # Get Values
    #-----------------------
    # Get current position and orientation of wrist FK
    wrs_trn = cmds.xform(wrs_lst[0], q=True,ws=True,translation=True)
    wrs_rot = cmds.xform(wrs_lst[0], q=True, ws=True,rotation=True)

    # Get current FK's pole vector locator values
    pv_trn = cmds.xform(pole_vector_lst[0], q=True, ws=True, translation=True)
    pv_rot = cmds.xform(pole_vector_lst[0], q=True, ws=True, rotation=True)

    # Get stretch values
    shld_str = cmds.getAttr("{}.{}".format(shld_fk_stretch_ctl, stretch_attr))
    elb_str = cmds.getAttr("{}.{}".format(elbow_fk_stretch_ctl, stretch_attr))

    #-----------------------
    # Set Values
    #-----------------------
    # Switch Status
    cmds.setAttr("{}.{}".format(arm_fkik_ctl, arm_fkik_attr), 0)

    # Set trn and rot
    cmds.xform(wrs_lst[1], ws=True, translation=wrs_trn)
    cmds.xform(wrs_lst[1], ws=True, rotation=wrs_rot)

    # (!) Reset hand to IK Rot just in case
    for axs in 'xyz':
        cmds.setAttr("{}.r{}".format(hand_ik_rot, axs), 0)

    # Apply FK pole vector pos to IK pole vecto
    cmds.xform(pole_vector_lst[1], ws=True, translation=pv_trn)
    cmds.xform(pole_vector_lst[1], ws=True, rotation=pv_rot)

    # (!) Reset stretch attribute for IK just in case
    cmds.setAttr("{}.{}".format(stretch_ik_ctl, stretch_attr), 0)

    # Set manual stretch values for IK
    if shld_str < 1:
        cmds.warning("The shoulder stretch is less than 1, but IK doesn't support values less than 1")
        shld_str = 1

    if elb_str < 1:
        cmds.warning("The elbow stretch is less than 1, but IK doesn't support values less than 1")
        elb_str = 1

    cmds.setAttr("{}.{}".format(stretch_ik_ctl, stretch_ik_up_attr), shld_str)
    cmds.setAttr("{}.{}".format(stretch_ik_ctl, stretch_ik_lwr_attr), elb_str)

def snap_arm_ik_to_fk(side="L"):
    """
    - Convierte del estado FK a IK (0 a 1).
    - Cuidado respecto a esta funcion:
        - No tiene en cuenta estado intermedios, solo de 0 a 1.
    Keyword Args:
        side   <str>   El lado donde se quiere crear el locator.
                        Default: "L". Posibles valores: ["L","R"]
    """
    if side not in ["L", "R"]:
        print("Please set a side argument: 'L' or ' R'")
        return

    #-----------------------
    # Define arguments
    #-----------------------
    # For translation and rotation
    shl_lst = [side + "_shoulderIK_jnt", side + "_shoulderFK_ctl"]
    elb_lst = [side + "_elbowIK_jnt", side + "_elbowFK_ctl"]
    wrs_lst = [side + "_wristIK_jnt", side + "_wristFK_ctl"]
    # For Pole Vector
    pole_vector_lst = [side + "_armPoleVector_ctl", side + "_armPoleVector_ctl_loc"]
    # Main switch
    arm_fkik_ctl = side + "_armIKFK_ctl"
    arm_fkik_attr = "IKFK"
    # For stretch
    elbow_loc_root = side + "_elbow_jnt_loc_root"
    elbow_jnt = side + "_elbow_jnt"
    wrist_loc_root = side + "_wrist_jnt_loc_root"
    wrist_jnt = side + "_wrist_jnt"
    stretch_attr = "Stretch"
    shld_stretch_ctl = side + "_shoulderFK_ctl"
    elbow_stretch_ctl = side + "_elbowFK_ctl"

    #-----------------------
    # Get Values
    #-----------------------
    # Get current IK's pole vector locator values
    pv_trn = cmds.xform(pole_vector_lst[0], q=True, ws=True, translation=True)
    pv_rot = cmds.xform(pole_vector_lst[0], q=True, ws=True, rotation=True)

    # Get stretch percentage
    shld_str_per = _get_stretch_percentage(start=elbow_loc_root, end=elbow_jnt)
    elb_str_per = _get_stretch_percentage(start=wrist_loc_root, end=wrist_jnt)

    #-----------------------
    # Set Values
    #-----------------------
    # Switch Status
    cmds.setAttr("{}.{}".format(arm_fkik_ctl, arm_fkik_attr), 1)

    # Apply orientation with constraint
    for axs in ["X", "Z"]:
        cmds.setAttr("{}.rotate{}".format(elb_lst[1], axs), lock=False)

    orCons_shl = cmds.orientConstraint(shl_lst[0], shl_lst[1], offset=[0,0,0], weight=1)
    orCons_elb = cmds.orientConstraint(elb_lst[0], elb_lst[1], offset=[0,0,0], weight=1)
    orCons_wrs = cmds.orientConstraint(wrs_lst[0], wrs_lst[1], offset=[0,0,0], weight=1)

    cmds.delete(orCons_shl, orCons_elb, orCons_wrs)

    for axs in ["X", "Z"]:
        cmds.setAttr("{}.rotate{}".format(elb_lst[1], axs), 0)
        cmds.setAttr("{}.rotate{}".format(elb_lst[1], axs), lock=True)

    # Apply IK pole vector pos to FK pole vecto
    cmds.xform(pole_vector_lst[1], ws=True, translation=pv_trn)
    cmds.xform(pole_vector_lst[1], ws=True, rotation=pv_rot)

    # Set stretch percentage
    cmds.setAttr("{}.{}".format(shld_stretch_ctl, stretch_attr), shld_str_per)
    cmds.setAttr("{}.{}".format(elbow_stretch_ctl, stretch_attr), elb_str_per)

def create_leg_fk_pv_locator(side = "L"):
    """
    - Cuidado: Ejecutar esta funcion con el rig en la posicion default.
    - Como el FK no tiene el locator para el pole vector, esta funcion lo agrega.
    - Utilizaran la posicion de L/R_legPoleVector_ctl y guardara el locator
        bajo L/R_kneeFK_ctl.
    - Esta funcion es valida para la configuracion del rig mostrado en este modulo.
        En caso de que la jerarquia de nodos o setup de los sistemas de FK/IK difieron,
        se debe adaptar su contenido.
    -Devolvera una lista: [locator, root]
    Keywords Args:
        side   <str> El lado donde se quiere crear el locator.
                    Default: "L". Posibles valores: "L" o "R".
    """

    ctl = side + "_legPoleVector_ctl"
    par = side + "_kneeFK_ctl"

    if side not in ["L", "R"]:
        print("Please set a side argument: 'L' or 'R'")
        return

    return  _create_hidden_locator(target=ctl, parent=par, lock=False)

def create_leg_bones_locator(side = "L"):
    """
    - Cuidado: Ejecutar esta funcion con el rig en la posicion default.
    - Crear dos locator ocultos en la posicion defual de los joints, para saber el porcentaje de stretch:
        - side + "_knee_jnt" (bajo side + "_hip_jnt")
        - side + "_ankle_jnt" (bajo side + "_knee_jnt")
    - Devolvera una lista: [knee_locator, knee_root,
                            ankle_locator, ankle_root]
    Keywords Args:
        side   <str>  El lado donde se quiere crear el locator.
                        Default: "L". Posible valores: "L" o "R"
    """

    knee = side + "_knee_jnt"
    knee_par = side + "_hip_jnt"
    ankle = side + "_ankle_jnt"
    ankle_par = knee
    toes= side + "_toe_jnt"
    toes_par= ankle

    if side not in ["L", "R"]:
        print("Please set a side argument: 'L' or ' R'")
        return

    knee_lst = _create_hidden_locator(target=knee, parent=knee_par)
    ankle_lst = _create_hidden_locator(target=ankle, parent=ankle_par)
    toes_lst = _create_hidden_locator(target=toes, parent=toes_par)

    result = knee_lst + ankle_lst + toes_lst

    return result

def snap_leg_fk_to_ik(side="L"):
    """
    - Convierte del estado FK a IK (1 a 0).
    - Cuidado respecto a esta funcion:
        - No tiene en cuenta estado intermedios, solo de 1 a 0.
        - No se pueden setear valores de stretch menores a 1 en el sistema IK,
            por lo que si en FK hay valores menores a 1, se seteara 1.
    Keyword Args:
        side   <str>   El lado donde se quiere crear el locator.
                        Default: "L". Posibles valores: ["L","R"]
    """
    if side not in ["L", "R"]:
        print("Please set a side argument: 'L' or ' R'")
        return

    #-----------------------
    # Define arguments
    #-----------------------
    # For translation and rotation
    ank_lst = [side + "_ankle_jnt_loc", side + "_footIK_ctl"]
    # For Pole Vector
    pole_vector_lst = [side + "_legPoleVector_ctl_loc", side + "_legPoleVector_ctl"]
    # For stretch
    hip_fk_stretch_ctl = side + "_hipFK_ctl"
    knee_fk_stretch_ctl = side + "_kneeFK_ctl"
    stretch_attr = "Stretch"
    stretch_ik_ctl = side + "_footIK_ctl"
    stretch_ik_up_attr = "UpperStretchManual"
    stretch_ik_lwr_attr = "LowerStretchManual"
    # For toes
    toes_lst= [side + "_toeFK_ctl", side + "_toeIK_ctl"]

    # Main Switch
    leg_fkik_ctl = side + "_legIKFK_ctl"
    leg_fkik_attr = "IKFK"

    #-----------------------
    # Get Values
    #-----------------------
    # Get current position and orientation of ankle FK
    ank_trn = cmds.xform(ank_lst[0], q=True,ws=True,translation=True)
    ank_rot = cmds.xform(ank_lst[0], q=True, ws=True,rotation=True)

    # Get current FK's pole vector locator values
    pv_trn = cmds.xform(pole_vector_lst[0], q=True, ws=True, translation=True)
    pv_rot = cmds.xform(pole_vector_lst[0], q=True, ws=True, rotation=True)

    # Get stretch values
    hip_str = cmds.getAttr("{}.{}".format(hip_fk_stretch_ctl, stretch_attr))
    knee_str = cmds.getAttr("{}.{}".format(knee_fk_stretch_ctl, stretch_attr))

    # Get rotation values for toes
    toes_rot = cmds.xform(toes_lst[0], q=True, ws=True, rotation=True)

    #-----------------------
    # Set Values
    #-----------------------
    # Switch Status
    cmds.setAttr("{}.{}".format(leg_fkik_ctl, leg_fkik_attr), 0)

    # Set trn and rot
    cmds.xform(ank_lst[1], ws=True, translation=ank_trn)
    cmds.xform(ank_lst[1], ws=True, rotation=ank_rot)

    # Apply FK pole vector pos to IK pole vecto
    cmds.xform(pole_vector_lst[1], ws=True, translation=pv_trn)
    cmds.xform(pole_vector_lst[1], ws=True, rotation=pv_rot)

    # (!) Reset stretch attribute for IK just in case
    cmds.setAttr("{}.{}".format(stretch_ik_ctl, stretch_attr), 0)

    # Set manual stretch values for IK
    if hip_str < 1:
        cmds.warning("The hip stretch is less than 1, but IK doesn't support values less than 1")
        hip_str = 1

    if knee_str < 1:
        cmds.warning("The knee stretch is less than 1, but IK doesn't support values less than 1")
        knee_str = 1

    cmds.setAttr("{}.{}".format(stretch_ik_ctl, stretch_ik_up_attr), hip_str)
    cmds.setAttr("{}.{}".format(stretch_ik_ctl, stretch_ik_lwr_attr), knee_str)

    # Set toes rotation
    cmds.xform(toes_lst[1], ws=True, rotation=toes_rot)

def snap_leg_ik_to_fk(side="L"):
    """
    - Convierte del estado FK a IK (0 a 1).
    - Cuidado respecto a esta funcion:
        - No tiene en cuenta estado intermedios, solo de 0 a 1.
    Keyword Args:
        side   <str>   El lado donde se quiere crear el locator.
                        Default: "L". Posibles valores: ["L","R"]
    """
    if side not in ["L", "R"]:
        print("Please set a side argument: 'L' or ' R'")
        return

    #-----------------------
    # Define arguments
    #-----------------------
    # For translation and rotation
    hip_lst = [side + "_hipIK_jnt", side + "_hipFK_ctl"]
    knee_lst = [side + "_kneeIK_jnt", side + "_kneeFK_ctl"]
    ankle_lst = [side + "_ankleIK_jnt", side + "_ankleFK_ctl"]
    # For Pole Vector
    pole_vector_lst = [side + "_legPoleVector_ctl", side + "_legPoleVector_ctl_loc"]
    # Main switch
    leg_fkik_ctl = side + "_legIKFK_ctl"
    leg_fkik_attr = "IKFK"
    # For stretch
    knee_loc_root = side + "_knee_jnt_loc_root"
    knee_jnt = side + "_knee_jnt"
    ankle_loc_root = side + "_ankle_jnt_loc_root"
    ankle_jnt = side + "_ankle_jnt"
    stretch_attr = "Stretch"
    hip_stretch_ctl = side + "_hipFK_ctl"
    knee_stretch_ctl = side + "_kneeFK_ctl"

    # For toes
    toes_lst= [side + "_toeIK_ctl", side + "_toeFK_ctl"]

    #-----------------------
    # Get Values
    #-----------------------
    # Get current IK's pole vector locator values
    pv_trn = cmds.xform(pole_vector_lst[0], q=True, ws=True, translation=True)
    pv_rot = cmds.xform(pole_vector_lst[0], q=True, ws=True, rotation=True)

    # Get stretch percentage
    hip_str_per = _get_stretch_percentage(start=knee_loc_root, end=knee_jnt)
    knee_str_per = _get_stretch_percentage(start=ankle_loc_root, end=ankle_jnt)

    # Get rotation values for toes
    toes_rot = cmds.xform(toes_lst[0], q=True, ws=True, rotation=True)

    #-----------------------
    # Set Values
    #-----------------------
    # Switch Status
    cmds.setAttr("{}.{}".format(leg_fkik_ctl, leg_fkik_attr), 1)

    # Apply orientation with constraint
    for axs in ["X", "Y"]:
        cmds.setAttr("{}.rotate{}".format(knee_lst[1], axs), lock=False)

    orCons_hip = cmds.orientConstraint(hip_lst[0], hip_lst[1], offset=[0,0,0], weight=1)
    orCons_knee = cmds.orientConstraint(knee_lst[0], knee_lst[1], offset=[0,0,0], weight=1)
    orCons_ankle = cmds.orientConstraint(ankle_lst[0], ankle_lst[1], offset=[0,0,0], weight=1)

    cmds.delete(orCons_hip, orCons_knee, orCons_ankle)

    for axs in ["X", "Y"]:
        cmds.setAttr("{}.rotate{}".format(knee_lst[1], axs), 0)
        cmds.setAttr("{}.rotate{}".format(knee_lst[1], axs), lock=True)

    # Apply IK pole vector pos to FK pole vecto
    cmds.xform(pole_vector_lst[1], ws=True, translation=pv_trn)
    cmds.xform(pole_vector_lst[1], ws=True, rotation=pv_rot)

    # Set stretch percentage
    cmds.setAttr("{}.{}".format(hip_stretch_ctl, stretch_attr), hip_str_per)
    cmds.setAttr("{}.{}".format(knee_stretch_ctl, stretch_attr), knee_str_per)

    # Set toes rotation
    cmds.xform(toes_lst[1], ws=True, rotation=toes_rot)

def auto_snap(part="arm", side="L"):
    """
    - Automaticamente detecta si el control esta en FK o IK, y ejecuta la funcion adecuada.
    Keyword Args:
            part  <str> La parte a la cual se el quiere aplicar el snap.
                        Default: "arm". Posibles valores: ["arm", "leg"
            side  <str> El lado donde se quiere crear el locator.
                        Default: "L". Posibles valores: ["L", "R"]
    """
    fkik_attr = "IKFK"
    part_valid = ["arm", "leg"]
    side_valid = ["L",  "R"]

    # Input Verifications
    if part not in part_valid:
        print("The specified part is not valid. Please use one of the following: {!r}".format(part_valid))
    if side not in side_valid:
        print("The specified side is not valid. Please use one of the following: {!r}".format(side_valid))

    # Comprobation and execution on arm ctls
    _full_name = "{}_{}IKFK_ctl.{}".format(side, part, fkik_attr)
    if cmds.objExists(_full_name):
        current = cmds.getAttr(_full_name)
        # Current state is FK
        if current == 1:
            if part == part_valid[0]:  #"arm"
                snap_arm_fk_to_ik(side=side)
            elif part == part_valid[1]:
                snap_leg_fk_to_ik(side=side)

        # Current state is IK
        elif current == 0:
            if part == part_valid[0]:  #"arm"
                snap_arm_ik_to_fk(side=side)
            elif part == part_valid[1]:
                snap_leg_ik_to_fk(side=side)

    else:
        print("Please specify a valid IK/FK arm switch controller and attribute.")
        return


# Codigos para utilizar para testeo en el modelo de maya

#import snapFKIK

#snapFKIK.create_arm_fk_pv_locator()
# snapFKIK.create_arm_bones_locator()
# snapFKIK.snap_arm_fk_to_ik()
# snapFKIK.snap_arm_ik_to_fk()
# snapFKIK.create_leg_fk_pv_locator()
# snapFKIK.create_leg_bones_locator()
# snapFKIK.snap_leg_fk_to_ik()
# snapFKIK.snap_leg_ik_to_fk()
# snapFKIK.auto_snap()
