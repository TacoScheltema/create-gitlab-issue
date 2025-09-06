import argparse
import gitlab
import os
import subprocess
import re
import sys
from create_issue import __version__


def sanitize_title(title: str) -> str:
    """Replace spaces/dashes with underscores and remove special chars."""
    title = title.replace("-", "_").replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_]", "", title)


def detect_git_repo():
    """Check if we are inside a git repo and extract host + project path."""
    try:
        subprocess.check_output(
            ["git", "rev-parse", "--is-inside-work-tree"], stderr=subprocess.DEVNULL
        )
        remote_url = subprocess.check_output(
            ["git", "remote", "get-url", "origin"], text=True
        ).strip()

        if remote_url.startswith("git@"):
            # SSH format: git@host:group/project.git
            _, rest = remote_url.split(":", 1)
            host = remote_url.split("@")[1].split(":")[0]
        elif remote_url.startswith("http"):
            # HTTPS format: https://host/group/project.git
            parts = remote_url.split("/")
            host = parts[2]
            rest = "/".join(parts[3:])
        else:
            raise ValueError("Unsupported remote URL format")

        project_path = rest.replace(".git", "")
        return host, project_path

    except subprocess.CalledProcessError:
        sys.exit("This is not a git repository")


def main(args):
    host, project_path = detect_git_repo()

    # Load token
    token_path = os.path.expanduser("~/.gitlab-token")
    if not os.path.exists(token_path):
        sys.exit("Missing ~/.gitlab-token file")

    with open(token_path, "r") as f:
        private_token = f.read().strip()

    gl = gitlab.Gitlab(f"https://{host}", private_token=private_token)
    project = gl.projects.get(project_path)

    # Sanitize title
    issue_title = sanitize_title(args.title)

    # Authenticate and fetch current user
    gl.auth()
    current_user = gl.user

    # Default assignee = current user, unless -a overrides
    assignee_id = None
    if args.assignee:
        users = project.users.list(username=args.assignee)
        if users:
            assignee_id = users[0].id
    else:
        assignee_id = current_user.id

    # Create issue
    issue_data = {
        "title": issue_title,
        "description": args.description or "",
        "issue_type": args.type,
    }
    if assignee_id:
        issue_data["assignee_ids"] = [assignee_id]
    if args.label:
        issue_data["labels"] = [args.label]

    issue = project.issues.create(issue_data)
    print(f"Issue created: {issue.web_url}")

    if args.mr:
        branch_name = f"{issue.iid}_{issue_title}"
        default_branch = project.default_branch

        # Create branch via API
        project.branches.create({"branch": branch_name, "ref": default_branch})

        # Reviewer (optional)
        reviewer_ids = []
        if args.reviewer:
            users = project.users.list(username=args.reviewer)
            if users:
                reviewer_ids = [users[0].id]

        # Create MR
        mr = project.mergerequests.create({
            "source_branch": branch_name,
            "target_branch": default_branch,
            "title": f"Draft: {issue.iid}_{issue_title}",
            "description": f"Closes #{issue.iid}",
            "assignee_id": assignee_id,
            "reviewer_ids": reviewer_ids,
        })
        print(f"Merge request created: {mr.web_url}")


def main_cli():
    parser = argparse.ArgumentParser(description="Create GitLab issue (and optionally MR)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-t", "--title", required=True, help="Title of the issue")
    parser.add_argument("-d", "--description", help="Description of the issue")
    parser.add_argument("-a", "--assignee", help="Username to assign the issue")
    parser.add_argument("-r", "--reviewer", help="Username to add as MR reviewer")
    parser.add_argument("--type", choices=["incident", "task", "issue"], default="issue", help="Type of issue")
    parser.add_argument("-l", "--label", help="Label to add to the issue")
    parser.add_argument("-m", "--mr", action="store_true", help="Also create a merge request")
    args = parser.parse_args()
    main(args)
