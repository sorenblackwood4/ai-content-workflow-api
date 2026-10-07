import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]))
from content.manifest import build
class T(unittest.TestCase):
 def test_order(self):self.assertEqual([x['kind'] for x in build('x')['steps']],['text','image','video'])
if __name__=='__main__':unittest.main()
