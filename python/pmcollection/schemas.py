"""All data schemas that are used to manipulate data in the database."""

from __future__ import annotations

import datetime
from typing import List, Tuple, Union

from pydantic import BaseModel
from rxml import Node, SearchType

from pmcollection.constants import MONTHS
from pmcollection.utils import define_datetime_from_node, find_tag_or_none


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
    def from_xml(cls, node: Node) -> Article:
        """Create an Article from an XML node.

        Args:
            node (Node): The XML node to create the Article from.

        Returns:
            Article: The Article created from the XML node.
        """
        _abstract = node.search(by=SearchType.Tag, value="AbstractText")

        return cls(
            publication_model=node.attrs.get("PubModel"),
            journal=Journal.from_xml(node.search(by=SearchType.Tag, value="Journal")[0]),
            title=node.search(by=SearchType.Tag, value="ArticleTitle")[0].text,
            abstract=find_tag_or_none(node, "AbstractText"),
            pagination=find_tag_or_none(node, "MedlinePgn"),
            authors=[
                Author.from_xml(item)
                for item in node.findall(".//AuthorList//Author")
            ],
            language=node.find(".//Language").text,
            date=(
                datetime.date(
                    year=int(node.find(".//ArticleDate//Year").text),
                    month=int(node.find(".//ArticleDate//Month").text),
                    day=int(node.find(".//ArticleDate//Day").text),
                )
                if node.find(".//ArticleDate") is not None
                else None
            ),
            grants=[
                Grant.from_xml(item) for item in node.findall(".//GrantList//Grant")
            ]
            if node.find(".//GrantList") is not None
            else None,
            publication_types=[
                Publication.from_xml(item)
                for item in node.findall(".//PublicationTypeList//PublicationType")
            ],
            elocation_id=(
                ELocationId.from_xml(node.find(".//ELocationID"))
                if node.find(".//ELocationID") is not None
                else None
            ),
            vernacular_title=(
                "".join(node.find(".//VernacularTitle").itertext())
                if node.find(".//VernacularTitle") is not None
                else None
            ),
            data_banks=[
                DataBank.from_xml(item)
                for item in node.findall(".//DataBankList//DataBank")
            ]
            if node.find(".//DataBankList") is not None
            else None,
            copyright_information=(
                node.find(".//Abstract//CopyrightInformation").text
                if node.find(".//Abstract//CopyrightInformation") is not None
                else None
            ),
        )


class DataBank(BaseModel):
    """A data bank object that represents a data bank used in a publication."""

    name: str
    accession_numbers: List[str]
    complete: bool

    @classmethod
    def from_xml(cls, node: Node) -> DataBank:
        """Create a DataBank from an XML node.

        Args:
            node (Node): The XML node to create the DataBank from.

        Returns:
            DataBank: The DataBank created from the XML node.
        """
        return cls(
            name=node.find(".//DataBankName").text,
            accession_numbers=[
                item.text
                for item in node.findall(".//AccessionNumberList//AccessionNumber")
            ],
            complete=True if node.attrib.get("CompleteYN") == "Y" else False,
        )


class ELocationId(BaseModel):
    """An ELocation ID object that represents an ELocation ID of a publication."""

    id_type: str
    valid: bool
    value: str

    @classmethod
    def from_xml(cls, node: Node) -> ELocationId:
        """Create an ELocationId from an XML node.

        Args:
            node (Node): The XML node to create the ELocationId from.

        Returns:
            ELocationId: The ELocationId created from the XML node.
        """
        return cls(
            id_type=node.attrib.get("EIdType"),
            valid=True if node.attrib.get("ValidYN") == "Y" else False,
            value=node.text,
        )


