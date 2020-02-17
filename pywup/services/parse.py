from glob import glob

import yaml
import csv
import os


class Parse:

    def __init__(self, input_folder, output_file, default_patterns, experiments):
        self.default_patterns = default_patterns
        self.input_folder = input_folder
        self.experiments = experiments
        self.output_file = output_file


    def start(self):
        header = self.validate_headers()
        experiments = glob(os.path.join(self.input_folder, "experiments", "*"))

        with open(self.output_file, "w") as fout:
            writer = csv.writer(fout, delimiter=";")

            for experiment in experiments:
                tasks = glob(os.path.join(experiment, "*"))

                for task in tasks:
                    info = os.path.join(task, "info.yml")
                    output = os.path.join(task, "output.txt")

                    with open(info, "r") as fin:
                        data = yaml.load(fin, Loader=yaml.FullLoader)
                    
                    import pdb; pdb.set_trace()

                    writer.writerow([2,3,4])

    def validate_headers(self):
        return ["a", "b", "c"]
