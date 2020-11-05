import argparse
import os
import sys

import bpy

""" 
    blender test.blend -b -P rendering.py -- --r 512 --m normalmap --o ./normalmap.png
    blender test.blend -b -P rendering.py -- --r 512 --m heightmap --o ./heightmap.png
"""

dirpath = os.path.dirname(os.path.abspath(__file__))


def render_heightmap(img_resolution: int, out_path: str) -> str:
    bpy.context.window.scene = bpy.data.scenes["Scene"]
    bpy.ops.object.select_all(action='DESELECT')

    # Объекты, объём которых запекаем
    objs_collection = bpy.data.collections["objects_for_baking"].all_objects

    # Материал, содержащий ноды Material Output с именами
    # heightmap_out и normalmap_out
    out_mat = bpy.data.materials["Heightmap_and_Normalmap"]

    # Активируем Material Output для карты нормалей
    out_mat.node_tree.nodes.active = out_mat.node_tree.nodes["heightmap_out"]

    bpy.context.scene.render.filepath = out_path

    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.scene.view_settings.view_transform = 'Standard'
    bpy.context.scene.render.image_settings.color_mode = 'BW'

    bpy.context.scene.render.resolution_y = img_resolution
    bpy.context.scene.render.resolution_x = img_resolution

    bpy.data.objects["bakescreen"].hide_render = True

    bpy.ops.render.render('INVOKE_DEFAULT', write_still=True)
    return out_path


def bake_normalmap(img_resolution: int, out_path: str) -> str:
    """ Запекает карту нормалей в режиме selected to active.
        Предпологается, что существует объект с названием `bakescreen`
        и с одноимённым материалом. На этот объект запекаются нормали
        с объекта `object_name`. """
    bpy.context.window.scene = bpy.data.scenes["Scene"]
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.render.engine = 'CYCLES'

    # Объект, на который запекаем
    bakescreen_obj = bpy.data.objects["bakescreen"]

    # Объекты, объём которых запекаем
    objs_collection = bpy.data.collections["objects_for_baking"].all_objects

    # Материал, содержащий ноды Material Output с именами
    # heightmap_out и normalmap_out
    out_mat = bpy.data.materials["Heightmap_and_Normalmap"]

    # Активируем Material Output для карты нормалей
    out_mat.node_tree.nodes.active = out_mat.node_tree.nodes["normalmap_out"]

    # Выделяем все объекты, а bakescreen делаем активным
    for obj in objs_collection:
        obj.select_set(True)

    bakescreen_obj.select_set(True)
    bpy.context.view_layer.objects.active = bakescreen_obj

    # Создаём картинку для запекания
    bake_img = bpy.data.images.new('bake', img_resolution, img_resolution)

    mat = bakescreen_obj.material_slots[0].material

    # Создаём нод с картинкой
    nodes = mat.node_tree.nodes
    texture_node = nodes.new('ShaderNodeTexImage')
    # texture_node.name = 'normalmap_bake_node'
    texture_node.select = True
    nodes.active = texture_node
    texture_node.image = bake_img

    bpy.context.scene.render.image_settings.color_mode = 'RGB'

    # Selected to active
    bpy.context.scene.render.bake.use_selected_to_active = True

    bpy.ops.object.bake(type='NORMAL', save_mode='EXTERNAL')
    bake_img.save_render(filepath=out_path)
    return out_path


parser = argparse.ArgumentParser()
parser.add_argument("--resolution", "--r", help="output image side in pixels")
parser.add_argument("--out", "--o", help="Output file path")
parser.add_argument("--map", "--m", help="heightmap or normalmap")

args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])

if args.map == "heightmap":
    render_heightmap(int(args.resolution), os.path.abspath(args.out))
else:
    bake_normalmap(int(args.resolution), os.path.abspath(args.out))
