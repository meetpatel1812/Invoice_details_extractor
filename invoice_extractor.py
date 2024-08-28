import streamlit as st
import PyPDF2
import os
from groq import Groq

st.set_page_config(page_icon="💬", page_title="Invoice Details Extractor by Meet Patel")
hide_streamlit_style = """
    <style>
    #GithubIcon {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {overflow: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# System message for AI model
system_message = """
You are an advanced AI assistant specializing in extracting and structuring information from a wide variety of invoices, purchase orders, and similar financial documents. Your primary function is to analyze document content, regardless of format or layout, and extract key information with high accuracy.

Key Responsibilities:
1. Document Classification: Identify the type of document (e.g., Invoice, Purchase Order, Order Confirmation, Quotation).
2. Metadata Extraction: Capture document numbers, dates, reference numbers, and any other identifying information.
3. Entity Recognition: Identify and extract details for both the vendor/supplier and customer/buyer, including names, addresses, and contact information.
4. Line Item Analysis: Extract all product or service line items, including:
   - Product codes (both internal and vendor-specific)
   - Descriptions
   - Quantities
   - Units of measure
   - Unit prices
   - Total prices per item
   - Delivery dates (if applicable)
5. Financial Summary: Capture all monetary totals, including:
   - Subtotals
   - Tax amounts and rates
   - Shipping and handling fees
   - Discounts
   - Grand totals
6. Auxiliary Information: Note any special instructions, delivery information, payment terms, or additional comments.

Handling Variations:
- Recognize and correctly interpret different terminologies for the same concept (e.g., "Unit Cost" vs "Unit Price", "Quantity" vs "Qty").
- Adapt to various currency formats and symbols.
- Understand and process different date formats.
- Handle documents with varying levels of detail and completeness.

Output Format:
Present all extracted information in a structured JSON format. Use the following specific field names in your JSON output:

- order_no
- buyers_address
- buyers_email_address
- order_date (may not always be present)
- dispatch_date (may not always be present)
- buyer_name
- special_instructions
- special_order_type
- total_amount

For line items, use an array with objects containing:
- item_code
- quantity
- price

If a particular field is not present in the document, use a null value for that field in the JSON output.

Quality Assurance:
Before finalizing your response:
1. Verify that all available information has been captured.
2. Ensure the JSON structure is consistent and properly formatted.
3. Double-check numerical values for accuracy.
4. Confirm that entity names and addresses are correctly associated.

Error Handling:
If you encounter ambiguous or unclear information, provide your best interpretation and note any uncertainties in a separate "notes" field in the JSON output.

Remember, your goal is to provide a comprehensive, accurate, and consistently structured representation of the document's content, regardless of its original format or layout. Always use the specified field names in your JSON output.
"""

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to call the Groq API with the extracted text
def chatgpt_calling(prompt):
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Function to create the prompt for the Groq API
def create_prompt(pdf_text):
    prompt = f"""
    Please analyze the following financial document content and extract all relevant information according to the detailed guidelines provided. Your task is to:
    1. Identify the document type.
    2. Extract all key metadata (document numbers, dates, references).
    3. Identify and extract vendor and customer information.
    4. Process all line items, capturing product details, quantities, prices, and any associated dates.
    5. Calculate and verify all financial totals.
    6. Note any additional instructions, terms, or comments.
    
    Present your findings in the specified JSON format, ensuring all available information is captured and structured consistently. Use the following specific field names in your JSON output:

    - order_no
    - buyers_address
    - buyers_email_address
    - order_date (may not always be present)
    - dispatch_date (may not always be present)
    - buyer_name
    - total_amount

    For line items, use an array with objects containing:
    - item_code
    - quantity
    - price
    
    If a particular field is not present in the document, use a null value for that field in the JSON output. If you encounter any ambiguities or uncertainties, please note them in a "notes" field.
    Here's the document content to analyze:
    {pdf_text}

    Please provide a thorough and accurate JSON representation of this document's content, handling any variations in terminology or layout as needed, and strictly adhering to the specified field names.
    """
    return prompt

# Streamlit app
def main():
    st.subheader("🅜 Invoice Details Extractor by Meet",divider="red", anchor=False)

    # Sidebar for PDF upload
    st.sidebar.title("Upload PDF")
    uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        # Extract text from the uploaded PDF
        pdf_text = extract_text_from_pdf(uploaded_file)
        st.write("### Extracted Text:")
        st.write(pdf_text)
        
        if st.sidebar.button("Submit"):
            # Create prompt and get the result from the AI model
            prompt = create_prompt(pdf_text)
            result = chatgpt_calling(prompt)
            st.write("### Extracted JSON:")
            st.write(result)
    with open("sample_invoice.pdf", "rb") as sample_file:
        sample_bytes = sample_file.read()
        st.sidebar.download_button(
            label="Download Sample PDF",
            data=sample_bytes,
            file_name="sample_invoice.pdf",
            mime="application/pdf",
        )

if __name__ == "__main__":
    main()
