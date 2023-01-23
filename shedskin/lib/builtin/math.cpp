/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */


/* int_ methods */

int_::int_(__ss_int i) {
    unit = i;
    __class__ = cl_int_;
}

str *int_::__repr__() {
    return __str(unit);
}

__ss_bool int_::__nonzero__() {
    return __mbool(unit);
}

/* float methods */

float_::float_(__ss_float f) {
    unit = f;
    __class__ = cl_float_;
}

str *float_::__repr__() {
    return __str(unit);
}

__ss_bool float_::__nonzero__() {
    return __mbool(unit);
}

