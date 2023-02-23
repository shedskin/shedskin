
# utility function to check if a string starts with a substring
function(string_starts_with str search result)
    string(FIND "${str}" "${search}" index)
    if("${index}" EQUAL 0)
        set(${result} TRUE PARENT_SCOPE)
    else()
        set(${result} FALSE PARENT_SCOPE)
    endif()
endfunction()


# join list with a specified seperator
#
# SET(somelist a b c)
# JOIN("${somelist}" ":" output)
# MESSAGE("${output}") # will output "a:b:c"
#
function(JOIN VALUES GLUE OUTPUT)
    string (REPLACE ";" "${GLUE}" _TMP_STR "${VALUES}")
    set (${OUTPUT} "${_TMP_STR}" PARENT_SCOPE)
endfunction()

