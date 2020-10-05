from logging import Logger

from googleapiclient.discovery import build
from libs.api_shared.credential_manger import CredentialManager

class CourseState:
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    PROVISIONED = "PROVISIONED"
    DECLINED = "DECLINED"
    SUSPENDED = "SUSPENDED"

class ClassroomAPIHandler(CredentialManager):
    def __init__(self, logger: Logger, token_store_path: str = "",
                 app_credential_path: str = "credentials.json") -> None:
        super().__init__(logger, token_store_path, app_credential_path)
        self.service = None
        self.auth_service()

    def auth_service(self) -> None:
        self.service = build('classroom', 'v1', credentials=self.credentials)

    def list_classroom(self, teacher_id="me", student_id="",
                       course_state: CourseState = CourseState.ACTIVE,
                       page_size: int = 20, page_token: str = ""):
        return self.service.courses().list(teacherId=teacher_id, studentId=student_id,
                                           courseStates=course_state,
                                           pageSize=page_size, pageToken=page_token).execute()

    def list_students(self, course_id: str, page_size: int = 50, page_token: str = ""):
        return self.service.courses().students().list(courseId=course_id,
                                                      pageSize=page_size, pageToken=page_token).execute()

    def get_student(self, course_id: str, user_id: str = "me"):
        return self.service.courses().students().get(courseId=course_id, userId=user_id).execute()
