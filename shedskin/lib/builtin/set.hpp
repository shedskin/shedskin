/* Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE) */

/*
set implementation, partially derived from CPython,
copyright Python Software Foundation (http://www.python.org/download/releases/2.6.2/license/)
*/

template <class T> set<T>::set(int frozen) : frozen(frozen) {
    this->__class__ = cl_set;
    this->hash = -1;
    EMPTY_TO_MINSIZE(this);
}

#ifdef __SS_BIND

template<class T> set<T>::set(PyObject *p) {
    this->__class__ = cl_set;
    this->hash = -1;
    EMPTY_TO_MINSIZE(this);
    if(PyFrozenSet_CheckExact(p))
        frozen = 1;
    else if(PyAnySet_CheckExact(p))
        frozen = 0;
    else
        throw new TypeError(new str("error in conversion to Shed Skin (set expected)"));

    PyObject *iter = PyObject_GetIter(p), *item;
    while ((item = PyIter_Next(iter))) {
        add(__to_ss<T>(item));
        Py_DECREF(item);
    }
    Py_DECREF(iter);
}

template<class T> PyObject *set<T>::__to_py__() {
    list<T> *l = new list<T>(this); /* XXX optimize */
    PyObject *s;
    PyObject *p = __to_py(l);
    if(frozen)
        s = PyFrozenSet_New(p);
    else
        s = PySet_New(p);
    Py_DECREF(p);
    return s;
}

#endif

template<class T> template<class U> set<T>::set(U *other, int frozen) {
    this->__class__ = cl_set;
    this->frozen = frozen;
    this->hash = -1;
    EMPTY_TO_MINSIZE(this);
    update(1, other);
}

template<class T> template<class U> set<T>::set(U *other) {
    this->__class__ = cl_set;
    this->frozen = 0;
    this->hash = -1;
    EMPTY_TO_MINSIZE(this);
    update(1, other);
}

template <class T> set<T>& set<T>::operator=(const set<T>& other) {
    // copy test
    /*int i;
    for (i=0; i<8; i++) {
        smalltable[i].use = unused;
    }

    table = smalltable;
    mask = MINSIZE - 1;
    used = 0;
    fill = 0;

    update(other);*/

    memcpy((void*)this, (void*)&other, sizeof(set<T>));
    int table_size = sizeof(setentry<T>) * (other.mask+1);
    table = (setentry<T>*)myallocate<T>(table_size);
    memcpy(table, other.table, table_size);
    return *this;
}

template<class T> __ss_bool set<T>::__eq__(pyobj *p) { /* XXX check hash */
    set<T> *b = (set<T> *)p;

    if( b->__len__() != this->__len__())
        return False;

    int pos = 0;
    setentry<T> *entry;
    while (next(&pos, &entry)) {
        if(!b->__contains__(entry))
            return False;
    }
    return True;
}

template <class T> void *set<T>::remove(T key) {
    if (!do_discard(key)) throw new KeyError(repr(key));
    return NULL;
}

template<class T> __ss_bool set<T>::__ge__(set<T> *s) {
    return issuperset(s);
}

template<class T> __ss_bool set<T>::__le__(set<T> *s) {
    return issubset(s);
}

template<class T> __ss_bool set<T>::__lt__(set<T> *s) {
    return issubset(s);
}

template<class T> __ss_bool set<T>::__gt__(set<T> *s) {
    return issuperset(s);
}

template<class T> __ss_int set<T>::__cmp__(pyobj *p) {
    /* XXX sometimes TypeError, sometimes not? */
    set<T> *s = (set<T> *)p;
    if(issubset(s)) return -1;
    else if(issuperset(s)) return 1;
    return 0;
}

template<class T> long set<T>::__hash__() {
    if(!this->frozen)
        throw new TypeError(new str("unhashable type: 'set'"));
    long h, hash = 1927868237L;
    if (this->hash != -1)
        return this->hash;
    hash *= __len__() + 1;
    int pos = 0;
    setentry<T> *entry;
    while (next(&pos, &entry)) {
        h = entry->hash;
        hash ^= (h ^ (h << 16) ^ 89869747L)  * 3644798167u;
    }
    hash = hash * 69069L + 907133923L;
    if (hash == -1)
        hash = 590923713L;
    this->hash = hash;
    return hash;
}

