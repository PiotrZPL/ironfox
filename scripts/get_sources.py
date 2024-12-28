#!/usr/bin/env python

import os
import subprocess
from config import GITHUB_REF_DOWNLOADS, GITHUB_REF_URL, MOZILLA_REF_DOWNLOADS, MOZILLA_REF_URL, WASI_REPO, WASI_TAG, GeckoPaths
from utils import download, zipextract_rmtoplevel

def get_sources(paths: GeckoPaths):
    print("Downloading sources...")

    for repo_name, repo, ref in GITHUB_REF_DOWNLOADS:
        do_download(repo_name, GITHUB_REF_URL.format(repo, ref))
        
    for repo_name, repo, ref in MOZILLA_REF_DOWNLOADS:
        do_download(repo_name, MOZILLA_REF_URL.format(repo, ref))
        
    print("Cloning wasi-sdk...")
    subprocess.check_call(["git", "clone", "--branch", WASI_TAG, "--depth=1", WASI_REPO], cwd=paths.rootdir)
    subprocess.check_call(["git", "submodule", "update", "--init", "--depth=1"], cwd=paths.wasisdkdir)

def do_download(repo_name, url):
    repo_zip = paths.builddir / ("{}.zip".format(repo_name))
    repo_path = paths.rootdir / repo_name
    download(url, repo_zip)

    if not repo_zip.exists():
        raise RuntimeError(f"Source archive for {repo_name} does not exist.")

    if not repo_path.exists():
        repo_path.mkdir(parents=True)

    print(f"Extracting {repo_zip}")
    zipextract_rmtoplevel(repo_zip, repo_path)
    print("\n")

if __name__ == "__main__":
    paths = GeckoPaths()

    if not paths.builddir.exists():
        paths.builddir.mkdir()

    get_sources(paths)

    paths_sh = paths.rootdir / "scripts/paths_local.sh"
    print(f"Writing {paths_sh}...")
    
    with open(paths_sh, "w") as f:
        f.write(
            f"""
export patches={paths.patchdir}
export rootdir={paths.rootdir}
export builddir="$rootdir/build"
export android_components={paths.android_components}
export application_services={paths.appservicesdir}
export glean={paths.gleandir}
export fenix={paths.fenix}
export mozilla_release={paths.geckodir}
export gmscore={paths.gmscoredir}
export wasi={paths.wasisdkdir}
export paths_source="true"
"""
        )
