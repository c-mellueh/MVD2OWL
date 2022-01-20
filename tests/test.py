from mvd2onto.core import *
'''
This File is for Testing the conversion from MVD to Onthology

Classes:

    None
    
Functions:
    
    main()

Misc variables:
    
    None

'''

########## Relationships ##########


def main():
    doc = "mvdXML_V1.1.xsd"
    file = "../Examples/mvdXML_V1-1-Final-Documentation.xml"
    file2 = "../Examples/Prüfregeln.mvdxml"
    file3 = "../Examples/RelAssociatesMaterial.xml"
    mvd = MvdXml(file=file2, doc=doc, validation=False)
    #
    #
    # mvd.import_xml()

    print("START")
    print("")
    tr = TemplateRule.instances()[3]

    print(tr.has_for_plain_text)
    paths, metrics = tr.get_linked_rules()
    #print(len(tr.has_for_parameters))
    #print(len(paths))

    for i, path in enumerate(paths):
        # print(path)
        text = ""
        for el in path:

            if isinstance(el, AttributeRule):
                text += el.has_for_attribute_name + "->"


            elif isinstance(el, EntityRule):
                text += el.has_for_entity_name + "->"

            elif isinstance(el, ConceptTemplate):
                text += el.has_for_applicable_entity + "->"
                print(el.has_for_applicable_entity)
            elif isinstance(el, ConceptRoot):
                text += el.has_for_applicable_root_entity + "->"

            else:
                text += str(el)

        print("{0} ({1})".format(text, metrics[i]))

    print()
    exit()


    onto.save("onto_test.rdfxml")

    for ct in ConceptTemplate.instances():
        print(ct.has_for_name + ct.has_for_uuid)

if __name__ == "__main__":
        main()
