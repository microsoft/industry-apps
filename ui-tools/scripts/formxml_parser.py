"""
Parser and object model for Dataverse Model-Driven App FormXml files.

This module provides classes and functions for reading, manipulating, and writing
FormXml files used in Dataverse solutions.
"""

import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path

from formxml_constants import (
    ControlClassId,
    FormPresentation,
    FormActivationState,
    HeaderDensity,
    SectionLayout,
    CellLabelAlignment,
    CellLabelPosition,
    DEFAULT_LANGUAGE_CODE,
    DEFAULT_SECTION_COLUMNS,
    DEFAULT_SECTION_LABELWIDTH,
    DEFAULT_SUBGRID_RECORDS_PER_PAGE,
    DEFAULT_SUBGRID_AUTO_EXPAND,
    get_classid_for_field_type,
    is_valid_classid,
)


def generate_guid() -> str:
    """Generate a new GUID in the format used by Dataverse (uppercase with braces)."""
    return "{" + str(uuid.uuid4()).upper() + "}"


@dataclass
class Label:
    """Represents a label element in FormXml."""
    description: str
    languagecode: int = DEFAULT_LANGUAGE_CODE
    
    def to_xml(self, parent: ET.Element) -> ET.Element:
        """Convert this label to an XML element."""
        label_elem = ET.SubElement(parent, "label")
        label_elem.set("description", self.description)
        label_elem.set("languagecode", str(self.languagecode))
        return label_elem


@dataclass
class SubgridParameters:
    """Parameters for a subgrid control."""
    relationship_name: str
    target_entity_type: str
    view_id: str
    records_per_page: int = DEFAULT_SUBGRID_RECORDS_PER_PAGE
    auto_expand: str = DEFAULT_SUBGRID_AUTO_EXPAND
    enable_quick_find: bool = False
    enable_view_picker: bool = False
    enable_chart_picker: bool = True
    chart_grid_mode: str = "All"
    
    def to_xml(self, parent: ET.Element) -> ET.Element:
        """Convert parameters to XML elements."""
        params = ET.SubElement(parent, "parameters")
        
        ET.SubElement(params, "RecordsPerPage").text = str(self.records_per_page)
        ET.SubElement(params, "AutoExpand").text = self.auto_expand
        ET.SubElement(params, "EnableQuickFind").text = str(self.enable_quick_find).lower()
        ET.SubElement(params, "EnableViewPicker").text = str(self.enable_view_picker).lower()
        ET.SubElement(params, "EnableChartPicker").text = str(self.enable_chart_picker).lower()
        ET.SubElement(params, "ChartGridMode").text = self.chart_grid_mode
        ET.SubElement(params, "RelationshipName").text = self.relationship_name
        ET.SubElement(params, "TargetEntityType").text = self.target_entity_type
        ET.SubElement(params, "ViewId").text = self.view_id
        ET.SubElement(params, "ViewIds").text = self.view_id
        
        return params


@dataclass
class Control:
    """Represents a control element in a form cell."""
    id: str
    classid: str
    datafieldname: Optional[str] = None
    disabled: bool = False
    indication_of_subgrid: bool = False
    subgrid_params: Optional[SubgridParameters] = None
    
    def to_xml(self, parent: ET.Element) -> ET.Element:
        """Convert this control to an XML element."""
        control_elem = ET.SubElement(parent, "control")
        control_elem.set("id", self.id)
        control_elem.set("classid", self.classid)
        
        if self.datafieldname:
            control_elem.set("datafieldname", self.datafieldname)
        if self.disabled:
            control_elem.set("disabled", "true")
        if self.indication_of_subgrid:
            control_elem.set("indicationOfSubgrid", "true")
            
        if self.subgrid_params:
            self.subgrid_params.to_xml(control_elem)
            
        return control_elem


