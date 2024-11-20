/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

/* Exceptions */

OSError::OSError(str *fname) {
    this->filename = fname;
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

FileNotFoundError::FileNotFoundError(str *fname) {
    this->filename = fname;
    this->__class__ = cl_filenotfounderror;
    __ss_errno = errno;
    message = new str("");
    strerror = new str(::strerror(__ss_errno));
}
str *FileNotFoundError::__str__() {
    return __add_strs(7, new str("[Errno "), __str(__ss_errno), new str("] "), strerror, new str(": '"), filename, new str("'"));
}
str *FileNotFoundError::__repr__() {
    return __add_strs(5, new str("FileNotFoundError("), __str(__ss_errno), new str(", '"), strerror, new str("')"));
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

BaseException::BaseException(str *msg) {
    __init__(msg);

    this->__class__ = cl_baseexception;
    this->args = new tuple<str *>(1, msg);
}

str *BaseException::__str__() {
    return args->__getitem__(0);
}

str *BaseException::__repr__() {
    return __add_strs(4, this->__class__->__name__, new str("('"), args->__getitem__(0), new str("')"));
}
