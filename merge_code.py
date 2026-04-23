import os

# Files we want to collect
extensions = (".py", ".txt", ".yaml", ".md")
# Folders to IGNORE (so the file isn't huge)
ignore_folders = {".venv", "venv", "__pycache__", ".git", "node_modules"}

with open("project_dump.txt", "w", encoding="utf-8") as outfile:
    for root, dirs, files in os.walk("."):
        # Skip the ignored folders
        dirs[:] = [d for d in dirs if d not in ignore_folders]

        for file in files:
            if file.endswith(extensions) and file != "project_dump.txt":
                file_path = os.path.join(root, file)
                outfile.write(f"\n\n--- FILE: {file_path} ---\n")
                try:
                    with open(file_path, "r", encoding="utf-8") as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"[Could not read file: {e}]")

print("Done! Your project is now in project_dump.txt")
