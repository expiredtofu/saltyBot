import h5py

class Fighter:
        def __init__(self, name, rank):
                self.name = name
                self.rank = rank
        def __repr__(self):
                return repr((self.name, self.rank))

fighters = []
f = h5py.File('main.hdf5')

for i in f.keys():
	if 'Dataset' not in str(f[i].__class__):
		del(f[i])
		print i, 'deleted'
	else:
		try:
			fighters += [Fighter(i, int(f[i].value))]
		except:
			print i, 'deleted'
			del(f[i])

f.close()
sortedFighters = sorted(fighters, key=lambda fighter: fighter.rank, reverse=True)

with open('rankings.txt','w') as fout:
	for fighter in sortedFighters:
		fout.write(str(fighter) + "\n")