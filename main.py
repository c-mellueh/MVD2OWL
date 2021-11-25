from lxml import etree
from owlready2 import *
from classes import *

import re



########## Relationships ##########








def main():
    doc = "mvdXML_V1.1.xsd"
    file = "mvdXML_V1-1-Final-Documentation.xml"
    file2 = "bimq_rules.mvdxml"
    file3 = "RelAssociatesMaterial.mvdxml"
    mvd = MvdXml()
    #
    #
    mvd.import_xml(file=file3, doc=doc, validation=False)


    print("START")
    print("")

    for tr in TemplateRule.instances():

        # ct =  tr.get_referenced_concept_template()
        # parameters = tr.has_for_parameters
        #
        # print("--------------------------------")
        # print(tr.has_for_plain_text)
        #
        # for parameter in parameters:
        #
        #
        #
        #     rule_id = parameter.has_for_parameter_text
        #
        #     metric = parameter.has_for_metric
        #     value = parameter.has_for_parameter_value
        #     test, path =ct.find_rule_id(rule_id)
        #
        #     text = rule_id+" : "
        print(tr.has_for_plain_text)
        paths = tr.path_list
        for path in paths:
            text = ""
            for el in path:
                if AttributeRule.__instancecheck__(el):
                    text += el.has_for_attribute_name+"->"

                elif EntityRule.__instancecheck__(el):
                    text += el.has_for_entity_name+"->"

                elif ConceptTemplate.__instancecheck__(el):
                    text += el.has_for_applicable_entity+"->"

                else:    text+=str(el)


            print(text)

        print()
    onto.save("onto_test.rdfxml")



if __name__ == "__main__":
    main()


