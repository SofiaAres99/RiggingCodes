"""
Detalles:
    -  Script con utilidades para crear grupos
    -  Funciones:
        switchspaces()

Autor:
    - Sofia Ares Fernandez
Fecha de actualizacion:
    03/02/2024 by Sofia:
        -Create script
        -Testing and changing spelling mistakes
    06/02/2023
        -Recommended corrections by tutor
Entorno:
    -Python 2023.2.4
    -Autodesk Maya 2023
    -Windows
"""

import maya.cmds as cmds

# controlName y el space se cambiara por el controlador y el space deseado (este es solamente de ejemplo)

def change_switchSpace(controlName="", attr="Spaces", space=0):
    """
        -Funcion que sirve para poder cambiar el sistema de spaces de los controladores IK.
            El sistema hace que cuando se mueva un controlador relacionado con el space del controlador IK,
            el animador pueda cambiar el sistema de spaces sin que el controlador se mueva de posicion

        """
    #Creamos una lista vacia para la seleccion
    selection= list()

    #Comporbar si hay controlName
    if controlName:
        selection= [controlName]

    else:
        # Obtenemos la seleccionn actual
        selection = cmds.ls(sl=True)

    # Verificamos si hay seleccion
    if selection:
        # Cuando hay seleccion
        # Iteramos sobre cada objeto
        for item in selection:

            #Comporbar si la seleccion tiene el attribute de .Spaces
            if not cmds.attributeQuery(attr, node=item, exists=True):
                cmds.warning (item + "does not have the attribute" + attr)
                continue

            # Guardamos los valores de matriz (translation y rotation)
            ctlMatrix = cmds.xform(item, query=True, worldSpace=True, matrix=True)

            # Saber el valor maximo de el atributo enum del controlador seleccionado
            enum_max = int(cmds.addAttr(item + attr, query=True, max=True))

            #Comprobar si space es mayor que enum_max
            if space > enum_max:
                cmds.warning(attr + "asked are bigger than max.")
                # Continue para que pase al siguiente item
                continue

            # Seteamos el space nuevo
            cmds.setAttr(item + '.' + attr, space)

            # Pegamos valores de matriz en el control
            cmds.xform(item, worldSpace=True, matrix=ctlMatrix)

    else:
        # Cuando no hay seleccion
        cmds.warning("Select at least one object.")

var = change_switchSpace(controlName="L_handIK_ctl", space=0)