from fabric_cicd import FabricWorkspace, publish_all_items
from azure.identity import InteractiveBrowserCredential

credential = InteractiveBrowserCredential()

workspace = FabricWorkspace(
    workspace_id="84cc9682-9946-44a6-83b4-9275ebfb9834",
    environment="dev",
    repository_directory="./fabric_items",   # path ที่ตั้งไว้ตอนเชื่อม Git integration
    item_type_in_scope=["Notebook"],
    token_credential=credential,
)

publish_all_items(workspace)