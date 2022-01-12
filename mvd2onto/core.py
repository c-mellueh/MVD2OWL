from __future__ import annotations
import lxml.etree
from lxml import etree
from owlready2 import *
from typing import Union

'''
Parse MVDXml file into Onthologies using owlready2

Most of the classes don't use the __init__ method.


Classes:
    
    Base
    IdentityObject
    MvdXml
    ConceptTemplate
    ModelView
    Definition
    Body
    Link
    AttributeRule
    Constraint
    EntityRule
    BaseView
    ExchangeRequirement
    ConceptRoot
    Concept
    Applicability
    TemplateRule
    TemplateRules
    Requirement
    Parameter

Function:

Misc variables:

    onto

'''

onto = get_ontology("http:/mvdxml/onto.owl")

with onto:
    class Base(Thing):
        """
        Masterclass because all Elements share the ability to import subitemes

        Attributes
        ---------
        None

        Methods
        -------
        get_sub_items(name: str, xml_obj: etree._Element) -> list[etree._Element]
            search for subitems with specific name

        import_items(self, xml_object: etree._Element, _class, prop, name: str) -> None
            link sub items to their parent

        """

        @staticmethod
        def get_sub_items(name: str, xml_obj: etree._Element) -> list[etree._Element]:
            """
            search for subitems with specific name

            This function takes a xml_object and searches for sub items,
            which matches the attribute 'name'

            :return: list of Subitems
            :rtype: list[etree._Element]
            :param name: name of subitems
            :type name: str
            :param xml_obj: XML Parent-Object
            :type xml_obj: etree._Element
            """
            elements = xml_obj.find(name, namespaces=xml_obj.nsmap)

            if elements is None:
                return []
            else:
                return list(elements)

        def import_items(self, xml_object: etree._Element, _class, prop, name: str) -> None:
            """
            link sub items to their parent

            This function uses get_sub_items to find the subitems
            
            Parameters
            -------------------

            :rtype: None
            :param xml_object: xml object, which is searched for subobject
            :type xml_object: etree._Element
            :param _class: class of subitems
            :type _class: Class
            :param prop: property which is used to link the subobject to the parent object
            :type prop: Class
            :param name: name of subitems
            :type name: str
            :return: None           
            """
            xml_list = self.get_sub_items(name, xml_object)

            property_name = prop.python_name  # get callable function name from owlready2

            for el in xml_list:
                item = _class(el)
                function = getattr(self, property_name)
                function.append(item)

            return None

        def import_item(self, xml_object: etree._Element, _class, prop, name: str) -> None:
            """
                       link sub item to their parent

                       This function uses get_sub_items to find the subitem
                       This function only works, when there is no possibility of multiple subitems
                       ONLY SINGLE SUBITEMS

                       Parameters
                       -------------------

                       :rtype: None
                       :param xml_object: xml object, which is searched for subobject
                       :type xml_object: etree._Element
                       :param _class: class of subitem
                       :type _class: Class
                       :param prop: property which is used to link the subobject to the parent object
                       :type prop: Class
                       :param name: name of subitems
                       :type name: str
                       :return: None
            """

            for element in xml_object.findall(name, namespaces=xml_object.nsmap):
                property_name = prop.python_name  # get callable function name from owlready2

                item = _class(element)
                function = getattr(self, property_name)
                function.append(item)

            return None

        def import_functional_item(self, xml_object: etree._Element, _class, prop, name: str) -> None:
            """
                link sub items to their parent
                same functionality as import_items but for functional items

                Parameters
                ----
                :param xml_object: xml object, which is searched for subobject
                :type xml_object: etree._Element
                :param _class: class of subitems
                :type _class: Class
                :param prop: property which is used to link the subobject to the parent object
                :type prop: function
                :param name: name of subitem
                :type name: str
    
                :returns: None
                :rtype: None
            """
            for element in xml_object.findall(name, namespaces=xml_object.nsmap):
                property_name = prop.python_name  # get callable function name from owlready2
                item = _class(element)
                setattr(self, property_name, item)

            return None

        def import_attribute(self, xml_object: etree._Element, prop, name: str, is_mandatory: bool) -> None:
            """
            adds attribute to Object \n
            :description: takes attribute 'name' of xml object and saves it in Onthology

            :param xml_object: xml object, which is searched for subobject
            :type xml_object: etree._Element
            :param prop: property which is used to link the subobject to the parent object
            :type prop: Class
            :param name: name of Attribute
            :type name: str
            :param is_mandatory: defines if attribute is mandatory
            :type is_mandatory: bool

            :return: None
            :rtype: None
            """
            property_name = prop.python_name  # get callable function name from owlready2
            attribute = str(xml_object.attrib.get(name))

            if attribute is None and is_mandatory:
                raise AttributeError(name + " needs to exist!")

            else:
                setattr(self, property_name, attribute)


    class IdentityObject(Base):
        """
                Subclass of :class: 'Base' because many Elements have identitydata

                Attributes
                ---------
                uuid
                name
                code
                version
                status
                auhor
                owner
                copyright

                Methods
                -------
                get_sub_items(name: str, xml_obj: etree._Element) -> list[etree._Element]
                    search for subitems with specific name

                import_items(self, xml_object: etree._Element, _class, prop, name: str) -> None
                    link sub items to their parent

                """

        def import_identity_data(self, xml_object):
            """
            Function Defintion
            --------
            imports all identity data specified by MVD Documentation

            :param xml_object: xml-object
            :type xml_object: etree._Element
            """
            self.import_attribute(xml_object, has_for_uuid, "uuid", True)
            self.import_attribute(xml_object, has_for_name, "name", True)
            self.import_attribute(xml_object, has_for_code, "code", False)
            self.import_attribute(xml_object, has_for_version, "version", False)
            self.import_attribute(xml_object, has_for_status, "status", False)
            self.import_attribute(xml_object, has_for_author, "author", False)
            self.import_attribute(xml_object, has_for_owner, "owner", False)
            self.import_attribute(xml_object, has_for_copyright, "copyright", False)


    class MvdXml(IdentityObject):
        """counterpart of 'MvdXml' (first Level of MVDxml)"""

        def __init__(self, file: str = None, doc: str = None, validation=None) -> etree._Element:

            """
               Initial Startup of class (comparable to __init__)

               :param xml_object: xml representation of mvdxml class
               :type xml_object: etree._Element
               :return: None
               :rtype: None
            """

            super().__init__()

            if not (file is None and doc is None and validation is None):
                xml_object = self.import_xml(file, doc=doc, validation=validation)

                self.import_identity_data(xml_object)
                self.import_items(xml_object, ConceptTemplate, has_concept_templates, "Templates")

                for entity_rule in EntityRule.instances():  # all Templates need to be imported befor it is possivle to find referenced templates
                    entity_rule.reference_templates()

                self.import_items(xml_object, ModelView, has_model_views, "Views")

                for template_rule in TemplateRule.instances():  # all Rules needs to be imported, before it is possible to import them
                    template_rule.get_linked_rules()

            return None

        def import_xml(self, file: str, doc: str = None, validation=None) -> etree._Element:
            """
            Imports xml file into python environment
            If given the xml file will be validated against a xsd file

            :param file: MVDXML file to import
            :type file: file
            :param doc: XSD-file
            :type doc: file
            :param validation: bool if XML file should be validated
            :type validation: bool
            :return: xml representation of mvdxml class
            :rtype: etree._Element
            """
            xml_file = etree.parse(file)

            if validation and doc is not None:
                xmlshemadoc = etree.parse(doc)
                xmlshema = etree.XMLSchema(xmlshemadoc)

                if not xmlshema.validate(xml_file):
                    raise ValueError("MVD entspricht nicht den Vorgaben der XSD")
                else:
                    print("Dokument ist fehlerfrei")
            elif doc is None:
                raise TypeError("attribute Doc needs to exist")  # TODO: richtiger Fehler raussuchen

            xml_object = xml_file.getroot()

            return xml_object


    class ConceptTemplate(IdentityObject):
        """ Counterpart of 'ConceptTemplate' in MVDxml"""

        def __init__(self, xml_object: etree._Element) -> None:
            """
                Initial Startup of class

                :param xml_object: xml representation of mvdxml class
                :type xml_object: etree._Element
                :return: None
                :rtype: None
            """

            super().__init__()

            self.import_identity_data(xml_object)

            self.import_items(xml_object, ConceptTemplate, has_sub_templates, "SubTemplates")
            self.import_items(xml_object, Definition, has_definitions, "Definitions")
            self.import_items(xml_object, AttributeRule, has_attribute_rules, "Rules")

            self.import_attribute(xml_object, has_for_applicable_schema, "applicableSchema", True)
            self.import_attribute(xml_object, has_for_applicable_entity, "applicableEntity", False)
            self.import_attribute(xml_object, is_partial, "isPartial", False)

            self.name = self.has_for_name + " [Concept Template] " + self.name

            return None

        def find_rule_id(self, ruleid: str, path: list = [], prefix="", entity_name=None) -> Union[
            (None, None), (AttributeRule, list), (EntityRule, list)]:

            """finds the path to an EntityRule/AttributeRule with matching ruleid
            :param ruleid: rule id searched rule
            :type ruleid: str
            :param path: chronological list of itempath
                        from beginning to this ConceptTemplate
            :type path: list
            :param prefix: prefix given by EntityRule       TODO: check if entityRules give prefixes
            :type prefix: str
            :param entity_name: linked name from EntityRule
            :type entity_name: linked name from EntityRule
            :return: if path is found, a tuple with (searched object, path) will be returned
                            else (None,None) will be returned
            :rtype: Union[(None,None),(AttributeRule,list),(EntityRule,list)]
            """

            path = path[:]  # else python will change the value of input

            if entity_name != self.has_for_applicable_entity:  # if Concept Template is not called by Entity Rule
                path.append(self)

            for concept_template in self.sub_templates:

                value, new_path = concept_template.find_rule_id(ruleid, path=path, prefix=prefix)
                if value is not None:
                    return value, new_path

            for attribute_rule in self.attribute_rules:

                value, new_path = attribute_rule.find_rule_id(ruleid, path=path, prefix=prefix)
                if value is not None:
                    return value, new_path

            return None, None