@dataclass
class Cell:
    """Represents a cell in a form section row."""
    id: str
    labels: List[Label] = field(default_factory=list)
    control: Optional[Control] = None
    locklevel: int = 0
    colspan: int = 1
    rowspan: int = 1
    auto: bool = False
    showlabel: bool = True
    
    def to_xml(self, parent: ET.Element) -> ET.Element:
        """Convert this cell to an XML element."""
        cell_elem = ET.SubElement(parent, "cell")
        cell_elem.set("id", self.id)
        
        if self.locklevel != 0:
            cell_elem.set("locklevel", str(self.locklevel))
        if self.colspan != 1:
            cell_elem.set("colspan", str(self.colspan))
        if self.rowspan != 1:
            cell_elem.set("rowspan", str(self.rowspan))
        if self.auto:
            cell_elem.set("auto", "true")
        if not self.showlabel:
            cell_elem.set("showlabel", "false")
            
        if self.labels:
            labels_elem = ET.SubElement(cell_elem, "labels")
            for label in self.labels:
                label.to_xml(labels_elem)
                
        if self.control:
            self.control.to_xml(cell_elem)
            
        return cell_elem


@dataclass
class Row:
    """Represents a row in a form section."""
    cells: List[Cell] = field(default_factory=list)
    
    def to_xml(self, parent: ET.Element) -> ET.Element:
        """Convert this row to an XML element."""
        row_elem = ET.SubElement(parent, "row")
        for cell in self.cells:
            cell.to_xml(row_elem)
        return row_elem


