import owlready2

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

owlready2.JAVA_EXE = "C:\Program Files (x86)\Common Files\Oracle\Java\javapath\java.exe"


def main():
    doc = "mvdXML_V1.1.xsd"
    file = "../Examples/mvdXML_V1-1-Final-Documentation.xml"
    file2 = "../Examples/Prüfregeln.mvdxml"
    file3 = "../Examples/RelAssociatesMaterial.xml"
    mvd = MvdXml(file=file3, doc=doc, validation=False)
    #
    #
    # mvd.import_xml()

    print("START")
    print("")
    tr:TemplateRule = TemplateRule.instances()[0]

    print(tr.has_for_plain_text)

    for i,parameter in enumerate(tr.has_for_parameters):

        path = parameter.path
        metric = parameter.has_for_metric
        operator = parameter.has_for_parameter_operator

        # print(path)
        text = ""
        for el in path:

            if isinstance(el, AttributeRule):
                text += el.has_for_attribute_name + "->"


            elif isinstance(el, EntityRule):
                text += el.has_for_entity_name + "->"

            elif isinstance(el, ConceptTemplate):
                text += el.has_for_applicable_entity + "->"

            elif isinstance(el, ConceptRoot):
                text += el.has_for_applicable_root_entity + "->"

            else:
                text += str(el)

        print("{0} {1} {2}".format(text,operator, metric))

    print()
    onto.save("onto_test.rdfxml")

    close_world(MvdXml)

if __name__ == "__main__":
        main()
