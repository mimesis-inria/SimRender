from typing import Dict, Type
from inspect import getmembers, isclass

from SimRender.sofa.local.sofa_objects.base import Object
from SimRender.sofa.local.sofa_objects import meshes, points, arrows


def collection() -> Dict[str, Type[Object]]:

    objects = {}
    for (name, cls) in getmembers(meshes, isclass) + getmembers(points, isclass) + getmembers(arrows, isclass):
        if name not in ['Mesh', 'Points', 'Arrows', 'Object', 'Any']:
            objects[name] = cls
    return objects
