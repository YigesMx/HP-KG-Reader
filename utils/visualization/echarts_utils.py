from typing import Optional
import math
import json


class EChartsGraphData(object):
    """
    graph_data = {
        "nodes": [
            {
                "id": str, # = index
                "url": str,
                "name": str,
                "value": int, # 图节点度数
                "symbolSize": float, # = log(value+1)
                "category": int # 类别
                "properties": json # 属性
            },
        ],
        "nodes_map": {
            url: id
        },

        "links": [
            {
                "source": int, # = index
                "target": int, # = index
                "value": str # 关系 url
                "source_name": str,
                "target_name": str,
            }
        ],
        "links_map": {
            (src_index, tgt_index): link_index
        },

        "catagories": [
            {
                "id": str, # = index
                "url": str,
                "name": "catagory_name"
            }
        ],
        "catagories_map": {
            url : id
        }
    }
    """
    def __init__(self):
        self.graph_data = {
            "nodes": [],
            "nodes_map": {},
            "links": [],
            "links_map": {},
            "catagories": [],
            "catagories_map": {}
        }
    
    def add_node(self, url: str, name: str, catagory: str, properties: Optional[dict] = None, stress: Optional[bool] = False):
        if catagory not in self.graph_data["catagories_map"]:
            self.graph_data["catagories"].append({
                "id": str(len(self.graph_data["catagories"])),
                "url": catagory,
                "name": catagory.split("/")[-1]
            })
            self.graph_data["catagories_map"][catagory] = len(self.graph_data["catagories"]) - 1
        
        if url not in self.graph_data["nodes_map"]:
            self.graph_data["nodes"].append({
                "id": str(len(self.graph_data["nodes"])),
                "url": url,
                "name": name,
                "value": 0,
                "symbolSize": 0,
                "category": self.graph_data["catagories_map"][catagory],
                "properties": properties,
                "stress": stress
            })
            self.graph_data["nodes_map"][url] = len(self.graph_data["nodes"]) - 1
    
    def update_node(self, url: str, new_name: str = None, new_catagory: str = None, new_properties: Optional[dict] = None, new_stress: Optional[bool] = None):
        if url in self.graph_data["nodes_map"]:
            node_index = self.graph_data["nodes_map"][url]
            if new_name is not None:
                self.graph_data["nodes"][node_index]["name"] = new_name
            if new_catagory is not None:
                if new_catagory not in self.graph_data["catagories_map"]:
                    self.graph_data["catagories"].append({
                        "id": str(len(self.graph_data["catagories"])),
                        "url": new_catagory,
                        "name": new_catagory.split("/")[-1]
                    })
                    self.graph_data["catagories_map"][new_catagory] = len(self.graph_data["catagories"]) - 1
                self.graph_data["nodes"][node_index]["category"] = self.graph_data["catagories_map"][new_catagory]
            if new_properties is not None:
                self.graph_data["nodes"][node_index]["properties"] = new_properties
            if new_stress is not None:
                self.graph_data["nodes"][node_index]["stress"] = new_stress
        else:
            raise ValueError(f"Node with url {url} not found.")
    
    def add_link(self, source_url: str, target_url: str, value: str):
        if (source_url, target_url) not in self.graph_data["links_map"]:
            source_id = self.graph_data["nodes_map"].get(source_url, None)
            target_id = self.graph_data["nodes_map"].get(target_url, None)
            self.graph_data["links"].append({
                "source": source_id,
                "source_name": self.graph_data["nodes"][source_id]["name"],
                "target": target_id,
                "target_name": self.graph_data["nodes"][target_id]["name"],
                "value": value
            })
            self.graph_data["links_map"][(source_url, target_url)] = len(self.graph_data["links"]) - 1

            # update degree (node value)
            self.graph_data["nodes"][source_id]["value"] = self.graph_data["nodes"][source_id].get("value", 0) + 1
            self.graph_data["nodes"][target_id]["value"] = self.graph_data["nodes"][target_id].get("value", 0) + 1
        
    def update_link(self, source_url: str, target_url: str, new_value: str):
        if (source_url, target_url) in self.graph_data["links_map"]:
            link_index = self.graph_data["links_map"][(source_url, target_url)]
            self.graph_data["links"][link_index]["value"] = new_value
            # update_name
            source_id = self.graph_data["nodes_map"].get(source_url, None)
            target_id = self.graph_data["nodes_map"].get(target_url, None)
            self.graph_data["links"][link_index]["source_name"] = self.graph_data["nodes"][source_id]["name"]
            self.graph_data["links"][link_index]["target_name"] = self.graph_data["nodes"][target_id]["name"]
        else:
            raise ValueError(f"Link with source {source_url} and target {target_url} not found.")
    
    def calc_node_size(self):
        basic = 10 * ( 1 / math.sqrt(max(len(self.graph_data["nodes"]), 3)) ) + 5
        for node in self.graph_data["nodes"]:
            inflation = math.log(node["value"] + math.e)
            node["symbolSize"] = basic * inflation

            if node["stress"]:
                # node["symbolSize"] = node["symbolSize"] * 1.5
                # node["itemStyle"] = {
                #     "borderColor": "red",
                # }
                node["symbol"] = 'roundRect'

    def to_json(self, exclude_map: bool = True):
        if exclude_map:
            return json.dumps({
                "nodes": self.graph_data["nodes"],
                "links": self.graph_data["links"],
                "categories": self.graph_data["catagories"]
            }, sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False)
        else:
            return json.dumps(self.graph_data, sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False)
    
    def generate_summary_supplement(self):
        summary_supplement: str = ""
        stress_nodes = []
        stress_nodes_id = []
        for node in self.graph_data["nodes"]:
            if node["stress"]:
                stress_nodes.append(node)
                stress_nodes_id.append(int(node["id"]))
        
        summary_supplement = f"Stress nodes: {len(stress_nodes)}\n"

        for node in stress_nodes:
            # name
            summary_supplement += f"{node['name']}:\n"
            # class
            summary_supplement += f"\tclass: {self.graph_data['catagories'][node['category']]['name']}\n"
            # properties
            if node["properties"] and not(len(node["properties"]) == 1 and node["properties"][0]["pred"]["value"].split("#")[-1] == "name"):
                summary_supplement += f"\tproperties:\n"
                for p in node["properties"]:
                    # except name
                    if p["pred"]["value"].split("#")[-1] == "name":
                        continue
                    pred = p["pred"]["value"].split("#")[-1]
                    obj = p["obj"]["value"]
                    summary_supplement += f"\t\t{pred}: {obj}\n"

            # relations
            relations_tmp = []
            for link in self.graph_data["links"]:
                if (link["source"] == int(node["id"]) and link["target"] in stress_nodes_id) or \
                   (link["target"] == int(node["id"]) and link["source"] in stress_nodes_id):
                    relations_tmp.append(link)

            if len(relations_tmp) > 0:
                summary_supplement += f"\trelations:\n"
                for link in relations_tmp:
                    if (link["source"] == int(node["id"]) and link["target"] in stress_nodes_id):
                        value = link["value"].split("#")[-1]
                        summary_supplement += f"\t\t--[{value}]-> {link['target_name']}\n"
                    elif (link["target"] == int(node["id"]) and link["source"] in stress_nodes_id):
                        value = link["value"].split("#")[-1]
                        summary_supplement += f"\t\t<-[{value}]-- {link['source_name']}\n"
            

        
        return summary_supplement
                

    def clear(self):
        self.graph_data = {
            "nodes": [],
            "nodes_map": {},
            "links": [],
            "links_map": {},
            "catagories": [],
            "catagories_map": {}
        }

