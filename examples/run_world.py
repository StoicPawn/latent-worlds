from latent_worlds.metrics import snapshot
from latent_worlds.world import World

world = World(seed=7)
for _ in range(500):
    world.step()

print(snapshot(world))
print("Ground truth (researcher only):", world.yield_law)
