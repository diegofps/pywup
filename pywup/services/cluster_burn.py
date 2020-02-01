from pywup.services.system import expand_path, error
from pywup.services.context import Context
from multiprocessing import Pool

import hashlib
import uuid
import copy
import os

# Print a signature after entering ssh and after disconnecting
# ssh -t wup@172.17.0.3 "echo 12345 ; bash" ; echo '54321'

# Print output code of last command
# echo $?

def combine_variables(variables, combination=[]):
    if len(variables) == len(combination):
        yield copy.copy(combination)
    
    else:
        var = variables[len(combination)]
        name = var.get_name()
        
        for value in var.get_values():
            combination.append((name, value))

            for tmp in combine_variables(variables, combination):
                yield tmp
            
            combination.pop()


class Task:

    def __init__(self, experiment_idd, perm_idd, run_idd, cmd_idd, combination, cmdline):

        self.experiment_idd = experiment_idd
        self.perm_idd = perm_idd
        self.run_idd = run_idd
        self.cmd_idd = cmd_idd
        self.combination = combination
        self.cmdline = cmdline
    
    def __str__(self):
        comb = ";".join(str(v) for v in self.combination)
        return "%d %d %d %d %s %s" % (self.experiment_idd, self.perm_idd, self.run_idd, self.cmd_idd, comb, self.cmdline)


class Proc:

    def __init__(self, machine, global_idd, local_idd):
        self.global_idd = global_idd
        self.local_idd = local_idd
        self.machine = machine


class ClusterBurn(Context):

    def __init__(self, num_runs, output_dir, default_workdir, default_variables, experiments):

        Context.__init__(self)

        self.default_variables = default_variables
        self.output_dir = expand_path(output_dir)
        self.default_workdir = default_workdir
        self.experiments = experiments
        self.num_runs = num_runs

        self.key_ssh_on, self.echo_ssh_on = self._gen_key()
        self.key_ssh_off, self.echo_ssh_off = self._gen_key()

        self.key_cmd_on, self.echo_cmd_on = self._gen_key()
        self.key_cmd_off, self.echo_cmd_off = self._gen_key()

        os.makedirs(self.output_dir, exist_ok=True)


    def start(self):

        cluster = self.clusterfile()

        tasks = self._start_tasks()
        self._validate_signature(tasks)

        procs = self._start_cluster(cluster)
        self._burn(tasks, procs)


    def _gen_key(self):
        
        key = str(uuid.uuid4())
        echo = "echo " + key.replace("-", "-\b-")

        return key, echo
    

    def _validate_signature(self, tasks):

        key = hashlib.md5()

        key.update(str(self.num_runs))
        key.update(str(tasks))

        signature = key.digest()
        
        signature_filepath = os.path.join(self.output_dir, "experiment.sig")

        if os.path.exists(signature_filepath):
            with open(signature_filepath) as fin:
                data = fin.readline().strip()
                if data != signature:
                    error("This output directory belongs to another experiment combination, use an empty directory or clean it")
        else:
            with open(signature_filepath, "w") as fout:
                fout.write(signature + "\n")


    def _start_tasks(self):

        experiment_idd = -1
        perm_idd = -1
        run_idd = -1
        cmd_idd = -1
        tasks = []

        for e in self.experiments:
            experiment_idd += 1
            variables = e.get_variables(self.default_variables)

            for combination in combine_variables(variables):
                perm_idd += 1

                for _ in range(self.num_runs):
                    run_idd += 1

                    for cmdline in e.commands:
                        cmd_idd += 1

                        task = Task(experiment_idd, perm_idd, run_idd, cmd_idd, combination, cmdline)
                        tasks.append(task)
        
        return tasks
    

    def _start_cluster(self, cluster):
        procs = []
        global_idd = 0

        for m in cluster.all_machines():
            for machine_idd in range(m.procs):
                p = Proc(m, global_idd, machine_idd)
                procs.append(p)
                global_idd += 1
        
        return procs


    def _burn(self, tasks, procs):

        pool = Pool(len(procs))
