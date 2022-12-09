/* Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE) */

/* 
dict implementation, partially derived from CPython,
copyright Python Software Foundation (http://www.python.org/download/releases/2.6.2/license/)
*/

#define INIT_NONZERO_SET_SLOTS(so) do {				\
	(so)->table = (so)->smalltable;				\
	(so)->mask = MINSIZE - 1;				\
    } while(0)


#define EMPTY_TO_MINSIZE(so) do {				\
	memset((so)->smalltable, 0, sizeof((so)->smalltable));	\
	(so)->used = (so)->fill = 0;				\
	INIT_NONZERO_SET_SLOTS(so);				\
    } while(0)

template <class T> void *myallocate(int n) { return GC_MALLOC(n); }
template <> void *myallocate<__ss_int>(int n);

template <class K, class V> void *myallocate(int n) { return GC_MALLOC(n); }
template <> void *myallocate<__ss_int, __ss_int>(int n);

template<class K, class V> dict<K,V>::dict() {
    this->__class__ = cl_dict;
    EMPTY_TO_MINSIZE(this);
}

template<class K, class V> dict<K, V>::dict(int count, ...)  {
    this->__class__ = cl_dict;
    EMPTY_TO_MINSIZE(this);
    va_list ap;
    va_start(ap, count);
    for(int i=0; i<count; i++) {
        typedef tuple2<K, V> * bert;
        bert t = va_arg(ap, bert);
        __setitem__(t->__getfirst__(), t->__getsecond__());
    }
    va_end(ap);
}

template<class K, class V, class U> static inline void __add_to_dict(dict<K, V> *d, U *iter) {
    __iter<typename U::for_in_unit> *it = ___iter(iter);
    typename U::for_in_unit a, b;
    a = it->__next__();
    b = it->__next__();
    d->__setitem__(a, b);
}

template<class K, class V> static inline void __add_to_dict(dict<K, V> *d, tuple2<K, V> *t) {
    d->__setitem__(t->__getfirst__(), t->__getsecond__());
}

template<class K, class V> template<class U> dict<K, V>::dict(U *other) {
    this->__class__ = cl_dict;
    EMPTY_TO_MINSIZE(this);
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN(e,other,1,2,3)
        __add_to_dict(this, e);
    END_FOR
}

template<class K, class V> dict<K, V>::dict(dict<K, V> *p)  {
    this->__class__ = cl_dict;
    EMPTY_TO_MINSIZE(this);

    *this = *p;
}

#ifdef __SS_BIND
template<class K, class V> dict<K, V>::dict(PyObject *p) {
    if(!PyDict_Check(p))
        throw new TypeError(new str("error in conversion to Shed Skin (dictionary expected)"));

    this->__class__ = cl_dict;
    EMPTY_TO_MINSIZE(this);
    PyObject *key, *value;

    PyObject *iter = PyObject_GetIter(p);
    while ((key = PyIter_Next(iter))) {
        value = PyDict_GetItem(p, key);
        __setitem__(__to_ss<K>(key), __to_ss<V>(value));
        Py_DECREF(key);
    }
    Py_DECREF(iter);
}

template<class K, class V> PyObject *dict<K, V>::__to_py__() {
   PyObject *p = PyDict_New();
   __ss_int pos = 0;
   dictentry<K,V> *entry;
   while(next(&pos, &entry)) {
       PyObject *pkey = __to_py(entry->key);
       PyObject *pvalue = __to_py(entry->value);
       PyDict_SetItem(p, pkey, pvalue);
       Py_DECREF(pkey);
       Py_DECREF(pvalue);
   }
   return p;
}
#endif

template <class K, class V> dict<K,V>& dict<K,V>::operator=(const dict<K,V>& other) {
    memcpy((void*)this, (void*)&other, sizeof(dict<K,V>));
    int table_size = sizeof(dictentry<K,V>) * (other.mask+1);
    table = (dictentry<K,V>*)myallocate<K,V>(table_size);
    memcpy(table, other.table, table_size);
    return *this;
}

template<class K, class V> __ss_bool dict<K,V>::__eq__(pyobj *p) { /* XXX check hash */
    dict<K,V> *b = (dict<K,V> *)p;
    if(b->__len__() != this->__len__())
        return False;
    __ss_int pos = 0;
    dictentry<K,V> *entry;
    while (next(&pos, &entry)) {
        dictentry<K, V> *entryb;
        entryb = b->lookup(entry->key, entry->hash);
        if (entryb->use != active)
            return False;
        if(!__eq(entry->value, entryb->value))
            return False;
    }
    return True;
}

