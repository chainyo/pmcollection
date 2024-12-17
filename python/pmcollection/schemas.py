"""All data schemas that are used to manipulate data in the database."""

from __future__ import annotations

import datetime

from pydantic import BaseModel
from rxml import Node

from pmcollection.constants import MONTHS
from pmcollection.utils import find_or_none


class Article(BaseModel):
    """An article object that represents an article in a publication."""

    publication_model: str
    journal: Journal
    title: str
    abstract: str | None
    pagination: str | None
    authors: list[Author]
    language: str
    date: datetime.date | None
    grants: list[Grant] | None
    publication_types: list[Publication]
    elocation_id: ELocationId | None
    vernacular_title: str | None
    data_banks: list[DataBank] | None
    copyright_information: str | None

    @classmethod
    def from_xml(cls, node: Node) -> Article:
        """Create an Article from an XML node.

        Args:
            node (Node): The XML node to create the Article from.

        Returns:
            Article: The Article created from the XML node.
        """
        return cls(
            publication_model=node.attrib.get("PubModel"),
            journal=Journal.from_xml(node.find(".//Journal")),
            title="".join(node.find(".//ArticleTitle").itertext()),
            abstract=(
                "".join(node.find(".//Abstract//AbstractText").itertext())
                if node.find(".//Abstract//AbstractText") is not None
                else None
            ),
            pagination=find_or_none(node, ".//Pagination//MedlinePgn"),
            authors=[
                Author.from_xml(item)
                for item in node.findall(".//Authorlist//Author")
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
                Grant.from_xml(item) for item in node.findall(".//Grantlist//Grant")
            ]
            if node.find(".//Grantlist") is not None
            else None,
            publication_types=[
                Publication.from_xml(item)
                for item in node.findall(".//PublicationTypelist//PublicationType")
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
                for item in node.findall(".//DataBanklist//DataBank")
            ]
            if node.find(".//DataBanklist") is not None
            else None,
            copyright_information=(
                node.find(".//Abstract//CopyrightInformation").text
                if node.find(".//Abstract//CopyrightInformation") is not None
                else None
            ),
        )


class DataBank(BaseModel):
    """A data bank object that represents a data bank used in a publication."""

    name: str | None
    accession_numbers: list[str]
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
                for item in node.findall(".//AccessionNumberlist//AccessionNumber")
                if item is not None and item.text is not None
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

    issn: Issn | None
    issue: JournalIssue
    title: str
    iso_abbreviation: str | None

    @classmethod
    def from_xml(cls, node: Node) -> Journal:
        """Create a Journal from an XML node.

        Args:
            node (Node): The XML node to create the Journal from.

        Returns:
            Journal: The Journal created from the XML node.
        """
        _issn = (
            Issn.from_xml(node.find(".//ISSN"))
            if node.find(".//ISSN") is not None
            else None
        )

        return cls(
            issn=_issn,
            issue=JournalIssue.from_xml(node.find(".//JournalIssue")),
            title=node.find(".//Title").text,
            iso_abbreviation=find_or_none(node, ".//ISOAbbreviation"),
        )


class JournalIssue(BaseModel):
    """A journal issue object that represents an issue of a journal."""

    medium: str
    volume: str | None
    issue: str | None
    date: datetime.date | None
    season: str | None
    medline_date: str | None

    @classmethod
    def from_xml(cls, node: Node) -> JournalIssue:
        """Create a JournalIssue from an XML node.

        Args:
            node (Node): The XML node to create the JournalIssue from.

        Returns:
            JournalIssue: The JournalIssue created from the XML node.
        """
        if node.find(".//PubDate") is not None:
            _year = (
                int(node.find(".//PubDate//Year").text)
                if node.find(".//PubDate//Year") is not None
                else None
            )
            if node.find(".//PubDate//Month") is not None:
                _month = node.find(".//PubDate//Month").text
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
            medium=node.attrib.get("CitedMedium"),
            volume=find_or_none(node, ".//Volume"),
            issue=find_or_none(node, ".//Issue"),
            date=_date,
            season=find_or_none(node, ".//PubDate//Season"),
            medline_date=find_or_none(node, ".//PubDate//MedlineDate"),
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
        return cls(type=node.attrib.get("IssnType"), value=node.text)


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

    id: str | None
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
    last_name: str | None
    fore_name: str | None
    initials: str | None
    collective_name: str | None
    affiliation: str | None
    identifier: Identifier | None

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
            last_name=find_or_none(node, ".//LastName"),
            fore_name=find_or_none(node, ".//ForeName"),
            initials=find_or_none(node, ".//Initials"),
            collective_name=find_or_none(node, ".//CollectiveName"),
            affiliation=find_or_none(node, ".//AffiliationInfo//Affiliation"),
            identifier=(
                Identifier.from_xml(node.find(".//Identifier"))
                if node.find(".//Identifier") is not None
                else None
            ),
        )


