import os
import shutil
import argparse
from fabric_cicd import FabricWorkspace, publish_all_items, unpublish_all_orphan_items
from azure.identity import ClientSecretCredential

# หา path ของ fabric_items แบบ absolute อ้างอิงจากตำแหน่งไฟล์นี้เอง (อยู่ใน scripts/ ต้องขึ้นไป 1 ชั้น)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ITEMS_DIR = os.path.join(BASE_DIR, "..", "fabric_items")

# item type ทั้งหมดที่ fabric-cicd (เวอร์ชันที่ติดตั้งจริง) รองรับ — ดึงมาจาก
# fabric_cicd.constants.ItemType เพื่อไม่ต้องมานั่งเพิ่มทีละตัวทุกครั้งที่มี item type ใหม่
# (แบบที่เจอกับ Warehouse/Dataflow มาแล้ว) — ใส่ type ที่ยังไม่มี item จริงใน repo ไว้ล่วงหน้าได้
# เพราะ fabric-cicd แค่ข้าม type ที่ไม่เจอโฟลเดอร์ folder เฉยๆ ไม่มีผลเสีย
# ถ้า fabric-cicd อัปเดตแล้วมี item type เพิ่ม ให้เช็ค ItemType enum ใน constants.py แล้ว sync list นี้อีกที
ALL_SUPPORTED_ITEM_TYPES = [
    "ApacheAirflowJob",
    "CopyJob",
    "DataAgent",
    "DataBuildToolJob",
    "DataPipeline",
    "Dataflow",
    "Environment",
    "Eventhouse",
    "Eventstream",
    "GraphQLApi",
    "KQLDashboard",
    "KQLDatabase",
    "KQLQueryset",
    "Lakehouse",
    "Map",
    "MirroredDatabase",
    "MLExperiment",
    "MountedDataFactory",
    "Notebook",
    "Ontology",
    "PaginatedReport",
    "Reflex",
    "Report",
    "SemanticModel",
    "SparkJobDefinition",
    "SQLDatabase",
    "UserDataFunction",
    "VariableLibrary",
    "Warehouse",
]


def _clean_pycache(root: str) -> None:
    # fabric-cicd ส่งทุกไฟล์ที่เจอในโฟลเดอร์ item เป็น definition part — __pycache__/*.pyc
    # ที่หลุดเข้ามา (เช่นจากรัน pytest ที่ import notebook-content.py ตรงๆ) ทำให้ publish fail
    # ด้วย error "doesn't support definition parts with empty payload"
    for dirpath, dirnames, _ in os.walk(root):
        if "__pycache__" in dirnames:
            shutil.rmtree(os.path.join(dirpath, "__pycache__"))
            dirnames.remove("__pycache__")


parser = argparse.ArgumentParser()
parser.add_argument("--workspace", required=True, help="Fabric workspace ID (GUID)")
parser.add_argument("--environment", default="dev")
args = parser.parse_args()

_clean_pycache(REPO_ITEMS_DIR)

credential = ClientSecretCredential(
    tenant_id=os.environ["FABRIC_TENANT_ID"],
    client_id=os.environ["FABRIC_CLIENT_ID"],
    client_secret=os.environ["FABRIC_CLIENT_SECRET"],
)

workspace = FabricWorkspace(
    workspace_id=args.workspace,
    environment=args.environment,
    repository_directory=REPO_ITEMS_DIR,
    item_type_in_scope=ALL_SUPPORTED_ITEM_TYPES,
    token_credential=credential,
)

try:
    publish_all_items(workspace)
except Exception as e:
    # fabric-cicd's summary exception message มีแค่ชื่อ item ที่ fail (ไม่มี error text จริง) —
    # error text จริงอยู่ใน e.additional_info (ดู fabric_cicd._common._exceptions.PublishError)
    # ใช้ getattr แทน import class ตรงๆ เพราะเป็น private module เสี่ยง break ถ้า library อัปเดต
    detail = getattr(e, "additional_info", None) or str(e)
    if "does not have access to the connection" in detail:
        print(
            "::error::Publish fail เพราะ SP ไม่มีสิทธิ์บน connection ที่ item อ้างอิง "
            "(known issue — connection ผูกกับ user ที่สร้างมันเท่านั้น ไม่ใช่ SP) "
            "ดู runbook ใน DataOps-CICD-Workflow.md section 12 "
            "('deploy-prod fail ด้วย connection-permission error → ทำยังไงต่อ') "
            "แนะนำให้คนที่มีสิทธิ์บน connection รัน scripts/deploy_local.py จากเครื่องตัวเองแทน"
        )
    raise

# ลบ item ที่ถูกลบออกจาก fabric_items/ แล้วออกจาก workspace ปลายทางด้วย (ไม่งั้นค้างอยู่ตลอด)
# Default = soft delete (เข้า recycle bin ของ workspace) ไม่ใช่ลบถาวร
# Lakehouse/Warehouse/SQL Database จะไม่ถูกลบโดย default (ต้องเปิด feature flag
# enable_lakehouse_unpublish / enable_warehouse_unpublish / enable_sqldatabase_unpublish
# เองถึงจะลบได้ — ตั้งใจไม่เปิดตรงนี้ เพราะ item พวกนี้มีข้อมูลจริงอยู่ข้างใน)
unpublish_all_orphan_items(workspace)
