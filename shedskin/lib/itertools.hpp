#ifndef ITERTOOLS_HPP
#define ITERTOOLS_HPP

#include "builtin.hpp"
#include <cassert>


using namespace __shedskin__;

namespace __itertools__ {

/* Local helpers */

template<class T> static bool _identity(T value) {
    return value;
}

/* Infinite Iterators */

// count

template<class T> class countiter : public __iter<T> {
public:
    T counter;
    T step;

    countiter();
    countiter(T start, T step);

    T next();
};

template<class T> inline countiter<T>::countiter() {}
template<class T> inline countiter<T>::countiter(T start, T step) {
    this->counter = start - step;
    this->step = step;
}

template<class T> inline T countiter<T>::next() {
    return this->counter += this->step;
}

template<class T> inline countiter<T> *count(T start, T step) {
    return new countiter<T>(start, step);
}
inline countiter<int> *count(int start = 0) {
    return new countiter<int>(start, 1);
}
inline countiter<double> *count(double start, double step = 1.) {
    return new countiter<double>(start, step);
}

// cycle

template<class T> class cycleiter : public __iter<T> {
public:
    bool exhausted;
    int position;
    __iter<T> *iter;
    __GC_VECTOR(T) cache;

    cycleiter();
    cycleiter(pyiter<T> *iterable);

    T next();
};

template<class T> inline cycleiter<T>::cycleiter() {}
template<class T> inline cycleiter<T>::cycleiter(pyiter<T> *iterable) {
    this->exhausted = false;
    this->position = 0;
    this->iter = iterable->__iter__();
}

template<class T> T cycleiter<T>::next() {
    if (!this->exhausted) {
        try  {
            this->cache.push_back(this->iter->next());
            return this->cache.back();
        } catch (StopIteration *) {
            if (this->cache.empty())
                throw new StopIteration();
            this->exhausted = true;
        }
    }
    assert(this->cache.size());
    const T& value = this->cache[position];
    this->position = (this->position + 1) % this->cache.size();
    return value;
}

template<class T> inline cycleiter<T> *cycle(pyiter<T> *iterable) {
    return new cycleiter<T>(iterable);
}

// repeat

template<class T> class repeatiter : public __iter<T> {
public:
    T object;
    int times;

    repeatiter();
    repeatiter(T object, int times);

    T next();
};

template<class T> inline repeatiter<T>::repeatiter() {}
template<class T> inline repeatiter<T>::repeatiter(T object, int times) {
    this->object = object;
    this->times = times ? times : -1;
}

template<class T> T repeatiter<T>::next() {
  if (!times)
    throw new StopIteration();

  if (times > 0)
    --times;

  return object;
}

template<class T> inline repeatiter<T> *repeat(T object, int times = 0) {
    return new repeatiter<T>(object, times);
}

/* Iterators terminating on the shortest input sequence */

// chain

template<class T> class chainiter : public __iter<T> {
public:
    unsigned int iterable;
    __GC_VECTOR(__iter<T> *) iters;

    chainiter();
    chainiter(pyiter<T> *iterable);

    void push_iter(pyiter<T> *iterable);

    T next();
};

template<class T> inline chainiter<T>::chainiter() {}
template<class T> inline chainiter<T>::chainiter(pyiter<T> *iterable) {
    this->iterable = 0;
    this->push_iter(iterable);
}
template<class T> void chainiter<T>::push_iter(pyiter<T> *iterable) {
    this->iters.push_back(iterable->__iter__());
}

template<class T> T chainiter<T>::next() {
    for (; ; ) {
        try  {
            return this->iters[iterable]->next();
        } catch (StopIteration *) {
            if (this->iterable == this->iters.size() - 1)
                throw new StopIteration();
            ++this->iterable;
        }
    }
}

template<class T> inline chainiter<T> *chain(int iterable_count, pyiter<T> *iterable, ...) {
    chainiter<T> *iter = new chainiter<T>(iterable);

    va_list ap;
    va_start(ap, iterable);

    while (--iterable_count) {
        iter->push_iter(va_arg(ap, pyiter<T> *));
    }

    va_end(ap);

    return iter;
}

// compress

template<class T, class B> class compressiter : public __iter<T> {
public:
    __iter<T> *data_iter;
    __iter<B> *selectors_iter;

    compressiter();
    compressiter(pyiter<T> *data, pyiter<B> *selectors);

    T next();
};

template<class T, class B> inline compressiter<T, B>::compressiter() {}
template<class T, class B> inline compressiter<T, B>::compressiter(pyiter<T> *data, pyiter<B> *selectors) {
    this->data_iter = data->__iter__();
    this->selectors_iter = selectors->__iter__();
}

template<class T, class B> T compressiter<T, B>::next() {
    while (!this->selectors_iter->next()) {
        this->data_iter->next();
    }
    return this->data_iter->next();
}

template<class T, class B> inline compressiter<T, B> *compress(pyiter<T> *data, pyiter<B> *selectors) {
    return new compressiter<T, B>(data, selectors);
}

// dropwhile

template<class T, class B> class dropwhileiter : public __iter<T> {
public:
    bool drop;
    B (*predicate)(T);
    __iter<T> *iter;

    dropwhileiter();
    dropwhileiter(B (*predicate)(T), pyiter<T> *iterable);

    T next();
};

template<class T, class B> inline dropwhileiter<T, B>::dropwhileiter() {}
template<class T, class B> inline dropwhileiter<T, B>::dropwhileiter(B (*predicate)(T), pyiter<T> *iterable) {
    this->drop = true;
    this->predicate = predicate;
    this->iter = iterable->__iter__();
}

template<class T, class B> T dropwhileiter<T, B>::next() {
    if (drop) {
        for (; ; ) {
            const T& value = this->iter->next();
            if (!this->predicate(value)) {
                this->drop = false;
                return value;
            }
        }
    }
    return this->iter->next();
}

template<class T, class B> inline dropwhileiter<T, B> *dropwhile(B (*predicate)(T), pyiter<T> *iterable) {
    return new dropwhileiter<T, B>(predicate, iterable);
}

// groupby

template<class T, class K> class groupiter;

template<class T, class K> class groupbyiter : public __iter<tuple2<K, __iter<T> *> *> {
public:
    bool first;
    bool skip;
    T current_value;
    K current_key;
    K (*key)(T);
    __iter<T> *iter;

    groupbyiter();
    groupbyiter(pyiter<T> *iterable, K (*key)(T));

    tuple2<K, __iter<T> *> *next();

    friend class groupiter<T, K>;
};

template<class T, class K> class groupiter : public __iter<T> {
public:
    bool first;
    groupbyiter<T, K>* iter;

    groupiter();
    groupiter(groupbyiter<T, K>* iter);

    T next();
};

template<class T, class K> inline groupiter<T, K>::groupiter() {}
template<class T, class K> inline groupiter<T, K>::groupiter(groupbyiter<T, K>* iter) {
    this->first = true;
    this->iter = iter;
}

template<class T, class K> T groupiter<T, K>::next() {
    if (this->first) {
        this->first = false;
        return this->iter->current_value;
    }

    this->iter->current_value = this->iter->iter->next();;
    const K& new_key = this->iter->key(this->iter->current_value);

    if (new_key != this->iter->current_key) {
        this->iter->current_key = new_key;
        this->iter->skip = false;
        throw new StopIteration();
    }

    return this->iter->current_value;
}

template<class T, class K> inline groupbyiter<T, K>::groupbyiter() {}
template<class T, class K> inline groupbyiter<T, K>::groupbyiter(pyiter<T> *iterable, K (*key)(T)) {
    this->first = true;
    this->skip = false;
    this->key = key;
    this->iter = iterable->__iter__();
}

template<class T, class K> tuple2<K, __iter<T> *> *groupbyiter<T, K>::next() {
    if (!this->skip) {
        if (this->first) {
            this->current_value = this->iter->next();;
            this->current_key = this->key(this->current_value);
            this->first = false;
        }

        this->skip = true;
        return new tuple2<K, __iter<T> *>(2, this->current_key, new groupiter<T, K>(this));
    }

    for (; ; ) {
        this->current_value = this->iter->next();
        const K& new_key = this->key(this->current_value);
        if (new_key != this->current_key) {
            this->current_key = new_key;
            return new tuple2<K, __iter<T> *>(2, this->current_key, new groupiter<T, K>(this));
        }
    }
}

template<class T, class K> inline groupbyiter<T, K> *groupby(pyiter<T> *iterable, K (*key)(T)) {
    return new groupbyiter<T, K>(iterable, key);
}

// ifilter

template<class T, class B> class ifilteriter : public __iter<T> {
public:
    B (*predicate)(T);
    __iter<T> *iter;

    ifilteriter();
    ifilteriter(B (*predicate)(T), pyiter<T> *iterable);

    T next();
};

template<class T, class B> inline ifilteriter<T, B>::ifilteriter() {}
template<class T, class B> inline ifilteriter<T, B>::ifilteriter(B (*predicate)(T), pyiter<T> *iterable) {
    this->predicate = predicate;
    this->iter = iterable->__iter__();
}

template<class T, class B> T ifilteriter<T, B>::next() {
    for (; ; ) {
        const T& value = this->iter->next();
        if (this->predicate(value)) {
            return value;
        }
    }

    assert(false && "unreachable");
}

template<class T, class B> inline ifilteriter<T, B> *ifilter(B (*predicate)(T), pyiter<T> *iterable) {
    return new ifilteriter<T, B>(predicate, iterable);
}
template<class T> inline ifilteriter<T, bool> *ifilter(void * /* null */, pyiter<T> *iterable) {
    return new ifilteriter<T, bool>(_identity, iterable);
}

// ifilterfalse

template<class T, class B> class ifilterfalseiter : public __iter<T> {
public:
    B (*predicate)(T);
    __iter<T> *iter;

    ifilterfalseiter();
    ifilterfalseiter(B (*predicate)(T), pyiter<T> *iterable);

    T next();
};

template<class T, class B> inline ifilterfalseiter<T, B>::ifilterfalseiter() {}
template<class T, class B> inline ifilterfalseiter<T, B>::ifilterfalseiter(B (*predicate)(T), pyiter<T> *iterable) {
    this->predicate = predicate;
    this->iter = iterable->__iter__();
}

template<class T, class B> T ifilterfalseiter<T, B>::next() {
    for (; ; ) {
        const T& value = this->iter->next();
        if (!this->predicate(value)) {
            return value;
        }
    }

    assert(false && "unreachable");
}

template<class T, class B> inline ifilterfalseiter<T, B> *ifilterfalse(B (*predicate)(T), pyiter<T> *iterable) {
    return new ifilterfalseiter<T, B>(predicate, iterable);
}
template<class T> inline ifilterfalseiter<T, bool> *ifilterfalse(void * /* null */, pyiter<T> *iterable) {
    return new ifilterfalseiter<T, bool>(_identity, iterable);
}

// islice

template<class T> class isliceiter : public __iter<T> {
public:
    int current_position;
    int next_position;
    int stop;
    int step;
    __iter<T> *iter;

    isliceiter();
    isliceiter(pyiter<T> *iterable, int start, int stop, int step);

    T next();
};

template<class T> inline isliceiter<T>::isliceiter() {}
template<class T> inline isliceiter<T>::isliceiter(pyiter<T> *iterable, int start, int stop, int step) {
    this->current_position = 0;
    this->next_position = start;
    this->stop = stop;
    this->step = step;
    this->iter = iterable->__iter__();
}

template<class T> T isliceiter<T>::next() {
    if (this->next_position >= this->stop && this->stop != -1)
        throw new StopIteration();

    for (; this->current_position < this->next_position; ++this->current_position) {
        this->iter->next();
    }

    ++this->current_position;
    this->next_position += this->step;

    return this->iter->next();
}

inline int _start(int start) {
    return start;
}
inline int _start(void*) {
    return 0;
}
inline int _stop(int stop) {
    return stop;
}
inline int _stop(void*) {
    return -1;
}
inline int _step(int step) {
    if (step > 0) {
        return step;
    } else {
        return 1;
    }
}
inline int _step(void*) {
    return 1;
}
template<class T> inline bool _onearg(T /* stop */) {
    return false;
}
template<> inline bool _onearg(__ss_int stop) {
    return stop == -1;
}

template<class T, class U, class V, class W> inline isliceiter<T> *islice(pyiter<T> *iterable, U start, V stop, W step) {
  if (_onearg(stop)) {
      return new isliceiter<T>(iterable, 0, _stop(start), _step(step));
  } else {
      return new isliceiter<T>(iterable, _start(start), _stop(stop), _step(step));
  }
}

// imap

#define I(N, TP, FP, RP, AP, DP, CP, VP)                                                                 \
template<class R, TP> class imapiter##N : public __iter<R> {                                             \
public:                                                                                                  \
    bool exhausted;                                                                                      \
    R (*function)(FP);                                                                                   \
    RP                                                                                                   \
                                                                                                         \
    imapiter##N();                                                                                       \
    imapiter##N(R (*function)(FP), DP);                                                                  \
                                                                                                         \
    R next();                                                                                            \
};                                                                                                       \
                                                                                                         \
