set(modules
    random
    math
    time
    sys
)

set(app_modules
    box_bc
    coulomb
    fermion
    qmc_loop
    sum_jastrow
    wave_func
    jastrow/__init__
    jastrow/base_jastrow
    jastrow/const_jastrow
    jastrow/simple_pade
    observables/__init__
    observables/ee_dist
    observables/en_dist
    observables/observable_base
    orbital/__init__
    orbital/atomic_sto
    orbital/atomic_sto_primitive
    orbital/create_orbital
    orbital/lcao
    orbital/orbital_base
    stats/__init__
    stats/average
    stats/histogram
)

add_shedskin_example("${modules}" "${app_modules}")
