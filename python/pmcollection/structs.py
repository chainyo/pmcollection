"""All data schemas that are used to manipulate data in the database."""

from __future__ import annotations

import datetime
import xml.etree.ElementTree as ET
from typing import List, Tuple, Union

from pydantic import BaseModel


MONTHS = {
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12",
}


def find_or_none(element: ET.Element, tag: str) -> ET.Element:
    """Find a child element or return None."""
    return element.find(tag).text if element.find(tag) is not None else None


class Article(BaseModel):
    """An article object that represents an article in a publication."""

    publication_model: str
    journal: Journal
    title: str
    abstract: Union[str, None]
    pagination: Union[str, None]
    authors: List[Author]
    language: str
    date: Union[datetime.date, None]
    grants: Union[List[Grant], None]
    publication_types: List[Publication]
    elocation_id: Union[ELocationId, None]
    vernacular_title: Union[str, None]
    data_banks: Union[List[DataBank], None]
    copyright_information: Union[str, None]

    @classmethod
    def from_xml(cls, element: ET.Element) -> Article:
        """Create an Article from an XML element.

        Args:
            element (ET.Element): The XML element to create the Article from.

        Returns:
            Article: The Article created from the XML element.
        """
        return cls(
            publication_model=element.attrib.get("PubModel"),
            journal=Journal.from_xml(element.find(".//Journal")),
            title="".join(element.find(".//ArticleTitle").itertext()),
            abstract=(
                "".join(element.find(".//Abstract//AbstractText").itertext())
                if element.find(".//Abstract//AbstractText") is not None
                else None
            ),
            pagination=find_or_none(element, ".//Pagination//MedlinePgn"),
            authors=[
                Author.from_xml(item)
                for item in element.findall(".//AuthorList//Author")
            ],
            language=element.find(".//Language").text,
            date=(
                datetime.date(
                    year=int(element.find(".//ArticleDate//Year").text),
                    month=int(element.find(".//ArticleDate//Month").text),
                    day=int(element.find(".//ArticleDate//Day").text),
                )
                if element.find(".//ArticleDate") is not None
                else None
            ),
            grants=[
                Grant.from_xml(item) for item in element.findall(".//GrantList//Grant")
            ]
            if element.find(".//GrantList") is not None
            else None,
            publication_types=[
                Publication.from_xml(item)
                for item in element.findall(".//PublicationTypeList//PublicationType")
            ],
            elocation_id=(
                ELocationId.from_xml(element.find(".//ELocationID"))
                if element.find(".//ELocationID") is not None
                else None
            ),
            vernacular_title=(
                "".join(element.find(".//VernacularTitle").itertext())
                if element.find(".//VernacularTitle") is not None
                else None
            ),
            data_banks=[
                DataBank.from_xml(item)
                for item in element.findall(".//DataBankList//DataBank")
            ]
            if element.find(".//DataBankList") is not None
            else None,
            copyright_information=(
                element.find(".//Abstract//CopyrightInformation").text
                if element.find(".//Abstract//CopyrightInformation") is not None
                else None
            ),
        )


class DataBank(BaseModel):
    """A data bank object that represents a data bank used in a publication."""

    name: str
    accession_numbers: List[str]
    complete: bool

    @classmethod
    def from_xml(cls, element: ET.Element) -> DataBank:
        """Create a DataBank from an XML element.

        Args:
            element (ET.Element): The XML element to create the DataBank from.

        Returns:
            DataBank: The DataBank created from the XML element.
        """
        return cls(
            name=element.find(".//DataBankName").text,
            accession_numbers=[
                item.text
                for item in element.findall(".//AccessionNumberList//AccessionNumber")
            ],
            complete=True if element.attrib.get("CompleteYN") == "Y" else False,
        )


class ELocationId(BaseModel):
    """An ELocation ID object that represents an ELocation ID of a publication."""

    id_type: str
    valid: bool
    value: str

    @classmethod
    def from_xml(cls, element: ET.Element) -> ELocationId:
        """Create an ELocationId from an XML element.

        Args:
            element (ET.Element): The XML element to create the ELocationId from.

        Returns:
            ELocationId: The ELocationId created from the XML element.
        """
        return cls(
            id_type=element.attrib.get("EIdType"),
            valid=True if element.attrib.get("ValidYN") == "Y" else False,
            value=element.text,
        )


