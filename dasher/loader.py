import imp
import os

PLUGINFOLDER = os.path.join(os.path.dirname(__file__), 'modules/')
INIT = '__init__'

def get_plugins():
    '''
    Loads modules placed in the modules/ directory
    '''
    plugins = []
    possible_plugins = os.listdir(PLUGINFOLDER)
    for i in possible_plugins:
        if i.endswith('.py') and INIT not in i:
            mod = os.path.splitext(i)[0]
            info = imp.find_module(mod, [PLUGINFOLDER])
            plugins.append({'name': i, 'info': info})
    return plugins


def load_plugin(plugin):
    return imp.load_module(plugin['name'], *plugin['info'])

