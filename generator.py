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
min_cost = int(questionary.text('Enter min_cost', '10', validate=lambda val: val.isdecimal() and int(val) >= 1).ask())
max_cost = int(questionary.text('Enter max_cost', str(min_cost), validate=lambda val: val.isdecimal() and int(val) >= min_cost).ask())
formula_count = int(questionary.text('Enter formula_count', '25', validate=lambda val: val.isdecimal() and int(val) >= 1).ask())

formulas = []
while len(formulas) < formula_count:
    tree = Tree.random(random.randint(min_variable_count, max_variable_count), random.randint(min_max_degree, max_max_degree))
    if min_cost <= tree.cost() <= max_cost:
        formulas += [tree.formula]

console = Console()
with console.status('Generating formulas...') as status:
    path.mkdir(parents=True, exist_ok=True)
    with open(path / f'{filename}.txt', 'w') as fd:
        for formula in formulas:
            fd.write(formula + '\n')
    time.sleep(3)
    console.print(f'Formula file [yellow]{filename}[/yellow] successfully generated in dataset [yellow]{subdirname}[/yellow]! 🎉')
