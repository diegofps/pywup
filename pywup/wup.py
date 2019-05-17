from sys import argv


def wup():
    args = argv[1:]
    
    if len(args) == 0:
        return print("Missing wup command")
    
    cmd = args[0]
    
    if cmd == "heatmap":
        from .cmdtools.heatmap import main
    
    elif cmd == "collect":
        from .cmdtools.collect import main
    
    else:
        return print("Unknown wup command:", cmd)
    
    main(args[1:])
