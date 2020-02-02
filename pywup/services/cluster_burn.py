from pywup.services.system import expand_path, error, warn, info, readlines
from pywup.services.state_machine import StateMachine
from pywup.services.context import Context
from multiprocessing import Process, Queue
from subprocess import Popen


import hashlib
import select
import shlex
import uuid
import copy
import time
import yaml
import pty
import sys
import os

# Print a signature after entering ssh and after disconnecting
# ssh -t wup@172.17.0.3 "echo 12345 ; bash" ; echo '54321'

# Print output code of last command
# echo $?

KEY_SSH_ON = b'74ffc7c4-a6ad-4315-94cb-59d045a230c0'
KEY_SSH_OFF = b'93dfc971-fa64-4beb-a24e-d8874738b9ca'
KEY_CMD_ON = b'15e6896c-3ea7-42a0-aa32-23e2ab3c0e12'
KEY_CMD_OFF = b'e04a4348-8092-46a6-8e0c-d30d10c86fb3'
KEY_OUTPUT_CODE = b'2a25b3bf-efd5-4d38-81dd-1065c683ec85'

echo = lambda x: b"echo -e \"%s\"" % x.replace(b"-", b"-\b-")

ECHO_SSH_ON = echo(KEY_SSH_ON)
ECHO_SSH_OFF = echo(KEY_SSH_OFF)
ECHO_CMD_ON = echo(KEY_CMD_ON)
ECHO_CMD_OFF = b"echo -e \"\n$? %s\"" % KEY_CMD_OFF.replace(b"-", b"-\b-")


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


class Msg:

    def __init__(self, action, source=-1):
        self.action = action
        self.source = source
        self.data = {}
    
    def __getattr__(self, key):
        return self.data[key]
    
    def __setattr__(self, key, value):
        self.data[key] = value


class Task:

    def __init__(self, experiment_idd, perm_idd, run_idd, cmd_idd, combination, cmdline):

        self.experiment_idd = experiment_idd
        self.perm_idd = perm_idd
        self.run_idd = run_idd
        self.cmd_idd = cmd_idd
        self.combination = combination
        self.cmdline = cmdline
        self.assigned_to = None
        self.tries = 0
    
    
    def __str__(self):
        comb = ";".join(str(v) for v in self.combination)
        return "%d %d %d %d %s %s" % (self.experiment_idd, self.perm_idd, self.run_idd, self.cmd_idd, comb, self.cmdline)


class DaemonConnector:
    pass


class SSHConnector:
    pass


