# Admin Tool for RubiX

## Installation
`rubix-admin` should be installed on the cluster (Presto/Spark/Hadoop2) master

    git clone https://github.com/qubole/rubix-admin.git
    virtualenv venv
    source venv/bin/activate
    python setup.py install
    rubix-admin -h
    
## Configure Admin Tool
`rubix-admin` expects a configuration file at `~/.radminrc`. If you followed
the instruction in the previous section, it should already be present. 
If the configuration file does not exist, run:

    rubix-admin -h
    
Edit the configuration file.

## Install RubiX
Generate a RubiX RPM by following the instructions in Qubole Rubix project.
  
    rubix-admin installer install --cluster-type {presto,spark} --rpm <path to rpm>
    
## Start RubiX

    rubix-admin daemon start

