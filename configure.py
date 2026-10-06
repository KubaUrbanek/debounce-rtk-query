#!/usr/bin/env python3
"""Render local config; never overwrite existing OpenCode configuration."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--weak', required=True, help='Exact provider/model-id for Luna')
    parser.add_argument('--strong', required=True, help='Exact provider/model-id for Sol')
    args = parser.parse_args()
    for value in (args.weak, args.strong):
        if '/' not in value or any(c.isspace() for c in value) or value.startswith('__'):
            parser.error('Use an exact provider/model-id from opencode models.')
    base = Path(__file__).resolve().parent
    root = base.parent
    config = json.loads((base / 'config.template.json').read_text(encoding='utf-8'))

    def replace(value):
        if isinstance(value, dict):
            return {key: replace(item) for key, item in value.items()}
        if isinstance(value, list):
            return [replace(item) for item in value]
        return {'__WEAK_MODEL__': args.weak, '__STRONG_MODEL__': args.strong}.get(value, value) if isinstance(value, str) else value

    existing = any((root / name).exists() for name in ('opencode.json', 'opencode.jsonc'))
    existing = existing or any((base / name).exists() for name in ('opencode.json', 'opencode.jsonc'))
    existing = existing or any((base / name).exists() for name in ('agents', 'agent'))
    target = root / ('opencode.ai-setup.candidate.json' if existing else 'opencode.json')
    try:
        with target.open('x', encoding='utf-8') as output:
            json.dump(replace(config), output, ensure_ascii=False, indent=2)
            output.write('\n')
    except FileExistsError:
        parser.error(f'{target.name} already exists; inspect it instead of overwriting.')
    print(f'Created: {target}')
    if existing:
        print('Existing config/agents detected. Merge candidate using PROJECT-SETUP-PROMPT.md; candidate is not automatically loaded.')
    print('Model availability and local OpenCode compatibility must be checked in your environment.')


if __name__ == '__main__':
    main()
