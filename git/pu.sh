#!/bin/bash
cd ..
git add .
git commit -m "update"
git push origin main
echo -e '\nlocal repo pushed to remote origin\n'