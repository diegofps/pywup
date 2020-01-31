from pywup.services.system import run, quote, quote_single, error, expand_path, yprint

import re
import os


def init_and_open(cont_name, bash_init):
    k = quote("".join(["source \"$HOME/.bashrc\" 2> /dev/null \n"] + bash_init))
    b = quote("bash --init-file <(echo " + k + ") || true").replace("$", "\\$")
    return run("docker exec -it " + cont_name + " bash -c " + b)


def init_and_run(cont_name, bash_init, cmd, attach=False):
    if type(cmd) is not list:
        cmd = [cmd, "exit\n"]
    else:
        cmd.append("exit\n")
    
    k = quote_single("".join(["source \"$HOME/.bashrc\" 2> /dev/null \n"] + bash_init + cmd))

    if attach:
        return run("docker exec -it " + cont_name + " bash -c " + k)
    else:
        return run("docker exec " + cont_name + " bash -c " + k)


def clean_volumes(volumes):
    volumes = [j.strip() for j in volumes]
    volumes = [j.split(":") for j in volumes if j]

    for v in volumes:
        if len(v) != 2:
            error("The only valid sintaxes for volumes are:\n\n    <SourcePath>:<DestinationPath>\n    :<DestinationPath>\n    <SourcePath>:")

    return [[expand_path(a), expand_path(b)] for a, b in volumes]


def validate_volumes(volumes, allow_missing=True):
    for src, dst in volumes:
        if src:
            if not os.path.exists(src):
                error("Missing source directory in host:", src)
            
            if not os.path.isdir(src):
                error("Source volume in host is not a directory:", src)
        
        else:
            error("Use --v to specify a source directory for destination:", dst)

        if not dst:
            error("Invalid destination directory:", dst)
    

def expand_volumes(volumes, extra_volumes):
    extra_volumes_map = {v[1]:v[0] for v in extra_volumes}

    for v in volumes:
        if v[1] in extra_volumes_map:
            v[0] = extra_volumes_map[v[1]]


def parse_volumes(volumes, extra_volumes):
    volumes = clean_volumes(volumes)
    extra_volumes = clean_volumes(extra_volumes)
    
    expand_volumes(volumes, extra_volumes)
    validate_volumes(volumes)

    return [v[0] + ":" + v[1] for v in volumes]


def build_single(cont_name, e, extra_volumes=[]):
    create_container("tmp", e.flags, e.build_volumes, extra_volumes, e.expose, e.map_ports, e.base)
    exec("tmp", e.bashrc, e.full_build, attach=True)
    
    rm_container(cont_name)
    rename_container("tmp", cont_name)


def create_container(cont_name, flags, volumes, extra_volumes, expose, map_ports, base_name):
    createCmd = "docker run -d -i --name " + cont_name

    if "privileged" in flags:
        createCmd += " --privileged"
    
    if volumes:
        createCmd += " -v " + " -v ".join(parse_volumes(volumes, extra_volumes))
    
    if expose:
        createCmd += " --expose=" + " --expose=".join(expose)

    if map_ports:
        createCmd += " -p " + " -p".join(map_ports)
    
    createCmd += " " + base_name

    rm_container(cont_name)
    run(createCmd, write=["\n "])


def build_with_commits(cont_name, img_name, e, fromCommit=None, extra_volumes=[], allVolumes=False):

    # Retrieve existing commits
    commits = ls_commits()
    commits_map = {x[0] for x in commits}

    if allVolumes:
        volumes = e.deploy_volumes + e.build_volumes
    else:
        volumes = e.build_volumes

    # Here
    restore_point = None

    if fromCommit is None:
        for i in range(len(e.commits)-1,-1,-1):
            name = e.commits[i].commit_name

            if name in commits_map:
                restore_point = i
                break
    
    else:
        found = False

        for i in range(len(e.commits)):
            name = e.commits[i].name

            if name == fromCommit:
                if i != 0:
                    previous = e.commits[i-1].commit_name

                    if not previous in commits_map:
                        error("Can't restore from", fromCommit, ", previous snapshot is not available")
                    
                    restore_point = i - 1
                
                found = True
                break

        if not found:
            error("Invalid migration", fromCommit)

    if restore_point is None:
        yprint("Starting from base image", e.base)
        restore_point = 0
        create_container("tmp", e.flags, volumes, extra_volumes, e.expose, e.map_ports, e.base)

        if e.get_bash is not None:
            run("docker exec -t tmp %s" % e.get_bash)


    else:
        for i in range(restore_point):
            yprint("Skipping migration", e.commits[i].name)

        yprint("Recovering snapshot", e.commits[restore_point].name, "...")
        base = e.commits[restore_point].commit_name
        create_container("tmp", e.flags, volumes, extra_volumes, e.expose, e.map_ports, base)
        restore_point += 1
    
    start_container("tmp", e, skip_start=True)

    for i in range(restore_point, len(e.commits)):
        c = e.commits[i]

        yprint("Applying", c.name, "migration ...")
        status, _ = exec("tmp", e.bashrc, c.lines, False)

        if status != 0:
            error("Migration is not working, please fix it")

        print("Saving snapshot...")
        commit("tmp", c.commit_name)
    
    yprint("Creating final image:", img_name, "...")
    rm_container(cont_name)
    commit("tmp", img_name)
    rename_container("tmp", cont_name)

    run_start(cont_name, e, attach=True)

    yprint("Cleaning old snapshots ...")
    current_hashs = {x.hashstr for x in e.commits}
    olds = []

    for x in commits:
        commit_img = x[0]
        xhash = x[-1]

        if commit_img.startswith(e.commit_prefix):
            if not xhash in current_hashs:
                olds.append(commit_img)

    rm_image(olds)


