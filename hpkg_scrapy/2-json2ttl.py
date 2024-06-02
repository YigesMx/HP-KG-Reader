import json
import re

with open('harry_potter_property_processed.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

character_set = set()
group_set = set()
house_set = set()
blood_set = set()

for character in data.keys():
    character_set.add(character)
    character_info = data[character]
    if "学院" in character_info:
        house = character_info["学院"]
        house_set.add(house)
    if "从属" in character_info:
        group_list = character_info["从属"]
        for group in group_list:
            group_set.add(group)
    if "血统" in character_info:
        blood = character_info["血统"]
        blood_set.add(blood)

ttl_file = open('harry_potter.ttl', 'w', encoding='utf-8')

prefix = """@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

@prefix hp: <http://kg.course/harry_potter/> .

@prefix hp_relation: <http://kg.course/harry_potter/关系> .
@prefix hp_class: <http://kg.course/harry_potter/类> .
@prefix hp_character: <http://kg.course/harry_potter/角色> .
@prefix hp_group: <http://kg.course/harry_potter/组织> .
@prefix hp_house: <http://kg.course/harry_potter/学院> .
@prefix hp_blood: <http://kg.course/harry_potter/血统> .

@prefix hp_relation_: <http://kg.course/harry_potter/关系#> .
@prefix hp_character_: <http://kg.course/harry_potter/角色#> .
@prefix hp_group_: <http://kg.course/harry_potter/组织#> .
@prefix hp_house_: <http://kg.course/harry_potter/学院#> .
@prefix hp_blood_: <http://kg.course/harry_potter/血统#> .

"""

ttl_file.write(prefix)

for group in group_set:
    ttl_file.write(f"hp_group_:{group.replace('.', '')}\n\thp_relation_:name \"{group}\" ;\n\ta hp_group: .\n")

for house in house_set:
    ttl_file.write(f"hp_house_:{house.replace('.', '')}\n\thp_relation_:name \"{house}\" ;\n\ta hp_house: .\n")

for blood in blood_set:
    ttl_file.write(f"hp_blood_:{blood.replace('.', '')}\n\thp_relation_:name \"{blood}\" ;\n\ta hp_blood: .\n")

for character in character_set:
    character_info = data[character]
    character_value = re.sub("[() ]", "", character)
    ttl_file.write(f"hp_character_:{character_value}\n\thp_relation_:name \"{character}\" ")
    ttl_file.write(";\n\ta hp_character: ")
    for i, key in enumerate(character_info.keys()):
        if key == "家庭信息":
            family_info = character_info["家庭信息"]
            for family_relation in family_info.keys():
                if type(family_info[family_relation]) == list:
                    for name in family_info[family_relation]:
                        if name in character_set:
                            family_relation = family_relation.replace(" ", "，")
                            family_relation = family_relation.replace("/", "或")
                            ttl_file.write(f";\n\thp_relation_:{family_relation} hp_character_:{name} ")
                else:
                    name = family_info[family_relation]
                    if name in character_set:
                        family_relation = family_relation.replace(" ", "，")
                        family_relation = family_relation.replace("/", "或")
                        ttl_file.write(f";\n\thp_relation_:{family_relation} hp_character_:{name} ")
        elif key == "学院":
            house = character_info["学院"]
            ttl_file.write(f";\n\thp_relation_:学院 hp_house_:{house} ")
        elif key == "血统":
            blood = character_info["血统"]
            ttl_file.write(f";\n\thp_relation_:血统 hp_blood_:{blood} ")
        elif key == "从属":
            group_list = character_info["从属"]
            for group in group_list:
                ttl_file.write(f";\n\thp_relation_:从属 hp_group_:{group.replace('.', '')} ")
        elif key == "职业":
            career_list = character_info["职业"]
            for career in career_list:
                ttl_file.write(f";\n\thp_relation_:职业 \"{career}\" ")
        else:
            ttl_file.write(f";\n\thp_relation_:{key} \"{character_info[key]}\" ")
    ttl_file.write(".\n")
