import pulp


def first_fit_decreasing(items_list, bin_width):
    remain = [bin_width]
    sol = [[]]
    for item in sorted(items_list, reverse=True):
        for j, free in enumerate(remain):
            if free >= item:
                remain[j] -= item
                sol[j].append(item)
                break
        else:
            sol.append([item])
            remain.append(bin_width - item)
    return sol


def mip_model(items_dict, bins_width):

    I = list(items_dict.keys())
    J = range(len(first_fit_decreasing(list(items_dict.values()), bins_width)))
    x_keys = [(i, j) for i in I for j in J]
    y_keys = J

    mdl = pulp.LpProblem('bin_packing', sense=pulp.LpMinimize)

    x = pulp.LpVariable.dicts(indexs=x_keys, cat=pulp.LpBinary, name='x')
    y = pulp.LpVariable.dicts(indexs=y_keys, cat=pulp.LpBinary, name='y')

    # every item must be packed exactly once:
    for i in I:
        mdl.addConstraint(pulp.lpSum(x[i, j] for j in J) == 1, name=f'c1_{i}')

    # bins capacity:
    for j in J:
        mdl.addConstraint(pulp.lpSum(w * x[i, j] for i, w in items_dict.items()) <= bins_width * y[j], name=f'c2_{j}')

    # bin is used if it gets any item assigned to it:
    for i in I:
        for j in J:
            mdl.addConstraint(x[i, j] <= y[j], name=f'c3_{i}_{j}')

    mdl.solve(pulp.PULP_CBC_CMD(timeLimit=60, gapRel=1e-5))
    status = pulp.LpStatus[mdl.status]
    if status == 'Optimal':
        x_sol = [(i, j) for (i, j), var in x.items() if var.value() > 0.5]
        y_sol = [j for j, var in y.items() if var.value() > 0.5]
        sol = {j: list() for j in y_sol}
        for i, j in x_sol:
            sol[j].append(items_dict[i])
    else:
        x_sol, y_sol, sol = None, None, None
        print(f'Model is not optimal. Status: {status}')

    return sol


def initial_patters(item_qty_dict, bins_width):
    bin_width_dict = {k+1: w for k, w in enumerate(item_qty_dict.keys())}
    patters = dict()
    for k, w in bin_width_dict.items():
        patters[k] = {w_: 0 for w_ in item_qty_dict.keys()}
        patters[k][w] = int(bins_width / w)
    return patters


def master_problem(patterns, item_qty_dict, relaxed):
    K = list(patterns.keys())

    mdl = pulp.LpProblem("master_LP", sense=pulp.LpMinimize)
    if relaxed:
        x = pulp.LpVariable.dicts(indexs=K, cat=pulp.LpContinuous, lowBound=0, name='x')
    else:
        x = pulp.LpVariable.dicts(indexs=K, cat=pulp.LpInteger, lowBound=0, name='x')
    for i, num_items in item_qty_dict.items():
        mdl.addConstraint(pulp.lpSum(patterns[k][i] * x[k] for k in K) >= num_items, name=f'{i}')
    mdl.setObjective(pulp.lpSum(x[k] for k in K))

    mdl.solve(pulp.PULP_CBC_CMD(timeLimit=60, gapRel=1e-5))
    status = pulp.LpStatus[mdl.status]
    if status == 'Optimal':
        x_sol = {k: var.value() for k, var in x.items()}
        pi = {int(i): c.pi for i, c in mdl.constraints.items()}
    else:
        x_sol, pi = None, None
        print(f'Model is not optimal. Status: {status}')
    return mdl, x_sol, pi


def sub_problem(patterns, item_qty_dict, bin_width, pi):
    flag = True
    mdl = pulp.LpProblem("knapsackP", sense=pulp.LpMaximize)
    y = dict()
    for i, num_items in item_qty_dict.items():
        y[i] = pulp.LpVariable(cat=pulp.LpInteger, lowBound=0, upBound=num_items, name=f"y[{i}]")

    mdl.addConstraint(pulp.lpSum(i * y[i] for i in item_qty_dict.keys()) <= bin_width, name="width")

    obj = pulp.lpSum(pi[i] * y[i] for i in item_qty_dict.keys())
    mdl.setObjective(obj)
    mdl.solve(pulp.PULP_CBC_CMD(timeLimit=60, gapRel=1e-5))
    status = pulp.LpStatus[mdl.status]
    if status == 'Optimal':
        if obj.value() < 1 + 1e-5:
            flag = False
        pattern = {i: int(var.value() + 0.5) for i, var in y.items()}
        key = max(patterns.keys()) + 1
        patterns[key] = pattern
    else:
        raise ValueError(f'Model is not optimal. Status: {status}')
    return flag, patterns


def column_generation(patterns, item_qty_dict, bin_width):
    while True:
        mdl_master, x_sol_relaxed, pi = master_problem(patterns, item_qty_dict, relaxed=True)
        flag, patterns = sub_problem(patterns, item_qty_dict, bin_width, pi)
        if not flag:
            break
    _, x_sol, _ = master_problem(patterns, item_qty_dict, relaxed=False)
    return x_sol, patterns







