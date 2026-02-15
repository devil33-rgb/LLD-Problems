import uuid
from enum import Enum


# =========================
# ENUMS
# =========================

class OperationType(Enum):
    """
    Represents the type of PDF operation requested by the user.
    Helps the system understand what processing needs to be performed.
    """
    MERGE = "MERGE"
    COMPRESS = "COMPRESS"
    WATERMARK = "WATERMARK"


class OperationStatus(Enum):
    """
    Represents lifecycle state of an operation.
    Used for tracking progress and result retrieval.
    """
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# =========================
# DOMAIN MODELS
# =========================

class User:
    """
    Represents a system user.
    For simplicity, only username is stored.
    """
    def __init__(self, username: str):
        self.username = username


class PDFDocument:
    """
    Represents a PDF file in memory.

    Attributes:
        id      : Unique identifier for the document
        name    : File name
        pages   : List representing pages in the PDF
    """
    def __init__(self, name: str, pages: list):
        self.id = str(uuid.uuid4())
        self.name = name
        self.pages = pages

    def __repr__(self):
        return f"PDFDocument(name={self.name}, pages={len(self.pages)})"


class Operation:
    """
    Represents a user-requested PDF processing task.

    Tracks:
        - which user initiated it
        - operation type
        - input files
        - output result
        - execution status
    """
    def __init__(self, user: User, op_type: OperationType, input_files: list):
        self.id = str(uuid.uuid4())
        self.user = user.username
        self.type = op_type
        self.input_files = input_files
        self.output_file = None
        self.status = OperationStatus.PENDING

    def mark_completed(self, output):
        """Mark operation as successful and store result."""
        self.output_file = output
        self.status = OperationStatus.COMPLETED

    def mark_failed(self):
        """Mark operation as failed."""
        self.status = OperationStatus.FAILED


# =========================
# REPOSITORY
# =========================

class OperationRepository:
    """
    Acts as an in-memory database for operations.

    Responsibilities:
        - Store operations
        - Retrieve operations by ID
    """
    def __init__(self):
        self.operations = {}

    def save(self, operation: Operation):
        """Persist operation."""
        self.operations[operation.id] = operation

    def get(self, operation_id: str):
        """Fetch operation by ID."""
        return self.operations.get(operation_id)


# =========================
# SERVICES
# =========================

class PDFService:
    """
    Contains core PDF processing logic.
    In a real system this would call a PDF processing library.
    """

    def merge(self, pdf1: PDFDocument, pdf2: PDFDocument):
        """
        Combine pages of two PDFs into a new document.
        """
        merged_pages = pdf1.pages + pdf2.pages
        return PDFDocument("merged.pdf", merged_pages)

    def compress(self, pdf: PDFDocument):
        """
        Simulates compression.
        Real implementation would reduce file size.
        """
        return pdf

    def add_watermark(self, pdf: PDFDocument, page_range=None):
        """
        Simulates watermarking.
        page_range can define which pages to modify.
        """
        return pdf


class FileManager:
    """
    Simulates file storage system.

    Responsibilities:
        - Store files
        - Retrieve files
        - Assign unique file IDs
    """
    def __init__(self):
        self.storage = {}

    def upload(self, file_obj):
        """Store file and return generated file ID."""
        file_id = str(uuid.uuid4())
        self.storage[file_id] = file_obj
        return file_id

    def download(self, file_id):
        """Retrieve stored file by ID."""
        return self.storage.get(file_id)


# =========================
# USER MANAGERS
# =========================

class UserFileManager:
    """
    Handles file operations scoped to a specific user.

    Responsibilities:
        - Upload files
        - Track user's uploaded files
        - Download files
    """
    def __init__(self, user: User, file_manager: FileManager):
        self.user = user
        self.file_manager = file_manager
        self.user_files = {}

    def upload_file(self, file_obj):
        """
        Upload file to storage and associate it with the user.
        """
        file_id = self.file_manager.upload(file_obj)
        self.user_files.setdefault(self.user.username, []).append(file_id)
        return file_id

    def download_file(self, file_id):
        """Download file from storage."""
        return self.file_manager.download(file_id)


class UserPdfManager:
    """
    Coordinates PDF processing for a specific user.

    Responsibilities:
        - Create operations
        - Execute PDF service methods
        - Track user operations
        - Provide result retrieval
    """
    def __init__(self, user: User, operation_repo: OperationRepository):
        self.user = user
        self.pdf_service = PDFService()
        self.operation_repo = operation_repo
        self.user_operations = {}

    def _record_operation(self, operation: Operation):
        """
        Persist operation and associate it with user.
        """
        self.operation_repo.save(operation)
        self.user_operations.setdefault(self.user.username, []).append(operation.id)

    def merge_pdf(self, pdf1, pdf2):
        """
        Create and execute merge operation.
        Returns operation ID for tracking.
        """
        operation = Operation(self.user, OperationType.MERGE, [pdf1, pdf2])
        self._record_operation(operation)

        try:
            result = self.pdf_service.merge(pdf1, pdf2)
            operation.mark_completed(result)
        except Exception:
            operation.mark_failed()

        return operation.id

    def compress_pdf(self, pdf):
        """
        Create and execute compression operation.
        """
        operation = Operation(self.user, OperationType.COMPRESS, [pdf])
        self._record_operation(operation)

        try:
            result = self.pdf_service.compress(pdf)
            operation.mark_completed(result)
        except Exception:
            operation.mark_failed()

        return operation.id

    def add_watermark(self, pdf, page_range=None):
        """
        Create and execute watermark operation.
        """
        operation = Operation(self.user, OperationType.WATERMARK, [pdf])
        self._record_operation(operation)

        try:
            result = self.pdf_service.add_watermark(pdf, page_range)
            operation.mark_completed(result)
        except Exception:
            operation.mark_failed()

        return operation.id

    def download_result(self, operation_id):
        """
        Retrieve output of a completed operation.
        Returns None if operation failed or not finished.
        """
        operation = self.operation_repo.get(operation_id)
        if operation and operation.status == OperationStatus.COMPLETED:
            return operation.output_file
        return None


# =========================
# DEMO
# =========================

if __name__ == "__main__":
    """
    Demonstrates system workflow:
        1. User uploads file
        2. User triggers merge operation
        3. System processes request
        4. User downloads result
    """

    repo = OperationRepository()
    file_manager = FileManager()

    user = User("alex")

    file_mgr = UserFileManager(user, file_manager)
    pdf_mgr = UserPdfManager(user, repo)

    pdf1 = PDFDocument("file1.pdf", [1, 2, 3])
    pdf2 = PDFDocument("file2.pdf", [4, 5])

    upload_id = file_mgr.upload_file(pdf1)
    print("Uploaded File ID:", upload_id)

    op_id = pdf_mgr.merge_pdf(pdf1, pdf2)
    print("Operation ID:", op_id)

    result = pdf_mgr.download_result(op_id)
    print("Downloaded Result:", result)
