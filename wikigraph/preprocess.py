import re
from xml.etree.ElementTree import iterparse
import mmap
import os


# preprocess the wiki dump into a more simple XML format with only title and link labels
def preprocess_wiki_xml(input_path, output_path):
    with open(output_path, "w", encoding="utf-8") as out:
        out.write('<?xml version="1.0" encoding="UTF-8"?>\n<mediawiki>\n')

    def extract_wiki_links(text):
        if not text:
            return set()
        pattern = r"\[\[([^|\]]*?)(?:\|[^\]]*?)?\]\]"
        matches = re.finditer(pattern, text)
        links = set()

        for match in matches:
            link = match.group(1).strip()
            if any(
                link.startswith(ns + ":")
                for ns in ["File", "Category", "Template", "Wikipedia", "Help"]
            ):
                continue
            link = link.split("#")[0]  # Remove section anchors
            link = link.replace("_", " ")
            links.add(link)

        return links

    # used to ignore page entries that are redirects to real pages
    def is_redirect(elem):
        # Check for redirect tag
        redirect_elem = elem.find(".//{*}redirect")
        if redirect_elem is not None:
            return redirect_elem.get("title")

        # Check for #REDIRECT in text
        text_elem = elem.find(".//{*}text")
        if text_elem is not None and text_elem.text:
            text = text_elem.text.strip()
            if text.upper().startswith("#REDIRECT"):
                matches = re.findall(r"\[\[([^|\]]*?)(?:\|[^\]]*?)?\]\]", text)
                if matches:
                    return matches[0].strip()

        return None

    file_size = os.path.getsize(input_path)
    processed_bytes = 0
    page_count = 0
    redirect_count = 0

    with open(input_path, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

        for event, elem in iterparse(mm, events=("end",)):
            if elem.tag.endswith("page"):
                title_elem = elem.find(".//{*}title")

                if title_elem is not None:
                    title = title_elem.text

                    # Skip non-article namespaces
                    if ":" in title and not title.startswith("Talk:"):
                        elem.clear()
                        continue

                    # Check for redirect
                    redirect_target = is_redirect(elem)
                    if redirect_target:
                        redirect_count += 1
                        # Skip redirects
                        elem.clear()
                        continue

                    # Process regular article
                    text_elem = elem.find(".//{*}text")
                    if text_elem is not None:
                        content = text_elem.text or ""
                        links = extract_wiki_links(content)

                        if links:
                            with open(output_path, "a", encoding="utf-8") as out:
                                out.write(f"  <page>\n")
                                out.write(f"    <title>{title}</title>\n")
                                out.write(f"    <links>\n")
                                for link in sorted(links):
                                    out.write(f"      <link>{link}</link>\n")
                                out.write(f"    </links>\n")
                                out.write(f"  </page>\n")

                            page_count += 1
                            if page_count % 1000 == 0:
                                processed_bytes = mm.tell()
                                progress = (processed_bytes / file_size) * 100
                                print(
                                    f"Progress: {progress:.1f}% - Processed {page_count} pages (Skipped {redirect_count} redirects)"
                                )

                elem.clear()

        mm.close()

    with open(output_path, "a", encoding="utf-8") as out:
        out.write("</mediawiki>")

    print(f"\nPreprocessing complete!")
    print(f"Total pages processed: {page_count}")
    print(f"Total redirects skipped: {redirect_count}")
    print(f"Output file: {output_path}")


if __name__ == "__main__":
    input_path = "enwiki-20250201-pages-articles-multistream.xml"
    output_path = "wiki-links-only.xml"
    preprocess_wiki_xml(input_path, output_path)
