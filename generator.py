import os
import time
import random
import questionary
from tree import Tree
from pathlib import Path
from rich.console import Console

path = Path('inputs')
subdirnames = [entry.name for entry in os.scandir(path) if entry.is_dir()]
subdirname = questionary.select('Choose dataset directory', subdirnames + ['[new]'], '[new]').ask()
if subdirname == '[new]':
    subdirname = questionary.text('Enter new dataset name', 'dataset', validate=lambda val: val != '').ask()
path /= subdirname

filename = questionary.text('Enter filename', 'formulas', validate=lambda val: val != '').ask()
min_variable_count = int(questionary.text('Enter min_variable_count', '10', validate=lambda val: val.isdecimal() and int(val) >= 1).ask())
max_variable_count = int(questionary.text('Enter max_variable_count', str(min_variable_count), validate=lambda val: val.isdecimal() and int(val) >= min_variable_count).ask())
min_max_degree = int(questionary.text('Enter min_max_degree', '2', validate=lambda val: val.isdecimal() and int(val) >= 2).ask())
max_max_degree = int(questionary.text('Enter max_max_degree', str(min_max_degree), validate=lambda val: val.isdecimal() and int(val) >= min_max_degree).ask())
min_literal_count = int(questionary.text('Enter min_literal_count', '10', validate=lambda val: val.isdecimal() and int(val) >= 1).ask())
max_literal_count = int(questionary.text('Enter max_literal_count', str(min_literal_count), validate=lambda val: val.isdecimal() and int(val) >= min_literal_count).ask())
formula_count = int(questionary.text('Enter formula_count', '25', validate=lambda val: val.isdecimal() and int(val) >= 1).ask())

formulas = []
while len(formulas) < formula_count:
    tree = Tree.random(random.randint(min_variable_count, max_variable_count), random.randint(min_max_degree, max_max_degree))
    if min_literal_count <= tree.cost() <= max_literal_count:
        formulas += [tree.formula]

console = Console()
with console.status('Generating formulas...'):
    path.mkdir(parents=True, exist_ok=True)
    with open(path / f'{filename}.txt', 'w') as fd:
        for formula in formulas:
            fd.write(formula + '\n')
    time.sleep(3)
    console.print(f'Formula file [yellow]{filename}[/yellow] successfully generated in dataset [yellow]{subdirname}[/yellow]! 🎉')
