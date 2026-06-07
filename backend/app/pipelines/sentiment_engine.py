# Module: app.pipelines.sentiment_engine
# Description: NLP engine executing FinBERT sentiment checks, spaCy entity parsing, and topical scoring.

import re
import os
import json


class SentimentEngine:
    _finbert_pipeline = None
    _spacy_nlp = None

    @classmethod
    def load_nlp_models(cls):
        """Lazily load deep learning NLP models with fallback to local rule-based models."""
        # 1. Try loading HuggingFace FinBERT Pipeline
        if cls._finbert_pipeline is None:
            try:
                from transformers import pipeline
                # Use ProsusAI/finbert as it is the standard financial sentiment model
                cls._finbert_pipeline = pipeline(
                    "sentiment-analysis", 
                    model="ProsusAI/finbert",
                    tokenizer="ProsusAI/finbert"
                )
                print("[+] Successfully loaded FinBERT pipeline.")
            except Exception as e:
                print(f"[!] Warning: FinBERT pipeline failed to load ({e}). Using lexical fallback sentiment analysis.")
                cls._finbert_pipeline = "fallback"

        # 2. Try loading spaCy Model
        if cls._spacy_nlp is None:
            try:
                import spacy
                try:
                    cls._spacy_nlp = spacy.load("en_core_web_sm")
                    print("[+] Successfully loaded spaCy en_core_web_sm.")
                except OSError:
                    # Attempt download if not present
                    print("[*] downloading spaCy model en_core_web_sm...")
                    import subprocess
                    import sys
                    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
                    cls._spacy_nlp = spacy.load("en_core_web_sm")
            except Exception as e:
                print(f"[!] Warning: spaCy en_core_web_sm failed to load ({e}). Using regex/lexical entity extraction.")
                cls._spacy_nlp = "fallback"

    @classmethod
    def analyze_sentiment(cls, text: str) -> dict:
        """Determine sentiment label, polarity, and neutral probability using FinBERT or Lexical fallback."""
        cls.load_nlp_models()
        
        # Default fallback values
        sentiment_label = "neutral"
        polarity = 0.0
        neutral_prob = 1.0

        if cls._finbert_pipeline is not None and cls._finbert_pipeline != "fallback":
            try:
                res = cls._finbert_pipeline(text[:512])[0]
                label = res["label"].lower() # positive, negative, neutral
                score = res["score"]
                
                sentiment_label = label
                if label == "positive":
                    polarity = float(score)
                    neutral_prob = 1.0 - float(score)
                elif label == "negative":
                    polarity = -float(score)
                    neutral_prob = 1.0 - float(score)
                else:
                    polarity = 0.0
                    neutral_prob = float(score)
                
                return {
                    "label": sentiment_label,
                    "polarity": round(polarity, 4),
                    "neutral_prob": round(neutral_prob, 4)
                }
            except Exception as e:
                print(f"FinBERT inference failed ({e}). Running lexical fallback.")

        # Lexical Fallback logic (Loughran-McDonald approach)
        text_lower = text.lower()
        bearish_words = {"decline", "fall", "drop", "cut", "loss", "deficit", "recession", "slump", "negative", "downward", "inflation", "bearish", "crisis", "pressure", "hike"}
        bullish_words = {"growth", "gain", "profit", "rise", "surge", "increase", "bullish", "expansion", "positive", "stabilize", "recovery", "boost"}
        
        bear_count = sum(1 for word in bearish_words if word in text_lower)
        bull_count = sum(1 for word in bullish_words if word in text_lower)
        
        total = bear_count + bull_count
        if total > 0:
            net_sentiment = (bull_count - bear_count) / total
            polarity = net_sentiment
            neutral_prob = 1.0 - abs(net_sentiment)
            if net_sentiment > 0.15:
                sentiment_label = "positive"
            elif net_sentiment < -0.15:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
        
        return {
            "label": sentiment_label,
            "polarity": round(polarity, 4),
            "neutral_prob": round(neutral_prob, 4)
        }

    @classmethod
    def extract_entities(cls, text: str) -> list:
        """Extract monetary, geographical, and organizational entities."""
        cls.load_nlp_models()
        
        entities = []
        
        # spaCy extraction
        if cls._spacy_nlp is not None and cls._spacy_nlp != "fallback":
            try:
                doc = cls._spacy_nlp(text)
                for ent in doc.ents:
                    if ent.label_ in ["ORG", "GPE", "MONEY", "PRODUCT"]:
                        entities.append({
                            "name": ent.text,
                            "label": ent.label_
                        })
                return entities
            except Exception as e:
                print(f"spaCy NER failed ({e}). Running lexical extraction.")

        # Lexical Fallback NER
        # Regex scans for currencies, organizations, and Indian locations
        currencies = ["usd", "inr", "eur", "rupee", "dollar", "gold", "oil", "crude", "brent"]
        orgs = ["rbi", "fed", "mospi", "sebi", "central bank", "government", "imf", "world bank"]
        locations = ["india", "delhi", "mumbai", "maharashtra", "gujarat", "karnataka", "tamil nadu", "bengaluru"]
        
        text_lower = text.lower()
        for curr in currencies:
            if re.search(r'\b' + curr + r'\b', text_lower):
                entities.append({"name": curr.upper(), "label": "MONEY"})
        for org in orgs:
            if re.search(r'\b' + org + r'\b', text_lower):
                entities.append({"name": org.upper(), "label": "ORG"})
        for loc in locations:
            if re.search(r'\b' + loc + r'\b', text_lower):
                entities.append({"name": loc.title(), "label": "GPE"})
                
        return entities

    @classmethod
    def classify_topic(cls, text: str) -> str:
        """Classify article into economic taxonomy topics based on keyword density."""
        text_lower = text.lower()
        
        topic_keywords = {
            "Monetary Policy": ["repo", "rate", "interest", "rbi", "hike", "cut", "fed", "central bank", "monetary", "policy"],
            "Commodity Shocks": ["oil", "gas", "gold", "crude", "energy", "commodity", "fuel", "brent", "barrel"],
            "Food & Agriculture": ["crop", "wheat", "rice", "food", "vegetable", "agriculture", "monsoon", "grain", "onion", "pulses"],
            "Supply Chain & Logistics": ["supply chain", "shipping", "logistics", "freight", "delay", "transport", "shortage", "port"],
            "Currency & Exchange Rates": ["rupee", "exchange rate", "dollar", "usd", "inr", "currency", "forex", "depreciation"]
        }
        
        best_topic = "General Macroeconomics"
        max_matches = 0
        
        for topic, keywords in topic_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > max_matches:
                max_matches = matches
                best_topic = topic
                
        return best_topic

    @classmethod
    def compute_regional_impact(cls, entities: list) -> dict:
        """Map extracted regional locations to geopolitical impact categories."""
        impact = {}
        for ent in entities:
            if ent["label"] == "GPE":
                loc = ent["name"].title()
                impact[loc] = impact.get(loc, 0) + 1
        return impact
