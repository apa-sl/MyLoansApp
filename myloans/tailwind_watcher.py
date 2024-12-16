# tailwind_watcher.py
import subprocess

def run_tailwind_watch():
    """
    Runs TailwindCSS in watch mode for automatic recompilation.
    """
    command = [
        './tailwindcss.exe',  # Make sure that this points to your tailwindcss file in your project.
        '-i', './loansapp/static/css/input.css',  # input
        '-o', './loansapp/static/css/output.css',  # output
        '--watch'
    ]
    subprocess.run(command)
    print('TailwindCSS watcher started.')

run_tailwind_watch()
