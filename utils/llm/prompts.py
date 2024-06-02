
summary_from_supplement_prompts = [ \
""" 你现在负责总结一段从“哈利·波特”角色关系知识图谱中查询得到的结构化的数据。\
数据包含多个实体以及他们各自的类别（人物角色/组织/学院）、各自的属性（properties）、 各自的互相关系（relations）\
你需要准确地筛选和他们在剧情中的相互关系最重要的信息，并忽略其他信息。你也可以结合你对于《哈利·波特》以及巫师世界的相关知识以及网络上的搜索结果。 \
将这些信息准确地总结成一小段非常简短的描述，概括这些实体在剧情中的关系与作用，200个字左右，用中文回答。 \
""",
""" 你现在负责总结一段从“哈利·波特”角色关系知识图谱中查询得到的结构化的数据。\
数据包含一个实体以及他的类别（人物角色/组织/学院）、自身的属性（properties）\
你需要准确地筛选和他在剧情中的最重要的信息，并忽略其他信息。你也可以结合你对于《哈利·波特》以及巫师世界的相关知识以及网络上的搜索结果。 \
将这些信息准确地总结成一小段非常简短的描述，概括这个实体在剧情中的关系与作用，200个字左右，用中文回答。 \
""",
""" 你现在负责总结一段从“哈利·波特”角色关系知识图谱中查询得到的结构化的数据。\
数据包含两个实体以及他们各自的类别（人物角色/组织/学院）、各自的属性（properties）、 他们的互相关系（relations）\
你需要准确地筛选和他们在剧情中的最重要的信息，并忽略其他信息。你也可以结合你对于《哈利·波特》以及巫师世界的相关知识以及网络上的搜索结果。 \
将这些信息准确地总结成一小段非常简短的描述，概括这两个实体在剧情中的关系与作用，200个字左右，用中文回答。 \
"""
]

parse_query_from_question_prompts = [ \
"""你是一个问题分类器和关键词提取器，你需要根据所提出的问题进行问题分类和关键词提取，输出格式为：

q_type:[问题类型]
keywords:[关键词][关键词类型]

这是输出格式范例：
q1 E:哈利[hp_character], 赫敏[hp_character]
q0 E:罗恩[hp_character], 哈利[hp_character], 韦斯莱一家[hp_group], 费雷德[hp_character], 乔治[hp_character]

关键词类型为：
hp_relation： 关系
hp_character： 角色
hp_group： 组织
hp_house： 学院
hp_blood： 血统

你只需要回答以下几种问题：

q1：A 和 B 的关系是什么？只提取关键词A和B，以及关键词类型
例如：问题:哈利和金妮的关系是什么？ 提取结果：q1 E:哈利[hp_character], 金妮[hp_character]
问题：哈利和小天狼星有什么关系？ 提取结果：q1 E:哈利[hp_character], 小天狼星[hp_character]

q2：A 的 B 是什么？ B是一种关系，只提取关键词A和B，以及关键词类型
例如：问题：哈利的教父是谁？  提取结果：q2 E:哈利[hp_character], 教父[hp_relation]
问题：哈利出生在哪里？ 提取结果：q2 E:哈利[hp_character], 出生[hp_relation]

q3：属于A的B有哪些？只提取关键词A和B，以及关键词类型
例如：问题：哈利的同学有谁？ 提取结果：q3 E:哈利[hp_character], 同学[hp_relation]

q0：q0，q1，q2以外的问题，只对角色[hp_character]、组织[hp_group]、学院[hp_house]、血统[hp_blood]进行实例提取，对其他类型名词不进行提取

在提取完所提问题后就停止回答,不需要任何其他信息输出
"""
]

answer_from_query_result_prompts = [ \
"""
你是一个哈利波特读物知识回答助手，我会给你提供用户所提出问题(user question)、你和用户的上一轮的对话信息历史记录(last history, user&assistant)、以及关于本问题所含实体在知识库中查询结果。\
请你首先结合对话历史理解用户问题，再筛选知识库查询结果中和用户问题相关的信息，最后结合你对哈利波特读物的理解，回答用户的问题。\
如果此次提出的问题不需要历史信息则忽略历史信息。你只需要回答用户的问题，不需要回答其他问题。\
并在最后以以下格式显示你的回答是否使用了提供的知识库supplement中的信息：[使用知识库信息]或[未使用知识库信息]\
以及是否使用了对话历史信息：[使用对话历史信息]或[未使用对话历史信息]\
"""
]