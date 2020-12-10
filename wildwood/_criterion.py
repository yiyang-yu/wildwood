
# Authors: Gilles Louppe <g.louppe@gmail.com>
#          Peter Prettenhofer <peter.prettenhofer@gmail.com>
#          Brian Holt <bdholt1@gmail.com>
#          Joel Nothman <joel.nothman@gmail.com>
#          Arnaud Joly <arnaud.v.joly@gmail.com>
#          Jacob Schreiber <jmschreiber91@gmail.com>
#
# License: BSD 3 clause

# See _criterion.pyx for implementation details.

import numpy as np
from ._utils import SIZE_t, NP_SIZE_t, UINT32_t, NP_UINT32_t, DOUBLE_t, NP_DOUBLE_t
from numba import njit
from numba.experimental import jitclass


# import numpy as np
# cimport numpy as np
# np.import_array()
#
# from numpy.math cimport INFINITY
# from scipy.special.cython_special cimport xlogy
#
# from ._utils cimport log
# from ._utils cimport safe_realloc
# from ._utils cimport sizet_ptr_to_ndarray
# from ._utils cimport WeightedMedianCalculator
#
# # EPSILON is used in the Poisson criterion
# cdef double EPSILON = 10 * np.finfo('double').eps


# cimport numpy as np
#
# from ._tree cimport DTYPE_t          # Type of X
# from ._tree cimport DOUBLE_t         # Type of y, sample_weight
# from ._tree cimport SIZE_t           # Type for indices and counters
# from ._tree cimport INT32_t          # Signed 32 bit integer
# from ._tree cimport UINT32_t         # Unsigned 32 bit integer



# class Criterion(object):
#
#     cdef int init(self, const DOUBLE_t[:, ::1] y, DOUBLE_t* sample_weight,
#                   double weighted_n_samples, SIZE_t* samples, SIZE_t start,
#                   SIZE_t end) nogil except -1:
#
#
#     def __init__(self):
#         pass

# @njit
# def criterion_children_impurity(criterion):
#     pass


@njit
def criterion_proxy_impurity_improvement(criterion):
#     cdef double proxy_impurity_improvement(self) nogil:
#         """Compute a proxy of the impurity reduction.
#
#         This method is used to speed up the search for the best split.
#         It is a proxy quantity such that the split that maximizes this value
#         also maximizes the impurity improvement. It neglects all constant terms
#         of the impurity decrease for a given split.
#
#         The absolute impurity improvement is only computed by the
#         impurity_improvement method once the best split has been found.
#         """
#         cdef double impurity_left
#         cdef double impurity_right
#         self.children_impurity(&impurity_left, &impurity_right)
#
#         return (- self.weighted_n_right * impurity_right
#                 - self.weighted_n_left * impurity_left)
    impurity_left, impurity_right = gini_children_impurity(criterion)
    return - criterion.weighted_n_right * impurity_right - criterion.weighted_n_left \
           * impurity_left


@njit
def criterion_impurity_improvement(criterion, impurity_parent, impurity_left,
                                   impurity_right):
#     cdef double impurity_improvement(self, double impurity_parent,
#                                      double impurity_left,
#                                      double impurity_right) nogil:
#         """Compute the improvement in impurity.
#
#         This method computes the improvement in impurity when a split occurs.
#         The weighted impurity improvement equation is the following:
#
#             N_t / N * (impurity - N_t_R / N_t * right_impurity
#                                 - N_t_L / N_t * left_impurity)
#
#         where N is the total number of samples, N_t is the number of samples
#         at the current node, N_t_L is the number of samples in the left child,
#         and N_t_R is the number of samples in the right child,
#
#         Parameters
#         ----------
#         impurity_parent : double
#             The initial impurity of the parent node before the split
#
#         impurity_left : double
#             The impurity of the left child
#
#         impurity_right : double
#             The impurity of the right child
#
#         Return
#         ------
#         double : improvement in impurity after the split occurs
#         """
#         return ((self.weighted_n_node_samples / self.weighted_n_samples) *
#                 (impurity_parent - (self.weighted_n_right /
#                                     self.weighted_n_node_samples * impurity_right)
#                                  - (self.weighted_n_left /
#                                     self.weighted_n_node_samples * impurity_left)))

    return ((criterion.weighted_n_node_samples / criterion.weighted_n_samples) *
            (impurity_parent - (criterion.weighted_n_right /
                                criterion.weighted_n_node_samples * impurity_right)
                             - (criterion.weighted_n_left /
                                criterion.weighted_n_node_samples * impurity_left)))

# cdef class Criterion:
#     # The criterion computes the impurity of a node and the reduction of
#     # impurity of a split on that node. It also computes the output statistics
#     # such as the mean in regression and class probabilities in classification.
#
#     # Internal structures
#     cdef const DOUBLE_t[:, ::1] y        # Values of y
#     cdef DOUBLE_t* sample_weight         # Sample weights
#
#     cdef SIZE_t* samples                 # Sample indices in X, y
#     cdef SIZE_t start                    # samples[start:pos] are the samples in the left node
#     cdef SIZE_t pos                      # samples[pos:end] are the samples in the right node
#     cdef SIZE_t end
#
#     cdef SIZE_t n_outputs                # Number of outputs
#     cdef SIZE_t n_samples                # Number of samples
#     cdef SIZE_t n_node_samples           # Number of samples in the node (end-start)
#     cdef double weighted_n_samples       # Weighted number of samples (in total)
#     cdef double weighted_n_node_samples  # Weighted number of samples in the node
#     cdef double weighted_n_left          # Weighted number of samples in the left node
#     cdef double weighted_n_right         # Weighted number of samples in the right node
#
#     cdef double* sum_total          # For classification criteria, the sum of the
#                                     # weighted count of each label. For regression,
#                                     # the sum of w*y. sum_total[k] is equal to
#                                     # sum_{i=start}^{end-1} w[samples[i]]*y[samples[i], k],
#                                     # where k is output index.
#     cdef double* sum_left           # Same as above, but for the left side of the split
#     cdef double* sum_right          # same as above, but for the right side of the split
spec_criterion = [
    ("y", DOUBLE_t[:, ::1]),
    ("sample_weight", DOUBLE_t[::1]),

    ("samples", SIZE_t[::1]),  # A numpy array holding the sample indices
    ("start", SIZE_t),
    ("pos", SIZE_t),
    ("end", SIZE_t),

    ("n_samples", SIZE_t),       # It's X.shape[0]
    ("n_node_samples", SIZE_t),  # It's X.shape[0]
    ("n_outputs", SIZE_t),
    ("weighted_n_samples", DOUBLE_t),
    ("weighted_n_node_samples", DOUBLE_t),
    ("weighted_n_left", DOUBLE_t),
    ("weighted_n_right", DOUBLE_t),

    # TODO: Si je comprends bien faut enlever sum_stride et mettre plutot avant
    #  c'etait des tableaux 1D... faut voir si c'est F ou C major
    # ("sum_stride", SIZE_t),
    ("max_n_classes", SIZE_t),
    ("sum_total", DOUBLE_t[:, ::1]),
    ("sum_left", DOUBLE_t[:, ::1]),
    ("sum_right", DOUBLE_t[:, ::1]),
]

# cdef class ClassificationCriterion(Criterion):
#     """Abstract criterion for classification."""
#
#     cdef SIZE_t* n_classes
#     cdef SIZE_t sum_stride
spec_classification_criterion = spec_criterion + [
    ("n_classes", SIZE_t[::1])
]

# cdef class RegressionCriterion(Criterion):
#     """Abstract regression criterion."""
#
#     cdef double sq_sum_total
spec_regression_criterion = spec_criterion + [
    ("sq_sum_total", DOUBLE_t),
]


@jitclass(spec_classification_criterion)
class ClassificationCriterion(object):

    def __init__(self, n_outputs, n_classes):
#     def __cinit__(self, SIZE_t n_outputs,
#                   np.ndarray[SIZE_t, ndim=1] n_classes):
#         """Initialize attributes for this criterion.
#
#         Parameters
#         ----------
#         n_outputs : SIZE_t
#             The number of targets, the dimensionality of the prediction
#         n_classes : numpy.ndarray, dtype=SIZE_t
#             The number of unique classes in each target
#         """
#         self.sample_weight = NULL
#
#         self.samples = NULL
#         self.start = 0
#         self.pos = 0
#         self.end = 0
#
#         self.n_outputs = n_outputs
#         self.n_samples = 0
#         self.n_node_samples = 0
#         self.weighted_n_node_samples = 0.0
#         self.weighted_n_left = 0.0
#         self.weighted_n_right = 0.0
#
#         # Count labels for each output
#         self.sum_total = NULL
#         self.sum_left = NULL
#         self.sum_right = NULL
#         self.n_classes = NULL
#
#         safe_realloc(&self.n_classes, n_outputs)
#
#         cdef SIZE_t k = 0
#         cdef SIZE_t sum_stride = 0
#
#         # For each target, set the number of unique classes in that target,
#         # and also compute the maximal stride of all targets
#         for k in range(n_outputs):
#             self.n_classes[k] = n_classes[k]
#
#             if n_classes[k] > sum_stride:
#                 sum_stride = n_classes[k]
#
#         self.sum_stride = sum_stride
#
#         cdef SIZE_t n_elements = n_outputs * sum_stride
#         self.sum_total = <double*> calloc(n_elements, sizeof(double))
#         self.sum_left = <double*> calloc(n_elements, sizeof(double))
#         self.sum_right = <double*> calloc(n_elements, sizeof(double))
#
#         if (self.sum_total == NULL or
#                 self.sum_left == NULL or
#                 self.sum_right == NULL):
#             raise MemoryError()

