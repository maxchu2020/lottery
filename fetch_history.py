import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def fetch_lotto_max_history():
    """
    Fetches Lotto Max past winning numbers for all years.
    """
    all_results = []
    current_year = datetime.now().year
    
    for year in range(2009, current_year + 1):
        try:
            ajax_url = "https://www.getmylottoresults.com/asp/pastresults.asp"
            params = {'lt': 3, 'yr': year}
            response = requests.get(ajax_url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all table rows, skipping the header row
            rows = soup.find_all('tr')[1:]
            
            for row in rows:
                cells = row.find_all(['th', 'td'])
                if len(cells) == 9:
                    try:
                        date = cells[0].get_text(strip=True)
                        numbers = [cell.get_text(strip=True) for cell in cells[1:8]]
                        bonus = cells[8].get_text(strip=True)
                        
                        line = f"{date}	{' '.join(numbers)}	{bonus}"
                        all_results.append(line)
                    except (AttributeError, IndexError):
                        continue
        except requests.RequestException as e:
            print(f"Error fetching data for year {year}: {e}")
            continue
            
    print(f"Fetched a total of {len(all_results)} results from the website.")
    return all_results

def update_past_results(file_path, new_results):
    """
    Updates the past results file with new results, avoiding duplicates.
    """
    try:
        with open(file_path, 'r') as f:
            existing_lines = [line.strip() for line in f]
    except FileNotFoundError:
        existing_lines = ["Draw Date	Regular Numbers	Bonus"]

    # Create a set of existing dates for quick lookup
    existing_dates = set()
    for line in existing_lines[1:]: # Skip header
        try:
            # Handle lines with multiple spaces as well as tabs
            parts = re.split(r'	+|\s{2,}', line)
            if len(parts) > 1:
                # The date might be in the first part, or spread across a few
                # A bit of a heuristic here, but dates are usually like "24th February 2026"
                date_part = parts[0]
                if len(parts[0].split()) < 3 and len(parts) >=3:
                    date_part = " ".join(parts[:3])

                existing_dates.add(date_part)
        except IndexError:
            continue

    new_entries = []
    for line in new_results:
        date = line.split('	')[0]
        if date not in existing_dates:
            new_entries.append(line)
    
    if not new_entries:
        print("No new results to add.")
        return

    # Combine header, new entries, and the rest of the old entries
    header = existing_lines[0]
    old_results = existing_lines[1:]
    
    # We want to insert new results at the top after the header
    updated_content = [header] + new_entries + old_results
    
    # Let's re-parse and sort everything by date to be safe and clean
    all_results_parsed = []
    
    def clean_date_str(date_str):
        # remove suffixes like 'st', 'nd', 'rd', 'th' from day
        return re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date_str)

    for line in updated_content[1:]:
        try:
            parts = re.split(r'	+|\s{2,}', line)
            date_str = parts[0]
            # Handle cases where date is split by spaces in the source file
            if len(parts[0].split()) < 3 and len(parts) >= 3:
                 # e.g. "17th February 2026  10  11..."
                date_str = " ".join(parts[0:3])
                num_parts = parts[3:]
            else: # Date is in the first part
                num_parts = parts[1:]

            date_str_cleaned = clean_date_str(date_str)
            dt = datetime.strptime(date_str_cleaned, '%d %B %Y')
            
            # Re-assemble the line to be consistent
            numbers = num_parts[:-1]
            bonus = num_parts[-1]
            formatted_line = f"{date_str}	{' '.join(numbers)}	{bonus}"

            all_results_parsed.append({'date': dt, 'line': formatted_line})
        except (ValueError, IndexError) as e:
            print(f"Skipping malformed line: {line}, error: {e}")
            continue

    # Sort by date, descending (most recent first)
    all_results_parsed.sort(key=lambda x: x['date'], reverse=True)
    
    # Remove duplicates based on the line content
    seen = set()
    unique_results = []
    for item in all_results_parsed:
        if item['line'] not in seen:
            unique_results.append(item)
            seen.add(item['line'])

    # Write back to file
    with open(file_path, 'w') as f:
        f.write(header + '\n')
        for item in unique_results:
            f.write(item['line'] + '\n')
            
    print(f"Successfully added {len(new_entries)} new results to {file_path}.")


if __name__ == "__main__":
    results = fetch_lotto_max_history()
    if results:
        update_past_results('pastresult.txt', results)
