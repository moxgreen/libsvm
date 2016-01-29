#!/usr/bin/env python

import sys
import os
from subprocess import *
from optparse import OptionParser

usage = 'Usage: {0} training_file [testing_file]'.format(sys.argv[0])
parser = OptionParser(usage=usage)
parser.add_option('-v', '--verbose', dest='verbose', action='store_true', default=False, help='verbose [default: %default]')
parser.add_option('-d', '--nodisplay', dest='nodisplay', action='store_true', default=False, help='do non use the display to show the plot [default: %default]')
parser.add_option('-l', '--scale_low_limit', dest='scale_low_limit', type=int, default=-1, help='the value passed to -l in svm-scale [default: %default]')

options, args = parser.parse_args()

if len(args) == 0 or len(args) > 2:
	print('Usage: {0} training_file [testing_file]'.format(sys.argv[0]))
	raise SystemExit

# svm, grid, and gnuplot executable files

is_win32 = (sys.platform == 'win32')
if not is_win32:
	svmscale_exe = "svm-scale"
	svmtrain_exe = "svm-train"
	svmpredict_exe = "svm-predict"
	grid_py = "svm-grid"
	gnuplot_exe = "gnuplot"
else:
        # example for windows
	svmscale_exe = r"..\windows\svm-scale.exe"
	svmtrain_exe = r"..\windows\svm-train.exe"
	svmpredict_exe = r"..\windows\svm-predict.exe"
	gnuplot_exe = r"c:\tmp\gnuplot\binary\pgnuplot.exe"
	grid_py = r".\grid.py"

#assert os.path.exists(svmscale_exe),"svm-scale executable not found"
#assert os.path.exists(svmtrain_exe),"svm-train executable not found"
#assert os.path.exists(svmpredict_exe),"svm-predict executable not found"
#assert os.path.exists(gnuplot_exe),"gnuplot executable not found"
#assert os.path.exists(grid_py),"grid.py not found"

train_pathname = args[0]
assert os.path.exists(train_pathname),"training file not found"
file_name = os.path.split(train_pathname)[1]
scaled_file = file_name + ".scale"
model_file = file_name + ".model"
range_file = file_name + ".range"

if len(args) > 2:
	test_pathname = args[2]
	file_name = os.path.split(test_pathname)[1]
	assert os.path.exists(test_pathname),"testing file not found"
	scaled_test_file = file_name + ".scale"
	predict_test_file = file_name + ".predict"

cmd = '{0} -l {1} -s "{2}" "{3}" > "{4}"'.format(svmscale_exe, options.scale_low_limit, range_file, train_pathname, scaled_file)
if options.verbose:
    print('Scaling training data...')
Popen(cmd, shell = True, stdout = PIPE).communicate()	

gnuplot =  gnuplot_exe
if options.nodisplay:
    gnuplot = "null"
cmd = '{0} -svmtrain "{1}" -gnuplot "{2}" "{3}"'.format(grid_py, svmtrain_exe, gnuplot, scaled_file)
if options.verbose:
    print('Cross validation...')
f = Popen(cmd, shell = True, stdout = PIPE).stdout

line = ''
while True:
	last_line = line
	line = f.readline()
	if not line: break
c,g,rate = map(float,last_line.split())

print('Best c={0}, g={1} CV rate={2}'.format(c,g,rate))

cmd = '{0} -b 1 -c {1} -g {2} "{3}" "{4}"'.format(svmtrain_exe,c,g,scaled_file,model_file)
if options.verbose:
    print('Training...')
Popen(cmd, shell = True, stdout = PIPE).communicate()

if options.verbose:
    print('Output model: {0}'.format(model_file))
if len(sys.argv) > 2:
	cmd = '{0} -r "{1}" "{2}" > "{3}"'.format(svmscale_exe, range_file, test_pathname, scaled_test_file)
        if options.verbose:
            print('Scaling testing data...')
	Popen(cmd, shell = True, stdout = PIPE).communicate()	

	cmd = '{0} -b 1 "{1}" "{2}" "{3}"'.format(svmpredict_exe, scaled_test_file, model_file, predict_test_file)
        if options.verbose:
            print('Testing...')
	Popen(cmd, shell = True).communicate()	

        if options.verbose:
            print('Output prediction: {0}'.format(predict_test_file))
