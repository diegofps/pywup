from pywup.services.system import expand_path, error, warn, info, debug, critical, readlines, colors
from pywup.services.state_machine import StateMachine
from pywup.services.clusterfile import ClusterFile
from pywup.services.context import Context
from pywup.services.ssh import BasicSSH

from multiprocessing import Process, Queue
from datetime import datetime
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

echo = lambda x: b" echo -e \"%s\"" % x.replace(b"-", b"-\b-")

ECHO_SSH_ON = echo(KEY_SSH_ON)
ECHO_SSH_OFF = echo(KEY_SSH_OFF)
ECHO_CMD_ON = echo(KEY_CMD_ON)
ECHO_CMD_OFF = b" echo -en \"\n $? %s\"" % KEY_CMD_OFF.replace(b"-", b"-\b-")


def combine_variables(variables, combination=[]):
    if len(variables) == len(combination):
        yield copy.copy(combination)
    
    else:
        var = variables[len(combination)]
        name = var.get_name()
        
        for value in var.get_values():
            combination.append([name, value])

            for tmp in combine_variables(variables, combination):
                yield tmp
            
            combination.pop()


class Msg(dict):

    def __init__(self, action, source=-1):
        self.action = action
        self.source = source
        self.data = {}
    
    def __setstate__(self, state):
        self.__dict__ = state

    def __getstate__(self):
        return self.__dict__

    def __getattr__(self, key):
        return self[key]
    
    def __setattr__(self, key, value):
        self[key] = value


class Task:

    def __init__(self, 
            experiment_name, output_dir, work_dir, experiment_idd, perm_idd, 
            run_idd, task_idd, combination, cmdline, cmd_idd):

        self.experiment_name = experiment_name
        self.experiment_idd = experiment_idd
        self.combination = combination
        self.output_dir = output_dir
        self.work_dir = work_dir
        self.perm_idd = perm_idd
        self.task_idd = task_idd
        self.assigned_to = None
        self.cmdline = cmdline
        self.run_idd = run_idd
        self.cmd_idd = cmd_idd
        self.started_at = None
        self.ended_at = None
        self.duration = None
        self.success = None
        self.output = None
        self.status = None
        self.tries = 0
    
    
    def __repr__(self):
        comb = ";".join(str(v) for v in self.combination)
        return "%d %d %d %d %s %s" % (self.experiment_idd, self.perm_idd, 
                    self.run_idd, self.task_idd, comb, self.cmdline)


class ConnectorBuilder:

    def __init__(self, connector, machine):
        self.connector = connector
        self.machine = machine

    def __call__(self):
        return self.connector(self.machine)


class VirtualConnector:
    pass


class BashConnector:
    pass


class SSHConnector:

    def __init__(self, machine):

        self.ssh = BasicSSH(machine.user, machine.ip, machine.ip)
        self.machine = machine
        self.is_alive = False

        # Opens a pseudo-terminal
        self.master, self.slave = pty.openpty()
        self.start_bash()
        
        self.credential = self.machine.credential.encode()
        self.conn_string = b" ssh -t %s '%s ; bash' ; %s\n" % (self.credential, ECHO_SSH_ON, ECHO_SSH_OFF)

        self.connect()


    def start_bash(self):
        debug("Starting bash")
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
            debug("Connection attempt:", conn_try)
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
                
                for i in range(*readlines(self.master, lines, verbose=False)):
                    line = lines[i]

                    if KEY_SSH_ON in line:
                        found_ssh_on = True
                    
                    elif KEY_SSH_OFF in line:
                        found_ssh_off = True
                
                if found_ssh_on:
                    debug("SSH connection established")
                    self.is_alive = True
                    return
                
                if found_ssh_off:
                    warn("SSH connection against %s has failed, trying again" % self.credential)
                    break

            warn("Sleeping before next try...")
            time.sleep(1)
            conn_try += 1


    def execute(self, initrc, cmds):
        if type(cmds) is not list:
            cmds = [cmds]

        lines = []
        output_start = 0
        output_end = None

        p1 = b" ; ".join(initrc)
        p2 = ECHO_CMD_ON
        p3 = b" ; ".join(cmds)
        p4 = ECHO_CMD_OFF

        cmd_str = b" %s ; %s ; %s ; %s\n" % (p1, p2, p3, p4)

        os.write(self.master, cmd_str)
        
        while True:
            if self.popen.poll() is not None:
                return False, None, None
            
            r, _, _ = select.select([self.master], [], [])

            if not self.master in r:
                warn("Unexpected file descriptor while searching for command output")
                continue

            for i in range(*readlines(self.master, lines, verbose=False)):
                line = lines[i]

                if KEY_SSH_OFF in line:
                    warn("Found KEY_SSH_OFF")
                    self.popen.kill()
                    self.is_alive = False
                    return False, None, None
                
                elif KEY_CMD_ON in line:
                    #debug("Found KEY_CMD_ON")
                    output_start = i + 1
                
                elif KEY_CMD_OFF in line and output_end is None:
                    #debug("Found KEY_CMD_OFF")
                    output_end = i
            
            if output_end is not None:
                status = lines[output_end].strip().split()[0].decode("utf-8") if output_end < len(lines) else "255"
                break

        return (status == "0"), lines[output_start:output_end], status


