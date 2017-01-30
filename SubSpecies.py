from wrapt import ObjectProxy as proxy
from PaddedMatrix import PaddedMatrix, matricies
from utils import accumu,addTo,equate

class SubSpecies:
    def __init__(self,M,number=1,numbers=None,col_pruning=False,row_pruning=True):
        row_absence = [(False not in [r.is_zero is True for r in row]) and not(row_pruning) for row in M.rows()]
        column_absence = [(False not in [r.is_zero is True for r in col]) and not(col_pruning) for col in M.cols()]
        self.absence = [row_absence[i] or column_absence[i] for i in range(M.nrows)]
        self.map = B = list(accumu([1 if not(a) else 0 for a in self.absence]))
        rows_present = sum([1 for a in self.absence if not(a)])
        if numbers is None:
            self.oldvalues = [proxy(number/rows_present) for i in range(M.nrows) if not self.absence[i]]
            self.newvalues = [proxy(number/rows_present) for i in range(M.nrows) if not self.absence[i]]
        else:
            assert M.nrows == len(numbers)
            for i in range(M.nrows):
                self.oldvalues = []
                self.newvalues = []
                if not self.absence[i]:
                    self.oldvalues.append(proxy(numbers[i]/rows_present))
                    self.newvalues.append(proxy(numbers[i]/rows_present))
                elif numbers[i] > 0:
                    print "warning: cannot assign values to pruned states"
        self._temp = [0]*M.nrows
        removed_states = 0
        for index,a in enumerate(self.absence):
            if a:
                removed_states += 1
                M = M.del_row_col(index-removed_states+1,index-removed_states+1)
        self.M = addTo(PaddedMatrix(M),matricies)
    def update(self,smoothing):
        mm = self.M.M.grid
        ov = self.oldvalues
        inverse_smoothing = 1-smoothing
        temp = self._temp
        for r in range(len(self.oldvalues)):
            s = 0
            for c in range(self.M.M.ncols):
                s += mm[r][c]*ov[c]*inverse_smoothing
            s += smoothing*ov[r]
            temp[r] = s
        equate(self.newvalues,temp)
    def turnOver(self):
        for i in range(len(self.oldvalues)):
            nv = self.newvalues[i]
            ov = self.oldvalues[i]
            t = nv.__wrapped__
            nv.__wrapped__ = ov.__wrapped__
            ov.__wrapped__ = t
    def __getitem__(self, key):
        if self.absence[key] is True:
            return 0
        else:
            return self.newvalues[self.map[key]]
