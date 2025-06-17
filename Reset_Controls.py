"""
Detalles:
    -  Scriptpara resetear los valores de nodos.
    -  Este script tiene dos grandes funcionalidades:
        01) Guardar los valores del channelBox de los nodos especificados en un archivo externo.
        02) Ejecutar esos valores guardados.
    - CUIDADO: Este script supone que no existen nodos con el mismo nombre en la escena.
                Si se llegara ejecutar en ese caso, los resultados son inesperados (debido al full path en el nombre).
    - Ejemplos de usos:
        # Export
        _nodes_info = get_nodesInfo_asDict()
        export_dict(dictToExport=nodes_info,
                filePath= 'C:/Example/Directory/Path',
                fileName= 'ctrlsData')
        # Load
        load_dict(fileName= 'ctrlsData',
                  filePath= 'C:/Example/Directory/Path') # Se puede usar prefix en caso necesario usando el argumento prefix
Autor:
    - Sofia Ares Fernandez
Fecha de actualizacion:
    09/02/2024 by Sofia:
        -Create script
        -Testing and changing spelling mistake
Entorno:
    -Python 2023.2.4
    -Autodesk Maya 2023
    -Windows
"""

import maya.cmds as cmds
import os
import json


def get_channelBox_attrs(node):
    """
            -Funcion para obtener los atributos actuales del channelBox de un "node".
            -Esta funcion necesita un objeto para ser ejecutada.
    """

    # Lista a devolver en esta funcion
    _attrs = []
    _allAttrs = cmds.listAttr(node)
    _chbxAttrs = cmds.listAnimatable(node)

    # Comprobamos la informacion de las listas (por si esta vacia)
    if _allAttrs and _chbxAttrs:
        for _attr in _allAttrs:
            for _cbAttr in _chbxAttrs:
                if _cbAttr.endswith(_attr):
                    _attrs.append(_attr)
    return _attrs


def get_nodesInfo_asDict(*args):
    """
            -Devolvera un diccionario con los nombres de los nodos y los atributos en su channel box.
            -Si no se pasa ningun objeto en sus argumentos, intentara utilizar la seleccion actual.
            -El formato del diccionario es:
                {'nombreDelNodoA':
                    {'nombreDelAttrAA':
                        {'value': 'valorAA':
                         'type' : 'typeNameAA'}
                     {'nombreDelAttrAB':
                        {'value': 'valorAB':
                         'type' : 'typeNameAB'}
                }
    """

    # Definir nuestra data que vamos a delvolver
    _data = {}
    if args:
        _targets = args
    else:
        _targets = cmds.ls(sl=True)

    # Verificar el imput por las dudad
    if _targets:
        for target in _targets:

            # Verificar que nuestro target realmente exista
            if cmds.objExists(target):
                _attrs = get_channelBox_attrs(target)

                # Verificar que obtuvimos atributos
                if _attrs:

                    # Creemos una clave con el objeto seleccionado
                    _data[target] = {}
                    for attr in _attrs:
                        typ = cmds.getAttr('{}.{}'.format(target, attr), type=True)
                        val = cmds.getAttr('{}.{}'.format(target, attr))

                        # Guardamos los valores de los atributos y su tipo
                        _data[target][attr] = {'value': val,
                                               'type': typ}
    return _data


def export_dict(**kwargs):
    """
        -Guardar el diccionario como una archivo .json en el directorio especificado.
        -Se necesitan los siguientes argumentos:
            -dictToExport    <dict> La data, en forma de diccionario a exportar o sobreescribir.
                                    Valor default: {}.
            -fileName        <str> El nombre del archivo (sin extension) a exportar o sobreescribir.
                                    Valor default: "".
            -filePath        <str> El path hacia el archivo a exportar o sobreescribir.
                                    Valor default: "".
        -Argumentos opcionales:

            -file_extension        <str> La extension del archivo a exportar o sobreescribir.
                                        Valor default: "json".
            -overwrite             <bool> Si es True, sobreescribira el archivo que ya existe con el mismo nombre.
                                        Valor default: True
    """

    dict_to_export = kwargs.get('dictToExport', {})

    # Definir el nombre del archivo que va ha ser exportardo
    file_name = kwargs.get('fileName', "")  # Sin la extension

    # Definir la extension del archivo a exportar
    file_extension = kwargs.get('fileExtension', "json")

    # Definir el directorio donde queremos que se guarde el archivo exportado
    file_path = kwargs.get('filePath', "")

    # Overwrite de archivos exportados (por default el archivo hara un overwrite)
    overwrite = kwargs.get('overwrite', True)

    # --------------------------------------------------------------------------
    # Input Verification
    # --------------------------------------------------------------------------
    # Dictionary to export

    if not dict_to_export:
        dict_to_export = get_nodesInfo_asDict()
    if not dict_to_export:
        cmds.warning("No values found for the dictionary to export. Process skipped")
        return

    # File information
    if not file_name or not file_path or not file_extension:
        _args = ["fileName", "filePath", "fileExtension"]
        cmds.warning("Please provide a valid input for the following arguments : {!r}".format(_args))
        return

    # Verificar que el path exista
    if not os.path.isdir(file_path):
        cmds.warning("The following path doesn't exist: {!r}".format(file_path))
        return

    # --------------------------------------------------------------------------
    # Main Process
    # --------------------------------------------------------------------------

    file_fullName = "{}.{}".format(file_name, file_extension)
    filePath_full = os.path.join(file_path, file_fullName)

    # Confirmar si existre file overwrite

    if os.path.isfile(filePath_full):
        if overwrite is False:
            cmds.warning("The following is already exists and overwrite is set up to False: {!r}".format(filePath_full))
            return

    # Usar Python's context manager para abrir el archivo

    dict_to_export = get_nodesInfo_asDict()
    with open(filePath_full, "w") as file_to_write:
        json.dump(dict_to_export, file_to_write, indent=4)

    print("# Exported data to file: {!r}".format(filePath_full))
    return dict_to_export


