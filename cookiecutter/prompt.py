# -*- coding: utf-8 -*-

"""
cookiecutter.prompt
---------------------

Functions for prompting the user for project info.
"""

import json
import re
from collections import OrderedDict

import click
from future.utils import iteritems
from jinja2.exceptions import UndefinedError
from past.builtins import basestring

from .environment import StrictEnvironment
from .exceptions import UndefinedVariableInTemplate


def read_user_variable(var_name, default_value):
    """Prompt the user for the given variable and return the entered value
    or the given default.

    :param str var_name: Variable of the context to query the user
    :param default_value: Value that will be returned if no input happens
    """
    # Please see http://click.pocoo.org/4/api/#click.prompt
    if var_name == "":
        raise UndefinedError
    return click.prompt(var_name, default=default_value)


def read_user_int(var_name, default_value):
    """Prompt the user for the given variable and return the entered value
    or the given default.

    :param str var_name: Variable of the context to query the user
    :param default_value: Value that will be returned if no input happens
    """
    # Please see http://click.pocoo.org/4/api/#click.prompt
    return click.prompt(var_name, default=default_value, type=click.INT)


def read_user_yes_no(question, default_value):
    """Prompt the user to reply with 'yes' or 'no' (or equivalent values).

    Note:
      Possible choices are 'true', '1', 'yes', 'y' or 'false', '0', 'no', 'n'

    :param str question: Question to the user
    :param default_value: Value that will be returned if no input happens
    """
    # Please see http://click.pocoo.org/4/api/#click.prompt
    return click.prompt(
        question,
        default=default_value,
        type=click.BOOL
    )


def read_user_float(var_name, default):
    return click.prompt(var_name, default=default, type=click.FLOAT)


def read_repo_password(question, default=None):
    """Prompt the user to enter a password

    :param str question: Question to the user
    """
    # Please see http://click.pocoo.org/4/api/#click.prompt
    return click.prompt(question, hide_input=True)


def read_user_choice(var_name, options, multiple=False):
    """Prompt the user to choose from several options for the given variable.

    The first item will be returned if no input happens.

    :param str var_name: Variable as specified in the context
    :param list options: Sequence of options that are available to select from
    :return: Exactly one item of ``options`` that has been chosen by the user
    """
    # Please see http://click.pocoo.org/4/api/#click.prompt
    if not isinstance(options, list):
        raise TypeError

    if not options:
        raise ValueError

    choice_map = OrderedDict(
        (u'{}'.format(i), value) for i, value in enumerate(options, 1)
    )
    choices = choice_map.keys()
    default = u'1'

    choice_lines = [u'{} - {}'.format(*c) for c in choice_map.items()]
    prompt = u'\n'.join((
        u'Select {}:'.format(var_name),
        u'\n'.join(choice_lines),
        u'Choose from {}'.format(u', '.join(choices))
    ))
    if multiple:
        prompt = u'\n'.join((
            u'Select {}:'.format(var_name),
            u'\n'.join(choice_lines),
            u'Choose multiple from {}'.format(u', '.join(choices)),
            u"Use commas to seperate the items in the list"
        ))

    def select_multiple_choices(indices, lst):
        try:
            return [lst[i] for i in indices]
        except Exception:
            raise UndefinedError("The selected options are not in the list")

    if multiple:
        user_choice = click.prompt(prompt, default=default)
        selected_choice = [x.strip() for x in user_choice.split(',')]
        return select_multiple_choices(selected_choice, choice_map)

    user_choice = click.prompt(
        prompt, type=click.Choice(choices), default=default
    )
    return choice_map[user_choice]


def process_json(user_value):
    try:
        user_dict = json.loads(
            user_value,
            object_pairs_hook=OrderedDict,
        )
    except Exception:
        # Leave it up to click to ask the user again
        raise click.UsageError('Unable to decode to JSON.')

    if not isinstance(user_dict, dict):
        # Leave it up to click to ask the user again
        raise click.UsageError('Requires JSON dict.')

    return user_dict


def read_user_dict(var_name, default_value):
    """Prompt the user to provide a dictionary of data.

    :param str var_name: Variable as specified in the context
    :param default_value: Value that will be returned if no input is provided
    :return: A Python dictionary to use in the context.
    """
    # Please see http://click.pocoo.org/4/api/#click.prompt
    if not isinstance(default_value, dict):
        raise TypeError

    default_display = 'default'

    user_value = click.prompt(
        var_name,
        default=default_display,
        type=click.STRING,
        value_proc=process_json,
    )

    if user_value == default_display:
        # Return the given default w/o any processing
        return default_value
    return user_value