class ModelView(IdentityObject):
    """Counterpart of 'ModelView' in MVDxml"""

    def __init__(self, xml_object: etree._Element) -> None:
        """
        Initial Startup of class

        :param xml_object: xml representation of MVDxml class
        :type xml_object: etree._Element
        :return: None
        :rtype:None
        """

        super().__init__()
        self.import_identity_data(xml_object)
        self.import_items(xml_object, Definition, has_definitions, "Definitions")
        self.import_items(xml_object, ExchangeRequirement, has_exchange_requirements, "ExchangeRequirements")
        self.import_items(xml_object, ConceptRoot, has_concept_roots, "Roots")

        self.import_attribute(xml_object, has_for_applicable_schema, "applicableSchema", True)
        # TODO: Add BaseView


class Definition(Base):
    """Counterpart of 'Definition' in MVDxml"""

    def __init__(self, xml_object: etree._Element) -> None:
        """
        Initial Startup of class (comparable to __init__)

        :param xml_object: xml representation of MVDxml class
        :type xml_object: etree._Element
        :return: None
        :rtype:None
        """

        super().__init__()
        self.import_functional_item(xml_object, Body, has_body, "Body")
        self.import_item(xml_object, Link, has_links, "Link")


class Body(Base):
    """ Counterpart of 'Body' in MVDxml"""

    def __init__(self, xml_object: etree._Element) -> None:
        """
       Initial Startup of class (comparable to __init__)

       :param xml_object: xml representation of MVDxml class
       :type xml_object: etree._Element
       :return: None
       :rtype:None
        """

        super().__init__()
        self.import_attribute(xml_object, has_for_lang, "lang", is_mandatory=False)
        self.import_attribute(xml_object, has_for_tags, "tags", is_mandatory=False)

        self.import_content(xml_object)

    def import_content(self, xml_object: etree._Element) -> None:
        """
        Imports Text of xml Object

        :param xml_object: xml representation of MVDxml class
        :type xml_object: etree._Element
        """
        content = xml_object.text
        self.has_for_content = content


