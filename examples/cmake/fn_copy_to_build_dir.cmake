
function(copy_to_build_dir)

	get_filename_component(name ${CMAKE_CURRENT_SOURCE_DIR} NAME_WLE)

	set(BUILD_DIR ${PROJECT_BINARY_DIR}/${name})

	foreach(fname ${ARGV})
	    file(COPY ${fname} DESTINATION ${BUILD_DIR})
	endforeach()

	# add_custom_command(
    #     OUTPUT ${name}-copied.txt
    #     POST_BUILD
    #     COMMAND ${CMAKE_COMMAND}
    #     ARGS    -E copy_if_different "${ARGV}" "${BUILD_DIR}"
    #     COMMENT "copy files to build dir"
    # )

endfunction()