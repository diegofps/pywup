from pywup.services.burn import Experiment, ListVariable, GeometricVariable, ArithmeticVariable
from pywup.services.system import error, Params, Route, print_table, colors
from pywup.services.cluster import Cluster

import sys
import os


def template(cmd, args):

    p = Params(cmd, args)
    p.map("clustername", 1, None, "Name of the new cluster", mandatory=True)
    p.map("outputfolder", 1, ".", "Output folder to save the cluster file descriptor")

    if p.run():
        Cluster().template(p.clustername, p.outputfolder)


def ls(cmd, args):

    p = Params(cmd, args)

    if p.run():
        result = Cluster().ls()
        print_table(result)


def open(cmd, args):
    
    p = Params(cmd, args)
    p.map("clustername", 1, None, "Name of the new cluster to open", mandatory=True)

    if p.run():
        Cluster().open(p.clustername)


def exec(cmd, args):

    p = Params(cmd, args, limit_parameters=False)
    p.map("command", 1, None, "Command to be executed", mandatory=True)
    p.map("--m", 1, None, "Execute command on a single machine")

    if p.run():
        if p.__m:
            Cluster().exec_single(p.command, p.__m)
        else:
            Cluster().exec_all(p.command)


def send(cmd, args):

    p = Params(cmd, args)
    p.map("src", 1, None, "Source path to the file inside the host", mandatory=True)
    p.map("dst", 1, None, "Destination path inside the remote machines")
    p.map("--m", 1, None, "Sends the file to a single machine")

    if p.run():
        if p.__m:
            Cluster().send_single(p.__m, p.src, p.dst)
        else:
            Cluster().send_all(p.src, p.dst)


def get(cmd, args):

    p = Params(cmd, args)
    p.map("src", 1, None, "Path to the source files inside the remote machines", mandatory=True)
    p.map("dst", 1, None, "Destination folder inside the host to store the received files, each machine will have its own folder")
    p.map("--m", 1, None, "Gets the file from a single machine")

    if p.run():
        if p.__m:
            Cluster().get_single(p.__m, p.src, p.dst)
        else:
            Cluster().get_all(p.src, p.dst)


def doctor(cmd, args):

    p = Params(cmd, args)

    if p.run():
        Cluster().doctor()


def pbash(cmd, args):

    p = Params(cmd, args)
    p.map("--v", 0, None, "Prints sdtout from the first machine. Usefull when issuing interactive commands")

    if p.run():
        Cluster().pbash(p.__v)


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


def main(cmd, args):

    r = Route(args, cmd)

    r.map("template", template, "Create an empty cluster file that you can modify to represent a real cluster")
    r.map("ls", ls, "Summarizes all machines in this cluster")
    r.map("open", open, "Opens a remote machine using ssh")
    r.map("exec", exec, "Execute a command in all remote machines")
    r.map("send", send, "Sends a file or directory to all remote machines")
    r.map("get", get, "Retrieve a file or directory from the remote machines")
    r.map("doctor", doctor, "Fixes common SSH validations")
    r.map("pbash", pbash, "A really basic parallel bash")
    r.map("burn", burn, "Runs distributed experiments")
    
    r.run()
