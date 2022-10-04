#! /bin/python3
import json
import re
import glob
import os
import pycodestyle


def ipynb_to_py(file):
    """returns a python script from an ipython notebook string"""
    ipynb = open(file)
    data = json.load(ipynb)

    pyscript = ''
    for cell in data['cells']:
        pyscript += ''.join(cell['source']) + '\n\n'

    return pyscript


def get_funcs_wout_docstrings(python_script):
    """returns function names which dont have a docstring"""
    functions = []
    docstring_required = False
    for line in pyscript.split('\n'):
        if docstring_required:
            if not re.match(r'.*""".*"""', line):
                functions.append(function)
            docstring_required = False
        if re.match('^def .*:', line):
            function = line.split('def')[-1].strip()
            docstring_required = True
    return functions


ipynbs = glob.glob('**/*.ipynb', recursive=True)
pys = glob.glob('**/*.py', recursive=True)

for file in ipynbs + pys:
    if file in ipynbs:
        pyscript = ipynb_to_py(file)
        tmp_file = ''.join(file.split('.')[:-1]) + '-tmp.py'
        tmp_file_ptr = open(tmp_file, "a")
        tmp_file_ptr.write(pyscript)
    else:
        pyscript = open(file).read()

    funcs = get_funcs_wout_docstrings(pyscript)
    if len(funcs) == 0:
        print(f'docstrings PASSED\u2713 for {file}')
    else:
        print(f'docstrings FAILED\u274C for {file}')
        print(f'functions missing docstrings:')
        for f in funcs:
            print(f' - {f}')

    f = tmp_file if file in ipynbs else file
    if os.system(f'pycodestyle {f}') != 0:
        print(f'PEP8       FAILED\u274C for {file}')
    else:
        print(f'PEP8       PASSED\u2713 ffor {file}')

    if file in ipynbs:
        os.remove(tmp_file)
