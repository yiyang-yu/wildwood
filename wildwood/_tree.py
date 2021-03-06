# Authors: Stephane Gaiffas <stephane.gaiffas@gmail.com>
# License: BSD 3 clause

"""
This contains all the data structures for a tree together with prediction functions
of a tree.
"""

from math import exp
import numpy as np

from numba import (
    jit,
    boolean,
    uint8,
    int32,
    intp,
    uintp,
    float32,
    void,
    optional,
)
from numba.experimental import jitclass

from ._utils import get_type, resize
from ._node import node_type, node_dtype


IS_FIRST = 1
IS_NOT_FIRST = 0
IS_LEFT = 1
IS_NOT_LEFT = 0
TREE_LEAF = intp(-1)
TREE_UNDEFINED = intp(-2)


tree_type = [
    # Number of features
    ("n_features", uintp),
    # random_state used for seeding numpy from numba. Note that numba uses its own
    # random_state, so that we need to seed numpy.random.seed() within jitted code
    ("random_state", int32),
    # Maximum depth allowed in the tree
    ("max_depth", uintp),
    # Number of nodes in the tree
    ("node_count", uintp),
    # Maximum number of nodes storable in the tree
    ("capacity", uintp),
    # A numpy array containing the nodes data
    ("nodes", node_type[::1]),
]

tree_classifier_type = [
    *tree_type,
    # Number of classes
    ("n_classes", uintp),
    # The predictions of each node in the tree with shape (n_nodes, n_classes)
    ("y_pred", float32[:, ::1]),
]


tree_regressor_type = [
    *tree_type,
    # The predictions of each node in the tree with shape (n_nodes,)
    ("y_pred", float32[::1]),
]


@jitclass(tree_classifier_type)
class _TreeClassifier(object):
    """A tree for classification containing an array of nodes and an array for its
    predictions

    Parameters
    ----------
    n_features : int
        Number of input features

    n_classes : int
        Number of label classes

    Attributes
    ----------
    n_features : int
        Number of input features

    n_classes :
        Number of label classes

    max_depth :
        Maximum depth allowed in the tree (not used for now)

    node_count :
        Number of nodes in the tree

    capacity :
        Maximum number of nodes storable in the tree

    nodes : ndarray
        A numpy array containing the nodes data

    y_pred : ndarray
        The predictions of each node in the tree with shape (n_nodes, n_classes)
    """

    def __init__(self, n_features, n_classes, random_state):
        self.n_features = n_features
        self.n_classes = n_classes
        self.max_depth = 0
        self.node_count = 0
        self.capacity = 0
        self.random_state = random_state
        # Seed numba's random generator...
        np.random.seed(random_state)
        # Both node and prediction arrays have zero on the first axis and are resized
        # later when we know the initial capacity required for the tree
        self.nodes = np.empty(0, dtype=node_dtype)
        self.y_pred = np.empty((0, self.n_classes), dtype=np.float32)


@jitclass(tree_regressor_type)
class _TreeRegressor(object):
    """A tree for regression containing an array of nodes and an array for its
    predictions

    Parameters
    ----------
    n_features : int
        Number of input features

    Attributes
    ----------
    n_features : int
        Number of input features

    max_depth :
        Maximum depth allowed in the tree (not used for now)

    node_count :
        Number of nodes in the tree

    capacity :
        Maximum number of nodes storable in the tree

    nodes : ndarray
        A numpy array containing the nodes data

    y_pred : ndarray
        The predictions of each node in the tree with shape (n_nodes,)
    """

    def __init__(self, n_features, random_state):
        self.n_features = n_features
        self.max_depth = 0
        self.node_count = 0
        self.capacity = 0
        self.random_state = random_state
        # Seed numba's random generator...
        np.random.seed(random_state)
        # Both node and prediction arrays have zero on the first axis and are resized
        # later when we know the initial capacity required for the tree
        self.nodes = np.empty(0, dtype=node_dtype)
        self.y_pred = np.empty(0, dtype=np.float32)


# Numba types for Trees
TreeClassifierType = get_type(_TreeClassifier)
TreeRegressorType = get_type(_TreeRegressor)


def get_nodes(tree):
    import pandas as pd

    nodes = tree.nodes

    columns = [
        "node_id",
        "parent",
        "left_child",
        "right_child",
        "is_leaf",
        "depth",
        "feature",
        "threshold",
        "bin_threshold",
        "impurity",
        "n_samples_train",
        "n_samples_valid",
        "w_samples_train",
        "w_samples_valid",
        "start_train",
        "end_train",
        "start_valid",
        "end_valid",
        "is_left",
        "loss_valid",
        "log_weight_tree",
    ]

    return pd.DataFrame.from_records(
        (
            tuple(node[col] for col in columns)
            for i, node in enumerate(nodes)
            if i < tree.node_count
        ),
        columns=columns,
    )


