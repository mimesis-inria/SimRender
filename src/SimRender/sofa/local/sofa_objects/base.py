from typing import Dict, Any
import Sofa


class Object:

    def __init__(self, sofa_object: Sofa.Core.Object):

        self.sofa_object: Sofa.Core.Object = sofa_object
        self.sofa_node: Sofa.Core.Node = sofa_object.getContext()
        self.object_type = ''
        self.display_model = ''

    def create(self) -> Dict[str, Any]:
        return {}

    def update(self) -> Dict[str, Any]:
        return {}