#         self.sample_weight = NULL
#
#         self.samples = NULL
#         self.start = 0
#         self.pos = 0
#         self.end = 0
#        self.start = 0
        self.pos = 0
        self.end = 0

        self.n_outputs = n_outputs
        self.n_samples = 0
        self.n_node_samples = 0
        self.weighted_n_node_samples = 0.0
        self.weighted_n_left = 0.0
        self.weighted_n_right = 0.0

        # Count labels for each output
        # self.sum_total = NULL
        # self.sum_left = NULL
        # self.sum_right = NULL
        # self.n_classes = NULL

        # safe_realloc(&self.n_classes, n_outputs)
        self.n_classes = np.empty(n_outputs, dtype=NP_SIZE_t)

        # k = 0
        # sum_stride = 0
        # For each target, set the number of unique classes in that target,
        # and also compute the maximal stride of all targets


        # for k in range(n_outputs):
        #     self.n_classes[k] = n_classes[k]
        #
        #     if n_classes[k] > sum_stride:
        #         sum_stride = n_classes[k]

        self.n_classes[:] = n_classes

        self.max_n_classes = np.max(self.n_classes)

        # self.sum_stride = sum_stride

        # n_elements = n_outputs * sum_stride

        # self.sum_total = <double*> calloc(n_elements, sizeof(double))
        # self.sum_left = <double*> calloc(n_elements, sizeof(double))
        # self.sum_right = <double*> calloc(n_elements, sizeof(double))
        shape = (self.n_outputs, self.max_n_classes)
        self.sum_total = np.empty(shape, dtype=NP_DOUBLE_t)
        self.sum_left = np.empty(shape, dtype=NP_DOUBLE_t)
        self.sum_right = np.empty(shape, dtype=NP_DOUBLE_t)


@njit
def classification_criterion_init(criterion, y, sample_weight, weighted_n_samples,
                                  samples, start, end):
#     cdef int init(self, const DOUBLE_t[:, ::1] y,
#                   DOUBLE_t* sample_weight, double weighted_n_samples,
#                   SIZE_t* samples, SIZE_t start, SIZE_t end) nogil except -1:
#         """Initialize the criterion.
#
#         This initializes the criterion at node samples[start:end] and children
#         samples[start:start] and samples[start:end].
#
#         Returns -1 in case of failure to allocate memory (and raise MemoryError)
#         or 0 otherwise.
#
#         Parameters
#         ----------
#         y : array-like, dtype=DOUBLE_t
#             The target stored as a buffer for memory efficiency
#         sample_weight : array-like, dtype=DOUBLE_t
#             The weight of each sample
#         weighted_n_samples : double
#             The total weight of all samples
#         samples : array-like, dtype=SIZE_t
#             A mask on the samples, showing which ones we want to use
#         start : SIZE_t
#             The first sample to use in the mask
#         end : SIZE_t
#             The last sample to use in the mask
#         """
#         self.y = y
#         self.sample_weight = sample_weight
#         self.samples = samples
#         self.start = start
#         self.end = end
#         self.n_node_samples = end - start
#         self.weighted_n_samples = weighted_n_samples
#         self.weighted_n_node_samples = 0.0
#
#         cdef SIZE_t* n_classes = self.n_classes
#         cdef double* sum_total = self.sum_total
#
#         cdef SIZE_t i
#         cdef SIZE_t p
#         cdef SIZE_t k
#         cdef SIZE_t c
#         cdef DOUBLE_t w = 1.0
#         cdef SIZE_t offset = 0
#
#         for k in range(self.n_outputs):
#             memset(sum_total + offset, 0, n_classes[k] * sizeof(double))
#             offset += self.sum_stride
#
#         for p in range(start, end):
#             i = samples[p]
#
#             # w is originally set to be 1.0, meaning that if no sample weights
#             # are given, the default weight of each sample is 1.0
#             if sample_weight != NULL:
#                 w = sample_weight[i]
#
#             # Count weighted class frequency for each target
#             for k in range(self.n_outputs):
#                 c = <SIZE_t> self.y[i, k]
#                 sum_total[k * self.sum_stride + c] += w
#
#             self.weighted_n_node_samples += w
#
#         # Reset to pos=start
#         self.reset()
#         return 0

    criterion.y = y
    criterion.sample_weight = sample_weight
    criterion.samples = samples
    criterion.start = start
    criterion.end = end
    criterion.n_node_samples = end - start
    criterion.weighted_n_samples = weighted_n_samples
    criterion.weighted_n_node_samples = 0.0

    # cdef SIZE_t* n_classes = criterion.n_classes
    # cdef double* sum_total = criterion.sum_total

    n_classes = criterion.n_classes
    sum_total = criterion.sum_total


    # cdef SIZE_t i
    # cdef SIZE_t p
    # cdef SIZE_t k
    # cdef SIZE_t c
    # cdef DOUBLE_t w = 1.0
    # cdef SIZE_t offset = 0

    w = 1.0
    # offset = 0

    # for k in range(criterion.n_outputs):
    #     # memset(sum_total + offset, 0, n_classes[k] * sizeof(double))
    #     sum_total[offset:(offset + n_classes[k])] = 0
    #     offset += criterion.sum_stride

    sum_total[:] = 0.0

    for p in range(start, end):
        i = samples[p]

        # w is originally set to be 1.0, meaning that if no sample weights
        # are given, the default weight of each sample is 1.0
        # if sample_weight != NULL:
        # TODO: faire ce test en dehors
        if sample_weight.size > 0:
            w = sample_weight[i]

        # Count weighted class frequency for each target
        for n_output in range(criterion.n_outputs):
            c = SIZE_t(criterion.y[i, n_output])
            # sum_total[n_output * criterion.sum_stride + c] += w
            sum_total[n_output, c] += w

        criterion.weighted_n_node_samples += w

    # Reset to pos=start
    # criterion.reset()
    criterion_reset(criterion)
    return 0


#
#     cdef int reverse_reset(self) nogil except -1:
#         """Reset the criterion at pos=end.
#
#         Returns -1 in case of failure to allocate memory (and raise MemoryError)
#         or 0 otherwise.
#         """
#         self.pos = self.end
#
#         self.weighted_n_left = self.weighted_n_node_samples
#         self.weighted_n_right = 0.0
#
#         cdef double* sum_total = self.sum_total
#         cdef double* sum_left = self.sum_left
#         cdef double* sum_right = self.sum_right
#
#         cdef SIZE_t* n_classes = self.n_classes
#         cdef SIZE_t k
#
#         for k in range(self.n_outputs):
#             memset(sum_right, 0, n_classes[k] * sizeof(double))
#             memcpy(sum_left, sum_total, n_classes[k] * sizeof(double))
#
#             sum_total += self.sum_stride
#             sum_left += self.sum_stride
#             sum_right += self.sum_stride
#         return 0
#
#     cdef int update(self, SIZE_t new_pos) nogil except -1:
#         """Updated statistics by moving samples[pos:new_pos] to the left child.
#
#         Returns -1 in case of failure to allocate memory (and raise MemoryError)
#         or 0 otherwise.
#
#         Parameters
#         ----------
#         new_pos : SIZE_t
#             The new ending position for which to move samples from the right
#             child to the left child.
#         """
#         cdef SIZE_t pos = self.pos
#         cdef SIZE_t end = self.end
#
#         cdef double* sum_left = self.sum_left
#         cdef double* sum_right = self.sum_right
#         cdef double* sum_total = self.sum_total
#
#         cdef SIZE_t* n_classes = self.n_classes
#         cdef SIZE_t* samples = self.samples
#         cdef DOUBLE_t* sample_weight = self.sample_weight
#
#         cdef SIZE_t i
#         cdef SIZE_t p
#         cdef SIZE_t k
#         cdef SIZE_t c
#         cdef SIZE_t label_index
#         cdef DOUBLE_t w = 1.0
#
#         # Update statistics up to new_pos
#         #
#         # Given that
#         #   sum_left[x] +  sum_right[x] = sum_total[x]
#         # and that sum_total is known, we are going to update
#         # sum_left from the direction that require the least amount
#         # of computations, i.e. from pos to new_pos or from end to new_po.
#         if (new_pos - pos) <= (end - new_pos):
#             for p in range(pos, new_pos):
#                 i = samples[p]
#
#                 if sample_weight != NULL:
#                     w = sample_weight[i]
#
#                 for k in range(self.n_outputs):
#                     label_index = k * self.sum_stride + <SIZE_t> self.y[i, k]
#                     sum_left[label_index] += w
#
#                 self.weighted_n_left += w
#
#         else:
#             self.reverse_reset()
#
#             for p in range(end - 1, new_pos - 1, -1):
#                 i = samples[p]
#
#                 if sample_weight != NULL:
#                     w = sample_weight[i]
#
#                 for k in range(self.n_outputs):
#                     label_index = k * self.sum_stride + <SIZE_t> self.y[i, k]
#                     sum_left[label_index] -= w
#
#                 self.weighted_n_left -= w
#
#         # Update right part statistics
#         self.weighted_n_right = self.weighted_n_node_samples - self.weighted_n_left
#         for k in range(self.n_outputs):
#             for c in range(n_classes[k]):
#                 sum_right[c] = sum_total[c] - sum_left[c]
#
#             sum_right += self.sum_stride
#             sum_left += self.sum_stride
#             sum_total += self.sum_stride
#
#         self.pos = new_pos
#         return 0
#
#     cdef double node_impurity(self) nogil:
#         pass
#
#     cdef void children_impurity(self, double* impurity_left,
#                                 double* impurity_right) nogil:
#         pass


