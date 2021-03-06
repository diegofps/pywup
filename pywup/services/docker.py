from pywup.services.system import run, quote, error, expand_path, yprint

import re
import os


def open_and_init(cont_name, bash_init, tty=True):
    k = quote("".join(["source \"$HOME/.bashrc\"\n"] + bash_init))
    b = quote("bash --init-file <(echo " + k + ")")
    tty = "-it " if tty else "-i "
    c = "docker exec " + tty + cont_name + " bash -c " + b.replace("$", "\\$")
    run(c)


def parse_volumes(volumes):
    volumes = [j.strip() for j in volumes]
    volumes = [expand_path(j) for j in volumes if j]

    for v in volumes:
        src = v.split(":")[0]

        if not os.path.exists(src):
            error("Missing source directory in host:", src)
        
        if not os.path.isdir(src):
            error("Source volume in host is not a directory:", src)
    
    return volumes


def build_single(cont_name, e):
    createCmd = "docker run -i --name tmp"
    
    if e.volumes:
        createCmd += " -v " + " -v ".join(parse_volumes(e.volumes))
    
    if e.expose:
        createCmd += " --expose=" + " --expose=".join(e.expose)

    if e.map_ports:
        createCmd += " -p " + " -p".join(e.map_ports)

    createCmd += " " + e.base

    rm_container("tmp")

    cmds = e.bashrc + e.full_build
    run(createCmd, write=cmds)

    rm_container(cont_name)
    rename_container("tmp", cont_name)


def build_with_commits(cont_name, img_name, e):


    # Retrieve existing commits
    commits = ls_commits()
    commits_map = {x[0] for x in commits}

    # Prefix for creating the container
    createCmd = "docker run -i --name tmp"
    
    if e.volumes:
        createCmd += " -v " + " -v ".join(parse_volumes(e.volumes))
    
    if e.expose:
        createCmd += " --expose=" + " --expose=".join(e.expose)

    if e.map_ports:
        createCmd += " -p " + " -p".join(e.map_ports)

    # Here
    restore_point = None

    for i in range(len(e.commits)-1,-1,-1):
        name = e.commits[i].commit_name

        if name in commits_map:
            restore_point = i
            break

    if restore_point is None:
        yprint("Creating from the base image", e.base)
        createCmd += " " + e.base
        restore_point = 0

    else:
        for i in range(restore_point):
            yprint("Skipping migration", e.commits[i].name)

        yprint("Recovering snapshot", e.commits[restore_point].name, "...")
        createCmd += " " + e.commits[restore_point].commit_name
        restore_point += 1

    rm_container("tmp")
    run(createCmd, write=e.bashrc)
    start_container("tmp", e)

    for i in range(restore_point, len(e.commits)):
        c = e.commits[i]
        yprint("Applying migration", c.name, "...")
        exec("tmp", c.lines + ["exit\n"])

        print("Saving snapshot...")
        commit("tmp", c.commit_name)
    
    yprint("Creating final image:", img_name, "...")
    rm_container(cont_name)
    commit("tmp", img_name)
    rename_container("tmp", cont_name)

    yprint("Cleaning old snapshots ...")
    current_hashs = {x.hashstr for x in e.commits}
    olds = []

    for x in commits:
        commit_img = x[0]
        xhash = x[4]

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
    run("docker rm " + cont_name + " 1> /dev/null 2> /dev/null")


def rm_image(img_name):
    if type(img_name) is list:
        img_name = " ".join(img_name)
    
    run("docker rmi " + img_name + " 2> /dev/null")


def stop(cont_name):
    if type(cont_name) is list:
        cont_name = " ".join(cont_name)
    
    run("docker kill " + cont_name + " 1> /dev/null 2> /dev/null")


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


def start_container(cont_name, e):
    if type(cont_name) is list:
        for n in cont_name:
            start_container(n, e)
        return
    
    if is_container_running(cont_name):
        return
    
    run("docker start " + cont_name + " > /dev/null")

    cmds = e.bashrc + e.start + ["sleep 1\n exit\n"]
    exec(cont_name, cmds)


def launch(cont_name, e):
    exec(cont_name, e.bashrc + e.launch + ["exit\n"])


def exec(cont_name, cmds):
    open_and_init(cont_name, cmds)


def commit(cont_name, img_name):
    rm_image(img_name)
    run("docker commit " + cont_name + " " + img_name)


def new(img_name, cont_name, e):
    if not exists_image(img_name):
        error("Image not found")

    createCmd = "docker run -i --name tmp"

    if e.volumes:
        createCmd += " -v " + " -v ".join(e.volumes)
    
    if e.expose:
        createCmd += " --expose=" + " --expose=".join(e.expose)

    if e.map_ports:
        createCmd += " -p " + " -p".join(e.map_ports)

    createCmd += " " + img_name

    rm_container("tmp")

    cmds = e.bashrc + e.new
    run(createCmd, write=cmds)

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

