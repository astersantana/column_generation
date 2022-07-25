bins_width = 9
item_qty_dict = {2: 4, 3: 2, 4: 6, 5: 6, 6: 2, 7: 2, 8: 2}  # {item_width: num_items}
items_dict = dict()
item_id = 0
for item_width, num_items in item_qty_dict.items():
    for i in range(num_items):
        item_id += 1
        items_dict[item_id] = item_width
