# StackExchangeDumpFilter

StackExchangeDumpFilter allows you to filter a Stack Exchange dump 

## Installation

1. Install lxml
     > pip install lxml
  
2. Install bitarray
     > pip install bitarray
     
3. Install file-read-backwards
     > pip install file-read-backwards
     
## How to use it
In the root of the folder

    python script.py <filepath>
  
  This command will almost copy-past the dump and delete all the users who didn't participate.
  
    python script.py -h
  
  To display help 
## Post-Scriptum
  If you are a Windows user : pip install lxml should work but you may have trouble installing bitarray.
