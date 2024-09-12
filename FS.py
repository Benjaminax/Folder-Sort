import os
import shutil
import re
import logging
import time

# Dynamically get the user's home directory
home_directory = os.path.expanduser("~")
downloads_folders = [
    os.path.join(home_directory, "Downloads"),
    os.path.join(home_directory, "Downloads", "Telegram Desktop")
]
movies_folder = os.path.join(home_directory, "Videos", "Movies")
series_folder = os.path.join(home_directory, "Videos", "Series")

# Define file extensions
media_extensions = ['.mp4', '.mkv', '.avi', '.mov']

# Set up logging
log_file = os.path.join(home_directory, "sort_files.log")
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def replace_underscores_and_dots(file_name):
    return file_name.replace('_', ' ').replace('.', ' ')


def is_series(file_name):
    series_pattern = re.compile(r'.*[Ss]\d{1,2}[Ee]\d{1,2}', re.IGNORECASE)
    return series_pattern.search(file_name)


def get_series_name(file_name):
    series_name_match = re.match(r'(.+?)\s*[Ss]\d{1,2}[Ee]\d{1,2}', file_name)
    return series_name_match.group(1).strip() if series_name_match else None


def get_unique_filename(dest_folder, file_name):
    base_name, extension = os.path.splitext(file_name)
    unique_name = file_name
    counter = 1
    while os.path.exists(os.path.join(dest_folder, unique_name)):
        unique_name = f"{base_name}_{counter}{extension}"
        counter += 1
    return unique_name


def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory: {directory}")


def move_file(src_path, dest_folder, file_name):
    retries = 3
    for attempt in range(retries):
        try:
            ensure_directory_exists(dest_folder)
            unique_name = get_unique_filename(dest_folder, file_name)
            dest_path = os.path.join(dest_folder, unique_name)
            logging.info(f"Moving file from {src_path} to {dest_path}")
            shutil.move(src_path, dest_path)
            file_size = os.path.getsize(dest_path) / (1024 * 1024)  # Size in MB
            logging.info(f"Moved {file_name} to {dest_folder}. Size: {file_size:.2f} MB")
            break
        except PermissionError as e:
            logging.error(f"Permission error moving {file_name} to {dest_folder}: {str(e)}")
            time.sleep(5)  # Wait before retrying
        except FileNotFoundError as e:
            logging.error(f"File not found: {file_name}. Error: {str(e)}")
            break
        except Exception as e:
            logging.error(f"Error moving {file_name} to {dest_folder}: {str(e)}")
            break


def process_downloads_folder(downloads_folder):
    for file_name in os.listdir(downloads_folder):
        file_path = os.path.join(downloads_folder, file_name)
        logging.info(f"Processing file: {file_path}")

        if os.path.isdir(file_path):
            continue

        try:
            # Only modify media files
            if any(file_name.lower().endswith(ext) for ext in media_extensions):
                file_name_with_spaces = replace_underscores_and_dots(file_name)
                logging.info(f"File {file_name} identified as media.")

                if is_series(file_name_with_spaces):
                    series_name = get_series_name(file_name_with_spaces)
                    if series_name:
                        series_folder_path = os.path.join(series_folder, series_name)
                        logging.info(f"Series detected. Moving to: {series_folder_path}")
                        move_file(file_path, series_folder_path, file_name)
                    else:
                        logging.warning(f"Series name could not be extracted for {file_name}. Moving to Movies.")
                        move_file(file_path, movies_folder, file_name)
                else:
                    logging.info(f"File {file_name} identified as a movie.")
                    move_file(file_path, movies_folder, file_name)
            else:
                logging.info(f"File {file_name} is not a media file. No action taken.")

        except Exception as e:
            logging.error(f"Failed to process {file_name}: {str(e)}")


def sort_files():
    for downloads_folder in downloads_folders:
        if not os.path.exists(downloads_folder):
            logging.error(f"Downloads folder not found: {downloads_folder}")
            continue
        process_downloads_folder(downloads_folder)


if __name__ == "__main__":
    sort_files()
    input("Press Enter to exit...")
