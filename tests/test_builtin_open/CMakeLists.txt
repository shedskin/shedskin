set(sys_modules
    os
    os.path
    stat
)
set(app_modules
)
add_shedskin_test("${sys_modules}" "${app_modules}")
