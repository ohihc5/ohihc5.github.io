import time
import random
import re
import pandas as pd
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from webdriver_manager.chrome import ChromeDriverManager

from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter


# --- 1. SETUP / UTILS ---

def get_filename_date():
    return "A" + datetime.now().strftime("%y-%m-%d")


def setup_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(60)
    return driver


def clean_text(text: str) -> str:
    if text is None:
        return ""
    # Normalize Windows/Mac line endings to \n (Excel line break / CHAR(10))
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Keep spaces and line breaks; only trim outer blank lines
    # (keeps bullets/point-form and blank lines inside the section)
    text = text.strip("\n")

    return text



def extract_first_url(raw_line: str) -> str | None:
    """
    Supports:
      - https://example.com/...
      - - https://example.com/...
      - - [https://example.com/...](https://example.com/...)
    """
    if not raw_line:
        return None
    m = re.search(r"https?://[^\s)]+", raw_line)
    return m.group(0) if m else None


def generate_cve_range(start_cve, end_cve):
    try:
        s = start_cve.split("-")
        e = end_cve.split("-")
        if len(s) != 3 or len(e) != 3:
            return [start_cve]
        if s[1] != e[1]:
            return [start_cve]  # only same-year ranges supported

        year = s[1]
        start_num = int(s[2])
        end_num = int(e[2])
        if end_num < start_num:
            return [start_cve]

        return [f"CVE-{year}-{i}" for i in range(start_num, end_num + 1)]
    except Exception as ex:
        print(f"[!] Error generating CVE range: {ex}")
        return [start_cve]


def wait_for_body_keywords(
    driver,
    timeout=25,
    keywords=(
        "Product Affected",
        "Severity",
        "Problem",
        "Solution",
        "Workaround",
        "Severity Assessment",
        "References",
        "Access Denied",
    ),
):
    """
    Wait until the body text contains at least one keyword (or timeout).
    WebDriverWait polls until the condition succeeds or times out. [web:7]
    """
    wait = WebDriverWait(driver, timeout)

    def _cond(d):
        try:
            body = d.find_element(By.TAG_NAME, "body")
            txt = body.get_attribute("innerText") or ""
            return any(k in txt for k in keywords)
        except Exception:
            return False

    try:
        wait.until(_cond)
    except Exception:
        pass


def find_section(body_text: str, section_name: str, next_section_names: list[str], max_len=12000) -> str:
    """
    Best-effort string slicing:
    - Finds section_name (exact match, case-sensitive)
    - Ends at earliest next section heading found AFTER it
    """
    if not body_text:
        return ""

    start = body_text.find(section_name)
    if start == -1:
        return ""

    candidates = []
    for nxt in next_section_names:
        pos = body_text.find(nxt, start + len(section_name))
        if pos != -1:
            candidates.append(pos)

    end = min(candidates) if candidates else min(len(body_text), start + max_len)
    raw = body_text[start:end]

    if raw.lstrip().startswith(section_name):
        raw = raw.lstrip()[len(section_name):]
    return clean_text(raw)


def find_section_any(body_text: str, section_names: list[str], next_section_names: list[str], max_len=12000) -> str:
    """
    Try multiple possible headings and return the first non-empty section found.
    """
    for name in section_names:
        out = find_section(body_text, name, next_section_names, max_len=max_len)
        if out:
            return out
    return ""


def extract_affects_clause(text: str) -> str:
    """
    Extracts a short 'This issue affects ...' or 'These issues affect ...' clause
    from the given text (best-effort).
    """
    if not text:
        return ""

    for kw in ("This issue affects", "These issues affect"):
        pos = text.find(kw)
        if pos != -1:
            start = pos + len(kw)
            end = text.find(". ", start)
            chunk = text[start:end + 1] if end != -1 else text[start:]
            return clean_text(chunk).strip()

    return ""


# --- 2. CORE PROCESSING ---

