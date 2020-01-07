from pywup.services.context import Context

class Cluster:

    def __init__(self):
        self.c = Context()

    
    def new(self, args):
        clustername = args.pop_parameter()
        qtt = int(args.pop_parameter())
        outfile = args.pop_parameter()

        project, tag = lookup_env(image)
        variables, templates = parse_env(tag, "cluster create")

        volumes = "-v " + " -v ".join(templates["VOLUMES"]) if templates["VOLUMES"] else ""
        base = get_image_name(project, tag)

        containers = get_containers_in_cluster(clustername)
        if containers:
            error("A cluster with this name already exists, remove it first")

        # Build the tasks
        tasks = []
        for i in range(qtt):
            cont_name = get_container_name(project, tag, clustername, i, qtt)
            tasks.append(CreateTask(cont_name, volumes, base))

        # Run in parallel
        print("Creating cluster...")
        jobs = cpu_count()
        result = []

        with Pool(jobs) as p:
            for status in tqdm.tqdm(p.imap(parallel_do_new, tasks), total=len(tasks)):
                result.append(status)
        
        if sum(result) != 0:
            error("Cluster creation has failed, check the output for details")
        
        cluster = {
            "local_arch": {
                "m" + str(i) : {
                    "tags": ["fakecluster"],
                    "host": "unknown",
                    "user": "unknown",
                    "procs": 1
                } for i in range(qtt)
            }
        }

        with open(outfile, "w") as fout:
            yaml.dump(cluster)
    

    def rm(self):
        pass
    

    def start(self):
        pass
    

    def stop(self):
        pass
    

    def open(self):
        pass
    

    def ls(self):
        pass
    