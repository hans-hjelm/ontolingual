import scipy.stats


def context_subsumption(context_vector1, context_vector2):
    non_zero_1 = set(context_vector1.nonzero()[1])
    non_zero_2 = set(context_vector2.nonzero()[1])
    non_zero_both = non_zero_1 & non_zero_2
    if len(non_zero_1) <= len(non_zero_2) or len(non_zero_2) == 0:
        return 0
    return len(non_zero_both) / len(non_zero_2)


def entropy(context_vector):
    if len(context_vector.nonzero()[1]) == 0:
        return 0
    min_val = min(context_vector.data)
    if min_val < 0:
        context_vector.data -= min_val
    context_sum = sum(context_vector.data)
    if context_sum == 0:
        return 0
    data_as_probs = context_vector.data/context_sum
    return scipy.stats.entropy(data_as_probs, base=2)