def process_url(driver, raw_line, index):
    url = extract_first_url(raw_line) or ""
    row_data = {
        "Index": index,
        "Vulnerabilities Reference Link": url if url else raw_line.strip(),
        "Description": "",
        "Affected Product": "",
        "Affected Version(s)": "",
        "Affected by Product and Version(Y/N)": "N",
        "Affected ImmD Environment(Y/N)": "N",
        "Reason\n(If Column F value is Y, \nbut Column G value is N)": "",
        "Solution": "",
        "Workaround": "",
        "IsMitre": False,
        "TargetCVEs": []
    }

    if not url:
        row_data["Description"] = "Error: No URL detected on this line"
        return row_data

    # --- CASE A: MITRE ---
    if "cve.mitre.org" in url:
        row_data["IsMitre"] = True

        # Range is in the RAW LINE (your example: "... ) (to CVE-...)" )
        range_match = re.search(r"(CVE-\d{4}-\d+)\s*\(to\s*(CVE-\d{4}-\d+)\)", raw_line)
        if range_match:
            start_cve = range_match.group(1)
            end_cve = range_match.group(2)
            row_data["TargetCVEs"] = generate_cve_range(start_cve, end_cve)
            row_data["Description"] = f"Range Reference: {start_cve} to {end_cve}"
        else:
            match = re.search(r"(CVE-\d{4}-\d+)", url)
            if match:
                cve_id = match.group(1)
                row_data["TargetCVEs"] = [cve_id]
                row_data["Description"] = f"Reference: {cve_id}"
            else:
                row_data["Description"] = "Error: No CVE ID found in MITRE URL"

        return row_data

    # --- CASE B: JUNIPER / OTHER ---
    try:
        driver.get(url)
        wait_for_body_keywords(driver, timeout=25)

        body_el = driver.find_element(By.TAG_NAME, "body")
        body_text = body_el.get_attribute("innerText") or ""

        if "Access Denied" in body_text:
            row_data["Description"] = "BLOCKED: Firewall Access Denied"
            return row_data

        # --- Extract sections (best-effort) ---
        stop_after_product = ["Severity", "Problem", "Solution", "Workaround", "Severity Assessment", "References"]
        stop_after_problem = ["Solution", "Workaround", "Severity Assessment", "References"]
        stop_after_solution = ["Workaround", "Severity Assessment", "References"]
        stop_after_workaround = ["Severity Assessment", "References"]

        product_affected = find_section_any(
            body_text,
            ["Product Affected", "Products Affected"],
            stop_after_product,
        )

        problem = find_section(body_text, "Problem", stop_after_problem)
        solution = find_section(body_text, "Solution", stop_after_solution)
        workaround = find_section(body_text, "Workaround", stop_after_workaround)

        # Populate Description/Solution/Workaround
        if problem:
            row_data["Description"] = problem
        else:
            match = re.search(r"(CVE-\d{4}-\d+)", url)
            row_data["Description"] = f"Security Bulletin for {match.group(1)}" if match else "Problem section not detected"

        row_data["Solution"] = solution if solution else "Solution section not detected"
        row_data["Workaround"] = workaround

        # --- Affected extraction (best-effort from product_affected) ---
        if product_affected:
            # Store the whole section in Affected Product
            row_data["Affected Product"] = product_affected

            # Try to derive a shorter clause for Affected Version(s)
            affects_clause = extract_affects_clause(row_data["Description"])
            row_data["Affected Version(s)"] = affects_clause if affects_clause else product_affected
        else:
            row_data["Affected Product"] = "Product Affected section not detected"
            row_data["Affected Version(s)"] = ""

    except Exception as e:
        row_data["Description"] = f"Error: {e}"

    return row_data


def resolve_mitre_references(all_results):
    scan_columns = [
        "Vulnerabilities Reference Link",
        "Description",
        "Solution",
        "Workaround",
        "Affected Product",
        "Affected Version(s)",
    ]

    for row in all_results:
        if row.get("IsMitre") and row.get("TargetCVEs"):
            output_lines = []
            for target_cve in row["TargetCVEs"]:
                found_indices = []
                for search_row in all_results:
                    if search_row.get("Index") == row.get("Index"):
                        continue

                    for col in scan_columns:
                        if target_cve in str(search_row.get(col, "")):
                            found_indices.append(str(search_row["Index"]))
                            break

                if found_indices:
                    output_lines.append(f"{target_cve}: Refer to record with Index {', '.join(found_indices)}")
                else:
                    output_lines.append(f"{target_cve}: No record found")

            row["Description"] = "\n".join(output_lines)
            row["Solution"] = ""
            row["Workaround"] = ""

    return all_results


