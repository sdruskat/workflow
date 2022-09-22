# SPDX-FileCopyrightText: 2022 Stephan Druskat
#
# SPDX-License-Identifier: Apache-2.0

import subprocess

from git import Repo

# Get the repository for this directory, which is the hermes-hmc/workflow clone
repo = Repo('.')
assert not repo.bare

# Get the git instance for this repository
git = repo.git
# Get the active branch
branch = repo.active_branch

# Get a list of files in the current branch, ignore the following:
# LICENSES/*
files = [file_str for file_str in git.ls_tree('-r', '--name-only', branch, repo.working_dir).split('\n') if not file_str.startswith('LICENSES/')]

# Build a list of files to unique committer names, using git log
file_committer_map = {}
for file in files:
    if file not in file_committer_map:
        file_committer_map[file] = set()
    for name in git.log('--follow', '--pretty=format:%an', '--', file).split('\n'):
        file_committer_map[file].add(name)

# Run the reuse CLI to add copyright headers for all committers
for file in file_committer_map:
    exts = ['.txt', '.bat', 'Makefile', '.py', '.toml', '.yml', '.gitignore']
    force_single_line = False
    for ext in exts:
        if file.endswith(ext):
            force_single_line = True
    for name in file_committer_map[file]:
        if force_single_line:
            # Force single line copyright comments for those file types that support it
            subprocess.run(['reuse', 'addheader', '--merge-copyrights', '--single-line', f'-c={name}', file])
        else:
            subprocess.run(['reuse', 'addheader', '--merge-copyrights', f'-c={name}', file])
