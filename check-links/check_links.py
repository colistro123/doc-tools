"""
Author: colistro123 (colistro123@aol.com)
Created: 2024-11-10
Description: This script resolves relative URLs in a web-like manner and checks if the corresponding files exist in a given directory.
It handles various URL formats (e.g., `../`, `./`, absolute paths) and ensures proper resolution to mimic browser behavior.
"""

import os
import re
import requests
import subprocess
from urllib.parse import urlparse, urlunparse, urljoin


# Define the base project root for resolving paths
ROOT_DIR = os.path.normpath(r"D:\Users\Ignacio\Desktop\Projects\Resources (Projects that are not mine)\fivem-docs\content\docs")

# Base URL for the site (used to check links)
BASE_URL = "http://localhost:1313/docs/"

# Regex patterns
LINK_PATTERN = re.compile(r'(?<!\!)\[.*?\]\((.*?)\)')  # Match Markdown links excluding images
TEMPLATE_TAG_PATTERN = re.compile(r'{{[%<].*?[%>]}}')  # Match template tags
REFERENCE_LINK_PATTERN = re.compile(r'^\[.*?\]:\s*(.*?)$', re.MULTILINE)

# List of URL schemes to skip
SKIP_LINKS = [
    "mailto:",  # Skip mailto links
    "discord.gg",  # Skip discord links
    "/natives",
    "level_metas",
    "fivem://",
    "#",
    "/static/", # Skip static files for now
]


# Helper Functions
def is_url(link):
    """Check if the link is a valid URL."""
    parsed_link = urlparse(link)
    return bool(parsed_link.netloc)


def is_file_in_directory(base_dir, file_path):
    # Normalize paths to use forward slashes and handle OS differences
    normalized_base_dir = os.path.normpath(base_dir).replace('\\', '/')
    normalized_file_path = os.path.normpath(file_path).replace('\\', '/')

    # Check if the file is within the base directory by joining them
    # This will give us the full path to the file relative to base_dir
    full_file_path = os.path.join(normalized_base_dir, normalized_file_path)

    # Check if the file exists at the full path
    if os.path.exists(full_file_path):
        return True
    return False


