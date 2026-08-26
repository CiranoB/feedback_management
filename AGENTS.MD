# General information
This API has the main target to manage some feedback for a particular client.
The requirements are widely available on docs/challenge_info.md
Don't assume any information that is not explicit, ask first

# Swagger UI
Tornado does not offer a automatically integration with Swagger, so it is needed to check after every implementation if it keeps up-to-date.

# Allowed tools
You can check what are the dependencies for this particular project on: pyproject.toml
If some other library will help in order to reach the objective, let it clear and ask for the user to istall.

# UV package manager
This project uses uv, so all python commands must have this in mind.

# Readme
Make the README.md up to date, consice and clear.

# Pre-commit
After an entire implemenation, please perform pre-commit run --all-files to check if there's anything missing in therms of ty and ruff.