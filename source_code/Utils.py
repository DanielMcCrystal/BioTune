import math

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
	return triad

def note_in_set(pitch, set):
	if set is None:
		return False
	for note in set:
		if notes_equal(pitch, note):
			return True
	return False

def geometric_mean(set):
	prod = 1
	for item in set:
		prod *= item
	return prod ** (1 / float(len(set)))

def compact_chord_cols(chords):
	compact = []
	last = None
	count = 0
	for chord in chords:
		count += 1
		if not chord == last:
			if last is not None:
				compact.append([last, count])
			last = chord
			count = 0
	count += 1
	compact.append([last, count])
	return compact

def norm_pdf(x, mean, sd):
	var = float(sd) ** 2
	denom = math.sqrt(2 * math.pi * var)
	num = math.exp(-(float(x) - float(mean)) ** 2 / (2 * var))
	return num / denom