class Journal(BaseModel):
    """A journal object that represents a journal in a publication."""

    issn: Union[Issn, None]
    issue: JournalIssue
    title: str
    iso_abbreviation: str

    @classmethod
    def from_xml(cls, node: Node) -> Journal:
        """Create a Journal from an XML node.

        Args:
            node (Node): The XML node to create the Journal from.

        Returns:
            Journal: The Journal created from the XML node.
        """
        _issn = node.search(by=SearchType.Tag, value="ISSN")

        return cls(
            issn=Issn.from_xml(_issn[0]) if _issn else None,
            issue=JournalIssue.from_xml(node.search(SearchType.Tag, "JournalIssue")[0]),
            title=node.search(SearchType.Tag, "Title")[0].text,
            iso_abbreviation=node.search(SearchType.Tag, "ISOAbbreviation")[0].text,
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
    def from_xml(cls, node: Node) -> JournalIssue:
        """Create a JournalIssue from an XML node.

        Args:
            node (Node): The XML node to create the JournalIssue from.

        Returns:
            JournalIssue: The JournalIssue created from the XML node.
        """
        _date = define_datetime_from_node(node.search(by=SearchType.Tag, value="PubDate"))

        return cls(
            medium=node.attrs.get("CitedMedium"),
            volume=find_tag_or_none(node, "Volume"),
            issue=find_tag_or_none(node, "Issue"),
            date=_date,
            season=find_tag_or_none(node, "Season"),
            medline_date=find_tag_or_none(node, "MedlineDate"),
        )


class Issn(BaseModel):
    """An ISSN object that represents an ISSN of a journal."""

    type: str
    value: str

    @classmethod
    def from_xml(cls, node: Node) -> Issn:
        """Create an Issn from an XML node.

        Args:
            node (Node): The XML node to create the Issn from.

        Returns:
            Issn: The Issn created from the XML node.
        """
        return cls(type=node.attrs.get("IssnType"), value=node.text)


class Publication(BaseModel):
    """A publication object that represents a publication type of an article."""

    unique_identifier: str
    type: str

    @classmethod
    def from_xml(cls, node: Node) -> Publication:
        """Create a Publication from an XML node.

        Args:
            node (Node): The XML node to create the Publication from.

        Returns:
            Publication: The Publication created from the XML node.
        """
        return cls(unique_identifier=node.attrib.get("UI"), type=node.text)


class ArticleId(BaseModel):
    """An article ID object that represents an article ID."""

    id: Union[str, None]
    id_type: str

    @classmethod
    def from_xml(cls, node: Node) -> ArticleId:
        """Create an ArticleId from an XML node.

        Args:
            node (Node): The XML node to create the ArticleId from.

        Returns:
            ArticleId: The ArticleId created from the XML node.
        """
        return cls(id=node.text, id_type=node.attrib.get("IdType"))


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
    def from_xml(cls, node: Node) -> Author:
        """Create an Author from an XML node.

        Args:
            node (Node): The XML node to create the Author from.

        Returns:
            Author: The Author created from the XML node.
        """
        return cls(
            valid=True if node.attrib.get("ValidYN") == "Y" else False,
            last_name=find_tag_or_none(node, ".//LastName"),
            fore_name=find_tag_or_none(node, ".//ForeName"),
            initials=find_tag_or_none(node, ".//Initials"),
            collective_name=find_tag_or_none(node, ".//CollectiveName"),
            affiliation=find_tag_or_none(node, ".//AffiliationInfo//Affiliation"),
            identifier=(
                Identifier.from_xml(node.find(".//Identifier"))
                if node.find(".//Identifier") is not None
                else None
            ),
        )


class Chemical(BaseModel):
    """A chemical object that represents a chemical used in a publication."""

    registry_number: str
    unique_identifier: Union[str, None]
    name_of_substance: str

    @classmethod
    def from_xml(cls, node: Node) -> Chemical:
        """Create a Chemical from an XML node.

        Args:
            node (Node): The XML node to create the Chemical from.

        Returns:
            Chemical: The Chemical created from the XML node.
        """
        return cls(
            registry_number=node.find(".//RegistryNumber").text,
            unique_identifier=node.attrib.get("UI"),
            name_of_substance=node.find(".//NameOfSubstance").text,
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
    gene_symbols: Union[List[str], None]
    supplemental_meshs: Union[List[SupplementalMesh], None]
    investigators: Union[List[Investigator], None]
    coi_statement: Union[str, None]

    @classmethod
    def from_xml(cls, node: Node) -> MedlineCitation:
        """Create a MedlineCitation from an XML node."""
        _date_completed = define_datetime_from_node(node.search(by=SearchType.Tag, value="DateCompleted"))
        _date_revised = define_datetime_from_node(node.search(by=SearchType.Tag, value="DateRevised"))

        _keywords = node.search(by=SearchType.Tag, value="KeywordList")
        _personal_name_subjects = node.search(by=SearchType.Tag, value="PersonalNameSubjectList")
        _comments_corrections = node.search(by=SearchType.Tag, value="CommentsCorrectionsList")
        _other_ids = node.search(by=SearchType.Tag, value="OtherID")
        _other_abstracts = node.search(by=SearchType.Tag, value="OtherAbstract")
        _general_note = node.search(by=SearchType.Tag, value="GeneralNote")
        _space_flight_missions = node.search(by=SearchType.Tag, value="SpaceFlightMission")
        _gene_symbols = node.search(by=SearchType.Tag, value="GeneSymbolList")
        _supplemental_meshs = node.search(by=SearchType.Tag, value="SupplMeshList")
        _investigators = node.search(by=SearchType.Tag, value="InvestigatorList")

        return cls(
            pmid=int(node.children[0].text),
            pmid_version=int(node.children[0].attrs.get("Version")),
            completed=_date_completed,
            revised=_date_revised,
            article=Article.from_xml(node.search(by=SearchType.Tag, value="Article")[0]),
            journal_info=MedlineJournalInfo.from_xml(
                node.search(by=SearchType.Tag, value="MedlineJournalInfo")[0]
            ),
            chemicals=[
                Chemical.from_xml(item)
                for item in node.search(by=SearchType.Tag, value="Chemical")
            ],
            subset=find_tag_or_none(node, "CitationSubset"),
            mesh_headings=[
                MeshHeading.from_xml(item)
                for item in node.search(by=SearchType.Tag, value="MeshHeading")
            ],
            keywords=[
                Keyword.from_xml(item)
                for item in node.search(by=SearchType.Tag, value="Keyword")
            ]
            if _keywords
            else None,
            personal_name_subjects=[
                Author.from_xml(item)
                for item in node.search(by=SearchType.Tag, value="PersonalNameSubject")
            ]
            if _personal_name_subjects
            else None,
            comments_corrections=[
                CommentCorrection.from_xml(item)
                for item in node.search(by=SearchType.Tag, value="CommentsCorrections")
            ]
            if _comments_corrections
            else None,
            other_ids=[Identifier.from_xml(item) for item in _other_ids] if _other_ids else None,
            other_abstracts=[OtherAbstract.from_xml(item) for item in _other_abstracts] if _other_abstracts else None,
            general_note=GeneralNote.from_xml(_general_note[0]) if _general_note else None,
            space_flight_missions=[item.text for item in _space_flight_missions] if _space_flight_missions else None,
            genes_symbols=[item.text for item in _gene_symbols] if _gene_symbols else None,
            supplemental_meshs=[
                SupplementalMesh.from_xml(item) for item in _supplemental_meshs
            ] if _supplemental_meshs else None,
            investigators=[Investigator.from_xml(item) for item in _investigators] if _investigators else None,
            coi_statement=find_tag_or_none(node, "CoiStatement"),
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
    def from_xml(cls, node: Node) -> Investigator:
        """Create an Investigator from an XML node."""
        return cls(
            last_name=node.find(".//LastName").text,
            fore_name=find_tag_or_none(node, ".//ForeName"),
            initials=find_tag_or_none(node, ".//Initials"),
            suffix=find_tag_or_none(node, ".//Suffix"),
            affiliation=(
                "".join(node.find(".//AffiliationInfo//Affiliation").itertext())
                if node.find(".//AffiliationInfo//Affiliation") is not None
                else None
            ),
            identifier=(
                Identifier.from_xml(node.find(".//Identifier"))
                if node.find(".//Identifier") is not None
                else None
            ),
            valid=True if node.attrib.get("ValidYN") == "Y" else False,
        )


class SupplementalMesh(BaseModel):
    """A supplemental mesh object that represents a supplemental mesh used in a publication."""

    type: str
    ui: str
    name: str

    @classmethod
    def from_xml(cls, node: Node) -> SupplementalMesh:
        """Create a SupplementalMesh from an XML node."""
        return cls(
            type=node.attrib.get("Type"),
            ui=node.attrib.get("UI"),
            name=node.text,
        )


class Grant(BaseModel):
    """A grant object that represents a grant of a publication."""

    id: Union[str, None]
    acronym: Union[str, None]
    agency: Union[str, None]
    country: Union[str, None]

    @classmethod
    def from_xml(cls, node: Node) -> Grant:
        """Create a Grant from an XML node."""
        return cls(
            id=find_tag_or_none(node, ".//GrantID"),
            acronym=find_tag_or_none(node, ".//Acronym"),
            agency=find_tag_or_none(node, ".//Agency"),
            country=find_tag_or_none(node, ".//Country"),
        )


class OtherAbstract(BaseModel):
    """An other abstract object that represents an other abstract of a publication."""

    text: str
    source: Union[str, None]
    language: str

    @classmethod
    def from_xml(cls, node: Node) -> OtherAbstract:
        """Create an OtherAbstract from an XML node."""
        return cls(
            text="".join(node.find(".//AbstractText").itertext()),
            source=node.attrib.get("Source"),
            language=node.attrib.get("Language"),
        )


class Identifier(BaseModel):
    """An identifier object that represents an identifier of a publication or an author."""

    id: str
    source: str

    @classmethod
    def from_xml(cls, node: Node) -> Identifier:
        """Create an Identifier from an XML node."""
        return cls(id=node.text, source=node.attrib.get("Source"))


class MedlineJournalInfo(BaseModel):
    """A journal info object that represents information about a journal."""

    country: Union[str, None]
    title_abbreviation: str
    nlm_unique_id: str
    issn_linking: Union[str, None]

    @classmethod
    def from_xml(cls, node: Node) -> MedlineJournalInfo:
        """Create a MedlineJournalInfo from an XML node."""
        return cls(
            country=find_tag_or_none(node, ".//Country"),
            title_abbreviation=node.find(".//MedlineTA").text,
            nlm_unique_id=node.find(".//NlmUniqueID").text,
            issn_linking=find_tag_or_none(node, ".//ISSNLinking"),
        )


class CommentCorrection(BaseModel):
    """A comment correction object that represents a comment or correction of a publication."""

    pmid: Union[int, None]
    pmid_version: Union[int, None]
    ref_source: str
    ref_type: str

    @classmethod
    def from_xml(cls, node: Node) -> CommentCorrection:
        """Create a CommentCorrection from an XML node."""
        return cls(
            pmid=find_tag_or_none(node, ".//PMID"),
            pmid_version=(
                int(node.find(".//PMID").attrib.get("Version"))
                if node.find(".//PMID") is not None
                else None
            ),
            ref_source=node.find(".//RefSource").text,
            ref_type=node.attrib.get("RefType"),
        )


class MeshHeading(BaseModel):
    """A mesh heading object that represents a mesh heading used in a publication."""

    descriptor: Topic
    qualifier: Union[Topic, None]

    @classmethod
    def from_xml(cls, node: Node) -> MeshHeading:
        """Create a MeshHeading from an XML node."""
        _qualifier = (
            Topic.from_xml(node.find(".//QualifierName"))
            if node.find(".//QualifierName") is not None
            else None
        )

        return cls(
            descriptor=Topic.from_xml(node.find(".//DescriptorName")),
            qualifier=_qualifier,
        )


class GeneralNote(BaseModel):
    """A general note object that represents a general note of a publication."""

    owner: str
    note: str

    @classmethod
    def from_xml(cls, node: Node) -> GeneralNote:
        """Create a GeneralNote from an XML node."""
        return cls(owner=node.attrib.get("Owner"), note=node.text)


class Keyword(BaseModel):
    """A keyword object that represents a keyword used in a publication."""

    major_topic: bool
    text: str

    @classmethod
    def from_xml(cls, node: Node) -> Keyword:
        """Create a Keyword from an XML node."""
        return cls(
            major_topic=True if node.attrib.get("MajorTopicYN") == "Y" else False,
            text="".join(node.itertext()),
        )


class Topic(BaseModel):
    """A descriptor object that represents a descriptor used in a publication."""

    major_topic: bool
    unique_identifier: str
    name: str

    @classmethod
    def from_xml(cls, node: Node) -> Topic:
        """Create a Topic from an XML node."""
        return cls(
            major_topic=True if node.attrib.get("MajorTopicYN") == "Y" else False,
            unique_identifier=node.attrib.get("UI"),
            name=node.text,
        )


class PubMedPubDate(BaseModel):
    """A PubMed publication date object that represents a publication date."""

    publication_status: str
    date: datetime.date

    @classmethod
    def from_xml(cls, node: Node) -> PubMedPubDate:
        """Create a PubMedPubDate from an XML node.

        Args:
            node (Node): The XML node to create the PubMedPubDate from.

        Returns:
            PubMedPubDate: The PubMedPubDate created from the XML node.
        """
        try:
            _year = int(node.find(".//Year").text)
            _month = int(node.find(".//Month").text)
            _day = int(node.find(".//Day").text)
            _date = datetime.date(year=_year, month=_month, day=_day)
        except ValueError as e:
            if _month == 2 and _day == 29:
                _date = datetime.date(year=_year, month=_month, day=28)
            else:
                raise ValueError(
                    f"Failed to parse PubMedPubDate: {e}\n\n"
                    f"year = {node.find('.//Year').text}\n"
                    f"month = {node.find('.//Month').text}\n"
                    f"day = {node.find('.//Day').text}"
                )

        return cls(publication_status=node.attrib.get("PubStatus"), date=_date)


class PubmedData(BaseModel):
    """A PubMed data object that represents the data of a publication."""

    article_ids: List[ArticleId]
    publication_status: str
    history: List[PubMedPubDate]
    references: List[Reference]

    @classmethod
    def from_xml(cls, node: Node) -> PubmedData:
        """Create a PubmedData from an XML node.

        Args:
            node (Node): The XML node to create the PubmedData from.

        Returns:
            PubmedData: The PubmedData created from the XML node.
        """
        _article_ids = [
            ArticleId.from_xml(item)
            for item in node.findall(".//ArticleIdList//ArticleId")
        ]
        _history = [
            PubMedPubDate.from_xml(item)
            for item in node.findall(".//History//PubMedPubDate")
        ]
        _references = [
            Reference.from_xml(item)
            for item in node.findall(".//ReferenceList//Reference")
        ]
        _nested_references = [
            Reference.from_xml(item)
            for item in node.findall(".//ReferenceList//ReferenceList//Reference")
        ]
        _nested_nested_references = [
            Reference.from_xml(item)
            for item in node.findall(
                ".//ReferenceList//ReferenceList//ReferenceList//Reference"
            )
        ]

        return cls(
            article_ids=_article_ids,
            publication_status=node.find(".//PublicationStatus").text,
            history=_history,
            references=_references + _nested_references + _nested_nested_references,
        )


class PubmedItem(BaseModel):
    """A PubMed item object that represents a publication in PubMed."""

    citation: MedlineCitation
    # data: PubmedData

    @classmethod
    def from_xml(cls, node: Node) -> PubmedItem:
        """Create a PubmedItem from an XML node.

        Args:
            node (Node): The XML node to create the PubmedItem from.

        Returns:
            PubmedItem: The PubmedItem created from the XML node.
        """
        _citation = MedlineCitation.from_xml(node.children[0])
        # _data = PubmedData.from_xml(node.children[1])

        # return cls(citation=_citation, data=_data)
        return cls(citation=_citation)

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
    def from_xml(cls, node: Node) -> Reference:
        """Create a Reference from an XML node."""
        _article_ids = [
            ArticleId.from_xml(item)
            for item in node.findall(".//ArticleIdList//ArticleId")
        ]

        return cls(
            citation="".join(node.find(".//Citation").itertext()),
            article_ids=_article_ids,
        )
