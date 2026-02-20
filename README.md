# sprint_planning_simulator

```bash
find . -type f ! -path '*/.*' ! -name "*.lock" ! -name "*.db" ! -name "*.sh" ! -name "*.toml" ! -name "*.lock" ! -name "*.ps1" ! -name "*.md" ! -name "*.pyc" ! -name "*.local.yaml" | while read -r file; do
    echo "=== $file ==="
    cat "$file"
    echo "=============="
    echo
done
```