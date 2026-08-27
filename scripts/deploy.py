import os
import argparse
from fabric_cicd import FabricWorkspace, publish_all_items
from azure.identity import InteractiveBrowserCredential

# หา path ของ fabric_items แบบ absolute อ้างอิงจากตำแหน่งไฟล์นี้เอง (อยู่ใน scripts/ ต้องขึ้นไป 1 ชั้น)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ITEMS_DIR = os.path.join(BASE_DIR, "..", "fabric_items")

parser = argparse.ArgumentParser()
parser.add_argument("--workspace", required=True, help="Fabric workspace ID (GUID)")
parser.add_argument("--environment", default="dev")
args = parser.parse_args()

# TODO: เปลี่ยนเป็น ClientSecretCredential (Service Principal) เมื่อ IT อนุมัติแล้ว
# ดูตัวอย่างใน Setup-Guide-Git-Fabric.md section 3
credential = InteractiveBrowserCredential()

workspace = FabricWorkspace(
    workspace_id=args.workspace,
    environment=args.environment,
    repository_directory=REPO_ITEMS_DIR,
    item_type_in_scope=["Notebook", "DataPipeline", "Dataflow", "Lakehouse"],
    token_credential=credential,
)

publish_all_items(workspace)