@njit
def classification_criterion_node_value(criterion, dest, node_id):
#     cdef void node_value(self, double* dest) nogil:
#         """Compute the node value of samples[start:end] and save it into dest.
#
#         Parameters
#         ----------
#         dest : double pointer
#             The memory address which we will save the node value into.
#         """
#         cdef double* sum_total = self.sum_total
#         cdef SIZE_t* n_classes = self.n_classes
#         cdef SIZE_t k
#
#         for k in range(self.n_outputs):
#             memcpy(dest, sum_total, n_classes[k] * sizeof(double))
#             dest += self.sum_stride
#             sum_total += self.sum_stride

    sum_total = criterion.sum_total
    # n_classes = criterion.n_classes
    #
    # for k in range(criterion.n_outputs):
    #     # memcpy(dest, sum_total, n_classes[k] * sizeof(double))
    #
    #     dest += criterion.sum_stride
    #     sum_total += criterion.sum_stride

    dest[node_id, :, :] = sum_total

#
#
# cdef class Entropy(ClassificationCriterion):
#     r"""Cross Entropy impurity criterion.
#
#     This handles cases where the target is a classification taking values
#     0, 1, ... K-2, K-1. If node m represents a region Rm with Nm observations,
#     then let
#
#         count_k = 1 / Nm \sum_{x_i in Rm} I(yi = k)
#
#     be the proportion of class k observations in node m.
#
#     The cross-entropy is then defined as
#
#         cross-entropy = -\sum_{k=0}^{K-1} count_k log(count_k)
#     """
#
#     cdef double node_impurity(self) nogil:
#         """Evaluate the impurity of the current node.
#
#         Evaluate the cross-entropy criterion as impurity of the current node,
#         i.e. the impurity of samples[start:end]. The smaller the impurity the
#         better.
#         """
#         cdef SIZE_t* n_classes = self.n_classes
#         cdef double* sum_total = self.sum_total
#         cdef double entropy = 0.0
#         cdef double count_k
#         cdef SIZE_t k
#         cdef SIZE_t c
#
#         for k in range(self.n_outputs):
#             for c in range(n_classes[k]):
#                 count_k = sum_total[c]
#                 if count_k > 0.0:
#                     count_k /= self.weighted_n_node_samples
#                     entropy -= count_k * log(count_k)
#
#             sum_total += self.sum_stride
#
#         return entropy / self.n_outputs
#
#     cdef void children_impurity(self, double* impurity_left,
#                                 double* impurity_right) nogil:
#         """Evaluate the impurity in children nodes.
#
#         i.e. the impurity of the left child (samples[start:pos]) and the
#         impurity the right child (samples[pos:end]).
#
#         Parameters
#         ----------
#         impurity_left : double pointer
#             The memory address to save the impurity of the left node
#         impurity_right : double pointer
#             The memory address to save the impurity of the right node
#         """
#         cdef SIZE_t* n_classes = self.n_classes
#         cdef double* sum_left = self.sum_left
#         cdef double* sum_right = self.sum_right
#         cdef double entropy_left = 0.0
#         cdef double entropy_right = 0.0
#         cdef double count_k
#         cdef SIZE_t k
#         cdef SIZE_t c
#
#         for k in range(self.n_outputs):
#             for c in range(n_classes[k]):
#                 count_k = sum_left[c]
#                 if count_k > 0.0:
#                     count_k /= self.weighted_n_left
#                     entropy_left -= count_k * log(count_k)
#
#                 count_k = sum_right[c]
#                 if count_k > 0.0:
#                     count_k /= self.weighted_n_right
#                     entropy_right -= count_k * log(count_k)
#
#             sum_left += self.sum_stride
#             sum_right += self.sum_stride
#
#         impurity_left[0] = entropy_left / self.n_outputs
#         impurity_right[0] = entropy_right / self.n_outputs



