"""
This module is used to generate test data for vocalization.

Download and unzip the test data from the following link here:
https://sourceforge.net/projects/tashkeela/
"""

from glob import glob

directory = "vocalization/Tashkeela/texts"

sub_dirs = [
    "aljazeera",
    "enfal.de",
    "manual",
    "sulaity",
    "كتب حديثة",
    "منوع",
]

total_file = "vocalization/Tashkeela.txt"
total_unvocalized_file = "vocalization/Tashkeela_unvocalized.txt"


def gen_total_file():
    with open(total_file, "w", encoding="utf-8") as f:
        for file in files:
            with open(file, "r", encoding="utf-8") as f2:
                f.write(f2.read())
                f.write("\n" + "#" * 50 + "\n")


def unvocalize_total_file():
    import pyarabic.araby as araby

    with open(total_file, "r", encoding="utf-8") as f:
        text = f.read()

    with open(total_unvocalized_file, "w", encoding="utf-8") as f:
        f.write(araby.strip_tashkeel(text))


if __name__ == "__main__":
    files = glob(f"{directory}/*.txt")

    for sub_dir in sub_dirs:
        files += glob(f"{directory}/msa/{sub_dir}/*")
