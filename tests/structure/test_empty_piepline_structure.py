import json
import os

PIPELINE_DIR = "fabric_items/pl_test_2.DataPipeline"

def test_pipeline_json_exists():
    """เช็คว่า pipeline-content.json มีอยู่จริง"""
    path = f"{PIPELINE_DIR}/pipeline-content.json"
    assert os.path.exists(path), f"File not found: {path}"

def test_pipeline_json_valid():
    """เช็คว่า JSON format ถูกต้อง อ่านได้"""
    path = f"{PIPELINE_DIR}/pipeline-content.json"
    with open(path, "r") as f:
        data = json.load(f)  # ถ้า JSON ผิด format จะ throw error ตรงนี้

    assert isinstance(data, dict), "Pipeline content must be a JSON object"

def test_platform_metadata_exists():
    """เช็คว่ามี .platform metadata file"""
    path = f"{PIPELINE_DIR}/.platform"
    assert os.path.exists(path), f"Metadata file not found: {path}"