template <class T> setentry<T>* set<T>::lookup(T key, long hash) const {

    int i = hash & mask;
    setentry<T>* entry = &table[i];
    if (!(entry->use) || __eq(entry->key, key))
        return entry;

    setentry <T>* freeslot;

    if (entry->use == dummy)
        freeslot = entry;
    else
        freeslot = NULL;

    unsigned int perturb;
    for (perturb = hash; ; perturb >>= PERTURB_SHIFT) {
        i = (i << 2) + i + perturb + 1;
        entry = &table[i & mask];
        if (!(entry->use)) {
            if (freeslot != NULL)
                entry = freeslot;
            break;
        }
        if (__eq(entry->key, key))
            break;

        else if (entry->use == dummy && freeslot == NULL)
            freeslot = entry;
	}
	return entry;
}

template <class T> void set<T>::insert_key(T key, long hash) {
    setentry<T>* entry;

    entry = lookup(key, hash);
    if (!(entry->use)) {
        fill++;
        entry->key = key;
        entry->hash = hash;
        entry->use = active;
        used++;
    }
    else if (entry->use == dummy) {
        entry->key = key;
        entry->hash = hash;
        entry->use = active;
        used++;
    }
}

template <class T> void *set<T>::add(T key)
{
    long hash = hasher<T>(key);
    int n_used = used;
    insert_key(key, hash);
    if ((used > n_used && fill*3 >= (mask+1)*2))
        resize(used>50000 ? used*2 : used*4);
    return NULL;
}

template <class T> void *set<T>::add(setentry<T>* entry)
{
    int n_used = used;

    insert_key(entry->key, entry->hash);
    if ((used > n_used && fill*3 >= (mask+1)*2))
        resize(used>50000 ? used*2 : used*4);
    return NULL;
}

template <class T> int freeze(set<T> *key) {
    int orig_frozen = key->frozen;
    key->frozen = 1;
    return orig_frozen;
}
template <class T> void unfreeze(set<T> *key, int orig_frozen) {
    key->frozen = orig_frozen;
}
template <class U> int freeze(U key) {
    return 0;
}
template <class U> void unfreeze(U, int orig_frozen) {
}

template <class T> void *set<T>::discard(T key) {
    do_discard(key);
    return NULL;
}

template <class T> int set<T>::do_discard(T key) {
    int orig_frozen = freeze(key);
	long hash = hasher<T>(key);
	setentry<T> *entry;

	entry = lookup(key, hash);
    unfreeze(key, orig_frozen);

	if (entry->use != active)
		return DISCARD_NOTFOUND; // nothing to discard

	entry->use = dummy;
	used--;
	return DISCARD_FOUND;
}

template<class T> T set<T>::pop() {
    int i = 0;
	setentry<T> *entry;

	if (used == 0)
		throw new KeyError(new str("pop from an empty set"));

	entry = &table[0];
	if (entry->use != active) {
		i = entry->hash;
		if (i > mask || i < 1)
			i = 1;	/* skip slot 0 */
		while ((entry = &table[i])->use != active) {
			i++;
			if (i > mask)
				i = 1;
		}
	}
	entry->use = dummy;
	used--;
	table[0].hash = i + 1;  /* next place to start */
	return entry->key;
}

/*
 * Iterate over a set table.  Use like so:
 *
 *     Py_ssize_t pos;
 *     setentry *entry;
 *     pos = 0;   # important!  pos should not otherwise be changed by you
 *     while (set_next(yourset, &pos, &entry)) {
 *              Refer to borrowed reference in entry->key.
 *     }
 */
template <class T> int set<T>::next(int *pos_ptr, setentry<T> **entry_ptr)
{
	int i;

	i = *pos_ptr;

	while (i <= mask && (table[i].use != active))
		i++;
	*pos_ptr = i+1;
	if (i > mask)
		return 0;
	*entry_ptr = &table[i];
	return 1;
}

/*
Internal routine used by set_table_resize() to insert an item which is
known to be absent from the set.  This routine also assumes that
the set contains no deleted entries.  Besides the performance benefit,
using insert() in resize() is dangerous (SF bug #1456209).
*/
template <class T> void set<T>::insert_clean(T key, long hash)
{
	int i;
	unsigned int perturb;
	setentry<T> *entry;

	i = hash & mask;

	entry = &table[i];
	for (perturb = hash; entry->use; perturb >>= PERTURB_SHIFT) {
		i = (i << 2) + i + perturb + 1;
		entry = &table[i & mask];
	}
	fill++;
	entry->key = key;
	entry->hash = hash;
	entry->use = active;
	used++;
}


