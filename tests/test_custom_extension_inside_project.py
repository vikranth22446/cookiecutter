import codecs
import os

import pytest

from cookiecutter import main


@pytest.fixture()
def template():
    return 'tests/test-extensions/custom-local-extension'


@pytest.fixture
def output_dir(tmpdir):
    return str(tmpdir.mkdir('local'))


def test_local_with_extension(template, output_dir):
    project_dir = main.cookiecutter(
        template,
        no_input=True,
        output_dir=output_dir,
        extra_context={
            'project_slug': 'local_extension',
            'name': 'World',
        },
    )

    readme_file = os.path.join(project_dir, 'README.rst')

    with codecs.open(readme_file, encoding='utf8') as f:
        readme = f.read().strip()

    assert readme == 'Hello Local World!'
