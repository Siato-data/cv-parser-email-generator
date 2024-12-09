#cv parsing 2/app_parsing/service/document_loader.py

from pathlib import Path
import logging
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader, TextLoader
from typing import Set




class DocumentLoader:
    """Resume document loader manager for different formats.

    This class provides methods to load and extract content
    from resumes in PDF, DOCX, and TXT formats.

    Attributes:
        SUPPORTED_FORMATS (set): Set of supported file extensions
    """
    SUPPORTED_FORMATS = {'.pdf', '.docx', '.txt'}

    @classmethod
    def load_document(cls, file_path: Path) -> str:
        """Loads document content based on file format.
        
        Args:
            file_path (Path): Path to the document file
            
        Returns:
            str: Extracted text content
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is not supported
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_extension = file_path.suffix.lower()
        
        if file_extension not in cls.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {file_extension}")

        try:
            if file_extension == '.pdf':
                loader = PyPDFLoader(str(file_path))
                pages = loader.load()
                return "\n\n".join([page.page_content for page in pages])
            elif file_extension == '.docx':
                loader = Docx2txtLoader(str(file_path))
                return loader.load()[0].page_content
            elif file_extension == '.txt':
                loader = TextLoader(str(file_path))
                return loader.load()[0].page_content
                
        except Exception as e:
            logging.error(f"Error loading document {file_path}: {str(e)}")
            raise