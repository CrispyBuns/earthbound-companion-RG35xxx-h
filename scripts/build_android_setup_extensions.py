# SPDX-License-Identifier: GPL-3.0-or-later
"""Cross-compile the pinned Redux compiler/compressor for embedded Python."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import urllib.request
import zipfile

PYTHON_TARGET = '3.13.9-0'
TARGET_SHA256 = {
    'arm64-v8a': 'c19f39fecada0b3932ab7a61b0f214c1212068cbbae0dc22c2afa38a4f354b8e',
    'x86_64': 'f9f2e36b08e60e92bcdd201eea4aff5ba13681b7b425ce24e0a140eca626674d',
}

def download(url, path):
    if not path.exists():
        urllib.request.urlretrieve(url, path)
    return path

def wheel(output, name, version, abi, module_path, library):
    tag = 'cp313-cp313-android_26_'+abi.replace('-', '_')
    filename = output/f'{name}-{version}-{tag}.whl'
    metadata = f'{name}-{version}.dist-info'
    with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(library, module_path)
        z.writestr(metadata+'/METADATA', f'Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n')
        z.writestr(metadata+'/WHEEL', f'Wheel-Version: 1.0\nRoot-Is-Purelib: false\nTag: {tag}\n')
        rows = []
        for name in z.namelist():
            content = z.read(name)
            digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).decode().rstrip('=')
            rows.append(f'{name},sha256={digest},{len(content)}')
        z.writestr(metadata+'/RECORD', '\n'.join(rows)+'\n'+metadata+'/RECORD,,\n')

def build(work, ndk):
    output = work/'wheels'
    output.mkdir(parents=True, exist_ok=True)
    host = 'windows-x86_64' if platform.system() == 'Windows' else 'linux-x86_64'
    compiler_root = ndk/'toolchains/llvm/prebuilt'/host/'bin'
    ccc = work/'tools/CCScript'
    cs = work/'tools/CoilSnake'
    for abi, triple in [('arm64-v8a', 'aarch64-linux-android'), ('x86_64', 'x86_64-linux-android')]:
        directory = work/('native-'+abi)
        directory.mkdir(exist_ok=True)
        url = f'https://repo.maven.apache.org/maven2/com/chaquo/python/target/{PYTHON_TARGET}/target-{PYTHON_TARGET}-{abi}.zip'
        archive = download(url, directory/'python.zip')
        if hashlib.sha256(archive.read_bytes()).hexdigest() != TARGET_SHA256[abi]:
            raise ValueError('Android Python target checksum differs')
        with zipfile.ZipFile(archive) as z:
            z.extractall(directory/'python')
        includes = directory/'python/include/python3.13'
        libraries = directory/'python/jniLibs'/abi
        suffix = '.cmd' if platform.system() == 'Windows' else ''
        cc = compiler_root/(triple+'26-clang'+suffix)
        cpp = compiler_root/(triple+'26-clang++'+suffix)
        common = ['-shared', '-fPIC', '-O2', '-I'+str(includes), '-L'+str(libraries),
                  '-lpython3.13', '-Wl,-rpath,$ORIGIN']
        source_files = sorted((ccc/'src').rglob('*')) + sorted((cs/'coilsnake/util/eb/exhal').glob('*')) + [cs/'coilsnake/util/eb/native_comp.c', ndk/'source.properties']
        identity = hashlib.sha256((TARGET_SHA256[abi]+'|'+abi+'|android26-c++17-O2-static-libc++-native_comp-alias').encode())
        for file in source_files:
            if file.is_file():
                identity.update(file.name.encode());identity.update(file.read_bytes())
        build_key = identity.hexdigest()
        native_source = directory/'native_comp.c'
        native_source.write_text((cs/'coilsnake/util/eb/native_comp.c').read_text(encoding='utf-8')
            .replace('PyInit_native_comp', 'PyInit_eb_native_comp'), encoding='utf-8')
        comp = directory/'eb_native_comp.so'
        compiler = directory/'ccscript.so'
        receipt = directory/'compiled.json'
        previous = json.loads(receipt.read_text()) if receipt.exists() else {}
        current = previous.get('sourceSha256') == build_key and all(p.exists() and
            hashlib.sha256(p.read_bytes()).hexdigest() == previous.get(p.name) for p in (comp, compiler))
        if not current:
            subprocess.run([str(cc), *common, '-I'+str(cs/'coilsnake/util/eb'),
                        str(native_source), str(cs/'coilsnake/util/eb/exhal/compress.c'), '-o', str(comp)], check=True)
            subprocess.run([str(cpp), *common, '-std=c++17', '-static-libstdc++',
                        *map(str, sorted((ccc/'src').glob('*.cpp'))), '-o', str(compiler)], check=True)
            receipt.write_text(json.dumps({'sourceSha256': build_key,
                **{p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (comp, compiler)}}, indent=2), encoding='utf-8')
        wheel(output, 'eb_native_comp', '1.0.0', abi, 'eb_native_comp.so', comp)
        wheel(output, 'ccscript', '1.500', abi, 'ccscript.so', compiler)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, default=Path('build/android-setup'))
    parser.add_argument('--ndk', type=Path, required=True)
    args = parser.parse_args()
    build(args.work.resolve(), args.ndk.resolve())
