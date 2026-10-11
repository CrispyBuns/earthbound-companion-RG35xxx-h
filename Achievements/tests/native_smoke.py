"""Focused achievement checks. Uses only new, explicitly chosen private sessions."""
from pathlib import Path
import argparse, subprocess, os, json, hashlib

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--game',type=Path,required=True)
parser.add_argument('--original-pak',type=Path,required=True)
parser.add_argument('--redux-pak',type=Path)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
output=args.output.resolve()
if output.exists():parser.error('--output must be a new directory; existing profiles are never overwritten')
for source in [args.game,args.original_pak]+([args.redux_pak] if args.redux_pak else []):
 if not source.is_file():parser.error(f'Missing input: {source}')
output.mkdir(parents=True)
env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
packs={'original':args.original_pak.resolve()}
if args.redux_pak:packs['redux']=args.redux_pak.resolve()
def run(label,edition,extra,profile):
 session=output/label;session.mkdir()
 cmd=[str(args.game.resolve()),'--session-dir',str(session),'--assets',str(packs[edition]),'--headless','--frames','3','--achievements-dir',str(profile)]
 if edition=='redux':cmd+=['--allow-redux-development']
 result=subprocess.run(cmd+extra,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
 (session/'test.log').write_bytes(result.stdout)
 if result.returncode:raise RuntimeError(f'{label} failed ({result.returncode}); see its private test.log')
 return result.stdout.decode(errors='replace')
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for edition in packs:
 profile=output/(edition+'-progress')
 assert 'production hooks: PASS' in run(edition+'-hooks',edition,['--selftest-achievements'],profile)
 file=profile/f'earthbound-{edition}.json';records=json.loads(file.read_text())['achievements']
 assert len(records)==46 and all(item['unlockedAt']>0 for item in records)
 before=digest(file);text=run(edition+'-restart',edition,[],profile)
 assert digest(file)==before and 'Achievement unlocked:' not in text
 run(edition+'-shuffle',edition,['--selftest-achievements','--achievement-shuffle'],profile)
 assert (profile/f'earthbound-shuffle-{edition}.json').exists() and digest(file)==before
 print(f'PASS {edition}: production hooks, persistence, duplicate rejection, overlay bounds and shuffle isolation')
bad=output/'corrupt-progress';bad.mkdir();file=bad/'earthbound-original.json';file.write_text('{broken')
before=digest(file);text=run('corrupt','original',[],bad)
assert digest(file)==before and 'left untouched' in text
off=output/'disabled-progress';run('disabled','original',['--no-achievements'],off);assert not off.exists()
print('PASS corrupt profile preservation and tracking opt-out. Private fixtures:',output)