class Journal(BaseModel):
    """A journal object that represents a journal in a publication."""

    issn: Union[Issn, None]
    issue: JournalIssue
    title: str
    iso_abbreviation: str

    @classmethod
    def from_xml(cls, element: ET.Element) -> Journal:
        """Create a Journal from an XML element.

        Args:
            element (ET.Element): The XML element to create the Journal from.

        Returns:
            Journal: The Journal created from the XML element.
        """
        _issn = (
            Issn.from_xml(element.find(".//ISSN"))
            if element.find(".//ISSN") is not None
            else None
        )

        return cls(
            issn=_issn,
            issue=JournalIssue.from_xml(element.find(".//JournalIssue")),
            title=element.find(".//Title").text,
            iso_abbreviation=element.find(".//ISOAbbreviation").text,
        )


class JournalIssue(BaseModel):
    """A journal issue object that represents an issue of a journal."""

    medium: str
    volume: Union[str, None]
    issue: Union[str, None]
    date: Union[datetime.date, None]
    season: Union[str, None]
    medline_date: Union[str, None]

    @classmethod
    def from_xml(cls, element: ET.Element) -> JournalIssue:
        """Create a JournalIssue from an XML element.

        Args:
            element (ET.Element): The XML element to create the JournalIssue from.

        Returns:
            JournalIssue: The JournalIssue created from the XML element.
        """
        if element.find(".//PubDate") is not None:
            _year = (
                int(element.find(".//PubDate//Year").text)
                if element.find(".//PubDate//Year") is not None
                else None
            )
            if element.find(".//PubDate//Month") is not None:
                _month = element.find(".//PubDate//Month").text
                try:
                    _month = int(_month)
                except ValueError:
                    _month = int(MONTHS[_month])
            else:
                _month = None

            if not _year or not _month:
                _date = None
            else:
                _date = datetime.date(year=_year, month=_month, day=1)

        return cls(
            medium=element.attrib.get("CitedMedium"),
            volume=find_or_none(element, ".//Volume"),
            issue=find_or_none(element, ".//Issue"),
            date=_date,
            season=find_or_none(element, ".//PubDate//Season"),
            medline_date=find_or_none(element, ".//PubDate//MedlineDate"),
        )


class Issn(BaseModel):
    """An ISSN object that represents an ISSN of a journal."""

    type: str
    value: str

    @classmethod
    def from_xml(cls, element: ET.Element) -> Issn:
        """Create an Issn from an XML element.

        Args:
            element (ET.Element): The XML element to create the Issn from.

        Returns:
            Issn: The Issn created from the XML element.
        """
        return cls(type=element.attrib.get("IssnType"), value=element.text)


class Publication(BaseModel):
    """A publication object that represents a publication type of an article."""

    unique_identifier: str
    type: str

    @classmethod
    def from_xml(cls, element: ET.Element) -> Publication:
        """Create a Publication from an XML element.

        Args:
            element (ET.Element): The XML element to create the Publication from.

        Returns:
            Publication: The Publication created from the XML element.
        """
        return cls(unique_identifier=element.attrib.get("UI"), type=element.text)


class ArticleId(BaseModel):
    """An article ID object that represents an article ID."""

    id: Union[str, None]
    id_type: str

    @classmethod
    def from_xml(cls, element: ET.Element) -> ArticleId:
        """Create an ArticleId from an XML element.

        Args:
            element (ET.Element): The XML element to create the ArticleId from.

        Returns:
            ArticleId: The ArticleId created from the XML element.
        """
        return cls(id=element.text, id_type=element.attrib.get("IdType"))


