# استيراد جميع النماذج
from app.models.user import User, Permission, DetailedPermission
from app.models.club import Club
from app.models.facility import Facility, FacilityCheckItem, FacilityCheck, FacilityCheckResult
from app.models.employee import Employee, WorkRecord
from app.models.work_tracking import WorkTracking
from app.models.issue import Issue
from app.models.violation import ViolationType, ViolationSource, Violation
from app.models.camera_check import CameraCheck
from app.models.visit import Visit
from app.models.suggestion import Suggestion
from app.models.revenue import RevenueCategory, Revenue
from app.models.facility_quality import FacilityQuality
from app.models.shomoos import Shomoos