template<class R, TP> inline imapiter##N<R, FP>::imapiter##N() {                                         \
    this->exhausted = true;                                                                              \
}                                                                                                        \
template<class R, TP> inline imapiter##N<R, FP>::imapiter##N(R (*function)(FP), DP) {                    \
    this->exhausted = false;                                                                             \
    this->function = function;                                                                           \
    AP                                                                                                   \
}                                                                                                        \
                                                                                                         \
template<class R, TP> R imapiter##N<R, FP>::next() {                                                     \
    if (this->exhausted) {                                                                               \
        throw new StopIteration();                                                                       \
    }                                                                                                    \
                                                                                                         \
    try  {                                                                                               \
        return this->function(CP);                                                                       \
    } catch (StopIteration *) {                                                                          \
        this->exhausted = true;                                                                          \
        throw;                                                                                           \
    }                                                                                                    \
}                                                                                                        \
                                                                                                         \
template<class R, TP> inline imapiter##N<R, FP> *imap(int /* iterable_count */, R (*function)(FP), DP) { \
    return new imapiter##N<R, FP>(function, VP);                                                         \
}

#define S ,
#define L(P) class T##P
#define F(P) T##P
#define E(P) __iter<T##P> *iter##P;
#define A(P) this->iter##P = iterable##P->__iter__();
#define D(P) pyiter<T##P> *iterable##P
#define C(P) this->iter##P->next()
#define V(P) iterable##P