class Link(Base):
    """Counterpart of 'Link' in MVDxml"""

    def __init__(self, xml_object: etree._Element) -> None:
        """
      Initial Startup of class

      :param xml_object: xml representation of MVDxml class
      :type xml_object: etree._Element
      :return: None
      :rtype:None
        """

        super().__init__()
        self.import_attribute(xml_object, has_for_lang, "lang", is_mandatory=True)
        self.import_attribute(xml_object, has_for_title, "title", is_mandatory=False)
        self.import_attribute(xml_object, has_for_category, "catagory", is_mandatory=False)
        self.import_attribute(xml_object, has_for_href, "href", is_mandatory=True)

        self.has_for_content = xml_object.text


class AttributeRule(Base):
    """Counterpart of 'AttributeRule' in MVDxml"""

    def __init__(self, xml_object):

        """
          Initial Startup of class

          :param xml_object: xml representation of MVDxml class
          :type xml_object: etree._Element
          :return: None
          :rtype:None
        """

        super().__init__()
        self.import_items(xml_object, EntityRule, has_entity_rules, "EntityRules")
        self.import_items(xml_object, Constraint, has_constraints, "Constraints")

        self.import_attribute(xml_object, has_for_attribute_name, "AttributeName", is_mandatory=True)
        self.import_attribute(xml_object, has_for_rule_id, "RuleID", is_mandatory=False)
        self.import_attribute(xml_object, has_for_description, "Description", is_mandatory=False)

        self.name = self.has_for_attribute_name + " [Attribute Rule]" + self.name

        pass

    pass

    def find_rule_id(self, ruleid: str, path: list = [], prefix="") -> Union[
        (None, None), (AttributeRule, list), (EntityRule, list)]:

        """finds the path to an EntityRule/AttributeRule with matching ruleid
        :param ruleid: rule id searched rule
        :type ruleid: str
        :param path: chronological list of itempath
                    from beginning to this ConceptTemplate
        :type path: list
        :param prefix: prefix given by EntityRule       TODO: check if entityRules give prefixes
        :type prefix: str
        :return: if path is found, a tuple with (searched object, path) will be returned
                        else (None,None) will be returned
        :rtype: Union[(None,None),(AttributeRule,list),(EntityRule,list)]
        """

        path = path[:]  # else python will change the value of input
        path.append(self)

        if prefix + self.has_for_rule_id == ruleid:
            return self, path

        else:

            for entity_rule in self.entity_rules:
                value, new_path = entity_rule.find_rule_id(ruleid, path=path, prefix=prefix)
                if value is not None:
                    return value, new_path

            return None, None


class Constraint(Base):
    """Counterpart of 'Constraint' in MVDxml"""

    def __init__(self, xml_object: etree._Element) -> None:
        """
             Initial Startup of class

             :param xml_object: xml representation of MVDxml class
             :type xml_object: etree._Element
             :return: None
             :rtype:None
        """
        super().__init__()
        self.import_attribute(xml_object, has_for_expression, "Expression", is_mandatory=True)


