from typing import Dict, Type
from inspect import getmembers, isclass

from SimRender.sofa.local.sofa_objects.base import Base
from SimRender.sofa.local.sofa_objects import meshes


SOFA_OBJECTS: Dict[str, Type[Base]] = {}
for (name, cls) in getmembers(meshes, isclass):
    if name != 'Mesh':
        SOFA_OBJECTS[name] = cls