def get_nodes_regressor(tree):
    nodes = get_nodes(tree)
    y_pred = tree.y_pred[: tree.node_count]
    nodes["y_pred"] = y_pred
    return nodes


def get_nodes_classifier(tree):
    nodes = get_nodes(tree)
    return nodes


@jit(
    [void(TreeClassifierType, uintp), void(TreeRegressorType, uintp)],
    nopython=True,
    nogil=True,
)
def resize_tree_(tree, capacity):
    """Resizes and updates the tree to have the required capacity. This functions
    resizes the tree no matter what (no test is performed here).

    Parameters
    ----------
    tree : TreeClassifier or TreeRegressor
        The tree to be resized

    capacity : int
        The new desired capacity (maximum number of nodes it can contain) of the tree
    """
    tree.nodes = resize(tree.nodes, capacity)
    tree.y_pred = resize(tree.y_pred, capacity, zeros=True)
    tree.capacity = capacity


@jit(
    [
        void(TreeClassifierType, optional(uintp)),
        void(TreeRegressorType, optional(uintp)),
    ],
    nopython=True,
    nogil=True,
)
def resize_tree(tree, capacity=None):
    """Resizes and updates the tree to have the required capacity if necessary. By
    default, it doubles the current capacity of the tree if no capacity is specified
    and set it to 3 if the tree is empty.

    Parameters
    ----------
    tree : TreeClassifier or TreeRegressor
        The tree to be resized

    capacity : int or None
        The new desired capacity (maximum number of nodes it can contain) of the tree.
        If None, then it doubles the capacity of the tree.
    """
    if capacity is None:
        if tree.capacity == 0:
            # If no capacity is specified and there is no node in the tree yet,
            # we set it to 3
            resize_tree_(tree, 3)
        else:
            # If no capacity is specified we double the current capacity
            resize_tree_(tree, 2 * tree.capacity)
    else:
        if capacity <= tree.capacity and tree.nodes.size > 0:
            # If the capacity of the tree is already large enough, we no nothing
            return
        else:
            # Otherwise, we resize using the specified capacity
            resize_tree_(tree, capacity)


@jit(
    [
        uintp(
            TreeClassifierType,
            intp,
            uintp,
            boolean,
            boolean,
            uintp,
            float32,
            uint8,
            float32,
            uintp,
            uintp,
            float32,
            float32,
            uintp,
            uintp,
            uintp,
            uintp,
            float32,
        ),
        uintp(
            TreeRegressorType,
            intp,
            uintp,
            boolean,
            boolean,
            uintp,
            float32,
            uint8,
            float32,
            uintp,
            uintp,
            float32,
            float32,
            uintp,
            uintp,
            uintp,
            uintp,
            float32,
        ),
    ],
    nopython=True,
    nogil=True,
    locals={"node_idx": uintp, "nodes": node_type[::1], "node": node_type},
)
def add_node_tree(
    tree,
    parent,
    depth,
    is_left,
    is_leaf,
    feature,
    threshold,
    bin_threshold,
    impurity,
    n_samples_train,
    n_samples_valid,
    w_samples_train,
    w_samples_valid,
    start_train,
    end_train,
    start_valid,
    end_valid,
    loss_valid,
):
    """Adds a node in the tree.

    Parameters
    ----------
    tree : TreeClassifier or TreeRegressor
        The tree in which we want to add a node

    parent : int
        Index of the parent node

    depth : int
       Depth of the node in the tree

    is_left : bool
        True if the node is a left child, False otherwise

    is_leaf : bool
        True if the node is a leaf node, False otherwise

    feature : int
        Feature used to split the node

    threshold : float
        Continuous threshold used to split the node (not used for now)

    bin_threshold : int
        Index of the bin threshold used to split the node

    impurity : float
        Impurity of the node. Used to avoid to split a "pure" node (with impurity=0).

    n_samples_train : int
        Number of training samples in the node

    n_samples_valid : int
        Number of validation (out-of-the-bag) samples in the node

    w_samples_train : float
        Weighted number of training samples in the node

    w_samples_valid : float
        Weighted number of validation (out-of-the-bag) samples in the node

    start_train : int
        Index of the first training sample in the node. We have that
        partition_train[start_train:end_train] contains the indexes of the node's
        training samples

    end_train : int
        End-index of the slice containing the node's training samples indexes

    start_valid : int
        Index of the first validation (out-of-the-bag) sample in the node. We have
        that partition_valid[start_valid:end_valid] contains the indexes of the
        node's validation samples

    end_valid : int
        End-index of the slice containing the node's validation samples indexes

    loss_valid : float
        Validation loss of the node, computed on validation (out-of-the-bag) samples
    """
    # New node index is given by the current number of nodes in the tree
    node_idx = tree.node_count
    if node_idx >= tree.capacity:
        resize_tree(tree, None)

    nodes = tree.nodes
    node = nodes[node_idx]
    node["node_id"] = node_idx
    node["parent"] = parent
    node["depth"] = depth
    node["is_leaf"] = is_leaf
    node["impurity"] = impurity
    node["n_samples_train"] = n_samples_train
    node["n_samples_valid"] = n_samples_valid
    node["w_samples_train"] = w_samples_train
    node["w_samples_valid"] = w_samples_valid
    node["start_train"] = start_train
    node["end_train"] = end_train
    node["start_valid"] = start_valid
    node["end_valid"] = end_valid
    node["loss_valid"] = loss_valid
    node["log_weight_tree"] = np.nan

    if parent != TREE_UNDEFINED:
        if is_left:
            nodes[parent]["left_child"] = node_idx
        else:
            nodes[parent]["right_child"] = node_idx

    if is_leaf:
        node["left_child"] = TREE_LEAF
        node["right_child"] = TREE_LEAF
        node["feature"] = TREE_UNDEFINED
        node["threshold"] = TREE_UNDEFINED
        node["bin_threshold"] = TREE_UNDEFINED
    else:
        node["feature"] = feature
        node["threshold"] = threshold
        node["bin_threshold"] = bin_threshold

    tree.node_count += 1
    return node_idx


