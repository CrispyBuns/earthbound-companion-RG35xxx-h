# SPDX-License-Identifier: GPL-3.0-or-later
"""Stage code-only Python support for on-device ROM setup. No ROM is needed."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import urllib.request
import zipfile

def copy_tree(source, target, exclude=()):
    for path in source.rglob('*'):
        relative = path.relative_to(source)
        if any(part in exclude for part in relative.parts) or path.suffix in ('.pyc', '.pyd', '.so'):
            continue
        if path.is_file():
            out = target/relative
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, out)

def clone(url, revision, output):
    if not output.exists():
        subprocess.run(['git', 'clone', '--no-checkout', url, str(output)], check=True)
        subprocess.run(['git', '-C', str(output), 'checkout', '--detach', revision], check=True)
    head = subprocess.check_output(['git', '-C', str(output), 'rev-parse', 'HEAD'], text=True).strip()
    if head != revision:
        raise ValueError('Android setup tool revision differs: '+str(output))

def stage(native, work, output):
    repo = Path(__file__).resolve().parents[1]
    output.mkdir(parents=True, exist_ok=True)
    copy_tree(native/'ebtools', output/'ebtools', ('__pycache__',))
    # The embedded entry calls converter functions, not the desktop command
    # registry. Importing cli must not initialize or parse a command-line app.
    (output/'ebtools/cli/__init__.py').write_text('# Embedded converter functions; no CLI registration.\n', encoding='utf-8')
    for file in (output/'ebtools').rglob('*.py'):
        source = file.read_text(encoding='utf-8')
        if 'from pydantic import' in source:
            file.write_text(source.replace('from pydantic import', 'from android_models import'), encoding='utf-8')
    support = output/'support'
    copy_tree(native/'src/custom_assets', support/'custom_assets', ('__pycache__',))
    for relative in ('earthbound.yml', 'commondefs.yml', 'src/data/event_script_data.h',
                     'src/data/text_refs.h', 'src/data/runtime_generated/asset_ids.h', 'src/include/constants.h'):
        destination = support/'native-source'/relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(native/relative, destination)
    for folder in ('src/game', 'src/entity', 'src/intro'):
        for path in (native/folder).glob('*.c'):
            destination = support/'native-source'/folder/path.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
    for name in ('maternalbound-native-bridge.json', 'redux-module-order.txt'):
        destination = support/'research'/name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo/'research'/name, destination)
    scripts = ['build_redux_profile.py', 'redux_setup_entry.py', 'redux_compile_order.py',
               'build_maternalbound_pack.py', 'apply_rom_patch.py', 'apply_bps.py', 'audit_redux_movement.py']
    scripts += [p.name for p in (repo/'scripts').glob('maternalbound_*.py')]
    for name in scripts:
        shutil.copy2(repo/'scripts'/name, output/name)
    tools = work/'tools'
    tools.mkdir(parents=True, exist_ok=True)
    cs, ccc, writer = tools/'CoilSnake', tools/'CCScript', tools/'CCScriptWriter'
    clone('https://github.com/pk-hack/CoilSnake.git', '346cfc753644bc3703b6fc4eaa0a5d6bdcb9bb4a', cs)
    clone('https://github.com/charasyn/ccscript_legacy.git', 'cecd6a44baf88f3e6de86938b4052502b4c53366', ccc)
    clone('https://github.com/pk-hack/CCScriptWriter.git', 'f7e290a68f99511b96dbc704eda6b21edc161faa', writer)
    for name in ('ccscript-cxx17.patch', 'ccscript-module-order.patch'):
        patch = str(repo/'patches'/name)
        reverse = subprocess.run(['git', '-C', str(ccc), 'apply', '--ignore-space-change', '--reverse', '--check', patch], capture_output=True)
        if reverse.returncode:
            subprocess.run(['git', '-C', str(ccc), 'apply', '--ignore-space-change', patch], check=True)
    copy_tree(cs/'coilsnake', output/'coilsnake', ('__pycache__', 'bin', 'images'))
    for file in (output/'coilsnake').rglob('*.py'):
        source = file.read_text(encoding='utf-8')
        rewritten = source.replace('coilsnake.util.eb.native_comp', 'eb_native_comp')
        rewritten = rewritten.replace('from coilsnake.util.eb import native_comp', 'import eb_native_comp as native_comp')
        if rewritten != source:
            file.write_text(rewritten, encoding='utf-8')
    copy_tree(writer/'CCScriptWriter', output/'CCScriptWriter', ('__pycache__',))
    for name, version in [('CCScriptWriter', '1.3'), ('coilsnake', '0.1.dev1+g346cfc753')]:
        info = output/f'{name}-{version}.dist-info'
        info.mkdir(exist_ok=True)
        (info/'METADATA').write_text(f'Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n', encoding='utf-8')
    # V2's v1 compatibility package is pure Python and needs no Rust/Cython
    # runtime. Download only the official, checksum-pinned Python wheel.
    metadata = json.load(urllib.request.urlopen('https://pypi.org/pypi/pydantic/2.13.5/json'))
    wheel = next(v for v in metadata['urls'] if v['filename'].endswith('py3-none-any.whl'))
    archive = work/wheel['filename']
    if not archive.exists():
        urllib.request.urlretrieve(wheel['url'], archive)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != '346a034f080da3755d8e9cb5e00e8b07de1d39e4f6e2c87d8ab7cafa0b269a73':
        raise ValueError('Pydantic source checksum differs')
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            if name.startswith('pydantic/v1/') and name.endswith('.py'):
                destination = output/name
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(z.read(name))
        license_name = next(n for n in z.namelist() if n.endswith('/licenses/LICENSE'))
        license_dir = support/'Licenses'
        license_dir.mkdir(parents=True, exist_ok=True)
        (license_dir/'Pydantic-LICENSE.txt').write_bytes(z.read(license_name))
    shutil.copy2(cs/'LICENSE', license_dir/'CoilSnake-LICENSE.txt')
    shutil.copy2(cs/'coilsnake/util/eb/exhal/COPYING.txt', license_dir/'Exhal-COPYING.txt')
    shutil.copy2(ccc/'src/filesystem/LICENSE', license_dir/'CCScript-filesystem-LICENSE.txt')
    shutil.copy2(writer/'pyproject.toml', license_dir/'CCScriptWriter-package-metadata.toml')
    (license_dir/'Tools-UPSTREAM.txt').write_text(
        'CoilSnake 346cfc753644bc3703b6fc4eaa0a5d6bdcb9bb4a https://github.com/pk-hack/CoilSnake\n'
        'CCScript cecd6a44baf88f3e6de86938b4052502b4c53366 https://github.com/charasyn/ccscript_legacy\n'
        'CCScriptWriter f7e290a68f99511b96dbc704eda6b21edc161faa https://github.com/pk-hack/CCScriptWriter\n'
        'Pinned CCScript/CCScriptWriter have no standalone license declaration; retain provenance without inventing one.\n', encoding='utf-8')
    (output/'pydantic/__init__.py').write_text('from .v1 import *\n', encoding='utf-8')
    return cs, ccc

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', type=Path, required=True)
    parser.add_argument('--work', type=Path, default=Path('build/android-setup'))
    args = parser.parse_args()
    stage(args.native.resolve(), args.work.resolve(), args.work.resolve()/'python')
