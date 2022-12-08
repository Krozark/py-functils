# Built-in
import os
import re
from logging import getLogger
from typing import List, Tuple, Union

# Third-party
import jinja2

logger = getLogger(__name__)


def render_templates(
    template_dir: str,
    path_regex: str,
    context: dict,
    results: int = None,
) -> Union[Tuple[str, str], List[Tuple[str, str]]]:
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))

    res = []
    for file in os.listdir(template_dir):
        if re.match(path_regex, file):
            logger.debug(f"Rendering template {file}.")
            path = os.path.join(template_dir, file)
            tpl = env.get_template(file)
            render = tpl.render(context)
            res.append((path, render))

    if results == 1:
        return res[0]
    elif results is not None:
        return res[:results]
    return res