template <class K, class V> int characterize(dict<K,V> *a, dict<K,V> *b, V *pval)
{
	int i;
	int difference_found = 0;
	K akey;
	V aval;
    akey = 0; aval = 0;
	int cmp;

	for (i = 0; i <= a->mask; i++) {
		dictentry<K, V> *entry;
		K thiskey;
		V thisaval, thisbval;
		if (a->table[i].use != active) continue;

		thiskey = a->table[i].key;
		if (difference_found) {
			cmp = __cmp(akey, thiskey);
			if (cmp < 0) continue;
		}

		thisaval = a->table[i].value;
		entry = b->lookup(thiskey, a->table[i].hash);

		if (entry->use != active) cmp = 1;
		else {
			thisbval = entry->value;
			cmp = __cmp(thisaval, thisbval);
		}

		if (cmp != 0) {
			difference_found = 1;
			akey = thiskey;
			aval = thisaval;
		}
	}

	*pval = aval;
	return difference_found;
}


template<class K, class V> __ss_bool dict<K,V>::__ge__(dict<K,V> *s) {
    return __mbool(__cmp__(s) >= 0);
}

template<class K, class V> __ss_bool dict<K,V>::__le__(dict<K,V> *s) {
    return __mbool(__cmp__(s) <= 0);
}

template<class K, class V> __ss_bool dict<K,V>::__lt__(dict<K,V> *s) {
    return __mbool(__cmp__(s) < 0);
}

template<class K, class V> __ss_bool dict<K,V>::__gt__(dict<K,V> *s) {
    return __mbool(__cmp__(s) > 0);
}

template<class K, class V> __ss_int dict<K,V>::__cmp__(pyobj *p) {
    dict<K,V> *s = (dict<K,V> *)p;
	int difference_found;
	V aval, bval;

    if (this->used < s->used) return -1;
    else if (this->used > s->used) return 1;

	difference_found = characterize(this, s, &aval);
	if (!difference_found) return 0;

	characterize(s, this, &bval);

	return __cmp(aval, bval);
}

