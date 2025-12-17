from .project_context import ProjectContext


class TOMLManager:
    def __init__(self, ctx: ProjectContext, name: str) -> None:
        self.toml_path = ctx.toml_path
        self.name = name

    def create(self):
        data = {
            "build-system": {
                "requires": ["hatchling", "hatch-vcs"],
                "build-backend": "hatchling.build",
            },
            "project": {"name": self.name},
        }
        print(data)