class SSHTunnelConnector:

    def __init__(self, machine, arch_name, machine_name, arch_idd, machine_idd, global_idd, proc_idd):

        self.machine_name = machine_name
        self.machine_idd = machine_idd
        self.global_idd = global_idd
        self.arch_name = arch_name
        self.arch_idd = arch_idd
        self.proc_idd = proc_idd
        self.machine = machine

        # Opens a pseudo-terminal
        self.master, self.slave = pty.openpty()
        self.start_bash()
        
        self.credential = self.machine.credential.encode()
        self.conn_string = b"ssh -t %s '%s ; bash' ; %s\n" % (self.credential, ECHO_SSH_ON, ECHO_SSH_OFF)

        self.connect()


    def start_bash(self):
        info("Starting bash")
        self.popen = Popen(
                shlex.shlex("bash"),
                preexec_fn=os.setsid,
                stdin=self.slave,
                stdout=self.slave,
                stderr=self.slave,
                universal_newlines=True)


    def connect(self):
        conn_try = 1

        while True:
            print("Connection attempt:", conn_try)
            os.write(self.master, self.conn_string)
            found_ssh_off = False
            found_ssh_on = False
            lines = []

            while True:
                if self.popen.poll() is not None:
                    warn("Bash has died, starting it again")
                    self.start_bash()
                
                r, _, _ = select.select([self.master], [], [])

                if not self.master in r:
                    warn("Unexpected file descriptor while connecting")
                    continue
                
                for i in range(*readlines(self.master, lines, True)):
                    line = lines[i]

                    if KEY_SSH_ON in line:
                        found_ssh_on = True
                    
                    elif KEY_SSH_OFF in line:
                        found_ssh_off = True
                
                if found_ssh_on:
                    info("SSH connection established")
                    return
                
                if found_ssh_off:
                    warn("SSH connection has failed, trying again")
                    break

            info("Sleeping before next try...")
            time.sleep(5)
            conn_try += 1


    def execute(self, cmds, variables):

        if type(cmds) is not list:
            cmds = [cmds]
        
        def add_variable(name, value):
            if name not in variables:
                variables[name] = value
        
        add_variable("WUP_MACHINE_NAME", self.machine_name)
        add_variable("WUP_MACHINE_IDD", self.machine_idd)
        add_variable("WUP_GLOBAL_IDD", self.global_idd)
        add_variable("WUP_ARCH_NAME", self.arch_name)
        add_variable("WUP_ARCH_IDD", self.arch_idd)
        add_variable("WUP_PROC_IDD", self.proc_idd)

        lines = []
        output_start = 0
        output_end = None
        variables = [b"%s=\"%s\"" % (a.encode(), b.encode()) for a,b in variables]
        cmd_str = b"%s ; %s ; %s ; %s\n" % (b" ; ".join(variables), ECHO_CMD_ON, b" ; ".join(cmds), ECHO_CMD_OFF)

        os.write(self.master, cmd_str)
        
        while True:
            if self.popen.poll() is not None:
                return False, None, None
            
            r, _, _ = select.select([self.master], [], [])

            if not self.master in r:
                warn("Unexpected file descriptor while searching for command output")
                continue

            for i in range(*readlines(self.master, lines, True)):
                line = lines[i]

                if KEY_SSH_OFF in line:
                    self.popen.kill()
                    return False, None, None
                
                elif KEY_CMD_ON in line:
                    output_start = i + 1
                
                elif KEY_CMD_OFF in line and output_end is None:
                    output_end = i
            
            if output_end is not None:
                status = lines[output_end].split()[0] if output_end < len(lines) else "255"
                break

        if status == "0":
            return True, lines[output_start:output_end], status
        else:
            return False, lines[output_start:output_end], status


class Proc:

    def __init__(self, connection_builder, proc_idd, output_folder):
        self.connection_builder = connection_builder
        self.output_folder = output_folder
        self.proc_idd = proc_idd


    def start(self, queue_master):
        self.queue = Queue()

        p = Process(target=self.run, args=(self.queue, queue_master))
        p.start()


    def run(self, queue_in, queue_master):
        
        conn = self.connection_builder()

        msg_out = Msg("ready", self.proc_idd)
        queue_master.put(msg_out)
        
        while True:
            msg_in = queue_in.get()

            if msg_in.action == "execute":
                success = self.execute(msg_in, conn)

                msg_out = Msg("finished", self.proc_idd)
                msg_out.success = success
                queue_master.put(msg_out)

                if not success:
                    conn = self.connection_builder()

                msg_out = Msg("ready", self.proc_idd)
                queue_master.put(msg_out)
            
            elif msg_in.action == "terminate":
                break
            
            else:
                warn("Unknown action:", msg_in.action)
        
        msg_out = Msg("ended", self.proc_idd)
        queue_master.put(msg_out)


    def execute(self, msg_in, conn):
        task = msg_in.task

        variables = {name:value for name, value in task.combination}
        cmd = task.cmdline

        # Execute this task
        success, output, status = conn.execute(cmd, variables)

        # Create the task folder
        folderpath = os.path.join(self.output_folder, "tasks", str(task.cmd_idd))
        os.makedirs(folderpath)

        # Dump task info
        filepath = os.path.join(folderpath, "task.yml")
        with open(filepath, "w") as fout:
            yaml.dump(data, fout, default_flow_style=False)
        
        # Dump task output
        filepath = os.path.join(folderpath, "task.output")
        with open(filepath, "w") as fout:
            fout.writelines(output)
        
        return success


