# Dup Remover

## Remove duplicated files by hash in given directory recursively

usage: dup_remove.py [-h] [-t threads] [-a] [-d] dir

| Options    | Description |
| ----------:| -----------:|
| dir        | Directory to recursively process |
| -h, --help | show this help message and exit |
| -t threads | Thread number, default: 16 |
| -a         | Auto-mode, always keep the 1st file and remove others |
| -d         | Dry-run only, skip the actual deletion |
