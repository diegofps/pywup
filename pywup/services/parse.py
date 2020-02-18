from pywup.services.system import expand_path, error
from glob import glob

import yaml
import csv
import os


class TaskParser:

    def __init__(self, info_filepath, patterns):

        self.patterns = patterns
        self.header_names = []
        self.header_map = {}

        # Input variables
        with open(info_filepath, "r") as fin:
            data = yaml.load(fin, Loader=yaml.FullLoader)
        
        for v in data["variables"]:
            self.add_var(v["name"])

        # Patterns
        for p in patterns:
            self.add_var(p.name)

        # Task
        for v in ["TASK_ID", "TASK_PERMID", "TASK_STARTED_AT", 
                  "TASK_ENDED_AT", "TASK_DURATION", "TASK_TRIES", 
                  "TASK_ARCH_USED", "TASK_MACHINE_USED"]:
            self.add_var(v)

        self.values = [None for _ in range(len(self.header_map))]


    def add_var(self, name):
        if name in self.header_map:
            error("Header appears multiple times:", name)
        
        self.header_names.append(name)
        self.header_map[name] = len(self.header_map)


    def write_header(self, writer):
        writer.writerow(self.header_names)


    def digest(self, task_folder, writer):
        self.clear_row()

        task_info = os.path.join(task_folder, "info.yml")
        task_output = os.path.join(task_folder, "output.txt")
        task_done = os.path.join(task_folder, ".done")

        if os.path.exists(task_done):
            self.parse_task_info(task_info)
            self.parse_task_output(task_output)
        else:
            print("Not done:", task_info)
        
        self.write_row(writer)


    def clear_row(self):
        for i in range(len(self.values)):
            self.values[i] = None


    def parse_task_info(self, task_info):
        with open(task_info, "r") as fin:
            data = yaml.load(fin, Loader=yaml.FullLoader)
        
        for v in data["combination"]:
            name = v["n"]
            value = v["v"]
            self.values[self.header_map[name]] = value

        self.values[self.header_map["TASK_ID"]] = data["task_idd"]
        self.values[self.header_map["TASK_PERMID"]] = data["perm_idd"]
        self.values[self.header_map["TASK_STARTED_AT"]] = data["started_at"]
        self.values[self.header_map["TASK_ENDED_AT"]] = data["ended_at"]
        self.values[self.header_map["TASK_DURATION"]] = data["duration"]
        self.values[self.header_map["TASK_TRIES"]] = data["tries"]
        self.values[self.header_map["TASK_ARCH_USED"]] = data["env_variables"]["WUP_ARCH_NAME"]
        self.values[self.header_map["TASK_MACHINE_USED"]] = data["env_variables"]["WUP_MACHINE_NAME"]


    def parse_task_output(self, task_output):
        for p in self.patterns:
            p.clear()

        with open(task_output, "r") as fin:
            for line in fin:
                for p in self.patterns:
                    p.check(line)
        
        for p in self.patterns:
            self.values[self.header_map[p.get_name()]] = p.get_value()


    def write_row(self, writer):
        writer.writerow(self.values)


class Parse:

    def __init__(self, input_folder, output_file, patterns, experiment):

        input_folder = expand_path(input_folder)

        self.output_file = output_file if output_file else os.path.join(input_folder, "parse.csv")
        self.input_folder = input_folder
        self.experiment = experiment
        self.patterns = patterns


    def start(self):
        exp_fp = os.path.join(self.input_folder, "experiments", self.experiment)
        exp_info_fp = os.path.join(exp_fp, "info.yml")
        exp_tasks = glob(os.path.join(exp_fp, "*"))
        task_parser = TaskParser(exp_info_fp, self.patterns)

        with open(self.output_file, "w") as fout:
            writer = csv.writer(fout, delimiter=";")
            task_parser.write_header(writer)

            for task in exp_tasks:
                if os.path.isdir(task):
                    task_parser.digest(task, writer)

