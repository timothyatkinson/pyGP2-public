default: $(OBJECTS)
	python3 GP2_lib_setup.py build_ext --inplace
	python3 parser_setup.py
	rm -r -f build GP2_lib_wrapper.c

clean:
	rm -f -r GP2_lib_wrapper.c GP2_lib.cpython* parser.out parsetab.py build
	rm -r -f __pycache__
