"""
Example: ImageGeneration backend with LangSmith integration
This shows how to integrate LangSmith tracing into your existing services.
"""

import base64
import os
import requests
import json
from typing import List
from langsmith_config import trace_llm_call, token_tracker, get_langsmith_url
from langsmith import traceable

# Example of wrapping the Gemini API call with LangSmith tracing
@trace_llm_call(
    name="gemini_image_generation",
    service="ImageGeneration",
    metadata={"api": "gemini"}
)
def call_nano_banana_traced(
    api_key: str,
    prompt: str,
    images: List[dict] = None,
    model: str = "gemini-2.5-flash-image",
    grounding: bool = False,
    aspect_ratio: str = None,
    user_id: str = None,
    job_id: str = None
):
    """
    Traced version of call_nano_banana with LangSmith integration.
    This automatically creates a trace in LangSmith with:
    - Waterfall visualization
    - Token usage
    - Cost analysis
    - Input/output logging
    """
    from langsmith.run_helpers import get_current_run_tree
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    
    parts = [{'text': prompt}]
    if images:
        for img in images:
            parts.append({'inlineData': {'data': img['data'], 'mimeType': img['mime']}})
    
    if aspect_ratio:
        parts[0]['text'] += f"\\n\\nAspect Ratio: {aspect_ratio}"
    
    payload = {'contents': [{'parts': parts}]}
    
    if grounding and "gemini-3-pro" in model:
        payload['tools'] = [{'google_search': {}}]
    
    # Add metadata to current run
    run_tree = get_current_run_tree()
    if run_tree:
        run_tree.metadata.update({
            "model": model,
            "grounding": grounding,
            "aspect_ratio": aspect_ratio,
            "user_id": user_id,
            "job_id": job_id,
            "prompt_length": len(prompt)
        })
        run_tree.inputs = {"prompt": prompt, "model": model}
    
    # Make the API call
    res = requests.post(f"{url}?key={api_key}", json=payload, headers={"Content-Type": "application/json"})
    
    if res.status_code != 200:
        error_msg = f"Error {res.status_code}: {res.text}"
        if run_tree:
            run_tree.error = error_msg
        return None, None, error_msg, res.status_code, 0
    
    data = res.json()
    parts_out = data.get('candidates', [{}])[0].get('content', {}).get('parts', [])
    
    # Extract token usage
    usage = data.get('usageMetadata', {})
    total_tokens = usage.get('totalTokenCount', 0)
    input_tokens = usage.get('promptTokenCount', 0)
    output_tokens = usage.get('candidatesTokenCount', 0)
    
    # Log token usage
    if user_id and job_id:
        token_tracker.log_usage(
            service="ImageGeneration",
            operation="generate_image",
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            user_id=user_id,
            job_id=job_id
        )
    
    # Update run metadata with token info
    if run_tree:
        from langsmith_config import calculate_cost
        cost = calculate_cost(model, input_tokens, output_tokens)
        
        run_tree.metadata.update({
            "total_tokens": total_tokens,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost_usd": cost
        })
    
    # Extract image
    for p in parts_out:
        if 'inlineData' in p:
            img_data = p['inlineData']['data']
            mime = p['inlineData'].get('mimeType', 'image/png')
            
            if run_tree:
                run_tree.outputs = {
                    "success": True,
                    "mime_type": mime,
                    "image_size_bytes": len(img_data)
                }
            
            return img_data, mime, None, 200, total_tokens
    
    return None, None, "No image returned", 500, 0


# Example of tracing an entire endpoint
@traceable(
    name="generate_image_endpoint",
    run_type="chain",
    project_name="NexusAI"
)
def generate_image_traced(
    prompt: str,
    model: str,
    api_key: str,
    user_id: str = None,
    job_id: str = None,
    grounding: bool = False,
    aspect_ratio: str = None
):
    """
    Example of a traced endpoint that shows the full flow:
    1. Input validation
    2. Prompt enhancement
    3. API call
    4. Response processing
    
    This creates a hierarchical trace in LangSmith showing all steps.
    """
    from langsmith.run_helpers import get_current_run_tree
    
    # Add metadata to the top-level run
    run_tree = get_current_run_tree()
    if run_tree:
        run_tree.metadata.update({
            "endpoint": "generate_image",
            "user_id": user_id,
            "job_id": job_id
        })
        run_tree.inputs = {
            "prompt": prompt,
            "model": model,
            "grounding": grounding
        }
    
    # Step 1: Enhance prompt (this will be a child trace)
    enhanced_prompt = enhance_prompt_traced(prompt)
    
    # Step 2: Call Gemini API (this will be another child trace)
    img_b64, mime, error, status, tokens = call_nano_banana_traced(
        api_key=api_key,
        prompt=enhanced_prompt,
        model=model,
        grounding=grounding,
        aspect_ratio=aspect_ratio,
        user_id=user_id,
        job_id=job_id
    )
    
    # Update outputs
    if run_tree:
        run_tree.outputs = {
            "success": error is None,
            "error": error,
            "status_code": status,
            "tokens_used": tokens
        }
    
    return img_b64, mime, error, status, tokens


@traceable(name="enhance_prompt", run_type="tool")
def enhance_prompt_traced(prompt: str) -> str:
    """
    Example of a traced utility function.
    This will appear as a separate step in the waterfall.
    """
    # Your prompt enhancement logic here
    system_prompt = "Create a highly detailed, photorealistic image of: "
    return f"{system_prompt}{prompt}"


# Example usage in your endpoint:
"""
@router.post("/generate")
def generate_image(
    api_key: str = Form(None), 
    prompt: str = Form(...), 
    model: str = Form("gemini-2.5-flash-image"), 
    grounding: bool = Form(False), 
    aspect_ratio: str = Form(None),
    user_id: str = Form(None),
    token_uid: str = Depends(verify_token)
):
    job_id = str(uuid.uuid4())
    
    # Use the traced version
    img_b64, mime, error, status, tokens = generate_image_traced(
        prompt=prompt,
        model=model,
        api_key=get_api_key(api_key),
        user_id=user_id,
        job_id=job_id,
        grounding=grounding,
        aspect_ratio=aspect_ratio
    )
    
    if img_b64:
        # Get LangSmith trace URL
        from langsmith.run_helpers import get_current_run_tree
        run_tree = get_current_run_tree()
        if run_tree:
            trace_url = get_langsmith_url(run_tree.id)
            print(f"View trace: {trace_url}")
        
        return JSONResponse({
            "image": img_b64,
            "mime": mime,
            "tokens": tokens,
            "trace_url": trace_url if run_tree else None
        })
    
    return JSONResponse({"detail": error}, status_code=status)
"""