I(1, L(1), F(1), E(1), A(1), D(1), C(1), V(1))
I(2, L(1) S L(2), F(1) S F(2), E(1) E(2), A(1) A(2), D(1) S D(2), C(1) S C(2), V(1) S V(2))
I(3, L(1) S L(2) S L(3), F(1) S F(2) S F(3), E(1) E(2) E(3), A(1) A(2) A(3), D(1) S D(2) S D(3), C(1) S C(2) S C(3), V(1) S V(2) S V(3))
I(4, L(1) S L(2) S L(3) S L(4), F(1) S F(2) S F(3) S F(4), E(1) E(2) E(3) E(4), A(1) A(2) A(3) A(4), D(1) S D(2) S D(3) S D(4), C(1) S C(2) S C(3) S C(4), V(1) S V(2) S V(3) S V(4))
I(5, L(1) S L(2) S L(3) S L(4) S L(5), F(1) S F(2) S F(3) S F(4) S F(5), E(1) E(2) E(3) E(4) E(5), A(1) A(2) A(3) A(4) A(5), D(1) S D(2) S D(3) S D(4) S D(5), C(1) S C(2) S C(3) S C(4) S C(5), V(1) S V(2) S V(3) S V(4) S V(5))

#undef S
#undef L
#undef F
#undef E
#undef A
#undef D
#undef C
#undef V
#undef I

