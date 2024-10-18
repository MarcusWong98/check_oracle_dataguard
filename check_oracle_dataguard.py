import sys
import argparse
from enum import Enum
from pathlib import Path
import pathlib
from subprocess import Popen, PIPE
import subprocess



##Program config file
config = {
    'prog': 'check_oracle_dataguard',
    'description': 'To check oracle dataguard connection',
    'epilog': 'Help'

}

parser = argparse.ArgumentParser(**config)


parser.add_argument('-e','--exe', nargs=1)
parser.add_argument('-d', '--dbname', nargs=1)
parser.add_argument('-p','--passwd', nargs=1)

args = parser.parse_args()

class STATUS(Enum):
    OK = 0
    Warning = 1	
    Critical = 2
    Unknown = 3

class RESULT(Enum):
    tnserr='ORA-12154: TNS:could not resolve the connect identifier specified'
    sucess='SUCCESS'
    warning='WARNING'

#############################################################



    
def is_exe(args):
    if args.exe == None:
        
        parser.error('No exe provided')
        return
    
    path = Path(args.exe[0])
    if not path.exists():
        parser.error("It does not exist")
        return
    print(path.name)
    if not 'dgmgrl' in path.name:
        parser.error('Please provide a dataguard bin')
    
    return path

def is_dbname(args):
    if args.dbname == None:
        parser.error('No dbname provided')
        return
    
    return args.dbname[0]

def is_passwd(args):
    if args.passwd == None:
        parser.error('No passwd provided')
        return
    
    return args.passwd[0]




def check_dataguard(args):

    try:
        exe = is_exe(args)
        dbname = is_dbname(args)
        passwd = is_passwd(args)
  

        scripts = """
        show database {dbname}
        """.format(dbname=dbname)
        
        cmd = [exe, 'sys/{passwd}@{dbname}'.format(passwd=passwd,dbname=dbname)]
        
        
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        (stdout, stderr) = p.communicate(scripts.encode('utf-8'))
    
        stdout_lines = stdout.decode('utf-8')
        
        if RESULT.tnserr.value in stdout_lines:
            print(RESULT.tnserr.value)
            exit(STATUS.Warning.value)

        if RESULT.warning.value in stdout_lines:
            print(RESULT.warning.value)
            exit(STATUS.Critical.value)
        
        if 'SUCCESS' in stdout_lines:
            print(stdout_lines)
            exit(STATUS.OK.value)

    except SystemError as e:
        print(e)
        exit(STATUS.Unknown.value)




if __name__ == '__main__':
    check_dataguard(args)
    