class ClusterBurn(Context):

    def __init__(self, num_runs, output_dir, default_workdir, default_variables, experiments):

        Context.__init__(self)

        self.default_variables = default_variables
        self.output_dir = expand_path(output_dir)
        self.default_workdir = default_workdir
        self.experiments = experiments
        self.num_runs = num_runs

        os.makedirs(self.output_dir, exist_ok=True)


    def start(self):

        cluster = self.clusterfile()

        self.tasks = self._start_tasks()
        self._validate_signature()

        self.procs = self._start_cluster(cluster)
        self._burn()


    def _validate_signature(self):

        key = hashlib.md5()

        key.update(str(self.num_runs))
        key.update(str(self.tasks))

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
        arch_idd = 0
        machine_idd = 0
        global_idd = 0
        procs = []

        for arch_name, machines in cluster.archs.items():
            arch_idd += 1

            for machine_name, machine in machines.items():
                machine_idd += 1

                for proc_idd in range(machine.procs):
                    builder = lambda: SSHTunnelConnector(machine, arch_name, machine_name, arch_idd, machine_idd, global_idd, proc_idd)
                    proc = Proc(builder, proc_idd)
                    procs.append(proc)
                    global_idd += 1
        
        return procs


    def _burn(self):
        self.queue = Queue()

        self.todo = copy.copy(self.tasks)
        self.doing = []
        self.done = []

        self.idle = []
        self.ended = []


        # Start loop
        print("Starting workers")
        for proc in self.procs:
            proc.start(self.queue)


        # Main loop
        try:
            print("Waiting for workers to start delegating tasks")
            
            while self.todo or self.doing:
                msg_in = self.queue.get()

                print()
                print("|MASTER| Status %d/%d/%d" % (len(self.todo), len(self.doing), len(self.done)))
                print("|MASTER| Message %s from %d" % (msg_in.action, msg_in.source))

                if msg_in.action == "ready":
                    self._ready(msg_in)
                
                elif msg_in.action == "finished":
                    self._finished(msg_in)
                
                else:
                    warn("Unknown action:", msg_in.action)
            
            print("Completed")
        except KeyboardInterrupt:
            print("Operation interrupted")
            return


        # Ending loop
        try:
            print("Terminating child processes...")
            # Sending TERM signal
            for proc in self.procs:
                msg = Msg("terminate")
                proc.queue.put(msg)
            
            # Waiting for ENDED signal
            while len(self.procs) != len(self.ended):
                print("Ended %d/%d" % (len(self.procs), len(self.ended)))
                msg = self.queue.get()

                if msg.action == "ended":
                    info("Worker %d has ended" % msg.source)
                    self.ended.append(msg.source)
                
                else:
                    info("Ignoring action, terminating execution:", msg.action)

            print("Completed")
        except KeyboardInterrupt:
            print("Operation interrupted")
            return


    def _ready(self, msg_in):
        if self.todo:
            msg_out = Msg("execute")
            msg_out.task = self.todo.pop()
            msg_out.task.assigned_to = msg_in.source
            msg_out.task.tries += 1

            self.doing.append(msg_out.task)
            self.procs[msg_in.source].queue.put(msg_out)
        
        else:
            self.idle.append(msg_in.source)


    def _finished(self, msg_in):
        for i, x in enumerate(self.doing):
            if x.assigned_to == msg_in.source:
                break
        
        if i == len(self.doing):
            warn("Received finished msg but the task was not found inside doing")
            return
        
        task = self.doing[i]
        del self.doing[i]

        if msg_in.success:
            self.done.append(task)
            return

        if task.tries >= 3:
            warn("Giving up on task %d too many fails" % task.cmd_idd)
            return
        
        if not self.idle:
            self.todo.append(task)
            return

        target = self.idle.pop()

        msg_out = Msg("execute")
        msg_out.task = task
        msg_out.task.assigned_to = target
        msg_out.task.tries += 1

        self.procs[target].queue.put(msg_out)