// starmap

// TODO

// tee

template<class T> class teecache {
public:
    typedef std::pair<T, int> item;

    int begin;
    int end;
    int clients;
    __GC_DEQUE(item) cache;

    teecache(int clients);

    void add(const T& value);
    T get(int position);
};

template<class T> inline teecache<T>::teecache(int clients) {
    this->begin = 0;
    this->end = 0;
    this->clients = clients;
}

template<class T> void teecache<T>::add(const T& value) {
    ++this->end;
    this->cache.push_back(std::make_pair(value, clients));
}

template<class T> T teecache<T>::get(int position) {
    assert(!this->cache.empty());

    while (!this->cache.front().second) {
        ++this->begin;
        this->cache.pop_front();
    }

    --this->cache[position - this->begin].second;
    return this->cache[position - this->begin].first;
}

template<class T> class teeiter : public __iter<T> {
public:
    int position;
    __iter<T> *iter;
    teecache<T> *cache;

    teeiter();
    teeiter(pyiter<T> *iterable, teecache<T> *cache);

    T next();
};

template<class T> inline teeiter<T>::teeiter() {}
template<class T> inline teeiter<T>::teeiter(pyiter<T> *iterable, teecache<T> *cache) {
    this->position = 0;
    this->iter = iterable->__iter__();
    this->cache = cache;
}

template<class T> T teeiter<T>::next() {
    if (this->position == this->cache->end) {
        this->cache->add(this->iter->next());
    }

    return this->cache->get(position++);
}

template<class T> inline tuple2<__iter<T> *, __iter<T> *> *tee(pyiter<T> *iterable, int n = 2) {
    teecache<T> *cache = new teecache<T>(n);

    if (n == 2) {
        return new tuple2<__iter<T> *, __iter<T> *>(n, new teeiter<T>(iterable, cache), new teeiter<T>(iterable, cache));
    }

    tuple2<__iter<T> *, __iter<T> *>* tuple = new tuple2<__iter<T> *, __iter<T> *>(1, new teeiter<T>(iterable, cache));

    for (int i = 1; i < n; ++i) {
        tuple->units.push_back(new teeiter<T>(iterable, cache));
    }

    return tuple;
}

// takewhile

template<class T, class B> class takewhileiter : public __iter<T> {
public:
    bool take;
    B (*predicate)(T);
    __iter<T> *iter;

    takewhileiter();
    takewhileiter(B (*predicate)(T), pyiter<T> *iterable);

    T next();
};

template<class T, class B> inline takewhileiter<T, B>::takewhileiter() {}
template<class T, class B> inline takewhileiter<T, B>::takewhileiter(B (*predicate)(T), pyiter<T> *iterable) {
    this->take = true;
    this->predicate = predicate;
    this->iter = iterable->__iter__();
}

template<class T, class B> T takewhileiter<T, B>::next() {
    if (take) {
        const T& value = this->iter->next();
        if (this->predicate(value)) {
            return value;
        }
        this->take = false;
    }

    throw new StopIteration();
}

template<class T, class B> inline takewhileiter<T, B> *takewhile(B (*predicate)(T), pyiter<T> *iterable) {
    return new takewhileiter<T, B>(predicate, iterable);
}

// izip

template<class T, class U> class izipiter;
template<class T> inline izipiter<T, T> *izip(int iterable_count, pyiter<T> *iterable, ...);

template<class T, class U> class izipiter : public __iter<tuple2<T, U> *> {
public:
    bool exhausted;
    __iter<T> *first;
    __iter<U> *second;

    izipiter();
    izipiter(pyiter<T> *iterable1, pyiter<U> *iterable2);

    tuple2<T, U> *next();
};

template<class T, class U> inline izipiter<T, U>::izipiter() {
    this->exhausted = true;
}
template<class T, class U> inline izipiter<T, U>::izipiter(pyiter<T> *iterable1, pyiter<U> *iterable2) {
    this->exhausted = false;
    this->first = iterable1->__iter__();
    this->second = iterable2->__iter__();
}

template<class T, class U> tuple2<T, U> *izipiter<T, U>::next() {
    if (this->exhausted) {
        throw new StopIteration();
    }

    tuple2<T, U> *tuple = new tuple2<T, U>;
    try  {
        tuple->first = this->first->next();
        tuple->second = this->second->next();
    } catch (StopIteration *) {
        this->exhausted = true;
        throw;
    }

    return tuple;
}

template<class T> class izipiter<T, T> : public __iter<tuple2<T, T> *> {
public:
    bool exhausted;
    __GC_VECTOR(__iter<T> *) iters;

    izipiter();
    izipiter(pyiter<T> *iterable);

    void push_iter(pyiter<T> *iterable);

    tuple2<T, T> *next();

    friend izipiter<T, T> *izip<T>(int iterable_count, pyiter<T> *iterable, ...);
};

