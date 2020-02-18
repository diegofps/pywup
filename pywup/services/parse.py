from pywup.services.system import expand_path
from glob import glob

import yaml
import csv
import os


class RowParser:

    def __init__(self, einfo_fp, epatterns):
        import pdb; pdb.set_trace()
        a = 10
        pass


    def write_header(self, writer):
        pass


    def digest(self, task_info, task_output, writer):
        self.clear_row()
        self.parse_task_info(task_info)
        self.parse_task_output(task_output)
        self.write_row(writer)


    def clear_row(self):
        pass


    def parse_task_info(self, task_info):
        with open(task_info, "r") as fin:
            data = yaml.load(fin, Loader=yaml.FullLoader)


        

    def parse_task_output(self, task_output):
        with open(task_output, "r") as fin:
            for line in fin:
                pass


    def write_row(self, writer):
        writer.writerow([2,3,4])


class Parse:

    def __init__(self, input_folder, output_folder, default_patterns, experiments):
        input_folder = expand_path(input_folder)

        self.output_folder = output_folder if output_folder else os.path.join(input_folder, "parse")
        self.default_patterns = default_patterns
        self.input_folder = input_folder
        self.experiments = experiments


    def start(self):
        experiments = glob(os.path.join(self.input_folder, "experiments", "*"))

        for e in experiments:
            epatterns = e.get_patterns(self.default_patterns)
            einfo_fp = os.path.join(e, "info.yml")
            ename = os.path.basename(e)
            etasks = glob(os.path.join(e, "*"))
            eout = os.path.join(self.output_folder, ename)
            row = RowParser(einfo_fp, epatterns)

            with open(eout, "w") as fout:
                writer = csv.writer(fout, delimiter=";")
                row.write_header(writer)

                for task in etasks:
                    task_info = os.path.join(task, "info.yml")
                    task_output = os.path.join(task, "output.txt")
                    row.digest(task_info, task_output, writer)

