from typing import Dict, Type
from inspect import getmembers, isclass

from SimRender.sofa.local.sofa_objects.base import Base
from SimRender.sofa.local.sofa_objects import meshes, points, arrows


SOFA_OBJECTS: Dict[str, Type[Base]] = {}
for (name, cls) in getmembers(meshes, isclass) + getmembers(points, isclass) + getmembers(arrows, isclass):
    if name not in ['Mesh', 'Points', 'Arrows']:
        SOFA_OBJECTS[name] = cls
