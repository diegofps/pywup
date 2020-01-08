from pywup.services.system import run, quote, error

import re


def open_and_init(cont_name, bash_init, tty=True):
    k = quote("".join(["source \"$HOME/.bashrc\"\n"] + bash_init))
    b = quote("bash --init-file <(echo " + k + ")")
    tty = "-it " if tty else "-i "
    c = "docker exec " + tty + cont_name + " bash -c " + b.replace("$", "\\$")
    run(c)


def build(cont_name, bashrc, templates, variables):
    createCmd = "docker run -i --name tmp"
    
    if templates["VOLUMES"]:
        createCmd += " -v " + " -v ".join(templates["VOLUMES"])
    
    if variables["EXPOSE"]:
        createCmd += " --expose=" + " --expose=".join(variables["EXPOSE"].split(","))

    if variables["MAP_PORTS"]:
        createCmd += " -p " + " -p".join(variables["MAP_PORTS"].split(","))

    createCmd += " " + variables["BASE"]

    rm("tmp")

    cmds = bashrc + templates["BUILD"]
    run(createCmd, write=cmds)

    rm(cont_name)
    rename("tmp", cont_name)


def rename(oldname, newname):
    run("docker rename " + oldname + " " + newname)


def rm(cont_name):
    if type(cont_name) is list:
        cont_name = " ".join(cont_name)
    
    stop(cont_name)
    run("docker rm " + cont_name + " 2> /dev/null")


def rmi(img_name):
    if type(img_name) is list:
        img_name = " ".join(img_name)
    
    run("docker rmi " + img_name + " 2> /dev/null")


def stop(cont_name):
    if type(cont_name) is list:
        cont_name = " ".join(cont_name)
    
    run("docker kill " + cont_name + " 2> /dev/null")


def ls():
    run("docker ps -a -f \"name=wcont__*\"")


def lsi():
    run("docker image ls \"wimg*\"")


def export(img_name, filepath):
    run("docker save {} | gzip > {}".format(img_name, filepath))


def load(filepath):
    run(["zcat " + filepath, "docker load -q"])


def ip(cont_name):
    if type(cont_name) is list:
        return [ip(x) for x in cont_name]
    
    cmd = "docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' " + cont_name
    status, rows = run(cmd, read=True)

    if status != 0 or not rows:
        error("Command error")
    
    return rows[0].strip()


def is_running(cont_name):
    cmd = "docker inspect -f '{{.State.Running}}' " + cont_name
    status, rows = run(cmd, read=True)

    if status != 0 or not rows:
        error("Command error")
    
    return rows[0] == "true\n"


def exists_img(img_name):
    status, rows = run("docker image ls \"" + img_name + "\"", read=True)

    if status != 0:
        error("Command error")
    
    return len(rows) >= 2


def start(cont_name, bashrc, templates):
    if type(cont_name) is list:
        for n in cont_name:
            start(n, bashrc, templates)
        return
    
    if is_running(cont_name):
        return
    
    run("docker start " + cont_name)

    cmds = bashrc + templates["START"] + ["sleep 1\n exit\n"]
    exec(cont_name, cmds)


def launch(cont_name, bashrc, templates):
    exec(cont_name, bashrc + templates["LAUNCH"])


def exec(cont_name, cmds):
    open_and_init(cont_name, cmds)


def commit(cont_name, img_name):
    rmi(img_name)
    run("docker commit " + cont_name + " " + img_name)


def new(img_name, cont_name, bashrc, templates, variables):
    if not exists_img(img_name):
        error("Image not found")

    createCmd = "docker run -i --name tmp"

    if templates["VOLUMES"]:
        createCmd += " -v " + " -v ".join(templates["VOLUMES"])
    
    if variables["EXPOSE"]:
        createCmd += " --expose=" + " --expose=".join(variables["EXPOSE"].split(","))

    if variables["MAP_PORTS"]:
        createCmd += " -p " + " -p".join(variables["MAP_PORTS"].split(","))

    createCmd += " " + img_name

    rm("tmp")

    cmds = bashrc + templates["NEW"]
    run(createCmd, write=cmds)

    rm(cont_name)
    rename("tmp", cont_name)


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

