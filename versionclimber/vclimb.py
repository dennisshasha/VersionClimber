"""Script to run versionclimber from a configuration file."""

import sys
import os
from optparse import OptionParser

from versionclimber import liquid, liquidparser

def main():
    """This function is called by vclimb

    To obtain specific help, type::

        vclimb --help


    """

    usage = """
vclimb traverse the versions of the packages and get the optimal one.
Example

       vclimb --conf config.yaml --log vclimb.log
"""

    parser = OptionParser(usage=usage)

    parser.add_option("--conf", dest='config', default='config.yaml',
        help="YAML configuration file")
    parser.add_option("--log", dest='log_file', default='versionclimber.log',
        help="Store logging information in this file")

    (opts, args)= parser.parse_args()


    if opts.config == None:
        raise ValueError("""--conf must be provided. See help (--help)""")


    liquidparser.start_logging(opts.log_file)

    env = liquid.YAMLEnv(opts.config)
    solutions = env.run(liquidparser)

    print('\n' * 3)
    print('Solution is:')
    for sol in solutions:
        print(sol)

