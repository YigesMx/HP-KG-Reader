import os
import sys
from typing import List

import json
import numpy
import pandas

import requests

class JenaFusekiDatabase(object):

    def __init__(self, host, port, dataset, prefix, http='http'):
        self.http = http
        self.host = host
        self.port = port
        self.dataset = dataset
        self.url = f"{http}://{host}:{port}/{dataset}/"

        self.prefix = prefix

        pass

    def query_with_prefix(self, query: str)->dict:
        response = requests.post(
            self.url + 'query',
            data={'query': self.prefix + query},
            headers={'Accept': 'application/json'}
        )
        return response.json()

    @staticmethod
    def parse_pd_table(jena_fuseki_result_json: dict)->pandas.DataFrame:
        json_data = jena_fuseki_result_json
        columns = json_data['head']['vars']
        rows = json_data['results']['bindings']
        data = []
        for row in rows:
            data.append([row.get(column, {}).get('value', None) for column in columns])
        return pandas.DataFrame(data, columns=columns)
    

class HPDatabase(JenaFusekiDatabase):

    def __init__(self, host, port, dataset):
        sparql_prefix = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        PREFIX hp: <http://kg.course/harry_potter/>

        PREFIX hp_relation: <http://kg.course/harry_potter/关系>
        PREFIX hp_class: <http://kg.course/harry_potter/类>
        PREFIX hp_character: <http://kg.course/harry_potter/角色>
        PREFIX hp_group: <http://kg.course/harry_potter/组织>
        PREFIX hp_house: <http://kg.course/harry_potter/学院>
        PREFIX hp_blood: <http://kg.course/harry_potter/血统>

        PREFIX hp_relation_: <http://kg.course/harry_potter/关系#>
        PREFIX hp_character_: <http://kg.course/harry_potter/角色#>
        PREFIX hp_group_: <http://kg.course/harry_potter/组织#>
        PREFIX hp_house_: <http://kg.course/harry_potter/学院#>
        PREFIX hp_blood_: <http://kg.course/harry_potter/血统#>
        """
        super().__init__(host, port, dataset, sparql_prefix)

    def query_entities_by_name(self, name: str, strict: bool) -> dict:
        
        if strict:
            query = f"""
            SELECT DISTINCT ?sub ?name ?text ?class WHERE {{
                ?sub hp_relation_:name "{name}".
                ?sub a ?class.
                ?class a hp_class: .
                BIND("{name}" AS ?text)
            }}
            """
        else:
            name_regex = ".*".join(name)
            query = f"""
            SELECT DISTINCT ?sub ?name ?text ?class WHERE {{
                ?sub hp_relation_:name ?name.
                ?sub a ?class.
                ?class a hp_class: .
                FILTER regex(?name, "{name_regex}", "i")
                BIND("{name}" AS ?text)
            }}
            """

        # print(query)
        
        res = self.query_with_prefix(query)

        return query, res
    
    def query_adjcent_entities_by_subject(self, subject: str, subject_format: str = 'url') -> dict:
        assert subject_format in ['url'] #'strict_name', 'fuzzy_name'
        if subject_format == 'url':
            query = f"""
            SELECT DISTINCT ?obj ?name ?class ?pred WHERE {{
                {{
                    <{subject}> ?pred ?obj.
                }} UNION {{
                    ?obj ?pred <{subject}>.
                }}
                ?obj hp_relation_:name ?name.
                ?obj a ?class.
                ?class a hp_class: .
                ?pred a hp_relation: .
            }}
            """
        
        res = self.query_with_prefix(query)

        return query, res
    
    def query_pred_between_subjects(self, subjects: List[str], subject_format: str = 'url') -> dict:
        assert subject_format in ['url'] #'strict_name', 'fuzzy_name'
        if subject_format == 'url':
            query = f"""
            SELECT DISTINCT ?sub1 ?pred ?sub2 WHERE {{
                VALUES ?sub1 {{ {" ".join([f"<{sub}>" for sub in subjects])} }}
                VALUES ?sub2 {{ {" ".join([f"<{sub}>" for sub in subjects])} }}
                ?sub1 ?pred ?sub2.
                ?pred a hp_relation: .
            }}
            """

        res = self.query_with_prefix(query)

        return query, res
            
    
    def query_pred_among_adjcent_entities(self, subject: str, subject_format: str = 'url') -> dict:
        assert subject_format in ['url'] #'strict_name', 'fuzzy_name'
        if subject_format == 'url':
            query = f"""
            SELECT DISTINCT ?obj1 ?pred3 ?obj2 WHERE {{
                <{subject}> ?pred1 ?obj1.
                ?obj1 hp_relation_:name ?name1.
                ?obj1 a ?class1.
                ?class1 a hp_class: .

                <{subject}> ?pred2 ?obj2.
                ?obj2 hp_relation_:name ?name2.
                ?obj2 a ?class2.
                ?class2 a hp_class: .

                ?obj1 ?pred3 ?obj2.
                ?pred3 a hp_relation: .
            }}
            """
        
        res = self.query_with_prefix(query)

        return query, res

    def query_properties_by_subject(self, subject: str, subject_format: str = 'url') -> dict:
        assert subject_format in ['url'] #'strict_name', 'fuzzy_name'
        if subject_format == 'url':
            query = f"""
            SELECT DISTINCT ?pred ?obj WHERE {{
                <{subject}> ?pred ?obj.
                FILTER NOT EXISTS {{
                    ?obj a* hp_class: .
                }}
                ?pred a hp_relation: .
            }}
            """
        
        res = self.query_with_prefix(query)

        return query, res

    def query_relation_by_name(self, relation: str, strict: bool) -> dict:
    
        if strict:
            query = f"""
            SELECT DISTINCT ?relation WHERE {{
                ?sub ?relation ?obj.                 
                ?relation a hp_relation: .
            }}
            """
        else:
            relation_regex = ".*".join(relation)
            query = f"""
            SELECT DISTINCT ?relation WHERE {{
                ?sub ?relation ?obj.                 
                ?relation a hp_relation: .                 
                FILTER regex(str(?relation), "{relation_regex}", "i")                     
            }}
            """

        # print(query)
        
        res = self.query_with_prefix(query)

        return query, res

    def query_object_by_subject_and_relation(self, subject: List[str], relation: List[str], subject_format: str = 'url') -> dict:
        assert subject_format in ['url']
        if subject_format == 'url':
            query = f"""
            SELECT DISTINCT ?sub1 ?pred ?sub2 ?class2 ?name2 WHERE {{
                VALUES ?sub1 {{ {" ".join([f"<{sub}>" for sub in subject])} }}
                VALUES ?pred {{ {" ".join([f"<{pred}>" for pred in relation])} }}
                ?sub1 ?pred ?sub2.
                ?pred a hp_relation: .\
                ?sub2 hp_relation_:name ?name2.
                ?sub2 a ?class2.
                ?class2 a hp_class: .
            }}
            """
        
        res = self.query_with_prefix(query)

        return query, res

