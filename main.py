from PIL import Image
from pathlib import Path

# USER-SPECIFIED
CARD_WIDTH_MM = 50
CARD_GAP_MM = 0
PAGE_WIDTH_IN = 11
PAGE_LENGTH_IN = 8.5
DPI = 300

# CONSTANTS
ORIG_CARD_WIDTH_PX = 691
ORIG_CARD_LENGTH_PX = 1050
IN_TO_MM = 25.4
MM_TO_IN = 1 / IN_TO_MM
PAGE_WIDTH_MM = PAGE_WIDTH_IN * IN_TO_MM
PAGE_LENGTH_MM = PAGE_LENGTH_IN * IN_TO_MM


def compute_paper_width_px(page_width_in, dpi):
    return page_width_in * dpi


def compute_paper_length_px(page_length_in, dpi):
    return page_length_in * dpi


def compute_card_length_mm(card_width_mm, orig_card_width_px, orig_card_length_px):
    length_to_width_ratio = orig_card_length_px / orig_card_width_px
    return card_width_mm * length_to_width_ratio


def compute_card_width_px(card_width_mm, dpi=DPI):
    return round(card_width_mm * MM_TO_IN * dpi)


def compute_card_length_px(card_length_mm, dpi=DPI):
    return round(card_length_mm * MM_TO_IN * dpi)


def compute_num_cols(paper_width_mm, card_width_mm):
    return int(paper_width_mm / card_width_mm)


def compute_num_rows(paper_length_mm, card_length_mm):
    return int(paper_length_mm / card_length_mm)


def compute_card_coordinates(nrows, ncols, card_width_px, card_length_px):
    # list of (x, y) tuples
    card_coordinates = []

    for row in range(nrows):
        for col in range(ncols):
            x = col * card_width_px
            y = row * card_length_px
            card_coordinates.append((x, y))

    return card_coordinates


def main():
    CARD_WIDTH_MM = int(input("Card width (mm)? "))

    output_dir = Path("output")
    if not output_dir.is_dir():
        output_dir.mkdir()

    paper_width_px = round(PAGE_WIDTH_IN * DPI)
    paper_length_px = round(PAGE_LENGTH_IN * DPI)

    card_length_mm = compute_card_length_mm(
        CARD_WIDTH_MM, ORIG_CARD_WIDTH_PX, ORIG_CARD_LENGTH_PX
    )

    card_width_px = compute_card_width_px(CARD_WIDTH_MM)
    card_length_px = compute_card_length_px(card_length_mm)

    nrows = compute_num_rows(PAGE_LENGTH_MM, card_length_mm)
    ncols = compute_num_cols(PAGE_WIDTH_MM, CARD_WIDTH_MM)

    card_coordinates = compute_card_coordinates(
        nrows, ncols, card_width_px, card_length_px
    )
    cards_per_page = len(card_coordinates)

    with Image.new("RGBA", (paper_width_px, paper_length_px)) as img_page:
        card_root = Path("Cards") / "Regular"
        files = card_root.glob("*")
        files = list(files)
        files = files[:cards_per_page]

        for index, file in enumerate(files):
            with Image.open(file) as img_card:
                img_card_resized = img_card.resize((card_width_px, card_length_px))
                img_page.paste(img_card_resized, card_coordinates[index])

        img_page.save(output_dir / "p01.png")


main()
