from typing import Optional, Callable
import time
import math
import json
import re

import gradio as gr

from utils.query import HPDatabase

from utils.llm import LLM_Client
from utils.llm.prompts import summary_from_supplement_prompts, parse_query_from_question_prompts, answer_from_query_result_prompts
from utils.llm.config import config as llm_config

from utils.read import read_selection_js_html_head, btn_update_selected_text_callback_js

from utils.visualization import \
    kg_html_head, load_KG_at_start_js, btn_flush_KG_js, click_btn_flush_kg, click_btn_query_select_text, \
    EChartsGraphData



######### basic utils & data #########

with open("excerpts.txt", "r", encoding="utf-8") as excerpts_file:
    excerpts = excerpts_file.readlines()
    excerpt_string = "".join(excerpts)

selected_text_example = \
"""1. 哈利，斯内普，小天狼星，凤凰社，格兰芬多
2. 哈利&&金妮&&小天狼星&&格兰芬多学院&&凤凰社

q1：哈利和赫敏的关系是什么？
q2：哈利的妻子是谁？
q3：哈利、小天狼星、阿不思·邓布利多以及凤凰社之间的关系是什么
q4：哈利出生信息
q5：哈利波特的作者是谁？
"""

hp_dataset = HPDatabase("localhost", 3030, "hp_kg")
llm_client = LLM_Client(llm_config['token'], llm_config['url'], llm_config['model'])



######### helper functions #########

def load_kg_data():
    with open("kg_data.json", "r", encoding="utf-8") as kg_data_file:
        kg_data = json.load(kg_data_file)
    return json.dumps(kg_data, sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False)



######### Task: "select text" functions #########

def btn_query_select_text_callback(selected_text: str|None, ratio_query_range: bool) -> str:
    if selected_text is None or selected_text == "":
        return json.dumps([], sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False), ''

    # 将 selected_text 按 && 分割
    texts_to_query = selected_text.split("&&")
    # print(texts_to_query)

    raw_queries_results = []
    graph_data = EChartsGraphData()

    # query subjects with name containing selected_text
    for text in texts_to_query:
        query, results = hp_dataset.query_entities_by_name(text, strict=False)
        
        raw_queries_results.append({
            "query": query,
            "results": results
        })

        # print(raw_queries_results)

        for result in results["results"]["bindings"]:
            graph_data.add_node(result["sub"]["value"], result["name"]["value"], result["class"]["value"], stress=True)
        
    subject_length = len(graph_data.graph_data["nodes"])
    # print(subject_length)

    if ratio_query_range > 0:

        for i in range(subject_length):
            # query adjcent entities
            query, results = hp_dataset.query_adjcent_entities_by_subject(graph_data.graph_data["nodes"][i]["url"], subject_format='url')

            raw_queries_results.append({
                "query": query,
                "results": results
            })
            # print(raw_queries_results)

            for result in results["results"]["bindings"]:
                graph_data.add_node(result["obj"]["value"], result["name"]["value"], result["class"]["value"])
                graph_data.add_link(graph_data.graph_data["nodes"][i]["url"], result["obj"]["value"], result["pred"]["value"])

            if ratio_query_range > 1:
                # query pred among adjcent entities
                query, results = hp_dataset.query_pred_among_adjcent_entities(graph_data.graph_data["nodes"][i]["url"], subject_format='url')

                raw_queries_results.append({
                    "query": query,
                    "results": results
                })

                for result in results["results"]["bindings"]:
                    graph_data.add_link(result["obj1"]["value"], result["obj2"]["value"], result["pred3"]["value"])

    else:
        query, results = hp_dataset.query_pred_between_subjects([node["url"] for node in graph_data.graph_data["nodes"]], subject_format='url')

        raw_queries_results.append({
            "query": query,
            "results": results
        })

        for result in results["results"]["bindings"]:
            graph_data.add_link(result["sub1"]["value"], result["sub2"]["value"], result["pred"]["value"])


    for node in graph_data.graph_data["nodes"]:
        query, results = hp_dataset.query_properties_by_subject(node["url"], subject_format='url')

        raw_queries_results.append({
            "query": query,
            "results": results
        })

        node_properties = results["results"]["bindings"]
        graph_data.update_node(node["url"], new_properties=node_properties)
    
    graph_data.calc_node_size()

    # save graph_data to 'kg_data.json'
    with open("kg_data.json", "w", encoding="utf-8") as kg_data_file:
        kg_data_file.write(graph_data.to_json())
    
    summary_supplement = graph_data.generate_summary_supplement()
    
    return json.dumps(raw_queries_results, sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False), summary_supplement



