from langchain_core.language_models.chat_models import BaseChatModel


def create_gemini_llm() -> BaseChatModel:
    """Factory function to create and configure a ChatGoogleGenerativeAI instance."""

    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
    )
    return llm
