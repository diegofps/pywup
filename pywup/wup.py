#!/usr/bin/env python3

from pywup.services.burn import Experiment, ListVariable, GeometricVariable, ArithmeticVariable
from pywup.services.system import abort, error, WupError, Route, Params, colors
from pywup.consts import version as wup_version
from pywup.services.context import Context

from pywup import cmdtools

import sys
import os


def use(cmd, args):
    from pywup.cmdtools.use import main
    main(cmd, args)

def collect(cmd, args):
    from pywup.cmdtools.collect import main
    main(cmd, args)

def heatmap(cmd, args):
    from pywup.cmdtools.heatmap import main
    main(cmd, args)

def bars(cmd, args):
    from pywup.cmdtools.bars import main
    main(cmd, args)

def backup(cmd, args):
    from pywup.cmdtools.backup import main
    main(cmd, args)

def q(cmd, args):
    from pywup.cmdtools.q import main
    main(cmd, args)

def env(cmd, args):
    from pywup.cmdtools.env import main
    main(cmd, args)

def menv(cmd, args):
    from pywup.cmdtools.menv import main
    main(cmd, args)

def cluster(cmd, args):
    from pywup.cmdtools.cluster import main
    main(cmd, args)

def virtual(cmd, args):
    from pywup.cmdtools.virtual import main
    main(cmd, args)

def about(cmd, args):
    print(wup_version)

def burn(cmd, args):

    from pywup.services.cluster_burn import ClusterBurn

    current_experiment = None
    default_variables = []
    default_workdir = None
    output_dir = "./burn"
    redo_tasks = False
    tasks_filter = []
    experiments = []
    no_check = False
    cluster = False
    num_runs = 1

    def require_experiment():
        if current_experiment is None:
            error("You must start an experiment first: --e <EXPERIMENT_NAME>")

    while args.has_next():
        cmd = args.pop_cmd()

        if cmd == "--e":
            name = args.pop_parameter()
            current_experiment = Experiment(name)
            experiments.append(current_experiment)
        
        elif cmd == "--only":
            while args.has_parameter():
                p = args.pop_parameter().strip().split(":")
                
                if len(p) != 2:
                    a = colors.white("first:last")
                    b = colors.white(":last")
                    c = colors.white("first:")
                    d = colors.white(":")
                    error("Valid formats for --only are: %s or %s or %s or %s" % (a, b, c, d))
                
                first = int(p[0]) if p[0] else 0
                final = int(p[1]) if p[1] else sys.maxsize

                tasks_filter.append((first, final))
        
        elif cmd == "--cluster":
            cluster = True
        
        elif cmd == "--redo":
            redo_tasks = True
        
        elif cmd == "--no-check":
            no_check = True
        
        elif cmd == "--w":
            if current_experiment is None:
                default_workdir = args.pop_parameter()
            else:
                current_experiment.work_dir = args.pop_parameter()
        
        elif cmd == "--o":
            output_dir = args.pop_parameter()
        
        elif cmd == "--runs":
            num_runs = int(args.pop_parameter())
        
        elif cmd == "--c":
            require_experiment()
            cmd = args.pop_parameter()
            current_experiment.add_command(cmd)
        
        elif cmd == "--vc":
            require_experiment()
            env = args.pop_parameter()
            cmd = args.pop_parameter()
            current_experiment.add_virtual_command(env, cmd)

        elif cmd.startswith("--v"):
            if cmd == "--v":
                v = ListVariable(args)

            elif cmd == "--va":
                v = ArithmeticVariable(args)
            
            elif cmd == "--vg":
                v = GeometricVariable(args)

            else:
                error("Unknown variable type:", cmd)

            if current_experiment is None:
                if any(v.get_name() == o.get_name() for o in default_variables):
                    error("Default variable defined more than once:", v.get_name())
                else:
                    default_variables.append(v)
            else:
                current_experiment.add_variable(v)
        
        else:
            error("Unknown parameter:", cmd)
    
    ClusterBurn(cluster, redo_tasks, tasks_filter, num_runs, output_dir, default_workdir, default_variables, experiments, no_check).start()


def wup(*params):
    r = Route(sys.argv[1:], "wup")

    r.map("use", use, "Set current env, cluster or architecture files")
    r.map("collect", collect, "Run an app multiple times, variating its parameters and collecting its output attributes")
    r.map("burn", burn, "Runs distributed experiments")
    r.map("heatmap", heatmap, "Plot a heatmap image using the data collected (requires matplotlib)")
    r.map("bars", bars, "Plot bars image using the data collected (requires matplotlib)")
    r.map("backup", backup, "Backup system files into a folder synced to a cloud")
    r.map("q", q, "Run SQL in CSV files (Requires python-q-text-as-data)")
    r.map("env", env, "Manage docker environments for development and cluster deploy (wup style)")
    r.map("menv", menv, "Simulate a cluster on your local machine using docker containers and wup environments")
    r.map("cluster", cluster, "Interact with the current cluster")
    r.map("virtual", virtual, "Manage wup environments as a virtual cluster deployed on top of a real cluster")
    r.map("about", about, "Display wup info")
    
    r.run(handleError=True)


if __name__ == "__main__":
    wup()