template<class T> inline izipiter<T, T>::izipiter() {
    this->exhausted = true;
}
template<class T> inline izipiter<T, T>::izipiter(pyiter<T> *iterable) {
    this->exhausted = false;
    this->push_iter(iterable);
}
template<class T> void izipiter<T, T>::push_iter(pyiter<T> *iterable) {
    this->iters.push_back(iterable->__iter__());
}

template<class T> tuple2<T, T> *izipiter<T, T>::next() {
    if (this->exhausted) {
        throw new StopIteration();
    }

    tuple2<T, T> *tuple = new tuple2<T, T>;
    for (unsigned int i = 0; i < this->iters.size(); ++i) {
        try  {
            tuple->units.push_back(this->iters[i]->next());
        } catch (StopIteration *) {
            this->exhausted = true;
            throw;
        }
    }

    return tuple;
}

inline izipiter<void*, void*> *izip(int /* iterable_count */) {
    return new izipiter<void*, void*>();
}
template<class T, class U> inline izipiter<T, U> *izip(int /* iterable_count */, pyiter<T> *iterable1, pyiter<U> *iterable2) {
    return new izipiter<T, U>(iterable1, iterable2);
}
template<class T> inline izipiter<T, T> *izip(int iterable_count, pyiter<T> *iterable, ...) {
    izipiter<T, T> *iter = new izipiter<T, T>(iterable);

    va_list ap;
    va_start(ap, iterable);

    while (--iterable_count) {
        iter->push_iter(va_arg(ap, pyiter<T> *));
    }

    va_end(ap);

    return iter;
}

// izip_longest

template<class T, class U> class izip_longestiter;
template<class T, class F> inline izip_longestiter<T, T> *izip_longest(int iterable_count, F fillvalue, pyiter<T> *iterable, ...);

template<class T, class U> class izip_longestiter : public __iter<tuple2<T, U> *> {
public:
    bool exhausted;
    bool first_exhausted;
    bool second_exhausted;
    __iter<T> *first;
    __iter<U> *second;
    T fillvalue;

    izip_longestiter();
    izip_longestiter(T fillvalue, pyiter<T> *iterable1, pyiter<U>* iterable2);

    tuple2<T, U> *next();
};

template<class T, class U> inline izip_longestiter<T, U>::izip_longestiter() {
    this->exhausted = true;
}
template<class T, class U> inline izip_longestiter<T, U>::izip_longestiter(T fillvalue, pyiter<T> *iterable1, pyiter<U> *iterable2) {
    this->exhausted = false;
    this->first_exhausted = false;
    this->second_exhausted = false;
    this->first = iterable1->__iter__();
    this->second = iterable2->__iter__();
    this->fillvalue = fillvalue;
}

template<class T, class U> tuple2<T, U> *izip_longestiter<T, U>::next() {
    if (this->exhausted) {
        throw new StopIteration();
    }

    tuple2<T, U> *tuple = new tuple2<T, U>;

    if (this->first_exhausted) {
        tuple->first = this->fillvalue;
    } else {
        try {
            tuple->first = this->first->next();
        } catch (StopIteration *) {
            if (this->second_exhausted) {
                this->exhausted = true;
                throw;
            }
            this->first_exhausted = true;
            tuple->first = this->fillvalue;
        }

        if (this->second_exhausted) {
            tuple->second = (U)this->fillvalue;
            return tuple;
        }
    }

    try {
        tuple->second = this->second->next();
    } catch (StopIteration *) {
        if (this->first_exhausted) {
            this->exhausted = true;
            throw;
        }
        this->second_exhausted = true;
        tuple->second = (U)this->fillvalue;
    }

    return tuple;
}

template<class T> class izip_longestiter<T, T> : public __iter<tuple2<T, T> *> {
public:
    unsigned int exhausted;
    std::vector<char> exhausted_iter; // never use std::vector<bool> because this is *slow*
    __GC_VECTOR(__iter<T> *) iters;
    T fillvalue;

    izip_longestiter();
    izip_longestiter(T fillvalue, pyiter<T> *iterable);

    void push_iter(pyiter<T> *iterable);

    tuple2<T, T> *next();

    friend izip_longestiter<T, T> *izip_longest<T, T>(int iterable_count, T fillvalue, pyiter<T> *iterable, ...);
};

template<class T> inline izip_longestiter<T, T>::izip_longestiter() {
    this->exhausted = 0;
}
template<class T> inline izip_longestiter<T, T>::izip_longestiter(T fillvalue, pyiter<T> *iterable) {
    this->exhausted = 0;
    this->push_iter(iterable);
    this->fillvalue = fillvalue;
}

template<class T> void izip_longestiter<T, T>::push_iter(pyiter<T> *iterable) {
    this->iters.push_back(iterable->__iter__());
    this->exhausted_iter.push_back(0);
}

template<class T> tuple2<T, T> *izip_longestiter<T, T>::next() {
    if (this->exhausted == this->iters.size()) {
        throw new StopIteration();
    }

    tuple2<T, T> *tuple = new tuple2<T, T>;
    for (unsigned int i = 0; i < this->iters.size(); ++i) {
        if (!this->exhausted_iter[i]) {
            try  {
                tuple->units.push_back(this->iters[i]->next());
                continue;
            } catch (StopIteration *) {
                ++this->exhausted;
                if (this->exhausted == this->iters.size()) {
                    throw;
                }
                this->exhausted_iter[i] = 1;
            }
        }
        tuple->units.push_back(this->fillvalue);
    }

    return tuple;
}