######### Task: "generate summary" functions #########

def summary(summary_supplement: str) -> str:
    if summary_supplement is None or summary_supplement == "":
        return "No Summary Supplment."
    
    # 匹配第一个 “Stress nodes: 123” 处的数字
    num_nodes = int(re.search(r"Stress nodes: (\d+)", summary_supplement).group(1))

    if num_nodes == 0:
        return "No entities selected."
    elif num_nodes < 3:
        prompt = summary_from_supplement_prompts[num_nodes - 1]
    else:
        prompt = summary_from_supplement_prompts[2]

    result = llm_client.query_once(prompt, summary_supplement)
    result = eval(result)

    summary = f"Summaried Nodes Num: {num_nodes}\n Summary: " + result
    
    return summary



######### Task: "Chatbot" functions #########

def add_question_to_chat_history(message, history):
    # for x in message["files"]:
    #     history.append(((x,), None))
    if message["text"] is not None:
        history.append((message["text"], None))
    return gr.MultimodalTextbox(value=None, placeholder="Waiting...", interactive=False), history

def parse_function_output(output_str):
    # 初始化结果字典
    result = {'C': 0, 'E': {}}

    # 使用正则表达式匹配q后面的数字
    q_match = re.search(r'q(\d+)', output_str)
    if q_match:
        result['C'] = int(q_match.group(1))  # 提取并转换q后面的数字
    else:
        raise ValueError("无法找到q后面的数字")

    # 找到E:后的内容
    e_part = output_str.split('E:')[1].strip()
    
    # 使用正则表达式匹配实体和类型
    entity_pattern = re.compile(r'(\w+)\[(\w+)\]')
    matches = entity_pattern.findall(e_part)
    
    # 构建实体和类型的字典
    for name, type_tag in matches:
        result['E'][name] = type_tag

    return result['C'], result['E']

