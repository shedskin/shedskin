#include "builtin.hpp"
#include "collections.hpp"
#include "itertools.hpp"
#include "time.hpp"
#include "life.hpp"

/**
Implementation of: http://en.wikipedia.org/wiki/Conway's_Game_of_Life 
Tested on Python 2.6.4 and Python 3.1.1 
*/

namespace __life__ {

str *const_0, *const_1, *const_2, *const_3, *const_4, *const_5, *const_6;

using __collections__::defaultdict;
using __itertools__::product;

file *__file;
__ss_int __30, __31, __32, __33, __void, columns, count, m, n, rows;
str *__name__;
__ss_float t0;


static inline list<tuple<__ss_int> *> *list_comp_0(__ss_int columns, __ss_int rows);
static inline __ss_int __lambda0__();
static inline __ss_int __lambda1__();

static inline list<tuple<__ss_int> *> *list_comp_0(__ss_int columns, __ss_int rows) {
    __ss_int __10, __11, __12, __13, column, row;

    list<tuple<__ss_int> *> *__ss_result = new list<tuple<__ss_int> *>();

    __SS_LIST_RESERVE(__ss_result, 8);
    FAST_FOR(row,0,rows,1,10,11)
        FAST_FOR(column,0,columns,1,12,13)
            __ss_result->append((__ss_tuple_int(2,row,column)));
        END_FOR

    END_FOR

    return __ss_result;
}

static inline __ss_int __lambda0__() {
    return __int();
}

static inline __ss_int __lambda1__() {
    return __int();
}

__ss_int add(__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *board, tuple<__ss_int> *pos) {
    /**
    Adds eight cells near current cell 
    */
    __ss_int column, row;
    tuple<__ss_int> *__0;

    __0 = pos;
    __SS_UNPACK_CHECK(__0, 2);
    row = __0->__getfirst__();
    column = __0->__getsecond__();
    return (((((((board->__getitem__((__ss_tuple_int(2,(row-__ss_int(1LL)),(column-__ss_int(1LL)))))+board->__getitem__((__ss_tuple_int(2,(row-__ss_int(1LL)),column))))+board->__getitem__((__ss_tuple_int(2,(row-__ss_int(1LL)),(column+__ss_int(1LL))))))+board->__getitem__((__ss_tuple_int(2,row,(column-__ss_int(1LL))))))+board->__getitem__((__ss_tuple_int(2,row,(column+__ss_int(1LL))))))+board->__getitem__((__ss_tuple_int(2,(row+__ss_int(1LL)),(column-__ss_int(1LL))))))+board->__getitem__((__ss_tuple_int(2,(row+__ss_int(1LL)),column))))+board->__getitem__((__ss_tuple_int(2,(row+__ss_int(1LL)),(column+__ss_int(1LL))))));
}

__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *snext(__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *board) {
    /**
    Calculates the next stage 
    */
    __collections__::defaultdict<tuple<__ss_int> *, __ss_int> *__ss_new;
    tuple<__ss_int> *pos;
    __ss_int __3, __5, __ss_near, item;
    list<tuple<__ss_int> *> *__1;
    __iter<tuple<__ss_int> *> *__2;
    list<tuple<__ss_int> *>::for_in_loop __4;
    pyobj *__6, *__7;
    __ss_bool __8, __9;

    __ss_new = (new __collections__::defaultdict<tuple<__ss_int> *, __ss_int>(__lambda0__, board));

    FOR_IN(pos,(new list<tuple<__ss_int> *>(board)),1,3,4)
        __ss_near = add(board, pos);
        item = board->__getitem__(pos);
        if (((!__eq(__5=__ss_near,__ss_int(2LL)) && !__eq(__5,__ss_int(3LL))) and item)) {
            __ss_new->__setitem__(pos, __ss_int(0LL));
        }
        else if (((__ss_near==__ss_int(3LL)) and __NOT(item))) {
            __ss_new->__setitem__(pos, __ss_int(1LL));
        }
    END_FOR

    return __ss_new;
}

__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *process(__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *board) {
    /**
    Finds if this board repeats itself 
    */
    list<__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *> *history;

    history = (new list<__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *>(1,(new __collections__::defaultdict<tuple<__ss_int> *, __ss_int>(NULL, board))));

    while (__ss_int(1LL)) {
        board = snext(board);
        if ((history)->__contains__(board)) {
            if (__eq(board, history->__getfast__(__ss_int(0LL)))) {
                return board;
            }
            return NULL;
        }
        history->append((new __collections__::defaultdict<tuple<__ss_int> *, __ss_int>(NULL, board)));
    }
    return 0;
}

class __gen_generator : public __iter<__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *> {
public:
    list<tuple<__ss_int> *> *__22, *ppos;
    __iter<tuple<__ss_int> *> *__14, *__15, *possibilities;
    tuple<__ss_int> *__23, *__ss_case, *pos;
    __collections__::defaultdict<tuple<__ss_int> *, __ss_int> *board;
    __ss_int __16, __21, __24, columns, rows, value;
    __iter<tuple<__ss_int> *>::for_in_loop __17;
    tuple2<tuple<__ss_int> *, __ss_int> *__18;
    __iter<tuple2<tuple<__ss_int> *, __ss_int> *> *__19, *__20;
    __iter<tuple2<tuple<__ss_int> *, __ss_int> *>::for_in_loop __25;

