import subprocess

if __name__ == "__main__":
    proc1 = subprocess.Popen(['gnome-terminal', '-x', 'python', 'print1.py'])
    proc2 = subprocess.Popen(['gnome-terminal', '-x', 'python', 'print2.py'])
    proc1.wait()
    proc2.wait()