template<class T> inline izip_longestiter<void*, void*> *izip_longest(int /* iterable_count */, T /* fillvalue */) {
    return new izip_longestiter<void*, void*>();
}
template<class T, class U, class F> inline izip_longestiter<T, U> *izip_longest(int iterable_count, F fillvalue, pyiter<T> *iterable1, pyiter<U> *iterable2) {
  return new izip_longestiter<T, U>((T)fillvalue, iterable1, iterable2);
}
template<class T, class F> inline izip_longestiter<T, T> *izip_longest(int iterable_count, F fillvalue, pyiter<T> *iterable, ...) {
    izip_longestiter<T, T> *iter = new izip_longestiter<T, T>((T)fillvalue, iterable);

    va_list ap;
    va_start(ap, iterable);

    while (--iterable_count) {
        iter->push_iter(va_arg(ap, pyiter<T> *));
    }

    va_end(ap);

    return iter;
}

/* Combinatoric generators */

// product

template<class T, class U> class productiter;
template<class T> inline productiter<T, T> *product(int iterable_count, int repeat, pyiter<T> *iterable, ...);

template<class T, class U> class productiter : public __iter<tuple2<T, U> *> {
public:
    bool exhausted;
    std::vector<T> values1;
    std::vector<U> values2;
    unsigned int indice1;
    unsigned int indice2;

    productiter();
    productiter(pyiter<T> *iterable1, pyiter<U> *iterable2);

    tuple2<T, U> *next();
};

template<class T, class U> inline productiter<T, U>::productiter() { }
template<class T, class U> inline productiter<T, U>::productiter(pyiter<T> *iterable1, pyiter<U> *iterable2) {
    this->exhausted = false;
    this->indice1 = 0;
    this->indice2 = 0;

    // TODO this is not optimal at all for pyseq
    // (could be improved with static polymorphism and partial specialization on templates templates)

    #define CACHE_VALUES(TYPE, ID)                            \
        __iter<TYPE> *iter##ID = iterable##ID->__iter__();    \
        for (; ; ) {                                          \
            try {                                             \
                this->values##ID.push_back(iter##ID->next()); \
            } catch (StopIteration *) {                       \
                break;                                        \
            }                                                 \
        }                                                     \
        if (this->values##ID.empty()) {                       \
            this->exhausted = true;                           \
            return;                                           \
        }

    CACHE_VALUES(T, 1)
    CACHE_VALUES(U, 2)

    #undef CACHE_VALUES
}

template<class T, class U> tuple2<T, U> *productiter<T, U>::next() {
    if (this->exhausted) {
        throw new StopIteration();
    }

    tuple2<T, U> *tuple = new tuple2<T, U>;

    tuple->first = this->values1[this->indice1];
    tuple->second = this->values2[this->indice2];

    ++this->indice2;
    if (this->indice2 == this->values2.size()) {
        this->indice2 = 0;

        ++this->indice1;
        if (this->indice1 == this->values1.size()) {
            this->exhausted = true;
        }
    }

    return tuple;
}

template<class T> class productiter<T, T> : public __iter<tuple2<T, T> *> {
public:
    bool exhausted;
    unsigned int highest_exhausted;
    std::vector<std::vector<T> > values;
    std::vector<unsigned int> iter;
    std::vector<unsigned int> indices;

    productiter();

    void push_iter(pyiter<T> *iterable);
    void repeat(int times);

    tuple2<T, T> *next();

    friend productiter<T, T> *product<T>(int iterable_count, int repeat, pyiter<T> *iterable, ...);
};

template<class T> inline productiter<T, T>::productiter() {
    this->exhausted = false;
    this->highest_exhausted = 0;
}

template<class T> void productiter<T, T>::push_iter(pyiter<T> *iterable) {
    this->values.push_back(std::vector<T>());
    this->indices.push_back(0);

    // TODO this is not optimal at all for pyseq
    // (could be improved with static polymorphism and partial specialization on templates templates)
    __iter<T> *iter = iterable->__iter__();
    for (; ; ) {
        try {
            this->values.back().push_back(iter->next());
        } catch (StopIteration *) {
            break;
        }
    }

    if (!this->values.back().size()) {
        this->exhausted = true;
    } else if (this->values.back().size() == 1 && this->highest_exhausted == this->values.size() - 1) {
        ++this->highest_exhausted;
    }
}

template<class T> inline void productiter<T, T>::repeat(int times) {
    if (this->highest_exhausted == this->values.size()) {
      this->highest_exhausted *= times;
    }

    for (int time = 0; time < times; ++time) {
        for (int iter = 0; iter < this->values.size(); ++iter) {
            this->iter.push_back(iter);
            this->indices.push_back(0);
        }
    }
}