# cdef class Gini(ClassificationCriterion):
#     r"""Gini Index impurity criterion.
#
#     This handles cases where the target is a classification taking values
#     0, 1, ... K-2, K-1. If node m represents a region Rm with Nm observations,
#     then let
#
#         count_k = 1/ Nm \sum_{x_i in Rm} I(yi = k)
#
#     be the proportion of class k observations in node m.
#
#     The Gini Index is then defined as:
#
#         index = \sum_{k=0}^{K-1} count_k (1 - count_k)
#               = 1 - \sum_{k=0}^{K-1} count_k ** 2
#     """
#
#     cdef double node_impurity(self) nogil:
#         """Evaluate the impurity of the current node.
#
#         Evaluate the Gini criterion as impurity of the current node,
#         i.e. the impurity of samples[start:end]. The smaller the impurity the
#         better.
#         """
#         cdef SIZE_t* n_classes = self.n_classes
#         cdef double* sum_total = self.sum_total
#         cdef double gini = 0.0
#         cdef double sq_count
#         cdef double count_k
#         cdef SIZE_t k
#         cdef SIZE_t c
#
#         for k in range(self.n_outputs):
#             sq_count = 0.0
#
#             for c in range(n_classes[k]):
#                 count_k = sum_total[c]
#                 sq_count += count_k * count_k
#
#             gini += 1.0 - sq_count / (self.weighted_n_node_samples *
#                                       self.weighted_n_node_samples)
#
#             sum_total += self.sum_stride
#
#         return gini / self.n_outputs
#
#     cdef void children_impurity(self, double* impurity_left,
#                                 double* impurity_right) nogil:
#         """Evaluate the impurity in children nodes.
#
#         i.e. the impurity of the left child (samples[start:pos]) and the
#         impurity the right child (samples[pos:end]) using the Gini index.
#
#         Parameters
#         ----------
#         impurity_left : double pointer
#             The memory address to save the impurity of the left node to
#         impurity_right : double pointer
#             The memory address to save the impurity of the right node to
#         """
#         cdef SIZE_t* n_classes = self.n_classes
#         cdef double* sum_left = self.sum_left
#         cdef double* sum_right = self.sum_right
#         cdef double gini_left = 0.0
#         cdef double gini_right = 0.0
#         cdef double sq_count_left
#         cdef double sq_count_right
#         cdef double count_k
#         cdef SIZE_t k
#         cdef SIZE_t c
#
#         for k in range(self.n_outputs):
#             sq_count_left = 0.0
#             sq_count_right = 0.0
#
#             for c in range(n_classes[k]):
#                 count_k = sum_left[c]
#                 sq_count_left += count_k * count_k
#
#                 count_k = sum_right[c]
#                 sq_count_right += count_k * count_k
#
#             gini_left += 1.0 - sq_count_left / (self.weighted_n_left *
#                                                 self.weighted_n_left)
#
#             gini_right += 1.0 - sq_count_right / (self.weighted_n_right *
#                                                   self.weighted_n_right)
#
#             sum_left += self.sum_stride
#             sum_right += self.sum_stride
#
#         impurity_left[0] = gini_left / self.n_outputs
#         impurity_right[0] = gini_right / self.n_outputs
#
#
# cdef class RegressionCriterion(Criterion):
#     r"""Abstract regression criterion.
#
#     This handles cases where the target is a continuous value, and is
#     evaluated by computing the variance of the target values left and right
#     of the split point. The computation takes linear time with `n_samples`
#     by using ::
#
#         var = \sum_i^n (y_i - y_bar) ** 2
#             = (\sum_i^n y_i ** 2) - n_samples * y_bar ** 2
#     """
#
#     def __cinit__(self, SIZE_t n_outputs, SIZE_t n_samples):
#         """Initialize parameters for this criterion.
#
#         Parameters
#         ----------
#         n_outputs : SIZE_t
#             The number of targets to be predicted
#
#         n_samples : SIZE_t
#             The total number of samples to fit on
#         """
#         # Default values
#         self.sample_weight = NULL
#
#         self.samples = NULL
#         self.start = 0
#         self.pos = 0
#         self.end = 0
#
#         self.n_outputs = n_outputs
#         self.n_samples = n_samples
#         self.n_node_samples = 0
#         self.weighted_n_node_samples = 0.0
#         self.weighted_n_left = 0.0
#         self.weighted_n_right = 0.0
#
#         self.sq_sum_total = 0.0
#
#         # Allocate accumulators. Make sure they are NULL, not uninitialized,
#         # before an exception can be raised (which triggers __dealloc__).
#         self.sum_total = NULL
#         self.sum_left = NULL
#         self.sum_right = NULL
#
#         # Allocate memory for the accumulators
#         self.sum_total = <double*> calloc(n_outputs, sizeof(double))
#         self.sum_left = <double*> calloc(n_outputs, sizeof(double))
#         self.sum_right = <double*> calloc(n_outputs, sizeof(double))
#
#         if (self.sum_total == NULL or
#                 self.sum_left == NULL or
#                 self.sum_right == NULL):
#             raise MemoryError()
#
#     def __reduce__(self):
#         return (type(self), (self.n_outputs, self.n_samples), self.__getstate__())
#
#     cdef int init(self, const DOUBLE_t[:, ::1] y, DOUBLE_t* sample_weight,
#                   double weighted_n_samples, SIZE_t* samples, SIZE_t start,
#                   SIZE_t end) nogil except -1:
#         """Initialize the criterion.
#
#         This initializes the criterion at node samples[start:end] and children
#         samples[start:start] and samples[start:end].
#         """
#         # Initialize fields
#         self.y = y
#         self.sample_weight = sample_weight
#         self.samples = samples
#         self.start = start
#         self.end = end
#         self.n_node_samples = end - start
#         self.weighted_n_samples = weighted_n_samples
#         self.weighted_n_node_samples = 0.
#
#         cdef SIZE_t i
#         cdef SIZE_t p
#         cdef SIZE_t k
#         cdef DOUBLE_t y_ik
#         cdef DOUBLE_t w_y_ik
#         cdef DOUBLE_t w = 1.0
#
#         self.sq_sum_total = 0.0
#         memset(self.sum_total, 0, self.n_outputs * sizeof(double))
#
#         for p in range(start, end):
#             i = samples[p]
#
#             if sample_weight != NULL:
#                 w = sample_weight[i]
#
#             for k in range(self.n_outputs):
#                 y_ik = self.y[i, k]
#                 w_y_ik = w * y_ik
#                 self.sum_total[k] += w_y_ik
#                 self.sq_sum_total += w_y_ik * y_ik
#
#             self.weighted_n_node_samples += w
#
#         # Reset to pos=start
#         self.reset()
#         return 0
#
#     cdef int reset(self) nogil except -1:
#         """Reset the criterion at pos=start."""
#         cdef SIZE_t n_bytes = self.n_outputs * sizeof(double)
#         memset(self.sum_left, 0, n_bytes)
#         memcpy(self.sum_right, self.sum_total, n_bytes)
#
#         self.weighted_n_left = 0.0
#         self.weighted_n_right = self.weighted_n_node_samples
#         self.pos = self.start
#         return 0
#
#     cdef int reverse_reset(self) nogil except -1:
#         """Reset the criterion at pos=end."""
#         cdef SIZE_t n_bytes = self.n_outputs * sizeof(double)
#         memset(self.sum_right, 0, n_bytes)
#         memcpy(self.sum_left, self.sum_total, n_bytes)
#
#         self.weighted_n_right = 0.0
#         self.weighted_n_left = self.weighted_n_node_samples
#         self.pos = self.end
#         return 0
#
#     cdef int update(self, SIZE_t new_pos) nogil except -1:
#         """Updated statistics by moving samples[pos:new_pos] to the left."""
#         cdef double* sum_left = self.sum_left
#         cdef double* sum_right = self.sum_right
#         cdef double* sum_total = self.sum_total
#
#         cdef double* sample_weight = self.sample_weight
#         cdef SIZE_t* samples = self.samples
#
#         cdef SIZE_t pos = self.pos
#         cdef SIZE_t end = self.end
#         cdef SIZE_t i
#         cdef SIZE_t p
#         cdef SIZE_t k
#         cdef DOUBLE_t w = 1.0
#
#         # Update statistics up to new_pos
#         #
#         # Given that
#         #           sum_left[x] +  sum_right[x] = sum_total[x]
#         # and that sum_total is known, we are going to update
#         # sum_left from the direction that require the least amount
#         # of computations, i.e. from pos to new_pos or from end to new_pos.
#         if (new_pos - pos) <= (end - new_pos):
#             for p in range(pos, new_pos):
#                 i = samples[p]
#
#                 if sample_weight != NULL:
#                     w = sample_weight[i]
#
#                 for k in range(self.n_outputs):
#                     sum_left[k] += w * self.y[i, k]
#
#                 self.weighted_n_left += w
#         else:
#             self.reverse_reset()
#
#             for p in range(end - 1, new_pos - 1, -1):
#                 i = samples[p]
#
#                 if sample_weight != NULL:
#                     w = sample_weight[i]
#
#                 for k in range(self.n_outputs):
#                     sum_left[k] -= w * self.y[i, k]
#
#                 self.weighted_n_left -= w
#
#         self.weighted_n_right = (self.weighted_n_node_samples -
#                                  self.weighted_n_left)
#         for k in range(self.n_outputs):
#             sum_right[k] = sum_total[k] - sum_left[k]
#
#         self.pos = new_pos
#         return 0
#
#     cdef double node_impurity(self) nogil:
#         pass
#
#     cdef void children_impurity(self, double* impurity_left,
#                                 double* impurity_right) nogil:
#         pass
#
#     cdef void node_value(self, double* dest) nogil:
#         """Compute the node value of samples[start:end] into dest."""
#         cdef SIZE_t k
#
#         for k in range(self.n_outputs):
#             dest[k] = self.sum_total[k] / self.weighted_n_node_samples
#
#
# cdef class MSE(RegressionCriterion):
#     """Mean squared error impurity criterion.
#
#         MSE = var_left + var_right
#     """
#
#     cdef double node_impurity(self) nogil:
#         """Evaluate the impurity of the current node.
#
#         Evaluate the MSE criterion as impurity of the current node,
#         i.e. the impurity of samples[start:end]. The smaller the impurity the
#         better.
#         """
#         cdef double* sum_total = self.sum_total
#         cdef double impurity
#         cdef SIZE_t k
#
#         impurity = self.sq_sum_total / self.weighted_n_node_samples
#         for k in range(self.n_outputs):
#             impurity -= (sum_total[k] / self.weighted_n_node_samples)**2.0
#
#         return impurity / self.n_outputs
#
#     cdef double proxy_impurity_improvement(self) nogil:
#         """Compute a proxy of the impurity reduction.
#
#         This method is used to speed up the search for the best split.
#         It is a proxy quantity such that the split that maximizes this value
#         also maximizes the impurity improvement. It neglects all constant terms
#         of the impurity decrease for a given split.
#
#         The absolute impurity improvement is only computed by the
#         impurity_improvement method once the best split has been found.
#         """
#         cdef double* sum_left = self.sum_left
#         cdef double* sum_right = self.sum_right
#
#         cdef SIZE_t k
#         cdef double proxy_impurity_left = 0.0
#         cdef double proxy_impurity_right = 0.0
#
#         for k in range(self.n_outputs):
#             proxy_impurity_left += sum_left[k] * sum_left[k]
#             proxy_impurity_right += sum_right[k] * sum_right[k]
#
#         return (proxy_impurity_left / self.weighted_n_left +
#                 proxy_impurity_right / self.weighted_n_right)
#
#     cdef void children_impurity(self, double* impurity_left,
#                                 double* impurity_right) nogil:
#         """Evaluate the impurity in children nodes.
#
#         i.e. the impurity of the left child (samples[start:pos]) and the
#         impurity the right child (samples[pos:end]).
#         """
#         cdef DOUBLE_t* sample_weight = self.sample_weight
#         cdef SIZE_t* samples = self.samples
#         cdef SIZE_t pos = self.pos
#         cdef SIZE_t start = self.start
#
#         cdef double* sum_left = self.sum_left
#         cdef double* sum_right = self.sum_right
#         cdef DOUBLE_t y_ik
#
#         cdef double sq_sum_left = 0.0
#         cdef double sq_sum_right
#
#         cdef SIZE_t i
#         cdef SIZE_t p
#         cdef SIZE_t k
#         cdef DOUBLE_t w = 1.0
#
#         for p in range(start, pos):
#             i = samples[p]
#
#             if sample_weight != NULL:
#                 w = sample_weight[i]
#
#             for k in range(self.n_outputs):
#                 y_ik = self.y[i, k]
#                 sq_sum_left += w * y_ik * y_ik
#
#         sq_sum_right = self.sq_sum_total - sq_sum_left
#
#         impurity_left[0] = sq_sum_left / self.weighted_n_left
#         impurity_right[0] = sq_sum_right / self.weighted_n_right
#
#         for k in range(self.n_outputs):
#             impurity_left[0] -= (sum_left[k] / self.weighted_n_left) ** 2.0
#             impurity_right[0] -= (sum_right[k] / self.weighted_n_right) ** 2.0
#
#         impurity_left[0] /= self.n_outputs
#         impurity_right[0] /= self.n_outputs
#
#
# cdef class MAE(RegressionCriterion):
#     r"""Mean absolute error impurity criterion.
#
#        MAE = (1 / n)*(\sum_i |y_i - f_i|), where y_i is the true
#        value and f_i is the predicted value."""
#
#     def __dealloc__(self):
#         """Destructor."""
#         free(self.node_medians)
#
#     cdef np.ndarray left_child
#     cdef np.ndarray right_child
#     cdef DOUBLE_t* node_medians
#
#     def __cinit__(self, SIZE_t n_outputs, SIZE_t n_samples):
#         """Initialize parameters for this criterion.
#
#         Parameters
#         ----------
#         n_outputs : SIZE_t
#             The number of targets to be predicted
#
#         n_samples : SIZE_t
#             The total number of samples to fit on
#         """
#         # Default values
#         self.sample_weight = NULL
#
#         self.samples = NULL
#         self.start = 0
#         self.pos = 0
#         self.end = 0
#
#         self.n_outputs = n_outputs
#         self.n_samples = n_samples
#         self.n_node_samples = 0
#         self.weighted_n_node_samples = 0.0
#         self.weighted_n_left = 0.0
#         self.weighted_n_right = 0.0
#
#         # Allocate accumulators. Make sure they are NULL, not uninitialized,
#         # before an exception can be raised (which triggers __dealloc__).
#         self.node_medians = NULL
#
#         # Allocate memory for the accumulators
#         safe_realloc(&self.node_medians, n_outputs)
#
#         self.left_child = np.empty(n_outputs, dtype='object')
#         self.right_child = np.empty(n_outputs, dtype='object')
#         # initialize WeightedMedianCalculators
#         for k in range(n_outputs):
#             self.left_child[k] = WeightedMedianCalculator(n_samples)
#             self.right_child[k] = WeightedMedianCalculator(n_samples)
#
#     cdef int init(self, const DOUBLE_t[:, ::1] y, DOUBLE_t* sample_weight,
#                   double weighted_n_samples, SIZE_t* samples, SIZE_t start,
#                   SIZE_t end) nogil except -1:
#         """Initialize the criterion.
#
#         This initializes the criterion at node samples[start:end] and children
#         samples[start:start] and samples[start:end].
#         """
#         cdef SIZE_t i, p, k
#         cdef DOUBLE_t w = 1.0
#
#         # Initialize fields
#         self.y = y
#         self.sample_weight = sample_weight
#         self.samples = samples
#         self.start = start
#         self.end = end
#         self.n_node_samples = end - start
#         self.weighted_n_samples = weighted_n_samples
#         self.weighted_n_node_samples = 0.
#
#         cdef void** left_child
#         cdef void** right_child
#
#         left_child = <void**> self.left_child.data
#         right_child = <void**> self.right_child.data
#
#         for k in range(self.n_outputs):
#             (<WeightedMedianCalculator> left_child[k]).reset()
#             (<WeightedMedianCalculator> right_child[k]).reset()
#
#         for p in range(start, end):
#             i = samples[p]
#
#             if sample_weight != NULL:
#                 w = sample_weight[i]
#
#             for k in range(self.n_outputs):
#                 # push method ends up calling safe_realloc, hence `except -1`
#                 # push all values to the right side,
#                 # since pos = start initially anyway
#                 (<WeightedMedianCalculator> right_child[k]).push(self.y[i, k], w)
#
#             self.weighted_n_node_samples += w
#         # calculate the node medians
#         for k in range(self.n_outputs):
#             self.node_medians[k] = (<WeightedMedianCalculator> right_child[k]).get_median()
#
#         # Reset to pos=start
#         self.reset()
#         return 0
#
#     cdef int reset(self) nogil except -1:
#         """Reset the criterion at pos=start.
#
#         Returns -1 in case of failure to allocate memory (and raise MemoryError)
#         or 0 otherwise.
#         """
#         cdef SIZE_t i, k
#         cdef DOUBLE_t value
#         cdef DOUBLE_t weight
#
#         cdef void** left_child = <void**> self.left_child.data
#         cdef void** right_child = <void**> self.right_child.data
#
#         self.weighted_n_left = 0.0
#         self.weighted_n_right = self.weighted_n_node_samples
#         self.pos = self.start
#
#         # reset the WeightedMedianCalculators, left should have no
#         # elements and right should have all elements.
#
#         for k in range(self.n_outputs):
#             # if left has no elements, it's already reset
#             for i in range((<WeightedMedianCalculator> left_child[k]).size()):
#                 # remove everything from left and put it into right
#                 (<WeightedMedianCalculator> left_child[k]).pop(&value,
#                                                                &weight)
#                 # push method ends up calling safe_realloc, hence `except -1`
#                 (<WeightedMedianCalculator> right_child[k]).push(value,
#                                                                  weight)
#         return 0
#
#     cdef int reverse_reset(self) nogil except -1:
#         """Reset the criterion at pos=end.
#
#         Returns -1 in case of failure to allocate memory (and raise MemoryError)
#         or 0 otherwise.
#         """
#         self.weighted_n_right = 0.0
#         self.weighted_n_left = self.weighted_n_node_samples
#         self.pos = self.end
#
#         cdef DOUBLE_t value
#         cdef DOUBLE_t weight
#         cdef void** left_child = <void**> self.left_child.data
#         cdef void** right_child = <void**> self.right_child.data
#
#         # reverse reset the WeightedMedianCalculators, right should have no
#         # elements and left should have all elements.
#         for k in range(self.n_outputs):
#             # if right has no elements, it's already reset
#             for i in range((<WeightedMedianCalculator> right_child[k]).size()):
#                 # remove everything from right and put it into left
#                 (<WeightedMedianCalculator> right_child[k]).pop(&value,
#                                                                 &weight)
#                 # push method ends up calling safe_realloc, hence `except -1`
#                 (<WeightedMedianCalculator> left_child[k]).push(value,
#                                                                 weight)
#         return 0
#
#     cdef int update(self, SIZE_t new_pos) nogil except -1:
#         """Updated statistics by moving samples[pos:new_pos] to the left.
#
#         Returns -1 in case of failure to allocate memory (and raise MemoryError)
#         or 0 otherwise.
#         """
#         cdef DOUBLE_t* sample_weight = self.sample_weight
#         cdef SIZE_t* samples = self.samples
#
#         cdef void** left_child = <void**> self.left_child.data
#         cdef void** right_child = <void**> self.right_child.data
#
#         cdef SIZE_t pos = self.pos
#         cdef SIZE_t end = self.end
#         cdef SIZE_t i, p, k
#         cdef DOUBLE_t w = 1.0
#
#         # Update statistics up to new_pos
#         #
#         # We are going to update right_child and left_child
#         # from the direction that require the least amount of
#         # computations, i.e. from pos to new_pos or from end to new_pos.
#         if (new_pos - pos) <= (end - new_pos):
#             for p in range(pos, new_pos):
#                 i = samples[p]
#
#                 if sample_weight != NULL:
#                     w = sample_weight[i]
#
#                 for k in range(self.n_outputs):
#                     # remove y_ik and its weight w from right and add to left
#                     (<WeightedMedianCalculator> right_child[k]).remove(self.y[i, k], w)
#                     # push method ends up calling safe_realloc, hence except -1
#                     (<WeightedMedianCalculator> left_child[k]).push(self.y[i, k], w)
#
#                 self.weighted_n_left += w
#         else:
#             self.reverse_reset()
#
#             for p in range(end - 1, new_pos - 1, -1):
#                 i = samples[p]
#
#                 if sample_weight != NULL:
#                     w = sample_weight[i]
#
#                 for k in range(self.n_outputs):
#                     # remove y_ik and its weight w from left and add to right
#                     (<WeightedMedianCalculator> left_child[k]).remove(self.y[i, k], w)
#                     (<WeightedMedianCalculator> right_child[k]).push(self.y[i, k], w)
#
#                 self.weighted_n_left -= w
#
#         self.weighted_n_right = (self.weighted_n_node_samples -
#                                  self.weighted_n_left)
#         self.pos = new_pos
#         return 0
#
#     cdef void node_value(self, double* dest) nogil:
#         """Computes the node value of samples[start:end] into dest."""
#         cdef SIZE_t k
#         for k in range(self.n_outputs):
#             dest[k] = <double> self.node_medians[k]
#
#     cdef double node_impurity(self) nogil:
#         """Evaluate the impurity of the current node.
#
#         Evaluate the MAE criterion as impurity of the current node,
#         i.e. the impurity of samples[start:end]. The smaller the impurity the
#         better.
#         """
#         cdef DOUBLE_t* sample_weight = self.sample_weight
#         cdef SIZE_t* samples = self.samples
#         cdef SIZE_t i, p, k
#         cdef DOUBLE_t w = 1.0
#         cdef DOUBLE_t impurity = 0.0
#
#         for k in range(self.n_outputs):
#             for p in range(self.start, self.end):
#                 i = samples[p]
#
#                 if sample_weight != NULL:
#                     w = sample_weight[i]
#
#                 impurity += fabs(self.y[i, k] - self.node_medians[k]) * w
#
#         return impurity / (self.weighted_n_node_samples * self.n_outputs)
#
#     cdef void children_impurity(self, double* p_impurity_left,
#                                 double* p_impurity_right) nogil:
#         """Evaluate the impurity in children nodes.
#
#         i.e. the impurity of the left child (samples[start:pos]) and the
#         impurity the right child (samples[pos:end]).
#         """
#         cdef DOUBLE_t* sample_weight = self.sample_weight
#         cdef SIZE_t* samples = self.samples
#
#         cdef SIZE_t start = self.start
#         cdef SIZE_t pos = self.pos
#         cdef SIZE_t end = self.end
#
#         cdef SIZE_t i, p, k
#         cdef DOUBLE_t median
#         cdef DOUBLE_t w = 1.0
#         cdef DOUBLE_t impurity_left = 0.0
#         cdef DOUBLE_t impurity_right = 0.0
#
#         cdef void** left_child = <void**> self.left_child.data
#         cdef void** right_child = <void**> self.right_child.data
#
#         for k in range(self.n_outputs):
#             median = (<WeightedMedianCalculator> left_child[k]).get_median()
#             for p in range(start, pos):
#                 i = samples[p]
#
#                 if sample_weight != NULL:
#                     w = sample_weight[i]
#
#                 impurity_left += fabs(self.y[i, k] - median) * w
#         p_impurity_left[0] = impurity_left / (self.weighted_n_left *
#                                               self.n_outputs)
#
#         for k in range(self.n_outputs):
#             median = (<WeightedMedianCalculator> right_child[k]).get_median()
#             for p in range(pos, end):
#                 i = samples[p]
#
#                 if sample_weight != NULL:
#                     w = sample_weight[i]
#
#                 impurity_right += fabs(self.y[i, k] - median) * w
#         p_impurity_right[0] = impurity_right / (self.weighted_n_right *
#                                                 self.n_outputs)
#
#
# cdef class FriedmanMSE(MSE):
#     """Mean squared error impurity criterion with improvement score by Friedman.
#
#     Uses the formula (35) in Friedman's original Gradient Boosting paper:
#
#         diff = mean_left - mean_right
#         improvement = n_left * n_right * diff^2 / (n_left + n_right)
#     """
#
#     cdef double proxy_impurity_improvement(self) nogil:
#         """Compute a proxy of the impurity reduction.
#
#         This method is used to speed up the search for the best split.
#         It is a proxy quantity such that the split that maximizes this value
#         also maximizes the impurity improvement. It neglects all constant terms
#         of the impurity decrease for a given split.
#
#         The absolute impurity improvement is only computed by the
#         impurity_improvement method once the best split has been found.
#         """
#         cdef double* sum_left = self.sum_left
#         cdef double* sum_right = self.sum_right
#
#         cdef double total_sum_left = 0.0
#         cdef double total_sum_right = 0.0
#
#         cdef SIZE_t k
#         cdef double diff = 0.0
#
#         for k in range(self.n_outputs):
#             total_sum_left += sum_left[k]
#             total_sum_right += sum_right[k]
#
#         diff = (self.weighted_n_right * total_sum_left -
#                 self.weighted_n_left * total_sum_right)
#
#         return diff * diff / (self.weighted_n_left * self.weighted_n_right)
#
#     cdef double impurity_improvement(self, double impurity_parent, double
#                                      impurity_left, double impurity_right) nogil:
#         # Note: none of the arguments are used here
#         cdef double* sum_left = self.sum_left
#         cdef double* sum_right = self.sum_right
#
#         cdef double total_sum_left = 0.0
#         cdef double total_sum_right = 0.0
#
#         cdef SIZE_t k
#         cdef double diff = 0.0
#
#         for k in range(self.n_outputs):
#             total_sum_left += sum_left[k]
#             total_sum_right += sum_right[k]
#
#         diff = (self.weighted_n_right * total_sum_left -
#                 self.weighted_n_left * total_sum_right) / self.n_outputs
#
#         return (diff * diff / (self.weighted_n_left * self.weighted_n_right *
#                                self.weighted_n_node_samples))
#
#
# cdef class Poisson(RegressionCriterion):
#     """Half Poisson deviance as impurity criterion.
#
#     Poisson deviance = 2/n * sum(y_true * log(y_true/y_pred) + y_pred - y_true)
#
#     Note that the deviance is >= 0, and since we have `y_pred = mean(y_true)`
#     at the leaves, one always has `sum(y_pred - y_true) = 0`. It remains the
#     implemented impurity:
#         1/n * sum(y_true * log(y_true/y_pred)
#     """
#     # FIXME in 0.25:
#     # min_impurity_split with default = 0 forces us to use a non-negative
#     # impurity like the Poisson deviance. Without this restriction, one could
#     # throw away the 'constant' term sum(y_true * log(y_true)) and just use
#     # Poisson loss = - 1/n * sum(y_true * log(y_pred))
#     #              = - 1/n * sum(y_true * log(mean(y_true))
#     #              = - mean(y_true) * log(mean(y_true))
#     # With this trick (used in proxy_impurity_improvement()), as for MSE,
#     # children_impurity would only need to go over left xor right split, not
#     # both. This could be faster.
#
#     cdef double node_impurity(self) nogil:
#         """Evaluate the impurity of the current node.
#
#         Evaluate the Poisson criterion as impurity of the current node,
#         i.e. the impurity of samples[start:end]. The smaller the impurity the
#         better.
#         """
#         return self.poisson_loss(self.start, self.end, self.sum_total,
#                                  self.weighted_n_node_samples)
#
#     cdef double proxy_impurity_improvement(self) nogil:
#         """Compute a proxy of the impurity reduction.
#
#         This method is used to speed up the search for the best split.
#         It is a proxy quantity such that the split that maximizes this value
#         also maximizes the impurity improvement. It neglects all constant terms
#         of the impurity decrease for a given split.
#
#         The absolute impurity improvement is only computed by the
#         impurity_improvement method once the best split has been found.
#
#         Poisson proxy is:
#             - 1/n * sum(y_i * log(y_pred)) = -mean(y_i) * log(mean(y_i))
#         """
#         cdef SIZE_t k
#         cdef double proxy_impurity_left = 0.0
#         cdef double proxy_impurity_right = 0.0
#         cdef double y_mean_left = 0.
#         cdef double y_mean_right = 0.
#
#         for k in range(self.n_outputs):
#             if (self.sum_left[k] <= EPSILON) or (self.sum_right[k] <= EPSILON):
#                 # Poisson loss does not allow non-positive predictions. We
#                 # therefore forbid splits that have child nodes with
#                 # sum(y_i) <= 0.
#                 # Since sum_right = sum_total - sum_left, it can lead to
#                 # floating point rounding error and will not give zero. Thus,
#                 # we relax the above comparison to sum(y_i) <= EPSILON.
#                 return -INFINITY
#             else:
#                 y_mean_left = self.sum_left[k] / self.weighted_n_left
#                 y_mean_right = self.sum_right[k] / self.weighted_n_right
#                 proxy_impurity_left -= y_mean_left * log(y_mean_left)
#                 proxy_impurity_right -= y_mean_right * log(y_mean_right)
#
#         return - proxy_impurity_left - proxy_impurity_right
#
#     cdef void children_impurity(self, double* impurity_left,
#                                 double* impurity_right) nogil:
#         """Evaluate the impurity in children nodes.
#
#         i.e. the impurity of the left child (samples[start:pos]) and the
#         impurity of the right child (samples[pos:end]) for Poisson.
#         """
#         cdef const DOUBLE_t[:, ::1] y = self.y
#
#         cdef SIZE_t start = self.start
#         cdef SIZE_t pos = self.pos
#         cdef SIZE_t end = self.end
#
#         cdef SIZE_t i, p, k
#         cdef DOUBLE_t y_mean = 0.
#         cdef DOUBLE_t w = 1.0
#
#         impurity_left[0] = self.poisson_loss(start, pos, self.sum_left,
#                                              self.weighted_n_left)
#
#         impurity_right[0] = self.poisson_loss(pos, end, self.sum_right,
#                                               self.weighted_n_right)
#
#     cdef inline DOUBLE_t poisson_loss(self,
#                                       SIZE_t start,
#                                       SIZE_t end,
#                                       DOUBLE_t* y_sum,
#                                       DOUBLE_t weight_sum) nogil:
#         """Helper function to compute Poisson loss (~deviance) of a given node.
#         """
#         cdef const DOUBLE_t[:, ::1] y = self.y
#         cdef DOUBLE_t* weight = self.sample_weight
#
#         cdef DOUBLE_t y_mean = 0.
#         cdef DOUBLE_t poisson_loss = 0.
#         cdef DOUBLE_t w = 1.0
#         cdef SIZE_t n_outputs = self.n_outputs
#
#         for k in range(n_outputs):
#             if y_sum[k] <= EPSILON:
#                 # y_sum could be computed from the subtraction
#                 # sum_right = sum_total - sum_left leading to a potential
#                 # floating point rounding error.
#                 # Thus, we relax the comparison y_sum <= 0 to
#                 # y_sum <= EPSILON.
#                 return INFINITY
#
#             y_mean = y_sum[k] / weight_sum
#
#             for p in range(start, end):
#                 i = self.samples[p]
#
#                 if weight != NULL:
#                     w = weight[i]
#
#                 poisson_loss += w * xlogy(y[i, k], y[i, k] / y_mean)
#         return poisson_loss / (weight_sum * n_outputs)

    # criterion.y = y
    # criterion.sample_weight = sample_weight
    # criterion.samples = samples
    # criterion.start = start
    # criterion.end = end
    # criterion.n_node_samples = end - start
    # criterion.weighted_n_samples = weighted_n_samples
    # criterion.weighted_n_node_samples = 0.0
    #
    # n_classes = criterion.n_classes
    # sum_total = criterion.sum_total
    #
    # w = 1.0
    # offset = 0
    #
    # for k in range(criterion.n_outputs):
    #     # memset(sum_total + offset, 0, n_classes[k] * sizeof(double))
    #     sum_total[offset, n_classes[k]] = 0
    #     offset += criterion.sum_stride
    #
    # for p in range(start, end):
    #     i = samples[p]
    #
    #     # w is originally set to be 1.0, meaning that if no sample weights
    #     # are given, the default weight of each sample is 1.0
    #     if sample_weight.shape[0] != 0:
    #         w = sample_weight[i]
    #
    #     # Count weighted class frequency for each target
    #     for k in range(criterion.n_outputs):
    #         c = SIZE_t(criterion.y[i, k])
    #         sum_total[k * criterion.sum_stride + c] += w
    #
    #     criterion.weighted_n_node_samples += w
    #
    # # Reset to pos=start
    # # criterion.reset()
    # criterion_reset(criterion)
