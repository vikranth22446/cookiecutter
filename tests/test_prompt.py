# -*- coding: utf-8 -*-

"""
test_prompt
-----------

Tests for `cookiecutter.prompt` module.
"""

import platform
from collections import OrderedDict

import pytest
from jinja2 import UndefinedError

from cookiecutter import prompt, exceptions, environment


@pytest.fixture(autouse=True)
def patch_readline_on_win(monkeypatch):
    if 'windows' in platform.platform().lower():
        monkeypatch.setattr('sys.stdin.readline', lambda: '\n')


class TestPrompt(object):
    def test_prompt_for_config_simple(self, monkeypatch):
        monkeypatch.setattr(
            'cookiecutter.prompt.read_user_variable',
            lambda var, default: u'Audrey Roy'
        )
        context = {'cookiecutter': {'full_name': 'Your Name'}}

        cookiecutter_dict = prompt.prompt_for_config(context)
        assert cookiecutter_dict == {'full_name': u'Audrey Roy'}

    def test_prompt_for_config_unicode(self, monkeypatch):
        monkeypatch.setattr(
            'cookiecutter.prompt.read_user_variable',
            lambda var, default: u'Pizzä ïs Gööd'
        )
        context = {'cookiecutter': {'full_name': 'Your Name'}}

        cookiecutter_dict = prompt.prompt_for_config(context)
        assert cookiecutter_dict == {'full_name': u'Pizzä ïs Gööd'}

    def test_prompt_for_config_empty_dict(self, monkeypatch):
        monkeypatch.setattr(
            'cookiecutter.prompt.read_user_dict',
            lambda var, default: {}
        )
        context = {'cookiecutter': {'details': {}}}

        cookiecutter_dict = prompt.prompt_for_config(context)
        assert cookiecutter_dict == {'details': {}}

    def test_prompt_for_config_dict(self, monkeypatch):
        monkeypatch.setattr(
            'cookiecutter.prompt.read_user_dict',
            lambda var, default: {"key": "value", "integer": 37}
        )
        context = {'cookiecutter': {'details': {}}}

        cookiecutter_dict = prompt.prompt_for_config(context)
        assert cookiecutter_dict == {
            'details': {
                'key': u'value',
                'integer': 37
            }
        }

    def test_prompt_for_config_deep_dict(self, monkeypatch):
        monkeypatch.setattr(
            'cookiecutter.prompt.read_user_dict',
            lambda var, default: {
                "key": "value",
                "integer_key": 37,
                "dict_key": {
                    "deep_key": "deep_value",
                    "deep_integer": 42,
                    "deep_list": [
                        "deep value 1",
                        "deep value 2",
                        "deep value 3",
                    ]
                },
                "list_key": [
                    "value 1",
                    "value 2",
                    "value 3",
                ]
            }
        )
        context = {'cookiecutter': {'details': {}}}

        cookiecutter_dict = prompt.prompt_for_config(context)
        assert cookiecutter_dict == OrderedDict({
            'details': {
                "key": "value",
                "integer_key": 37,
                "dict_key": {
                    "deep_key": "deep_value",
                    "deep_integer": 42,
                    "deep_list": [
                        "deep value 1",
                        "deep value 2",
                        "deep value 3",
                    ]
                },
                "list_key": [
                    "value 1",
                    "value 2",
                    "value 3",
                ]
            }
        })

    def test_should_render_dict(self):
        context = {
            'cookiecutter': {
                'project_name': 'Slartibartfast',
                'details': {
                    'other_name': '{{cookiecutter.project_name}}'
                }
            }
        }

        cookiecutter_dict = prompt.prompt_for_config(context, no_input=True)
        assert cookiecutter_dict == {
            'project_name': 'Slartibartfast',
            'details': {
                'other_name': u'Slartibartfast',
            }
        }

    def test_should_render_deep_dict(self):
        context = {
            'cookiecutter': {
                'project_name': "Slartibartfast",
                'details': {
                    "key": "value",
                    "integer_key": 37,
                    "other_name": '{{cookiecutter.project_name}}',
                    "dict_key": {
                        "deep_key": "deep_value",
                        "deep_integer": 42,
                        "deep_other_name": '{{cookiecutter.project_name}}',
                        "deep_list": [
                            "deep value 1",
                            "{{cookiecutter.project_name}}",
                            "deep value 3",
                        ]
                    },
                    "list_key": [
                        "value 1",
                        "{{cookiecutter.project_name}}",
                        "value 3",
                    ]
                }
            }
        }

        cookiecutter_dict = prompt.prompt_for_config(context, no_input=True)
        assert cookiecutter_dict == {
            'project_name': "Slartibartfast",
            'details': {
                "key": "value",
                "integer_key": 37,
                "other_name": "Slartibartfast",
                "dict_key": {
                    "deep_key": "deep_value",
                    "deep_integer": 42,
                    "deep_other_name": "Slartibartfast",
                    "deep_list": [
                        "deep value 1",
                        "Slartibartfast",
                        "deep value 3",
                    ]
                },
                "list_key": [
                    "value 1",
                    "Slartibartfast",
                    "value 3",
                ]
            }
        }

    def test_unicode_prompt_for_config_unicode(self, monkeypatch):
        monkeypatch.setattr(
            'cookiecutter.prompt.read_user_variable',
            lambda var, default: u'Pizzä ïs Gööd'
        )
        context = {'cookiecutter': {'full_name': u'Řekni či napiš své jméno'}}

        cookiecutter_dict = prompt.prompt_for_config(context)
        assert cookiecutter_dict == {'full_name': u'Pizzä ïs Gööd'}

    def test_unicode_prompt_for_default_config_unicode(self, monkeypatch):
        monkeypatch.setattr(
            'cookiecutter.prompt.read_user_variable',
            lambda var, default: default
        )
        context = {'cookiecutter': {'full_name': u'Řekni či napiš své jméno'}}

        cookiecutter_dict = prompt.prompt_for_config(context)
        assert cookiecutter_dict == {'full_name': u'Řekni či napiš své jméno'}

    def test_unicode_prompt_for_templated_config(self, monkeypatch):
        monkeypatch.setattr(
            'cookiecutter.prompt.read_user_variable',
            lambda var, default: default
        )
        context = {'cookiecutter': OrderedDict([
            (
                'project_name',
                u'A New Project'
            ), (
                'pkg_name',
                u'{{ cookiecutter.project_name|lower|replace(" ", "") }}'
            )
        ])}

        exp_cookiecutter_dict = {
            'project_name': u'A New Project', 'pkg_name': u'anewproject'
        }
        cookiecutter_dict = prompt.prompt_for_config(context)
        assert cookiecutter_dict == exp_cookiecutter_dict

    def test_dont_prompt_for_private_context_var(self, monkeypatch):
        monkeypatch.setattr(
            'cookiecutter.prompt.read_user_variable',
            lambda var, default: pytest.fail(
                'Should not try to read a response for private context var'
            )
        )
        context = {'cookiecutter': {'_copy_without_render': ['*.html']}}
        cookiecutter_dict = prompt.prompt_for_config(context)
        assert cookiecutter_dict == {'_copy_without_render': ['*.html']}


