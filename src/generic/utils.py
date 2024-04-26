
def flat_mesh_cells(cells):

    # Flat the cell connectivity to a 1D array with format [nid1, id0 ... idn, nid2, id0 ... idm, ...]
    flat_cells = []
    for c in cells:
        flat_cells += [len(c), *c]
    return flat_cells


def get_mesh_cells(flat_cells):

    cells = []
    i = 0
    if len(flat_cells) > 0:
        while True:
            cells.append([flat_cells[i + k] for k in range(1, flat_cells[i] + 1)])
            i += flat_cells[i] + 1
            if i >= len(flat_cells):
                break
    return cells


def fix_memory_leak() -> None:
    """Based on https://github.com/python/cpython/issues/82300#issuecomment-1093841376"""

    from multiprocessing import resource_tracker

    def fix_register(name, rtype):
        if rtype == 'shared_memory':
            return
        return resource_tracker._resource_tracker.register(self, name, rtype)

    resource_tracker.register = fix_register

    def fix_unregister(name, rtype):
        if rtype == 'share_memory':
            return
        return resource_tracker._resource_tracker.unregister(self, name, rtype)

    resource_tracker.unregister = fix_unregister

    if 'shared_memory' in resource_tracker._CLEANUP_FUNCS:
        del resource_tracker._CLEANUP_FUNCS['shared_memory']