class EntityRule(Base):
    """Counterpart of 'EntityRule' in MVDxml"""

    def __init__(self, xml_object: etree._Element) -> None:

        """
             Initial Startup of class

             :param xml_object: xml representation of MVDxml class
             :type xml_object: etree._Element
             :return: None
             :rtype:None
        """
        super().__init__()

        # Reference to Templates needs to be established later
        # with reference_templates(), because of nesting

        self.references = []
        self.has_for_id_prefix = ""

        self.import_items(xml_object, AttributeRule, has_attribute_rules, "AttributeRules")
        self.import_items(xml_object, Constraint, has_constraints, "Constraints")

        self.import_reference(xml_object)

        self.import_attribute(xml_object, has_for_entity_name, "EntityName", is_mandatory=False)
        self.import_attribute(xml_object, has_for_rule_id, "RuleID", is_mandatory=False)
        self.import_attribute(xml_object, has_for_description, "Description", is_mandatory=False)

        self.name = self.has_for_entity_name + " [Entity Rule]" + self.name

        pass

    def import_reference(self, xml_object: etree._Element) -> None:

        """import references to Templates


            :return: None
            :rtype: None
            :param xml_object: xml representation of MVDxml class
            :type xml_object: etree._Element

        """

        xml_references = xml_object.find("References", namespaces=xml_object.nsmap)
        if xml_references is not None:
            for el in list(xml_references):
                self.references.append(el.attrib.get("ref"))

            id_prefix = xml_references.attrib.get("IdPrefix")
            if id_prefix is not None:
                self.has_for_id_prefix = id_prefix

    def reference_templates(self) -> ConceptTemplate:
        """
        This function needs to be called for every Entity Rule
            after the whole MVD is initialized
            if called while initialization it will lead to a crash because
            the associated template might not be initialized

        :return: reffered Concept Template
        :rtype: ConceptTemplate
        """

        for concept_template in ConceptTemplate.instances():
            for uuid in self.references:
                if uuid == concept_template.has_for_uuid:
                    self.refers = concept_template

        return self.refers

    def find_rule_id(self, ruleid: str, path: list = [], prefix: str = "") -> Union[
        (None, None), (AttributeRule, list), (EntityRule, list)]:

        """finds the path to an EntityRule/AttributeRule with matching ruleid
            :param ruleid: rule id searched rule
            :type ruleid: str
            :param path: chronological list of itempath
                        from beginning to this ConceptTemplate
            :type path: list
            :param prefix: prefix given by EntityRule
            :type prefix: str
            :return: if path is found, a tuple with (searched object, path) will be returned
                            else (None,None) will be returned
            :rtype: Union[(None,None),(AttributeRule,list),(EntityRule,list)]
        """

        path = path[:]  # else python will change the value of input
        path.append(self)

        if self.has_for_id_prefix is not None:
            prefix += self.has_for_id_prefix

        if prefix + self.has_for_rule_id == ruleid:
            return self, path
        else:
            for attribute_rule in self.attribute_rules:
                value, new_path = attribute_rule.find_rule_id(ruleid, path=path, prefix=prefix)
                if value is not None:
                    return value, new_path

            if self.refers is not None:
                value, new_path = self.refers.find_rule_id(ruleid, path=path, prefix=prefix,
                                                           entity_name=self.has_for_entity_name)
                if value is not None:
                    return value, new_path

            return None, None


class BaseView(Base):
    """Counterpart of 'BaseView' in MVDxml"""

    def __init__(self, xml_object):
        """
             Initial Startup of class

             :param xml_object: xml representation of MVDxml class
             :type xml_object: etree._Element
             :return: None
             :rtype:None
        """
        super().__init__()


class ExchangeRequirement(IdentityObject):
    """Counterpart of 'ExchangeRequirement' in MVDxml"""

    def __init__(self, xml_object: etree._Element) -> None:
        """
             Initial Startup of class

             :param xml_object: xml representation of MVDxml class
             :type xml_object: etree._Element
             :return: None
             :rtype:None
        """
        super().__init__()

        self.import_identity_data(xml_object)
        self.import_attribute(xml_object, has_for_applicability, "applicability", is_mandatory=False)
        pass

    pass


class ConceptRoot(IdentityObject):
    """Counterpart of 'ConceptRoot' in MVDxml"""

    def __init__(self, xml_object: etree._Element) -> None:
        """
             Initial Startup of class

             :param xml_object: xml representation of MVDxml class
             :type xml_object: etree._Element
             :return: None
             :rtype:None
        """
        super().__init__()

        self.import_identity_data(xml_object)
        self.import_items(xml_object, Definition, has_definitions, "Definitions")
        self.import_functional_item(xml_object, Applicability, has_applicability, "Applicability")
        self.import_items(xml_object, Concept, has_concepts, "Concepts")

        self.import_attribute(xml_object, has_for_applicable_root_entity, "applicableRootEntity", is_mandatory=True)


