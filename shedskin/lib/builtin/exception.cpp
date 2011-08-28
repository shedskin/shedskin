/* Copyright 2005-2011 Mark Dufour and contributors; License MIT (See LICENSE) */

/* Exceptions */

OSError::OSError(str *filename) {
    this->filename = filename;
    this->__class__ = cl_oserror;
    __ss_errno = errno;
    message = new str("");
    strerror = new str(::strerror(__ss_errno));
}
str *OSError::__str__() {
    return __add_strs(7, new str("[Errno "), __str(__ss_errno), new str("] "), strerror, new str(": '"), filename, new str("'"));
}
str *OSError::__repr__() {
    return __add_strs(5, new str("OSError("), __str(__ss_errno), new str(", '"), strerror, new str("')"));
}

IOError::IOError(str *filename) {
    this->filename = filename;
    this->__class__ = cl_ioerror;
    __ss_errno = errno;
    message = new str("");
    strerror = new str(::strerror(__ss_errno));
}
str *IOError::__str__() {
    return __add_strs(7, new str("[Errno "), __str(__ss_errno), new str("] "), strerror, new str(": '"), filename, new str("'"));
}
str *IOError::__repr__() {
    return __add_strs(5, new str("IOError("), __str(__ss_errno), new str(", '"), strerror, new str("')"));
}

void __throw_index_out_of_range() {
    throw new IndexError(new str("index out of range"));
}
void __throw_range_step_zero() {
    throw new ValueError(new str("range() step argument must not be zero"));
}
void __throw_set_changed() {
    throw new RuntimeError(new str("set changed size during iteration"));
}
void __throw_dict_changed() {
    throw new RuntimeError(new str("dict changed size during iteration"));
}
void __throw_slice_step_zero() {
    throw new ValueError(new str("slice step cannot be zero"));
}
void __throw_stop_iteration() {
    throw new StopIteration();
}
