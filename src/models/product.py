"""Product base model."""

import typing

import pydantic


class Product(pydantic.BaseModel):
    name: str
    image_url: str
    description: str

    def process(
        self,
    ) -> None:
        """Process text."""
        points: typing.List[int]

        points = [
            i
            for i in range(len(self.description))
            if self.description.startswith(".", i)
        ]
        print(self.description)
        if len(points) > 4:
            self.description = self.description[: (points[4] + 1)]
            print(points[4])

        self.name = self.name.upper()
