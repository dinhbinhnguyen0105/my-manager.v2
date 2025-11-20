import os
import shutil
from PIL import Image
from typing import List, Union

from src.utils.logger import Logger

logger = Logger(__name__)


def insert_logo_to_images(
    image_source: List[str],
    logo_path: str,
    output_dir: str,
    output_name_prefix: str,
    opacity: float = 0.5,
) -> List[str]:
    """
    Inserts a logo watermark onto a list of source images and saves the results.

    The logo is resized proportionally to 30% of the main image's width,
    its opacity is adjusted, and it is placed at the center of the image.

    Args:
        image_source: A list of file paths to the source images.
        logo_path: The file path to the logo image.
        output_dir: The destination directory to save the watermarked images.
        output_name_prefix: The file name prefix for the output images.
        opacity: The transparency level of the logo (0.0 to 1.0).

    Returns:
        A list of file paths to the newly created watermarked images.
    """
    new_paths: List[str] = []
    os.makedirs(output_dir, exist_ok=True)

    try:
        logo = Image.open(logo_path).convert("RGBA")
    except Exception as e:
        logger.error(f"Error opening logo file: {e}")
        return []

    for i, image_path in enumerate(image_source):
        dest_img_path = os.path.join(output_dir, f"{output_name_prefix}_{i}.png")

        try:
            main_image = Image.open(image_path).convert("RGBA")
            main_width, main_height = main_image.size

            new_logo_width = int(main_width * 0.3)
            logo_width, logo_height = logo.size
            new_logo_height = int(logo_height * (new_logo_width / logo_width))
            resized_logo = logo.resize((new_logo_width, new_logo_height), Image.LANCZOS)

            alpha = resized_logo.split()[-1]
            alpha = Image.eval(alpha, lambda x: x * opacity)
            resized_logo.putalpha(alpha)
            position = (
                (main_width - resized_logo.width) // 2,
                (main_height - resized_logo.height) // 2,
            )
            main_image.paste(resized_logo, position, resized_logo)
            main_image.save(dest_img_path, "PNG")
            new_paths.append(dest_img_path)

        except FileNotFoundError:
            logger.error(f"Image file not found: '{image_path}'. Skipping.")
            continue
        except Exception as e:
            logger.error(f"Error processing image '{image_path}': {e}")
            continue

    return new_paths


def copy_source_images(
    image_source: List[str],
    output_dir: str,
    output_name_prefix: str,
) -> None:
    """
    Copies the original source images to a separate destination directory.

    Args:
        image_source: A list of file paths to the source images.
        output_dir: The destination directory to store the copies of source images.
        output_name_prefix: The file name prefix for the output images.
    """
    os.makedirs(output_dir, exist_ok=True)

    for index, image_path in enumerate(image_source):
        try:
            file_extension = os.path.splitext(image_path)[1]
            new_file_name = f"{output_name_prefix}_{index}{file_extension}"
            new_path = os.path.join(output_dir, new_file_name)

            shutil.copy2(image_path, new_path)

        except Exception as e:
            logger.error(f"Error copying source file {image_path}: {e}")
            continue


def remove_images(image_folder: str) -> bool:
    """
    Deletes a directory and all its contents recursively.

    Args:
        image_folder: The path to the directory to be deleted.

    Returns:
        True if the directory was successfully deleted or didn't exist, False otherwise.
    """
    if not os.path.exists(image_folder):
        logger.warning(
            f"Image directory with name '{os.path.basename(image_folder)}' does not exist. Skipping deletion."
        )
        return True
    try:
        shutil.rmtree(image_folder)
        logger.info(f"Directory '{image_folder}' and all its contents deleted.")
        return True
    except OSError as e:
        logger.error(f"Error deleting directory {e.filename}: {e.strerror}.")
        return False


def get_images(image_folder: str) -> List[str]:
    """
    Retrieves a sorted list of image file paths from a given directory.

    Supported extensions: .png, .jpg, .jpeg, .gif, .bmp, .svg.

    Args:
        image_folder: The path to the directory to search for images.

    Returns:
        A sorted list of full paths to the image files. Returns an empty list if the path is not found.
    """
    if not os.path.exists(image_folder):
        logger.warning(f"Image directory path not found: '{image_folder}'.")
        return []

    image_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg")
    image_files = []

    for file_name in os.listdir(image_folder):
        if file_name.lower().endswith(image_extensions):
            full_path = os.path.join(image_folder, file_name)
            image_files.append(full_path)

    return sorted(image_files)


# --- Coordinating Function ---


def process_images_with_logo(
    image_source: List[str],
    image_container: str,
    logo_path: str,
    output_name: str,
    opacity: float = 0.5,
) -> Union[List[str], bool]:
    """
    Coordinates the entire process of inserting a logo and copying source images.

    This function defines the output structure and calls the necessary sub-functions.

    Args:
        image_source: List of file paths to the source images.
        image_container: The base directory where the output folder will be created.
        logo_path: The path to the logo file.
        output_name: The name of the main output directory and file prefix.
        opacity: The logo's opacity level (0.0 to 1.0).

    Returns:
        A list of file paths to the newly created watermarked images, or False on critical failure.
    """
    # 1. Define final destination directories
    dest_base_path = os.path.join(image_container, output_name)
    logo_output_dir = os.path.join(dest_base_path, f"logo_{output_name}")
    source_copy_dir = os.path.join(dest_base_path, f"source_{output_name}")

    # 2. Execute logo insertion
    logger.info(f"Starting logo insertion to {len(image_source)} images...")
    new_paths = insert_logo_to_images(
        image_source=image_source,
        logo_path=logo_path,
        output_dir=logo_output_dir,
        output_name_prefix=output_name,
        opacity=opacity,
    )

    if not new_paths and image_source:
        logger.warning("No images were processed successfully with the logo.")
        return False

    # 3. Execute source image copying
    logger.info(f"Starting copy of {len(image_source)} source images...")
    copy_source_images(
        image_source=image_source,
        output_dir=source_copy_dir,
        output_name_prefix=output_name,
    )

    logger.info("Image processing complete.")
    return new_paths