class Proc:

    def __init__(self, proc_idd, connection_builder, env_variables):

        self.connection_builder = connection_builder
        self.env_variables = env_variables
        self.proc_idd = proc_idd
        self.process = None
        self.queue = None


    def start(self, queue_master):
        self.queue = Queue()
        self.process = Process(target=self.run, args=(self.queue, queue_master))
        self.process.start()

    def debug(self, *args):
        debug(self.proc_idd, "|", *args)


    def run(self, queue_in, queue_master):
        try:
            conn = self.connection_builder()

            msg_out = Msg("ready", self.proc_idd)
            queue_master.put(msg_out)
            
            while True:
                msg_in = queue_in.get()

                if msg_in.action == "execute":
                    #self.debug("Starting execute")
                    success = self.execute(msg_in, conn)

                    msg_out = Msg("finished", self.proc_idd)
                    msg_out.success = success
                    queue_master.put(msg_out)

                    if not conn.is_alive:
                        conn = self.connection_builder()

                    msg_out = Msg("ready", self.proc_idd)
                    queue_master.put(msg_out)
                
                elif msg_in.action == "terminate":
                    break
                
                else:
                    warn("Unknown action:", msg_in.action)
            
            msg_out = Msg("ended", self.proc_idd)
            queue_master.put(msg_out)
        except KeyboardInterrupt:
            pass


    def execute(self, msg_in, conn):
        task = msg_in.task

        # Prepare the initrc
        variables = copy.copy(self.env_variables)
        variables["WUP_WORK_DIR"] = task.work_dir

        for name, value in task.combination:
            variables[name] = str(value)

        initrc = [b"export %s=\"%s\"" % (a.encode(), b.encode()) for a, b in variables.items()]
        initrc.insert(0, b"cd \"%s\"" % task.work_dir.encode())

        # Execute this task
        #self.debug("Calling execute on connection")
        task.started_at = datetime.now()
        task.success, task.output, task.status = conn.execute(initrc, task.cmdline.encode())
        task.ended_at = datetime.now()
        task.duration = (task.ended_at - task.started_at).total_seconds()

        # Create the task folder and clean any old .done file
        done_filepath = os.path.join(task.output_dir, ".done")
        os.makedirs(task.output_dir, exist_ok=True)
        if os.path.exists(done_filepath):
            os.remove(done_filepath)

        # Dump task info
        info = copy.copy(task.__dict__)
        info["env_variables"] = variables
        del info["output"]

        filepath = os.path.join(task.output_dir, "info.yml")
        with open(filepath, "w") as fout:
            yaml.dump(info, fout, default_flow_style=False)
        
        # Dump task output
        #self.debug("Writing task output")
        filepath = os.path.join(task.output_dir, "output.txt")
        with open(filepath, "wb") as fout:
            fout.writelines(task.output)

        if task.success:
            # Create .done file
            with open(done_filepath, 'a'):
                os.utime(done_filepath, None)

        else:
            # Write output to stdout if task has failed
            critical("Task %d has failed. Exit code: %s" % (task.task_idd, task.status))
            for line in task.output:
                os.write(sys.stdout.fileno(), line)
            critical("--- END OF FAILED OUTPUT ---")

        return task.success


