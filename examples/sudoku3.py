# (c) Peter Cock
# --- http://www2.warwick.ac.uk/fac/sci/moac/currentstudents/peter_cock/python/sudoku/
#
# sudoku solver

TRIPLETS = [[0,1,2],[3,4,5],[6,7,8]]

ROW_ITER = [[(row,col) for col in range(0,9)] for row in range(0,9)]
COL_ITER = [[(row,col) for row in range(0,9)] for col in range(0,9)]
TxT_ITER = [[(row,col) for row in rows for col in cols] for rows in TRIPLETS for cols in TRIPLETS]

class soduko:
    def __init__(self, start_grid=None) :
        self.squares =[ [range(1,10)  for col in range(0,9)] for row in range(0,9)]
        
        if start_grid is not None:
            assert len(start_grid)==9, "Bad input!"
            for row in range(0,9) :
                self.set_row(row, start_grid[row])
                
        self._changed=False
    
    def copy(self) :
        soduko_copy = soduko(None)
        for row in range(0,9) :
            for col in range(0,9) :
                soduko_copy.squares[row][col] = self.squares[row][col][:] 
        soduko_copy._changed=False
        return soduko_copy
    
    def set_row(self,row, x_list) :
        assert len(x_list)==9, 'not 9'
        for col in range(0,9) :
            try :
                x = int(x_list[col])
            except :
                x = 0
            self.set_cell(row,col,x)

    def set_cell(self,row,col,x):
        if self.squares[row][col] == [x] :
            pass
        elif x not in range(1,9+1) :
            pass
        else:
            assert x in self.squares[row][col], "bugger2" 
            
            self.squares[row][col] = [x]
            self.update_neighbours(row,col,x)
            self._changed=True
            
    def cell_exclude(self, row,col,x) :
        assert x in range(1,9+1), 'inra'
        if x in self.squares[row][col] :
            self.squares[row][col].remove(x)
            assert len(self.squares[row][col]) > 0, "bugger"
            if len(self.squares[row][col]) == 1 :
                self._changed=True
                self.update_neighbours(row,col,self.squares[row][col][0])
        else :
            pass
        return

    def update_neighbours(self,set_row,set_col,x) :
        for row in range(0,9) :
            if row <> set_row :
                self.cell_exclude(row,set_col,x)
        for col in range(0,9) :
            if col <> set_col :
                self.cell_exclude(set_row,col,x)
        for triplet in TRIPLETS :
            if set_row in triplet : rows = triplet[:]
            if set_col in triplet : cols = triplet[:]
        rows.remove(set_row)
        cols.remove(set_col)
        for row in rows :
            for col in cols :
                assert row <> set_row or col <> set_col , 'meuh'
                self.cell_exclude(row,col,x)
            
    def get_cell_digit_str(self,row,col) :
        if len(self.squares[row][col])==1 :
            return str(self.squares[row][col][0])
        else :
            return "0"
            
    def __str__(self):
        answer = "   123   456   789\n"
        for row in range(0,9) :
            answer = answer + str(row+1)                         +   " [" + "".join([self.get_cell_digit_str(row,col).replace("0","?") for col in range(0,3)])                         + "] [" + "".join([self.get_cell_digit_str(row,col).replace("0","?") for col in range(3,6)])                         + "] [" + "".join([self.get_cell_digit_str(row,col).replace("0","?") for col in range(6,9)])                         + "]\n"
            if row+1 in [3,6] : 
              answer = answer + "   ---   ---   ---\n"
        return answer
                    
    def check(self) :
        self._changed=True
        while self._changed:
            self._changed=False
            self.check_for_single_occurances()
            self.check_for_last_in_row_col_3x3()
        return
        
    def check_for_single_occurances(self):
        for check_type in [ROW_ITER, COL_ITER, TxT_ITER]:
            for check_list in check_type :
                for x in range(1,9+1) : #1 to 9 inclusive
                    x_in_list = []
                    for (row,col) in check_list :
                        if x in self.squares[row][col] :
                            x_in_list.append((row,col))
                    if len(x_in_list)==1 :
                        (row,col) = x_in_list[0]
                        if len(self.squares[row][col]) > 1 :
                            self.set_cell(row,col,x)

    def check_for_last_in_row_col_3x3(self):
        for (type_name, check_type) in [("Row",ROW_ITER),("Col",COL_ITER),("3x3",TxT_ITER)]:
            for check_list in check_type :
                unknown_entries = []
                unassigned_values = range(1,9+1) #1-9 inclusive
                known_values = []
                for (row,col) in check_list :
                    if len(self.squares[row][col]) == 1 :
                        assert self.squares[row][col][0] not in known_values, "bugger3"

                        known_values.append(self.squares[row][col][0])

                        assert self.squares[row][col][0] in unassigned_values, "bugger4"

                        unassigned_values.remove(self.squares[row][col][0])
                    else :
                        unknown_entries.append((row,col))
                assert len(unknown_entries) + len(known_values) == 9, 'bugger5'
                assert len(unknown_entries) == len(unassigned_values), 'bugger6'
                if len(unknown_entries) == 1 :
                    x = unassigned_values[0]
                    (row,col) = unknown_entries[0]
                    self.set_cell(row,col,x)
        return
        
    def one_level_supposition(self):
        progress=True
        while progress :
            progress=False
            for row in range(0,9) :
                for col in range(0,9):
                    if len(self.squares[row][col]) > 1 :
                        bad_x = []
                        for x in self.squares[row][col] :
                            soduko_copy = self.copy()
                            try:
                                soduko_copy.set_cell(row,col,x)
                                soduko_copy.check()
                            except AssertionError, e :
                                bad_x.append(x)
                            del soduko_copy
                        if len(bad_x) == 0 :
                            pass
                        elif len(bad_x) < len(self.squares[row][col]) :
                            for x in bad_x :
                                self.cell_exclude(row,col,x)
                                self.check() 
                            progress=True
                        else :
                            assert False, "bugger7"


for x in range(50):
    t = soduko(["800000600",
                   "040500100",
                   "070090000",
                   "030020007",
                   "600008004",
                   "500000090",
                   "000030020",
                   "001006050",
                   "004000003"])

    t.check()
    t.one_level_supposition()
    t.check()
    print t

