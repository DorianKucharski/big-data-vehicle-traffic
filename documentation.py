import pdoc
from pathlib import Path
import os

path = "WebApp/templates/docs/"
modules = ['Data', 'Publisher', 'Subscriber', 'WebApp']
main_modules = modules + ["WebApp/api", "WebApp/vehicletraffic", "WebApp/webapp"]
context = pdoc.Context()

modules = [pdoc.Module(mod, context=context, skip_errors=True) for mod in modules]
pdoc.link_inheritance(context)


def recursive_htmls(mod):
    yield mod.name, mod.html()
    for submod in mod.submodules():
        yield from recursive_htmls(submod)


for mod in modules:
    module_path = os.path.join(path, mod.name)
    for module_name, html in recursive_htmls(mod):

        module_name = module_name.replace(".", "/")
        if module_name in main_modules:
            Path(path + module_name).mkdir(parents=True, exist_ok=True)
            module_name = module_name + "/index"

        with open(path + module_name + ".html", "w", encoding='utf-8') as file:
            file.write(html)
