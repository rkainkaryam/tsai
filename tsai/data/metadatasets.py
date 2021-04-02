# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/002c_data.metadatasets.ipynb (unless otherwise specified).

__all__ = ['TSMetaDataset', 'TSMetaDatasets']

# Cell
from ..imports import *
from ..utils import *
from .validation import *
from .core import *

# Cell
class TSMetaDataset():
    " A dataset capable of indexing mutiple datasets at the same time!"
    def __init__(self, dataset_list, **kwargs):
        if not is_listy(dataset_list): dataset_list = [dataset_list]
        self.datasets = dataset_list
        self.split = kwargs['split'] if 'split' in kwargs else None
        self.mapping = self._mapping()
        if hasattr(dataset_list[0], 'loss_func'):
            self.loss_func =  dataset_list[0].loss_func
        else:
            self.loss_func = None

    def __len__(self):
        if self.split is not None:
            return len(self.split)
        else:
            return sum([len(ds) for ds in self.datasets])

    def __getitem__(self, idx):
        if self.split is not None: idx = self.split[idx]
        idx = listify(idx)
        idxs = self.mapping[idx]
        idxs = idxs[idxs[:, 0].argsort()]
        self.mapping_idxs = idxs
        ds = np.unique(idxs[:, 0])
        b = [self.datasets[d][idxs[idxs[:, 0] == d, 1]] for d in ds]
        output = tuple(map(torch.cat, zip(*b)))
        return output

    def _mapping(self):
        lengths = [len(ds) for ds in self.datasets]
        idx_pairs = np.zeros((np.sum(lengths), 2)).astype(np.int32)
        start = 0
        for i,length in enumerate(lengths):
            if i > 0:
                idx_pairs[start:start+length, 0] = i
            idx_pairs[start:start+length, 1] = np.arange(length)
            start += length
        return idx_pairs

    @property
    def vars(self):
        s = self.datasets[0][0][0] if not isinstance(self.datasets[0][0][0], tuple) else self.datasets[0][0][0][0]
        return s.shape[-2]
    @property
    def len(self):
        s = self.datasets[0][0][0] if not isinstance(self.datasets[0][0][0], tuple) else self.datasets[0][0][0][0]
        return s.shape[-1]


class TSMetaDatasets(FilteredBase):
    def __init__(self, metadataset, splits):
        store_attr()
        self.mapping = metadataset.mapping
    def subset(self, i):
        return type(self.metadataset)(self.metadataset.datasets, split=self.splits[i])
    @property
    def train(self):
        return self.subset(0)
    @property
    def valid(self):
        return self.subset(1)