#
# @njit
# def criterion_init(criterion, y, sample_weight, weighted_n_samples, samples, start,
#                    end):
#     pass


@njit
def criterion_reset(criterion):
    #     ClassificationCriterion.reset
    #     cdef int reset(self) nogil except -1:
    #         """Reset the criterion at pos=start.
    #
    #         Returns -1 in case of failure to allocate memory (and raise MemoryError)
    #         or 0 otherwise.
    #         """
    #         self.pos = self.start
    #
    #         self.weighted_n_left = 0.0
    #         self.weighted_n_right = self.weighted_n_node_samples
    #
    #         cdef double* sum_total = self.sum_total
    #         cdef double* sum_left = self.sum_left
    #         cdef double* sum_right = self.sum_right
    #
    #         cdef SIZE_t* n_classes = self.n_classes
    #         cdef SIZE_t k
    #
    #         for k in range(self.n_outputs):
    #             memset(sum_left, 0, n_classes[k] * sizeof(double))
    #             memcpy(sum_right, sum_total, n_classes[k] * sizeof(double))
    #
    #             sum_total += self.sum_stride
    #             sum_left += self.sum_stride
    #             sum_right += self.sum_stride
    #         return 0
    criterion.pos = criterion.start
    criterion.weighted_n_left = 0.0
    criterion.weighted_n_right = criterion.weighted_n_node_samples

    sum_total = criterion.sum_total
    sum_left = criterion.sum_left
    sum_right = criterion.sum_right

    # n_classes = criterion.n_classes
    # criterion.max
    # cdef SIZE_t k
    # idx_sum_total = 0
    # idx_sum_left = 0
    # idx_sum_right = 0

    # for k in range(criterion.n_outputs):
    #     # memset(sum_left, 0, n_classes[k] * sizeof(double))
    #     sum_left[idx_sum_left:n_classes[k]] = 0
    #     # memcpy(sum_right, sum_total, n_classes[k] * sizeof(double))
    #     sum_right[idx_sum_right:n_classes[k]] = sum_total[idx_sum_total:n_classes[k]]
    #
    #     # sum_total += criterion.sum_stride
    #     idx_sum_total += criterion.sum_stride
    #     # sum_left += criterion.sum_stride
    #     idx_sum_left += criterion.sum_stride
    #     # sum_right += criterion.sum_stride
    #     idx_sum_right += criterion.sum_stride

    sum_left[:, :] = 0
    sum_right[:, :] = sum_total


