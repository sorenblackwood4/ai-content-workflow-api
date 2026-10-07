import argparse,csv,json,pathlib
def build(topic,folder='output'):
 return {'topic':topic,'steps':[{'kind':'text','model':'gpt-5.4'},{'kind':'image','model':'gpt-image-2'},{'kind':'video','model':'seedance-2.5'}],'folder':folder}
def write_csv(path,rows):
 with open(path,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['kind','model','status']);w.writeheader();w.writerows(rows)
def main():
 p=argparse.ArgumentParser();p.add_argument('topic');p.add_argument('--out',default='manifest.json');a=p.parse_args();pathlib.Path(a.out).write_text(json.dumps(build(a.topic),indent=2))
if __name__=='__main__':main()