/*
Restructure the table by allocating a new table and reinserting all
keys again.  When entries have been deleted, the new table may
actually be smaller than the old one.
*/
template <class T> void set<T>::resize(int minused)
{
	int newsize;
	setentry<T> *oldtable, *newtable, *entry;
	int i;
	setentry<T> small_copy[MINSIZE];

	/* Find the smallest table size > minused. */
	for (newsize = MINSIZE;
	     newsize <= minused && newsize > 0;
	     newsize <<= 1)
		;
	if (newsize <= 0) {
		//XXX raise memory error
	}

	/* Get space for a new table. */
	oldtable = table;

	if (newsize == MINSIZE) {
		/* A large table is shrinking, or we can't get any smaller. */
		newtable = smalltable;
		if (newtable == oldtable) {
			if (fill == used) {
				/* No dummies, so no point doing anything. */
				return;
			}
			/* We're not going to resize it, but rebuild the
			   table anyway to purge old dummy entries.
			   Subtle:  This is *necessary* if fill==size,
			   as set_lookkey needs at least one virgin slot to
			   terminate failing searches.  If fill < size, it's
			   merely desirable, as dummies slow searches. */
			memcpy(small_copy, oldtable, sizeof(small_copy));
			oldtable = small_copy;
		}
	}
	else {
        newtable = (setentry<T>*) myallocate<T>(sizeof(setentry<T>) * newsize);
	}

	/* Make the set empty, using the new table. */
	table = newtable;
	mask = newsize - 1;

	memset(newtable, 0, sizeof(setentry<T>) * newsize);

    i = used;
    used = 0;
	fill = 0;

	/* Copy the data over;
	   dummy entries aren't copied over */
	for (entry = oldtable; i > 0; entry++) {
		if (entry->use == active) {
			/* ACTIVE */
			--i;
			insert_clean(entry->key, entry->hash);
		}
	}
}

template<class T> str *set<T>::__repr__() {
    str *r;

    if(this->frozen) {
        if(used == 0)
            return new str("frozenset()");
        r = new str("frozenset({");
    }
    else {
        if(used == 0)
            return new str("set()");
        r = new str("{");
    }

    int rest = used-1;

    int pos = 0;
    setentry<T>* entry;
    while (next(&pos, &entry)) {
        T e = entry->key;
        r->unit += repr(e)->unit;
        if(rest)
           r->unit += ", ";
        --rest;
    }
    if(this->frozen)
        r->unit += "})";
    else
        r->unit += "}";
    return r;
}

template<class T> __ss_int set<T>::__len__() {
    return used;
}

template <class T> __ss_bool set<T>::__contains__(T key) {
    long hash = hasher(key);
	setentry<T> *entry;

	entry = lookup(key, hash);

	return __mbool(entry->use==active);
}

template <class T> __ss_bool set<T>::__contains__(setentry<T>* entry) {
	entry = lookup(entry->key, entry->hash);

	return __mbool(entry->use == active);
}

template <class T> void *set<T>::clear()
{
	setentry<T> *entry, *table;
	int table_is_malloced;
	size_t fill;
	setentry<T> small_copy[MINSIZE];

    table = this->table;
	table_is_malloced = table != smalltable;

	/* This is delicate.  During the process of clearing the set,
	 * decrefs can cause the set to mutate.  To avoid fatal confusion
	 * (voice of experience), we have to make the set empty before
	 * clearing the slots, and never refer to anything via so->ref while
	 * clearing.
	 */
	fill = this->fill;
	if (table_is_malloced)
		EMPTY_TO_MINSIZE(this);

	else if (fill > 0) {
		/* It's a small table with something that needs to be cleared.
		 * Afraid the only safe way is to copy the set entries into
		 * another small table first.
		 */
		// ffao: is this really needed without reference counting?
		//memcpy(small_copy, table, sizeof(small_copy));
		//table = small_copy;
		EMPTY_TO_MINSIZE(this);
	}
	/* else it's a small table that's already empty */

	/* if (table_is_malloced)
		PyMem_DEL(table); */
	return NULL;
}

template<class T> template<class U> void *set<T>::update(int, U *iter) {
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN(e,iter,1,2,3)
        add(e);
    END_FOR
    return NULL;
}

template <class T> void *set<T>::update(int, set<T>* other)
{
	int i;
	setentry<T> *entry;

	/* if (other == this || other->used == 0)
		// a.update(a) or a.update({}); nothing to do
		return 0; */
	/* Do one big resize at the start, rather than
	 * incrementally resizing as we insert new keys.  Expect
	 * that there will be no (or few) overlapping keys.
	 */
	if ((fill + other->used)*3 >= (mask+1)*2)
	   resize((used + other->used)*2);
	for (i = 0; i <= other->mask; i++) {
		entry = &other->table[i];
		if (entry->use == active) {
			insert_key(entry->key, entry->hash);
		}
	}
    return NULL;
}

