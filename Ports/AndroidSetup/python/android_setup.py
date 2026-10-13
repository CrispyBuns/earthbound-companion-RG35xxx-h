# SPDX-License-Identifier: GPL-3.0-or-later
"""Private-ROM conversion inside Android's app process. Never downloads a ROM."""
import contextlib
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import traceback

USA = 'a8fe2226728002786d68c27ddddf0b90a894db52e4dfe268fdf72a68cae5f02e'

def selftest():
    import PIL.Image
    import yaml
    import eb_native_comp
    from coilsnake.ui import common, cli
    import build_maternalbound_pack
    from ebtools.config import load_dump_doc
    import ebtools
    support = Path(ebtools.__file__).parent.parent/'support'
    load_dump_doc(support/'native-source/earthbound.yml')
    from redux_compile_order import compiler_order_selftest
    compiler_order_selftest()
    return ''

class ProgressLog:
    def __init__(self, path):
        self.path = Path(path)
        self.log = self.path.with_suffix('.log').open('w', encoding='utf-8')
    def write(self, text):
        self.log.write(text)
        for line in text.splitlines():
            detail = None
            try:
                data = json.loads(line)
                if data.get('stage'):
                    detail = {
                        'download-source': 'Downloading Redux source files…',
                        'expand-base': 'Preparing Redux…',
                        'compile-redux': 'Building Redux…',
                        'convert-dialogue': 'Preparing Redux dialogue…',
                        'convert-pack': 'Packing Redux game data…',
                        'audit-movement': 'Checking Redux game data…',
                    }.get(data['stage'])
            except (ValueError, AttributeError):
                detail = {
                    'Reading your ROM...': 'Reading your ROM…',
                    'Packing assets...': 'Packing game data…',
                    'Building assets.pak...': 'Checking game data…',
                }.get(line.strip())
            if detail:
                self.path.write_text(detail, encoding='utf-8')
                self.log.flush()
        return len(text)
    def flush(self):
        self.log.flush()

def build(rom, output, redux, progress):
    """Return an empty string on success, an actionable error otherwise.

    Managed code owns validation and the final atomic install. Everything here
    is generated in a new, private staging directory, away from existing saves.
    """
    rom, output = Path(rom), Path(output)
    import ebtools
    support = Path(ebtools.__file__).parent.parent / 'support'
    output.parent.mkdir(parents=True, exist_ok=True)
    writer = ProgressLog(progress)
    old_cwd, old_args = os.getcwd(), sys.argv[:]
    old_bundle = getattr(sys, '_MEIPASS', None)
    try:
        with contextlib.redirect_stdout(writer), contextlib.redirect_stderr(writer):
            writer.path.write_text('Checking your ROM…', encoding='utf-8')
            raw = rom.read_bytes()
            if len(raw) == 3146240:
                raw = raw[512:]
            if len(raw) != 3145728 or hashlib.sha256(raw).hexdigest() != USA:
                raise ValueError('Choose a clean EarthBound (USA) .sfc or .smc ROM. Patched ROMs are not supported.')
            if output.exists():
                raise ValueError('Setup staging already exists. Existing games were preserved.')
            sys._MEIPASS = str(support)
            with tempfile.TemporaryDirectory(prefix='convert-', dir=output.parent) as work_name:
                work = Path(work_name)
                normalized = work / 'clean.sfc'
                normalized.write_bytes(raw)
                del raw
                from ebtools.cli.setup import setup
                base = work / 'assets.pak'
                setup(normalized, out=base, yaml_config=support/'native-source/earthbound.yml',
                      commondata=support/'native-source/commondefs.yml')
                from build_redux_profile import AUDITED_ORIGINAL_PACKS
                if hashlib.sha256(base.read_bytes()).hexdigest().upper() not in AUDITED_ORIGINAL_PACKS:
                    raise ValueError('Converted Original data differs from the supported version. Nothing was installed.')
                if redux:
                    from redux_setup_entry import main, run_worker
                    main(['--rom', str(normalized), '--base-assets', str(base),
                          '--output-directory', str(output)], worker_runner=run_worker)
                    shutil.move(str(base), output/'original-assets.pak')
                else:
                    output.mkdir()
                    shutil.move(str(base), output/'assets.pak')
            writer.path.write_text('Checking generated game data…', encoding='utf-8')
        return ''
    except BaseException as error:
        # Retain small compiler diagnostics in the exportable text log; remove
        # all generated ROMs/source copies when managed code cleans staging.
        for stage in output.parent.glob('.'+output.name+'.*.partial'):
            for name in ('compiler-identity.json', 'compile-redux.log'):
                diagnostic = stage/name
                if diagnostic.is_file():
                    writer.log.write('\n'+name+'\n'+diagnostic.read_text(encoding='utf-8', errors='replace')+'\n')
        traceback.print_exc(file=writer.log)
        return str(error) or 'ROM setup stopped. See rom-setup.log for details.'
    finally:
        os.chdir(old_cwd)
        sys.argv = old_args
        if old_bundle is None:
            if hasattr(sys, '_MEIPASS'):
                delattr(sys, '_MEIPASS')
        else:
            sys._MEIPASS = old_bundle
        writer.log.close()
