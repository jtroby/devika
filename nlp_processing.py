# nlp_processing.py
from transformers import pipeline

# Initialize summarization and sentiment analysis pipelines.
# You can choose a summarization model like "facebook/bart-large-cnn" or "t5-small" as needed.
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
sentiment_analyzer = pipeline("sentiment-analysis")

def summarize_text(text, max_length=130, min_length=30):
    """
    Summarizes the provided text using a Hugging Face summarization model.
    """
    try:
        summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"Error during summarization: {str(e)}"

def analyze_sentiment(text):
    """
    Analyzes the sentiment of the provided text.
    """
    try:
        result = sentiment_analyzer(text)
        return result[0]  # returns a dict with 'label' and 'score'
    except Exception as e:
        return f"Error during sentiment analysis: {str(e)}"

if __name__ == "__main__":
    # Test text for summarization and sentiment analysis
    test_text = (
        "Artificial Intelligence is transforming many industries by automating processes, "
        "enhancing data analysis, and improving decision-making processes. Its rapid development "
        "has led to groundbreaking innovations across various fields."
    )
    
    print("Original Text:")
    print(test_text)
    print("\nSummary:")
    print(summarize_text(test_text))
    print("\nSentiment Analysis:")
    print(analyze_sentiment(test_text))
