from data import items_dict, bins_width, item_qty_dict
from optimization_utils import first_fit_decreasing
from optimization_utils import mip_model
from optimization_utils import initial_patters
from optimization_utils import master_problem
from  optimization_utils import column_generation

if __name__ == '__main__':

    widths = set(items_dict.values())
    solution_ffd = first_fit_decreasing(list(items_dict.values()), bins_width)

    solution_mip = mip_model(items_dict, bins_width)
    print(f'Solution FFD: {solution_ffd}')
    print(f'Solution MIP: {solution_mip}')

    patterns = initial_patters(item_qty_dict, bins_width)
    print(f'Initial Patterns: {patterns}')

    _, x_sol_relaxed, _ = master_problem(patterns, item_qty_dict, relaxed=True)
    _, x_sol, _ = master_problem(patterns, item_qty_dict, relaxed=False)
    print(f'Master Relaxed Solution: {x_sol_relaxed}')
    print(f'Master Solution: {x_sol}')

    x_sol, patterns = column_generation(patterns, item_qty_dict, bins_width)
    s = {k: patterns[k] for k, v in x_sol.items() if v > 0.5}
    print(f'Solution: {x_sol}')
    for k, v in x_sol.items():
        if v > 0.5:
            print(patterns[k])
