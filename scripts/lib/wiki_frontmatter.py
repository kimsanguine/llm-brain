"""Read legacy paper titles without rewriting source files or source fields."""
import json
from pathlib import Path

import frontmatter
import yaml


def loads_wiki_post(text: str, *, allow_legacy_title: bool = False):
    try:
        return frontmatter.loads(text)
    except yaml.YAMLError:
        if not allow_legacy_title:
            raise
        lines = text.splitlines(keepends=True)
        if not lines or lines[0].strip() != '---':
            raise
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == '---'), None)
        if end is None:
            raise
        titles = [i for i in range(1, end) if lines[i].startswith('title:')]
        if len(titles) != 1:
            raise
        index = titles[0]
        value = lines[index][len('title:'):].strip()
        if (not value or ': ' not in value or value[0] in '\"\'[{>|!&*' or ' #' in value):
            raise
        ending = '\r\n' if lines[index].endswith('\r\n') else '\n'
        lines[index] = 'title: ' + json.dumps(value, ensure_ascii=False) + ending
        # All remaining metadata still goes through the same safe YAML parser.
        return frontmatter.loads(''.join(lines))


def load_wiki_post(path: Path, *, allow_legacy_title: bool = False):
    return loads_wiki_post(Path(path).read_text(encoding='utf-8'), allow_legacy_title=allow_legacy_title)
