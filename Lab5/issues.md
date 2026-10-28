Line numbers refer to the original movie_reviews.py at commit 780810d.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Bandit B324 Weak MD5 | Security High | 46 | MD5 is weak, and the ID was shortened to 10 characters. Concatenated fields could produce the same input. | Use a full SHA-256 digest of a JSON array containing the title and review. |
| Bandit B104 All interfaces | Security Medium | 4 | 0.0.0.0 could expose a server on every interface. This demo only prints the address. | Use 127.0.0.1 for the local streaming address. |
| Bandit B105 Password | Security Low | 6 | An unused moderator password was written in the source. | Remove the unused password constant. |
| Bandit B311 Random choice | Security Low | 41 | Bandit flags the standard random generator. Featured selection itself is not security sensitive. | Use secrets.choice to resolve the finding. |
| Pylint C0114 C0116 Docstrings | Convention | 1; 11-58 | The module and nine functions had no docstrings. | Add short module and function docstrings. |
| Pylint C0103 Naming | Convention | 8; 11-54 | Functions and reviewText used mixed case. The featured name was also flagged. | Use snake_case names, update callers, and remove unused featured state. |
| Pylint W0603 Global state | Warning | 40-42 | Featured selection reassigned a global that no caller read. | Return the selected title directly. |
| Pylint R1705 Extra else | Refactor | 28-31 | The else after return added unnecessary nesting. | Return 0.0 after the conditional. |
| Pylint C0200 Indexed loop | Convention | 49-51 | The loop used range and len on a copied title list. | Use enumerate(movies, start=1). |
| Flake8 E225 E231 Whitespace | Style | 35; 72 | Spaces were missing around an assignment and after a comma. | Insert the required spaces. |
| Flake8 E302 E261 Spacing | Style | 48; 70 | A function needed another blank line. An inline comment needed more spacing. | Use two blank lines between functions and two spaces before the comment. Wrap long lines to 79 characters. |

After fixes: Pylint 10.00/10, Bandit 0 findings, Flake8 0 findings. No checks were disabled.
