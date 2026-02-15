# dependencies import
import asyncio
import json

# noinspection PyPackageRequirements
import os

import discord

from html2image import Html2Image
from PIL import Image


def update_json_file_from_dict(json_file: str, json_dict: dict) -> None:
    with open(json_file, "w", encoding="utf8") as f:
        f.seek(0)
        json.dump(json_dict, f, indent=4)


def get_dict_from_json_file(json_file: str) -> dict:
    with open(json_file, "r+", encoding="utf8") as f:
        data = json.load(f)
        return data


def create_new_member_welcome_card(member: discord.Member):
    # constants
    from globals import COMPUTER_OS

    print(member.avatar.url)

    # Oversized image we crop
    hti = Html2Image(size=(1920, 1200))
    #hti.load_file('background.png')
    hti.load_file('1.png')
    hti.load_file('2.png')
    hti.load_file('5.png')
    hti.load_file('6.png')

    # sur les systèmes utilisant Unix, on doit désactiver le GUI du navigateur et cacher les scrollbars
    if COMPUTER_OS.casefold() == "UNIX".casefold():
        hti.browser.flags = ["--no-sandbox", "--hide-scrollbars"]

    with open("member_join.html") as f:
        file_content = f.read()
        file_content = file_content.replace("{NICKNAME}", member.name) \
            .replace("{AVATAR_LINK}", member.avatar.url if member.avatar is not None else None)

        new_file = open(f"{member.id}_card.html", "w")
        new_file.write(file_content)
        new_file.close()

    hti.screenshot(html_file=f"{member.id}_card.html",
                   css_file="style_member_join.css",
                   save_as='page.png')

    # Remove white background
    img = Image.open("page.png")
    img = img.convert("RGBA")

    datas = img.getdata()

    new_data = []

    for item in datas:
        if item[0] == 54 and item[1] == 57 and item[2] == 63:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    img.putdata(new_data)
    img.save("./page.png", "PNG")

    # Get the content bounds.
    content = img.getbbox()

    # Crop the image.
    img = img.crop(content)

    # Save the image.
    img.save("./page.png", "PNG")

    file = discord.File("page.png")

    return file


def check(msg: discord.Message):
    """checks a message to be sure it is not the bot nor a user command"""
    return not msg.content.startswith("=") and not msg.author.bot