def check_url(url):
    try:
        # Run curl to get the HTTP headers and status code
        result = subprocess.run(
            [   
                "curl", "--silent", "--head", "--location",
                 "--write-out", "%{http_code}", "--output",
                "/dev/null", url
            ],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Get the HTTP status code from the result's stdout
        http_code = int(result.stdout.strip())
        
        # Check if the status code is 200 (or add more codes if needed)
        if http_code == 200:
            return True
        
        return False
    
    except Exception as e:
        print(f"Error checking URL {url}: {e}")
        return False


def should_skip(link):
    """Check if the link should be skipped."""
    for skip in SKIP_LINKS:
        if link.startswith(skip):
            return True
    return False


def resolve_link(current_dir, link_to_find_rel_to_file):
    # Normalize the current directory and the link
    normalized_current_dir = os.path.normpath(current_dir).replace('\\', '/')
    normalized_link = os.path.normpath(link_to_find_rel_to_file).replace('\\', '/')

    # If the link starts with `../`, we need to go up the directory structure
    if normalized_link.startswith('../'):
        # Count how many `../` there are
        depth = normalized_link.count('../')

        # Ensure we don't go above the base directory
        for _ in range(depth):
            # Move up one directory level for each `../`
            normalized_current_dir = os.path.dirname(normalized_current_dir)
            normalized_link = normalized_link[3:]  # Remove `../`
    # If the link starts with `./`, it should replace the last segment of the current directory
    else:
        if link_to_find_rel_to_file.startswith('./'):
            # Remove './' from the front of the link
            normalized_link = link_to_find_rel_to_file[2:]
            
            # Build the new path by resolving it one level up from the current directory
            parent_dir = os.path.dirname(normalized_current_dir)
            potential_path = os.path.join(parent_dir, normalized_link)

            # Check if the file exists in the directory structure with .md extension
            if is_file_in_directory(ROOT_DIR, potential_path + '.md'):
                normalized_current_dir = parent_dir  # Remove the last segment from current_dir

    # Now, resolve the link within the current directory context
    resolved_path = os.path.normpath(
        os.path.join(normalized_current_dir, normalized_link)
    ).replace('\\', '/')

    # Handle if it's a directory (no file extension), ensure it ends with a slash
    if not os.path.splitext(resolved_path)[1]:  # No file extension
        if not resolved_path.endswith('/'):
            resolved_path += '/'
    
    return resolved_path


def process_link(file_path, link_to_find_rel_to_file, base_url='http://localhost:1313', root_path='/docs'):
    """
    Resolve a relative or absolute link to a web URL based on the filesystem path.
    
    Args:
        file_path (str): The full filesystem path of the file.
        link_to_find_rel_to_file (str): The relative or absolute link to be resolved.
        base_url (str, optional): The base URL for constructing the resolved web path. Defaults to 'http://localhost:1313'.
        root_path (str, optional): The base path for web paths. Defaults to '/docs'.
    
    Returns:
        str: The resolved web URL.
    
    Raises:
        ValueError: If the file_path is not within the root_path.
    """
    
    if is_url(link_to_find_rel_to_file):
        return # Skip URLs for now
    
    # Normalize the input file_path to use forward slashes and make absolute
    file_path = os.path.abspath(file_path).replace('\\', '/')
    
    # Find the relative part of the file_path starting from root_path
    if root_path not in file_path:
        raise ValueError(f"The file_path {file_path} is not within the root_path {root_path}")
    
    relative_to_root = file_path.split(root_path, 1)[1].lstrip('/')
    relative_to_root_as_page = relative_to_root
    
    # Strip `.md` extensions for cleaner URLs
    if relative_to_root_as_page.endswith('.md'):
        relative_to_root_as_page = relative_to_root.removesuffix('.md').replace('_index', '')
    
    if '/docs/' in link_to_find_rel_to_file:
        link_to_find_rel_to_file = link_to_find_rel_to_file.replace('/docs/', '/')
    
    # Simulate web-like resolution of the relative link
    normalized_path = resolve_link(relative_to_root_as_page, link_to_find_rel_to_file)
    
    # Build the resolved web path
    resolved_web_path = f"{root_path}/{normalized_path}".replace('//', '/')
    
    # Construct the full URL
    resolved_web_path = urlunparse(urlparse(resolved_web_path)._replace(fragment=''))

    # Strip `.md` extension since this is supposed to replicate web behavior
    if resolved_web_path.endswith('.md'):
        resolved_web_path = resolved_web_path.removesuffix('.md')

    # Check if it's a file (contains a known file extension) or a directory
    # Append / at the end so it doesn't 301 redirect
    if not resolved_web_path.endswith('/'):
        resolved_web_path += '/'  # Add trailing slash if not already present

    full_url = base_url + resolved_web_path
    
    # Check if the URL exists
    if not check_url(full_url):
        print(f"Broken URL: {full_url} (from file: {file_path}, link: {link_to_find_rel_to_file})")
    
    return full_url


def check_links_in_file(file_path):
    """Check all links in a Markdown file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()

    in_code_block = False

    #print(f"Reading': {file.name}")

    # Process each line in the file
    for line_index, line in enumerate(content, start=1):
        line = line.strip()

        # Skip template tags
        if TEMPLATE_TAG_PATTERN.search(line):
            continue
        
        # Handle inline comments on the same line
        if "<!--" in line and "-->" in line:
            continue  # Skip inline comments

        # Handle code blocks and comments
        if line.startswith("```") or line.startswith("<!--") or line.startswith("-->"):
            in_code_block = not in_code_block
            #print(f"Code block toggled by '{line}': {line_index} to state {in_code_block}")
            continue

        if in_code_block:
            continue

        # Find and process all links in the line
        # Process inline links
        for link in LINK_PATTERN.findall(line):
            link = link.strip()

            if should_skip(link):
                continue

            process_link(file_path, link)

        # Process reference-style links
        for ref_link in REFERENCE_LINK_PATTERN.findall(line):
            ref_link = ref_link.strip()

            if should_skip(ref_link):
                continue

            process_link(file_path, ref_link)


def traverse_directory(directory):
    """Traverse the directory and process Markdown files."""
    for root, _, files in os.walk(directory):
        for file in files:
            # Process everything, including non-Markdown files for links.
            file_path = os.path.join(root, file)
            if file.endswith(".md"):  # For Markdown files, check links
                check_links_in_file(file_path)
            else:
                # Log if necessary to ensure non-markdown isn't skipped silently
                print(f"Skipping non-Markdown file: {file_path}")


if __name__ == "__main__":
    traverse_directory(ROOT_DIR)
