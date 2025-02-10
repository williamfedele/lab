from xml.etree.ElementTree import iterparse
import re
from pathlib import Path
import os
import multiprocessing


# Create a file using title, insert links into the file in obsidian format [[link_label]]
def convert_page_to_obsidian(title, links, output_path):
    def sanitize_filename(title):
        safe_title = re.sub(r'[<>:"/\\|?*#\[\]]', "_", title)
        return safe_title[:240] + ".md"

    filename = sanitize_filename(title)
    file_path = output_path / filename

    with open(file_path, "w", encoding="utf-8") as f:
        links = [link for link in links if link is not None]
        f.write("".join(f"[[{link}]]\n" for link in sorted(links)))


def convert_to_obsidian(input_xml, output_dir, num_processes=4):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    page_count = 0
    total_links = 0

    pool = multiprocessing.Pool(processes=num_processes)

    with open(input_xml, "rb") as f:
        pages = []
        for event, elem in iterparse(f, events=("end",)):
            if elem.tag == "page":
                title = elem.find("title").text
                links = [link.text for link in elem.findall(".//link")]

                pages.append((title, links))
                page_count += 1
                total_links += len(links)

                # clear mem
                elem.clear()

                # process pages in 1000 page chunks
                if page_count % 1000 == 0:
                    pool.starmap(
                        convert_page_to_obsidian,
                        [(title, links, output_path) for title, links in pages],
                    )
                    pages = []
                    print(f"Processed {page_count} pages ({total_links} total links)")

        if pages:
            pool.starmap(
                convert_page_to_obsidian, [(page, output_path) for page in pages]
            )

    pool.close()
    pool.join()

    print(f"\nConversion complete!")
    print(f"Total pages created: {page_count}")
    print(f"Total links processed: {total_links}")
    print(f"Average links per page: {total_links / page_count:.1f}")
    print(f"Output directory: {output_path}")


if __name__ == "__main__":
    input_xml = "wiki-links-only-clean.xml"
    output_dir = "obsidian_vault"
    convert_to_obsidian(input_xml, output_dir, num_processes=4)
