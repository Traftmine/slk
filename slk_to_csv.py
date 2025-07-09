#!/usr/bin/env python3
"""
Convert SLK files to CSV format.
"""
import os
import sys
from io import StringIO
from sylk_parser import SylkParser
import time as t

def format_time(seconds):
    """Helper function to format time"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

def parse_slk_to_csv(input_path):
    """Parse SLK file and return CSV content as string."""
    try:
        parser = SylkParser(input_path)
        fbuf = StringIO()
        parser.to_csv(fbuf)
        fbuf.seek(0)
        return fbuf.getvalue()
    except Exception as e:
        raise ValueError(f"Failed to parse {input_path}: {str(e)}")

def save_csv(content, output_path):
    """Save CSV content to file."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_file.write(content)
        return True
    except Exception as e:
        print(f"Error saving to {output_path}: {str(e)}", file=sys.stderr)
        return False

def process_file(input_path, output_dir=None):
    """Process a single SLK file and convert it to CSV."""
    try:
        # Get filename without extension
        filename = os.path.basename(input_path)
        output_filename = os.path.splitext(filename)[0] + '.csv'

        # Determine output path
        if output_dir:
            output_path = os.path.join(output_dir, output_filename)
        else:
            output_path = os.path.join('data/processed', output_filename)

        # Parse SLK file
        csv_content = parse_slk_to_csv(input_path)

        # Remove the first 17 rows from the CSV content
        csv_lines = csv_content.splitlines()
        if len(csv_lines) > 17:
            csv_content = '\n'.join(csv_lines[17:])
        else:
            print(f"Warning: CSV has fewer than 18 rows, keeping all content for {input_path}")

        # Save modified CSV content
        if save_csv(csv_content, output_path):
            print(f"CSV file saved to: {output_path}")
            return output_path

    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}", file=sys.stderr)

    return None

def process_directory_with_progress(input_dir, output_dir=None):
    """Process all SLK files in a directory."""
    try:
        files = [f for f in os.listdir(input_dir) if f.lower().endswith('.slk')]
        total_files = len(files)

        if not files:
            print(f"No SLK files found in {input_dir}")
            return []

        processed_files = []
        print(f"Processing {total_files} files...")

        for i, file in enumerate(files):
            input_path = os.path.join(input_dir, file)
            result = process_file(input_path, output_dir)
            if result:
                processed_files.append(result)

            # Show progress
            progress = (i + 1) / total_files
            bar_length = 40
            bar = '█' * int(bar_length * progress) + '-' * (bar_length - int(bar_length * progress))

            elapsed = t.time() - start_time
            if progress > 0:
                estimated_total = elapsed / progress
                remaining = estimated_total - elapsed
            else:
                remaining = 0

            print(f"\r[{bar}] {int(progress*100)}% | {i+1}/{total_files} files | Time: {format_time(elapsed)} | ETA: {format_time(remaining)}")

        print()  # New line when done
        print(f"Total processing time: {format_time(t.time() - start_time)}")
        return processed_files

    except Exception as e:
        print(f"\nError processing directory {input_dir}: {str(e)}", file=sys.stderr)
        return []

def process_directory(input_dir, output_dir=None):
    """Process all SLK files in a directory."""
    processed_files = []
    try:
        files = [f for f in os.listdir(input_dir) if f.lower().endswith('.slk')]
        if not files:
            print(f"No SLK files found in {input_dir}")
            return []

        for file in files:
            input_path = os.path.join(input_dir, file)
            result = process_file(input_path, output_dir)
            if result:
                processed_files.append(result)

    except Exception as e:
        print(f"Error processing directory {input_dir}: {str(e)}", file=sys.stderr)

    return processed_files

if __name__ == "__main__":
    path = 'data/raw/2023'
    output_dir = 'data/processed/2023'
    # Start timing
    start_time = t.time()

    print(f"Starting processing at {t.strftime('%H:%M:%S')}")

    if os.path.isdir(path):
        print(f"Processing directory: {path}")
        process_directory_with_progress(path, output_dir)
    elif os.path.isfile(path) and path.lower().endswith('.slk'):
        print(f"Processing file: {path}")
        process_file(path, output_dir)
    else:
        print("The provided path is not a valid SLK file or directory.")