class Concept(IdentityObject):
    """Counterpart of 'Concept' in MVDxml"""

    def __init__(self, xml_object: etree._Element) -> None:

        """
             Initial Startup of class

             :param xml_object: xml representation of MVDxml class
             :type xml_object: etree._Element
             :return: None
             :rtype:None
        """
        super().__init__()

        self.import_identity_data(xml_object)
        self.import_items(xml_object, Definition, has_definitions, "Definitions")
        self.import_items(xml_object, Requirement, has_requirement, "Requirements")
        self.import_item(xml_object, TemplateRule, has_template_rules, "TemplateRule")
        self.import_item(xml_object, TemplateRules, has_template_rules, "TemplateRules")

        self.refers = self.find_referred_concept_template(xml_object)

        self.import_attribute(xml_object, has_for_base_concept, "BaseConcept", is_mandatory=False)
        self.import_attribute(xml_object, has_for_override, "Override", is_mandatory=False)

    @staticmethod
    def find_referred_concept_template(xml_object: etree._Element) -> ConceptTemplate:

        """ finds referred concept Template
        :param xml_object: xml representation of MVDxml class
        :type xml_object: etree._Element
        :return: referred ConceptTemplate
        :rtype: ConceptTemplate
        """

        template = xml_object.find("Template", namespaces=xml_object.nsmap)
        uuid = template.attrib.get("ref")

        for concept_template in ConceptTemplate.instances():
            if uuid == concept_template.has_for_uuid:
                return concept_template

        return None


class Applicability(Base):
    """Counterpart of 'Applicability' in MVDxml"""

    def __init__(self, xml_object: etree._Element) -> None:

        """
             Initial Startup of class

             :param xml_object: xml representation of MVDxml class
             :type xml_object: etree._Element
             :return: None
             :rtype:None
        """
        super().__init__()

        self.import_items(xml_object, Definition, has_definitions, "Definitions")
        self.import_item(xml_object, TemplateRule, has_template_rules, "TemplateRule")
        self.import_item(xml_object, TemplateRules, has_template_rules, "TemplateRules")

        self.refers = self.find_referred_concept_template(xml_object)

    @staticmethod
    def find_referred_concept_template(xml_object: etree._Element) -> ConceptTemplate:

        """ finds referred concept Template
        :param xml_object: xml representation of MVDxml class
        :type xml_object: etree._Element

        """

        template = xml_object.find("Template", namespaces=xml_object.nsmap)
        uuid = template.attrib.get("ref")

        for concept_template in ConceptTemplate.instances():
            if uuid == concept_template.has_for_uuid:
                return concept_template

        return None


class TemplateRule(Base):
    """Counterpart of 'TemplateRule' in MVDxml"""

    def __init__(self, xml_object: etree._Element) -> None:

        """
             Initial Startup of class

             :param xml_object: xml representation of MVDxml class
             :type xml_object: etree._Element
             :return: None
             :rtype:None
        """
        super().__init__()
        # TODO: Add Description
        self.has_for_plain_text = xml_object.attrib.get("Parameters")
        self.import_parameter(self.has_for_plain_text)
        self.path_list = []
        self.metric_list = []
        
    def import_parameter(self, text: str) -> None:
        """import and parsing of Parameters

        :param text: parameter String
        :type text: str
        :return: None
        :rtype: None
        """

        split_list = " AND | OR | NOR | NAND | NOR | XOR | NXOR "

        param_list = re.split(split_list, text)

        for parameter_text in param_list:
            parameter = Parameter(parameter_text)
            self.has_for_parameters.append(parameter)

    def get_linked_rules(self) -> (list, list):
        """
        finds Path to referenced EntityRule/AttributeRule


        :return: tuple of (path to referenced Rule, contained metrics)
        :rtype: (list,list)
        """
        parameters = self.has_for_parameters
        ct = self.get_referenced_concept_template()


        for parameter in parameters:
            rule_id = parameter.has_for_parameter_text
            metric = parameter.has_for_metric
            value = parameter.has_for_parameter_value
            test, path = ct.find_rule_id(rule_id)
            path.append(value)
            parameter.path = path

            self.path_list = path
            self.metric_list = metric

        return self.path_list, self.metric_list

    def get_referenced_concept_template(self)-> ConceptTemplate:
        """
               finds parent Concept Template

               :return: Parent ConceptTemplate
               :rtype: ConceptTemplate
        """
        
        parent = self.get_parent()
        return parent.refers
        

    def get_parent(self)-> Union[ConceptTemplate,Applicability]:
        
        """loop up tree until Parent Concept Template/ Applicability is found
        
        :returns: Parent ConceptTemplate or Parent Applicability
        :rtype:Union[ConceptTemplate,Apllicability]
        """
        
        parent = self.is_template_rule_of
        if isinstance(parent,Concept) or isinstance(parent, Applicability):
            return parent
        elif parent is not None:
            return parent.get_parent()


