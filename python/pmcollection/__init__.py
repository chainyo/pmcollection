from pmcollection._lowlevel import download_files

__all__ = ["download_files"]


async def download_files_python(urls, cache_folder, concurrency_limit):
    await download_files(urls, cache_folder, concurrency_limit)


if __name__ == "__main__":
    # import asyncio

    # urls = [
    #     f"https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/pubmed24n{i:04d}.xml.gz"
    #     for i in range(1, 11)  # Use the first 10 files for benchmarking
    # ]
    # cache_folder_python = "./tmp"
    # concurrency_limit = 20

    # asyncio.run(download_files_python(urls, cache_folder_python, concurrency_limit))
    from pmcollection.schemas import PubmedItem
    from rxml import read_file, SearchType

    root_node = read_file("tmp/pubmed24n0001.xml", "PubmedArticleSet")
    for node in root_node.children:
        item = PubmedItem.from_xml(node)
        print(item)
        # print(node.search(SearchType.Tag, "Chemical"))
        # _node = node.children[0]
        # print(_node.name)
        # print(_node.text)
        # print(_node.attrs)
        # print(_node.children)

        break
