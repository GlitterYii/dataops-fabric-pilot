import os
import shutil
import argparse
from fabric_cicd import FabricWorkspace, publish_all_items
from azure.identity import ClientSecretCredential

# หา path ของ fabric_items แบบ absolute อ้างอิงจากตำแหน่งไฟล์นี้เอง (อยู่ใน scripts/ ต้องขึ้นไป 1 ชั้น)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ITEMS_DIR = os.path.join(BASE_DIR, "..", "fabric_items")


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
    item_type_in_scope=["Notebook", "DataPipeline", "Dataflow", "Lakehouse"],
    token_credential=credential,
)

publish_all_items(workspace)
