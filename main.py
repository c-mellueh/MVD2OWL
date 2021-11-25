from classes import *


########## Relationships ##########


def main():
    doc = "mvdXML_V1.1.xsd"
    file = "Examples/mvdXML_V1-1-Final-Documentation.xml"
    file2 = "Examples/bimq_rules.mvdxml"
    file3 = "Examples/RelAssociatesMaterial.mvdxml"
    mvd = MvdXml()
    #
    #
    mvd.import_xml(file=file3, doc=doc, validation=False)

    print("START")
    print("")

    for tr in TemplateRule.instances():

        print(tr.has_for_plain_text)
        paths = tr.path_list
        for path in paths:
            text = ""
            for el in path:
                if AttributeRule.__instancecheck__(el):
                    text += el.has_for_attribute_name + "->"

                elif EntityRule.__instancecheck__(el):
                    text += el.has_for_entity_name + "->"

                elif ConceptTemplate.__instancecheck__(el):
                    text += el.has_for_applicable_entity + "->"

                else:
                    text += str(el)

            print(text)

        print()
    onto.save("onto_test.rdfxml")


if __name__ == "__main__":
    main()
