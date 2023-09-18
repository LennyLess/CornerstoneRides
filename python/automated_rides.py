import subprocess
import os

os.chdir(r'.\python')

command = 'python rides.py'

subprocess.call(command, shell=True)

os.chdir(r'..\java')

command = 'java Sheets input.txt 5 ' +  r'..\python\output.txt'
print(command)
subprocess.call(command, shell=True)

command = 'del input.txt'

subprocess.call(command, shell=True)

os.chdir(r'..\python')

command = 'python upload.py'

subprocess.call(command, shell=True)

command = 'del output.txt'

subprocess.call(command, shell=True)