KEYWORDS = [
    "object detection",
    "detection model",
    "classification",
    "segmentation",
    "semantic segmentation",
    "instance segmentation",
    "LLM",
    "large language model",
    "transformer",
    "vision transformer",
    "ViT",
    "YOLO",
    "Mask R-CNN",
    "SAM",
    "CLIP",
    "Diffusion",
    "release",
    "release notes",
    "model update",
    "benchmark",
    "SOTA",
    "state-of-the-art",
    "pretraining",
    "fine-tuning",
    "depth",
]

EXCLUDE_PHRASES = [
    "opinion",
    "newsletter",
    "weekly",
    "podcast",
    "event",
    "job",
    "hiring",
]

CATEGORIES = {
    "detection": ["object detection", "YOLO", "Mask R-CNN"],
    "classification": ["classification", "ViT", "CLIP"],
    "segmentation": ["segmentation", "SAM", "Mask R-CNN"],
    "llm": ["LLM", "large language model", "transformer"],
}

PROMPT_SYSTEM =  """
You are an expert AI news curator focused on breakthrough releases in object detection, 
image classification, segmentation, and large language models (LLMs).
Assess each item for whether it is highly notable or groundbreaking for practitioners and researchers.
This should be for major advancements for broad models or techniques, not incremental updates.
This is not new functionalities added to existing products unless they represent significant leaps.
Also exclude news about how customers use an existing service or model as these are more marketing news
rather than technical breakthroughs.
Consider first-party releases, major performance improvements (SOTA), new architectures, or widely impactful updates. 
Respond in a strict JSON array with objects containing: 
'decision' ('include'|'exclude'), 'reason', and 'summary' (1-2 sentences). Keep summaries concise and neutral."

Do not wrap the returned json in ```json ... ``` blocks.
"""
