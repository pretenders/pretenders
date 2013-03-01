import os


def in_parent_process():
    return os.environ.get('BOTTLE_CHILD', 'false') != 'true'


def save_pid_file(filename):
    # Save PID to disk
    pid = os.getpid()
    with open(filename, 'w') as f:
        f.write(str(pid))
