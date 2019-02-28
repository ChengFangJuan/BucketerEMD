from NeuralFicititiousSelfPlay.Leduc.env import Env

env = Env()

env.reset()

s,r,t,i = env.init_state(0)

action = 0
env.step(action, 0)

s, a, r, s2, t, i = env.get_new_state(0)

env.reset()