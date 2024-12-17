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
    from rxml import read_file

    root_node = read_file("tmp/pubmed24n0001.xml", "PubmedArticleSet")
    print(len(root_node.children))
    for node in root_node.children:
        print(node.name)
        print(node.text)
        print(node.attrs)
        print(node.children)
        item = PubmedItem.from_xml(node)
        print(item)
        break
