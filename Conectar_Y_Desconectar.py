"""
Detalles:
    - Herramienta para conectar o desconectar los nodos especificados, en base a un archivo externo especificado
    - El script espera que no existan nodos con los mismos nombres en la escena, a menos que tengan un prefix.
    - El rig DEBE encontrarse en su posicion inicial a la hora de conectar y desconectar, para evitar desfases.
    - Ejemplos de uso:
        # Crear un template en base a la seleccion
        rigCon = RigConnector('C:/Users/user7Desktop'. 'templates.rigConnections')
        rigCon.export_template()

        # Conectar un rig
        rigCon = RigConnector('C:/Users/user7Desktop'. 'templates.rigConnections')
        rigCon.connect()

        # Desconectar un rig
        rigCon = RigConnector('C:/Users/user7Desktop'. 'templates.rigConnections')
        rigCon.disconnect()

Autor:
    - Sofia Ares Fernandez
Fecha de actualizacion:
    13/02/2024 by Sofia:
        -Create script
        -Testing and changing spelling mistake
Entorno:
    -Python 2023.2.4
    -Autodesk Maya 2023
    -Windows
"""

import os
from datetime import datetime
import json
import maya.cmds as cmds

class RigConnector:
    def __init__(self, file_path, file_name):
        # Verificamos el path
        self.filePath = file_path
        if not os.path.exists(self.filePath):
            raise OSError("The path {!r} was not found.".format(self.filePath))

        # Verificamos que el archivo existe
        self.fileName = file_name
        # Verificamos el path completo del archivo incluyendo el directorio
        self.full_filePath = os.path.join(self.filePath, self.fileName)
        self.valid_fullFilePath = False
        self.msg_invalid_file = ("This file {!r} doesn't exist. Only export method can ".format(self.full_filePath) +
                                 "be used until an existing file is set.")

        # Variable que guardara la informacion de los archivos externos
        self.data = {}

        # Analizar si el full_filePath existe
        if not os.path.exists(self.full_filePath):
            # Si no existe
            print(self.msg_invalid_file)
            self.valid_fullFilePath = False

        # Si existe
        else:
            self.valid_fullFilePath = True
            self.get_data()