class ClusterBurn(Context):

    def __init__(self, cluster, redo_tasks, tasks_filter, num_runs, output_dir, default_workdir, default_variables, experiments, no_check):

        Context.__init__(self)

        self.default_variables = default_variables
        self.output_dir = expand_path(output_dir)
        self.default_workdir = default_workdir
        self.tasks_filter = tasks_filter
        self.experiments = experiments
        self.redo_tasks = redo_tasks
        self.no_check = no_check
        self.num_runs = num_runs
        self.cluster = cluster

        os.makedirs(self.output_dir, exist_ok=True)


    def start(self):

        self.tasks = self._start_tasks()
        self._validate_signature()

        self.procs = self._start_cluster()
        self._burn()


    def _validate_signature(self):

        key = hashlib.md5()

        key.update(str(self.num_runs).encode())
        #key.update(str(self.tasks).encode())
        key.update(str(self.experiments).encode())
        key.update(str(self.default_variables).encode())

        signature = key.digest()
        other_signature = b""
        
        signature_filepath = os.path.join(self.output_dir, "experiment.sig")

        if os.path.exists(signature_filepath):
            with open(signature_filepath, "rb") as fin:
                other_signature = fin.read()

        if other_signature and other_signature != signature and not self.no_check:
            error("This output directory belongs to another experiment combination, use an empty directory (recommended) or add parameter --no-check to overwrite it")

        with open(signature_filepath, "wb") as fout:
            fout.write(signature)


    def _start_tasks(self):

        experiment_idd = -1
        perm_idd = -1
        run_idd = -1
        task_idd = -1
        tasks = []

        for e in self.experiments:
            experiment_idd += 1

            variables = e.get_variables(self.default_variables)
            work_dir = e.get_work_dir(self.default_workdir)

            for combination in combine_variables(variables):
                perm_idd += 1

                for _ in range(self.num_runs):
                    run_idd += 1

                    for cmd_idd, cmd in enumerate(e.commands):
                        task_idd += 1

                        if self.tasks_filter and not any(a<= task_idd < b for a, b in self.tasks_filter):
                            continue

                        output_dir = os.path.join(self.output_dir, "experiments", e.name, str(task_idd))

                        if not self.redo_tasks and os.path.exists(os.path.join(output_dir, ".done")):
                            continue

                        task = Task(e.name, output_dir, work_dir, experiment_idd, perm_idd, run_idd, task_idd, combination, cmd.cmdline, cmd_idd)
                        tasks.append(task)

        return tasks


    def _start_cluster(self):

        if self.cluster:
            cluster = self.clusterfile()

        else:
            cluster = ClusterFile()
            m = cluster.create_machine("local_arch", "local")
            m.hostname = "localhost"
            m.procs = os.cpu_count()

        arch_idd = -1
        machine_idd = -1
        proc_idd = -1

        result = []

        for arch_name, machines in cluster.archs.items():
            arch_idd += 1

            for machine_name, machine in machines.items():
                machine_idd += 1

                for _ in range(machine.procs):
                    proc_idd += 1

                    builder = ConnectorBuilder(SSHConnector, machine)

                    env_variables = {
                        "WUP_MACHINE_NAME": machine_name,
                        "WUP_ARCH_NAME": arch_name,

                        "WUP_MACHINE_IDD": str(machine_idd),
                        "WUP_ARCH_IDD": str(arch_idd),
                        "WUP_PROC_IDD": str(proc_idd)
                    }

                    proc = Proc(proc_idd, builder, env_variables)
                    result.append(proc)
        
        return result


    def _burn(self):
        self.queue = Queue()

        self.todo = copy.copy(self.tasks)
        self.doing = []
        self.done = []
        self.given_up = []

        self.idle = []
        self.ended = []

        len_todo = len(str(len(self.todo)))
        len_proc = len(str(len(self.procs)))
        

        # Start loop
        info("Starting %d worker(s)" % len(self.procs))
        for proc in self.procs:
            proc.start(self.queue)

        # Main loop
        try:
            info("Starting main loop")
            while self.todo or self.doing:
                msg_in = self.queue.get()

                l1 = str(len(self.todo))
                l2 = str(len(self.doing))
                l3 = str(len(self.done))
                l4 = str(len(self.given_up))

                d  = colors.gray("|%s|" % str(datetime.now()))
                l1 = colors.white(" " * (len_todo - len(l1)) + l1 + " |")
                l2 = colors.white(" " * (len_proc - len(l2)) + l2 + " |")
                l3 = colors.green(" " * (len_todo - len(l3)) + l3 + " |")
                l4 = colors.red(" " * (len_todo - len(l4)) + l4 + " |")

                msg = "%s %s %s %s %s" % (d, l1, l2, l3, l4)
                print(msg)

                #info("|MASTER| Status %d/%d/%d" % (len(self.todo), len(self.doing), len(self.done)))
                #info("|MASTER| Message %s from %d" % (msg_in.action, msg_in.source))

                if msg_in.action == "ready":
                    self._ready(msg_in)
                
                elif msg_in.action == "finished":
                    self._finished(msg_in)
                
                else:
                    warn("Unknown action:", msg_in.action)
            
            info("Completed")
        except KeyboardInterrupt:
            print("Operation interrupted")
            return

        print()

        # Ending loop
        try:
            info("Terminating child processes...")
            # Sending TERM signal
            for proc in self.procs:
                msg = Msg("terminate")
                proc.queue.put(msg)
            
            # Waiting for ENDED signal
            while len(self.procs) != len(self.ended):
                msg = self.queue.get()

                if msg.action == "ended":
                    self.ended.append(msg.source)

                    d = colors.gray("|%s|" % str(datetime.now()))

                    l1 = str(len(self.ended))
                    l2 = str(len(self.procs))

                    l1 = " " * (len_proc - len(l1)) + l1
                    l2 = " " * (len_proc - len(l2)) + l2

                    print("%s %sEnded %s / %s%s" % (d, colors.WHITE, l1, l2, colors.RESET))
                
                else:
                    #debug("Ignoring action %s from %s, execution is ending" % (msg.source, msg.action))
                    pass

            info("Terminated")
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
            warn("Giving up on task %d too many fails" % task.task_idd)
            self.given_up.append(task)
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