template<class T> tuple2<T, T> *productiter<T, T>::next() {
    if (this->exhausted) {
        throw new StopIteration();
    }

    tuple2<T, T> *tuple = new tuple2<T, T>;

    if (this->iter.size()) {
        for (int i = 0; i < (int)this->iter.size(); ++i) {
            int j = this->iter[i];
            tuple->units.push_back(this->values[j][this->indices[i]]);
        }
        for (int i = this->iter.size() - 1; i > -1; --i) {
            int j = this->iter[i];
            ++this->indices[i];
            if (i <= (int)this->highest_exhausted) {
                if (this->indices[i] >= this->values[j].size() - 1) {
                    ++this->highest_exhausted;
                    if (this->highest_exhausted > this->iter.size()) {
                        this->exhausted = true;
                    }
                    break;
                }
            }
            if (this->indices[i] == this->values[j].size()) {
                this->indices[i] = 0;
            } else {
                break;
            }
        }
    } else {
        this->exhausted = true;
    }

    return tuple;
}

inline productiter<void*, void*> *product(int /* iterable_count */, int /* repeat */) {
    return new productiter<void*, void*>();
}
template<class T> inline productiter<T, T> *product(int /* iterable_count */, int repeat, pyiter<T> *iterable1, pyiter<T> *iterable2) {
    productiter<T, T> *iter = new productiter<T, T>();

    iter->push_iter(iterable1);
    iter->push_iter(iterable2);

    iter->repeat(repeat);

    return iter;
}
template<class T, class U> inline productiter<T, U> *product(int /* iterable_count */, int /* repeat */, pyiter<T> *iterable1, pyiter<U> *iterable2) {
    return new productiter<T, U>(iterable1, iterable2);
}
template<class T> inline productiter<T, T> *product(int iterable_count, int repeat, pyiter<T> *iterable, ...) {
    productiter<T, T> *iter = new productiter<T, T>();

    int iter_count = iterable_count;

    iter->push_iter(iterable);

    va_list ap;
    va_start(ap, iterable);

    while (--iter_count) {
        iter->push_iter(va_arg(ap, pyiter<T> *));
    }

    va_end(ap);

    iter->repeat(repeat);

    return iter;
}

// permutations

template<class T> class permutationsiter : public __iter<tuple2<T, T> *> {
public:
    int r;
    int len;
    int current;
    unsigned int* indices;
    unsigned int* cycles;
    std::vector<T> cache;

    permutationsiter();
    permutationsiter(pyiter<T> *iterable, __ss_int r);

    ~permutationsiter();

    tuple2<T, T> *next();

private: // We might want to implement this, but we certainly don't want the default ones
    permutationsiter(const permutationsiter& other);
    permutationsiter<T>& operator=(const permutationsiter& other);
};

template<class T> inline permutationsiter<T>::permutationsiter() {
    this->indices = 0;
    this->cycles = 0;
}
template<class T> inline permutationsiter<T>::permutationsiter(pyiter<T> *iterable, __ss_int r) {
    this->r = r;
    this->len = 0;

    // TODO this is not optimal at all for pyseq
    // (could be improved with static polymorphism and partial specialization on templates templates)
    __iter<T> *iter = iterable->__iter__();
    for (; ; ) {
        try  {
            this->cache.push_back(iter->next());
        } catch (StopIteration *) {
            break;
        }
    }
    this->len = this->cache.size();

    if (r > this->len) {
        this->current = -1;
        this->indices = 0;
        this->cycles = 0;
    } else {
        this->current = this->r;
        this->indices = new unsigned int[this->len];
        this->cycles = new unsigned int[this->r];

        for (int i = 0; i < this->len; ++i) {
            this->indices[i] = i;
        }
        for (int i = 0; i < this->r; ++i) {
            this->cycles[i] = this->len - i;
        }
    }
}

template<class T> inline permutationsiter<T>::~permutationsiter() {
    delete[] this->indices;
    delete[] this->cycles;
}

template<class T> tuple2<T, T> *permutationsiter<T>::next() {
    if (this->current == this->r) {
        tuple2<T, T> *tuple = new tuple2<T, T>;
        for (int i = 0; i < this->r; ++i) {
            tuple->units.push_back(this->cache[i]);
        }
        --this->current;
        return tuple;
    }

    for (; ; ) {
        if (this->current == -1) {
            throw new StopIteration();
        }

        int cycle = --this->cycles[this->current];
        if (cycle) {
            assert(this->current < this->len);
            std::swap(this->indices[this->current], this->indices[cycle ? this->len - cycle : 0]);
            tuple2<T, T> *tuple = new tuple2<T, T>;
            for (int i = 0; i < this->r; ++i) {
                tuple->units.push_back(this->cache[this->indices[i]]);
            }
            this->current = this->r - 1;
            return tuple;
        } else {
            int last = this->indices[this->current];
            for (int i = this->current; i < this->len - 1; ++i) {
                this->indices[i] = this->indices[i + 1];
            }
            this->indices[this->len - 1] = last;
            this->cycles[this->current] = this->len - this->current;
            --this->current;
        }
    }
}

template<class T> inline permutationsiter<T> *permutations(pyiter<T> *iterable, void* /* r */) {
    return new permutationsiter<T>(iterable, iterable->__len__());
}
template<class T> inline permutationsiter<T> *permutations(pyiter<T> *iterable, __ss_int r) {
    return new permutationsiter<T>(iterable, r);
}

// combinations

