from typing import Dict, List, Any
from socket import socket
from multiprocessing.shared_memory import SharedMemory
from numpy import array, ndarray


class Memory:

    def __init__(self, object_type: str, data: Dict[str, Any]):
        """
        This class create and update the shared arrays for each data field of a visual object.

        :param object_type: Object type (mesh, points...).
        :param data: Object data (positions, color...).
        """

        # Create the shared memories container
        self.__buffers: Dict[str, List[SharedMemory]] = {}

        # Create the shared array containers for data and dirty flags
        self.__data: Dict[str, ndarray] = {}
        self.__dirty: Dict[str, ndarray] = {}

        # Visual object type (shared with the visualization process)
        self.__object_type = object_type

        # Create a shared memory buffer and a shared array for each data field
        for key, value in data.items():

            # Convert data to array
            value = value if isinstance(value, ndarray) else array(value)
            # if not isinstance(value, ndarray):
            #     try:
            #         value = array(value)
            #     except ValueError:
            #         value = array(value, dtype=object)

            # Dirty flag template
            dirty = array(0, dtype=bool)

            # Create the shared memories buffers for the data field and the associated dirty flag
            value_sm = SharedMemory(create=True, size=value.nbytes)
            dirty_sm = SharedMemory(create=True, size=dirty.nbytes, name=f'{value_sm.name}_dirty')
            self.__buffers[key] = [value_sm, dirty_sm]

            # Create the shared arrays for the data field and the associated dirty flag
            self.__data[key] = ndarray(shape=value.shape, dtype=value.dtype, buffer=value_sm.buf)
            self.__data[key][...] = value[...]
            self.__dirty[key] = ndarray(shape=dirty.shape, dtype=dirty.dtype, buffer=dirty_sm.buf)
            self.__dirty[key][...] = dirty[...]

    def connect(self, remote: socket) -> None:
        """
        Send each shared memory information to the visualization process.

        :param remote: Remote socket to communicate with.
        """

        # Send the object type
        object_type = self.__object_type.encode(encoding='utf-8')
        remote.send(len(object_type).to_bytes(length=2, byteorder='big'))
        remote.send(object_type)

        # Send the number of data fields, then information about each field shared array
        remote.send(len(self.__data).to_bytes(length=2, byteorder='big'))
        for key in self.__data.keys():

            # Send the shared memory name
            sm_name = self.__buffers[key][0].name.encode(encoding='utf-8')
            remote.send(len(sm_name).to_bytes(length=2, byteorder='big'))
            remote.send(sm_name)

            # Send the data field name
            field_name = key.encode('utf-8')
            remote.send(len(field_name).to_bytes(length=2, byteorder='big'))
            remote.send(field_name)

            # Send the data shape
            shape = array(self.__data[key].shape, dtype=float)
            remote.send(shape.nbytes.to_bytes(length=2, byteorder='big'))
            remote.send(shape.tobytes())

            # Send the data type
            dtype = self.__data[key].dtype.str.encode(encoding='utf-8')
            remote.send(len(dtype).to_bytes(length=2, byteorder='big'))
            remote.send(dtype)

    def update(self, data: Dict[str, Any]) -> None:
        """
        Update the shared arrays values.

        :param data: New object data (positions, color...).
        """

        # Turn all the dirty flags to False
        for key in self.__dirty.keys():
            self.__dirty[key][...] = False

        # Update each data field
        for key, value in data.items():
            if value is not None:

                # Convert data to array
                value = value if isinstance(value, ndarray) else array(value)

                # Update the shared array
                self.__data[key][...] = value[...]

                # Turn the associated dirty flag to True
                self.__dirty[key][...] = True

    def close(self) -> None:
        """
        Close every shared memories.
        """

        # Close each data/dirty shared memory pair
        for buffers in self.__buffers.values():
            buffers[0].close()
            buffers[0].unlink()
            buffers[1].close()
            buffers[1].unlink()
