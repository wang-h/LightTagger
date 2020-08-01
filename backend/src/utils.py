
def divide_n_package(big_list, n=5):
    l = len(big_list)
    x = [i for i in range(0, l, n)]
    small_lists = []
    for p, q in zip(x, x[1:]):
        small_lists.append(list(big_list[p: q]))
    if x[-1] < l:
        small_lists.append(list(big_list[x[-1]: l]))
    return small_lists
