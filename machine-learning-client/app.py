import os
import uuid
import nltk
from nltk.tokenize import word_tokenize
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from gensim import corpora, models
from nltk.corpus import stopwords
from gensim.models import CoherenceModel
from gensim.models.phrases import Phrases, Phraser
from gensim.utils import simple_preprocess
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from collections import defaultdict
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import text2emotion as te


# step 1: retrive the data in this structure
# {
#     "_id": ObjectId("..."),
#     "request_id": "unique_request_id",
#     "sentences": [
#         {
#             "sentence": "Sentence 1.",
#             "status": "pending",
#             "analysis": null
#         },
#         {
#             "sentence": "Sentence 2.",
#             "status": "pending",
#             "analysis": null
#         },
#         // ... more sentences
#     ],
#     "overall_status": "pending",   // Indicates the status of the entire submission
#     "timestamp": ISODate("...")    // Timestamp of the submission
# }

# step 2: do analysis and store Compond, Neutural, Postive, and Negative metircs into analysis field
# step 3: do Topic Modeling, Emotion Detection, Text Summarization, Sentiment Trend Analysis

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["sentiment"]
texts_collection = db["texts"]

# download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('vader_lexicon')

def perform_sentiment_analysis(sentences):
    analyzer = SentimentIntensityAnalyzer()
    def analyze_sentence(sentence_entry):
        if sentence_entry["status"] == "pending":
            sentiment_scores = analyzer.polarity_scores(sentence_entry["sentence"])
            return {
                **sentence_entry, # unpack dictionary: extracts all key-value pairs from that dictionary
                "analysis": sentiment_scores,
                "status": "processed"
            }
        else:
            return sentence_entry
    return list(map(analyze_sentence, sentences))

"""
reference: 
https://radimrehurek.com/gensim/corpora/dictionary.html
https://radimrehurek.com/gensim/models/ldamodel.html
https://www.machinelearningplus.com/nlp/topic-modeling-gensim-python/
https://www.tutorialspoint.com//gensim/gensim_topic_modeling.htm
https://www.nltk.org/api/nltk.stem.wordnet.html#nltk.stem.wordnet.WordNetLemmatizer
"""
# topic modeling
def perform_topic_modeling(sentences, num_topics=5):
    """
    Perform topic modeling on the list of sentences.
    Identifies main topics using LDA with improved preprocessing.
    
    :param sentences: List of sentence entries
    :param num_topics: Number of topics to identify
    :return: List of identified topics
    """
    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()
    
    # Preprocess
    def preprocess(text):
        tokens = word_tokenize(text.lower())
        tokens = [lemmatizer.lemmatize(token) for token in tokens if token.isalnum()]
        tokens = [token for token in tokens if token not in stop_words]
        return tokens
    
    texts = list(map(preprocess, [sentence_entry["sentence"] for sentence_entry in sentences]))
    
    # Create bigrams
    bigram = Phrases(texts, min_count=5, threshold=100)
    bigram_mod = Phraser(bigram)
    texts = [bigram_mod[doc] for doc in texts]
    
    # Create dictionary and filter extremes
    dictionary = corpora.Dictionary(texts)
    dictionary.filter_extremes(no_below=5, no_above=0.5)
    
    # Create corpus
    corpus = [dictionary.doc2bow(text) for text in texts]
    
    # Build LDA model
    lda_model = models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15, iterations=100, alpha='auto', eta='auto', random_state=42)
    
    # Compute coherence score
    coherence_model_lda = CoherenceModel(model=lda_model, texts=texts, dictionary=dictionary, coherence='c_v')
    coherence_score = coherence_model_lda.get_coherence()
    print(f"Coherence Score: {coherence_score}")
    
    topics = lda_model.print_topics(num_words=4)
    return topics