template <class K, class V> dictentry<K,V>* dict<K,V>::lookup(K key, long hash) const {

    int i = hash & mask;
    dictentry<K,V>* entry = &table[i];
    if (!(entry->use) || __eq(entry->key, key))
        return entry;

    dictentry <K,V>* freeslot;

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

template <class K, class V> void dict<K,V>::insert_key(K key, V value, long hash) {
    dictentry<K,V>* entry;

    entry = lookup(key, hash);
    if (!(entry->use)) {
        fill++;
        entry->key = key;
        entry->value = value;
        entry->hash = hash;
        entry->use = active;
        used++;
    }
    else if (entry->use == dummy) {
        entry->key = key;
        entry->value = value;
        entry->hash = hash;
        entry->use = active;
        used++;
    }
    else {
		entry->value = value;
	}
}

template <class K, class V> void *dict<K,V>::__setitem__(K key, V value)
{
    long hash = hasher<K>(key);
    int n_used = used;

    insert_key(key, value, hash);
    if ((used > n_used && fill*3 >= (mask+1)*2))
        resize(used>50000 ? used*2 : used*4);
    return NULL;
}

template<class T> T __none() { return NULL; }
template<> int __none();
template<> double __none();

template <class K, class V> V dict<K,V>::__getitem__(K key) {
	long hash = hasher<K>(key);
	dictentry<K, V> *entry;

	entry = lookup(key, hash);

	if (entry->use != active)
		throw new KeyError(repr(key));
	
	return entry->value;
}

template<class K, class V> void *dict<K,V>::__addtoitem__(K key, V value) {
	long hash = hasher<K>(key);
	dictentry<K, V> *entry;

	entry = lookup(key, hash);
	if (entry->use != active)
		throw new KeyError(repr(key));

    entry->value = __add(entry->value, value);
    return NULL;
}

template <class K, class V> V dict<K,V>::get(K key) {
    long hash = hasher<K>(key);
	dictentry<K, V> *entry;

	entry = lookup(key, hash);
	if (entry->use != active)
        return __none<V>();
	
	return entry->value;
}

template <class K, class V> V dict<K,V>::get(K key, V d) {
    long hash = hasher<K>(key);
	dictentry<K, V> *entry;

	entry = lookup(key, hash);
	if (entry->use != active)
		return d;
	
	return entry->value;
}

template <class K, class V> V dict<K,V>::setdefault(K key, V value)
{
    long hash = hasher<K>(key);
	dictentry<K, V> *entry;

	entry = lookup(key, hash);

    if (entry->use != active)
		__setitem__(key, value);

	return entry->value;
}

template <class K, class V> void *dict<K,V>::__delitem__(K key) {
    if (!do_discard(key)) 
        throw new KeyError(repr(key));
    return NULL;
}

template <class K, class V> int dict<K,V>::do_discard(K key) {
	long hash = hasher<K>(key);
	dictentry<K,V> *entry;

	entry = lookup(key, hash);

	if (entry->use != active)
		return DISCARD_NOTFOUND; // nothing to discard

	entry->use = dummy;
	used--;
	return DISCARD_FOUND;
}

template<class K, class V> V dict<K,V>::pop(K key) {
	long hash = hasher<K>(key);
    dictentry<K,V> *entry;

    entry = lookup(key, hash);

	if (entry->use != active)
		throw new KeyError(__str(key));

	entry->use = dummy;
	used--;
	return entry->value;
}

template<class K, class V> tuple2<K,V> *dict<K,V>::popitem() {
    int i = 0;
	dictentry<K,V> *entry;

	if (used == 0)
		throw new KeyError(new str("popitem(): dictionary is empty"));

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
	return new tuple2<K,V>(2, entry->key, entry->value);
}

/*
 * Iterate over a dict table.  Use like so:
 *
 *     int pos;
 *     dictentry<K,V> *entry;
 *     pos = 0;   # important!  pos should not otherwise be changed by you
 *     while (dict_next(yourdict, &pos, &entry)) {
 *              Refer to borrowed reference in entry->key.
 *     }
 */
template <class K, class V> int dict<K,V>::next(__ss_int *pos_ptr, dictentry<K,V> **entry_ptr)
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
Internal routine used by dict_table_resize() to insert an item which is
known to be absent from the dict.  This routine also assumes that
the dict contains no deleted entries.  Besides the performance benefit,
using insert() in resize() is dangerous (SF bug #1456209).
*/
template <class K, class V> void dict<K,V>::insert_clean(K key, V value, long hash)
{
	int i;
	unsigned int perturb;
	dictentry<K,V> *entry;

	i = hash & mask;

	entry = &table[i];
	for (perturb = hash; entry->use; perturb >>= PERTURB_SHIFT) {
		i = (i << 2) + i + perturb + 1;
		entry = &table[i & mask];
	}
	fill++;
	entry->key = key;
	entry->value = value;
	entry->hash = hash;
	entry->use = active;
	used++;
}


/*
Restructure the table by allocating a new table and reinserting all
keys again.  When entries have been deleted, the new table may
actually be smaller than the old one.
*/
template <class K, class V> void dict<K,V>::resize(int minused)
{
	int newsize;
	dictentry<K,V> *oldtable, *newtable, *entry;
	int i;
	dictentry<K,V> small_copy[MINSIZE];

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
			   as dict_lookkey needs at least one virgin slot to
			   terminate failing searches.  If fill < size, it's
			   merely desirable, as dummies slow searches. */
			memcpy(small_copy, oldtable, sizeof(small_copy));
			oldtable = small_copy;
		}
	}
	else {
        newtable = (dictentry<K,V>*) myallocate<K,V>(sizeof(dictentry<K,V>) * newsize);
	}

	/* Make the dict empty, using the new table. */
	table = newtable;
	mask = newsize - 1;

	memset(newtable, 0, sizeof(dictentry<K,V>) * newsize);

    i = used;
    used = 0;
	fill = 0;

	/* Copy the data over;
	   dummy entries aren't copied over */
	for (entry = oldtable; i > 0; entry++) {
		if (entry->use == active) {
			/* ACTIVE */
			--i;
			insert_clean(entry->key, entry->value, entry->hash);
		}
	}
}

template<class K, class V> str *dict<K,V>::__repr__() {
    str *r = new str("{");
    dictentry<K,V> *entry;

    int i = __len__();
    __ss_int pos = 0;

    while (next(&pos, &entry)) {
		--i;
        *r += repr(entry->key)->c_str();
        *r += ": ";
        *r += repr(entry->value)->c_str();
        if( i > 0 )
            *r += ", ";
    }

    r = *r + "}";
    return r;
}

template<class K, class V> __ss_int dict<K,V>::__len__() {
    return used;
}

template <class K, class V> __ss_bool dict<K,V>::__contains__(K key) {
    long hash = hasher(key);
	dictentry<K,V> *entry;

	entry = lookup(key, hash);

	return __mbool(entry->use==active);
}

template <class K, class V> __ss_bool dict<K,V>::__contains__(dictentry<K,V>* entry) {
	entry = lookup(entry->key, entry->hash);

	return __mbool(entry->use == active);
}

template <class K, class V> __ss_bool dict<K,V>::has_key(K key) {
	return __contains__(key);
}

