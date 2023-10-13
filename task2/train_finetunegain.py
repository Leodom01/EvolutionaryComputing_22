import os
import cma
import multiprocessing
import numpy as np
from functools import partial
from environment import training_environment
from scipy.spatial.distance import pdist

# BEGIN META PARAMETERS
# ENEMIES = [1, 3, 4, 6, 7]
ENEMIES = range(1, 9)
NGEN = 300
RUN_NUMBER = 5
# END META PARAMETERS

# BEGIN HYPER PARAMETERS
INITIAL_SIGMA = 0.05
NPOP = 100
# END HYPER PARAMETERS

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

neuron_number, env = training_environment(ENEMIES)

def evaluate(phenone):

  def run_single(enemy):
    f, p, e, t = env.run_single(pcont=phenone, enemyn=enemy, econt=None)
    return f, p, e, t

  fitnesses = []
  kills = 0
  deaths = 0
  time = 0
  gain = []
  phealth = 0
  for (f, p, e, t) in map(run_single, ENEMIES):
    fitnesses.append(f)
    phealth += p
    gain.append(p - e)
    if e == 0: kills += 1
    if p == 0: deaths += 1
    if p != 0 and e != 0: time += t

  classic_fitness = np.average(fitnesses) - np.std(fitnesses)
  f = np.sum(gain)
  return -f, np.sum(gain), kills

def main():
  # init = [0] * neuron_number

  for run_number in range(RUN_NUMBER):

    init = np.loadtxt("./tmp-agent.txt")

    engine = cma.CMAEvolutionStrategy(
      init,
      INITIAL_SIGMA,
      {
        "popsize": NPOP,
      }
    )

    try:
      cpus = multiprocessing.cpu_count()
    except NotImplementedError:
      cpus = 1

    print("Running on ", cpus, " processors!")

    pool = multiprocessing.Pool(processes=cpus)

    # for i in range(NGEN):
    i = 0
    while i < NGEN:
      solutions = engine.ask()
      eval = list(zip(*pool.map(evaluate, solutions)))
      fitness, gain, kills = eval[0], eval[1], eval[2]
      engine.tell(solutions, fitness)

      current_best_fitness = - np.min(fitness)
      average_fitness = - np.average(fitness)
      global_best = - engine.result[1]


      print(
        f"Generation {i}\t"
        f"max fitness: {current_best_fitness}\t"
        f"Gain value: {gain[fitness.index(- current_best_fitness)]}\t"
        f"Amount of kills: {kills[fitness.index(- current_best_fitness)]}\t"
        f"average fitness: {average_fitness}\t"
        f"best of all time: {global_best}"
      )

      if current_best_fitness >= global_best:
        np.savetxt(f"tmp-agent.txt", engine.result[0])
        print("New agent saved in tmp-agent.txt")
        best_agent = engine.result[0]

      i += 1

    np.savetxt(f"agent--fit-{engine.result[1]}.txt", engine.result[0])
    pool.close()
    # np.savetxt(f"agent-custom-fitness-fit-{engine.result[1]}.txt", engine.result[0])
    # np.savetxt(f"agent-custom-enemies-fit-{engine.result[1]}.txt", engine.result[0])
    print("Completed run number: ", run_number)

  print("Agent saved in lars-best.txt")
  np.savetxt(f"lars-best8.txt", best_agent)


if __name__ == "__main__":
  multiprocessing.freeze_support()
  main()