    int __last_yield;

    __gen_generator(__ss_int rows,__ss_int columns) {
        this->rows = rows;
        this->columns = columns;
        __last_yield = -1;
    }

    __collections__::defaultdict<tuple<__ss_int> *, __ss_int> * __get_next() {
        return __get_next_awesome();
    }
    __collections__::defaultdict<tuple<__ss_int> *, __ss_int> * __get_next_awesome() {
        switch(__last_yield) {
            case 0: goto __after_yield_0;
            default: break;
        }
        ppos = list_comp_0(columns, rows);
        possibilities = product(1, (rows*columns), (__ss_tuple_int(2,__ss_int(0LL),__ss_int(1LL))));

        FOR_IN(__ss_case,possibilities,14,16,17)
            board = (new __collections__::defaultdict<tuple<__ss_int> *, __ss_int>(__lambda1__));

            FOR_IN_ZIP(pos,value,ppos,__ss_case,22,23,21,24)
                board->__setitem__(pos, value);
            END_FOR

            __last_yield = 0;
            __result = board;
            return __result;
            __after_yield_0:;
        END_FOR

        __stop_iteration = true;
        return __zero<__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *>();
    }

};

__iter<__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *> *generator(__ss_int rows, __ss_int columns) {
    /**
    Generates a board 
    */
    return new __gen_generator(rows,columns);

}

void *bruteforce(__ss_int rows, __ss_int columns) {
    __collections__::defaultdict<tuple<__ss_int> *, __ss_int> *board;
    __iter<__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *> *__26, *__27;
    __ss_int __28;
    __iter<__collections__::defaultdict<tuple<__ss_int> *, __ss_int> *>::for_in_loop __29;

    count = __ss_int(0LL);

    FOR_IN(board,map(1, False, process, generator(rows, columns)),26,28,29)
        if ((board!=NULL)) {
            count = (__life__::count+__ss_int(1LL));
        }
    END_FOR

    return NULL;
}

void __init() {
    __name__ = new str("__main__");

    const_0 = new str(" Implementation of: http://en.wikipedia.org/wiki/Conway's_Game_of_Life \012        Tested on Python 2.6.4 and Python 3.1.1 ");
    const_1 = new str(" Adds eight cells near current cell ");
    const_2 = new str(" Calculates the next stage ");
    const_3 = new str(" Finds if this board repeats itself ");
    const_4 = new str(" Generates a board ");
    const_5 = new str("__main__");
    const_6 = new str("TIME %.2f");

    if (__eq(__life__::__name__, const_5)) {

        FAST_FOR(m,0,__ss_int(10LL),1,30,31)
            if ((__life__::m==__ss_int(5LL))) {
                t0 = __time__::time();
            }

            FAST_FOR(n,0,__ss_int(20LL),1,32,33)
                rows = __ss_int(4LL);
                columns = __ss_int(3LL);
                bruteforce(__life__::rows, __life__::columns);
                print(__life__::count);
            END_FOR

        END_FOR

        print(__mod6(const_6, 1, (__time__::time()-__life__::t0)));
    }
}

} // module namespace

int main(int, char **) {
    __shedskin__::__init();
    __collections__::__init();
    __itertools__::__init();
    __time__::__init();
    __shedskin__::__start(__life__::__init);
}
