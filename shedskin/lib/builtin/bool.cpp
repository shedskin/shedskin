/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

/* bool methods */

bool_::bool_(__ss_bool i) {
    unit = i;
    __class__ = cl_bool;
}

str *bool_::__repr__() {
    if(unit.value)
        return new str("True");
    return new str("False");
}

__ss_bool bool_::__nonzero__() {
    return unit;
}

__ss_int bool_::__index__() {
    return unit.value;
}
