#!/bin/bash

echo "=== System Information ==="
echo ""
echo "Hostname: $(hostname)"
echo "OS: $(sw_vers -productName 2>/dev/null || uname -s) $(sw_vers -productVersion 2>/dev/null || uname -r)"
echo "Architecture: $(uname -m)"
echo ""
echo "=== CPU Info ==="
top -l 1 | head -10
echo ""
echo "=== Memory Info ==="
vm_stat | head -8
