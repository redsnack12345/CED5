# verification.py: 학교 검색, PDF 텍스트 추출 및 정보 일치 검사
from pathlib import Path  # 파일 경로 처리
from io import BytesIO    # 메모리의 바이트 데이터를 파일처럼 읽기
from data import get_user_by_id, verification_requests

SCHOOLS = ['경북대학교', '영남대학교', '계명대학교']
MAX_PDF_BYTES = 5 * 1024 * 1024  # 5 MiB 제한(임시 정책)


def find_school(school_name):
    """학교 이름(str)을 검색하여 유일한 정식 명칭(str) 또는 정수 0을 반환한다."""
    # 공백을 제거하고, 빈 검색어는 결과 없음으로 처리한다.
    keyword = ''.join(school_name.split())
    if not keyword:
        return 0
    # 학교가 3개뿐이므로 선형 탐색과 문자열 포함 여부 비교를 사용한다.
    matches = []
    for school in SCHOOLS:
        if keyword in school:
            matches.append(school)
    # 여러 학교와 일치하면 임의 선택하지 않는다.
    return matches[0] if len(matches) == 1 else 0


def extract_pdf_text(pdf_data):
    """PDF 바이트(bytes)에서 텍스트(str)를 추출한다. 실패하면 예외를 발생시킨다."""
    # 이 함수가 호출될 때만 외부 라이브러리를 불러온다.
    from pypdf import PdfReader
    reader = PdfReader(BytesIO(pdf_data))
    if reader.is_encrypted:
        raise ValueError('암호화된 PDF는 지원하지 않습니다.')
    # 페이지별 텍스트를 추출하여 하나의 문자열로 합친다.
    text = '\n'.join(page.extract_text() or '' for page in reader.pages)
    if not text.strip():
        raise ValueError('문자 추출 불가: 이미지 PDF일 수 있습니다.')
    return text


def check_certificate(text, name, school, department):
    """추출된 문자열과 회원 정보를 비교하고 항목별 검사 결과(dict)를 반환한다."""
    # PDF 텍스트 추출 시 추가되는 줄바꿈과 공백을 제거한다.
    normalized = ''.join(text.split())
    checks = {
        '증명서 유형': any(word in normalized for word in ('재학증명서', '등록증명서')),
        '이름': ''.join(name.split()) in normalized,
        '학교': ''.join(school.split()) in normalized,
        '학과': ''.join(department.split()) in normalized
    }
    # all(): 모든 검사값이 True일 때만 True를 반환한다.
    # 단순 문자열 비교이므로 실제 문서 진위나 발급 여부를 보장하지 않는다.
    return {'matched': all(checks.values()), 'checks': checks,
            'missing': [key for key, ok in checks.items() if not ok]}


def submit_certificate(user_id, file_path):
    """로그인 회원의 PDF 경로를 받아 검토 요청을 저장하고 결과(dict)를 반환한다."""
    user = get_user_by_id(user_id)
    if user is None or user['is_banned'] or user['verified']:
        return {'success': False, 'message': '제출할 수 없는 계정입니다.'}
    try:
        path = Path(file_path)
        if path.suffix.lower() != '.pdf':
            raise ValueError('PDF 파일만 지원합니다.')
        # 파일의 바이너리 데이터를 크기 제한까지 읽는다.
        with path.open('rb') as file:
            pdf_data = file.read(MAX_PDF_BYTES + 1)
        if len(pdf_data) > MAX_PDF_BYTES:
            raise ValueError('PDF는 5 MiB 이하여야 합니다.')
        text = extract_pdf_text(pdf_data)
    except ImportError:
        return {'success': False, 'message': 'pypdf를 설치하세요.'}
    except ValueError as error:
        return {'success': False, 'message': str(error)}
    except Exception:
        # 파일 없음, 읽기 권한 문제, 손상된 PDF 등을 사용자에게 안내한다.
        return {'success': False, 'message': 'PDF를 읽을 수 없습니다.'}

    check = check_certificate(text, user['name'], user['school'], user['department'])
    # 정보 일치 여부와 별개로 최종 검토 대기 상태로 저장한다.
    # 실제 발급기관 연동 및 최종 승인 기능은 이번 버전에서 제외한다.
    verification_requests[user_id] = {
        'pdf_bytes': pdf_data, 'check_result': check, 'status': 'pending'
    }
    return {'success': True, 'message': '증명서 제출 완료. 최종 검토가 필요합니다.',
            'matched': check['matched'], 'missing': check['missing'], 'status': 'pending'}
