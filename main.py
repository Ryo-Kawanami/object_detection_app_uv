from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse 
from transformers import DetrImageProcessor, DetrForObjectDetection
from PIL import Image
import torch
import io
from pydantic import BaseModel
from typing import List

app = FastAPI(title="DETR Object Detection API")

# モデル設定
MODEL_NAME = "facebook/detr-resnet-50"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading model on {DEVICE}...")
processor = DetrImageProcessor.from_pretrained(MODEL_NAME)
model = DetrForObjectDetection.from_pretrained(MODEL_NAME)
model.to(DEVICE)
model.eval()

# レスポンス型
class BoundingBox(BaseModel):
    xmin: float
    ymin: float
    xmax: float
    ymax: float

class DetectionResult(BaseModel):
    label: str
    score: float
    box: BoundingBox

class ResponseModel(BaseModel):
    filename: str
    detections: List[DetectionResult]


# APIエンドポイント
@app.post("/detect", response_model=ResponseModel)
async def detect_objects(file: UploadFile = File(...), threshold: float = 0.9):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    inputs = processor(images=image, return_tensors="pt")
    inputs = inputs.to(DEVICE)

    with torch.no_grad():
        outputs = model(**inputs)

    target_sizes = torch.tensor([image.size[::-1]]).to(DEVICE)
    results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=threshold)[0]

    detections = []
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        box_data = [round(i, 2) for i in box.tolist()]
        detections.append(DetectionResult(
            label=model.config.id2label[label.item()],
            score=round(score.item(), 4),
            box=BoundingBox(
                xmin=box_data[0], ymin=box_data[1], xmax=box_data[2], ymax=box_data[3]
            )
        ))

    return {"filename": file.filename, "detections": detections}

# フロントエンド配信設定
# 1. ルートアクセスでindex.htmlを返す
@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

# 2. staticディレクトリをマウント
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)