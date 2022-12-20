set(sys_modules
)

set(app_modules
	foo
	bar
	spam
)

add_shedskin_test("${sys_modules}" "${app_modules}")