class Author(BaseModel):
    """An author object that represents an author of a publication."""

    valid: bool
    last_name: Union[str, None]
    fore_name: Union[str, None]
    initials: Union[str, None]
    collective_name: Union[str, None]
    affiliation: Union[str, None]
    identifier: Union[Identifier, None]

    @classmethod
    def from_xml(cls, element: ET.Element) -> Author:
        """Create an Author from an XML element.

        Args:
            element (ET.Element): The XML element to create the Author from.

        Returns:
            Author: The Author created from the XML element.
        """
        return cls(
            valid=True if element.attrib.get("ValidYN") == "Y" else False,
            last_name=find_or_none(element, ".//LastName"),
            fore_name=find_or_none(element, ".//ForeName"),
            initials=find_or_none(element, ".//Initials"),
            collective_name=find_or_none(element, ".//CollectiveName"),
            affiliation=find_or_none(element, ".//AffiliationInfo//Affiliation"),
            identifier=(
                Identifier.from_xml(element.find(".//Identifier"))
                if element.find(".//Identifier") is not None
                else None
            ),
        )


class Chemical(BaseModel):
    """A chemical object that represents a chemical used in a publication."""

    registry_number: str
    unique_identifier: Union[str, None]
    name_of_substance: str

    @classmethod
    def from_xml(cls, element: ET.Element) -> Chemical:
        """Create a Chemical from an XML element.

        Args:
            element (ET.Element): The XML element to create the Chemical from.

        Returns:
            Chemical: The Chemical created from the XML element.
        """
        return cls(
            registry_number=element.find(".//RegistryNumber").text,
            unique_identifier=element.attrib.get("UI"),
            name_of_substance=element.find(".//NameOfSubstance").text,
        )


class MedlineCitation(BaseModel):
    """A citation object that represents a citation of a publication."""

    pmid: int
    pmid_version: int
    completed: Union[datetime.date, None]
    revised: datetime.date
    article: Article
    journal_info: MedlineJournalInfo
    chemicals: List[Chemical]
    subset: Union[str, None]
    mesh_headings: List[MeshHeading]
    keywords: Union[List[Keyword], None]
    personal_name_subjects: Union[List[Author], None]
    comments_corrections: Union[List[CommentCorrection], None]
    other_ids: Union[List[Identifier], None]
    other_abstracts: Union[List[OtherAbstract], None]
    general_note: Union[GeneralNote, None]
    space_flight_missions: Union[List[str], None]
    genes: Union[List[str], None]
    gene_symbols: Union[List[str], None]
    supplemental_meshs: Union[List[SupplementalMesh], None]
    investigators: Union[List[Investigator], None]
    coi_statement: Union[str, None]

    @classmethod
    def from_xml(cls, element: ET.Element) -> MedlineCitation:
        """Create a MedlineCitation from an XML element."""
        if element.find(".//DateCompleted") is not None:
            _year = (
                int(element.find(".//DateCompleted//Year").text)
                if element.find(".//DateCompleted//Year") is not None
                else None
            )
            _month = (
                int(element.find(".//DateCompleted//Month").text)
                if element.find(".//DateCompleted//Month") is not None
                else None
            )
            _day = (
                int(element.find(".//DateCompleted//Day").text)
                if element.find(".//DateCompleted//Day") is not None
                else None
            )
            if not _year or not _month:
                _date_completed = None
            else:
                _date_completed = datetime.date(year=_year, month=_month, day=_day)
        else:
            _date_completed = None

        return cls(
            pmid=int(element.find(".//PMID").text),
            pmid_version=int(element.find(".//PMID").attrib.get("Version")),
            completed=_date_completed,
            revised=datetime.date(
                year=int(element.find(".//DateRevised//Year").text),
                month=int(element.find(".//DateRevised//Month").text),
                day=int(element.find(".//DateRevised//Day").text),
            ),
            article=Article.from_xml(element.find(".//Article")),
            journal_info=MedlineJournalInfo.from_xml(
                element.find(".//MedlineJournalInfo")
            ),
            chemicals=[
                Chemical.from_xml(item)
                for item in element.findall(".//ChemicalList//Chemical")
            ],
            subset=find_or_none(element, ".//CitationSubset"),
            mesh_headings=[
                MeshHeading.from_xml(item)
                for item in element.findall(".//MeshHeadingList//MeshHeading")
            ],
            keywords=[
                Keyword.from_xml(item)
                for item in element.findall(".//KeywordList//Keyword")
            ]
            if element.find(".//KeywordList") is not None
            else None,
            personal_name_subjects=[
                Author.from_xml(item)
                for item in element.findall(
                    ".//PersonalNameSubjectList//PersonalNameSubject"
                )
            ]
            if element.find(".//PersonalNameSubjectList") is not None
            else None,
            comments_corrections=[
                CommentCorrection.from_xml(item)
                for item in element.findall(
                    ".//CommentsCorrectionsList//CommentsCorrections"
                )
            ]
            if element.find(".//CommentsCorrectionsList") is not None
            else None,
            other_ids=[
                Identifier.from_xml(item) for item in element.findall(".//OtherID")
            ]
            if element.find(".//OtherID") is not None
            else None,
            other_abstracts=[
                OtherAbstract.from_xml(item)
                for item in element.findall(".//OtherAbstract")
            ]
            if element.find(".//OtherAbstract") is not None
            else None,
            general_note=(
                GeneralNote.from_xml(element.find(".//GeneralNote"))
                if element.find(".//GeneralNote") is not None
                else None
            ),
            space_flight_missions=[
                item.text for item in element.findall(".//SpaceFlightMission")
            ]
            if element.find(".//SpaceFlightMission") is not None
            else None,
            genes=[
                item.text for item in element.findall(".//GeneSymbolList//GeneSymbol")
            ]
            if element.find(".//GeneSymbolList") is not None
            else None,
            gene_symbols=[
                item.text for item in element.findall(".//GeneSymbolList//GeneSymbol")
            ]
            if element.find(".//GeneSymbolList") is not None
            else None,
            supplemental_meshs=[
                SupplementalMesh.from_xml(item)
                for item in element.findall(".//SupplMeshList//SupplMeshName")
            ]
            if element.find(".//SupplMeshList") is not None
            else None,
            investigators=[
                Investigator.from_xml(item)
                for item in element.findall(".//InvestigatorList//Investigator")
            ]
            if element.find(".//InvestigatorList") is not None
            else None,
            coi_statement=(
                "".join(element.find(".//CoiStatement").itertext())
                if element.find(".//CoiStatement") is not None
                else None
            ),
        )


