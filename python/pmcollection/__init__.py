from pmcollection._lowlevel import download_files


__all__ = ["download_files"]


async def download_files_python(urls, cache_folder, concurrency_limit):
    await download_files(urls, cache_folder, concurrency_limit)


if __name__ == "__main__":
    # import asyncio

    # urls = [
    #     f"https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/pubmed24n{i:04d}.xml.gz"
    #     for i in range(1, 1219)
    # ]
    # cache_folder_python = "./tmp"
    # concurrency_limit = 20

    # asyncio.run(download_files_python(urls, cache_folder_python, concurrency_limit))
    import time
    from pmcollection.schemas import PubmedItem
    from rxml import read_file, SearchType
    from pathlib import Path
    from rich.progress import track

    list_files = list(Path("tmp").glob("*.xml"))

    for it, file in enumerate(list_files):
        print(f"Processing file {it + 1}/{len(list_files)}")
        root_node = read_file(str(file), "PubmedArticleSet")
        for node in track(
            root_node.children,
            description="Loading items",
            total=len(root_node.children),
        ):
            try:
                item_load = time.time()
                item = PubmedItem.from_xml(node)
                item_load_end = time.time()
            except Exception as err:
                # kws = node.search(by=SearchType.Tag, value="GeneSymbolList")
                # for k in kws:
                #     print(k.children)
                raise err from err

    # print(f"Read file in {end - start:.2f} seconds")
    # print(f"Load item in {item_load_end - item_load:.2f} seconds")
