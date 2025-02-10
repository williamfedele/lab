import re

input_file = "wiki-links-only.xml"  # Change this to your actual file
output_file = "wiki-links-only-clean.xml"


def clean_link(link_text):
    # Remove or replace characters invalid characters in filenames
    cleaned_link = re.sub(
        r'[<>:"/\\|?*#\[\]]', "_", link_text
    )  # Replace with underscore
    cleaned_link = cleaned_link.strip()
    return cleaned_link


with (
    open(input_file, "r", encoding="utf-8") as infile,
    open(output_file, "w", encoding="utf-8") as outfile,
):
    for line in infile:
        # Delete any line that doesn't contain a valid tag
        if (
            "<page>" not in line
            and "</page>" not in line
            and "<mediawiki>" not in line
            and "</mediawiki>" not in line
            and "<links>" not in line
            and "</links>" not in line
            and "<title>" not in line
            and "</title>" not in line
            and "<link>" not in line
            and "</link>" not in line
            and "<?xml" not in line
        ):
            print(f"DELETE: {line}")
        # Delete any line without matching link tags
        elif "<link>" in line and "</link>" not in line:
            print(f"DELETE: {line}")
        elif "<link>" not in line and "</link>" in line:
            print(f"DELETE: {line}")
        # do not allow empty <link></link>
        elif "<link></link>" in line:
            print(f"DELETE (empty): {line}")
        # Process valid links
        elif "<link>" in line and "</link>" in line:
            match = re.match(r"^\s*<link>(?P<link_text>[^><]*)<\/link>\s*$", line)
            if match:
                link_text = match.group("link_text")
                cleaned_link = clean_link(link_text)
                if cleaned_link:  # Only write if the cleaned link isn't empty
                    outfile.write(f"<link>{cleaned_link}</link>\n")
                else:
                    print(f"DELETE (empty after cleaning): {line}")
            else:
                print(f"DELETE (invalid format): {line}")
        else:
            outfile.write(line)

print("Cleanup complete! Saved to:", output_file)
