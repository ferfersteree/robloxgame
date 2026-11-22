# label the raw biome photo: python shot.py NN   (system Python 3.13 with Pillow)
import sys, os, json
import post_photo
nn = int(sys.argv[1])
here = os.path.dirname(os.path.abspath(__file__))
ro = json.load(open(os.path.join(here, '..', 'roster.json'), encoding='utf-8'))['biomes'][str(nn)]
tmp = os.environ.get('TEMP')
out = os.path.join(here, '..', 'shots', 'biome_%02d_%s.png' % (nn, ro['key']))
post_photo.label(os.path.join(tmp, 'biome%02d_raw.png' % nn), os.path.join(tmp, 'biome%02d_labels.json' % nn), out,
                 'Biome %02d - %s' % (nn, ro['name']))
print(out)