def generate_and_excuete_query(history):

    question = history[-1][0]

    prompt = parse_query_from_question_prompts[0]

    result = llm_client.query_once(prompt, question)

    # result = "C:q1 E:哈利[hp_character], 赫敏[hp_character]"
    # print("LLM's Classification & NER Result:", result)

    c_value, e_dict = parse_function_output(result)
    # print("C Value:", c_value)
    # print("E Dictionary:", e_dict)
    # print("")
    cls_ner_result = f"C Value: {c_value}\nE Dictionary: {e_dict}"

    raw_queries_results = []
    graph_data = EChartsGraphData()

    if c_value == 1:
        subject_list = []
        for key in e_dict:
            query, results = hp_dataset.query_entities_by_name(key, strict=False)
            raw_queries_results.append({
                "query": query,
                "results": results
            })
            for result in results["results"]["bindings"]:
                url = result["sub"]['value']
                subject_list.append(url)
                graph_data.add_node(result["sub"]["value"], result["name"]["value"], result["class"]["value"], stress=True)
        # print(ls)
        query, res = hp_dataset.query_pred_between_subjects(subject_list, subject_format="url")
        raw_queries_results.append({
            "query": query,
            "results": res
        })
        for result in res["results"]["bindings"]:
            graph_data.add_link(result["sub1"]["value"], result["sub2"]["value"], result["pred"]["value"])
        
        for node in graph_data.graph_data["nodes"]:
            blank_properties = []
            graph_data.update_node(node["url"], new_properties=blank_properties)
        
        graph_data.calc_node_size()
        with open("kg_data.json", "w", encoding="utf-8") as kg_data_file:
            kg_data_file.write(graph_data.to_json())
        summary_supplement = graph_data.generate_summary_supplement()

    elif c_value == 2 or c_value == 3:
        subject=[]
        relation=[]
        graph_data = EChartsGraphData()
        for key in e_dict:
            if e_dict[key] == 'hp_character':
                query, results = hp_dataset.query_entities_by_name(key, strict=False)
                raw_queries_results.append({
                    "query": query,
                    "results": results
                })
                for result in results["results"]["bindings"]:
                    subject.append(result["sub"]['value'])
                    graph_data.add_node(result["sub"]["value"], result["name"]["value"], result["class"]["value"], stress=True)
            elif e_dict[key] == 'hp_relation':
                query, results = hp_dataset.query_relation_by_name(key, strict=False)
                raw_queries_results.append({
                    "query": query,
                    "results": results
                })
                # print(results)
                for result in results["results"]["bindings"]:
                    relation.append(result["relation"]['value'])
        query, res = hp_dataset.query_object_by_subject_and_relation(subject, relation)
        raw_queries_results.append({
            "query": query,
            "results": res
        })
        for result in res["results"]["bindings"]:
            graph_data.add_node(result["sub2"]["value"], result["name2"]["value"], result["class2"]["value"], stress=True)
            graph_data.add_link(result["sub1"]["value"], result["sub2"]["value"], result["pred"]["value"])
        
        for node in graph_data.graph_data["nodes"]:
            query, results = hp_dataset.query_properties_by_subject(node["url"], subject_format='url')
            raw_queries_results.append({
                "query": query,
                "results": results
            })
            node_properties = results["results"]["bindings"]
            # print(node_properties)
            filtered_properties = []
            for key in e_dict:
                if e_dict[key] == 'hp_relation':
                    filtered_properties.extend(
                        [prop for prop in node_properties if key in prop['pred']['value']]
                    )
            # print(filtered_properties)
            graph_data.update_node(node["url"], new_properties=filtered_properties)
        graph_data.calc_node_size()
        with open("kg_data.json", "w", encoding="utf-8") as kg_data_file:
            kg_data_file.write(graph_data.to_json())
            
        summary_supplement = graph_data.generate_summary_supplement()
    
    elif c_value == 0:
        query = '&&'.join(e_dict.keys())
        # print(query)
        raw_queries_results, summary_supplement = btn_query_select_text_callback(query, 0)

    else:
        raw_queries_results = []
        summary_supplement = "No Summary Supplement."
        cls_ner_result = "No Classification & NER Result."

    return history, raw_queries_results, summary_supplement, cls_ner_result

def answer_with_supplement(history, summary_supplement):

    question = history[-1][0]
    if len(history) > 1:
        last_history = f"""
        \tlast user question: {history[-2][0]}
        \tlast assistant answer: {history[-2][1]}
        """
    else:
        last_history = "There's no history."
    
    final_question = f"""
    knowledge graph supplement: 
    {summary_supplement}

    last history:
    {last_history}
    
    user question: 
    {question}
    """

    prompt = answer_from_query_result_prompts[0]

    answer_output = llm_client.query_once(prompt, final_question)

    # print("LLM's Answer:", answer_output)
    answer_output = eval(answer_output)

    history[-1][1] = ''

    for character in answer_output:
        history[-1][1] += character
        time.sleep(0.03)
        yield history


######### gradio UI components & actions #########