@jit(
    uintp(node_type[::1], uint8[:]),
    nopython=True,
    nogil=True,
    locals={"idx_leaf": uintp, "node": node_type},
)
def find_leaf(nodes, xi):
    """Find the leaf index containing the given features vector.

    Parameters
    ----------
    nodes : ndarray
        Array of nodes with shape (n_nodes,) with node_dtype dtype

    xi : ndarray
        Input features vector of shape (n_features,) with uint8 dtype

    Returns
    -------
    output : uintp
        Index of the leaf node containing the input features vector
    """
    idx_leaf = 0
    node = nodes[idx_leaf]
    while not node["is_leaf"]:
        if xi[node["feature"]] <= node["bin_threshold"]:
            idx_leaf = node["left_child"]
        else:
            idx_leaf = node["right_child"]
        node = nodes[idx_leaf]

    return idx_leaf


@jit(
    [
        uintp[::1](TreeClassifierType, uint8[:, :]),
        uintp[::1](TreeRegressorType, uint8[:, :]),
    ],
    nopython=True,
    nogil=True,
    locals={"n_samples": uintp, "out": uintp[::1], "i": uintp, "idx_leaf": uintp},
)
def tree_apply(tree, X):
    """Finds the indexes of the leaves containing each input vector of features (rows
    of the input matrix of features)

    Parameters
    ----------
    tree : TreeClassifier or TreeRegressor
        The tree

    X : ndarray
        Input matrix of features with shape (n_samples, n_features) and uint8 dtype

    Returns
    -------
    output : ndarray
        An array of shape (n_samples,) and uintp dtype containing the indexes of the
        leaves containing each input vector of features
    """
    n_samples = X.shape[0]
    out = np.zeros((n_samples,), dtype=uintp)
    for i in range(n_samples):
        idx_leaf = find_leaf(tree.nodes, X[i])
        out[i] = idx_leaf

    return out


@jit(
    float32[:, ::1](TreeClassifierType, uint8[:, :], boolean, float32),
    nopython=True,
    nogil=True,
    locals={
        "n_samples": uintp,
        "n_classes": uintp,
        "nodes": node_type[::1],
        "y_pred": float32[:, ::1],
        "out": float32[:, ::1],
        "i": uintp,
        "idx_current": uintp,
        "pred_i": float32[::1],
        "node": node_type,
        "node_pred": float32[::1],
        "loss": float32,
        "log_weight_tree": float32,
        "alpha": float32,
    },
)
def tree_classifier_predict_proba(tree, X, aggregation, step):
    """Predicts class probabilities for the input matrix of features.

    Parameters
    ----------
    tree : TreeClassifier
        The tree

    X : ndarray
        Input matrix of features with shape (n_samples, n_features) and uint8 dtype

    aggregation : bool
        If True we predict the class probabilities using the aggregation algorithm.
        Otherwise, we simply use the prediction given by the leaf node containing the
        input features.

    step : float
        Step-size used for the computation of the aggregation weights. Used only if
        aggregation=True

    Returns
    -------
    output : ndarray
        An array of shape (n_samples, n_classes) and float32 dtype containing the
        predicted class probabilities
    """
    n_samples = X.shape[0]
    n_classes = tree.n_classes
    nodes = tree.nodes
    y_pred = tree.y_pred
    out = np.zeros((n_samples, n_classes), dtype=float32)
    for i in range(n_samples):
        # FInd the leaf containing X[i]
        idx_current = find_leaf(nodes, X[i])
        # Get a view to save the prediction for X[i]
        pred_i = out[i]
        # First, we get the prediction of the leaf
        pred_i[:] = y_pred[idx_current]
        if aggregation:
            while idx_current != 0:
                # Get the parent node
                idx_current = nodes[idx_current]["parent"]
                node = nodes[idx_current]
                # Prediction of this node
                node_pred = y_pred[idx_current]
                # logarithm of the aggregation weight
                loss = -step * node["loss_valid"]
                log_weight_tree = node["log_weight_tree"]
                alpha = 0.5 * exp(loss - log_weight_tree)
                # Context tree weighting dark magic
                pred_i[:] = alpha * node_pred + (1 - alpha) * pred_i

    return out