class TestV2DictConfig:
    @pytest.fixture()
    def reload_supported_types(self):
        def make_reloader():
            prompt.SUPPORTED_TYPES = {
                "multilist": prompt.read_user_choice,
                "list": prompt.read_user_choice,
                "string": prompt.read_user_variable,
                "int": prompt.read_user_int,
                "float": prompt.read_user_float,
                "bool": prompt.read_user_yes_no,
                "password": prompt.read_repo_password,
                "json": prompt.read_user_dict
            }

        return make_reloader

    def test_dict_format_support(self):
        assert prompt.supports_new_format({'default': 'test', 'type': "string"})
        assert not prompt.supports_new_format({'data': ["list1", "list2"], "other data": "string"})

    def test_dict_valid_supported_types(self):
        assert prompt.supports_new_format({'default': 'test', 'type': "int"})
        assert not prompt.supports_new_format({'default': 'test', 'type': "a random type not in the list"}, )
        assert prompt.supported_type("int")
        assert not prompt.supported_type("A random type")

    def test_dict_click_description(self, mocker):
        echo = mocker.patch('click.echo')
        context = {
            'cookiecutter': {
                'project_name': 'Sample Project',
                'details': {
                    'default': 'test',
                    'description': 'This is a description of the field that is printed before the variable',
                    "type": "string"
                }
            }
        }
        prompt.prompt_for_config(context, no_input=True)
        echo.assert_called_once_with('This is a description of the field that is printed before the variable')

    def test_dict_prompt_invisible(self, mocker, reload_supported_types):
        read_variable = mocker.patch('cookiecutter.prompt.read_user_variable')
        reload_supported_types()
        context = {
            'cookiecutter': {
                'details': {
                    'default': 'test',
                    "visible": False
                }
            }
        }
        assert prompt.prompt_for_config(context) == {
            "details": "test"
        }
        assert not read_variable.called

    def test_dict_prompt_visible(self, monkeypatch, reload_supported_types):
        monkeypatch.setattr(
            'cookiecutter.prompt.read_user_variable',
            lambda var, default: "This is a string variable read from the prompt"
        )
        reload_supported_types()
        context = {
            'cookiecutter': {
                'details': {
                    'default': 'Sample',
                    "visible": True
                }
            }
        }
        assert prompt.prompt_for_config(context) == {
            "details": "This is a string variable read from the prompt"
        }

    def test_dict_custom_prompt(self, monkeypatch, mocker, reload_supported_types):
        monkeypatch.setattr(
            'cookiecutter.prompt.read_user_variable',
            lambda var, default: 'test2'
        )
        read_variable = mocker.patch('cookiecutter.prompt.read_user_variable')
        read_variable.return_value = "test2"
        reload_supported_types()
        context = {
            'cookiecutter': {
                'details': {
                    'default': 'test',
                    "prompt": "This is a custom prompt"
                }
            }
        }
        assert prompt.prompt_for_config(context) == {
            "details": "test2"
        }
        read_variable.assert_called_once_with("This is a custom prompt", "test")

    def test_dict_skip_if(self, monkeypatch, mocker, reload_supported_types):
        echo = mocker.patch('click.echo')
        monkeypatch.setattr(
            'cookiecutter.prompt.read_user_variable', lambda var, default: default
        )
        monkeypatch.setattr(
            "cookiecutter.prompt.read_user_yes_no", lambda var, default: default
        )
        reload_supported_types()
        context = {
            'cookiecutter': {
                "project_name": "Sample Project",
                "test": "{% if cookiecutter.project_name == 'Sample Project' %}true{%endif%}",
                'details': {
                    'default': 'test',
                    "skip_if": "{% if cookiecutter.project_name == 'Sample Project' %}true{%else%}false{%endif%}"
                },
                "next_variable": "Skipped to current variable"
            }
        }
        assert prompt.prompt_for_config(context) == {
            "project_name": "Sample Project",
            "details": None,
            "next_variable": "Skipped to current variable",
            "test": True
        }
        echo.assert_any_call("skipped " + "details")

    def test_dict_skip_to(self, monkeypatch, mocker, reload_supported_types):
        echo = mocker.patch('click.echo')
        monkeypatch.setattr(
            'cookiecutter.prompt.read_user_variable', lambda var, default: default
        )
        reload_supported_types()
        context = {
            'cookiecutter': {
                "project_name": "Sample Project",
                'details': {
                    'default': 'test',
                    "skip_if": "{% if cookiecutter.project_name == 'Sample Project' %}true{%else%}false{%endif%}",
                    "skip_to": "future_variable"
                },
                "next_variable": "Skipped variable",
                "future_variable": "Some Variable"
            }
        }
        assert prompt.prompt_for_config(context) == {
            "project_name": "Sample Project",
            "details": None,
            "next_variable": None,
            "future_variable": "Some Variable"
        }
        echo.assert_any_call("skipped " + "details")
        echo.assert_any_call("skipped " + "next_variable")
        echo.assert_any_call("skipping to " + "future_variable")

    def test_dict_skip_to_invalid(self, monkeypatch, mocker, reload_supported_types):
        echo = mocker.patch('click.echo')
        monkeypatch.setattr(
            'cookiecutter.prompt.read_user_variable', lambda var, default: default
        )
        reload_supported_types()
        context = {
            'cookiecutter': {
                "project_name": "Sample Project",
                'details': {
                    'default': 'test',
                    "skip_if": "{% if cookiecutter.project_name == 'Sample Project' %}true{%else%}false{%endif%}",
                    "skip_to": "Invalid Variable"
                },
                "next_variable": None,
                "future_variable": None
            }
        }
        assert prompt.prompt_for_config(context) == {
            "project_name": "Sample Project",
            "details": None,
            "next_variable": None,
            "future_variable": None
        }
        echo.assert_any_call("skipped " + "details")
        echo.assert_any_call("skipping to " + "Invalid Variable")
        echo.assert_any_call("skipped " + "next_variable")
        echo.assert_any_call("skipped " + "future_variable")
        echo.assert_any_call("Processed all variables, but skip_to_variable 'Invalid Variable' was never found.")

    def test_dict_correct_validation(self, monkeypatch, reload_supported_types):
        monkeypatch.setattr(
            'cookiecutter.prompt.read_user_variable', lambda var, default: default
        )
        reload_supported_types()
        context = {
            'cookiecutter': {
                "project_name": {
                    "default": "Sample Project",
                },
                "email": {
                    "default": "test@gmail.com",
                    "validation": "(\w+)@gmail.com"
                }
            }
        }
        assert prompt.prompt_for_config(context) == {
            "project_name": "Sample Project",
            "email": "test@gmail.com"
        }

    def test_dict_invalid_validation(self, monkeypatch, reload_supported_types):
        monkeypatch.setattr(
            'cookiecutter.prompt.read_user_variable', lambda var, default: default
        )
        reload_supported_types()
        context = {
            'cookiecutter': {
                "project_name": {
                    "default": "Sample Project",
                },
                "email": {
                    "default": "test",
                    "validation": "(\w+)@gmail.com"
                }
            }
        }
        with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
            prompt.prompt_for_config(context)
        error = err.value
        assert error.message == "Unable to render variable 'email'"
        assert error.context == context

    def test_validation_wrapper(self):
        assert prompt.validate("", None, lambda: True)()
        assert prompt.validate("(\w+)@gmail.com", "key", lambda: "test@gmail.com")() == "test@gmail.com"

    def test_dict_basic_list(self, mocker):
        choices = ["1", "2", "3", "4"]
        click_prompt = mocker.patch("click.prompt")
        click_prompt.return_value = "3"

        context = {
            'cookiecutter': {
                "options": {
                    "default": "1",
                    "choices": choices,
                    "type": "list"
                }
            }
        }
        assert prompt.prompt_for_config(context) == {
            "options": "3"
        }
        assert prompt.prompt_for_config(context, no_input=True) == {"options": "1"}
        context["cookiecutter"]["options"]["default"] = "a"
        with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
            prompt.prompt_for_config(context)
        error = err.value
        assert error.message == "Unable to render variable 'options'"
        assert error.context == context

    def test_dict_multilist(self):
        pass

    def test_dict_str(self, monkeypatch, reload_supported_types):
        monkeypatch.setattr(
            'cookiecutter.prompt.read_user_variable',
            lambda var, default: 'A Random String'
        )
        reload_supported_types()
        context = \
            {'cookiecutter':
                {'details': {
                    'default': 'test',
                    'type': "string"}
                }
            }

        cookiecutter_dict = prompt.prompt_for_config(context)
        assert cookiecutter_dict == {
            'details': "A Random String"
        }

    def test_dict_raw_types(self):
        pass


