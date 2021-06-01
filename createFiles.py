
import os

# root where the files will be created
fileRoot = 'sequenceFileSelector/'

# make the directory if it doesn't exist
try:
	os.makedirs(fileRoot)
except Exception as err:
	# raise the error only if the directory doesn't exist
	if not os.path.isdir(fileRoot):
		raise err

# filenames
files = {
	'taco.%04d.jpg': 5,
	'tuesday.%02d.jpg': 2,
	'reel.mov': 1,
	'box.mb': 1,
	'box2.mb': 1,
	'box3.mb': 1,
	'comp_v001.mb': 1,
	'comp_v002.mb': 1,
	'comp_v003.mb': 1,
	'split.001.jpg': 1,
	'split.003.jpg': 1,
	'split.004.jpg': 1,
	'underOverTen.0009.png': 1,
	'underOverTen.0010.png': 1,
	'underOverTen.0011.png':1,
	'underOverTen.0012.png':1,
	'long.file.name.%04d.pdf': 4,
	'another.one.%01d.jpg': 3,
}

# make the files
for name, count in files.iteritems():
	if count == 1:
		open(fileRoot + name, 'w+')
	else:
		for i in range(1, count+1):
			open(fileRoot + name % i, 'w+')
