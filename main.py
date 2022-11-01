# coding: utf-8
"""
Usage:
    python3 main.py -i <inputpath> [-o <outputfile>] [-r <y/N>] [-v <y/N>] [-b <y/N]

Required Options:
    -i <inputpath>    The run directory of the experiment. Eventually this will be the experiment's root directory. Try to use absolute paths, for some reason this doesnt like ~ for homedirs

Optional options:
    -o <outputfile>    Prompts this program to output the gantt chart to a file instead of showing it to you via the matplotlib viewer. Be careful with this, as it can make large charts unusable
    -r <y/n>    Prompts this program to look for and utilize reservations when creating the output charts 
    -v <y/N>    verbose operation.
    -b <y/N>    Bin reservations by size

"""

from evalys.jobset import JobSet
from evalys.utils import cut_workload
from evalys.visu.legacy import (
    plot_gantt,
)
from evalys.visu.gantt import plot_gantt_df
import sys, getopt
import json
import os
from utils import *
from gantt import *
from plots import *
from datetime import datetime
from yaspin import yaspin
import pandas as pd
import matplotlib

matplotlib.use("MacOSX")  # Comment this line if you're not using macos


def main(argv):
    inputpath = ""
    outputfile = ""
    reservation = False
    verbosity = False
    binned = False
    average = False

    # Parse the arguments passed in
    try:
        opts, args = getopt.getopt(
            argv,
            "hi:o:r:v:b:a:",
            ["ipath=", "ofile=", "resv=", "verbosity=", "binned=", "average="],
        )
    except getopt.GetoptError:
        print(
            "Option error! See usage below:\npython3 main.py -i <inputpath> [-o <outputfile>] [-r <y/N>] [-v <y/N>] [-b <y/N>] [-a <y/N>]"
        )
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print(
                "Help menu:\npython3 main.py -i <inputpath> [-o <outputfile>] [-r <y/N>] [-v <y/N>] [-b <y/N] [-a <y/N>]"
            )
            sys.exit(2)
        elif opt in ("-i", "--ipath"):
            if arg == "":
                print(
                    "python3 main.py -i <inputpath> [-o <outputfile>] [-r <y/N>] [-v <y/N>] [-b <y/N] [-a <y/N>]\n Please supply an input path!"
                )
                sys.exit(2)
            else:
                inputpath = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-r", "--resv"):
            if arg.lower() == "y":
                reservation = True
        elif opt in ("-v", "--verbosity"):
            if arg.lower() == "y":
                verbosity = True
        elif opt in ("-b", "--binned"):
            if arg.lower() == "y":
                binned = True
        elif opt in ("-a", "--average"):
            if arg.lower() == "y":
                average = True

    # Parse the path of the required files.
    outJobsCSV = os.path.join(inputpath, "output", "expe-out", "out_jobs.csv")

    # If no reservations are specified, process the chart normally
    if not reservation:
        with open(outJobsCSV) as f:
            if sum(1 for line in f) > 70000:
                print(
                    "Creating gantt charts can be unreliable with files larger than 70k jobs. Are you use you want to continue? (Y/n)"
                )
                cont = input()
                if cont == "Y" or cont == "y":
                    pass
                elif cont == "n":
                    sys.exit(2)

        js = JobSet.from_csv(outJobsCSV)
        plot_gantt(js, title="Gantt chart")
        if outputfile == "":
            matplotlib.pyplot.show()
        else:
            matplotlib.pyplot.savefig(outputfile)

    elif reservation and not average:
        iterateReservations(inputpath, outputfile, outJobsCSV, verbosity, binned)

    elif reservation and average:
        chartRunningAverage(inputpath, outputfile, outJobsCSV)

    else:
        print("Incompatible options entered! Please try again")
        sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