def render_variable(env, raw, cookiecutter_dict):
    """Inside the prompting taken from the cookiecutter.json file, this renders
    the next variable. For example, if a project_name is "Peanut Butter
    Cookie", the repo_name could be be rendered with:

        `{{ cookiecutter.project_name.replace(" ", "_") }}`.

    This is then presented to the user as the default.
    If a raw type such as boolean, integer, or float is entered, then it is
    directly returned
    

    :param Environment env: A Jinja2 Environment object.
    :param str raw: The next value to be prompted for by the user.
    :param dict cookiecutter_dict: The current context as it's gradually
        being populated with variables.
    :return: The rendered value for the default variable.
    """
    if raw is None or raw == "None" or raw == "":
        return None
    elif isinstance(raw, dict):
        return {
            render_variable(env, k, cookiecutter_dict):
                render_variable(env, v, cookiecutter_dict)
            for k, v in raw.items()
        }
    elif isinstance(raw, list):
        return [
            render_variable(env, v, cookiecutter_dict)
            for v in raw
        ]
    elif not isinstance(raw, basestring):
        return raw
    template = env.from_string(raw)

    rendered_template = template.render(cookiecutter=cookiecutter_dict)
    # Support booleans with Jinja Templates
    if str(rendered_template).lower() == "true" or str(rendered_template).lower() == "false":
        return str(rendered_template).lower() == "true"

    return rendered_template


def prompt_choice_for_config(cookiecutter_dict, env, key, options, no_input):
    """Prompt the user which option to choose from the given. Each of the
    possible choices is rendered beforehand.
    """
    rendered_options = [
        render_variable(env, raw, cookiecutter_dict) for raw in options
    ]

    if no_input:
        return rendered_options[0]
    return read_user_choice(key, rendered_options)


ATTRIBUTES = [
    "type",
    "default",
    "visible",
    "description",
    "prompt",
    "hide_input",
    "skip_if",
    "skip_to",
    "validation",
    "choices"
]


def is_multi_list(dic):
    return dic.get("type") == "multilist"


def supported_type(type):
    return type in list(SUPPORTED_TYPES.keys())


def supports_new_format(dic):
    def foreach(keys, f):
        for i in keys:
            if not f(i):
                return False
        return True

    return foreach(dic.keys(), lambda x: x in ATTRIBUTES) and dic.get("default") is not None and supported_type(
        dic.get("type", "string"))


def validate(regex, key, f, max_times_validated=5):
    regex = re.compile(regex) if regex else regex

    def make_validation_func(*args, **kwargs):
        if not regex:
            return f(*args, **kwargs)
        for _ in range(max_times_validated):
            val = f(*args, **kwargs)
            if re.match(regex, val):
                return val
            click.echo("Invalid Pattern for {}. Please follow the format {}".format(key, str(regex)))
        raise UndefinedError

    return make_validation_func


SUPPORTED_TYPES = {
    "multilist": read_user_choice,
    "list": read_user_choice,
    "string": read_user_variable,
    "int": read_user_int,
    "float": read_user_float,
    "bool": read_user_yes_no,
    "password": read_repo_password,
    "json": read_user_dict
}


def prompt_for_config(context, no_input=False):
    """
    Prompts the user to enter new config, using context as a source for the
    field names and sample values.

    :param no_input: Prompt the user at command line for manual configuration?
    """

    cookiecutter_dict = OrderedDict([])
    env = StrictEnvironment(context=context)
    skip_to_variable = None
    for key, raw in iteritems(context[u'cookiecutter']):
        if key.startswith(u'_'):
            cookiecutter_dict[key] = raw
            continue
        if skip_to_variable:
            if skip_to_variable == key:
                skip_to_variable = None
            else:
                cookiecutter_dict[key] = None
                click.echo("skipped " + key)
                continue
        try:
            val = render_variable(env, raw, cookiecutter_dict)
            if not val:  # Conditional formatting.
                cookiecutter_dict[key] = None
            if isinstance(val, list):
                # We are dealing with a choice variable
                cookiecutter_dict[key] = val[0] if no_input else read_user_choice(key, val)
            elif isinstance(val, bool):
                cookiecutter_dict[key] = read_user_yes_no(key + "?", val)
            elif isinstance(val, basestring):
                cookiecutter_dict[key] = val if no_input else read_user_variable(key, val)
            elif isinstance(val, dict):
                cookiecutter_dict[key] = val
                if not supports_new_format(val):
                    if not no_input:
                        cookiecutter_dict[key] = read_user_dict(key, val)
                else:
                    if "description" in val:
                        click.echo(val.get("description"))

                    if val.get("skip_if") is True:
                        click.echo("skipped " + key)
                        cookiecutter_dict[key] = None
                        skip_to = val.get("skip_to")
                        if val.get("skip_to"):
                            click.echo("skipping to " + skip_to)
                            skip_to_variable = skip_to
                        continue

                    if val.get("visible") is False:
                        cookiecutter_dict[key] = val.get("default")
                        continue

                    prompt = val.get("prompt", key)
                    prompt_f = SUPPORTED_TYPES[val.get("type", "string")]
                    default = val.get("default")
                    prompt_f = validate(val.get("validation"), key, prompt_f)
                    if val.get("choices"):
                        choices = val.get("choices")
                        default = choices[0]
                        if no_input:
                            cookiecutter_dict[key] = default
                            continue
                        cookiecutter_dict[key] = prompt_f(prompt, choices, multiple=is_multi_list(val))
                    else:
                        cookiecutter_dict[key] = prompt_f(prompt, default) if not no_input else default
        except UndefinedError as err:
            msg = "Unable to render variable '{}'".format(key)
            raise UndefinedVariableInTemplate(msg, err, context)

    if skip_to_variable:
        click.echo("Processed all variables, but skip_to_variable '{}' was never found.".format(skip_to_variable))

    return cookiecutter_dict