@njit
def criterion_reverse_reset(criterion):
#     cdef int reverse_reset(self) nogil except -1:
#         """Reset the criterion at pos=end.
#
#         Returns -1 in case of failure to allocate memory (and raise MemoryError)
#         or 0 otherwise.
#         """
#         self.pos = self.end
#
#         self.weighted_n_left = self.weighted_n_node_samples
#         self.weighted_n_right = 0.0
#
#         cdef double* sum_total = self.sum_total
#         cdef double* sum_left = self.sum_left
#         cdef double* sum_right = self.sum_right
#
#         cdef SIZE_t* n_classes = self.n_classes
#         cdef SIZE_t k
#
#         for k in range(self.n_outputs):
#             memset(sum_right, 0, n_classes[k] * sizeof(double))
#             memcpy(sum_left, sum_total, n_classes[k] * sizeof(double))
#
#             sum_total += self.sum_stride
#             sum_left += self.sum_stride
#             sum_right += self.sum_stride
#         return 0
    criterion.pos = criterion.end
    criterion.weighted_n_left = criterion.weighted_n_node_samples
    criterion.weighted_n_right = 0.0

    sum_total = criterion.sum_total
    sum_left = criterion.sum_left
    sum_right = criterion.sum_right

    # n_classes = criterion.n_classes
    # cdef SIZE_t k

    # idx_sum_total = 0
    # idx_sum_left = 0
    # idx_sum_right = 0

    # for k in range(criterion.n_outputs):
    #     # memset(sum_right, 0, n_classes[k] * sizeof(double))
    #     sum_right[idx_sum_right:n_classes[k]] = 0
    #     # memcpy(sum_left, sum_total, n_classes[k] * sizeof(double))
    #     sum_left[idx_sum_left:n_classes[k]] = sum_total[idx_sum_total:n_classes[k]]
    #     # sum_total += criterion.sum_stride
    #     idx_sum_total += criterion.sum_stride
    #     idx_sum_left += criterion.sum_stride
    #     idx_sum_right += criterion.sum_stride

    sum_right[:, :] = 0
    sum_left[:, :] = sum_total


