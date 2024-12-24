import os
from datetime import datetime
import pandas as pd
from pydantic import BaseModel, create_model
from typing import List, Type
import tiktoken
import math
import json
from assets import setup_selenium_driver
from aimodels import gpt_generate_response, gemini_generate_response  
SYSTEM_MESSAGE = """You are an intelligent text extraction and conversion assistant. Your task is to extract structured information
                    from the given text and convert it into a pure JSON format. The JSON should contain only the structured data extracted from the text,
                    with no additional commentary, explanations, or extraneous information."""
USER_MESSAGE = "Extract the following information from the provided text:\nPage content:\n\n"
def scrape_raw_html(url):
    driver = setup_selenium_driver()
    driver.get(url)
    raw_html = driver.page_source
    driver.quit()
    return raw_html

def convert_to_markdown(raw_html):
    import html2text
    converter = html2text.HTML2Text()
    converter.ignore_links = True
    markdown_text = converter.handle(raw_html)
    return markdown_text

def create_dynamic_listing_model(field_names: List[str]) -> Type[BaseModel]:
    field_definitions = {field: (str, ...) for field in field_names}
    return create_model("DynamicListingModel", **field_definitions)

def create_listings_container_model(listing_model: Type[BaseModel]) -> Type[BaseModel]:
    return create_model("DynamicListingsContainer", listings=(List[listing_model], ...))

def split_text_by_tokens(text, max_tokens):
    encoder = tiktoken.encoding_for_model("gpt-4")
    tokens = encoder.encode(text)
    num_chunks = math.ceil(len(tokens) / max_tokens)
    token_chunks = [tokens[i * max_tokens: (i + 1) * max_tokens] for i in range(num_chunks)]
    return [encoder.decode(chunk) for chunk in token_chunks]

def format_data_in_chunks(data, container_model, model_name, max_tokens=3000):
    text_chunks = split_text_by_tokens(data['markdown_text'], max_tokens)
    response_texts = []

    for chunk in text_chunks:
        prompt = f"{USER_MESSAGE}{data['fields']} from the following text:\n\n{chunk}"

        if model_name == "gpt-4":
            response_text = gpt_generate_response(prompt, SYSTEM_MESSAGE)
        elif model_name == "gemini-flash":
            response_text = gemini_generate_response(prompt, container_model)
        
        if response_text:
            response_texts.append(response_text)
            print(f"{model_name} Response for chunk:", response_text)

    combined_data = []
    for response_text in response_texts:
        try:
            parsed_data = json.loads(response_text)
            combined_data.extend(parsed_data.get("listings", []))
        except json.JSONDecodeError:
            print("Error decoding JSON for a chunk; skipping this chunk.")
            continue

    return {"listings": combined_data}

def scrape_and_convert(url, fields, model_choice):
    raw_html = scrape_raw_html(url)
    markdown_text = convert_to_markdown(raw_html)
    
    DynamicListingModel = create_dynamic_listing_model(fields)
    DynamicListingsContainer = create_listings_container_model(DynamicListingModel)
    
    formatted_result = format_data_in_chunks(
        data={"markdown_text": markdown_text, "fields": fields},
        container_model=DynamicListingsContainer,
        model_name=model_choice
    )
    
    formatted_table = pd.DataFrame(formatted_result.get("listings", []))
    formatted_table.index.name = 'Index'
    
    return {
        "table": formatted_table,
    }
