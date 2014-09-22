#!/usr/bin/env python
import os, os.path, sys, shutil
import subprocess

from os.path import abspath, dirname, join, exists, isdir

# This will try to build the project (and launch it ?)

home_path = abspath(dirname(__file__))

global_conf = {
	'name':'sidestrategy',
}

# all paths are relative to home_path
conf = {
	'pyinstaller_main':'../PyInstaller-2.1/pyinstaller.py',
	'build_path':'build',
	'ressources': 'src',
	'main' : 'src/main.py',
	'spec': 'build/' + global_conf['name'] + '.spec',
}

conf = {k:abspath(join(home_path, *conf[k].split('/'))) for k in conf}

print(conf)


# build the path
if exists(conf['build_path']):
	shutil.rmtree(conf['build_path'])
os.mkdir(conf['build_path'])
os.chdir(conf['build_path'])

subprocess.check_call([
	'python', conf['pyinstaller_main'],
	'--name', global_conf['name'],
	conf['main']]
)


# modify the spec file

to_add_at_beginning = ("from kivy.tools.packaging.pyinstaller_hooks import install_hooks\n"
						+"install_hooks(globals())\n")

file_content = None
with open(conf['spec']) as spec:
	file_content = spec.readlines()

file_content[1:1] = to_add_at_beginning

for n, line in enumerate(list(file_content)):
	if 'hookspath=None,\n' in line:
		file_content[n] = '' # delete the line
	if 'COLLECT' in line and 'exe' in line:
		file_content[n] += "Tree('%s'),\n" % conf['ressources']


# clean everything
os.chdir('..')
shutil.rmtree(conf['build_path'])

os.mkdir(conf['build_path'])
os.chdir(conf['build_path'])

with open(conf['spec'], 'w') as spec:
	spec.write(''.join(file_content))

# build the specs

subprocess.check_call([
	'python', conf['pyinstaller_main'],
	conf['spec']
])






#python pyinstaller.py --name touchtracer ..\kivy\examples\demo\touchtracer\main.py





#__EOF__