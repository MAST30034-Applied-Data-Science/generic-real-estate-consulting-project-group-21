#! /bin/python3
import re
import glob
import os
import pycodestyle
from json import load


def load_script(file):
    """
    Convert an interactive python notebook to a python script

    :param file: the location of an ipython notebook
    :returns: python script as a string
    """
    ipynb = open(file)
    data = load(ipynb)

    pyscript = ''
    for cell in data['cells']:
        if cell['cell_type'] == 'code':
            pyscript += ''.join(cell['source']) + '\n\n'

    # remove last new line
    pyscript = pyscript[:-1]
    return pyscript


def get_funcs_wout_reST_docstrings(python_script):
    """
    Get the functions without a reST docstring

    :param python_script: a string containing a python script
    :returns: list of function signatures which dont have a docstring
    """
    functions = []
    for func in pyscript.split('def ')[1:-1]:
        signature = func.split(':')[0]

        params = [param.strip('"): ') for param in
                  signature.split('(')[-1].split(',')]
        # handle default arguments
        params = map(lambda p: p if len(p.split('=')) == 1
                     else p.split('=')[0], params)
        # make regex like :param number:\n.*:param postcode:\n.*:returns: .*
        pattern = r' .*\n.*'.join([f':param {p}:' for p in params])\
            + r' .*\n.*:returns: .*'
        if not re.findall(pattern, func):
            functions.append(signature)
    return functions


ipynbs = glob.glob('**/*.ipynb', recursive=True)
pys = glob.glob('**/*.py', recursive=True)

for file in ipynbs + pys:
    if file in ipynbs:
        pyscript = load_script(file)
        tmp_file = ''.join(file.split('.')[:-1]) + '-tmp.py'
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
        tmp_file_ptr = open(tmp_file, "a")
        tmp_file_ptr.write(pyscript)
        tmp_file_ptr.flush()
    else:
        pyscript = open(file).read()

    funcs = get_funcs_wout_reST_docstrings(pyscript)
    if len(funcs) == 0:
        print(f'reST docstrings PASSED\u2713 for {file}')
    else:
        print(f'reST docstrings FAILED\u274C for {file}')
        print(f'functions missing reST docstrings:')
        for f in funcs:
            print(f' - {f}')

    f = tmp_file if file in ipynbs else file
    if os.system(f'pycodestyle {f} --ignore=E501 --show-source') != 0:
        print(f'PEP8 guidelines FAILED\u274C for {file}')
    else:
        print(f'PEP8 guidelines PASSED\u2713 for {file}')

    if file in ipynbs:
        os.remove(tmp_file)