class TemplateRules(Base):
    """Counterpart of 'TemplateRules' in MVDxml"""

    def __init__(self, xml_object: etree._Element) -> None:

        """
             Initial Startup of class

             :param xml_object: xml representation of MVDxml class
             :type xml_object: etree._Element
             :return: None
             :rtype:None
        """
        
        super().__init__()
        self.import_item(xml_object, TemplateRule, has_template_rules, "TemplateRule")
        self.import_item(xml_object, TemplateRules, has_template_rules, "TemplateRules")
        self.import_attribute(xml_object, has_for_operator, "operator", is_mandatory=True)
        # TODO: Add Description

    def get_referenced_concept_template(self)->Union[ConceptTemplate,Applicability]:
        """
               finds parent Concept Template or parent Applicability

               :return: Parent ConceptTemplate or Parent Applicability
               :rtype: Union[ConceptTemplate, Applicability]
        """

        parent = self.get_parent()[0]
        return parent.refers[0]
        pass

    def get_parent(self):
        """loop up tree until Parent Concept Template/ Applicability is found

        :returns: Parent ConceptTemplate or Parent Applicability
        :rtype:Union[ConceptTemplate,Apllicability]
        """

        parent = self.is_template_rule_of

        if isinstance(parent,Concept) or isinstance(parent, Applicability):
            return parent
        else:
            return parent.get_parent()


class Requirement(Base):
    """Counterpart of 'Requirement' in MVDxml"""

    def __init__(self, xml_object: etree._Element) -> None:

        """
             Initial Startup of class

             :param xml_object: xml representation of MVDxml class
             :type xml_object: etree._Element
             :return: None
             :rtype:None
        """
        super().__init__()

        self.import_attribute(xml_object, has_for_applicability, "applicability", is_mandatory=False)
        self.import_attribute(xml_object, has_for_requirement, "requirement", is_mandatory=True)
        # TODO: extend requirements  (mandatory, recommended, notrelevant...
        self.link_exchange_requirement(xml_object)

    def link_exchange_requirement(self, xml_object:etree._Element)->None:

        """link object to ExchangeRequirement

        :param xml_object: xml representation of MVDxml class
        :type xml_object: etree._Element
        :return: None
        :rtype: None
        """

        uuid = xml_object.attrib.get("exchangeRequirement") #TODO: check if uppercase is needed

        for er in ExchangeRequirement.instances():
            if uuid == er.has_for_uuid:
                self.links_to_exchange_requirement = er

class Parameter(Base):
    """Counterpart of 'Parameter' in MVDxml"""

    def __init__(self, text:str) -> None:

        """
             Initial Startup of class

             :param text: xml Parameter Text
             :type xml_object: str
             :return: None
             :rtype:None
        """

        super().__init__()
        self.has_for_text=text
        self.deconstruct_parameter(self.has_for_text)
        pass

    def deconstruct_parameter(self, text:str):

        """
        Deconstructs Parameter and saves parts

        :param text: raw Parameter text
        :type text: str
        :return: (parameter, metric, value)
        :rtype: (str,str,str)
        """


        pattern = re.compile("(.+)\\[(\D+)\\]=(.+)")    #Deconstructs Parameter Text
        text = re.search(pattern, text)

        if text is not None:

            self.has_for_parameter_text= text.group(1)
            self.has_for_metric = self.import_metric(text.group(2))
            self.has_for_parameter_value = self.import_value(text.group(3))

        else:
            raise AttributeError("parameter is not correctly defined: " + str(text))

        return (self.has_for_parameter_text,
                self.has_for_metric,
                self.has_for_parameter_value)

    @staticmethod
    def import_metric(text: str) -> str:
        """
        checks if Metric is acceptable
        :param text: input metric
        :type text: str
        :return: metric
        :rtype: str


        """
        possible_expressions = ['Value', 'Size', 'Type', 'Unique', 'Exists']

        if text not in possible_expressions:
            raise AttributeError("metric is not in authorized list")

        return text

    def import_value(self, text: str) -> Union[str, bool, int, float]:
        """
        parse Parameter Value

        :param text: parameter Value
        :type text: str
        :return: parsed Parameter Value
        :rtype: Union[str,bool,int,float]
        """

        value = None

        if self.has_for_metric == "Value":
            text = text.strip("'")
            value = text.strip('"')

        if self.has_for_metric == "Size":
            value = int(text)

        if self.has_for_metric == "Type":
            value = text

        if self.has_for_metric == "Unique" or self.has_for_metric == "Exists":

            if text.lower() in ["true"]:
                value = True
            elif text.lower() in ["false"]:
                value = False

            elif text.lower() in ["unknown"]:
                value = "UNKNOWN"

            else:
                value = None

        if value is None:
            raise AttributeError("value is not correctly defined in MVDxml: " + str(text))

        return (value)


