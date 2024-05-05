# How to use:
# Set first line to be the title of the devlog (end with a ^ if it's important).
# Then from the second line onward, put the content of the devlog.
# The third last line should be the date of the announcement.
# The second last line should be the game's id in the itch link. (eg. cat-called-cleo)
# The last line should be the games display name. (eg. A Cat Called Cleo)
# Always run this script when you have the repository folder open in VS Code, doesn't work otherwise.
# This will also have some inaccuracies (for example * and # may confuse it).
# You can also use \ as an escape character, meaning whatever character comes after it will be interpreted as pure text
# Characters that might need escaping include:
# \ * # [ ]

import os
import sys

is_list = False

def process_line(line: str) -> str:
  global is_list

  new_line = ""

  escaped = False
  is_bold = False
  is_italic = False
  asterisk_count = 0
  is_exclamation = False
  is_image = False
  is_link_text = False
  link_text = ""
  is_link_address = False
  link_address = ""

  for i in line:
    if escaped:
      new_line += i
      escaped = False
      continue

    if i == "\\":
      escaped = True
      continue

    if i == "*":
      asterisk_count += 1
      continue

    if asterisk_count > 0:
      if is_exclamation:
        new_line += "!"
        is_exclamation = False
      if asterisk_count == 1 or asterisk_count >= 3:
        if is_italic:
          new_line += "</i>"
          is_italic = False
        else:
          new_line += "<i>"
          is_italic = True
      if asterisk_count >= 2:
        if is_bold:
          new_line += "</b>"
          is_bold = False
        else:
          new_line += "<b>"
          is_bold = True
      asterisk_count = 0

    if i == "\n":
      if is_exclamation:
        new_line += "!"
        is_exclamation = False
      new_line += "<br>\n"
      continue

    if i == "!":
      is_exclamation = True
      continue
    
    if i == "[":
      if is_exclamation:
        is_exclamation = False
        is_image = True
      is_link_text = True
      link_text = ""
      continue
    if i == "]" and is_link_text:
      is_link_text = False
      continue
    if i == "(" and is_link_text != "":
      is_link_address = True
      link_address = ""
      continue
    if i == ")" and is_link_address:
      is_link_address = False
      if is_image:
        extension = link_address.split(".")[len(link_address.split(".")) - 1]
        if extension == "mov" or extension == "mp4":
          new_line += '''<video controls>
  <source src="''' + link_address + '''" type="video/mp4">
  Your browser does not support the video tag.
</video>'''
        else:
          new_line += '<img src="' + link_address + '" alt="' + link_text + '">'
        is_image = False
      else:
        new_line += '<a href="' + link_address + '">' + link_text + '</a>'
      link_address = ""
      link_text = ""
      continue
    if is_link_text:
      link_text += i
      continue
    if is_link_address:
      link_address += i
      continue

    # Otherwise
    if is_exclamation:
      new_line += "!"
      is_exclamation = False
    new_line += i

  if new_line.startswith("- "):
    new_line = new_line.removeprefix("- ")
    new_line = "<li>" + new_line
    new_line = new_line.removesuffix("<br>\n")
    new_line += "</li>\n" 
    if not is_list:
      new_line = "<ul>\n"
      is_list = True
  elif is_list:
    new_line = "</ul>" + new_line

  if new_line.startswith("#"):
    hashtags = new_line.split(" ")[0]
    num = hashtags.count("#")
    new_line = new_line.removeprefix(hashtags + " ")
    new_line = "<h" + str(num) + ">" + new_line
    new_line = new_line.removesuffix("<br>\n")
    new_line += "</h" + str(num) + "><br>\n" 

  return new_line

file_name = input("Enter the file to convert (no extension) > ")
delete = input("Delete .md file after .html file is created (y/n)? > ").lower() == "y"
full_path = os.path.realpath(os.path.join(os.getcwd(), "devlogs", file_name + ".md"))

if not os.path.isfile(full_path):
  print("File not found.")
  sys.exit()

file = open(full_path, "r")
index = 0

title = ""
important = False
date = ""
game_id = ""
game_name = ""
content = []

lines = file.readlines()
for line in lines:
  if index == 0:
    title = line.replace("\n", "")
    if title.endswith("^"):
      important = True
      title = title.removesuffix("^")
  elif index == len(lines) - 3:
    date = line.replace("\n", "")
  elif index == len(lines) - 2:
    game_id = line.replace("\n", "")
  elif index == len(lines) - 1:
    game_name = line.replace("\n", "")
  else:
    content.append(process_line(line))
  index += 1
file.close()

if delete:
  os.remove(full_path)

content_text = ""
for line in content:
  content_text += line

file = open(os.path.realpath(os.path.join(os.getcwd(), "devlogs", "devlog_template.html")), "r")

devlog_file_text = file.read()
devlog_file_text = devlog_file_text.replace("TITLE", title)
devlog_file_text = devlog_file_text.replace("IMPORTANT", "yellow" if important else "white")
devlog_file_text = devlog_file_text.replace("DATE", date)
devlog_file_text = devlog_file_text.replace("TEXT", content_text)
devlog_file_text = devlog_file_text.replace("GAME_ID", game_id)
devlog_file_text = devlog_file_text.replace("GAME_NAME", game_name)
file.close()

file = open(os.path.realpath(os.path.join(os.getcwd(), "devlogs", file_name + ".html")), "w")
file.write(devlog_file_text)
file.close()

devlog_select = os.path.realpath(os.path.join(os.getcwd(), "devlog_select.html"))
file = open(devlog_select, "r")
devlog_item_text = '''<!-- NEXT DEVLOG -->

      <div class="devlog-container">
        <a href="devlogs/''' + file_name + '''.html" class="game-button">
          <div>
            <img src="assets/game_icons/''' + game_id + '''.png">
            <h1 style="color: ''' + ('yellow' if important else "white") + ';">' + title + '''</h1>
          </div>
        </a>
        <h5>''' + date + '''</h5>
      </div>'''

new_text = file.read().replace("<!-- NEXT DEVLOG -->", devlog_item_text)
file.close()
file = open(devlog_select, "w")
file.write(new_text)
file.close()

print("Devlog created successfully.")