def rename_container(oldname, newname):
    run("docker rename " + oldname + " " + newname)


def rm_container(cont_name):
    if type(cont_name) is list:
        cont_name = " ".join(cont_name)
    
    stop(cont_name)
    run("docker rm " + cont_name + " 1> /dev/null 2> /dev/null", suppressError=True)


def rm_image(img_name):
    if img_name is None:
        return
    
    if type(img_name) is list:
        img_name = " ".join(img_name)
    
    if img_name.strip():
        run("docker rmi -f " + img_name, suppressError=True)


def stop(cont_name):
    if type(cont_name) is list:
        cont_name = " ".join(cont_name)
    
    run("docker kill " + cont_name + " 1> /dev/null 2> /dev/null", suppressError=True)


def ls_containers():
    run("docker ps -a -f \"name=wcont__*\"")


def ls_images():
    run("docker image ls \"wimg*\"")


def ls_commits():
    status, rows = run("docker image ls \"wcommit*\"", read=True)

    if status != 0:
        error("Command error")

    result = []
    for row in rows[1:]:
        cells1 = row.split()
        cells2 = cells1[1].split("__")
        result.append([cells1[0] + ":" + cells1[1]] + cells2)
    
    return result


def export_image(img_name, filepath):
    run("docker save {} | gzip > {}".format(img_name, filepath))


def load_image(filepath):
    run(["zcat " + filepath, "docker load -q"])


def get_container_ip(cont_name):
    if type(cont_name) is list:
        return [(x, get_container_ip(x)) for x in cont_name]
    
    cmd = "docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' " + cont_name
    status, rows = run(cmd, read=True)

    if status != 0 or not rows:
        error("Command error")
    
    return rows[0].strip()


def is_container_running(cont_name):
    if type(cont_name) is list:
        return [is_container_running(x) for x in cont_name]

    cmd = "docker inspect -f '{{.State.Running}}' " + cont_name
    status, rows = run(cmd, read=True)

    if status != 0 or not rows:
        error("Command error")
    
    return rows[0] == "true\n"


def exists_image(img_name):
    status, rows = run("docker image ls \"" + img_name + "\"", read=True)

    if status != 0:
        error("Command error")
    
    return len(rows) >= 2


def start_container(cont_name, e, attach=True, skip_start=False):
    if type(cont_name) is list:
        for n in cont_name:
            start_container(n, e, attach=attach, skip_start=skip_start)
        return
    
    if is_container_running(cont_name):
        #print("Container is running, skipping", cont_name)
        return
    
    print("Starting container", cont_name)
    run("docker start " + cont_name + " > /dev/null")

    if not skip_start:
        run_start(cont_name, e, attach)


def run_start(cont_name, e, attach=False):
    print("Running start script for", cont_name)
    cmds = e.start + ["sleep 1\n"]
    exec(cont_name, e.bashrc, cmds, attach)


def launch(cont_name, e, attach=False):
    exec(cont_name, e.bashrc, e.launch, attach)


def exec(cont_name, bashrc, cmds, attach=False):
    return init_and_run(cont_name, bashrc, cmds, attach)


def commit(cont_name, img_name):
    rm_image(img_name)
    run("docker commit " + cont_name + " " + img_name)


def deploy(img_name, cont_name, e, extra_volumes=[], allVolumes=False):
    if not exists_image(img_name):
        error("Image not found, did you build it?")

    if allVolumes:
        volumes = e.deploy_volumes + e.build_volumes
    else:
        volumes = e.deploy_volumes

    create_container("tmp", e.flags, volumes, extra_volumes, e.expose, e.map_ports, img_name)
    exec("tmp", e.bashrc, e.deploy, attach=True)
    run_start("tmp", e, attach=True)
    
    rm_container(cont_name)
    rename_container("tmp", cont_name)


def ls_clusters():
    _, rows = run("docker ps -a -f \"name=wclus__*\"", read=True)
    r = re.compile(r'wclus__([a-zA-Z0-9]+)__([a-zA-Z0-9]+)__([0-9]+)')
    s = [r.search(row) for row in rows]
    res = {}

    for m in s:
        if m:
            cluster = m.group(1)
            env = m.group(2)

            if not cluster in res:
                res[cluster] = [1, env]
            else:
                res[cluster][0] += 1
    
    for cluster in res:
        print("{} [{}, {}]".format(cluster, *res[cluster]))


def ls_cluster_nodes(clustername):
    run("docker ps -a -f \"name=wclus__" + clustername + "__*\"")


def copy(src, dst):
    run("docker cp " + src + " " + dst)

