from lxml import etree
from owlready2 import *
from classes import *

import re




########## Relationships ##########








def main():
    doc = "mvdXML_V1.1.xsd"
    # #file = "Prüfregeln.mvdxml"
    file = "mvdXML_V1-1-Final-Documentation.xml"
    mvd = MvdXml()
    #
    #
    mvd.import_xml(file=file, doc=doc, validation=False)


    print("START")
    print("")

    for tr in TemplateRule.instances():

        ct =  tr.get_referenced_concept_template()
        parameters = tr.has_for_parameters

        print("--------------------------------")
        print(tr.has_for_plain_text)

        for parameter in parameters:



            rule_id = parameter.has_for_parameter_text

            print(rule_id)
            metric = parameter.has_for_metric
            value = parameter.has_for_parameter_value
            test, path =ct.find_rule_id(rule_id)

            text = rule_id+" : "


            # for el in path:
            #     if AttributeRule.__instancecheck__(el):
            #         text += el.has_for_attribute_name+"->"
            #
            #     if EntityRule.__instancecheck__(el):
            #         text += el.has_for_entity_name+"->"
            #
            #     if ConceptTemplate.__instancecheck__(el):
            #         text += el.has_for_name+"->"


            # print(text+str(value))

        print()
    onto.save("onto_test.rdfxml")



if __name__ == "__main__":
    main()


