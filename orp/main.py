import argparse
import os
import platform
import re
import shutil
import sys
from typing import List, Optional

CMDS = [
    ("blender \"{}\" -b -P \"{}\" -- --r {} --m normalmap --o \"{}\"", "n"),
    ("blender \"{}\" -b -P \"{}\" -- --r {} --m heightmap --o \"{}\"", "h")
]

DIRPATH = os.path.dirname(os.path.abspath(__file__))

APP_NAME = "orp"
CONTEXT_MENU_TEXT = "Render normalmap and heightmap ({res})"


def _get_blender_templates_paths() -> List[str]:
    """ Возвращает пути к папкам
        `Blender/<version>/scripts/startup/bl_app_templates_system`. """
    paths = os.getenv("path").split(";")
    blender_path = None
    for p in paths:
        if "Blender" in p:
            blender_path = p
            break

    if blender_path is None:
        print("Blender is not added to PATH")
        return []

    result = []
    dirs = os.listdir(blender_path)
    version = None
    for dirname in dirs:
        found = re.findall("\\d+\\.\\d+", dirname)
        if len(found) == 1:
            result.append(
                os.path.join(blender_path, found[0], "scripts", "startup",
                             "bl_app_templates_system")
            )

    return result


def install_blender_template():
    """ Добавляет шаблон нового файла Blender,
        настроенный для рендеринга карт нормалей и высот. """
    for blender_path in _get_blender_templates_paths():
        try:
            src = os.path.join(DIRPATH, "blender_template")
            dst = os.path.join(blender_path)

            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)
                print("Installed template in", blender_path)
        except FileExistsError:
            pass
    print("OK")


def remove_blender_template():
    """ Удаляет шаблон нового файла Blender """
    for blender_path in _get_blender_templates_paths():
        try:
            p = os.path.join(blender_path,
                             "Minecraft resourcepack normal mapping")
            shutil.rmtree(p)
            print("Removed", p)
        except FileNotFoundError:
            pass
    print("OK")


def add_to_context(resolutions: List[int]):
    """ Добавляет в контекстное меню при клике по
        файлу `.blend` команды для рендеринга его
        в указанных разрешениях. 

        Если `resolutions == []`, команды будут убраны
        из контекстного меню."""
    path = os.path.join(DIRPATH, "reg", "context.reg")

    with open(path, "w", encoding="utf-8") as f:
        text = (
            "Windows Registry Editor Version 5.00\n"
            "\n"
        )

        for res in resolutions:
            text += (
                "[HKEY_CLASSES_ROOT\SystemFileAssociations\.blend\shell\{}\command]\n"
                "@=\"\\\"{}\\\" -m {} --render \\\"%1\\\" --res {}\""
                "\n"
            ).format(
                CONTEXT_MENU_TEXT.format(res=res),
                sys.executable.replace("\\", "\\\\"),
                APP_NAME,
                res
            )

        if len(resolutions) == 0:
            text += "[-HKEY_CLASSES_ROOT\SystemFileAssociations\.blend\shell]"

        print(text)
        f.write(text)

    if platform.system() == "Windows":
        os.system("explorer \"{}\"".format(path))
        print("OK")
    else:
        print("Available on Windows only.")


def render(path: str, resolution: int):
    """ Рендерит файл по пути `path` с разрешением `resolution`.
        На выходе получается 2 текстуры - карта нормалей и карта высот.
        Они имеют окончания в названии _n и _h соответственно, и 
        сохраняются рядом с blend файлом. """
    filepath = os.path.abspath(path.strip("\""))
    folder = os.path.dirname(filepath)

    filename, _ = os.path.basename(filepath).rsplit(".", 1)
    rendering_py_path = os.path.join(DIRPATH, "rendering.py")

    for cmd, suff in CMDS:
        command = cmd.format(filepath,
                             rendering_py_path,
                             resolution,
                             os.path.join(folder, filename+"_"+suff+".png"))
        os.system(command)


parser = argparse.ArgumentParser()

render_group = parser.add_argument_group()
render_group.add_argument("--render", help="Render blend file")
render_group.add_argument("--res", default=512, type=int,
                          help="Render resolution")

context_group = parser.add_argument_group()
context_group.add_argument("--context", nargs="*")

install_template_group = parser.add_argument_group()
install_template_group.add_argument("--install-template",
                                    action="store_true")

remove_template_group = parser.add_argument_group()
remove_template_group.add_argument("--remove-template",
                                   action="store_true")


def main():
    args = parser.parse_args()

    if args.render:
        render(os.path.abspath(args.render), args.res)
    elif args.context is not None:
        add_to_context([int(r) for r in args.context])
    elif args.install_template:
        install_blender_template()
    elif args.remove_template:
        remove_blender_template()
