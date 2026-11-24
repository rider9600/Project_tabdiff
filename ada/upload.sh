#!/bin/bash
# Laptop side (rules/03_ADA_HPC.md): copy the committed code and the clean tables to Ada.
#     bash ada/upload.sh <staging dir>          # run only after the user's go
# The code is `git archive HEAD` (committed files only, no data, secrets or runs), with a
# VERSION file naming the commit. No rsync on this laptop, so scp -r; scp overwrites but never
# deletes, so a file removed from the repo stays on Ada until the user says to delete it.
set -euo pipefail
STAGE=${1:?staging dir}
KEY=~/.ssh/id_ed25519_ada
HOST=cs9442.01@${ADA_GW:-ada-gw1}.iiit.ac.in   # ADA_GW=ada-gw2 when gw1 is down
PROJECT=${PROJECT:?set PROJECT, e.g. export PROJECT=myproj}
ROOT=$(git rev-parse --show-toplevel)

if [ -n "$(git -C "$ROOT" status --porcelain)" ]; then
    echo "Uncommitted code changes; commit first so VERSION names what runs."; exit 1
fi
rm -rf "$STAGE/code" && mkdir -p "$STAGE/code"
git -C "$ROOT" archive HEAD | tar -x -C "$STAGE/code"
echo "$(git -C "$ROOT" rev-parse --short HEAD) $(git -C "$ROOT" log -1 --format=%cs)" > "$STAGE/code/VERSION"
du -sh "$STAGE/code" "$ROOT/data_clean"

ssh -i $KEY -o BatchMode=yes $HOST "df -h ~ | tail -1; mkdir -p ~/$PROJECT/logs ~/$PROJECT/data_clean"
scp -i $KEY -o BatchMode=yes -q -r "$STAGE/code" $HOST:$PROJECT/
scp -i $KEY -o BatchMode=yes -q "$ROOT"/data_clean/*.parquet "$ROOT"/data_clean/*.graphml "$ROOT"/data_clean/data_report.json $HOST:$PROJECT/data_clean/
ssh -i $KEY -o BatchMode=yes $HOST "cat ~/$PROJECT/code/VERSION; ls -l ~/$PROJECT/data_clean; du -sh ~/$PROJECT"