@njit
def criterion_update(criterion, new_pos):
#     cdef int update(self, SIZE_t new_pos) nogil except -1:
#         """Updated statistics by moving samples[pos:new_pos] to the left child.
#
#         Returns -1 in case of failure to allocate memory (and raise MemoryError)
#         or 0 otherwise.
#
#         Parameters
#         ----------
#         new_pos : SIZE_t
#             The new ending position for which to move samples from the right
#             child to the left child.
#         """
#         cdef SIZE_t pos = self.pos
#         cdef SIZE_t end = self.end
#
#         cdef double* sum_left = self.sum_left
#         cdef double* sum_right = self.sum_right
#         cdef double* sum_total = self.sum_total
#
#         cdef SIZE_t* n_classes = self.n_classes
#         cdef SIZE_t* samples = self.samples
#         cdef DOUBLE_t* sample_weight = self.sample_weight
#
#         cdef SIZE_t i
#         cdef SIZE_t p
#         cdef SIZE_t k
#         cdef SIZE_t c
#         cdef SIZE_t label_index
#         cdef DOUBLE_t w = 1.0
#
#         # Update statistics up to new_pos
#         #
#         # Given that
#         #   sum_left[x] +  sum_right[x] = sum_total[x]
#         # and that sum_total is known, we are going to update
#         # sum_left from the direction that require the least amount
#         # of computations, i.e. from pos to new_pos or from end to new_po.
#         if (new_pos - pos) <= (end - new_pos):
#             for p in range(pos, new_pos):
#                 i = samples[p]
#
#                 if sample_weight != NULL:
#                     w = sample_weight[i]
#
#                 for k in range(self.n_outputs):
#                     label_index = k * self.sum_stride + <SIZE_t> self.y[i, k]
#                     sum_left[label_index] += w
#
#                 self.weighted_n_left += w
#
#         else:
#             self.reverse_reset()
#
#             for p in range(end - 1, new_pos - 1, -1):
#                 i = samples[p]
#
#                 if sample_weight != NULL:
#                     w = sample_weight[i]
#
#                 for k in range(self.n_outputs):
#                     label_index = k * self.sum_stride + <SIZE_t> self.y[i, k]
#                     sum_left[label_index] -= w
#
#                 self.weighted_n_left -= w
#
#         # Update right part statistics
#         self.weighted_n_right = self.weighted_n_node_samples - self.weighted_n_left
#         for k in range(self.n_outputs):
#             for c in range(n_classes[k]):
#                 sum_right[c] = sum_total[c] - sum_left[c]
#
#             sum_right += self.sum_stride
#             sum_left += self.sum_stride
#             sum_total += self.sum_stride
#
#         self.pos = new_pos
#         return 0
#
#     cdef double node_impurity(self) nogil:
#         pass
#
#     cdef void children_impurity(self, double* impurity_left,
#                                 double* impurity_right) nogil:
#         pass
#
#     cdef void node_value(self, double* dest) nogil:
#         """Compute the node value of samples[start:end] and save it into dest.
#
#         Parameters
#         ----------
#         dest : double pointer
#             The memory address which we will save the node value into.
#         """
#         cdef double* sum_total = self.sum_total
#         cdef SIZE_t* n_classes = self.n_classes
#         cdef SIZE_t k
#
#         for k in range(self.n_outputs):
#             memcpy(dest, sum_total, n_classes[k] * sizeof(double))
#             dest += self.sum_stride
#             sum_total += self.sum_stride

    pos = criterion.pos
    end = criterion.end

    sum_left = criterion.sum_left
    sum_right = criterion.sum_right
    sum_total = criterion.sum_total

    n_classes = criterion.n_classes
    samples = criterion.samples
    sample_weight = criterion.sample_weight

    # cdef SIZE_t i
    # cdef SIZE_t p
    # cdef SIZE_t k
    # cdef SIZE_t c
    # cdef SIZE_t label_index
    # cdef DOUBLE_t w = 1.0
    w = 1.0

    # Update statistics up to new_pos
    #
    # Given that
    #   sum_left[x] +  sum_right[x] = sum_total[x]
    # and that sum_total is known, we are going to update
    # sum_left from the direction that require the least amount
    # of computations, i.e. from pos to new_pos or from end to new_po.
    if (new_pos - pos) <= (end - new_pos):
        for p in range(pos, new_pos):
            i = samples[p]

            #if sample_weight != NULL:
            if sample_weight.size > 0:
                w = sample_weight[i]

            for k in range(criterion.n_outputs):
                # label_index = k * criterion.sum_stride + SIZE_t(criterion.y[i, k])
                c = SIZE_t(criterion.y[i, k])
                sum_left[k, c] += w
                # sum_left[label_index] += w

            criterion.weighted_n_left += w

    else:
        criterion_reverse_reset(criterion)
        # criterion.reverse_reset()

        for p in range(end - 1, new_pos - 1, -1):
            i = samples[p]

            if sample_weight.shape[0] != 0:
                w = sample_weight[i]

            for k in range(criterion.n_outputs):
                # label_index = k * criterion.sum_stride + SIZE_t(criterion.y[i, k])
                c = SIZE_t(criterion.y[i, k])
                sum_left[k, c] -= w

            criterion.weighted_n_left -= w

    # Update right part statistics
    criterion.weighted_n_right = criterion.weighted_n_node_samples - criterion.weighted_n_left

    # idx_sum_total = 0
    # idx_sum_left = 0
    # idx_sum_right = 0
    #
    # for k in range(criterion.n_outputs):
    #     # TODO : c'est pas terrible ca
    #     for c in range(n_classes[k]):
    #
    #         # sum_right[c] = sum_total[c] - sum_left[c]
    #         sum_right[idx_sum_right + c] = sum_total[idx_sum_total + c] - sum_left[
    #             idx_sum_left + c]
    #
    #     idx_sum_total += criterion.sum_stride
    #     idx_sum_left += criterion.sum_stride
    #     idx_sum_right += criterion.sum_stride

    sum_right[:] = sum_total - sum_left

    criterion.pos = new_pos
    return 0


