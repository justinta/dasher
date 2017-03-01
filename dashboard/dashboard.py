'''
Runs the other modules to push info up to influxdb
'''

# Python libs
from __future__ import print_function, absolute_import
import time

# Dashboard
from dashboard import loader
from dashboard.helper import common


def main():
    '''
    Main function to run the things
    '''
    args = common.parseargs()

    for pl in loader.get_plugins():
        plugin = loader.load_plugin(pl)
        mod_name = plugin.__name__.strip('.py')

        if args.modules:
            for mod in args.modules.split(','):
                if mod == mod_name:
                    plugin.run(args)

        if args.module == mod_name:
            plugin.run(args)
            break
        elif args.module == 'all' and not args.modules:
            plugin.run(args)


if __name__ == '__main__':
    main()
