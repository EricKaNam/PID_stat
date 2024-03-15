#!/usr/bin/python3
# Filename: m4q1.py
# Author: Eric Chung
# Details:  PARSE info from /proc/<PID>/stat for the current running program
#           1.Show a menu for user to start a new process
#           2.List all current user's process
#           3.Select a process to sleep for a peiod
#           4.Stop a process


import os
import subprocess
import time
import psutil
from prettytable import PrettyTable

class LinuxProcess:
    def __init__(self, pid):
        self.pid = pid
        self.filename = os.path.basename(__file__)
        self.stat_path = f'/proc/{pid}/stat'
        self.process = psutil.Process(pid)
        self.running = False  # Initialize the running flag for run, sleep and stop
        self.subprocess = None  # Initialize the subprocess attribute
        self._load_stat()

    def _load_stat(self):
        with open(self.stat_path, 'r') as stat_file:
            stat = stat_file.read().split() #use space to split
            self.ppid = int(stat[3])
            self.rss = int(stat[23])
            self.rsslim = int(stat[24])
            self.start_code = int(stat[25])
            self.end_code = int(stat[26])
            self.start_stack = int(stat[27])
            self.start_data = int(stat[44])
            self.end_data = int(stat[45])
            self.start_brk = int(stat[46])
            self.arg_start = int(stat[47])
            self.arg_end = int(stat[48])
            self.env_start = int(stat[49])
            self.env_end = int(stat[50])

    def to_pretty_table(self):
        table = PrettyTable()
        table.align = 'r'
        table.field_names = ['Attribute', 'Value']
        table.add_row(['Filename', self.filename])
        table.add_row(['PID', self.pid])
        table.add_row(['PPID', self.ppid])
        table.add_row(['RSS', hex(self.rss)])
        table.add_row(['RSSlim', hex(self.rsslim)])
        table.add_row(['Start_code', hex(self.start_code)])
        table.add_row(['End_code', hex(self.end_code)])
        table.add_row(['Start_stack', hex(self.start_stack)])
        table.add_row(['Start_data', hex(self.start_data)])
        table.add_row(['End_data', hex(self.end_data)])
        table.add_row(['Start_brk', hex(self.start_brk)])
        table.add_row(['Arg_start', hex(self.arg_start)])
        table.add_row(['Arg_end', hex(self.arg_end)])
        table.add_row(['Env_start', hex(self.env_start)])
        table.add_row(['Env_end', hex(self.env_end)])
        return table
    
    def run(self, command):
        #only start a new process when the self.running flag is not True
        if not self.running:
            try:
                print(f'Process {self.pid} is starting a new subprocess.')
                self.running = True
                #cannot use run()
                self.subprocess = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = self.subprocess.communicate()
                print('Subprocess output:')
                print(stdout)
                if stderr:
                    print('Subprocess error:')
                    print(stderr)
            except FileNotFoundError:
                print(f'\n\nError: Command "{command}" not found. What\'s that?')
                self.running = False                        
                print(f'The process is ended.')
        else:
            print(f'Process {self.pid} is already running.')

    def sleep(self, pid, seconds):
        if psutil.pid_exists(pid):
            print(f'Sleeping process with PID {pid} for {seconds} seconds...')
            time.sleep(seconds)
            print(f'Process with PID {pid} is awake!')
        else:
            print(f'No process with PID {pid} found.')

    def stop(self, pid):
        if psutil.pid_exists(pid):
            print(f'Stopping process with PID {pid}...')
            psutil.Process(pid).terminate()
            print(f'Process with PID {pid} stopped.')
        else:
            print(f'No process with PID {pid} found.')

    def list_processes(self):
        print('Listing all processes run by the current user:')
        current_user = os.getlogin()  #get the userid first
        for proc in psutil.process_iter(attrs=['pid', 'username', 'name']):
            if proc.info['username'] == current_user: #only list the current user's process
                print(f'PID: {proc.info["pid"]}, Name: {proc.info["name"]}')

if __name__ == '__main__':
    current_pid = os.getpid()
    process = LinuxProcess(current_pid)
    print(process.to_pretty_table(),"\n")
    print("***" * 15,"\n")

while True:
        print("###"*15,"\n")
        print("Choose an option:")
        print("1. Start a new subprocess")
        print("2. List all processes run by the current user")
        print("3. Make a process sleep")
        print("4. Stop a process")
        print("5. Exit\n")

        choice = input("Enter your choice: ")
        print("###"*15,"\n")

        if choice == '1':
            command = input("Enter the command to run in the subprocess: ")
            if not command:
                print("Command cannot be blank. Please try again.")
                continue
            process.run(command.split())

        elif choice == '2':
            process.list_processes()

        elif choice == '3':
            try:
                pid = int(input("Enter the PID of the process to sleep: "))
                seconds = int(input("Enter the sleep duration (Maximum 15 seconds): "))
                seconds = max(1, min(seconds, 15))  # Clamp the value between 1 and 15
                process.sleep(pid, seconds)
            except ValueError:
                print("Invalid input.")

        elif choice == '4':
            try:
                pid = int(input("Enter the PID of the process to stop: "))
                process.stop(pid)
            except ValueError:   
                print("Invalid input.")
        
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")