@jit(
    float32[:](TreeRegressorType, uint8[:, :], boolean, float32),
    nopython=True,
    nogil=True,
    locals={
        "n_samples": uintp,
        "nodes": node_type[::1],
        "y_pred": float32[::1],
        "out": float32[::1],
        "i": uintp,
        "idx_current": uintp,
        "pred_i": float32,
        "node": node_type,
        "node_pred": float32,
        "loss": float32,
        "log_weight_tree": float32,
        "alpha": float32,
    },
)
def tree_regressor_predict(tree, X, aggregation, step):
    """Predicts the labels for the input matrix of features.

    Parameters
    ----------
    tree : TreeRegressor
        The tree

    X : ndarray
        Input matrix of features with shape (n_samples, n_features) and uint8 dtype

    aggregation : bool
        If True we predict the labels using the aggregation algorithm.
        Otherwise, we simply use the prediction given by the leaf node containing the
        input features.

    step : float
        Step-size used for the computation of the aggregation weights. Used only if
        aggregation=True

    Returns
    -------
    output : ndarray
        An array of shape (n_samples,) and float32 dtype containing the
        predicted labels
    """
    n_samples = X.shape[0]
    nodes = tree.nodes
    y_pred = tree.y_pred
    out = np.zeros(n_samples, dtype=float32)

    for i in range(n_samples):
        idx_current = find_leaf(nodes, X[i])
        # First, we get the prediction of the leaf
        pred_i = y_pred[idx_current]
        if aggregation:
            while idx_current != 0:
                # Get the parent node
                idx_current = nodes[idx_current]["parent"]
                node = nodes[idx_current]
                # Prediction of this node
                node_pred = y_pred[idx_current]
                # logarithm of the aggregation weight
                loss = -step * node["loss_valid"]
                log_weight_tree = node["log_weight_tree"]
                # Compute the aggregation weight for this subtree
                alpha = 0.5 * exp(loss - log_weight_tree)
                # Context tree weighting dark magic
                pred_i = alpha * node_pred + (1 - alpha) * pred_i

        out[i] = pred_i

    return out


# TODO: code also a tree_classifier_weighted_depth or change the apply function with
#  an aggregation option


@jit(
    float32[:](TreeRegressorType, uint8[:, :], float32),
    nopython=True,
    nogil=True,
    locals={
        "n_samples": uintp,
        "nodes": node_type[::1],
        "out": float32[::1],
        "i": uintp,
        "idx_current": uintp,
        "node": node_type,
        "weighted_depth": float32,
        "node_pred": float32,
        "loss": float32,
        "log_weight_tree": float32,
        "alpha": float32,
    },
)
def tree_regressor_weighted_depth(tree, X, step):
    """Compute the weighted depth used by the aggregation algorithm for the
    input matrix of features.

    Parameters
    ----------
    tree : TreeRegressor
        The tree

    X : ndarray
        Input matrix of features with shape (n_samples, n_features) and uint8 dtype

    step : float
        Step-size used for the computation of the aggregation weights. Used only if
        aggregation=True

    Returns
    -------
    output : ndarray
        An array of shape (n_samples,) and float32 dtype containing the
        predicted labels
    """
    n_samples = X.shape[0]
    nodes = tree.nodes
    out = np.zeros(n_samples, dtype=float32)
    for i in range(n_samples):
        idx_current = find_leaf(nodes, X[i])
        node = nodes[idx_current]
        weighted_depth = float32(node["depth"])
        while idx_current != 0:
            idx_current = nodes[idx_current]["parent"]
            node = nodes[idx_current]
            depth_new = node["depth"]
            loss = -step * node["loss_valid"]
            log_weight_tree = node["log_weight_tree"]
            alpha = 0.5 * exp(loss - log_weight_tree)
            weighted_depth = alpha * depth_new + (1 - alpha) * weighted_depth
        out[i] = weighted_depth

    return out
