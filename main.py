import os
import time
import shutil
import inspect
import heuristics
import questionary
from tree import Tree
from pathlib import Path
from rich.table import Table
from rich.console import Console
from rich.progress import Progress

def run(dataset_path, heuristic, iterations=5):
    global rows
    with Progress() as progress:
        filenames = [entry.name for entry in os.scandir(dataset_path) if entry.is_file() and os.path.splitext(entry.name)[1] == '.txt']
        for filename in filenames:
            results_path = dataset_path / 'results' / heuristic.__name__
            results_path.mkdir(parents=True, exist_ok=True)
            task = progress.add_task(f'Running [yellow]{heuristic.__name__}[/yellow] for [yellow]{filename[0:-4]}[/yellow]')

            with open(results_path / filename, 'w') as fd:
                total_avg_improvement = 0
                total_max_improvement = 0
                total_avg_runningtime = 0

                formulas = [line for line in open(dataset_path / filename, 'r').read().split('\n') if line != '']
                for formula in formulas:
                    avg_improvement = 0
                    max_improvement = 0, ''
                    avg_runningtime = 0

                    for _ in range(iterations):
                        tree = Tree.parse(formula)
                        old_cost = tree.cost()
                        old_time = time.time()
                        heuristic(tree)
                        new_time = time.time()
                        new_cost = tree.cost()

                        improvement = (old_cost - new_cost) / old_cost * 100
                        runningtime = new_time - old_time
                        avg_improvement += improvement
                        max_improvement = max(max_improvement, (improvement, tree.formula))
                        avg_runningtime += runningtime
                        progress.update(task, advance=100 / len(formulas) / iterations)

                    avg_improvement /= iterations
                    avg_runningtime /= iterations
                    fd.write(max_improvement[1] + '\n')

                    total_avg_improvement += avg_improvement
                    total_max_improvement += max_improvement[0]
                    total_avg_runningtime += avg_runningtime

                total_avg_improvement /= len(formulas)
                total_max_improvement /= len(formulas)
                total_avg_runningtime /= len(formulas)

                progress.update(task, advance=100)
                rows += [(
                    filename[0:-4],
                    heuristic.__name__,
                    '{:.2f}'.format(total_avg_improvement),
                    '{:.2f}'.format(total_max_improvement),
                    '{:.2f}'.format(total_avg_runningtime)
                )]

path = Path('inputs')
subdirnames = [entry.name for entry in os.scandir(path) if entry.is_dir()]
subdirname = questionary.select('Choose dataset directory', subdirnames).ask()
path /= subdirname

options = {function[0]: function[1] for function in inspect.getmembers(heuristics, inspect.isfunction) if function[0] != 'iterate'}
checked = questionary.checkbox('Select heuristics to be run', list(options.keys())).ask()
chosen_heuristics = [options[name] for name in checked]

results_path = path / 'results'
if results_path.exists():
    shutil.rmtree(results_path)

table = Table(title=f'Score and Time Analysis on Dataset [yellow]{subdirname}[/yellow]', header_style='bold green')
table.add_column('Filename', justify='center')
table.add_column('Heuristic', justify='left')
table.add_column('Average Score (%)', justify='right')
table.add_column('Maximum Score (%)', justify='right')
table.add_column('Average Running Time (s)', justify='right')

console = Console()
console.print()

rows = []
for heuristic in chosen_heuristics:
    run(path, heuristic)
rows.sort()
for index, row in enumerate(rows, 1):
    new_row = list(row)
    best_avg_improvement = max([row[2] for row in rows if row[0] == new_row[0]], key=lambda val: float(val))
    best_max_improvement = max([row[3] for row in rows if row[0] == new_row[0]], key=lambda val: float(val))
    if best_avg_improvement == new_row[2]: new_row[2] = f'[red]{new_row[2]}[/red]'
    if best_max_improvement == new_row[3]: new_row[3] = f'[red]{new_row[3]}[/red]'
    table.add_row(*new_row, end_section=index % len(chosen_heuristics) == 0)

console.print()
console.print(table)
console.print()
console.print(f'Finished running heuristics! 🎉')