@dataclass
class Section:
    """Represents a section in a form tab."""
    id: str
    name: Optional[str] = None
    labels: List[Label] = field(default_factory=list)
    rows: List[Row] = field(default_factory=list)
    columns: int = DEFAULT_SECTION_COLUMNS
    is_user_defined: bool = False
    showlabel: bool = True
    showbar: bool = False
    layout: str = SectionLayout.VARWIDTH.value
    celllabelalignment: str = CellLabelAlignment.LEFT.value
    celllabelposition: str = CellLabelPosition.LEFT.value
    labelwidth: int = DEFAULT_SECTION_LABELWIDTH
    locklevel: int = 0
    
    def to_xml(self, parent: ET.Element) -> ET.Element:
        """Convert this section to an XML element."""
        section_elem = ET.SubElement(parent, "section")
        
        if self.name:
            section_elem.set("name", self.name)
        section_elem.set("id", self.id)
        section_elem.set("IsUserDefined", "1" if self.is_user_defined else "0")
        section_elem.set("locklevel", str(self.locklevel))
        section_elem.set("showlabel", "true" if self.showlabel else "false")
        section_elem.set("showbar", "true" if self.showbar else "false")
        section_elem.set("layout", self.layout)
        section_elem.set("celllabelalignment", self.celllabelalignment)
        section_elem.set("celllabelposition", self.celllabelposition)
        section_elem.set("columns", str(self.columns))
        section_elem.set("labelwidth", str(self.labelwidth))
        
        if self.labels:
            labels_elem = ET.SubElement(section_elem, "labels")
            for label in self.labels:
                label.to_xml(labels_elem)
                
        if self.rows:
            rows_elem = ET.SubElement(section_elem, "rows")
            for row in self.rows:
                row.to_xml(rows_elem)
                
        return section_elem
    
    def add_field(self, field_name: str, field_label: str, field_type: str, 
                  row_index: Optional[int] = None, cell_position: int = 0) -> Cell:
        """
        Add a field control to this section.
        
        Args:
            field_name: The schema name of the field (datafieldname)
            field_label: The display label for the field
            field_type: The type of field (text, optionset, lookup, datetime, etc.)
            row_index: Which row to add to (None = new row, -1 = last row)
            cell_position: Position in the row (0-based)
            
        Returns:
            The created Cell object
        """
        classid = get_classid_for_field_type(field_type)
        
        # Create the control
        control = Control(
            id=field_name,
            classid=classid,
            datafieldname=field_name,
            disabled=False
        )
        
        # Create the cell
        cell = Cell(
            id=generate_guid(),
            labels=[Label(description=field_label)],
            control=control,
            locklevel=0,
            colspan=1,
            rowspan=1
        )
        
        # Add to appropriate row
        if row_index is None:
            # Create new row
            row = Row(cells=[cell])
            self.rows.append(row)
        elif row_index == -1:
            # Add to last row
            if not self.rows:
                row = Row(cells=[cell])
                self.rows.append(row)
            else:
                self.rows[-1].cells.insert(cell_position, cell)
        else:
            # Add to specific row
            if row_index >= len(self.rows):
                # Create rows up to the index
                while len(self.rows) <= row_index:
                    self.rows.append(Row())
            self.rows[row_index].cells.insert(cell_position, cell)
            
        return cell
    
    def add_subgrid(self, subgrid_id: str, subgrid_label: str,
                    relationship_name: str, target_entity: str, view_id: str,
                    row_index: Optional[int] = None) -> Cell:
        """
        Add a subgrid control to this section.
        
        Args:
            subgrid_id: Unique ID for the subgrid control
            subgrid_label: Display label for the subgrid
            relationship_name: The relationship schema name
            target_entity: The logical name of the target entity
            view_id: The GUID of the view to display
            row_index: Which row to add to (None = new row)
            
        Returns:
            The created Cell object
        """
        subgrid_params = SubgridParameters(
            relationship_name=relationship_name,
            target_entity_type=target_entity,
            view_id=view_id
        )
        
        control = Control(
            id=subgrid_id,
            classid=ControlClassId.SUBGRID.value,
            indication_of_subgrid=True,
            subgrid_params=subgrid_params
        )
        
        cell = Cell(
            id=generate_guid(),
            labels=[Label(description=subgrid_label)],
            control=control,
            locklevel=0,
            colspan=1,
            rowspan=4,
            auto=False
        )
        
        # Add to appropriate row
        if row_index is None:
            row = Row(cells=[cell])
            self.rows.append(row)
        else:
            if row_index >= len(self.rows):
                while len(self.rows) <= row_index:
                    self.rows.append(Row())
            self.rows[row_index].cells.append(cell)
            
        return cell
    
    def remove_field(self, field_name: str) -> bool:
        """
        Remove a field from this section by its datafieldname.
        
        Args:
            field_name: The schema name of the field to remove
            
        Returns:
            True if the field was found and removed, False otherwise
        """
        for row in self.rows:
            for i, cell in enumerate(row.cells):
                if cell.control and cell.control.datafieldname == field_name:
                    row.cells.pop(i)
                    return True
        return False


@dataclass
class Column:
    """Represents a column in a tab."""
    width: str = "100%"
    sections: List[Section] = field(default_factory=list)
    
    def to_xml(self, parent: ET.Element) -> ET.Element:
        """Convert this column to an XML element."""
        column_elem = ET.SubElement(parent, "column")
        column_elem.set("width", self.width)
        
        if self.sections:
            sections_elem = ET.SubElement(column_elem, "sections")
            for section in self.sections:
                section.to_xml(sections_elem)
                
        return column_elem
    
    def get_section_by_name(self, section_name: str) -> Optional[Section]:
        """Get a section by its name (case-insensitive)."""
        section_name_lower = section_name.lower()
        for section in self.sections:
            # Check the section name attribute
            if section.name and section.name.lower() == section_name_lower:
                return section
            # Check the label description
            for label in section.labels:
                if label.description.lower() == section_name_lower:
                    return section
        return None
    
    def add_section(self, section_name: str, section_label: str,
                    columns: int = DEFAULT_SECTION_COLUMNS) -> Section:
        """
        Add a new section to this column.
        
        Args:
            section_name: Internal name for the section
            section_label: Display label for the section
            columns: Number of columns in the section
            
        Returns:
            The created Section object
        """
        section = Section(
            id=generate_guid(),
            name=section_name,
            labels=[Label(description=section_label)],
            columns=columns,
            is_user_defined=True,
            showlabel=True,
            showbar=False
        )
        self.sections.append(section)
        return section