class Investigator(BaseModel):
    """An investigator object that represents an investigator of a publication."""

    last_name: str
    fore_name: Union[str, None]
    initials: Union[str, None]
    suffix: Union[str, None]
    affiliation: Union[str, None]
    identifier: Union[Identifier, None]
    valid: bool

    @classmethod
    def from_xml(cls, element: ET.Element) -> Investigator:
        """Create an Investigator from an XML element."""
        return cls(
            last_name=element.find(".//LastName").text,
            fore_name=find_or_none(element, ".//ForeName"),
            initials=find_or_none(element, ".//Initials"),
            suffix=find_or_none(element, ".//Suffix"),
            affiliation=(
                "".join(element.find(".//AffiliationInfo//Affiliation").itertext())
                if element.find(".//AffiliationInfo//Affiliation") is not None
                else None
            ),
            identifier=(
                Identifier.from_xml(element.find(".//Identifier"))
                if element.find(".//Identifier") is not None
                else None
            ),
            valid=True if element.attrib.get("ValidYN") == "Y" else False,
        )


class SupplementalMesh(BaseModel):
    """A supplemental mesh object that represents a supplemental mesh used in a publication."""

    type: str
    ui: str
    name: str

    @classmethod
    def from_xml(cls, element: ET.Element) -> SupplementalMesh:
        """Create a SupplementalMesh from an XML element."""
        return cls(
            type=element.attrib.get("Type"),
            ui=element.attrib.get("UI"),
            name=element.text,
        )


class Grant(BaseModel):
    """A grant object that represents a grant of a publication."""

    id: Union[str, None]
    acronym: Union[str, None]
    agency: Union[str, None]
    country: Union[str, None]

    @classmethod
    def from_xml(cls, element: ET.Element) -> Grant:
        """Create a Grant from an XML element."""
        return cls(
            id=find_or_none(element, ".//GrantID"),
            acronym=find_or_none(element, ".//Acronym"),
            agency=find_or_none(element, ".//Agency"),
            country=find_or_none(element, ".//Country"),
        )


