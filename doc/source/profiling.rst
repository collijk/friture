Some details about profiling possibilities
==========================================

First option (cProfile and gprof2dot)
-------------------------------------

python -m cProfile -o output.pstats ./friture.py
scripts/gprof2dot.py -f pstats output.pstats -n 0.1 -e 0.02| dot -Tpng -o output2.png

Second option (cProfile and pstats)
-----------------------------------

./friture.py --python

Third option (cProfile, convert to kcachegrind)
-----------------------------------------------

python scripts/lsprofcalltree.py friture.py
kcachegrind

Fourth option (sysprof system-wide profiler on Linux)
-----------------------------------------------------

	For sysprof, either use "sudo m-a a-i sysprof-module" to build the module for your current kernel,
	on Debian-like distributions, or use a development version of sysprof (>=1.11) and a recent
	kernel (>=2.6.31) that has built-in support, with in-kernel tracing as an addition.

sysprof
./gprof2dot.py -f sysprof sysprof_profile_kernel| dot -Tpng -o output_sysprof_kernel.png

TODO : write a converter from sysprof to callgrind (similar to lsprofcalltree)