class TestReadUserChoice(object):
    def test_should_invoke_read_user_choice(self, mocker):
        read_choice = mocker.patch('cookiecutter.prompt.read_user_choice')
        read_choice.return_value = 'all'

        read_variable = mocker.patch('cookiecutter.prompt.read_user_variable')

        choices = ['landscape', 'portrait', 'all']
        context = {
            'cookiecutter': {
                'orientation': choices
            }
        }

        cookiecutter_dict = prompt.prompt_for_config(context)
        assert not read_variable.called
        read_choice.assert_called_once_with('orientation', choices)
        assert cookiecutter_dict == {'orientation': 'all'}

    def test_should_not_invoke_read_user_variable(self, mocker):
        read_variable = mocker.patch('cookiecutter.prompt.read_user_variable')
        read_variable.return_value = u'Audrey Roy'

        prompt_choice = mocker.patch(
            'cookiecutter.prompt.prompt_choice_for_config'
        )

        read_choice = mocker.patch('cookiecutter.prompt.read_user_choice')

        CONTEXT = {'cookiecutter': {'full_name': 'Your Name'}}

        cookiecutter_dict = prompt.prompt_for_config(CONTEXT)

        assert not prompt_choice.called
        assert not read_choice.called
        read_variable.assert_called_once_with('full_name', 'Your Name')
        assert cookiecutter_dict == {'full_name': u'Audrey Roy'}

    def test_should_render_choices(self, mocker):
        read_choice = mocker.patch('cookiecutter.prompt.read_user_choice')
        read_choice.return_value = u'anewproject'

        read_variable = mocker.patch('cookiecutter.prompt.read_user_variable')
        read_variable.return_value = u'A New Project'

        RENDERED_CHOICES = [
            u'foo',
            u'anewproject',
            u'bar'
        ]

        CONTEXT = {'cookiecutter': OrderedDict([
            (
                'project_name',
                u'A New Project'
            ), (
                'pkg_name',
                [
                    u'foo',
                    u'{{ cookiecutter.project_name|lower|replace(" ", "") }}',
                    u'bar'
                ]
            )
        ])}

        EXP_COOKIECUTTER_DICT = {
            'project_name': u'A New Project', 'pkg_name': u'anewproject'
        }
        cookiecutter_dict = prompt.prompt_for_config(CONTEXT)

        read_variable.assert_called_once_with('project_name', u'A New Project')
        read_choice.assert_called_once_with('pkg_name', RENDERED_CHOICES)
        assert cookiecutter_dict == EXP_COOKIECUTTER_DICT


