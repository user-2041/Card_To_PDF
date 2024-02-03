from PIL import Image
from pathlib import Path

# USER-SPECIFIED "CONSTANTS"
INPUT_DIR = "Cards"
OUTPUT_DIR = "Output"
ORIG_CARD_WIDTH_PX = 691
ORIG_CARD_LENGTH_PX = 1050

# DEFAULT "CONSTANTS"
DEFAULT_PAGE_WIDTH_IN = 11
DEFAULT_PAGE_LENGTH_IN = 8.5
DEFAULT_DPI = 300
DEFAULT_CARD_WIDTH_MM = 63  # Bicycle card standard width
DEFAULT_CARD_GAP_MM = 0

# CONVERSION "CONSTANTS"
IN_TO_MM = 25.4
MM_TO_IN = 1 / IN_TO_MM


def mm_to_px(mm, dpi=DEFAULT_DPI):
    inches = mm * MM_TO_IN
    px = inches * dpi
    return int(px)


def compute_paper_width_px(page_width_in, dpi):
    return page_width_in * dpi


def compute_paper_length_px(page_length_in, dpi):
    return page_length_in * dpi


def compute_card_length_mm(
    orig_card_width_px, orig_card_length_px, card_width_mm=DEFAULT_CARD_WIDTH_MM
):
    length_to_width_ratio = orig_card_length_px / orig_card_width_px
    return card_width_mm * length_to_width_ratio


def compute_card_width_px(card_width_mm=DEFAULT_CARD_WIDTH_MM, dpi=DEFAULT_DPI):
    return round(card_width_mm * MM_TO_IN * dpi)


def compute_card_length_px(card_length_mm, dpi=DEFAULT_DPI):
    return round(card_length_mm * MM_TO_IN * dpi)


def compute_num_cols(paper_width_mm, card_width_mm, card_gap_mm=DEFAULT_CARD_GAP_MM):
    return int(paper_width_mm / (card_width_mm + card_gap_mm))


def compute_num_rows(paper_length_mm, card_length_mm, card_gap_mm=DEFAULT_CARD_GAP_MM):
    return int(paper_length_mm / (card_length_mm + card_gap_mm))


def compute_card_coordinates(nrows, ncols, card_width_px, card_length_px, card_gap_px):
    # list of (x, y) tuples
    card_coordinates = []

    for row in range(nrows):
        for col in range(ncols):
            x = col * (card_width_px + card_gap_px)
            y = row * (card_length_px + card_gap_px)
            card_coordinates.append((x, y))

    return card_coordinates


def png_to_pdf(paths_to_png, path_to_pdf, dpi=DEFAULT_DPI):
    """Converts multiple PNG files into a single PDF

    ### Params
    - `paths_to_png` list containing paths to PNG images
    - `path_to_pdf` the path where the output PDF will be saved

    https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#pdf
    """

    image_list = []
    for i in paths_to_png:
        image = Image.open(i)
        image_list.append(image)

    image_list[0].save(
        path_to_pdf,
        "PDF",
        save_all=True,
        dpi=(dpi, dpi),
        append_images=image_list[1:],
    )


def main():
    # prompt user for page width (in)
    page_width_in = input(
        f"Enter page width in inches (default = {DEFAULT_PAGE_WIDTH_IN}): "
    )
    if page_width_in:
        page_width_in = float(page_width_in)
    else:
        page_width_in = DEFAULT_PAGE_WIDTH_IN

    # prompt user for page height (in)
    page_length_in = input(
        f"Enter page length in inches (default = {DEFAULT_PAGE_LENGTH_IN}): "
    )
    if page_length_in:
        page_length_in = float(page_length_in)
    else:
        page_length_in = DEFAULT_PAGE_LENGTH_IN

    # prompt user for card with (mm)
    card_width_mm = input(
        f"Enter card width in mm (default = {DEFAULT_CARD_WIDTH_MM}): "
    )
    if card_width_mm:
        card_width_mm = int(card_width_mm)
    else:
        card_width_mm = DEFAULT_CARD_WIDTH_MM

    # prompt user for card gap (mm)
    card_gap_mm = input(f"Enter card gap in mm (default = {DEFAULT_CARD_GAP_MM}): ")
    if card_gap_mm:
        card_gap_mm = int(card_gap_mm)
    else:
        card_gap_mm = DEFAULT_CARD_GAP_MM

    # prompt user for dpi
    dpi = input(f"Enter PDF dpi (default = {DEFAULT_DPI}): ")
    if dpi:
        dpi = int(dpi)
    else:
        dpi = DEFAULT_DPI

    # Convert page measurements from in to cm
    page_width_mm = page_width_in * IN_TO_MM
    page_length_mm = page_width_in * IN_TO_MM

    # compute paper and card relationship, including coordinates and how many cards fit per page
    paper_width_px = round(page_width_in * dpi)
    paper_length_px = round(page_length_in * dpi)

    card_length_mm = compute_card_length_mm(
        ORIG_CARD_WIDTH_PX, ORIG_CARD_LENGTH_PX, card_width_mm
    )

    card_width_px = compute_card_width_px(card_width_mm, dpi)
    card_length_px = compute_card_length_px(card_length_mm, dpi)
    card_gap_px = mm_to_px(card_gap_mm, dpi)

    nrows = compute_num_rows(page_length_mm, card_length_mm, card_gap_mm)
    ncols = compute_num_cols(page_width_mm, card_width_mm, card_gap_mm)

    card_coordinates = compute_card_coordinates(
        nrows, ncols, card_width_px, card_length_px, card_gap_px
    )
    cards_per_page = len(card_coordinates)

    # output directory to hold resulting PDF of cards
    output_dir = Path(OUTPUT_DIR)
    if not output_dir.is_dir():
        output_dir.mkdir()

    # input folder from which to access images of cards
    input_dir = Path(INPUT_DIR)
    card_image_paths = input_dir.glob("*.png")
    card_image_paths = list(card_image_paths)
    pdf_page_count = len(card_image_paths) // cards_per_page + 1

    # collection of page images which will be combined
    page_images = []

    # assemble cards on each page before combining as a single PDF
    for page_num in range(pdf_page_count):
        page_image = Image.new("RGBA", (paper_width_px, paper_length_px))

        # calculate which cards we will be placing on the current page
        img_start_index = cards_per_page * page_num
        img_end_index = img_start_index + cards_per_page
        cur_page_image_paths = card_image_paths[img_start_index:img_end_index]

        # resize card before pasting to the right coordinate on the current page
        for index, file in enumerate(cur_page_image_paths):
            with Image.open(file) as img_card:
                img_card_resized = img_card.resize((card_width_px, card_length_px))
                page_image.paste(img_card_resized, card_coordinates[index])

        page_images.append(page_image)

    # combine and save card sheets as a single PDF
    path_to_pdf = output_dir / "cards.pdf"
    page_images[0].save(
        path_to_pdf,
        save_all=True,
        dpi=(dpi, dpi),
        append_images=page_images[1:],
    )

    # free memory taken by card sheets
    for image in page_images:
        image.close()


main()
