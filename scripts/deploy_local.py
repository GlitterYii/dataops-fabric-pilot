import os
import shutil
import argparse
from fabric_cicd import FabricWorkspace, publish_all_items, unpublish_all_orphan_items
from azure.identity import InteractiveBrowserCredential

# Manual escape hatch สำหรับกรณีที่ deploy.py (Service Principal) publish ไม่ผ่านเพราะ
# "User does not have access to the connection used in the Pipeline" — SP ไม่มีสิทธิ์บน
# connection ที่ item อ้างอิง (เช่น Copy Data ไปยัง Lakehouse/Warehouse) แต่ user คนที่สร้าง
# connection เองมีสิทธิ์อยู่แล้ว — รันจากเครื่องตัวเอง (เปิด browser login) แทน SP
#
# ข้อจำกัด: รันผ่าน GitHub Actions ไม่ได้ (runner เปิด browser login ไม่ได้) ใช้เป็น fallback
# รันมือเท่านั้น ไม่ใช่ตัวแทน deploy-prod ถาวร

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ITEMS_DIR = os.path.join(BASE_DIR, "..", "fabric_items")

# item type ทั้งหมดที่ fabric-cicd รองรับ — ต้อง sync กับ deploy.py เสมอ (ดู comment ที่นั่น
# สำหรับที่มาของ list นี้: fabric_cicd.constants.ItemType)
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


# workspace GUID ของแต่ละ environment ที่รู้จักอยู่แล้ว (เอามาจาก deploy-prod step ใน
# fabric-ci.yml และ SP-Connection-Experiment-Plan.md) — ให้ไม่ต้องพิมพ์ GUID เองทุกครั้ง
ENVIRONMENT_WORKSPACE_IDS = {
    "dev": "7a829f6b-4fd1-45c7-8c8e-b7c317816e4b",
    "prod": "84cc9682-9946-44a6-83b4-9275ebfb9834",
    "target": "84cc9682-9946-44a6-83b4-9275ebfb9834",  # alias ของ prod (ws-pilot-target)
}


def _clean_pycache(root: str) -> None:
    for dirpath, dirnames, _ in os.walk(root):
        if "__pycache__" in dirnames:
            shutil.rmtree(os.path.join(dirpath, "__pycache__"))
            dirnames.remove("__pycache__")


parser = argparse.ArgumentParser()
parser.add_argument(
    "--workspace",
    help="Fabric workspace ID (GUID) — ไม่ใส่ก็ได้ถ้า --environment ตรงกับ dev/prod/target "
    "(resolve GUID ให้อัตโนมัติ) ใส่เฉพาะตอน environment ใหม่ที่ยังไม่รู้จัก",
)
parser.add_argument("--environment", default="dev")
args = parser.parse_args()

if args.workspace:
    workspace_id = args.workspace
elif args.environment in ENVIRONMENT_WORKSPACE_IDS:
    workspace_id = ENVIRONMENT_WORKSPACE_IDS[args.environment]
else:
    raise SystemExit(
        f"ไม่รู้จัก workspace GUID ของ environment '{args.environment}' "
        f"(รู้จักแค่ {list(ENVIRONMENT_WORKSPACE_IDS)}) — ใส่ --workspace <GUID> เองด้วย"
    )

_clean_pycache(REPO_ITEMS_DIR)

credential = InteractiveBrowserCredential()

workspace = FabricWorkspace(
    workspace_id=workspace_id,
    environment=args.environment,
    repository_directory=REPO_ITEMS_DIR,
    item_type_in_scope=ALL_SUPPORTED_ITEM_TYPES,
    token_credential=credential,
)

publish_all_items(workspace)
unpublish_all_orphan_items(workspace)
