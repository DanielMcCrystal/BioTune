import random
import source_code.Utils as utils
from source_code.Grid import Grid
#import matplotlib.pyplot as plt

class Genetic_Client:
	# Start with an initial population of variable size
	def __init__(self, population_size):
		self.generation = 0
		self.population = [[None for i in range(2)] for j in range(population_size)]
		self.tops = []
		for i in range(population_size):
			grid = Grid(24)
			grid.populate_random()
			self.population[i][0] = grid
			self.population[i][1] = self.fitness(grid)

	# Determine the fitness of a particular chord specimen
	def fitness(self, specimen):
		grid = specimen.grid
		fitness = 1.0

		col_chords = [None] * specimen.num_notes

		# Tier 1 setup
		last_chord = None
		scores1 = []

		# Tier 3 setup
		expected = 4
		sd = 1
		max_score = utils.norm_pdf(expected, expected, sd)
		scores3 = []

		# Tiers 1 and 3
		for col in range(specimen.num_notes):
			# generate list of notes in chord
			notes_in_col = []
			for i in range(specimen.note_range):
				if grid[col][i] is not None:
					notes_in_col.append(i)
			if len(notes_in_col) == 0:
				continue
			lowest_note = notes_in_col[0]

			# generate possible chords for the column
			possible_chords = [utils.get_triad(lowest_note, type) for type in range(3)]
			if last_chord is not None and last_chord not in possible_chords:
				possible_chords.append(last_chord)

			# find the ratio of notes in each chord
			ratios = [None] * len(possible_chords)
			for chord in range(len(possible_chords)):
				count = 0
				for note in notes_in_col:
					if utils.note_in_set(note, possible_chords[chord]):
						count += 1
				ratios[chord] = float(count) / len(notes_in_col)
			best_ratio = max(ratios)
			scores1.append(best_ratio)
			best_chord = possible_chords[ratios.index(best_ratio)]
			col_chords[col] = best_chord
			last_chord = best_chord

			# Do Tier 3 stuff
			count = len(notes_in_col)
			scores3.append(utils.norm_pdf(count, expected, sd))

		multiplier1 = (utils.geometric_mean(scores1) * 2) ** 4
		fitness *= multiplier1
		multiplier3 = utils.geometric_mean(scores3) * 2
		fitness *= multiplier3

		# Tier 2 (Chord Changing)
		chord_sequence = utils.compact_chord_cols(col_chords)
		scores2 = [None] * len(chord_sequence)
		expected = 8
		sd = 4
		max_score = utils.norm_pdf(expected, expected, sd)
		for i in range(len(chord_sequence)):
			chord = chord_sequence[i]
			scores2[i] = utils.norm_pdf(chord[1], expected, sd) / max_score

		multiplier2 = utils.geometric_mean(scores2) * 2
		fitness *= multiplier2

		# Tier 4 (Key)
		keys = [None] * 24
		for i in range(12):
			keys[i] = utils.chords_in_key(i, 0)
			keys[i + 12] = utils.chords_in_key(i, 1)
		max_count = 0
		for key in keys:
			count = 0
			for chord in chord_sequence:
				if utils.is_chord_in_key(chord[0], key):
					count += 1
			if count > max_count:
				max_count = count
		ratio = max_count / len(chord_sequence)
		multiplier = ratio * 2
		fitness *= multiplier

		return fitness

	# Calculate fitness of each specimen in the population
	# Print top fitness, average fitness
	# Kill bottom 50%
	# Repopulate with offspring of top 50%
	def darwin(self):
		self.population = sorted(self.population, key=lambda x: x[1])
		#print("Top fitness: " + str(self.population[len(self.population)-1][1]))
		#self.tops[self.generation] = self.best_fitness()
		#avg = self.avg_fitness()
		#print("Average fitness: " + str(avg))
		survivors = range(int(len(self.population) / 2), len(self.population))
		deaths = range(int(len(self.population) / 2))
		offsprings = [self.offspring(self.population[i][0]) for i in survivors]
		for i in deaths:
			self.population[i] = [offsprings[i], self.fitness(offsprings[i])]
		print("Simulated gen " + str(self.generation))
		self.generation = self.generation + 1

	def avg_fitness(self):
		sum = 0
		for individual in self.population:
			sum += individual[1]
		return sum / len(self.population)

	def best_fitness(self):
		return self.population[len(self.population) - 1][1]

	def best_individual(self):
		return self.population[len(self.population)-1][0]

	# Generate an offspring of a particular specimen with random mutations
	def offspring(self, specimen):
		grid = specimen.grid
		offspring = specimen.copy()
		n = random.randint(1, specimen.note_count)
		track = 0
		done = False
		for pos in range(specimen.num_notes):
			for pitch  in range(specimen.note_range):
				if grid[pos][pitch]:
					track += 1
					if track == n:
						pos_movement = random.randint(-3, 3)
						if pos + pos_movement < 0 or pos + pos_movement >= specimen.num_notes:
							pos_movement = 0
						pitch_movement = random.randint(-5, 5)
						if pitch + pitch_movement < 0 or pitch + pitch_movement >= specimen.note_range:
							pitch_movement = 0
						new_duration = random.randint(1, 8)
						if pos + pos_movement + new_duration >= specimen.num_notes - 1:
							new_duration = 1
						offspring.remove_note(pos, pitch)
						offspring.add_note(pos + pos_movement, pitch + pitch_movement, new_duration)
						done = True
						break
			if done:
				break

		return offspring


if __name__ == '__main__':
	gc = Genetic_Client(200)
	gc.population[0][0].convert_to_MIDI("../outputs/start.mid")
	#inpt = input("How many generations should I simulate? ")
	while(gc.best_fitness() < 10.0):
		#gc.tops += [None] * int(inpt)
		gc.darwin()
		#for i in range(int(inpt)):
		#	gc.darwin()
		#inpt = input("How many generations should I simulate? ")
	print("Fitness: " + str(gc.best_fitness()))
	gc.best_individual().convert_to_MIDI("../outputs/best.mid")
	#plt.plot(gc.tops)
	#plt.show()