class Chemical(BaseModel):
    """A chemical object that represents a chemical used in a publication."""

    registry_number: str
    unique_identifier: str | None
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
    completed: datetime.date | None
    revised: datetime.date
    article: Article
    journal_info: MedlineJournalInfo
    chemicals: list[Chemical]
    subset: str | None
    mesh_headings: list[MeshHeading]
    keywords: list[Keyword] | None
    personal_name_subjects: list[Author] | None
    comments_corrections: list[CommentCorrection] | None
    other_ids: list[Identifier] | None
    other_abstracts: list[OtherAbstract] | None
    general_note: GeneralNote | None
    space_flight_missions: list[str] | None
    genes: list[str] | None
    gene_symbols: list[str] | None
    supplemental_meshs: list[SupplementalMesh] | None
    investigators: list[Investigator] | None
    coi_statement: str | None

    @classmethod
    def from_xml(cls, node: Node) -> MedlineCitation:
        """Create a MedlineCitation from an XML node."""
        if node.find(".//DateCompleted") is not None:
            _year = (
                int(node.find(".//DateCompleted//Year").text)
                if node.find(".//DateCompleted//Year") is not None
                else None
            )
            _month = (
                int(node.find(".//DateCompleted//Month").text)
                if node.find(".//DateCompleted//Month") is not None
                else None
            )
            _day = (
                int(node.find(".//DateCompleted//Day").text)
                if node.find(".//DateCompleted//Day") is not None
                else None
            )
            if not _year or not _month:
                _date_completed = None
            else:
                _date_completed = datetime.date(year=_year, month=_month, day=_day)
        else:
            _date_completed = None

        return cls(
            pmid=int(node.find(".//PMID").text),
            pmid_version=int(node.find(".//PMID").attrib.get("Version")),
            completed=_date_completed,
            revised=datetime.date(
                year=int(node.find(".//DateRevised//Year").text),
                month=int(node.find(".//DateRevised//Month").text),
                day=int(node.find(".//DateRevised//Day").text),
            ),
            article=Article.from_xml(node.find(".//Article")),
            journal_info=MedlineJournalInfo.from_xml(
                node.find(".//MedlineJournalInfo")
            ),
            chemicals=[
                Chemical.from_xml(item)
                for item in node.findall(".//Chemicallist//Chemical")
            ],
            subset=find_or_none(node, ".//CitationSubset"),
            mesh_headings=[
                MeshHeading.from_xml(item)
                for item in node.findall(".//MeshHeadinglist//MeshHeading")
            ],
            keywords=[
                Keyword.from_xml(item)
                for item in node.findall(".//Keywordlist//Keyword")
            ]
            if node.find(".//Keywordlist") is not None
            else None,
            personal_name_subjects=[
                Author.from_xml(item)
                for item in node.findall(
                    ".//PersonalNameSubjectlist//PersonalNameSubject"
                )
            ]
            if node.find(".//PersonalNameSubjectlist") is not None
            else None,
            comments_corrections=[
                CommentCorrection.from_xml(item)
                for item in node.findall(
                    ".//CommentsCorrectionslist//CommentsCorrections"
                )
            ]
            if node.find(".//CommentsCorrectionslist") is not None
            else None,
            other_ids=[
                Identifier.from_xml(item) for item in node.findall(".//OtherID")
            ]
            if node.find(".//OtherID") is not None
            else None,
            other_abstracts=[
                OtherAbstract.from_xml(item)
                for item in node.findall(".//OtherAbstract")
            ]
            if node.find(".//OtherAbstract") is not None
            else None,
            general_note=(
                GeneralNote.from_xml(node.find(".//GeneralNote"))
                if node.find(".//GeneralNote") is not None
                else None
            ),
            space_flight_missions=[
                item.text for item in node.findall(".//SpaceFlightMission")
            ]
            if node.find(".//SpaceFlightMission") is not None
            else None,
            genes=[
                item.text for item in node.findall(".//GeneSymbollist//GeneSymbol")
            ]
            if node.find(".//GeneSymbolList") is not None
            else None,
            gene_symbols=[
                item.text for item in node.findall(".//GeneSymbolList//GeneSymbol")
            ]
            if node.find(".//GeneSymbolList") is not None
            else None,
            supplemental_meshs=[
                SupplementalMesh.from_xml(item)
                for item in node.findall(".//SupplMeshList//SupplMeshName")
            ]
            if node.find(".//SupplMeshList") is not None
            else None,
            investigators=[
                Investigator.from_xml(item)
                for item in node.findall(".//InvestigatorList//Investigator")
            ]
            if node.find(".//InvestigatorList") is not None
            else None,
            coi_statement=(
                "".join(node.find(".//CoiStatement").itertext())
                if node.find(".//CoiStatement") is not None
                else None
            ),
        )