@jitclass(spec_classification_criterion)
class Gini(object):
    # cdef class Gini(ClassificationCriterion):
    #     r"""Gini Index impurity criterion.
    #
    #     This handles cases where the target is a classification taking values
    #     0, 1, ... K-2, K-1. If node m represents a region Rm with Nm observations,
    #     then let
    #
    #         count_k = 1/ Nm \sum_{x_i in Rm} I(yi = k)
    #
    #     be the proportion of class k observations in node m.
    #
    #     The Gini Index is then defined as:
    #
    #         index = \sum_{k=0}^{K-1} count_k (1 - count_k)
    #               = 1 - \sum_{k=0}^{K-1} count_k ** 2
    #     """

    # NB : It's a copy paste of the __init__ of ClassificationCriterion
    def __init__(self, n_outputs, n_classes):
        self.pos = 0
        self.end = 0

        self.n_outputs = n_outputs
        self.n_samples = 0
        self.n_node_samples = 0
        self.weighted_n_node_samples = 0.0
        self.weighted_n_left = 0.0
        self.weighted_n_right = 0.0

        # Count labels for each output
        # self.sum_total = NULL
        # self.sum_left = NULL
        # self.sum_right = NULL
        # self.n_classes = NULL

        # safe_realloc(&self.n_classes, n_outputs)
        self.n_classes = np.empty(n_outputs, dtype=NP_SIZE_t)

        # k = 0
        # sum_stride = 0
        # For each target, set the number of unique classes in that target,
        # and also compute the maximal stride of all targets


        # for k in range(n_outputs):
        #     self.n_classes[k] = n_classes[k]
        #
        #     if n_classes[k] > sum_stride:
        #         sum_stride = n_classes[k]

        self.n_classes[:] = n_classes

        self.max_n_classes = np.max(self.n_classes)

        # self.sum_stride = sum_stride

        # n_elements = n_outputs * sum_stride

        # self.sum_total = <double*> calloc(n_elements, sizeof(double))
        # self.sum_left = <double*> calloc(n_elements, sizeof(double))
        # self.sum_right = <double*> calloc(n_elements, sizeof(double))
        shape = (self.n_outputs, self.max_n_classes)
        self.sum_total = np.empty(shape, dtype=NP_DOUBLE_t)
        self.sum_left = np.empty(shape, dtype=NP_DOUBLE_t)
        self.sum_right = np.empty(shape, dtype=NP_DOUBLE_t)

@njit
def gini_node_impurity(criterion):
#     cdef double node_impurity(self) nogil:
#         """Evaluate the impurity of the current node.
#
#         Evaluate the Gini criterion as impurity of the current node,
#         i.e. the impurity of samples[start:end]. The smaller the impurity the
#         better.
#         """
#         cdef SIZE_t* n_classes = self.n_classes
#         cdef double* sum_total = self.sum_total
#         cdef double gini = 0.0
#         cdef double sq_count
#         cdef double count_k
#         cdef SIZE_t k
#         cdef SIZE_t c
#
#         for k in range(self.n_outputs):
#             sq_count = 0.0
#
#             for c in range(n_classes[k]):
#                 count_k = sum_total[c]
#                 sq_count += count_k * count_k
#
#             gini += 1.0 - sq_count / (self.weighted_n_node_samples *
#                                       self.weighted_n_node_samples)
#
#             sum_total += self.sum_stride
#
#         return gini / self.n_outputs

    print(criterion)

    n_classes = criterion.n_classes
    sum_total = criterion.sum_total
    gini = 0.0
    # cdef double sq_count
    # cdef double count_k
    # cdef SIZE_t k
    # cdef SIZE_t c

    # for k in range(criterion.n_outputs):
    #     sq_count = 0.0
    #
    #     for c in range(n_classes[k]):
    #         count_k = sum_total[c]
    #         sq_count += count_k * count_k
    #
    #     gini += 1.0 - sq_count / (criterion.weighted_n_node_samples *
    #                               criterion.weighted_n_node_samples)
    #
    #     sum_total += criterion.sum_stride

    # TODO: For loop since a label might have more classes than others... du coup on
    #  ajouter plein de zeros mais ptet moins bon en terme de cache
    for k in range(criterion.n_outputs):
        sq_count = 0.0
        for c in range(n_classes[k]):
            count_k = sum_total[k, c]
            sq_count += count_k * count_k

        gini += 1.0 - sq_count / (criterion.weighted_n_node_samples *
                                  criterion.weighted_n_node_samples)

    return gini / criterion.n_outputs


@njit
def gini_children_impurity(criterion):
#     cdef void children_impurity(self, double* impurity_left,
#                                 double* impurity_right) nogil:
#         """Evaluate the impurity in children nodes.
#
#         i.e. the impurity of the left child (samples[start:pos]) and the
#         impurity the right child (samples[pos:end]) using the Gini index.
#
#         Parameters
#         ----------
#         impurity_left : double pointer
#             The memory address to save the impurity of the left node to
#         impurity_right : double pointer
#             The memory address to save the impurity of the right node to
#         """
#         cdef SIZE_t* n_classes = self.n_classes
#         cdef double* sum_left = self.sum_left
#         cdef double* sum_right = self.sum_right
#         cdef double gini_left = 0.0
#         cdef double gini_right = 0.0
#         cdef double sq_count_left
#         cdef double sq_count_right
#         cdef double count_k
#         cdef SIZE_t k
#         cdef SIZE_t c
#
#         for k in range(self.n_outputs):
#             sq_count_left = 0.0
#             sq_count_right = 0.0
#
#             for c in range(n_classes[k]):
#                 count_k = sum_left[c]
#                 sq_count_left += count_k * count_k
#
#                 count_k = sum_right[c]
#                 sq_count_right += count_k * count_k
#
#             gini_left += 1.0 - sq_count_left / (self.weighted_n_left *
#                                                 self.weighted_n_left)
#
#             gini_right += 1.0 - sq_count_right / (self.weighted_n_right *
#                                                   self.weighted_n_right)
#
#             sum_left += self.sum_stride
#             sum_right += self.sum_stride
#
#         impurity_left[0] = gini_left / self.n_outputs
#         impurity_right[0] = gini_right / self.n_outputs

    n_classes = criterion.n_classes
    sum_left = criterion.sum_left
    sum_right = criterion.sum_right
    gini_left = 0.0
    gini_right = 0.0
    # cdef double sq_count_left
    # cdef double sq_count_right
    # cdef double count_k
    # cdef SIZE_t k
    # cdef SIZE_t c

    # idx_sum_left = 0
    # idx_sum_right = 0
    #
    # for k in range(criterion.n_outputs):
    #     sq_count_left = 0.0
    #     sq_count_right = 0.0
    #
    #     for c in range(n_classes[k]):
    #         count_k = sum_left[idx_sum_left + c]
    #         sq_count_left += count_k * count_k
    #
    #         count_k = sum_right[idx_sum_right + c]
    #         sq_count_right += count_k * count_k
    #
    #     gini_left += 1.0 - sq_count_left / (criterion.weighted_n_left *
    #                                         criterion.weighted_n_left)
    #
    #     gini_right += 1.0 - sq_count_right / (criterion.weighted_n_right *
    #                                           criterion.weighted_n_right)
    #
    #     idx_sum_left += criterion.sum_stride
    #     idx_sum_right += criterion.sum_stride

    for k in range(criterion.n_outputs):
        sq_count_left = 0.0
        sq_count_right = 0.0

        for c in range(n_classes[k]):
            count_k = sum_left[k, c]
            sq_count_left += count_k * count_k

            count_k = sum_right[k, c]
            sq_count_right += count_k * count_k

        gini_left += 1.0 - sq_count_left / (criterion.weighted_n_left *
                                            criterion.weighted_n_left)

        gini_right += 1.0 - sq_count_right / (criterion.weighted_n_right *
                                              criterion.weighted_n_right)

        # idx_sum_left += criterion.sum_stride
        # idx_sum_right += criterion.sum_stride


    return gini_left / criterion.n_outputs, gini_right / criterion.n_outputs
