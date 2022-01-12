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
    print(tr.path_list)
    print(tr.get_linked_rules())
    print(tr.path_list)
    for l, tr in enumerate(TemplateRule.instances()):
        if l == 2:

            paths, metrics = tr.get_linked_rules()

            for el in enumerate(paths):

                text = ""
                if AttributeRule.__instancecheck__(el):
                    text += el.has_for_attribute_name + "->"

                elif EntityRule.__instancecheck__(el):
                    text += el.has_for_entity_name + "->"

                elif ConceptTemplate.__instancecheck__(el):
                    text += el.has_for_applicable_entity + "->"

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