@dataclass
class Tab:
    """Represents a tab in a form."""
    id: str
    name: Optional[str] = None
    labels: List[Label] = field(default_factory=list)
    columns: List[Column] = field(default_factory=list)
    is_user_defined: bool = True
    verticallayout: bool = True
    locklevel: int = 0
    showlabel: bool = True
    
    def to_xml(self, parent: ET.Element) -> ET.Element:
        """Convert this tab to an XML element."""
        tab_elem = ET.SubElement(parent, "tab")
        
        if self.name:
            tab_elem.set("name", self.name)
        tab_elem.set("id", self.id)
        tab_elem.set("IsUserDefined", "1" if self.is_user_defined else "0")
        tab_elem.set("locklevel", str(self.locklevel))
        
        if self.verticallayout:
            tab_elem.set("verticallayout", "true")
        if not self.showlabel:
            tab_elem.set("showlabel", "false")
            
        if self.labels:
            labels_elem = ET.SubElement(tab_elem, "labels")
            for label in self.labels:
                label.to_xml(labels_elem)
                
        if self.columns:
            columns_elem = ET.SubElement(tab_elem, "columns")
            for column in self.columns:
                column.to_xml(columns_elem)
                
        return tab_elem
    
    def get_section_by_name(self, section_name: str) -> Optional[Section]:
        """Get a section by its name from any column in this tab."""
        for column in self.columns:
            section = column.get_section_by_name(section_name)
            if section:
                return section
        return None
    
    def add_section(self, section_name: str, section_label: str,
                    columns: int = DEFAULT_SECTION_COLUMNS,
                    column_index: int = 0) -> Section:
        """
        Add a new section to this tab.
        
        Args:
            section_name: Internal name for the section
            section_label: Display label for the section
            columns: Number of columns in the section
            column_index: Which column to add the section to
            
        Returns:
            The created Section object
        """
        # Ensure the column exists
        while len(self.columns) <= column_index:
            self.columns.append(Column())
            
        return self.columns[column_index].add_section(section_name, section_label, columns)


@dataclass
class FormHeader:
    """Represents the form header section."""
    id: str
    rows: List[Row] = field(default_factory=list)
    celllabelposition: str = CellLabelPosition.TOP.value
    columns: int = 111
    labelwidth: int = DEFAULT_SECTION_LABELWIDTH
    celllabelalignment: str = CellLabelAlignment.LEFT.value
    
    def to_xml(self, parent: ET.Element) -> ET.Element:
        """Convert this header to an XML element."""
        header_elem = ET.SubElement(parent, "header")
        header_elem.set("id", self.id)
        header_elem.set("celllabelposition", self.celllabelposition)
        header_elem.set("columns", str(self.columns))
        header_elem.set("labelwidth", str(self.labelwidth))
        header_elem.set("celllabelalignment", self.celllabelalignment)
        
        if self.rows:
            rows_elem = ET.SubElement(header_elem, "rows")
            for row in self.rows:
                row.to_xml(rows_elem)
                
        return header_elem


@dataclass
class FormFooter:
    """Represents the form footer section."""
    id: str
    rows: List[Row] = field(default_factory=list)
    celllabelposition: str = CellLabelPosition.TOP.value
    columns: int = 111
    labelwidth: int = DEFAULT_SECTION_LABELWIDTH
    celllabelalignment: str = CellLabelAlignment.LEFT.value
    
    def to_xml(self, parent: ET.Element) -> ET.Element:
        """Convert this footer to an XML element."""
        footer_elem = ET.SubElement(parent, "footer")
        footer_elem.set("id", self.id)
        footer_elem.set("celllabelposition", self.celllabelposition)
        footer_elem.set("columns", str(self.columns))
        footer_elem.set("labelwidth", str(self.labelwidth))
        footer_elem.set("celllabelalignment", self.celllabelalignment)
        
        if self.rows:
            rows_elem = ET.SubElement(footer_elem, "rows")
            for row in self.rows:
                row.to_xml(rows_elem)
                
        return footer_elem