# emotion detection
def perform_emotion_detection(sentences):
    """
    Detect emotions in each sentence using the text2emotion package.
    Adds an 'emotions' field to each sentence entry.
    
    :param sentences: List of sentence entries
    :return: Updated list of sentence entries with emotions detected
    """
    
    def detect_emotion(sentence_entry):
        if "analysis" in sentence_entry and sentence_entry["analysis"] is not None:
            text = sentence_entry["sentence"]
            emotions = te.get_emotion(text)
            # determin dominat emotion(s)
            if any(emotions.values()):
                max_value = max(emotions.values())
                dominant_emotions = [emotion for emotion, score in emotions.items() if score == max_value and score > 0]
            else:
                dominant_emotions = ["Neutural"]
            
            return { 
                **sentence_entry,
                "emotions": dominant_emotions
            }
        else:
            return sentence_entry
    
    return list(map(detect_emotion, sentences))

# overall emotion detection
def perform_overall_emotion_detection(sentences):
    """
    Determine the overall dominant emotion(s) across all sentences.
    Adds an 'overall_emotions' field to the document.
    
    :param sentences: List of sentence entries
    :return: Overall emotions list
    """

    emotion_counter = defaultdict(int)
    for sentence in sentences:
        emotions = sentence.get("emotions", [])
        for emotion in emotions:
            emotion_counter[emotion] += 1

    if emotion_counter:
        max_count = max(emotion_counter.values())
        dominant_overall_emotions = [emotion for emotion, count in emotion_counter.items() if count == max_count]
    else:
        dominant_overall_emotions = ["Neutural"]

    return dominant_overall_emotions

# text summarization
def perform_text_summarization(sentences, sentence_count=5):
    """
    Generate a summary of the text using LexRank summarizer.
    
    :param sentences: List of sentence entries
    :param sentence_count: Number of sentences in the summary
    :return: Summary string
    """
    full_text = " ".join(sentence["sentence"] for sentence in sentences)
    parser = PlaintextParser.from_string(full_text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary_sentences = summarizer(parser.document, sentences_count=sentence_count)
    summary = " ".join(str(sentence) for sentence in summary_sentences)
    return summary

# sentiment trend analysis
def perform_sentiment_trend_analysis(sentences):
    """
    Analyze sentiment trend by tracking compound scores of each sentence.
    Returns a list of sentiment scores with sentence indices.
    
    :param sentences: List of sentence entries
    :return: List of dictionaries with sentence index and compound score
    """
    def extract_compound_score(idx_entry):
        index, sentence_entry = idx_entry
        compound_score = sentence_entry["analysis"]["compound"] if sentence_entry.get("analysis") else 0
        return { 
            "sentence_index": index,
            "compound": compound_score
        }
    
    return list(map(extract_compound_score, enumerate(sentences)))

# process all
def process_document(document):
    """
    Process a single document: perform sentiment analysis, topic modeling,
    emotion detection, text summarization, and sentiment trend analysis.
    
    :param document: MongoDB document
    :return: Updated document with analyses
    """
    sentences = document["sentences"]
    sentences = perform_sentiment_analysis(sentences)
    topics = perform_topic_modeling(sentences)
    sentences = perform_emotion_detection(sentences)
    summary = perform_text_summarization(sentences)
    sentiment_trend = perform_sentiment_trend_analysis(sentences)
    overall_emotions = perform_overall_emotion_detection(sentences)
    # update document
    updated_document = {
        **document,
        "sentences": sentences,
        "overall_status": "processed",
        "topics": topics,
        "summary": summary,
        "sentiment_trend": sentiment_trend,
        "overall_emotions": overall_emotions,
        "timestamp": datetime.now()
    }
    return updated_document

# update to database
def update_document_in_db(document):
    doc_id = document["_id"]
    texts_collection.update_one(
        {"_id": doc_id},
        {"$set": {
            "sentences": document["sentences"],
            "overall_status": document["overall_status"],
            "topics": document["topics"],
            "summary": document["summary"],
            "sentiment_trend": document["sentiment_trend"],
            "overall_emotions": document["overall_emotions"],
            "timestamp": document["timestamp"]
        }}
    )

def main():
    pending_documents = texts_collection.find({"overall_status": "pending"})
    for document in pending_documents:
        updated_document = process_document(document)
        update_document_in_db(updated_document)
        print(f"Processed document with request_id: {document['request_id']}")
    print("Sentiment analysis and additional analyses completed for all pending documents.")

if __name__ == "__main__":
    main()