class OtherAbstract(BaseModel):
    """An other abstract object that represents an other abstract of a publication."""

    text: str
    source: Union[str, None]
    language: str

    @classmethod
    def from_xml(cls, element: ET.Element) -> OtherAbstract:
        """Create an OtherAbstract from an XML element."""
        return cls(
            text="".join(element.find(".//AbstractText").itertext()),
            source=element.attrib.get("Source"),
            language=element.attrib.get("Language"),
        )


class Identifier(BaseModel):
    """An identifier object that represents an identifier of a publication or an author."""

    id: str
    source: str

    @classmethod
    def from_xml(cls, element: ET.Element) -> Identifier:
        """Create an Identifier from an XML element."""
        return cls(id=element.text, source=element.attrib.get("Source"))


class MedlineJournalInfo(BaseModel):
    """A journal info object that represents information about a journal."""

    country: Union[str, None]
    title_abbreviation: str
    nlm_unique_id: str
    issn_linking: Union[str, None]

    @classmethod
    def from_xml(cls, element: ET.Element) -> MedlineJournalInfo:
        """Create a MedlineJournalInfo from an XML element."""
        return cls(
            country=find_or_none(element, ".//Country"),
            title_abbreviation=element.find(".//MedlineTA").text,
            nlm_unique_id=element.find(".//NlmUniqueID").text,
            issn_linking=find_or_none(element, ".//ISSNLinking"),
        )


class CommentCorrection(BaseModel):
    """A comment correction object that represents a comment or correction of a publication."""

    pmid: Union[int, None]
    pmid_version: Union[int, None]
    ref_source: str
    ref_type: str

    @classmethod
    def from_xml(cls, element: ET.Element) -> CommentCorrection:
        """Create a CommentCorrection from an XML element."""
        return cls(
            pmid=find_or_none(element, ".//PMID"),
            pmid_version=(
                int(element.find(".//PMID").attrib.get("Version"))
                if element.find(".//PMID") is not None
                else None
            ),
            ref_source=element.find(".//RefSource").text,
            ref_type=element.attrib.get("RefType"),
        )


class MeshHeading(BaseModel):
    """A mesh heading object that represents a mesh heading used in a publication."""

    descriptor: Topic
    qualifier: Union[Topic, None]

    @classmethod
    def from_xml(cls, element: ET.Element) -> MeshHeading:
        """Create a MeshHeading from an XML element."""
        _qualifier = (
            Topic.from_xml(element.find(".//QualifierName"))
            if element.find(".//QualifierName") is not None
            else None
        )

        return cls(
            descriptor=Topic.from_xml(element.find(".//DescriptorName")),
            qualifier=_qualifier,
        )


class GeneralNote(BaseModel):
    """A general note object that represents a general note of a publication."""

    owner: str
    note: str

    @classmethod
    def from_xml(cls, element: ET.Element) -> GeneralNote:
        """Create a GeneralNote from an XML element."""
        return cls(owner=element.attrib.get("Owner"), note=element.text)


class Keyword(BaseModel):
    """A keyword object that represents a keyword used in a publication."""

    major_topic: bool
    text: str

    @classmethod
    def from_xml(cls, element: ET.Element) -> Keyword:
        """Create a Keyword from an XML element."""
        return cls(
            major_topic=True if element.attrib.get("MajorTopicYN") == "Y" else False,
            text="".join(element.itertext()),
        )


class Topic(BaseModel):
    """A descriptor object that represents a descriptor used in a publication."""

    major_topic: bool
    unique_identifier: str
    name: str

    @classmethod
    def from_xml(cls, element: ET.Element) -> Topic:
        """Create a Topic from an XML element."""
        return cls(
            major_topic=True if element.attrib.get("MajorTopicYN") == "Y" else False,
            unique_identifier=element.attrib.get("UI"),
            name=element.text,
        )


