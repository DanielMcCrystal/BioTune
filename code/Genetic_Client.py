from .Grid import Grid
import code.Utils as utils

class Genetic_Client:
	# Start with an initial population of variable size
	def __init__(self, population_size):
		self.generation = 1

		pass

	# Determine the fitness of a particular chord specimen
	def chord_fitness(self, specimen):
		grid = specimen
		fitness = 1

		col_chords = [None * grid.num_notes]

		# Tier 1 (Individual Columns)
		last_chord = None
		tier_1_scores = []
		for col in range(grid.num_notes):
			# generate list of notes in chord
			notes_in_col = []
			for i in range(grid.note_range):
				if grid[col][i] is not None:
					notes_in_col.append(i)
			if len(notes_in_col == 0):
				continue
			lowest_note = notes_in_col[0]

			# generate possible chords for the column
			possible_chords = [utils.get_triad(lowest_note, type) for type in range(4)]
			if last_chord is not None and last_chord not in possible_chords:
				possible_chords.append(last_chord)

			# find the ratio of notes in each chord
			ratios = [None * len(possible_chords)]
			for chord in range(len(possible_chords)):
				count = 0
				for note in notes_in_col:
					if utils.note_in_set(note, possible_chords[chord]):
						count += 1
				ratios[chord] = count / len(notes_in_col)
			best_ratio = max(ratios)
			tier_1_scores.append(best_ratio)
			best_chord = possible_chords[ratios.index(best_ratio)]
			col_chords[col] = best_chord
			last_chord = best_chord
		multiplier = utils.geometric_mean(tier_1_scores) * 2
		fitness *= multiplier

		return fitness

	# Calculate fitness of each specimen in the population
	# Print top fitness, average fitness
	# Kill bottom 50%
	# Repopulate with offspring of top 50%
	def darwin(self):
		print("Simulated gen " + str(self.generation))
		self.generation = self.generation + 1
		pass

	# Generate an offspring of a particular specimen with random mutations
	def offspring(self, specimen):
		pass


if __name__ == '__main__':
	gc = Genetic_Client(1000)
	inpt = input("How many generations should I simulate? ")
	while(inpt != "done"):
		for i in range(int(inpt)):
			gc.darwin()
		inpt = input("How many generations should I simulate? ")