@dataclass
class FormDefinition:
    """Represents the main form definition."""
    formid: str
    form_name: str
    tabs: List[Tab] = field(default_factory=list)
    header: Optional[FormHeader] = None
    footer: Optional[FormFooter] = None
    introduced_version: str = "1.0"
    form_presentation: int = FormPresentation.MAIN.value
    form_activation_state: int = FormActivationState.ACTIVE.value
    headerdensity: str = HeaderDensity.HIGH_WITH_CONTROLS.value
    shownavigationbar: bool = False
    localized_names: List[Label] = field(default_factory=list)
    descriptions: List[Label] = field(default_factory=list)
    
    def to_xml(self) -> ET.Element:
        """Convert this form definition to an XML element tree."""
        # Root element
        forms_elem = ET.Element("forms")
        forms_elem.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        
        # System form
        systemform_elem = ET.SubElement(forms_elem, "systemform")
        
        # Form metadata
        ET.SubElement(systemform_elem, "formid").text = self.formid
        ET.SubElement(systemform_elem, "IntroducedVersion").text = self.introduced_version
        ET.SubElement(systemform_elem, "FormPresentation").text = str(self.form_presentation)
        ET.SubElement(systemform_elem, "FormActivationState").text = str(self.form_activation_state)
        
        # Form element
        form_elem = ET.SubElement(systemform_elem, "form")
        form_elem.set("headerdensity", self.headerdensity)
        form_elem.set("shownavigationbar", "true" if self.shownavigationbar else "false")
        
        # Tabs
        if self.tabs:
            tabs_elem = ET.SubElement(form_elem, "tabs")
            for tab in self.tabs:
                tab.to_xml(tabs_elem)
                
        # Header
        if self.header:
            self.header.to_xml(form_elem)
            
        # Footer
        if self.footer:
            self.footer.to_xml(form_elem)
            
        # Display conditions (default to everyone)
        display_conditions = ET.SubElement(form_elem, "DisplayConditions")
        display_conditions.set("Order", "0")
        display_conditions.set("FallbackForm", "true")
        ET.SubElement(display_conditions, "Everyone")
        
        # IsCustomizable
        ET.SubElement(systemform_elem, "IsCustomizable").text = "1"
        ET.SubElement(systemform_elem, "CanBeDeleted").text = "1"
        
        # Localized names
        if self.localized_names:
            localized_names_elem = ET.SubElement(systemform_elem, "LocalizedNames")
            for label in self.localized_names:
                label.to_xml(localized_names_elem)
                
        # Descriptions
        if self.descriptions:
            descriptions_elem = ET.SubElement(systemform_elem, "Descriptions")
            for label in self.descriptions:
                label.to_xml(descriptions_elem)
                
        return forms_elem
    
    def get_tab_by_name(self, tab_name: str) -> Optional[Tab]:
        """Get a tab by its name (case-insensitive)."""
        tab_name_lower = tab_name.lower()
        for tab in self.tabs:
            # Check the tab name attribute
            if tab.name and tab.name.lower() == tab_name_lower:
                return tab
            # Check the label description
            for label in tab.labels:
                if label.description.lower() == tab_name_lower:
                    return tab
        return None
    
    def add_tab(self, tab_name: str, tab_label: str, index: Optional[int] = None) -> Tab:
        """
        Add a new tab to the form.
        
        Args:
            tab_name: Internal name for the tab
            tab_label: Display label for the tab
            index: Position to insert the tab (None = append at end)
            
        Returns:
            The created Tab object
        """
        tab = Tab(
            id=generate_guid(),
            name=tab_name,
            labels=[Label(description=tab_label)],
            columns=[Column()],  # Start with one column
            is_user_defined=True,
            verticallayout=True
        )
        
        if index is None:
            self.tabs.append(tab)
        else:
            self.tabs.insert(index, tab)
            
        return tab
    
    def remove_tab(self, tab_name: str) -> bool:
        """
        Remove a tab from the form by name.
        
        Args:
            tab_name: The name of the tab to remove
            
        Returns:
            True if the tab was found and removed, False otherwise
        """
        for i, tab in enumerate(self.tabs):
            if tab.name and tab.name.lower() == tab_name.lower():
                self.tabs.pop(i)
                return True
            for label in tab.labels:
                if label.description.lower() == tab_name.lower():
                    self.tabs.pop(i)
                    return True
        return False


