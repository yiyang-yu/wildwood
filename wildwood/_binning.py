"""
This module just imports for now a class from scikit-learn for features
binning. Later we'll implement another version of it in order to:
- Missing values do not end up at bin number 255, which can be sub-optimal
for wildwood
- Handling categorical features with more than 256 modalities
- Getting the list of ordered and non-ordered features, to fine-tune the pre-sorting
strategy used for splits computations in wildwood
"""

from sklearn.ensemble._hist_gradient_boosting.binning import _BinMapper as Binner