css = """
<style>
#chat-input .upload-button {
    display: none;
}
</style>
"""
html_head = kg_html_head + read_selection_js_html_head + css
with gr.Blocks(head=html_head, js=load_KG_at_start_js, theme=gr.themes.Default(primary_hue="blue", secondary_hue="sky")) as app:

    gr.Markdown(
    """
    # HP-KG-Reader
    """)

    with gr.Row(variant='panel') as body:

        with gr.Column() as col1:
            gr.Markdown("## 阅读与查询")

            textbox_excerpt = gr.Textbox(value=excerpt_string, lines=25, interactive=False, label="Excerpt")
            textbox_example = gr.Textbox(value=selected_text_example, lines=3, max_lines=3, interactive=False, label="Example")
            textbox_selected_text = gr.Textbox(value=None, placeholder="Select text with shift+s, add text with shift+a", lines=1, max_lines=1, interactive=True, label="Selected Text", elem_id="selected-text")
            textbox_selected_text.blur(fn=None, inputs=[textbox_selected_text], outputs=[], js=click_btn_query_select_text)
            ratio_query_range = gr.Radio(["Self", "Neighbors", "Neighbors Graph"], label="Query Range", value="Self", type="index")
            ratio_query_range.change(fn=None, inputs=[textbox_selected_text], outputs=[], js=click_btn_query_select_text)
            
            # 一个隐藏的 input 用于接收选中的文本，用作 buffer
            gr.HTML("""<div id="selected-text-buffer" style="display: none"><input type="text"></div>""")

            btn_update_selected_text = gr.Button("Update Selected Text", elem_id="btn-update-selected-text", visible=False)
            btn_update_selected_text.click(fn=None, inputs=[], outputs=[textbox_selected_text], js=btn_update_selected_text_callback_js)
            btn_query_select_text = gr.Button("Query & Flush KG", elem_id="btn-query-select-text", variant='primary')
                

        with gr.Column() as col2:
            gr.Markdown("## 查询与结果可视化")

            gr.HTML("""<div id="kg-container" style="height: 600px;"></div>""")

            with gr.Row():
                ratio_layout_option = gr.Radio(["circular", "force"], label="Layout", value="circular")
                ratio_layout_option.change(fn=None, inputs=[], outputs=[], js=click_btn_flush_kg)

                btn_flush_kg = gr.Button("Flush KG", elem_id="btn-flush-kg", variant='primary')

                textbox_kg_data_buffer = gr.Textbox(value=None, visible=False, interactive=False, label="KG Data Buffer", elem_id="kg-data-buffer")
                action_load_kg_data_to_buffer = btn_flush_kg.click(fn=load_kg_data, inputs=[], outputs=[textbox_kg_data_buffer])
                action_load_kg_data_to_buffer.then(fn=None, inputs=[ratio_layout_option, textbox_kg_data_buffer], outputs=[], js=btn_flush_KG_js)
                # btn_flush_kg.click(fn=None, inputs=[ratio_layout_option], outputs=[], js=btn_flush_KG_js)

            with gr.Accordion("Toggle to see Queries & Results", open=True):
                # json_sparql_query_res = gr.JSON(value=None, label="Queries & Results")
                json_sparql_query_res = gr.Textbox(value=None, lines=5, max_lines=10, interactive=False, label="Queries & Results", autoscroll=False, show_copy_button=True)
                # json_sparql_query_res = gr.Code(value=None, language="json", label="Queries & Results", interactive=False, lines=5)
                json_sparql_query_res.change(fn=None, inputs=[], outputs=[], js=click_btn_flush_kg)

                textbox_summary_supplement = gr.Textbox(value=None, lines=5, max_lines=10, interactive=False, label="Summary Supplment", autoscroll=False, show_copy_button=True)
                

        with gr.Column() as col3:
            gr.Markdown("## 总结与问答")

            textbox_summary = gr.Textbox(value=None, placeholder="Summary of query results", lines=5, max_lines=5, interactive=False, label="Summary")
            btn_summary = gr.Button("Generate Summary", elem_id="btn-summary", variant='primary')

            # gr.ChatInterface(reply_chat, multimodal=True)
            chatbot = gr.Chatbot(
                [],
                elem_id="chatbot",
                bubble_full_width=False,
                height=600
            )

            chat_input = gr.MultimodalTextbox(interactive=True, file_types=[], placeholder="Enter Questions...", show_label=False, elem_id="chat-input")

            textbox_cls_ner_result = gr.Textbox(value=None, lines=2, max_lines=5, interactive=False, label="Classification & NER Result", autoscroll=False, show_copy_button=True)

        btn_query_select_text.click(fn=btn_query_select_text_callback, inputs=[textbox_selected_text, ratio_query_range], outputs=[json_sparql_query_res, textbox_summary_supplement])
        btn_summary.click(fn=summary, inputs=[textbox_summary_supplement], outputs=[textbox_summary], js=None) # TODO
        
        action_add_question                 = chat_input.submit(add_question_to_chat_history, [chat_input, chatbot], [chat_input, chatbot])
        action_generate_and_excuete_query   = action_add_question.then(generate_and_excuete_query, [chatbot], [chatbot, json_sparql_query_res, textbox_summary_supplement, textbox_cls_ner_result])
        action_answer_with_supplement       = action_generate_and_excuete_query.then(answer_with_supplement, [chatbot, textbox_summary_supplement], [chatbot])
        action_answer_with_supplement.then(lambda: gr.MultimodalTextbox(placeholder="Enter Questions...", interactive=True), None, [chat_input])

if __name__ == "__main__":
    app.launch(share=False)