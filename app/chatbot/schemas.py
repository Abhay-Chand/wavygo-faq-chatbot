from typing import Literal

from pydantic import BaseModel, Field


class QueryClassification(BaseModel):
    """
    Structured classification result for the chatbot query.
    """

    intent: Literal[
        "faq",
        "normal",
        "out_of_scope",
    ] = Field(
        description="The category of the user's message."
    )