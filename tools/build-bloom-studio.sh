#!/bin/sh
# Wraps the Bloom Studio module in a full HTML document so it runs on its own
# (Netlify, a USB stick, or double-click). The module file itself has no
# <html>/<head>/<body> so it can also be published as an artifact or embedded.
set -e
cd "$(dirname "$0")/../bloom-studio"
{
  printf '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
  printf '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
  printf '<meta name="theme-color" content="#47533D">\n</head>\n<body>\n'
  cat bloom-studio.html
  printf '\n</body>\n</html>\n'
} > index.html
echo "wrote bloom-studio/index.html"
