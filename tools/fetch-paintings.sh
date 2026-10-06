#!/bin/sh
# Downloads every Picture Study painting from Wikimedia Commons into
# bloom-studio/paintings/<id>.jpg so the app can ship them with itself
# (needed wherever external images are blocked, such as a claude.ai artifact).
# All of these paintings are in the public domain.
set -e
cd "$(dirname "$0")/../bloom-studio"
mkdir -p paintings
node -e '
const s=require("fs").readFileSync("bloom-studio.html","utf8");
const m=s.match(/\/\*PAINTINGS-START\*\/([\s\S]*?)\/\*PAINTINGS-END\*\//);
const PAINTINGS=new Function(m[1]+";return PAINTINGS")();
for(const p of PAINTINGS)console.log(p.id+"\t"+encodeURIComponent(p.file));
' | while IFS="$(printf '\t')" read -r id file; do
  out="paintings/$id.jpg"
  [ -s "$out" ] && { echo "have $out"; continue; }
  echo "get  $out"
  curl -fsSL -A "BloomStudio/1.0 (picture study; public-domain art)" \
    "https://commons.wikimedia.org/wiki/Special:FilePath/$file?width=1200" -o "$out" || { echo "FAILED $id"; rm -f "$out"; }
done
