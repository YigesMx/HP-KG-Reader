import json
import re

with open('harry_potter_property.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

house_set = set()
blood_set = set()

for character in data.keys():
    character_info = data[character]
    if character == "哈利·波特":
        character_info["家庭信息"].update({"教父": "小天狼星·布莱克"})
    if "学院" in character_info:
        house = character_info["学院"]
        house = house.replace("学院", "")
        house = house.replace("萊", "莱")
        house_set.add(house)
        house = house + "学院"
        character_info["学院"] = house
    if "血统" in character_info:
        blood = character_info["血统"]
        blood = re.sub(u"\\(.*?\\)", "", blood)
        blood = re.sub(u"（.*?）", "", blood)
        blood = re.sub(" ", "", blood)
        # 去除前后的 //
        blood = re.sub("^//", "", blood)
        if blood == "未知":
            blood = "未知血统"
        if blood == "纯血":
            blood = "纯血统"
        if "媚娃" in blood:
            blood = "混血媚娃"
        blood_set.add(blood)
        character_info["血统"] = blood

from copy import deepcopy
import re

ignore_groups = ["他的同伙", "死亡圣器", "德拉科·马尔福一伙人", "哈利·波特"]

for character in data.keys():
    # if character == "特拉弗斯": print(data[character])
    character_info = data[character]
    if "从属" in character_info:
        group_list = deepcopy(character_info["从属"])

        new_group_list = []

        for group in group_list:

            group = re.sub(u"\\(.*?\\)", "", group)
            group = re.sub(u"（.*?）", "", group)

            group = group.replace(" ", "")
            group = group.replace("\xa0", "")

            if group == "霍格沃茨":
                group = "霍格沃茨魔法学校"
            if group in house_set:
                # if group == "格兰芬多":
                #     print(character)
                group += "学院"
                if "学院" not in character_info:
                    character_info["学院"] = group
                continue
            if "学院" in group:
                print(character)
                character_info["学院"] = house
                continue
            if group == "预言家日报":
                group = "《预言家日报》"
            if group == "英国魔法部":
                # print(character)
                if "魔法部" in new_group_list:
                    continue
                group = "魔法部"
            if group in ignore_groups:
                continue
        
            new_group_list.append(group)

        character_info["从属"] = new_group_list

with open('harry_potter_property_processed.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=1)