class PubMedPubDate(BaseModel):
    """A PubMed publication date object that represents a publication date."""

    publication_status: str
    date: datetime.date

    @classmethod
    def from_xml(cls, element: ET.Element) -> PubMedPubDate:
        """Create a PubMedPubDate from an XML element.

        Args:
            element (ET.Element): The XML element to create the PubMedPubDate from.

        Returns:
            PubMedPubDate: The PubMedPubDate created from the XML element.
        """
        try:
            _year = int(element.find(".//Year").text)
            _month = int(element.find(".//Month").text)
            _day = int(element.find(".//Day").text)
            _date = datetime.date(year=_year, month=_month, day=_day)
        except ValueError as e:
            if _month == 2 and _day == 29:
                _date = datetime.date(year=_year, month=_month, day=28)
            else:
                raise ValueError(
                    f"Failed to parse PubMedPubDate: {e}\n\n"
                    f"year = {element.find('.//Year').text}\n"
                    f"month = {element.find('.//Month').text}\n"
                    f"day = {element.find('.//Day').text}"
                )

        return cls(publication_status=element.attrib.get("PubStatus"), date=_date)


class PubmedData(BaseModel):
    """A PubMed data object that represents the data of a publication."""

    article_ids: List[ArticleId]
    publication_status: str
    history: List[PubMedPubDate]
    references: List[Reference]

    @classmethod
    def from_xml(cls, element: ET.Element) -> PubmedData:
        """Create a PubmedData from an XML element.

        Args:
            element (ET.Element): The XML element to create the PubmedData from.

        Returns:
            PubmedData: The PubmedData created from the XML element.
        """
        _article_ids = [
            ArticleId.from_xml(item)
            for item in element.findall(".//ArticleIdList//ArticleId")
        ]
        _history = [
            PubMedPubDate.from_xml(item)
            for item in element.findall(".//History//PubMedPubDate")
        ]
        _references = [
            Reference.from_xml(item)
            for item in element.findall(".//ReferenceList//Reference")
        ]
        _nested_references = [
            Reference.from_xml(item)
            for item in element.findall(".//ReferenceList//ReferenceList//Reference")
        ]
        _nested_nested_references = [
            Reference.from_xml(item)
            for item in element.findall(
                ".//ReferenceList//ReferenceList//ReferenceList//Reference"
            )
        ]

        return cls(
            article_ids=_article_ids,
            publication_status=element.find(".//PublicationStatus").text,
            history=_history,
            references=_references + _nested_references + _nested_nested_references,
        )


class PubmedItem(BaseModel):
    """A PubMed item object that represents a publication in PubMed."""

    citation: MedlineCitation
    data: PubmedData

    @classmethod
    def from_xml(cls, element: ET.Element) -> PubmedItem:
        """Create a PubmedItem from an XML element.

        Args:
            element (ET.Element): The XML element to create the PubmedItem from.

        Returns:
            PubmedItem: The PubmedItem created from the XML element.
        """
        _citation = MedlineCitation.from_xml(element.find(".//MedlineCitation"))
        _data = PubmedData.from_xml(element.find(".//PubmedData"))

        return cls(citation=_citation, data=_data)

    def prepare_to_ingestion(self) -> Union[Tuple[str, dict, int], None]:
        """Prepare the item for ingestion into the vector database.

        If the item has an abstract, it will be used as the text. Otherwise, a None will be returned to skip the item.
        """
        _abstract = self.citation.article.abstract

        if _abstract:
            _title = self.citation.article.title
            _dump = self.model_dump()
            _metadata = {**_dump["citation"], **_dump["data"]}

            return (f"{_title} {_abstract}", _metadata, self.citation.pmid,)
        else:
            return None


class Reference(BaseModel):
    """A reference object that represents a reference in a publication."""

    citation: str
    article_ids: List[ArticleId]

    @classmethod
    def from_xml(cls, element: ET.Element) -> Reference:
        """Create a Reference from an XML element."""
        _article_ids = [
            ArticleId.from_xml(item)
            for item in element.findall(".//ArticleIdList//ArticleId")
        ]

        return cls(
            citation="".join(element.find(".//Citation").itertext()),
            article_ids=_article_ids,
        )