class Investigator(BaseModel):
    """An investigator object that represents an investigator of a publication."""

    last_name: str
    fore_name: str | None
    initials: str | None
    suffix: str | None
    affiliation: str | None
    identifier: Identifier | None
    valid: bool

    @classmethod
    def from_xml(cls, node: Node) -> Investigator:
        """Create an Investigator from an XML node."""
        return cls(
            last_name=node.find(".//LastName").text,
            fore_name=find_or_none(node, ".//ForeName"),
            initials=find_or_none(node, ".//Initials"),
            suffix=find_or_none(node, ".//Suffix"),
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

    id: str | None
    acronym: str | None
    agency: str | None
    country: str | None

    @classmethod
    def from_xml(cls, node: Node) -> Grant:
        """Create a Grant from an XML node."""
        return cls(
            id=find_or_none(node, ".//GrantID"),
            acronym=find_or_none(node, ".//Acronym"),
            agency=find_or_none(node, ".//Agency"),
            country=find_or_none(node, ".//Country"),
        )


class OtherAbstract(BaseModel):
    """An other abstract object that represents an other abstract of a publication."""

    text: str
    source: str | None
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

    country: str | None
    title_abbreviation: str | None
    nlm_unique_id: str
    issn_linking: str | None

    @classmethod
    def from_xml(cls, node: Node) -> MedlineJournalInfo:
        """Create a MedlineJournalInfo from an XML node."""
        return cls(
            country=find_or_none(node, ".//Country"),
            title_abbreviation=find_or_none(node, ".//MedlineTA"),
            nlm_unique_id=node.find(".//NlmUniqueID").text,
            issn_linking=find_or_none(node, ".//ISSNLinking"),
        )


class CommentCorrection(BaseModel):
    """A comment correction object that represents a comment or correction of a publication."""

    pmid: int | None
    pmid_version: int | None
    ref_source: str | None
    ref_type: str | None

    @classmethod
    def from_xml(cls, node: Node) -> CommentCorrection:
        """Create a CommentCorrection from an XML node."""
        return cls(
            pmid=find_or_none(node, ".//PMID"),
            pmid_version=(
                int(node.find(".//PMID").attrib.get("Version"))
                if node.find(".//PMID") is not None
                else None
            ),
            ref_source=find_or_none(node, ".//RefSource"),
            ref_type=node.attrib.get("RefType")
                if node.attrib.get("RefType") is not None
                else None,
        )


class MeshHeading(BaseModel):
    """A mesh heading object that represents a mesh heading used in a publication."""

    descriptor: Topic
    qualifier: Topic | None

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
            if _month == 2 and _day >= 29:
                _date = datetime.date(year=_year, month=_month, day=28)
            elif _day == 31 and _month in [4, 6, 9, 11]:
                _date = datetime.date(year=_year, month=_month, day=30)
            else:
                raise ValueError(
                    f"Failed to parse PubMedPubDate: {e}\n\n"
                    f"year = {node.find('.//Year').text}\n"
                    f"month = {node.find('.//Month').text}\n"
                    f"day = {node.find('.//Day').text}"
                ) from e

        return cls(publication_status=node.attrib.get("PubStatus"), date=_date)


class PubmedData(BaseModel):
    """A PubMed data object that represents the data of a publication."""

    article_ids: list[ArticleId]
    publication_status: str
    history: list[PubMedPubDate]
    references: list[Reference]

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
            for item in node.findall(".//ArticleIdlist//ArticleId")
        ]
        _history = [
            PubMedPubDate.from_xml(item)
            for item in node.findall(".//History//PubMedPubDate")
        ]
        _references = [
            Reference.from_xml(item)
            for item in node.findall(".//Referencelist//Reference")
        ]
        _nested_references = [
            Reference.from_xml(item)
            for item in node.findall(".//Referencelist//Referencelist//Reference")
        ]
        _nested_nested_references = [
            Reference.from_xml(item)
            for item in node.findall(
                ".//Referencelist//Referencelist//Referencelist//Reference"
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
    data: PubmedData

    @classmethod
    def from_xml(cls, node: Node) -> PubmedItem:
        """Create a PubmedItem from an XML node.

        Args:
            node (Node): The XML node to create the PubmedItem from.

        Returns:
            PubmedItem: The PubmedItem created from the XML node.
        """
        _citation = MedlineCitation.from_xml(node.children[0])
        _data = PubmedData.from_xml(node.children[1])

        return cls(citation=_citation, data=_data)

    def prepare_to_ingestion(self) -> tuple[str, dict, int] | None:
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
    article_ids: list[ArticleId]

    @classmethod
    def from_xml(cls, node: Node) -> Reference:
        """Create a Reference from an XML node."""
        _article_ids = [
            ArticleId.from_xml(item)
            for item in node.findall(".//ArticleIdlist//ArticleId")
        ]

        return cls(
            citation="".join(node.find(".//Citation").itertext()),
            article_ids=_article_ids,
        )
