from app.models.resume_parser import parse_resume

def test_parse_pdf():
    content = parse_resume("sample.pdf")
    assert content is not None

def test_parse_docx():
    content = parse_resume("sample.docx")
    assert content is not None

