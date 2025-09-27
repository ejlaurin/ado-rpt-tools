# TODO: Get rid of the PDF report generation because we probably want to process the
#       raw json or feed it back into another process once we make modifications for
#       what to clean up or fix.
import requests
import json
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import argparse
import sys
from urllib.parse import quote
import base64

# === INPUTS ===
def parse_args():
    parser = argparse.ArgumentParser(description="Azure DevOps Branch Policy Auditor")
    parser.add_argument("--org", required=True, help="Azure DevOps organization name (e.g., 'myorg')")
    parser.add_argument("--pat", required=True, help="Azure DevOps Personal Access Token")
    parser.add_argument("--output", default="azure_devops_branch_policy_report.pdf", help="Output PDF filename")
    return parser.parse_args()

args = parse_args()
organization = args.org.strip()
pat = args.pat.strip()
output_file = args.output
api_version = "7.1-preview.1"

# === HEADERS ===
# Encode PAT as Basic Auth header
encoded_pat = base64.b64encode(f":{pat}".encode()).decode()
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {encoded_pat}"
}

# === PDF SETUP ===
class ReportPDF(FPDF):
    def __init__(self, font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_name="DejaVu", font_size=12):
        super().__init__()
        self.font_name = font_name
        self.font_size = font_size
        self._register_font(font_path)
        self.set_font(self.font_name, "", self.font_size)

    def _register_font(self, font_path):
        try:
            self.add_font(self.font_name, "", font_path)
        except RuntimeError:
            # Font already registered; suppress warning
            pass

    def header(self):
        self.set_font(self.font_name, "", self.font_size)
        self.cell(0, 14, "Azure DevOps Branch Policy Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.ln(5)

    def section_title(self, title):
        self.set_font(self.font_name, "", self.font_size)
        self.cell(0, 14, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
#        self.ln(2)

    def section_body(self, text):
        self.set_font(self.font_name, "", self.font_size)
        self.multi_cell(0, 14, text)
#        self.ln(2)

pdf = ReportPDF()
pdf.add_page()

# === GET PROJECTS ===
def get_projects():
    url = f"https://dev.azure.com/{organization}/_apis/projects?api-version={api_version}"
    response = requests.get(url, headers=headers)
    text_response_with_bom = response.text
    text_response_without_bom = text_response_with_bom.encode('utf-8').decode('utf-8-sig')
    projects = json.loads(text_response_without_bom) 
    return projects.get("value", [])

# === GET REPOS IN PROJECT ===
def get_repos(project):
    url = f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories?api-version={api_version}"
    response = requests.get(url, headers=headers)
    text_response_with_bom = response.text
    text_response_without_bom = text_response_with_bom.encode('utf-8').decode('utf-8-sig')
    repos = json.loads(text_response_without_bom)
    return repos.get("value", [])

# === GET BRANCHES ===
def get_branches(project, repo_id):
    url = f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repo_id}/refs?filter=refs/heads/&api-version={api_version}"
    response = requests.get(url, headers=headers)
    text_response_with_bom = response.text
    text_response_without_bom = text_response_with_bom.encode('utf-8').decode('utf-8-sig')
    branches = json.loads(text_response_without_bom)
    return branches.get("value", [])

# === GET POLICIES FOR BRANCH ===
def get_policies(project, repo_id, branch_name):
    url = f"https://dev.azure.com/{organization}/{project}/_apis/policy/configurations?repositoryId={repo_id}&refName={branch_name}&api-version={api_version}"
    response = requests.get(url, headers=headers)
    text_response_with_bom = response.text
    text_response_without_bom = text_response_with_bom.encode('utf-8').decode('utf-8-sig')
    policies = json.loads(text_response_without_bom)
    return policies.get("value", [])

# === MAIN AUDIT LOOP ===
def audit():
    projects = get_projects()
    for proj in projects:
        project_name = proj["name"]
        pdf.section_title(f"Project: {project_name}")
        repos = get_repos(project_name)

        for repo in repos:
            repo_name = repo["name"]
            repo_id = repo["id"]
            pdf.section_title(f"Repository: {repo_name}")

            locked_branches = []
            no_policy_branches = []
            policy_summary = {}

#            branches = get_branches(project_name, repo_id)
#            for branch in branches:
#                branch_name = branch["name"]
#                is_locked = branch.get("isLocked", False)
#                policies = get_policies(project_name, repo_id, branch_name)

#                if is_locked:
#                    locked_branches.append(branch_name)
#                if not policies:
#                    no_policy_branches.append(branch_name)
#                else:
#                    policy_summary[branch_name] = [p["type"]["displayName"] for p in policies]
#
#            if locked_branches:
#                pdf.section_body("Locked Branches:\n" + "\n".join(locked_branches))
#            if no_policy_branches:
#                pdf.section_body("Branches with No Policies:\n" + "\n".join(no_policy_branches))
#            if policy_summary:
#                pdf.section_body("Branch Policies:")
#                for branch, policies in policy_summary.items():
#                    pdf.section_body(f"  • {branch}:\n    - " + "\n    - ".join(policies))

# === RUN & SAVE ===
audit()
pdf.output("azure_devops_branch_policy_report.pdf")