# Exportar el archivo template

    def export_template(self, **kwargs):
        """
        - En base a la seleccion, exporta una base de datos template en el directorio especificado.
        - Este metodo espera que no hayan otros nodos con el mismo nombre en la escena,
            y su uso en esas condiciones puede ser inestable.
        - Este metodo unicamente se basa en crear un template simple, por lo que el prefix adquirido sera unicamente
        el del primer objeto de la seleccion y no es detallado para el resto de los objetos.
        - Si el archivo ya existe, lo creara con otro nombre.
        - Si el argumetno 'update' es True, los valores de la clase se actualizaran en base a los input
            del path y de este metodo
        - El formato necesario para el diccionario de data sera:
            {'prefix' : <str>,
                'database':
                    {<str targetNodeName>:
                        {'source': <str>,
                        'connectMethod': <str>,
                        'disconnectMethod': <str>,
                        'applyPrefix': <bool>
                    }
        }
        """
        file_name = kwargs.get('fileName', self.fileName)
        file_path = kwargs.get('filePath', self.filePath)
        update = kwargs.get('update', True)

        # Analizamos la seleccion
        _selection = cmds.ls(sl=True)

        # Si no hay seleccion
        if not _selection:
            raise ValueError("Please select at least one object for the template creation.")

        # Creamos el template donde guardamos el prefijo de la data
        _data = {}

        # Conseguimos el prefijo de la seleccion
        _sel = _selection[0]  # Por ejemplo: rig01:root
        _symb = ':'
        _hasPrefix = False # Por defecto es False

        if _symb in _sel:  # Si existe ":" en el nombre
            _split = _sel.split(_symb)  # Divide el nombre en: ["rig01", "root"]
            _data['prefix'] = _split[0]  # El primer elemento sera el prefijo: "rig01"

            # Si se encuentra ':'
            _hasPrefix = True

        # Guardamos la data
        _data['database'] = {}
        for eachNode in _selection:

            # Filtramos el prefijo, si existe
            if _symb in eachNode:
                eachNode = eachNode.split(_symb)[-1]

            _data['database'][eachNode] = {'source': '',
                                           'connectMethod': '',
                                           'disconnectMethod': '',
                                           'applyPrefix': _hasPrefix}

        # Verificamos el path
        if not os.path.exists(file_path):
            raise OSError("The path {!r} was not found.".format(file_path))

        # Verificamos el fichero
        _fullFilePath = os.path.join(file_path, file_name)

        # Si el fichero existe, creamos un nuevo fichero con un nuevo nombre que incluye el timepo
        if os.path.exists(_fullFilePath):

            # Añadimos un sufijo con el timepo actual
            # si el nombre tiene multiples "." el resultado puede ser inesperado
            # recomendacion de que el nombre tenga un unico "."
            _now = datetime.now() # Convertimos el valor en string
            _suffix = _now.strftime("%Y%m%d_%H%M%S")  #20230213
            _raw_file_name = file_name.split('.')[0]  # Por ejemplo: myFile
            _raw_extension = file_name.split('.')[1]  # Por ejemplo: json
            _new_raw_file_name = "{}_{}".format(_raw_file_name, _suffix)  # Por ejemplo: myFile_20230213_193720
            _new_file_name = "{}.{}".format(_new_raw_file_name, _raw_extension)
            _fullFilePath = os.path.join(file_path, _new_file_name)

        # Escribimos la data en el archivo
        with open(_fullFilePath, "w") as file_to_write:
            json.dump(_data, file_to_write, indent=4)

        print("Exported successfully to: {!r}".format(_fullFilePath))

        # Update del path, si se especifica
        if update:
            self.set_file_path(filePath=file_path, fileName=file_name, silent=True)  # Para que no imprima la ultima
                                                                                    # linea de get_data()


    def set_file_path(self, **kwargs):
        """
        - Metodo para setear el path y/o file de la clase.
        """
        # Variable para silenciar los prints y que no aparezcan cada vex que se ejecute esta parte del script
        silent = kwargs.get('silent', False)

        # Verificamos el path
        self.filePath = kwargs.get('filePath', self.filePath)

        # Si el path no existe
        if not os.path.exists(self.filePath):
            raise OSError("The path {!r} was not found.".format(self.filePath))

        # Verificamos el fichero
        _fileName = kwargs.get('fileName', self.fileName)
        self.full_filePath = os.path.join(self.filePath, _fileName)

        # Verificamos si existe o no
        # Si no existe
        if not os.path.exists(self.full_filePath):
            print(self.msg_invalid_file)
            self.valid_fullFilePath = False

        # Si existe
        else:
            self.valid_fullFilePath = True
            self.get_data(silent=silent)

    def get_data(self, **kwargs):
        """
        - Intentara leer la data del archivo especificado.
        """
        # Variable para silenciar los prints y que no aparezcan cada vex que se ejecute esta parte del script
        silent = kwargs.get('silent', False)

        # Verificamos si valid.fullFilePath es True
        if not self.valid_fullFilePath:
            print(self.msg_invalid_file)
            return

        # Usar Python's context manager para leer el archivo
        with open(self.full_filePath, "r") as file_to_read:
            self.data = json.load(file_to_read)

        if not silent:
            print("File read properly: {!r}".format(self.full_filePath))

    @staticmethod
    def con_typeA(sourceNode, destinationNode):
        """
        - Metodo de conexion.
        - La conexion se realizara de la siguiente manera:
            01) Parent Constraint del objeto source al objeto destinado.
            02) Conexion directa de los atributos scale.
        """
        # Aplicamos parentConstraint
        cmds.parentConstraint(sourceNode, destinationNode, mo=True, weight=True)
        # Aplicamos parentConstraint
        for axis in "xyz":
            cmds.connectAttr("{}.s{}".format(sourceNode, axis),  # scaleX == sx
                             "{}.s{}".format(destinationNode, axis))

        print("Connected successfully with Type A: {!r} -> {!r}".format(sourceNode, destinationNode))

    @staticmethod
    def con_typeB(sourceNode, destinationNode):
        """
        - Metodo de conexion.
        - La conexion se realizara de la siguiente manera:
            01) Orient Constraint del objeto source al objeto destinado.
            02) Conexion directa de los atributos scale.
        """
        # Aplicamos parentConstraint
        cmds.orientConstraint(sourceNode, destinationNode, mo=True, weight=True)
        # Aplicamos parentConstraint
        for axis in "xyz":
            cmds.connectAttr("{}.s{}".format(sourceNode, axis),  # scaleX == sx
                             "{}.s{}".format(destinationNode, axis))

        print("Connected successfully with Type B: {!r} -> {!r}".format(sourceNode, destinationNode))

    @staticmethod
    def con_typeC(sourceNode, destinationNode):
        """
        - Metodo de conexion.
        - La conexion se realizara de la siguiente manera:
            01) Scale Constraint del objeto source al objeto destinado.
            02) Conexion directa de los atributos scale.
        """
        # Aplicamos parentConstraint
        cmds.scaleConstraint(sourceNode, destinationNode, mo=True, weight=True)
        # Aplicamos parentConstraint
        for axis in "xyz":
            cmds.connectAttr("{}.s{}".format(sourceNode, axis),  # scaleX == sx
                             "{}.s{}".format(destinationNode, axis))

        print("Connected successfully with Type C: {!r} -> {!r}".format(sourceNode, destinationNode))

    @staticmethod
    def discon_typeA(sourceNode, destinationNode):
        """
        - Metodo de desconexion.
        - El rig DEBE estar reseteado en su posicion inicial.
        - La desconexion se realizara de la siguiente manera:
            01) Se obtiene el nodo parentContraint desde el destinationNode y se elimina.
            02) Se desconecta los atributos de scale.
        """
        # Get parentConstraint
        connection = cmds.listConnections('{}.tx'.format(destinationNode), source=True, plugs=False)

        # Confirmamos si hay conexion
        if connection :
            cmds.delete(connection)

        # Verificammos la scale de connection, y lo desconectamos si esta conectado
        for axis in "xyz":
            connection = cmds.listConnections('{}.s{}'.format(destinationNode, axis), source=True, plugs=False)

            # Si no hay conexion
            if not connection:
                continue
            # Si connection no tine el mismo nombre que nuestro sourceNode entonces continue
            if connection[0] != sourceNode:
                continue
            cmds.disconnectAttr("{}.s{}".format(sourceNode, axis),
                                "{}.s{}".format(destinationNode, axis))


    @staticmethod
    def discon_typeB(sourceNode, destinationNode):
        """
        - Metodo de desconexion.
        - El rig DEBE estar reseteado en su posicion inicial.
        - La desconexion se realizara de la siguiente manera:
            01) Se obtiene el nodo orientContraint desde el destinationNode y se elimina.
            02) Se desconecta los atributos de scale.
        """
        # Get orientConstraint
        connection = cmds.listConnections('{}.rx'.format(destinationNode), source=True, plugs=False)

        # Confirmamos si hay conexion
        if connection :
            cmds.delete(connection)

        # Verificammos la scale de connection, y lo desconectamos si esta conectado
        for axis in "xyz":
            connection = cmds.listConnections('{}.s{}'.format(destinationNode, axis), source=True, plugs=False)

            # Si no hay conexion
            if not connection:
                continue
            # Si connection no tine el mismo nombre que nuestro sourceNode entonces continue
            if connection[0] != sourceNode:
                continue
            cmds.disconnectAttr("{}.s{}".format(sourceNode, axis),
                                "{}.s{}".format(destinationNode, axis))

    @staticmethod
    def discon_typeC(sourceNode, destinationNode):
        """
        - Metodo de desconexion.
        - El rig DEBE estar reseteado en su posicion inicial.
        - La desconexion se realizara de la siguiente manera:
            01) Se obtiene el nodo scaleContraint desde el destinationNode y se elimina.
            02) Se desconecta los atributos de scale.
        """
        # Get orientConstraint
        connection = cmds.listConnections('{}.sx'.format(destinationNode), source=True, plugs=False)

        # Confirmamos si hay conexion
        if connection :
            cmds.delete(connection)

        # Verificammos la scale de connection, y lo desconectamos si esta conectado
        for axis in "xyz":
            connection = cmds.listConnections('{}.s{}'.format(destinationNode, axis), source=True, plugs=False)

            # Si no hay conexion
            if not connection:
                continue
            # Si connection no tine el mismo nombre que nuestro sourceNode entonces continue
            if connection[0] != sourceNode:
                continue
            cmds.disconnectAttr("{}.s{}".format(sourceNode, axis),
                                "{}.s{}".format(destinationNode, axis))

    def connect(self):
        """
        - En base al path y file, intentara conectar la data encontrada en ese archivo.
         """
        # Si el archivo no es valido
        if not self.valid_fullFilePath:
            print(self.msg_invalid_file)
            return

        # Refrescamos la data
        # verificamos que el full_filePath exista (por si el objeto a sido modificado o eliminado)
        if not os.path.exists(self.full_filePath):
            print(self.msg_invalid_file)

            # verificamos no existe
            self.valid_fullFilePath = False

        # Si existe
        else:
            self.valid_fullFilePath = True
            self.get_data(silent=True)

        if self.data:
            prefix = self.data.get('prefix', '')
            database = self.data.get('database', '')

            # Verificamos que exista database
            # Si existe
            if database:
                for destination in self.data['database'].keys():

                    #-------------------------------------
                    # Analizamos el prefix
                    applyPrefix = self.data['database'][destination].get('applyPrefix', False)

                    # Verificamos si existe prefix
                    if applyPrefix:

                        # Si existe prefix
                        if prefix:
                            destination = "{}:{}".format(prefix, destination)
                    # -------------------------------------
                    # Analizamos los nodos a conectar
                    if not cmds.objExists(destination):
                        print("Process skipped as the following object doesn't exist: {!r}".format(destination))
                        continue

                    # Definimos nodo Source
                    source = self.data['database'][destination].get('source', '')

                    # Si no hay source
                    if not source:
                        print("Process skipped as there is no source specified for: {!r}". format(destination))
                        continue

                    # Si existe source
                    else:
                        if applyPrefix:
                            if prefix:
                                source = "{}:{}".format(prefix, source)
                        if not cmds.objExists(source):
                            print("Process skipped as the following object doesn't exist: {!r}".format(destination))
                            continue

                    # -------------------------------------
                    # Ejecutar el metodo especifico de conexion

                    connectionMethod = self.data['database'][destination].get('connectMethod', '')
                    if not connectionMethod:
                        print("Process skipped as the following object's " +
                              "connect method was not found: {!r}".format(destination))

                    # Deribar si TypeA es igual a connectionMethos
                    if connectionMethod == 'typeA':
                        self.con_typeA(source, destination)

                    # Deribar si TypeB es igual a connectionMethos
                    if connectionMethod == 'typeB':
                        self.con_typeB(source, destination)

                    # Deribar si TypeC es igual a connectionMethos
                    if connectionMethod == 'typeC':
                        self.con_typeB(source, destination)

                    # si tubiera mas metodos de conexion
                    # elif connectionMethod == 'typeB':
                        # self.con_typeB(source, destination)

            # Si no existe database
            else:
                print("No database found to analyze.")
        else:
            print("No data found to analyze")

    def disconnect(self):
        """
         - En base al path y file, intentara desconectar la data encontrada en ese archivo.
          """
        # Si el archivo no es valido
        if not self.valid_fullFilePath:
            print(self.msg_invalid_file)
            return

        # Refrescamos la data
        # verificamos que el full_filePath exista (por si el objeto a sido modificado o eliminado)
        if not os.path.exists(self.full_filePath):
            print(self.msg_invalid_file)

            # verificamos no existe
            self.valid_fullFilePath = False

        # Si existe
        else:
            self.valid_fullFilePath = True
            self.get_data(silent=True)

        if self.data:
            prefix = self.data.get('prefix', '')
            database = self.data.get('database', '')

            # Verificamos que exista database
            # Si existe
            if database:
                for destination in self.data['database'].keys():

                    #-------------------------------------
                    # Analizamos el prefix
                    applyPrefix = self.data['database'][destination].get('applyPrefix', False)

                    # Verificamos si existe prefix
                    if applyPrefix:

                        # Si existe prefix
                        if prefix:
                            destination = "{}:{}".format(prefix, destination)
                    # -------------------------------------
                    # Analizamos los nodos a desconectar
                    if not cmds.objExists(destination):
                        print("Process skipped as the following object doesn't exist: {!r}".format(destination))
                        continue

                    # Definimos nodo Source
                    source = self.data['database'][destination].get('source', '')

                    # Si no hay source
                    if not source:
                        print("Process skipped as there is no source specified for: {!r}".format(destination))
                        continue

                    # Si existe source
                    else:
                        if applyPrefix:
                            if prefix:
                                source = "{}:{}".format(prefix, source)

                        if not cmds.objExists(source):
                            print("Process skipped as the following object doesn't exist: {!r}".format(destination))
                            continue

                    # -------------------------------------
                    # Ejecutar el metodo especifico de desconexions

                    disconnectionMethod = self.data['database'][destination].get('connectMethod', '')
                    if not disconnectionMethod:
                        print("Process skipped as the following object's " +
                              "disconnect method was not found: {!r}".format(destination))

                    # Deribar si TypeA es igual a connectionMethos
                    if disconnectionMethod == 'typeA':
                        self.discon_typeA(source, destination)

                    # Deribar si TypeB es igual a connectionMethos
                    if disconnectionMethod == 'typeB':
                        (self.discon_typeB(source, destination))

                    # Deribar si TypeC es igual a connectionMethos
                    if disconnectionMethod == 'typeC':
                            (self.discon_typeB(source, destination))

                   # si tubiera mas metodos de desconexion
                    # elif connectionMethod == 'typeB':
                        # self.con_typeB(source, destination)

           # Si no existe database
            else:
             print("No database found to analyze.")
        else:
            print("No data found to analyze")


# Codigo para poder aplicar codigo en el script editor en maya y ejecutarlo
import ConDesEsqueletoFinal as rc  # ConDesEsqueletoFinal<----  hay que cambiarlo por el nombre del fichero actual

# Crear nuestra instancia del objeto
rigCon = rc.RigConnector('C:/Users/User/Desktop/Animum/TareasWIP','templates.rigConnections') # Cambiar path al deseado

# Crear un template en base a la seleccion
rigCon.export_template()

# Conectar un rig
rigCon.connect()

# Desconectar un rig
rigCon.disconnect()