# --- 3. INPUT / RUN ---

def get_user_lines():
    print("=" * 70)
    print(" JUNIPER & MITRE SECURITY SCANNER")
    print("=" * 70)
    print("INSTRUCTIONS:")
    print("1. Copy your list of URLs (hyphens '-' at the start are okay).")
    print("2. Paste them below (Markdown link format is OK).")
    print("3. Press ENTER on a blank line to start the scan.")
    print("-" * 70)

    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)
        except EOFError:
            break
    return lines


def main():
    raw_lines = get_user_lines()
    detected_urls = [extract_first_url(x) for x in raw_lines]
    detected_urls = [u for u in detected_urls if u]

    if not raw_lines:
        print("[!] No input provided. Exiting.")
        return

    print(f"\n[*] Captured {len(raw_lines)} lines ({len(detected_urls)} URLs detected). Starting processing...")

    driver = setup_driver(headless=True)
    results = []
    total = len(raw_lines)

    try:
        for i, line in enumerate(raw_lines, 1):
            url = extract_first_url(line) or ""
            is_mitre = "cve.mitre.org" in url

            # Progress line (overwritten each loop)
            print(f"Processing {i}/{total}...", end="\r")

            data = process_url(driver, line, i)
            results.append(data)

            # Per-row log so it never "looks skipped"
            status = "MITRE" if data.get("IsMitre") else "WEB"
            desc_preview = (data.get("Description") or "")[:80]
            print(f"[{i:02d}] {status} | {data.get('Vulnerabilities Reference Link')} | {desc_preview}")

            if url and (not is_mitre):
                time.sleep(random.uniform(1.5, 3.0))

        results = resolve_mitre_references(results)

    finally:
        try:
            driver.quit()
        except Exception:
            pass

    print("\n[*] Scan complete. Generating formatted Excel...")

    export_columns = [
        "Index", "Vulnerabilities Reference Link", "Description",
        "Affected Product", "Affected Version(s)",
        "Affected by Product and Version(Y/N)", "Affected ImmD Environment(Y/N)",
        "Reason\n(If Column F value is Y, \nbut Column G value is N)",
        "Solution", "Workaround"
    ]

    df = pd.DataFrame(results)
    for col in export_columns:
        if col not in df.columns:
            df[col] = ""

    df = df[export_columns]

    date_str = get_filename_date()
    filename = f"Security Alert ({date_str}) Juniper Checking List .xlsx"

    try:
        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="SecurityAlert")
            worksheet = writer.sheets["SecurityAlert"]

            wrap_alignment = Alignment(wrap_text=True, vertical="top", horizontal="left")
            top_alignment = Alignment(vertical="top", horizontal="left")

            for col_idx, column_title in enumerate(export_columns, 1):
                col_letter = get_column_letter(col_idx)

                if column_title in ("Description", "Solution", "Workaround", "Affected Product", "Affected Version(s)"):
                    worksheet.column_dimensions[col_letter].width = 60
                    for cell in worksheet[col_letter]:
                        cell.alignment = wrap_alignment
                elif column_title == "Vulnerabilities Reference Link":
                    worksheet.column_dimensions[col_letter].width = 65
                    for cell in worksheet[col_letter]:
                        cell.alignment = top_alignment
                else:
                    worksheet.column_dimensions[col_letter].width = 25
                    for cell in worksheet[col_letter]:
                        cell.alignment = top_alignment

        print(f"[SUCCESS] Formatted report saved: {filename}")
    except Exception as e:
        print(f"[ERROR] Save failed: {e}")


if __name__ == "__main__":
    main()
