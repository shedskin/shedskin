/* file */

template<class U> void *file::writelines(U *iter) {
    __check_closed();
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN(e,iter,1,2,3)
        write(e);
    END_FOR
    return NULL;
}