def load_dict(**kwargs):
    """
        -Ejecuta los valores guardados en el diccionario del archivo especificado.
        -Se espera que el diccionario tenga el siguiente formato:
                {'nombreDelNodoA':
                    {'nombreDelAttrAA':
                        {'value': 'valorAA':
                         'type' : 'typeNameAA'}
                     {'nombreDelAttrAB':
                        {'value': 'valorAB':
                         'type' : 'typeNameAB'}
                }
        -Se necesitan los siguientes argumentos:
            -fileName        <str> El nombre del archivo (sin extension) a importar.
                                    Valor default: "".
            -filePath        <str> El path hacia el archivo a importar.
                                    Valor default: "".
        -Argumentos opcionales:

            -file_extension        <str> La extension del archivo a importar.
                                        Valor default: "json".
            -prefix             <str> El prefijo del nodo a leer.
                                        Valor default: "".
    """
    # Copiamos los argumentos que vamos a usar de export_dict
    file_name = kwargs.get('fileName', "")  # Sin la extension

    file_extension = kwargs.get('fileExtension', "json")

    file_path = kwargs.get('filePath', "")

    # Agregamos nuevo argumento prefijo
    prefix = kwargs.get('prefix', "")

    # --------------------------------------------------------------------------
    # Input Verification
    # --------------------------------------------------------------------------
    # File information
    if not file_name or not file_path or not file_extension:
        _args = ["fileName", "filePath", "fileExtension"]
        cmds.warning("Please provide a valid input for the following arguments : {!r}".format(_args))
        return

    # Verificar que el path exista
    if not os.path.isdir(file_path):
        cmds.warning("The following path doesn't exist: {!r}".format(file_path))
        return

    # File validation
    file_fullName = "{}.{}".format(file_name, file_extension)
    filePath_full = os.path.join(file_path, file_fullName)
    if not os.path.isfile(filePath_full):
        cmds.warning("The following file doesn't seem to exist: {!r}".format(filePath_full))

    # --------------------------------------------------------------------------
    # Main Process
    # --------------------------------------------------------------------------
    # Usar Python's context manager para leer el archivo
    with open(filePath_full, "r") as file_to_read:
        _dict_to_read = json.load(file_to_read)

    # Ver si hay algun tipo de contenido en el archivo
    if _dict_to_read:

        # Comprobar si el contenido que hay sea tipo diccionario
        if type(_dict_to_read) == dict:
            # Verificamos el nombre de los nodos
            for eachNode in _dict_to_read:

                # Primero buscar el nodo en la escena (con prefijo, si es especificado)
                if prefix:
                    eachNode = "{}.{}".format(prefix, eachNode)
                # Comprobamso que el nodo exista en la escena
                if not cmds.objExists(eachNode):
                    cmds.warning("The following node doesn't exist in the scene: {!r}".format(eachNode))
                    # En vez de usar return y acabar el proceso, usaremos continue para que pase al siguiente nodo
                    continue

                # Iteramos en los atributos verificando que existan
                for eachAttr in _dict_to_read[eachNode].keys():
                    # Guardamos su valor en variables
                    _attr_exists = cmds.attributeQuery(eachAttr, exists=True, node=eachNode)
                    # Si el attributo existe
                    if _attr_exists:
                        val = _dict_to_read[eachNode][eachAttr]['value']
                        typ = _dict_to_read[eachNode][eachAttr]['type']

                        # Miramos que tipo de attributos son los correctos
                        # Al haber alguno de estos valores se convertiran en float
                        _floatTypes = ["double", "doubleLinear", "doubleAngle"]

                        # En el caso de que sea bool se converitra en bool
                        if typ == "bool":
                            val = bool(val)
                        elif typ in _floatTypes:
                            val = float(val)

                        # Probar si se pueden setear los valores
                        try:
                            cmds.setAttr("{}.{}".format(eachNode, eachAttr), val)
                            print("# Set {}.{} to {}".format(eachNode, eachAttr, val))
                        except RuntimeError as e:
                            print(e)
                            cmds.warning("Skipping {}...".format(eachNode))

        # Si no el contenido no es de tipo diccionario
        else:
            cmds.warning("No valid dictionary data was found in the file: {!r}".format(filePath_full))
            return

    # Si no hay contenido
    else:
        cmds.warning("No data has been found in the file: {!r}".format(filePath_full))
        return


# Export ejemplo plantilla
_nodes_info = {}
export_dict(dictToExport=_nodes_info,
            fileName='ctrlsData',
            filePath='/Users/User/Desktop/Animum/TareasWIP',
            fileExtension='json')

# Load ejemplo plantilla
load_dict(fileName='ctrlsData',
          filePath='/Users/User/Desktop/Animum/TareasWIP')