class FormXmlParser:
    """Parser for Dataverse FormXml files."""
    
    @staticmethod
    def parse_label(label_elem: ET.Element) -> Label:
        """Parse a label element."""
        return Label(
            description=label_elem.get("description", ""),
            languagecode=int(label_elem.get("languagecode", DEFAULT_LANGUAGE_CODE))
        )
    
    @staticmethod
    def parse_labels(labels_elem: Optional[ET.Element]) -> List[Label]:
        """Parse a labels container element."""
        if labels_elem is None:
            return []
        return [FormXmlParser.parse_label(label) for label in labels_elem.findall("label")]
    
    @staticmethod
    def parse_subgrid_parameters(params_elem: Optional[ET.Element]) -> Optional[SubgridParameters]:
        """Parse subgrid parameters."""
        if params_elem is None:
            return None
            
        relationship_name_elem = params_elem.find("RelationshipName")
        target_entity_elem = params_elem.find("TargetEntityType")
        view_id_elem = params_elem.find("ViewId")
        
        if not all([relationship_name_elem, target_entity_elem, view_id_elem]):
            return None
            
        records_per_page = int(params_elem.findtext("RecordsPerPage", DEFAULT_SUBGRID_RECORDS_PER_PAGE))
        auto_expand = params_elem.findtext("AutoExpand", DEFAULT_SUBGRID_AUTO_EXPAND)
        enable_quick_find = params_elem.findtext("EnableQuickFind", "false").lower() == "true"
        enable_view_picker = params_elem.findtext("EnableViewPicker", "false").lower() == "true"
        enable_chart_picker = params_elem.findtext("EnableChartPicker", "true").lower() == "true"
        chart_grid_mode = params_elem.findtext("ChartGridMode", "All")
        
        return SubgridParameters(
            relationship_name=relationship_name_elem.text,
            target_entity_type=target_entity_elem.text,
            view_id=view_id_elem.text,
            records_per_page=records_per_page,
            auto_expand=auto_expand,
            enable_quick_find=enable_quick_find,
            enable_view_picker=enable_view_picker,
            enable_chart_picker=enable_chart_picker,
            chart_grid_mode=chart_grid_mode
        )
    
    @staticmethod
    def parse_control(control_elem: ET.Element) -> Control:
        """Parse a control element."""
        indication_of_subgrid = control_elem.get("indicationOfSubgrid", "false").lower() == "true"
        
        subgrid_params = None
        if indication_of_subgrid:
            params_elem = control_elem.find("parameters")
            subgrid_params = FormXmlParser.parse_subgrid_parameters(params_elem)
        
        return Control(
            id=control_elem.get("id", ""),
            classid=control_elem.get("classid", ""),
            datafieldname=control_elem.get("datafieldname"),
            disabled=control_elem.get("disabled", "false").lower() == "true",
            indication_of_subgrid=indication_of_subgrid,
            subgrid_params=subgrid_params
        )
    
    @staticmethod
    def parse_cell(cell_elem: ET.Element) -> Cell:
        """Parse a cell element."""
        labels = FormXmlParser.parse_labels(cell_elem.find("labels"))
        
        control_elem = cell_elem.find("control")
        control = FormXmlParser.parse_control(control_elem) if control_elem is not None else None
        
        return Cell(
            id=cell_elem.get("id", generate_guid()),
            labels=labels,
            control=control,
            locklevel=int(cell_elem.get("locklevel", "0")),
            colspan=int(cell_elem.get("colspan", "1")),
            rowspan=int(cell_elem.get("rowspan", "1")),
            auto=cell_elem.get("auto", "false").lower() == "true",
            showlabel=cell_elem.get("showlabel", "true").lower() == "true"
        )
    
    @staticmethod
    def parse_row(row_elem: ET.Element) -> Row:
        """Parse a row element."""
        cells = [FormXmlParser.parse_cell(cell) for cell in row_elem.findall("cell")]
        return Row(cells=cells)
    
    @staticmethod
    def parse_section(section_elem: ET.Element) -> Section:
        """Parse a section element."""
        labels = FormXmlParser.parse_labels(section_elem.find("labels"))
        
        rows_elem = section_elem.find("rows")
        rows = [FormXmlParser.parse_row(row) for row in rows_elem.findall("row")] if rows_elem is not None else []
        
        return Section(
            id=section_elem.get("id", generate_guid()),
            name=section_elem.get("name"),
            labels=labels,
            rows=rows,
            columns=int(section_elem.get("columns", str(DEFAULT_SECTION_COLUMNS))),
            is_user_defined=section_elem.get("IsUserDefined", "0") == "1",
            showlabel=section_elem.get("showlabel", "true").lower() == "true",
            showbar=section_elem.get("showbar", "false").lower() == "true",
            layout=section_elem.get("layout", SectionLayout.VARWIDTH.value),
            celllabelalignment=section_elem.get("celllabelalignment", CellLabelAlignment.LEFT.value),
            celllabelposition=section_elem.get("celllabelposition", CellLabelPosition.LEFT.value),
            labelwidth=int(section_elem.get("labelwidth", str(DEFAULT_SECTION_LABELWIDTH))),
            locklevel=int(section_elem.get("locklevel", "0"))
        )
    
    @staticmethod
    def parse_column(column_elem: ET.Element) -> Column:
        """Parse a column element."""
        sections_elem = column_elem.find("sections")
        sections = [FormXmlParser.parse_section(section) for section in sections_elem.findall("section")] if sections_elem is not None else []
        
        return Column(
            width=column_elem.get("width", "100%"),
            sections=sections
        )
    
    @staticmethod
    def parse_tab(tab_elem: ET.Element) -> Tab:
        """Parse a tab element."""
        labels = FormXmlParser.parse_labels(tab_elem.find("labels"))
        
        columns_elem = tab_elem.find("columns")
        columns = [FormXmlParser.parse_column(column) for column in columns_elem.findall("column")] if columns_elem is not None else []
        
        return Tab(
            id=tab_elem.get("id", generate_guid()),
            name=tab_elem.get("name"),
            labels=labels,
            columns=columns,
            is_user_defined=tab_elem.get("IsUserDefined", "0") == "1",
            verticallayout=tab_elem.get("verticallayout", "true").lower() == "true",
            locklevel=int(tab_elem.get("locklevel", "0")),
            showlabel=tab_elem.get("showlabel", "true").lower() == "true"
        )
    
    @staticmethod
    def parse_header(header_elem: Optional[ET.Element]) -> Optional[FormHeader]:
        """Parse a header element."""
        if header_elem is None:
            return None
            
        rows_elem = header_elem.find("rows")
        rows = [FormXmlParser.parse_row(row) for row in rows_elem.findall("row")] if rows_elem is not None else []
        
        return FormHeader(
            id=header_elem.get("id", generate_guid()),
            rows=rows,
            celllabelposition=header_elem.get("celllabelposition", CellLabelPosition.TOP.value),
            columns=int(header_elem.get("columns", "111")),
            labelwidth=int(header_elem.get("labelwidth", str(DEFAULT_SECTION_LABELWIDTH))),
            celllabelalignment=header_elem.get("celllabelalignment", CellLabelAlignment.LEFT.value)
        )
    
    @staticmethod
    def parse_footer(footer_elem: Optional[ET.Element]) -> Optional[FormFooter]:
        """Parse a footer element."""
        if footer_elem is None:
            return None
            
        rows_elem = footer_elem.find("rows")
        rows = [FormXmlParser.parse_row(row) for row in rows_elem.findall("row")] if rows_elem is not None else []
        
        return FormFooter(
            id=footer_elem.get("id", generate_guid()),
            rows=rows,
            celllabelposition=footer_elem.get("celllabelposition", CellLabelPosition.TOP.value),
            columns=int(footer_elem.get("columns", "111")),
            labelwidth=int(footer_elem.get("labelwidth", str(DEFAULT_SECTION_LABELWIDTH))),
            celllabelalignment=footer_elem.get("celllabelalignment", CellLabelAlignment.LEFT.value)
        )
    
    @staticmethod
    def parse_file(file_path: Path) -> FormDefinition:
        """
        Parse a FormXml file and return a FormDefinition object.
        
        Args:
            file_path: Path to the FormXml file
            
        Returns:
            FormDefinition object representing the form
        """
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        systemform = root.find("systemform")
        if systemform is None:
            raise ValueError("Invalid FormXml: missing <systemform> element")
            
        formid = systemform.findtext("formid", "")
        introduced_version = systemform.findtext("IntroducedVersion", "1.0")
        form_presentation = int(systemform.findtext("FormPresentation", str(FormPresentation.MAIN.value)))
        form_activation_state = int(systemform.findtext("FormActivationState", str(FormActivationState.ACTIVE.value)))
        
        form_elem = systemform.find("form")
        if form_elem is None:
            raise ValueError("Invalid FormXml: missing <form> element")
            
        headerdensity = form_elem.get("headerdensity", HeaderDensity.HIGH_WITH_CONTROLS.value)
        shownavigationbar = form_elem.get("shownavigationbar", "false").lower() == "true"
        
        # Parse tabs
        tabs_elem = form_elem.find("tabs")
        tabs = [FormXmlParser.parse_tab(tab) for tab in tabs_elem.findall("tab")] if tabs_elem is not None else []
        
        # Parse header and footer
        header = FormXmlParser.parse_header(form_elem.find("header"))
        footer = FormXmlParser.parse_footer(form_elem.find("footer"))
        
        # Parse localized names
        localized_names_elem = systemform.find("LocalizedNames")
        localized_names = FormXmlParser.parse_labels(localized_names_elem)
        
        # Parse descriptions
        descriptions_elem = systemform.find("Descriptions")
        descriptions = FormXmlParser.parse_labels(descriptions_elem)
        
        # Extract form name from localized names
        form_name = localized_names[0].description if localized_names else file_path.stem
        
        return FormDefinition(
            formid=formid,
            form_name=form_name,
            tabs=tabs,
            header=header,
            footer=footer,
            introduced_version=introduced_version,
            form_presentation=form_presentation,
            form_activation_state=form_activation_state,
            headerdensity=headerdensity,
            shownavigationbar=shownavigationbar,
            localized_names=localized_names,
            descriptions=descriptions
        )
    
    @staticmethod
    def write_file(form: FormDefinition, file_path: Path) -> None:
        """
        Write a FormDefinition to an XML file.
        
        Args:
            form: The FormDefinition to write
            file_path: Path where the file should be written
        """
        form_elem = form.to_xml()
        tree = ET.ElementTree(form_elem)
        
        # Format the XML with indentation
        ET.indent(tree, space="  ", level=0)
        
        # Write with XML declaration
        tree.write(file_path, encoding="utf-8", xml_declaration=True)
