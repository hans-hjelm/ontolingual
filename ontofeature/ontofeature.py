import scipy.stats


def context_subsumption(context_vector1, context_vector2):
    if len(context_vector1) != len(context_vector2):
        raise ValueError("Context vectors must have same length to calculate subsumption")
    non_zero_1 = set(context_vector1.nonzero()[0])
    non_zero_2 = set(context_vector2.nonzero()[0])
    non_zero_both = non_zero_1 & non_zero_2
    if len(non_zero_1) <= len(non_zero_2):
        return 0
    return len(non_zero_both) / len(non_zero_2)


def entropy(context_vector):
    return scipy.stats.entropy(context_vector, base=2)