template<class T> template<class U, class V> void *set<T>::update(int, U *iter, V *iter2) {
    update(1, iter);
    update(1, iter2);
    return NULL;
}

template<class T> template<class U, class V, class W> void *set<T>::update(int, U *iter, V *iter2, W *iter3) {
    update(1, iter);
    update(1, iter2);
    update(1, iter3);
    return NULL;
}


template<class T> template<class U> set<T> *set<T>::__ss_union(int, U *other) {
    set<T> *c = new set<T>(this->frozen);
    *c = *this;
    c->update(1, other);
    return c;
}

template<class T> set<T> *set<T>::__ss_union(int, set<T> *s) {
    set<T> *a, *b;
    set<T> *c = new set<T>(this->frozen);

    if(len(s) < len(this)) { a = s; b = this; }
    else { a = this; b = s; }

    *c = *b;
    c->update(1, a);

    return c;
}


template<class T> template<class U, class V> set<T> *set<T>::__ss_union(int, U *other, V *other2) {
    set<T> *c = new set<T>(this->frozen);
    *c = *this;
    c->update(1, other, other2);
    return c;
}

template<class T> template<class U, class V, class W> set<T> *set<T>::__ss_union(int, U *other, V *other2, W *other3) {
    set<T> *c = new set<T>(this->frozen);
    *c = *this;
    c->update(1, other, other2, other3);
    return c;
}

template<class T> set<T> *set<T>::symmetric_difference(set<T> *s) {
    set<T> *a, *b;
    set<T> *c = new set<T>(this->frozen);

    if(len(s) < len(this)) { a = s; b = this; }
    else { a = this; b = s; }

    *c = *b;

    int pos = 0;
    setentry<T> *entry;

    while (a->next(&pos, &entry)) {
        if (b->__contains__(entry))
            c->discard(entry->key);
        else
            c->add(entry);
    }

    return c;
}

template<class T> template <class U> set<T> *set<T>::intersection(int, U *iter) {
    set<T>* result = new set<T>;
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN(e,iter,1,2,3)
        if (__contains__(e)) {
            result->add(e);
        }
    END_FOR
    return result;
}

template<class T> set<T> *set<T>::intersection(int, set<T> *s) {
    set<T> *a, *b;
    set<T> *c = new set<T>(this->frozen);

    if(len(s) < len(this)) { a = s; b = this; }
    else { a = this; b = s; }

    int pos = 0;
    setentry<T> *entry;

    while (a->next(&pos, &entry)) {
        if(b->__contains__(entry))
            c->add(entry);
    }

    return c;
}

template<class T> template<class U, class V> set<T> *set<T>::intersection(int, U *iter, V *iter2) {
    return intersection(1, iter)->intersection(1, iter2);
}

template<class T> template<class U, class V, class W> set<T> *set<T>::intersection(int, U *iter, V *iter2, W *iter3) {
    return intersection(1, iter)->intersection(1, iter2)->intersection(1, iter3);
}


template<class T> template<class U> set<T>* set<T>::difference(int, U *other) {
    return difference(1, new set<T>(other));
}

template<class T> template<class U, class V> set<T>* set<T>::difference(int, U *other, V *other2) {
    set<T> *result = difference(1, new set<T>(other));
    return result->difference(1, new set<T>(other2));
}

template<class T> template<class U, class V, class W> set<T>* set<T>::difference(int, U *other, V *other2, W *other3) {
    set<T> *result = difference(1, new set<T>(other));
    result = result->difference(1, new set<T>(other2));
    return result->difference(1, new set<T>(other3));
}

template <class T> set<T>* set<T>::difference(int, set<T> *other)
{
    set<T>* result = new set<T>;
    int pos = 0;
    setentry<T> *entry;

    while (next(&pos, &entry)) {
        if (!other->__contains__(entry)) {
            result->add(entry);
        }
    }

    return result;
}

template<class T> set<T> *set<T>::__and__(set<T> *s) {
    return intersection(1, s);
}
template<class T> set<T> *set<T>::__or__(set<T> *s) {
    return __ss_union(1, s);
}
template<class T> set<T> *set<T>::__xor__(set<T> *s) {
    return symmetric_difference(s);
}
template<class T> set<T> *set<T>::__sub__(set<T> *s) {
    return difference(1, s);
}
template<class T> set<T> *set<T>::__iand__(set<T> *s) {
    *this = intersection(1, s);
    return this;
}
template<class T> set<T> *set<T>::__ior__(set<T> *s) {
    *this = __ss_union(1, s);
    return this;
}
template<class T> set<T> *set<T>::__ixor__(set<T> *s) {
    *this = symmetric_difference(s);
    return this;
}
template<class T> set<T> *set<T>::__isub__(set<T> *s) {
    *this = difference(1, s);
    return this;
}

