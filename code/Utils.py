
def notes_equal(a, b):
	return a % 12 == b % 12

def get_triad(pitch, type):
	triad = [pitch]
	if type == 0: # major
		triad.append(pitch + 4)
		triad.append(pitch + 7)
	elif type == 1: # minor
		triad.append(pitch + 3)
		triad.append(pitch + 7)
	elif type == 2: # augmented
		triad.append(pitch + 4)
		triad.append(pitch + 8)
	elif type == 3: # diminished
		triad.append(pitch + 3)
		triad.append(pitch + 6)

def note_in_set(pitch, set):
	for note in set:
		if notes_equal(pitch, note):
			return True
	return False

def geometric_mean(set):
	prod = 1
	for item in set:
		prod *= item
	return prod ** (1 / float(len(set)))