template<class T> class combinationsiter : public __iter<tuple2<T, T> *> {
public:
    int r;
    int len;
    int current;
    int* indices;
    __GC_VECTOR(T) cache;

    combinationsiter();
    combinationsiter(pyiter<T> *iterable, int r);

    ~combinationsiter();

    tuple2<T, T> *next();

private: // We might want to implement this, but we certainly don't want the default ones
    combinationsiter(const combinationsiter& other);
    combinationsiter<T>& operator=(const combinationsiter& other);
};

template<class T> inline combinationsiter<T>::combinationsiter() {
    this->indices = 0;
}
template<class T> inline combinationsiter<T>::combinationsiter(pyiter<T> *iterable, int r) {
    this->r = r;
    this->len = 0;

    // TODO this is not optimal at all for pyseq
    // (could be improved with static polymorphism and partial specialization on templates templates)
    __iter<T> *iter = iterable->__iter__();
    for (; ; ) {
        try  {
            this->cache.push_back(iter->next());
        } catch (StopIteration *) {
            break;
        }
    }
    this->len = this->cache.size();

    if (r > this->len) {
        this->current = -1;
        this->indices = 0;
    } else {
        this->current = r;
        this->indices = new int[r];

        for (int i = 0; i < this->r; ++i) {
            this->indices[i] = i;
        }
    }
}

template<class T> inline combinationsiter<T>::~combinationsiter() {
    delete[] this->indices;
}

template<class T> tuple2<T, T> *combinationsiter<T>::next() {
    if (this->current == this->r) {
        tuple2<T, T> *tuple = new tuple2<T, T>;
        for (int i = 0; i < this->r; ++i) {
            tuple->units.push_back(this->cache[i]);
        }
        --this->current;
        return tuple;
    }

    for (; ; ) {
        if (this->current == -1) {
            throw new StopIteration();
        }

        while (this->indices[this->current] == this->current + this->len - this->r) {
            --this->current;

            if (this->current == -1) {
                throw new StopIteration();
            }
        }


        ++this->indices[this->current];
        for (int i = this->current + 1; i < this->r; ++i) {
            this->indices[i] = this->indices[i - 1] + 1;
        }

        tuple2<T, T> *tuple = new tuple2<T, T>;
        for (int i = 0; i < this->r; ++i) {
            tuple->units.push_back(this->cache[this->indices[i]]);
        }

        this->current = this->r - 1;

        return tuple;
    }
}

template<class T> inline combinationsiter<T> *combinations(pyiter<T> *iterable, int r) {
    return new combinationsiter<T>(iterable, r);
}

// combinations_with_replacement

template<class T> class combinations_with_replacementiter : public __iter<tuple2<T, T> *> {
public:
    int r;
    int len;
    int current;
    int* indices;
    __GC_VECTOR(T) cache;

    combinations_with_replacementiter();
    combinations_with_replacementiter(pyiter<T> *iterable, int r);

    ~combinations_with_replacementiter();

    tuple2<T, T> *next();

private: // We might want to implement this, but we certainly don't want the default ones
    combinations_with_replacementiter(const combinations_with_replacementiter& other);
    combinations_with_replacementiter<T>& operator=(const combinations_with_replacementiter& other);
};

template<class T> inline combinations_with_replacementiter<T>::combinations_with_replacementiter() {
    this->indices = 0;
}
template<class T> inline combinations_with_replacementiter<T>::combinations_with_replacementiter(pyiter<T> *iterable, int r) {
    this->r = r;
    this->len = 0;

    // TODO this is not optimal at all for pyseq
    // (could be improved with static polymorphism and partial specialization on templates templates)
    __iter<T> *iter = iterable->__iter__();
    for (; ; ) {
        try  {
            this->cache.push_back(iter->next());
        } catch (StopIteration *) {
            break;
        }
    }
    this->len = this->cache.size();

    if (!this->len && r) {
        this->current = -1;
        this->indices = 0;
    } else {
        this->current = r;
        this->indices = new int[r];

        for (int i = 0; i < this->r; ++i) {
            this->indices[i] = 0;
        }
    }
}

template<class T> inline combinations_with_replacementiter<T>::~combinations_with_replacementiter() {
    delete[] this->indices;
}

template<class T> tuple2<T, T> *combinations_with_replacementiter<T>::next() {
    if (this->current == this->r) {
        tuple2<T, T> *tuple = new tuple2<T, T>;
        for (int i = 0; i < this->r; ++i) {
            tuple->units.push_back(this->cache[0]);
        }
        --this->current;
        return tuple;
    }

    for (; ; ) {
        if (this->current == -1) {
            throw new StopIteration();
        }

        while (this->indices[this->current] == this->len - 1) {
            --this->current;

            if (this->current == -1) {
                throw new StopIteration();
            }
        }

        ++this->indices[this->current];
        for (int i = this->current + 1; i < this->r; ++i) {
            this->indices[i] = this->indices[this->current];
        }

        tuple2<T, T> *tuple = new tuple2<T, T>;
        for (int i = 0; i < this->r; ++i) {
            tuple->units.push_back(this->cache[this->indices[i]]);
        }

        this->current = this->r - 1;

        return tuple;
    }
}

template<class T> inline combinations_with_replacementiter<T> *combinations_with_replacement(pyiter<T> *iterable, int r) {
    return new combinations_with_replacementiter<T>(iterable, r);
}

void __init();

} // module namespace
#endif
