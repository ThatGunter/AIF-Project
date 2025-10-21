from settings import * 
from os import walk
from os.path import join
import sys
import os

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def import_image(*path, alpha = True, format = 'png'):
    relative_path = join(*path) + f'.{format}'
    full_path = get_resource_path(relative_path)
    try:
        return pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()
    except FileNotFoundError:
        print(f"Warning: Image file '{full_path}' not found. Creating placeholder.")
        # Create a placeholder surface
        placeholder = pygame.Surface((32, 32))
        placeholder.fill((255, 0, 255))  # Magenta placeholder
        return placeholder.convert_alpha() if alpha else placeholder.convert()

def import_folder(*path):
    frames = []
    relative_path = join(*path)
    full_folder_path = get_resource_path(relative_path)
    try:
        for folder_path, subfolders, image_names in walk(full_folder_path):
            for image_name in sorted(image_names, key = lambda name: int(name.split('.')[0])):
                full_path = join(folder_path, image_name)
                try:
                    frames.append(pygame.image.load(full_path).convert_alpha())
                except FileNotFoundError:
                    print(f"Warning: Image file '{full_path}' not found. Skipping.")
                    continue
    except OSError:
        print(f"Warning: Folder '{full_folder_path}' not found.")
    return frames 

def import_folder_dict(*path):
    frame_dict = {}
    relative_path = join(*path)
    full_folder_path = get_resource_path(relative_path)
    try:
        for folder_path, _, image_names in walk(full_folder_path):
            for image_name in image_names:
                full_path = join(folder_path, image_name)
                try:
                    surface = pygame.image.load(full_path).convert_alpha()
                    frame_dict[image_name.split('.')[0]] = surface
                except FileNotFoundError:
                    print(f"Warning: Image file '{full_path}' not found. Skipping.")
                    continue
    except OSError:
        print(f"Warning: Folder '{full_folder_path}' not found.")
    return frame_dict

def import_sub_folders(*path):
    frame_dict = {}
    relative_path = join(*path)
    full_folder_path = get_resource_path(relative_path)
    try:
        for _, sub_folders, __ in walk(full_folder_path): 
            if sub_folders:
                for sub_folder in sub_folders:
                    frame_dict[sub_folder] = import_folder(*path, sub_folder)
    except OSError:
        print(f"Warning: Folder '{full_folder_path}' not found.")
    return frame_dict