with onto:
    class has_concept_templates(ObjectProperty, InverseFunctionalProperty):
        domain = [MvdXml]
        range = [ConceptTemplate]
        python_name = "concept_templates"
        pass


    class is_concept_template_of(ObjectProperty, FunctionalProperty):
        domain = [ConceptTemplate]
        range = [MvdXml]
        inverse_property = has_concept_templates
        python_name = "mvdxml"
        pass


    class has_model_views(ObjectProperty, InverseFunctionalProperty):
        domain = [MvdXml]
        range = [ModelView]
        python_name = "model_views"
        pass


    class is_model_view_of(ObjectProperty, FunctionalProperty):
        domain = [ModelView]
        range = [MvdXml]
        inverse_property = has_model_views
        python_name = "mvdxml"
        pass


    class has_sub_templates(ObjectProperty, InverseFunctionalProperty):
        domain = [ConceptTemplate]
        range = [ConceptTemplate]
        python_name = "sub_templates"
        pass


    class is_sub_template_of(ObjectProperty, FunctionalProperty):
        domain = [ConceptTemplate]
        range = [ConceptTemplate]
        inverse_property = has_sub_templates
        pass


    class has_definitions(ObjectProperty, InverseFunctionalProperty):
        domain = [ConceptTemplate | ModelView | ExchangeRequirement | ConceptRoot | Applicability | Concept]
        range = [Definition]
        python_name = "definitions"

        pass


    class is_definition_of(ObjectProperty, FunctionalProperty):
        domain = [Definition]
        range = [ConceptTemplate | ModelView | ExchangeRequirement | ConceptRoot | Applicability | Concept]
        inverse_property = has_definitions
        pass


    class has_attribute_rules(ObjectProperty, InverseFunctionalProperty):
        domain = [ConceptTemplate | EntityRule]
        range = [AttributeRule]
        python_name = "attribute_rules"
        pass


    class is_attribute_rule_of(ObjectProperty, FunctionalProperty):
        domain = [AttributeRule]
        range = [ConceptTemplate | EntityRule]

        inverse_property = has_attribute_rules

        pass


    class has_constraints(ObjectProperty, InverseFunctionalProperty):
        domain = [AttributeRule | EntityRule]
        range = [Constraint]
        python_name = "constraints"


    class is_constraint_of(ObjectProperty, FunctionalProperty):
        domain = [Constraint]
        range = [AttributeRule | EntityRule]
        inverse_property = has_constraints


    class has_entity_rules(ObjectProperty, InverseFunctionalProperty):
        domain = [AttributeRule]
        range = [EntityRule]
        python_name = "entity_rules"


    pass


    class is_entity_rule_of(ObjectProperty, FunctionalProperty):
        domain = [EntityRule]
        range = [AttributeRule]

        inverse_property = has_entity_rules
        pass


    class is_referred_by(ObjectProperty, InverseFunctionalProperty):
        domain = [ConceptTemplate]
        range = [EntityRule | Applicability | Concept]
        pass


    class refers_to(ObjectProperty, FunctionalProperty):
        domain = [EntityRule | Applicability | Concept]
        range = [ConceptTemplate]
        inverse_property = is_referred_by
        python_name = "refers"


    class has_base_views(ModelView >> BaseView, InverseFunctionalProperty):
        pass


    class is_base_view_of(BaseView >> ModelView, FunctionalProperty):
        inverse_property = has_base_views
        pass


    class has_exchange_requirements(ObjectProperty, InverseFunctionalProperty):
        domain = [ModelView]
        range = [ExchangeRequirement]
        python_name = "exchange_requirements"
        pass


    class is_exchange_requirement_of(ObjectProperty, FunctionalProperty):
        domain = [ExchangeRequirement]
        range = [ModelView]

        inverse_property = has_exchange_requirements
        pass


    class has_concept_roots(ObjectProperty, InverseFunctionalProperty):
        domain = [ModelView]
        range = [ConceptRoot]
        pass


    class is_concept_root_of(ObjectProperty, FunctionalProperty):
        domain = [ConceptRoot]
        range = [ModelView]
        inverse_property = has_concept_roots
        pass


    class has_concepts(ObjectProperty, InverseFunctionalProperty):
        domain = [ConceptRoot]
        range = [Concept]

        pass


    class is_concept_of(ObjectProperty, FunctionalProperty):
        domain = [Concept]
        range = [ConceptRoot]

        inverse_property = has_concepts
        pass


    class has_applicability(ObjectProperty, FunctionalProperty):
        domain = [ConceptRoot]
        range = [Applicability]

        pass


    class is_applicability_of(ObjectProperty, FunctionalProperty):
        domain = [Applicability]
        range = [ConceptRoot]

        inverse_property = has_applicability
        pass


    class has_template_rules(ObjectProperty, InverseFunctionalProperty):
        domain = [Applicability | Concept]
        range = [TemplateRule | TemplateRules]
        pass


    class is_template_rule_of(ObjectProperty, FunctionalProperty):
        domain = [TemplateRule | TemplateRules]
        range = [Applicability | Concept]
        inverse_property = has_template_rules
        pass


    class has_requirement(ObjectProperty, InverseFunctionalProperty):
        domain = [Concept]
        range = [Requirement]

        pass


    class is_requirement_of(ObjectProperty, FunctionalProperty):
        domain = [Requirement]
        range = [Concept]
        inverse_property = has_requirement
        pass


    class links_to_exchange_requirement(ObjectProperty, FunctionalProperty):
        domain = [Requirement]
        range = [ExchangeRequirement]
        pass


    class is_linked_by(ObjectProperty, InverseFunctionalProperty):
        domain = [ExchangeRequirement]
        range = [Requirement]
        inverse_property = links_to_exchange_requirement
        pass


    class has_body(ObjectProperty, FunctionalProperty):
        domain = [Definition]
        range = [Body]
        pass


    class is_body_of(ObjectProperty, FunctionalProperty):
        domain = [Body]
        range = [Definition]
        inverse_property = has_body
        pass


    class has_links(ObjectProperty, InverseFunctionalProperty):
        domain = [Definition]
        range = [Link]
        pass


    class is_link_of(ObjectProperty, FunctionalProperty):
        Domain = [Link]
        Range = [Definition]
        inverse_property = has_links
        pass


    ## Identity Objects
    class has_for_uuid(DataProperty, FunctionalProperty):
        domain = [IdentityObject]
        range = [str]

        pass


    class has_for_name(DataProperty, FunctionalProperty):
        domain = [IdentityObject]
        range = [str]
        pass


    class has_for_code(DataProperty, FunctionalProperty):
        domain = [IdentityObject]
        range = [str]
        pass


    class has_for_version(DataProperty, FunctionalProperty):
        domain = [IdentityObject]
        range = [str]
        pass


    class has_for_status(DataProperty, FunctionalProperty):
        domain = [IdentityObject]
        range = [str]
        pass


    class has_for_author(DataProperty, FunctionalProperty):
        domain = [IdentityObject]
        range = [str]
        pass


    class has_for_owner(DataProperty, FunctionalProperty):
        domain = [IdentityObject]
        range = [str]
        pass


    class has_for_copyright(DataProperty, FunctionalProperty):
        domain = [IdentityObject]
        range = [str]
        pass


    class has_for_applicable_schema(DataProperty, FunctionalProperty):
        domain = [ConceptTemplate | ModelView]
        range = [str]
        pass


    class has_for_applicable_entity(DataProperty, FunctionalProperty):
        domain = [ConceptTemplate]
        range = [str]
        pass


    class is_partial(DataProperty, FunctionalProperty):
        domain = [ConceptTemplate]
        range = [bool]
        pass


    class has_for_attribute_name(DataProperty, FunctionalProperty):
        domain = [AttributeRule]
        range = [str]
        pass


    class has_for_rule_id(DataProperty, FunctionalProperty):
        domain = [AttributeRule | EntityRule]
        range = [str]
        pass


    class has_for_description(DataProperty, FunctionalProperty):
        domain = [AttributeRule | EntityRule]
        range = [str]
        pass


    class has_for_entity_name(DataProperty, FunctionalProperty):
        domain = [EntityRule]
        range = [str]
        pass


    class has_for_expression(DataProperty, FunctionalProperty):
        domain = [Constraint]
        range = [str]
        pass


    class has_for_applicability(DataProperty, FunctionalProperty):
        domain = [Requirement | ExchangeRequirement]
        range = [str]
        pass


    class has_for_applicable_root_entity(DataProperty, FunctionalProperty):
        domain = [ConceptRoot]
        range = [str]
        pass


    class has_for_base_concept(DataProperty, FunctionalProperty):
        domain = [Concept]
        range = [str]
        pass


    class has_for_override(DataProperty, FunctionalProperty):
        domain = [Concept]
        range = [bool]
        pass


    class has_for_requirement(DataProperty, FunctionalProperty):
        domain = [Requirement]
        range = [str]
        pass


    class has_for_operator(DataProperty, FunctionalProperty):
        domain = [TemplateRules]
        range = [str]


    class has_for_parameters(ObjectProperty, InverseFunctionalProperty):
        domain = [TemplateRule]
        range = [Parameter]


    class is_parameter_of(ObjectProperty, FunctionalProperty):
        domain = [Parameter]
        range = [TemplateRule]


    class has_for_lang(DataProperty, FunctionalProperty):
        domain = [Body | Link]
        range = [str]


    class has_for_tags(DataProperty, FunctionalProperty):
        domain = [Body]
        range = [str]


    class has_for_content(DataProperty, FunctionalProperty):
        domain = [Body | Link]
        range = [str]


    class has_for_title(DataProperty, FunctionalProperty):
        domain = [Link]
        range = [str]


    class has_for_category(DataProperty, FunctionalProperty):
        domain = [Link]
        range = [str]


    class has_for_href(DataProperty, FunctionalProperty):
        domain = [Link]
        range = [str]


    class has_for_metric(DataProperty, FunctionalProperty):
        domain = [Parameter]
        range = [str]


    class has_for_parameter_value(DataProperty, FunctionalProperty):
        domain = [Parameter]
        range = [str, bool, int]


    class has_for_text(DataProperty, FunctionalProperty):
        domain = [Parameter]
        range = [str]


    class has_for_parameter_text(DataProperty, FunctionalProperty):
        domain = [Parameter]
        range = [str]


    class has_for_plain_text(DataProperty, FunctionalProperty):
        domain = [TemplateRule]
        range = [str]


    class has_for_id_prefix(DataProperty, FunctionalProperty):
        domain = [EntityRule]
        range = [str]
