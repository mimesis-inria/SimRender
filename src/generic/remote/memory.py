from typing import Optional, Dict, List, Tuple
from socket import socket
from multiprocessing.shared_memory import SharedMemory
from numpy import array, ndarray, frombuffer, dtype as np_dtype


class Memory:

    def __init__(self, remote: socket):
        """
        This class loads the shared arrays from the simulation process for each data field of a visual object.

        :param remote: Remote socket to communicate with.
        """

        # Create the shared memories container
        self.__buffers: Dict[str, List[SharedMemory]] = {}

        # Create the shared array containers for data and dirty flags
        self.__data: Dict[str, ndarray] = {}
        self.__dirty: Dict[str, ndarray] = {}

        # Receive the number of data fields, then information about each field shared array
        nb_data_fields = int.from_bytes(bytes=remote.recv(2), byteorder='big')
        for _ in range(nb_data_fields):

            # Receive the shared memory name and the data field name
            sm_name = remote.recv(int.from_bytes(bytes=remote.recv(2), byteorder='big')).decode('utf-8')
            field_name = remote.recv(int.from_bytes(bytes=remote.recv(2), byteorder='big')).decode('utf-8')

            # Receive the data shape and type
            shape = frombuffer(remote.recv(int.from_bytes(bytes=remote.recv(2),
                                                          byteorder='big'))).astype(int).reshape(-1)
            dtype = np_dtype(remote.recv(int.from_bytes(bytes=remote.recv(2), byteorder='big')).decode('utf-8'))

            # Dirty flag template
            dirty = array(False, dtype=bool)

            # Load the shared memories buffers for the data field and the associated dirty flag
            value_sm = SharedMemory(create=False, name=sm_name)
            dirty_sm = SharedMemory(create=False, name=f'{sm_name}_dirty')
            self.__buffers[field_name] = [value_sm, dirty_sm]

            # Load the shared arrays for the data field and the associated dirty flag
            self.__data[field_name] = ndarray(shape=shape, dtype=dtype, buffer=value_sm.buf)
            self.__dirty[field_name] = ndarray(shape=dirty.shape, dtype=dirty.dtype, buffer=dirty_sm.buf)

    @property
    def data(self) -> Dict[str, ndarray]:
        """
        Visual object data dictionary access.
        """

        # return self.__data.copy()
        return self.__data

    def get_data(self, field_name) -> Tuple[Optional[ndarray], Optional[ndarray]]:
        """
        Get a specific data field with the associated dirty flag.

        :param field_name: Name of the data field.
        :return: Data field, associated dirty flag
        """

        return self.__data.get(field_name, None), self.__dirty.get(field_name, None)

    def close(self) -> None:
        """
        Close every shared memories.
        """

        # Close each data/dirty shared memory pair
        for buffers in self.__buffers.values():
            buffers[0].close()
            buffers[1].close()
