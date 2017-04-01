# from Grid import Grid

class Genetic_Client:
	# Start with an initial population of variable size
	def __init__(self, population_size):
		self.generation = 1
		pass

	# Determine the fitness of a particular specimen
	def fitness(self, specimen):
		pass

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