template <class K, class V> void *dict<K,V>::clear()
{
	dictentry<K,V> *entry, *table;
	int table_is_malloced;
	size_t fill;
	dictentry<K,V> small_copy[MINSIZE];

    table = this->table;
	table_is_malloced = table != smalltable;

	/* This is delicate.  During the process of clearing the dict,
	 * decrefs can cause the dict to mutate.  To avoid fatal confusion
	 * (voice of experience), we have to make the dict empty before
	 * clearing the slots, and never refer to anything via so->ref while
	 * clearing.
	 */
	fill = this->fill;
	if (table_is_malloced)
		EMPTY_TO_MINSIZE(this);

	else if (fill > 0) {
		/* It's a small table with something that needs to be cleared.
		 * Afraid the only safe way is to copy the dict entries into
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

template <class K, class V> void *dict<K,V>::update(dict<K,V>* other)
{
	int i;
	dictentry<K,V> *entry;

	/* Do one big resize at the start, rather than
	 * incrementally resizing as we insert new keys.  Expect
	 * that there will be no (or few) overlapping keys.
	 */
	if ((fill + other->used)*3 >= (mask+1)*2)
	   resize((used + other->used)*2);
	for (i = 0; i <= other->mask; i++) {
		entry = &other->table[i];
		if (entry->use == active) {
			insert_key(entry->key, entry->value, entry->hash);
		}
	}
    return NULL;
}

template <class K, class V> template<class U> void *dict<K,V>::update(U *iter) {
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN(e,iter,1,2,3)
		__setitem__(e->__getitem__(0), e->__getitem__(1));
    END_FOR
    return NULL;
}

template<class K, class V> dict<K,V> *dict<K,V>::copy() {
    dict<K,V> *c = new dict<K,V>;
    *c = *this;
    return c;
}

template<class K, class V> dict<K,V> *dict<K,V>::__copy__() {
    dict<K,V> *c = new dict<K,V>;
    *c = *this;
    return c;
}

template<class K, class V> dict<K,V> *dict<K,V>::__deepcopy__(dict<void *, pyobj *> *memo) {
    dict<K,V> *c = new dict<K,V>();
    memo->__setitem__(this, c);
    K e;
    typename dict<K,V>::for_in_loop __3;
    int __2;
    dict<K,V> *__1;
    FOR_IN(e,this,1,2,3)
        c->__setitem__(__deepcopy(e, memo), __deepcopy(this->__getitem__(e), memo));
    END_FOR
    return c;
}

/* dictiterkeys/values/items */

template<class K, class V> __dictiterkeys<K, V>::__dictiterkeys(dict<K,V> *p) {
    this->p = p;
    this->pos = 0;
    this->si_used = p->used;
}

template<class K, class V> K __dictiterkeys<K, V>::__next__() {
    if (si_used != p->used) {
        si_used = -1;
        __throw_dict_changed();
    }
    int ret = p->next(&pos, &entry);
    if (!ret) __throw_stop_iteration();
    return entry->key;
}

template<class K, class V> __dictitervalues<K, V>::__dictitervalues(dict<K,V> *p) {
    this->p = p;
    this->pos = 0;
    this->si_used = p->used;
}

template<class K, class V> V __dictitervalues<K, V>::__next__() {
    if (si_used != p->used) {
        si_used = -1;
        __throw_dict_changed();
    }
    int ret = p->next(&pos, &entry);
    if (!ret) __throw_stop_iteration();
    return entry->value;
}

template<class K, class V> __dictiteritems<K, V>::__dictiteritems(dict<K,V> *p) {
    this->p = p;
    this->pos = 0;
    this->si_used = p->used;
}

template<class K, class V> tuple2<K, V> *__dictiteritems<K, V>::__next__() {
    if (si_used != p->used) {
        si_used = -1;
        __throw_dict_changed();
    }
    int ret = p->next(&pos, &entry);
    if (!ret) __throw_stop_iteration();
    return new tuple2<K, V>(2, entry->key, entry->value);
}

/* dict.fromkeys */

namespace __dict__ {
    template<class A, class B> dict<A, B> *fromkeys(pyiter<A> *f, B b) {
        dict<A, B> *d = new dict<A, B>();
        typename pyiter<A>::for_in_unit e;
        typename pyiter<A>::for_in_loop __3;
        int __2;
        pyiter<A> *__1;
        FOR_IN(e,f,1,2,3)
            d->__setitem__(e, b);
        END_FOR
        return d;
    }

    template<class A> dict<A, void *> *fromkeys(pyiter<A> *f) {
        return fromkeys(f, (void *)0);
    }

}