class TestPromptChoiceForConfig(object):
    @pytest.fixture
    def choices(self):
        return ['landscape', 'portrait', 'all']

    @pytest.fixture
    def context(self, choices):
        return {
            'cookiecutter': {
                'orientation': choices
            }
        }

    def test_should_return_first_option_if_no_input(
            self, mocker, choices, context):
        read_choice = mocker.patch('cookiecutter.prompt.read_user_choice')

        expected_choice = choices[0]

        actual_choice = prompt.prompt_choice_for_config(
            context,
            environment.StrictEnvironment(),
            'orientation',
            choices,
            True  # Suppress user input
        )
        assert not read_choice.called
        assert expected_choice == actual_choice

    def test_should_read_userchoice(self, mocker, choices, context):
        read_choice = mocker.patch('cookiecutter.prompt.read_user_choice')
        read_choice.return_value = 'all'

        expected_choice = 'all'

        actual_choice = prompt.prompt_choice_for_config(
            context,
            environment.StrictEnvironment(),
            'orientation',
            choices,
            False  # Ask the user for input
        )
        read_choice.assert_called_once_with('orientation', choices)
        assert expected_choice == actual_choice


def test_undefined_variable_in_cookiecutter_dict():
    context = {
        'cookiecutter': {
            'hello': 'world',
            'foo': '{{cookiecutter.nope}}'
        }
    }
    with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
        prompt.prompt_for_config(context, no_input=True)

    error = err.value
    assert error.message == "Unable to render variable 'foo'"
    assert error.context == context


def test_undefined_variable_in_cookiecutter_dict_with_choices():
    context = {
        'cookiecutter': {
            'hello': 'world',
            'foo': ['123', '{{cookiecutter.nope}}', '456']
        }
    }
    with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
        prompt.prompt_for_config(context, no_input=True)

    error = err.value
    assert error.message == "Unable to render variable 'foo'"
    assert error.context == context


def test_undefined_variable_in_cookiecutter_dict_with_dict_key():
    context = {
        'cookiecutter': {
            'hello': 'world',
            'foo': {'{{cookiecutter.nope}}': 'value'}
        }
    }
    with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
        prompt.prompt_for_config(context, no_input=True)

    error = err.value
    assert error.message == "Unable to render variable 'foo'"
    assert error.context == context


def test_undefined_variable_in_cookiecutter_dict_with_key_value():
    context = {
        'cookiecutter': {
            'hello': 'world',
            'foo': {'key': '{{cookiecutter.nope}}'}
        }
    }
    with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
        prompt.prompt_for_config(context, no_input=True)

    error = err.value
    assert error.message == "Unable to render variable 'foo'"
    assert error.context == context