template<class T> void *set<T>::difference_update(int, set<T> *s) {
    set<T> *c = difference(1, s);
    *this = *c; /* XXX don't copy */
    return NULL;
}


template<class T> template <class U> void *set<T>::difference_update(int, U *iter) {
    difference_update(1, new set<T>(iter));
    return NULL;
}

template<class T> template<class U, class V> void *set<T>::difference_update(int, U *iter, V *iter2) {
    difference_update(1, iter);
    difference_update(1, iter2);
    return NULL;
}

template<class T> template<class U, class V, class W> void *set<T>::difference_update(int, U *iter, V *iter2, W *iter3) {
    difference_update(1, iter);
    difference_update(1, iter2);
    difference_update(1, iter3);
    return NULL;
}

template<class T> void *set<T>::symmetric_difference_update(set<T> *s) {
    set<T> *c = symmetric_difference(s);
    *this = *c;
    return NULL;
}

template<class T> void *set<T>::intersection_update(int, set<T> *s) {
    set<T> *c = intersection(1, s);
    *this = *c;
    return NULL;
}

template<class T> template<class U> void *set<T>::intersection_update(int, U *iter) {
    intersection_update(1, new set<T>(iter));
    return NULL;
}

template<class T> template<class U, class V> void *set<T>::intersection_update(int, U *iter, V *iter2) {
    intersection_update(1, new set<T>(iter));
    intersection_update(1, new set<T>(iter2));
    return NULL;
}

template<class T> template<class U, class V, class W> void *set<T>::intersection_update(int, U *iter, V *iter2, W *iter3) {
    intersection_update(1, new set<T>(iter));
    intersection_update(1, new set<T>(iter2));
    intersection_update(1, new set<T>(iter3));
    return NULL;
}

template<class T> set<T> *set<T>::copy() {
    set<T> *c = new set<T>(this->frozen);
    *c = *this;
    return c;
}

template<class T> __ss_bool set<T>::issubset(set<T> *s) {
    if(__len__() > s->__len__()) { return False; }
    typename set<T>::for_in_unit e;
    typename set<T>::for_in_loop __3;
    int __2;
    set<T> *__1;
    FOR_IN(e,this,1,2,3)
        if(!s->__contains__(e))
            return False;
    END_FOR
    return True;
}

template<class T> __ss_bool set<T>::issuperset(set<T> *s) {
    if(__len__() < s->__len__()) return False;
    typename set<T>::for_in_unit e;
    typename set<T>::for_in_loop __3;
    int __2;
    set<T> *__1;
    FOR_IN(e,s,1,2,3)
        if(!__contains__(e))
            return False;
    END_FOR
    return True;
}

template<class T> __ss_bool set<T>::isdisjoint(set<T> *other) {
    int pos = 0;
    setentry<T> *entry;
    while (next(&pos, &entry)) {
        if (other->__contains__(entry)) {
            return False;
        }
    }
    return True;
}


template<class T> __ss_bool set<T>::issubset(pyiter<T> *s) {
    return issubset(new set<T>(s));
}

template<class T> __ss_bool set<T>::issuperset(pyiter<T> *s) {
    return issuperset(new set<T>(s));
}

template<class T> __ss_bool set<T>::isdisjoint(pyiter<T> *s) {
    return isdisjoint(new set<T>(s));
}

template<class T> set<T> *set<T>::__copy__() {
    set<T> *c = new set<T>();
    *c = *this;
    return c;
}

template<class T> set<T> *set<T>::__deepcopy__(dict<void *, pyobj *> *memo) {
    set<T> *c = new set<T>();
    memo->__setitem__(this, c);
    typename set<T>::for_in_unit e;
    typename set<T>::for_in_loop __3;
    int __2;
    set<T> *__1;
    FOR_IN(e,this,1,2,3)
        c->add(__deepcopy(e, memo));
    END_FOR
    return c;
}

template<class T> __setiter<T>::__setiter(set<T> *p) {
    this->p = p;
    this->pos = 0;
    this->si_used = p->used;
}

template<class T> T __setiter<T>::__next__() {
    if (si_used != p->used) {
        si_used = -1;
        __throw_set_changed();
    }
    int ret = p->next(&pos, &entry);
    if (!ret) __throw_stop_iteration();
    return entry->key;
}