kg_html_head = """
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.min.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>

<!-- Uncomment this line if you want to dataTool extension
<script type="text/javascript" src="https://registry.npmmirror.com/echarts/5.5.0/files/dist/extension/dataTool.min.js"></script>
-->
<!-- Uncomment this line if you want to use gl extension
<script type="text/javascript" src="https://registry.npmmirror.com/echarts-gl/2/files/dist/echarts-gl.min.js"></script>
-->
<!-- Uncomment this line if you want to echarts-stat extension
<script type="text/javascript" src="https://registry.npmmirror.com/echarts-stat/latest/files/dist/ecStat.min.js"></script>
-->
<!-- Uncomment this line if you want to use map
<script type="text/javascript" src="https://registry.npmmirror.com/echarts/4.9.0/files/map/js/china.js"></script>
<script type="text/javascript" src="https://registry.npmmirror.com/echarts/4.9.0/files/map/js/world.js"></script>
-->
<!-- Uncomment these two lines if you want to use bmap extension
<script type="text/javascript" src="https://api.map.baidu.com/api?v=3.0&ak=YOUR_API_KEY"></script>
<script type="text/javascript" src="https://registry.npmmirror.com/echarts/5.5.0/files/dist/extension/bmap.min.js"></script>
-->

<script type="text/javascript">

function flush_KG(layout='circular', graph_data_str='{}') {

    console.log("flushing_KG...");
    console.log(graph_data_str);
    
    var dom = document.getElementById('kg-container');

    var myChart = echarts.init(dom, null, {
        renderer: 'canvas',
        useDirtyRect: false
    });
    var option;

    myChart.showLoading();

    graph = $.parseJSON(graph_data_str);

    console.log(graph);

    if (graph.hasOwnProperty('nodes')) {
        myChart.hideLoading();
        graph.nodes.forEach(function (node) {
            node.label = {
                show: node.symbolSize > 4
            };
        });

        option = {
            title: {
                text: 'Harry Potter',
                subtext: 'Default layout',
                top: 'bottom',
                left: 'right'
            },
            tooltip: {},
            legend: [
            {
                // selectedMode: 'single',
                data: graph.categories.map(function (a) {
                    return a.name;
                })
            }
            ],
            animationDuration: 1500,
            animationEasingUpdate: 'quinticInOut',
            series: [
            {
                name: 'Harry Potter',
                type: 'graph',
                legendHoverLink: false,
                //layout: 'force',
                layout: layout,
                data: graph.nodes,
                links: graph.links,
                categories: graph.categories,
                roam: true,
                zoom: 0.7,
                label: {
                    show: true,
                    position: 'right',
                    formatter: '{b}'
                },
                lineStyle: {
                    color: 'target',
                    curveness: 0.1
                },
                emphasis: {
                    focus: 'adjacency',
                    lineStyle: {
                        width: 6
                    }
                },
                force: {
                    // initLayout: 'circular'
                    gravity: 0.6,
                    repulsion: 3000,
                    edgeLength: 25
                },
                circular: {
                    rotateLabel: true
                },
                tooltip: {
                    formatter: function (param) {
                        if (param.dataType === 'node') {
                            s = '<bold>' + param.data.name + '</bold><br/>';
                            param.data.properties.forEach(function (p) {
                                pred = p.pred.value.split('#')[1];
                                // skip name

                                if (pred === 'name') {
                                    return;
                                }

                                obj = p.obj.value;
                                s += pred + ': ' + obj + '<br>';
                            });
                            return s;
                        } else if (param.dataType === 'edge') {
                            s = param.data.source_name + ' --[' + param.data.value.split('#')[1] + ']-- ' + param.data.target_name + '<br/>';
                            return s;
                        }
                    }
                }
            }
            ]
        };

        myChart.setOption(option);
    }

    /*$.getJSON('http://127.0.0.1:5500/kg_data.json', function (graph) {
        
    });*/

    if (option && typeof option === 'object') {
        myChart.setOption(option);
    }

    window.addEventListener('resize', myChart.resize);
}

</script>

"""