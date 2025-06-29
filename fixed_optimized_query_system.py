#!/usr/bin/env python3
"""
Fixed Optimized Ski Equipment Query System - Version 2.4
LLM-Enhanced Property Response Generation

CRITICAL UPDATE: Added LLM prompts for property responses:
- First level: search vs property (rule-based)
- Second level (for property): property:property vs property:general (rule-based)
- Final response generation: LLM-powered with full product data and flex ratings (Gemini API)
"""

import logging
import time
import pandas as pd
import re
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
import sys
import os
import json

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. Install with: pip install google-generativeai")

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('query_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set Gemini API key (configure via environment variable)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
# Note: genai.configure() is now called dynamically in LLMCaller.call_gemini()

@dataclass
class QueryResult:
    """Structured result for queries."""
    intent: str
    response: str
    confidence: float
    processing_time: float
    data_sources: List[str]
    error_message: Optional[str] = None
    matched_products: Optional[List[Dict]] = None
    raw_technical_response: Optional[str] = None  # Store original technical response

class DataValidator:
    """Validates and preprocesses data for better accuracy."""
    
    # Define which fields contain default/placeholder values that should be treated as missing
    DEFAULT_VALUES = {
        'turn_radius_m': [20.0],  # 20.0 is a default value, not real data
        'weight_grams': [1140.0], # 1140.0 appears to be a default value
        'model_year': ['', None],  # Empty values
    }
    
    @staticmethod
    def validate_csv_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate the CSV data quality."""
        issues = []
        
        # Check for required columns
        required_cols = ['title', 'brand', 'price', 'waist_width_mm']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            issues.append(f"Missing required columns: {missing_cols}")
        
        # Check for default/placeholder values
        for col, defaults in DataValidator.DEFAULT_VALUES.items():
            if col in df.columns:
                default_count = df[col].isin(defaults).sum()
                if default_count > len(df) * 0.8:  # More than 80% are defaults
                    issues.append(f"Column '{col}' contains mostly default values ({default_count}/{len(df)})")
        
        # Check data completeness for real data
        completeness = {}
        for col in df.columns:
            if col in df.select_dtypes(include=['object']).columns:
                non_empty = df[col].notna() & (df[col] != '') & (df[col] != 'unknown')
                completeness[col] = non_empty.sum() / len(df) * 100
            else:
                # For numeric columns, exclude default values
                if col in DataValidator.DEFAULT_VALUES:
                    non_default = ~df[col].isin(DataValidator.DEFAULT_VALUES[col])
                    completeness[col] = non_default.sum() / len(df) * 100
                else:
                    completeness[col] = df[col].notna().sum() / len(df) * 100
        
        # Report low completeness
        low_completeness = {k: v for k, v in completeness.items() if v < 70}
        if low_completeness:
            issues.append(f"Low data completeness: {low_completeness}")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def clean_product_data(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize product data, removing default/placeholder values."""
        df = df.copy()
        
        # Replace default values with NaN to indicate missing data
        for col, defaults in DataValidator.DEFAULT_VALUES.items():
            if col in df.columns:
                df.loc[df[col].isin(defaults), col] = pd.NA
                logger.info(f"Replaced {defaults} with NaN in column '{col}' as these are default values")
        
        # Standardize text fields
        text_columns = df.select_dtypes(include=['object']).columns
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace(['nan', 'None', ''], None)
        
        # Ensure numeric fields are properly typed
        numeric_fields = ['waist_width_mm', 'price', 'weight_grams', 'turn_radius_m']
        for field in numeric_fields:
            if field in df.columns:
                df[field] = pd.to_numeric(df[field], errors='coerce')
        
        # Standardize brand names
        if 'brand' in df.columns:
            df['brand'] = df['brand'].str.lower().str.strip()
        
        # Parse length information more robustly
        if 'lengths_cm' in df.columns:
            df['parsed_lengths'] = df['lengths_cm'].apply(DataValidator._parse_lengths)
        
        return df
    
    @staticmethod
    def _parse_lengths(length_str: str) -> List[int]:
        """Parse length string into list of integers."""
        if pd.isna(length_str) or length_str == '':
            return []
        
        # Extract numbers from string
        numbers = re.findall(r'\d+', str(length_str))
        return [int(n) for n in numbers if 130 <= int(n) <= 220]  # Reasonable ski lengths
    
    @staticmethod
    def is_real_data(value: Any, column: str) -> bool:
        """Check if a value represents real data (not a default/placeholder)."""
        if pd.isna(value):
            return False
        
        if column in DataValidator.DEFAULT_VALUES:
            return value not in DataValidator.DEFAULT_VALUES[column]
        
        return True

class EnhancedProductMatcher:
    """Enhanced product matching with fuzzy search and validation."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.brand_patterns = self._build_brand_patterns()
        self.model_patterns = self._build_model_patterns()
        
    def _build_brand_patterns(self) -> Dict[str, List[str]]:
        """Build comprehensive brand pattern matching."""
        patterns = {
            'atomic': ['atomic'],
            'salomon': ['salomon'],
            'rossignol': ['rossignol'],
            'k2': ['k2'],
            'armada': ['armada'],
            'volkl': ['völkl', 'volkl'],
            'line': ['line'],
            'faction': ['faction'],
            'dynafit': ['dynafit'],
            'dps': ['dps'],
            'nordica': ['nordica'],
            'stockli': ['stöckli', 'stockli'],
            'fischer': ['fischer'],
            'head': ['head'],
            'blizzard': ['blizzard'],
            'scott': ['scott'],
            'extrem': ['extrem']  # Added Extrem brand
        }
        return patterns
    
    def _build_model_patterns(self) -> List[str]:
        """Build comprehensive model pattern matching."""
        return [
            # Atomic models
            r'bent\s*(\d+|chetler)', r'maverick', r'redster', r'vantage',
            # Salomon models  
            r'qst\s*(lux\s*)?(\d+)', r'stance', r'x\-drive', r'x\-access',
            # Armada models
            r'arv\s*\d+', r'declivity', r'tracer', r'invictus',
            # Line models
            r'pandora', r'chronic', r'sakana', r'vision', r'reckoner',
            # Faction models
            r'prodigy\s*\d*', r'candide', r'chapter',
            # Völkl models
            r'blaze\s*\d+', r'mantra', r'kendo', r'secret',
            # Dynafit models
            r'blacklight\s*\d*', r'radical', r'speed',
            # Extrem models
            r'mother\s*tree\s*\d*', r'mothertree\s*\d*',
            # Other common models
            r'rustler', r'laser', r'wailer', r'santa\s*ana', r'enforcer',
            # Added missing models
            r'explorair', r'montero'
        ]
    
    def find_products(self, query: str, max_results: int = 10) -> List[Dict]:
        """Find products matching the query with enhanced search."""
        query_lower = query.lower()
        matches = []
        
        # Extract potential product names and brands
        brands = self._extract_brands(query_lower)
        models = self._extract_models(query_lower)
        numbers = self._extract_numbers(query_lower)
        
        # Enhanced product matching with multiple passes for better accuracy
        
        # Pass 1: Exact brand + model matches (highest priority)
        for idx, row in self.df.iterrows():
            score = self._calculate_match_score(row, query_lower, brands, models, numbers)
            if score > 0.8:  # High confidence matches
                product_dict = row.to_dict()
                product_dict['match_score'] = score
                matches.append(product_dict)
        
        # Pass 2: If we need more matches, try partial matches
        if len(matches) < max_results:
            for idx, row in self.df.iterrows():
                # Skip if already matched
                if any(existing['title'] == row.get('title') for existing in matches):
                    continue
                    
                score = self._calculate_match_score(row, query_lower, brands, models, numbers)
                if score > 0.3:  # Medium confidence matches
                    product_dict = row.to_dict()
                    product_dict['match_score'] = score
                    matches.append(product_dict)
        
        # Pass 3: Fuzzy text matching for missed products
        if len(matches) < max_results:
            query_words = [w for w in query_lower.split() if len(w) > 2]
            for idx, row in self.df.iterrows():
                # Skip if already matched
                if any(existing['title'] == row.get('title') for existing in matches):
                    continue
                
                title = str(row.get('title', '')).lower()
                brand = str(row.get('brand', '')).lower()
                
                # Fuzzy matching score
                fuzzy_score = 0.0
                for word in query_words:
                    if word in title or word in brand:
                        fuzzy_score += 0.2
                    # Partial matching for model names
                    for title_word in title.split():
                        if len(word) > 3 and word in title_word:
                            fuzzy_score += 0.1
                        elif len(title_word) > 3 and title_word in word:
                            fuzzy_score += 0.1
                
                if fuzzy_score > 0.2:
                    product_dict = row.to_dict()
                    product_dict['match_score'] = fuzzy_score
                    matches.append(product_dict)
        
        # Sort by match score and return top results
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches[:max_results]
    
    def _extract_brands(self, query: str) -> List[str]:
        """Extract brand names from query with enhanced detection."""
        brands = []
        for brand, patterns in self.brand_patterns.items():
            if any(pattern in query for pattern in patterns):
                brands.append(brand)
        
        # Additional fuzzy brand matching
        query_words = query.split()
        for word in query_words:
            if len(word) > 3:
                for brand in self.brand_patterns.keys():
                    if word.startswith(brand[:3]) or brand.startswith(word[:3]):
                        if brand not in brands:
                            brands.append(brand)
        
        return brands
    
    def _extract_models(self, query: str) -> List[str]:
        """Extract potential model names from query with enhanced detection."""
        models = []
        
        # Regex pattern matching
        for pattern in self.model_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                models.extend([m if isinstance(m, str) else m[0] for m in matches])
        
        # Additional word-based model matching
        query_words = query.split()
        common_models = [
            'explorair', 'montero', 'mantra', 'laser', 'blaze', 'bent', 'qst',
            'arv', 'pandora', 'chronic', 'prodigy', 'wailer', 'enforcer',
            'rustler', 'sender', 'kore', 'vision', 'reckoner', 'blacklight',
            'mothertree', 'mother', 'tree'  # Added Dynafit and Extrem models
        ]
        
        for word in query_words:
            word_clean = re.sub(r'[^\w]', '', word.lower())
            if word_clean in common_models and word_clean not in models:
                models.append(word_clean)
            # Partial matching for longer model names
            for model in common_models:
                if len(word_clean) > 4 and word_clean in model:
                    if model not in models:
                        models.append(model)
        
        return models
    
    def _extract_numbers(self, query: str) -> List[int]:
        """Extract numbers that might be model numbers or waist widths."""
        numbers = re.findall(r'\b(\d{2,3})\b', query)
        return [int(n) for n in numbers if 70 <= int(n) <= 130]  # Typical waist widths
    
    def _calculate_match_score(self, product: pd.Series, query: str, brands: List[str], models: List[str], numbers: List[int]) -> float:
        """Calculate match score for a product with enhanced scoring."""
        score = 0.0
        title = str(product.get('title', '')).lower()
        brand = str(product.get('brand', '')).lower()  # Ensure lowercase for comparison
        tags = str(product.get('tags', '')).lower()
        
        # Check for exact or near-exact title match (highest priority)
        query_lower = query.lower()
        query_core = re.sub(r'\b(which|of|the|and|is|cheapest|best|for)\b', '', query_lower).strip()
        
        # Exact title match gets maximum score
        if title == query_lower or title == query_core:
            return 10.0  # Absolute highest score for exact match
        
        # Very close title match (ignoring punctuation and extra spaces)
        title_normalized = re.sub(r'[^\w\s]', '', title).strip()
        query_normalized = re.sub(r'[^\w\s]', '', query_core).strip()
        if title_normalized == query_normalized:
            return 9.5
        
        brand_match = False
        model_match = False
        
        # Brand matching (very high weight) - case insensitive
        if brands:
            for b in brands:
                b_lower = b.lower()
                if b_lower in brand:
                    score += 0.8  # Exact brand match
                    brand_match = True
                    break
                elif b_lower in title:
                    score += 0.6  # Brand in title
                    brand_match = True
                    break
                # Fuzzy brand matching
                elif any(b_lower.startswith(word[:3]) or word.startswith(b_lower[:3]) for word in brand.split() if len(word) > 2):
                    score += 0.4
                    brand_match = True
                    break
        
        # Model matching (very high weight) - case insensitive
        if models:
            for m in models:
                m_lower = m.lower()
                if m_lower in title:
                    score += 0.8  # Exact model match
                    model_match = True
                    break
                # Fuzzy model matching
                elif any(m_lower in title_word or title_word in m_lower for title_word in title.split() if len(title_word) > 3):
                    score += 0.5
                    model_match = True
                    break
        
        # Bonus for having both brand and model matches (this is key for specificity)
        if brand_match and model_match:
            score += 0.3
        
        # Number matching (waist width, model numbers)
        if numbers:
            waist = product.get('waist_width_mm')
            if waist and not pd.isna(waist):
                for num in numbers:
                    if abs(waist - num) <= 3:  # Close match for waist width
                        score += 0.4
                        break
                    elif abs(waist - num) <= 10:  # Reasonable match
                        score += 0.2
                        break
            
            # Also check if number appears in title
            for num in numbers:
                if str(num) in title:
                    score += 0.3
                    break
        
        # Year matching (model year indicators)
        year_patterns = [r'24/25', r'25/26', r'23/24', r'2024', r'2025']
        for pattern in year_patterns:
            if pattern in query and pattern in title:
                score += 0.2
                break
        
        # Enhanced text matching (reduced weight to avoid over-scoring)
        query_words = [w for w in query.split() if len(w) > 2]
        title_words = title.split()
        
        common_words = 0
        for q_word in query_words:
            q_word_lower = q_word.lower()
            for t_word in title_words:
                if q_word_lower == t_word:  # Exact match
                    common_words += 1
                    break
                elif len(q_word_lower) > 3 and (q_word_lower in t_word or t_word in q_word_lower):  # Partial match
                    common_words += 0.5
                    break
        
        if common_words > 0:
            score += 0.1 * (common_words / len(query_words))  # Reduced weight
        
        # Tag matching with better scoring (reduced weight)
        tag_words = tags.split()
        for q_word in query_words:
            q_word_lower = q_word.lower()
            if any(q_word_lower in tag_word for tag_word in tag_words):
                score += 0.05  # Reduced weight
        
        return score  # No longer capping at 1.0 to allow exact matches to score higher

class FixedOptimizedQueryHandler:
    """Enhanced query handler with simplified classification system."""
    
    def __init__(self, data_file: str = 'alpingaraget_ai_optimized.csv'):
        self.data_file = data_file
        self.df = None
        self.matcher = None
        self.load_data()
    
    def load_data(self) -> None:
        """Load and validate data with comprehensive error handling."""
        try:
            logger.info(f"Loading data from {self.data_file}")
            
            if not os.path.exists(self.data_file):
                raise FileNotFoundError(f"Data file {self.data_file} not found")
            
            self.df = pd.read_csv(self.data_file)
            
            # Validate and clean data
            is_valid, issues = DataValidator.validate_csv_data(self.df)
            if not is_valid:
                logger.warning(f"Data quality issues found: {issues}")
            
            self.df = DataValidator.clean_product_data(self.df)
            
            # Initialize matcher
            self.matcher = EnhancedProductMatcher(self.df)
            
            logger.info(f"Successfully loaded {len(self.df)} products")
            logger.info("IMPORTANT: Default/placeholder values (like turn_radius_m=20.0) have been removed")
            
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise
    
    def handle_query(self, query: str) -> QueryResult:
        """Handle query with simplified two-level classification system."""
        start_time = time.time()
        
        try:
            logger.info(f"Processing query: {query}")
            
            # Validate input
            if not query or len(query.strip()) < 3:
                return QueryResult(
                    intent="invalid",
                    response="Query too short or empty. Please provide a more detailed question.",
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    data_sources=[],
                    error_message="Invalid query"
                )
            
            # Step 1: Classify as search vs property
            is_search = self._is_search_query(query)
            
            if is_search:
                result = self._handle_search_query(query)
            else:
                # Step 2: For property queries, classify as property:property vs property:general
                property_type = self._classify_property_type(query)
                result = self._handle_property_query(query, property_type)
            
            result.processing_time = time.time() - start_time
            logger.info(f"Query processed successfully in {result.processing_time:.3f}s")
            
            # Add LLM interpretation
            result.response = self._interpret_technical_response(result.response, query, result.intent, result.matched_products)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query '{query}': {e}")
            return QueryResult(
                intent="error",
                response="I apologize, but I encountered an error while processing your query. Please try rephrasing your question.",
                confidence=0.0,
                processing_time=time.time() - start_time,
                data_sources=[],
                error_message=str(e)
            )
    
    def _is_search_query(self, query: str) -> bool:
        """Determine if this is a search query (first level classification)."""
        query_lower = query.lower()
        
        # Strong search indicators
        search_patterns = [
            r'\b(show|find|search|list|recommend|suggest)\s+me\b',
            r'\bi\s+(want|need|am\s+looking\s+for)\b.*\bunder\b',  # Budget searches
            r'\bdo\s+you\s+have.*\b(wider|cheaper|lighter)\b',  # Comparative searches
            r'\bshow\s+me.*\b(all|skis|options)\b',  # Show me all X
            r'\bwhat.*\b(options|choices|skis)\b.*\bhave\b',  # What options do you have
            r'\bwhich.*\b(cheapest|most\s+expensive|best\s+value|lightest|heaviest)\b.*ski',  # Superlative searches
            r'\blist.*\b(all|skis|options)\b',  # List all X
            r'\bgive\s+me.*\b(options|choices|list)\b'  # Give me options
        ]
        
        # Check for search patterns
        has_search_pattern = any(re.search(pattern, query_lower) for pattern in search_patterns)
        
        # Count specific product mentions
        brand_indicators = [
            'atomic', 'salomon', 'rossignol', 'k2', 'armada', 'völkl', 'volkl',
            'line', 'faction', 'dynafit', 'dps', 'nordica', 'stöckli', 'stockli',
            'fischer', 'head', 'blizzard', 'scott', 'extrem'
        ]
        
        model_indicators = [
            'bent', 'qst', 'arv', 'pandora', 'chronic', 'prodigy', 'blaze',
            'mantra', 'laser', 'wailer', 'santa ana', 'enforcer', 'rustler',
            'maverick', 'declivity', 'tracer', 'invictus', 'vision', 'reckoner',
            'kore', 'sender', 'explorair', 'montero', 'blacklight', 'mother tree'
        ]
        
        brand_count = sum(1 for brand in brand_indicators if brand in query_lower)
        model_count = sum(1 for model in model_indicators if model in query_lower)
        specific_products = brand_count + model_count
        
        # Search if: has search patterns OR very few specific products mentioned
        return has_search_pattern or specific_products == 0
    
    def _classify_property_type(self, query: str) -> str:
        """Classify property queries as property:property or property:general."""
        query_lower = query.lower()
        
        # Specific property indicators (property:property)
        specific_property_patterns = [
            r'\bwhat.*\b(waist width|price|cost|specs|length|weight|listed price)\b',
            r'\bhow much.*\b(cost|price|does.*cost)\b',
            r'\bwhat.*\b(is\s+the|are\s+the).*\b(price|waist|width|specs|dimensions)\b',
            r'\bprice.*\b(of|for)\b',  # Price of/for X
            r'\bcost.*\b(of|for)\b',   # Cost of/for X
            r'\bwaist.*width\b',       # Waist width queries
            r'\bhow\s+(wide|heavy|long)\b',  # How wide/heavy/long
            r'\bspecifications\b',     # Specifications
            r'\bdimensions\b',         # Dimensions
            r'\bweight.*\b(of|for)\b'  # Weight of/for X
        ]
        
        has_specific_property = any(re.search(pattern, query_lower) for pattern in specific_property_patterns)
        
        if has_specific_property:
            return "property:property"
        else:
            return "property:general"
    
    def _handle_property_query(self, query: str, property_type: str) -> QueryResult:
        """Handle property queries based on their type."""
        # Find relevant products first
        products = self._find_relevant_products(query)
        
        if not products:
            return QueryResult(
                intent=property_type,
                response="I couldn't find the specific products mentioned in your question. Please check the spelling or try different keywords.",
                confidence=0.3,
                processing_time=0,
                data_sources=["product_database"],
                matched_products=[]
            )
        
        if property_type == "property:property":
            return self._handle_specific_property_query(query, products)
        else:  # property:general
            return self._handle_general_property_query(query, products)
    
    def _find_relevant_products(self, query: str) -> List[Dict]:
        """Find products relevant to the query using enhanced matching."""
        query_lower = query.lower()
        
        # Check if this looks like a comparison (multiple products)
        comparison_indicators = [
            r'\b(compare|versus|vs|between\s+.+\s+and)\b',
            r'\bwhich\s+(is|has|ski|one)\s+.*(wider|better|cheaper|expensive|lighter)',
            r'\bwhich\s+of\s+the\s+.+\s+and\s+.+\s+(is|has)\s+',
            r'\bwhich\s+of\s+.+\s+and\s+.+\s+(cheapest|best|better|wider)'
        ]
        
        is_comparison = any(re.search(pattern, query_lower) for pattern in comparison_indicators)
        
        if is_comparison:
            # Try to find multiple specific products
            products = self._find_multiple_products_for_comparison(query)
            if len(products) >= 2:
                return products[:2]  # Return top 2 for comparison
        
        # Single product or general search
        products = self.matcher.find_products(query, max_results=5)
        return products
    
    def _find_multiple_products_for_comparison(self, query: str) -> List[Dict]:
        """Enhanced product detection for comparison queries."""
        query_lower = query.lower()
        found_products = []
        
        # First try to extract specific product names using pattern matching
        # Pattern: "Brand Model Number Year" combinations
        product_pattern = r'((?:dynafit|extrem|atomic|salomon|rossignol|k2|armada|völkl|volkl|line|faction|dps|nordica|stöckli|stockli|fischer|head|blizzard|scott)[^,]*?(?:24/25|25/26|23/24))'
        product_matches = re.findall(product_pattern, query_lower, re.IGNORECASE)
        
        # Search for each extracted product name
        for product_name in product_matches:
            product_name = product_name.strip()
            matches = self.matcher.find_products(product_name, max_results=10)
            if matches:
                # Find the best match with highest score
                best_match = max(matches, key=lambda x: x['match_score'])
                if not any(p['title'] == best_match['title'] for p in found_products):
                    found_products.append(best_match)
        
        # If we found exactly 2 products, return them
        if len(found_products) == 2:
            return found_products
        
        # Otherwise, continue with the original logic
        # Split query on common separators for comparison
        separators = [' and ', ' vs ', ' versus ', ' or ', ' between ']
        parts = [query_lower]
        
        for sep in separators:
            if sep in query_lower:
                parts = query_lower.split(sep)
                break
        
        # If we found separators, search each part individually
        if len(parts) > 1:
            for part in parts:
                part = part.strip()
                if len(part) > 5:  # Skip very short parts
                    matches = self.matcher.find_products(part, max_results=3)
                    if matches:
                        best_match = matches[0]
                        if not any(p['title'] == best_match['title'] for p in found_products):
                            found_products.append(best_match)
        
        # Fallback: Use regular search and take top products
        if len(found_products) < 2:
            matches = self.matcher.find_products(query, max_results=10)
            for match in matches:
                if not any(p['title'] == match['title'] for p in found_products):
                    found_products.append(match)
                if len(found_products) >= 2:
                    break
        
        return found_products
    
    def _handle_specific_property_query(self, query: str, products: List[Dict]) -> QueryResult:
        """Handle specific property questions (price, waist width, etc.) using LLM."""
        product = products[0]  # Use the best match
        
        # Generate LLM prompt with full product data
        prompt = LLMPromptGenerator.generate_property_property_prompt(query, product)
        
        # Try LLM first
        llm_response = LLMCaller.call_openai(prompt)
        
        if llm_response:
            logger.info("Using LLM response for property:property query")
            return QueryResult(
                intent="property:property",
                response=llm_response,
                confidence=0.9,
                processing_time=0,
                data_sources=["product_database", "llm"],
                matched_products=[product]
            )
        else:
            # Fallback to rule-based response
            logger.warning("LLM failed, using rule-based fallback for property:property query")
            response = self._generate_rule_based_property_response(product, query)
            return QueryResult(
                intent="property:property",
                response=response,
                confidence=0.7,
                processing_time=0,
                data_sources=["product_database"],
                matched_products=[product]
            )
    
    def _handle_general_property_query(self, query: str, products: List[Dict]) -> QueryResult:
        """Handle general property questions (comparisons, suitability, etc.) using LLM."""
        
        # Generate LLM prompt with full product data
        prompt = LLMPromptGenerator.generate_property_general_prompt(query, products)
        
        # Try LLM first
        llm_response = LLMCaller.call_openai(prompt, max_tokens=400)  # More tokens for comparisons
        
        if llm_response:
            logger.info("Using LLM response for property:general query")
            return QueryResult(
                intent="property:general",
                response=llm_response,
                confidence=0.9,
                processing_time=0,
                data_sources=["product_database", "llm"],
                matched_products=products
            )
        else:
            # Fallback to rule-based response
            logger.warning("LLM failed, using rule-based fallback for property:general query")
            if len(products) >= 2:
                response = self._generate_rule_based_comparison_response(products[:2], query)
            else:
                response = self._generate_rule_based_general_response(products[0], query)
            
            return QueryResult(
                intent="property:general",
                response=response,
                confidence=0.7,
                processing_time=0,
                data_sources=["product_database"],
                matched_products=products
            )
    
    def _get_price_response(self, product: Dict, query: str) -> str:
        """Generate price-specific response."""
        title = product.get('title', 'This ski')
        price = product.get('price')
        discounted_price = product.get('discounted_price')
        
        if discounted_price and discounted_price != price:
            return f"The {title} usually costs {price} SEK but is currently available at a discount for {discounted_price} SEK."
        elif price:
            return f"The {title} costs {price} SEK."
        else:
            return f"I don't have pricing information available for the {title}."
    
    def _get_waist_width_response(self, product: Dict, query: str) -> str:
        """Generate waist width-specific response."""
        title = product.get('title', 'This ski')
        waist_width = product.get('waist_width_mm')
        
        if waist_width:
            return f"The {title} has a waist width of {waist_width}mm."
        else:
            return f"I don't have waist width information available for the {title}."
    
    def _get_weight_response(self, product: Dict, query: str) -> str:
        """Generate weight-specific response."""
        title = product.get('title', 'This ski')
        weight = product.get('weight_grams')
        
        if weight and not pd.isna(weight):
            return f"The {title} weighs {weight}g."
        else:
            return f"I don't have weight information available for the {title}."
    
    def _get_length_response(self, product: Dict, query: str) -> str:
        """Generate length-specific response."""
        title = product.get('title', 'This ski')
        lengths = product.get('parsed_lengths', [])
        
        if lengths:
            length_str = ', '.join(map(str, lengths)) + 'cm'
            return f"The {title} is available in the following lengths: {length_str}."
        else:
            return f"I don't have length information available for the {title}."
    
    def _get_general_specs_response(self, product: Dict, query: str) -> str:
        """Generate general specifications response."""
        title = product.get('title', 'This ski')
        specs = []
        
        if product.get('waist_width_mm'):
            specs.append(f"waist width: {product['waist_width_mm']}mm")
        if product.get('price'):
            specs.append(f"price: {product['price']} SEK")
        if product.get('weight_grams') and not pd.isna(product['weight_grams']):
            specs.append(f"weight: {product['weight_grams']}g")
        
        if specs:
            return f"Here are the specifications for the {title}: {', '.join(specs)}."
        else:
            return f"I have limited specification data available for the {title}."
    
    def _generate_comparison_response(self, products: List[Dict], query: str) -> str:
        """Generate comparison response between products."""
        if len(products) < 2:
            return "I need at least two products to make a comparison."
        
        prod1, prod2 = products[0], products[1]
        query_lower = query.lower()
        
        # Check what type of comparison is being asked
        if any(word in query_lower for word in ['cheaper', 'cheapest', 'price', 'cost']):
            return self._compare_prices(prod1, prod2, query)
        elif any(word in query_lower for word in ['wider', 'waist', 'width']):
            return self._compare_waist_widths(prod1, prod2, query)
        elif any(word in query_lower for word in ['off piste', 'offpiste', 'powder', 'deep snow']):
            return self._compare_off_piste_performance(prod1, prod2, query)
        elif any(word in query_lower for word in ['icy', 'hard', 'groomed', 'edge', 'grip']):
            return self._compare_on_piste_performance(prod1, prod2, query)
        else:
            return self._compare_general(prod1, prod2, query)
    
    def _compare_prices(self, prod1: Dict, prod2: Dict, query: str) -> str:
        """Compare prices between two products."""
        # Get current prices (discounted if available, otherwise regular price)
        price1 = prod1.get('reapris') if prod1.get('reapris') else prod1.get('price')
        price2 = prod2.get('reapris') if prod2.get('reapris') else prod2.get('price')
        
        # Get original prices for context
        orig_price1 = prod1.get('price')
        orig_price2 = prod2.get('price')
        
        if not price1 or not price2:
            return f"I don't have complete pricing information for both products."
        
        if price1 < price2:
            cheaper = prod1['title']
            cheaper_price = price1
            other_price = price2
            cheaper_orig = orig_price1
            other_orig = orig_price2
        else:
            cheaper = prod2['title']
            cheaper_price = price2
            other_price = price1
            cheaper_orig = orig_price2
            other_orig = orig_price1
        
        # Build response with discount information
        response = f"The {cheaper} is cheaper at {int(cheaper_price)} SEK"
        
        # Add discount info if applicable
        if cheaper_orig and cheaper_orig != cheaper_price:
            response += f" (discounted from {int(cheaper_orig)} SEK)"
        
        response += f" compared to {int(other_price)} SEK"
        
        # Add discount info for the more expensive one if applicable
        if other_orig and other_orig != other_price:
            response += f" (discounted from {int(other_orig)} SEK)"
        
        response += "."
        
        return response
    
    def _compare_waist_widths(self, prod1: Dict, prod2: Dict, query: str) -> str:
        """Compare waist widths between two products."""
        waist1 = prod1.get('waist_width_mm')
        waist2 = prod2.get('waist_width_mm')
        
        if not waist1 or not waist2:
            return f"I don't have complete waist width information for both products."
        
        if waist1 > waist2:
            wider = prod1['title']
            wider_waist = waist1
            narrower_waist = waist2
        else:
            wider = prod2['title']
            wider_waist = waist2
            narrower_waist = waist1
        
        return f"The {wider} is wider with {wider_waist}mm waist compared to {narrower_waist}mm."
    
    def _compare_off_piste_performance(self, prod1: Dict, prod2: Dict, query: str) -> str:
        """Compare off-piste performance based on waist width and design."""
        waist1 = prod1.get('waist_width_mm', 0)
        waist2 = prod2.get('waist_width_mm', 0)
        
        if waist1 > waist2:
            better_powder = prod1['title']
            better_waist = waist1
            other_waist = waist2
        else:
            better_powder = prod2['title']
            better_waist = waist2
            other_waist = waist1
        
        return f"For off-piste skiing, the {better_powder} would be better with its {better_waist}mm waist providing more flotation in powder compared to the {other_waist}mm waist of the other ski."
    
    def _compare_on_piste_performance(self, prod1: Dict, prod2: Dict, query: str) -> str:
        """Compare on-piste performance based on waist width."""
        waist1 = prod1.get('waist_width_mm', 0)
        waist2 = prod2.get('waist_width_mm', 0)
        
        if waist1 < waist2:
            better_piste = prod1['title']
            better_waist = waist1
            other_waist = waist2
        else:
            better_piste = prod2['title']
            better_waist = waist2
            other_waist = waist1
        
        return f"For icy and hard-packed conditions, the {better_piste} would hold an edge more securely with its {better_waist}mm waist compared to the {other_waist}mm waist."
    
    def _compare_general(self, prod1: Dict, prod2: Dict, query: str) -> str:
        """General comparison between two products."""
        title1 = prod1.get('title', 'First ski')
        title2 = prod2.get('title', 'Second ski')
        
        comparison_points = []
        
        # Compare waist widths
        waist1 = prod1.get('waist_width_mm')
        waist2 = prod2.get('waist_width_mm')
        if waist1 and waist2:
            comparison_points.append(f"waist width: {title1} ({waist1}mm) vs {title2} ({waist2}mm)")
        
        # Compare prices
        price1 = prod1.get('discounted_price') or prod1.get('price')
        price2 = prod2.get('discounted_price') or prod2.get('price')
        if price1 and price2:
            comparison_points.append(f"price: {title1} ({price1} SEK) vs {title2} ({price2} SEK)")
        
        if comparison_points:
            return f"Comparing the {title1} and {title2}: {'; '.join(comparison_points)}."
        else:
            return f"I have limited data to compare the {title1} and {title2}."
    
    def _generate_general_response(self, product: Dict, query: str) -> str:
        """Generate general response about a single product."""
        title = product.get('title', 'This ski')
        query_lower = query.lower()
        
        # Check what kind of question is being asked
        if any(word in query_lower for word in ['beginner', 'intermediate', 'advanced']):
            return self._assess_skill_level_suitability(product, query)
        elif any(word in query_lower for word in ['good for', 'suitable', 'work for']):
            return self._assess_general_suitability(product, query)
        else:
            return f"The {title} is a quality ski. For specific recommendations, please ask about particular skiing conditions or your skill level."
    
    def _assess_skill_level_suitability(self, product: Dict, query: str) -> str:
        """Assess if a ski is suitable for a skill level."""
        title = product.get('title', 'This ski')
        waist_width = product.get('waist_width_mm', 0)
        
        if 'beginner' in query.lower():
            if 70 <= waist_width <= 90:
                return f"The {title} with its {waist_width}mm waist would be suitable for beginners as it offers good stability and is easy to turn."
            else:
                return f"The {title} with its {waist_width}mm waist might be challenging for beginners. Consider a ski with 70-90mm waist width for better learning."
        elif 'intermediate' in query.lower():
            return f"The {title} would be suitable for intermediate skiers looking to develop their skills across different conditions."
        else:  # advanced
            return f"The {title} is suitable for advanced skiers who can handle its performance characteristics."
    
    def _assess_general_suitability(self, product: Dict, query: str) -> str:
        """Assess general suitability for conditions or purposes."""
        title = product.get('title', 'This ski')
        waist_width = product.get('waist_width_mm', 0)
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['powder', 'deep', 'off piste']):
            if waist_width >= 100:
                return f"The {title} with its {waist_width}mm waist is excellent for powder and off-piste skiing, providing good flotation."
            else:
                return f"The {title} with its {waist_width}mm waist is more suited for groomed runs than deep powder."
        elif any(word in query_lower for word in ['groomed', 'piste', 'carving']):
            if waist_width <= 85:
                return f"The {title} with its {waist_width}mm waist is well-suited for groomed pistes and carving."
            else:
                return f"The {title} with its {waist_width}mm waist is more oriented towards off-piste than groomed carving."
        else:
            return f"The {title} is a versatile ski suitable for various skiing conditions."

    def _interpret_technical_response(self, technical_response: str, original_query: str = "", intent: str = "", matched_products: List[Dict] = None) -> str:
        """
        Interpret the technical response and transform it into everyday speech that answers the skiing question.
        This simulates an LLM interpretation step to provide useful, contextual answers.
        """
        if not matched_products:
            matched_products = []
        
        query_lower = original_query.lower()
        
        # Analyze the skiing context from the query
        skiing_contexts = {
            'off_piste': ['off-piste', 'off piste', 'steep', 'technical lines', 'backcountry'],
            'powder': ['powder', 'deep snow', 'float'],
            'carving': ['carving', 'icy', 'groomers', 'groomed', 'hard pack', 'edge'],
            'park': ['park', 'freestyle', 'pop', 'flex', 'jumps', 'rails'],
            'touring': ['touring', 'skinning', 'uphill', 'backcountry touring'],
            'beginner': ['beginner', 'progression', 'forgiving', 'easy'],
            'all_mountain': ['all-mountain', 'versatile', 'mixed conditions', 'versatility'],
            'slalom': ['slalom', 'tight turns', 'responsive', 'quick'],
            'edge_hold': ['edge hold', 'icy slopes', 'hard snow', 'secure']
        }
        
        detected_contexts = []
        for context, keywords in skiing_contexts.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_contexts.append(context)
        
        # Generate contextual response based on skiing expertise
        if intent == "compare" and len(matched_products) >= 2:
            return self._generate_comparison_interpretation(original_query, matched_products, detected_contexts)
        elif intent == "describe" and matched_products:
            return self._generate_description_interpretation(original_query, matched_products[0], detected_contexts)
        else:
            # For other cases, enhance the existing response with skiing context
            return self._enhance_technical_response(technical_response, detected_contexts, original_query)
    
    def _generate_comparison_interpretation(self, query: str, products: List[Dict], contexts: List[str]) -> str:
        """Generate skiing-focused comparison response."""
        p1, p2 = products[0], products[1]
        
        # Extract key specs
        waist1 = p1.get('waist_width_mm', 0)
        waist2 = p2.get('waist_width_mm', 0)
        price1 = p1.get('price', 0)
        price2 = p2.get('price', 0)
        
        responses = []
        query_lower = query.lower()
        
        # Handle specific comparison questions first
        if any(keyword in query_lower for keyword in ['cheapest', 'cheaper', 'price', 'cost']):
            # Price-focused comparison
            if price1 and price2 and not pd.isna(price1) and not pd.isna(price2):
                cheaper = p1 if price1 < price2 else p2
                expensive = p2 if price1 < price2 else p1
                price_diff = abs(price1 - price2)
                responses.append(f"The {cheaper['title']} at {int(cheaper['price'])} SEK is cheaper than the {expensive['title']} at {int(expensive['price'])} SEK by {int(price_diff)} SEK.")
            else:
                responses.append(f"Price comparison isn't possible as pricing information is incomplete in our database.")
            return " ".join(responses)
        
        # Context-specific recommendations
        if 'powder' in contexts or 'off_piste' in contexts:
            if waist1 and waist2:
                wider_ski = p1 if waist1 > waist2 else p2
                narrower_ski = p2 if waist1 > waist2 else p1
                
                if abs(waist1 - waist2) > 5:  # Significant difference
                    responses.append(f"For off-piste and powder skiing, the {wider_ski['title']} ({wider_ski.get('waist_width_mm')}mm) will perform significantly better than the {narrower_ski['title']} ({narrower_ski.get('waist_width_mm')}mm). The wider waist provides better flotation and stability in deep snow.")
                else:
                    responses.append(f"Both skis have similar waist widths - the {p1['title']} ({waist1}mm) and {p2['title']} ({waist2}mm) should perform comparably in off-piste conditions.")
        
        elif 'carving' in contexts or 'edge_hold' in contexts or 'icy' in contexts:
            if waist1 and waist2:
                narrower_ski = p1 if waist1 < waist2 else p2
                wider_ski = p2 if waist1 < waist2 else p1
                responses.append(f"For carving and edge hold on icy pistes, the {narrower_ski['title']} ({narrower_ski.get('waist_width_mm')}mm) will be more responsive than the {wider_ski['title']} ({wider_ski.get('waist_width_mm')}mm). Narrower skis transfer edge pressure more effectively on hard snow.")
        
        elif 'all_mountain' in contexts or 'versatile' in query_lower:
            if waist1 and waist2:
                responses.append(f"For all-mountain versatility, both skis are in good ranges. The {p1['title']} ({waist1}mm) vs {p2['title']} ({waist2}mm) will both handle mixed conditions, with slight differences in performance based on snow type.")
        
        # Handle "which is best" questions specifically
        elif any(keyword in query_lower for keyword in ['which is best', 'which is better', 'which one', 'best for']):
            if waist1 and waist2:
                # Determine recommendation based on waist width difference and context
                if abs(waist1 - waist2) > 10:  # Significant difference
                    wider_ski = p1 if waist1 > waist2 else p2
                    narrower_ski = p2 if waist1 > waist2 else p1
                    responses.append(f"The {wider_ski['title']} ({wider_ski.get('waist_width_mm')}mm) is better for powder and varied snow conditions, while the {narrower_ski['title']} ({narrower_ski.get('waist_width_mm')}mm) excels on groomed runs and harder snow.")
                else:
                    responses.append(f"The {p1['title']} ({waist1}mm) and {p2['title']} ({waist2}mm) are quite similar in width. Both would perform comparably in most conditions.")
        
        # Price consideration (secondary information)
        if price1 and price2 and not any(keyword in query_lower for keyword in ['cheapest', 'price', 'cost']):
            price_diff = abs(price1 - price2)
            if price_diff > 1500:  # Significant price difference
                cheaper = p1 if price1 < price2 else p2
                expensive = p2 if price1 < price2 else p1
                responses.append(f"Price-wise, the {cheaper['title']} at {int(cheaper['price'])} SEK is more budget-friendly than the {expensive['title']} at {int(expensive['price'])} SEK.")
        
        # Default if no specific context was handled
        if not responses:
            responses.append(f"Between the {p1['title']} and {p2['title']}, both are quality skis. The choice depends on your specific skiing preferences and conditions.")
        
        return " ".join(responses)
    
    def _generate_description_interpretation(self, query: str, product: Dict, contexts: List[str]) -> str:
        """Generate skiing-focused description response."""
        title = product.get('title', 'this ski')
        waist = product.get('waist_width_mm')
        price = product.get('price')
        discounted_price = product.get('reapris')  # Swedish for "sale price"
        
        query_lower = query.lower()
        responses = []
        
        # Check for direct factual queries first (these don't need skiing context)
        if any(keyword in query_lower for keyword in ['price', 'cost', 'listed price', 'how much']):
            if discounted_price and not pd.isna(discounted_price) and price and not pd.isna(price) and discounted_price < price:
                # Show both original and discounted price
                responses.append(f"The {title} usually costs {int(price)} SEK but right now it is at a discount and available for {int(discounted_price)} SEK.")
            elif price and not pd.isna(price):
                responses.append(f"The {title} is priced at {int(price)} SEK.")
            else:
                responses.append(f"The price for the {title} is not available in our database.")
                
        elif any(keyword in query_lower for keyword in ['waist width', 'wide', 'width', 'waist']):
            if waist and not pd.isna(waist):
                responses.append(f"The {title} has a waist width of {waist}mm.")
            else:
                responses.append(f"The waist width for the {title} is not specified in our database.")
                
        elif any(keyword in query_lower for keyword in ['weight', 'heavy', 'light']):
            weight = product.get('weight_grams')
            if weight and not pd.isna(weight) and DataValidator.is_real_data(weight, 'weight_grams'):
                responses.append(f"The {title} weighs {weight}g.")
            else:
                responses.append(f"The weight for the {title} is not available in our database.")
                
        elif any(keyword in query_lower for keyword in ['twin', 'twintip', 'twin-tip']):
            twin_tip = product.get('twin_tip', False)
            if pd.notna(twin_tip):
                responses.append(f"{'Yes' if twin_tip else 'No'}, the {title} {'is' if twin_tip else 'is not'} a twin-tip ski.")
            else:
                responses.append(f"The twin-tip design for the {title} is not available in our database.")
                
        elif any(keyword in query_lower for keyword in ['length', 'lengths', 'available']):
            lengths = product.get('parsed_lengths', [])
            if lengths:
                lengths_str = ', '.join(map(str, lengths))
                responses.append(f"The {title} is available in these lengths: {lengths_str}cm.")
            else:
                responses.append(f"The available lengths for the {title} are not specified in our database.")
                
        # Handle fit questions specifically
        elif any(keyword in query_lower for keyword in ['fit', 'suit', 'height', 'tall', 'cm']):
            lengths = product.get('parsed_lengths', [])
            # Extract height from query if mentioned
            height_match = re.search(r'(\d+)\s*cm', query_lower)
            if height_match and lengths:
                height = int(height_match.group(1))
                suitable_lengths = [l for l in lengths if height - 15 <= l <= height + 10]
                if suitable_lengths:
                    suitable_str = ', '.join(map(str, suitable_lengths))
                    responses.append(f"For someone who is {height}cm tall, the {title} would work well in these lengths: {suitable_str}cm. The {title} is available in: {', '.join(map(str, lengths))}cm.")
                else:
                    responses.append(f"For someone who is {height}cm tall, the {title} might not be ideal. Available lengths are: {', '.join(map(str, lengths))}cm.")
            elif lengths:
                responses.append(f"The {title} is available in these lengths: {', '.join(map(str, lengths))}cm. For proper fit, choose a length close to your height.")
            else:
                responses.append(f"The available lengths for the {title} are not specified in our database.")
        
        # If no direct factual query was matched, proceed with skiing context analysis
        if not responses:
            # Context-specific analysis for performance questions
            if 'off_piste' in contexts:
                if waist:
                    if waist >= 100:
                        responses.append(f"The {title} with its {waist}mm waist width is excellent for steep, technical off-piste lines. The wider platform gives you stability and control in variable snow conditions.")
                    elif waist >= 90:
                        responses.append(f"The {title} ({waist}mm) can handle off-piste terrain reasonably well, though it's more suited to lighter powder than deep, heavy snow.")
                    else:
                        responses.append(f"The {title} at {waist}mm is quite narrow for serious off-piste skiing. It would struggle in deeper snow and variable conditions.")
            
            elif 'carving' in contexts:
                if waist:
                    if waist <= 75:
                        responses.append(f"The {title} with its {waist}mm waist is built for high-speed carving. The narrow width allows for quick edge-to-edge transitions and precise control on icy groomers.")
                    elif waist <= 85:
                        responses.append(f"The {title} ({waist}mm) is decent for carving, though not as aggressive as dedicated carving skis. It'll handle groomed runs well but might feel less precise at very high speeds.")
                    else:
                        responses.append(f"The {title} at {waist}mm is too wide for optimal carving performance. It's designed more for all-mountain or powder skiing than precise groomer turns.")
            
            elif 'park' in contexts:
                # Check if it's a twin-tip
                twin_tip = product.get('twin_tip', False)
                if twin_tip:
                    responses.append(f"The {title} should work well for park skiing - it has a twin-tip design which is essential for landing backwards and doing switch tricks.")
                else:
                    responses.append(f"The {title} isn't ideal for serious park skiing. Most park skis have twin-tip designs for versatility in jumps and rails.")
            
            elif 'beginner' in contexts:
                if waist and 70 <= waist <= 85:
                    responses.append(f"The {title} could work for a progression-focused beginner. The {waist}mm waist width is in the forgiving all-mountain range that's not too demanding.")
                elif waist and waist > 90:
                    responses.append(f"The {title} might be challenging for a beginner. At {waist}mm, it's quite wide and could feel unstable when learning basic turns on groomed runs.")
                else:
                    responses.append(f"Without knowing the exact specifications, it's hard to assess if the {title} is beginner-friendly. Look for skis in the 70-85mm waist range for learning.")
            
            elif 'touring' in contexts:
                weight = product.get('weight_grams')
                if weight and DataValidator.is_real_data(weight, 'weight_grams'):
                    if weight < 1500:
                        responses.append(f"The {title} at {weight}g would be excellent for long touring days. That's a lightweight ski that won't tire you out on long ascents.")
                    elif weight < 2000:
                        responses.append(f"The {title} ({weight}g) is reasonable for touring, though not the lightest option. You'll notice the weight on very long days, but it should ski well on the descent.")
                    else:
                        responses.append(f"At {weight}g, the {title} is quite heavy for touring. Better suited for resort skiing than long backcountry days.")
                else:
                    responses.append(f"Without weight specifications available, it's hard to assess the {title} for touring. Lighter skis (under 1500g) are generally better for long uphill days.")
            
            # Handle powder/deep snow questions without "Yes," 
            elif 'powder' in contexts or 'deep snow' in contexts:
                if waist:
                    if waist >= 100:
                        responses.append(f"The {title} with its {waist}mm waist width is excellent for deep snow. The wide platform provides great flotation and stability in powder.")
                    elif waist >= 90:
                        responses.append(f"The {title} ({waist}mm) can handle powder reasonably well, though it's more suited to lighter powder than very deep snow.")
                    else:
                        responses.append(f"The {title} at {waist}mm is quite narrow for powder skiing. It would struggle to stay on top of deep snow.")
                else:
                    responses.append(f"Without waist width specifications, it's hard to assess the {title} for powder skiing.")
            
            # For general product queries without specific skiing context
            elif any(keyword in query_lower for keyword in ['spec', 'about', 'tell me', 'details', 'information']):
                spec_parts = []
                if waist and not pd.isna(waist):
                    spec_parts.append(f"waist width of {waist}mm")
                if price and not pd.isna(price):
                    spec_parts.append(f"priced at {int(price)} SEK")
                    
                if spec_parts:
                    responses.append(f"The {title} has a {' and is '.join(spec_parts)}.")
                    
                    # Add skiing category assessment based on waist width
                    if waist:
                        if waist < 80:
                            responses.append("This is a narrow, carving-oriented ski best suited for groomed runs.")
                        elif waist < 95:
                            responses.append("This is a versatile all-mountain ski suitable for mixed conditions.")
                        elif waist < 110:
                            responses.append("This is a wider all-mountain/powder ski designed for off-piste and deeper snow.")
                        else:
                            responses.append("This is a dedicated powder ski built for deep snow flotation.")
                else:
                    responses.append(f"The {title} is available in our database, but detailed specifications are limited.")
        
        # Only use the generic fallback if absolutely nothing else worked
        if not responses:
            responses.append(f"The {title} is available in our database. For specific performance advice, I'd need more details about your skiing style and preferred terrain.")
        
        return " ".join(responses)
    
    def _enhance_technical_response(self, technical_response: str, contexts: List[str], query: str) -> str:
        """Enhance existing technical response with skiing context."""
        if not contexts:
            return technical_response
        
        enhancements = []
        
        if 'powder' in contexts:
            enhancements.append("For powder skiing, look for skis with waist widths over 100mm for the best float.")
        elif 'carving' in contexts:
            enhancements.append("For carving, narrower skis (under 80mm) with good edge hold perform best on groomed runs.")
        elif 'touring' in contexts:
            enhancements.append("For touring, prioritize lightweight skis (under 1500g) to reduce fatigue on long ascents.")
        
        if enhancements:
            return technical_response + "\n\n" + " ".join(enhancements)
        
        return technical_response

    def _handle_search_query(self, query: str) -> QueryResult:
        """Handle search queries for finding products based on criteria."""
        products = self.matcher.find_products(query, max_results=10)
        
        if not products:
            return QueryResult(
                intent="search",
                response="I couldn't find any products matching your search criteria. Please try different keywords or be more specific.",
                confidence=0.2,
                processing_time=0,
                data_sources=["product_database"],
                matched_products=[]
            )
        
        # Generate search results response
        response_parts = ["Here are the products I found matching your search:\n"]
        
        for i, product in enumerate(products[:5], 1):  # Show top 5 results
            title = product.get('title', 'Unknown')
            
            # Handle price with NaN checking
            price = product.get('reapris') if product.get('reapris') and not pd.isna(product.get('reapris')) else None
            if not price:
                price = product.get('price') if product.get('price') and not pd.isna(product.get('price')) else None
            
            # Handle waist width with NaN checking
            waist = product.get('waist_width_mm')
            if waist and not pd.isna(waist):
                waist = f"{waist}mm"
            else:
                waist = 'N/A'
            
            response_parts.append(f"{i}. {title}")
            if price:
                response_parts.append(f"   Price: {int(price)} SEK | Waist: {waist}")
            else:
                response_parts.append(f"   Waist: {waist}")
        
        return QueryResult(
            intent="search",
            response="\n".join(response_parts),
            confidence=0.8,
            processing_time=0,
            data_sources=["product_database"],
            matched_products=products
        )

    def _generate_rule_based_property_response(self, product: Dict, query: str) -> str:
        """Fallback rule-based response for specific property questions."""
        query_lower = query.lower()
        title = product.get('title', 'This ski')
        
        # Determine what property is being asked about
        if any(word in query_lower for word in ['price', 'cost', 'much']):
            return self._get_price_response(product, query)
        elif any(word in query_lower for word in ['waist', 'width']):
            return self._get_waist_width_response(product, query)
        elif any(word in query_lower for word in ['weight']):
            return self._get_weight_response(product, query)
        elif any(word in query_lower for word in ['length', 'sizes']):
            return self._get_length_response(product, query)
        else:
            # General specs
            return self._get_general_specs_response(product, query)
    
    def _generate_rule_based_comparison_response(self, products: List[Dict], query: str) -> str:
        """Fallback rule-based response for comparison questions."""
        return self._generate_comparison_response(products, query)
    
    def _generate_rule_based_general_response(self, product: Dict, query: str) -> str:
        """Fallback rule-based response for general single product questions."""
        return self._generate_general_response(product, query)

    def handle_query_with_ski_list(self, query: str, ski_list: List[str]) -> QueryResult:
        """Handle query with a provided list of skis the user has looked at."""
        start_time = time.time()
        
        try:
            logger.info(f"Processing query with ski list: {query}")
            logger.info(f"Ski list: {ski_list}")
            
            # Validate input
            if not query or len(query.strip()) < 3:
                return QueryResult(
                    intent="invalid",
                    response="Query too short or empty. Please provide a more detailed question.",
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    data_sources=[],
                    error_message="Invalid query"
                )
            
            # If no skis provided, fall back to original method
            if not ski_list:
                return self.handle_query(query)
            
            # Step 1: Find products matching the provided ski list
            matched_products = self._find_products_from_ski_list(ski_list)
            
            if not matched_products:
                return QueryResult(
                    intent="property:property",
                    response="I couldn't find any of the skis you mentioned in our database. Please check the spelling or try different ski names.",
                    confidence=0.3,
                    processing_time=time.time() - start_time,
                    data_sources=["product_database"],
                    matched_products=[]
                )
            
            # Step 2: Classify the query type (since we have products, it's a property query)
            property_type = self._classify_property_type_for_ski_list(query, matched_products)
            
            # Step 3: Generate response using LLM with the matched products
            if property_type == "property:property":
                result = self._handle_specific_property_query_with_ski_list(query, matched_products)
            else:  # property:general
                result = self._handle_general_property_query_with_ski_list(query, matched_products)
            
            result.processing_time = time.time() - start_time
            logger.info(f"Query processed successfully in {result.processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query '{query}' with ski list: {e}")
            return QueryResult(
                intent="error",
                response="I apologize, but I encountered an error while processing your query. Please try rephrasing your question.",
                confidence=0.0,
                processing_time=time.time() - start_time,
                data_sources=[],
                error_message=str(e)
            )

    def _find_products_from_ski_list(self, ski_list: List[str]) -> List[Dict]:
        """Find products from the provided ski list."""
        matched_products = []
        
        for ski_name in ski_list:
            # Use the existing matcher to find products for each ski name
            products = self.matcher.find_products(ski_name, max_results=3)
            if products:
                # Take the best match for each ski name
                best_match = products[0]
                # Avoid duplicates
                if not any(p['title'] == best_match['title'] for p in matched_products):
                    matched_products.append(best_match)
        
        return matched_products
    
    def _classify_property_type_for_ski_list(self, query: str, products: List[Dict]) -> str:
        """Classify property type for queries with provided ski list."""
        query_lower = query.lower()
        
        # Specific property indicators (property:property)
        specific_property_patterns = [
            r'\bwhat.*\b(waist width|price|cost|specs|length|weight|listed price)\b',
            r'\bhow much.*\b(cost|price|does.*cost)\b',
            r'\bwhat.*\b(is\s+the|are\s+the).*\b(price|waist|width|specs|dimensions)\b',
            r'\bprice\b',           # Just "price"
            r'\bcost\b',            # Just "cost"
            r'\bwaist.*width\b',    # Waist width queries
            r'\bhow\s+(wide|heavy|long)\b',  # How wide/heavy/long
            r'\bspecifications\b',  # Specifications
            r'\bdimensions\b',      # Dimensions
            r'\bweight\b'           # Weight queries
        ]
        
        has_specific_property = any(re.search(pattern, query_lower) for pattern in specific_property_patterns)
        
        # Comparison indicators (property:general)
        comparison_patterns = [
            r'\bcompare\b',
            r'\bwhich.*\b(is|has|one)\s+.*(better|best|cheaper|expensive|lighter|wider)\b',
            r'\bbetter\s+for\b',
            r'\bsuitable\s+for\b',
            r'\bgood\s+for\b',
            r'\bdifference\s+between\b',
            r'\bvs\b|\bversus\b'
        ]
        
        has_comparison = any(re.search(pattern, query_lower) for pattern in comparison_patterns)
        
        if has_specific_property and not has_comparison:
            return "property:property"
        else:
            return "property:general"
    
    def _handle_specific_property_query_with_ski_list(self, query: str, products: List[Dict]) -> QueryResult:
        """Handle specific property questions with provided ski list."""
        
        # If multiple products, determine which one to focus on or answer for all
        if len(products) == 1:
            product = products[0]
            prompt = LLMPromptGenerator.generate_property_property_prompt(query, product)
        else:
            # For multiple products, we can answer about all of them
            prompt = LLMPromptGenerator.generate_property_property_multi_prompt(query, products)
        
        # Try LLM first
        llm_response = LLMCaller.call_openai(prompt)
        
        if llm_response:
            logger.info("Using LLM response for property:property query with ski list")
            return QueryResult(
                intent="property:property",
                response=llm_response,
                confidence=0.9,
                processing_time=0,
                data_sources=["product_database", "llm"],
                matched_products=products
            )
        else:
            # Fallback to rule-based response
            logger.warning("LLM failed, using rule-based fallback for property:property query with ski list")
            if len(products) == 1:
                response = self._generate_rule_based_property_response(products[0], query)
            else:
                response = self._generate_rule_based_multi_property_response(products, query)
            
            return QueryResult(
                intent="property:property",
                response=response,
                confidence=0.7,
                processing_time=0,
                data_sources=["product_database"],
                matched_products=products
            )
    
    def _handle_general_property_query_with_ski_list(self, query: str, products: List[Dict]) -> QueryResult:
        """Handle general property questions with provided ski list."""
        
        # Generate LLM prompt with all provided products
        prompt = LLMPromptGenerator.generate_property_general_prompt(query, products)
        
        # Try LLM first
        llm_response = LLMCaller.call_openai(prompt, max_tokens=400)
        
        if llm_response:
            logger.info("Using LLM response for property:general query with ski list")
            return QueryResult(
                intent="property:general",
                response=llm_response,
                confidence=0.9,
                processing_time=0,
                data_sources=["product_database", "llm"],
                matched_products=products
            )
        else:
            # Fallback to rule-based response
            logger.warning("LLM failed, using rule-based fallback for property:general query with ski list")
            if len(products) >= 2:
                response = self._generate_rule_based_comparison_response(products[:2], query)
            else:
                response = self._generate_rule_based_general_response(products[0], query)
            
            return QueryResult(
                intent="property:general",
                response=response,
                confidence=0.7,
                processing_time=0,
                data_sources=["product_database"],
                matched_products=products
            )
    
    def _generate_rule_based_multi_property_response(self, products: List[Dict], query: str) -> str:
        """Generate rule-based response for multiple products."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['price', 'cost', 'much']):
            return self._get_multi_price_response(products)
        elif any(word in query_lower for word in ['waist', 'width']):
            return self._get_multi_waist_width_response(products)
        elif any(word in query_lower for word in ['weight']):
            return self._get_multi_weight_response(products)
        else:
            return self._get_multi_general_specs_response(products)
    
    def _get_multi_price_response(self, products: List[Dict]) -> str:
        """Get price response for multiple products."""
        price_info = []
        for product in products:
            title = product.get('title', 'Unknown ski')
            price = product.get('price')
            discounted_price = product.get('reapris')
            
            if discounted_price and discounted_price != price:
                price_info.append(f"The {title} usually costs {price} SEK but is currently available at a discount for {discounted_price} SEK")
            elif price:
                price_info.append(f"The {title} costs {price} SEK")
            else:
                price_info.append(f"Pricing for the {title} is not available")
        
        return ". ".join(price_info) + "."
    
    def _get_multi_waist_width_response(self, products: List[Dict]) -> str:
        """Get waist width response for multiple products."""
        width_info = []
        for product in products:
            title = product.get('title', 'Unknown ski')
            waist_width = product.get('waist_width_mm')
            
            if waist_width:
                width_info.append(f"The {title} has a waist width of {waist_width}mm")
            else:
                width_info.append(f"Waist width for the {title} is not available")
        
        return ". ".join(width_info) + "."
    
    def _get_multi_weight_response(self, products: List[Dict]) -> str:
        """Get weight response for multiple products."""
        weight_info = []
        for product in products:
            title = product.get('title', 'Unknown ski')
            weight = product.get('weight_grams')
            
            if weight and not pd.isna(weight):
                weight_info.append(f"The {title} weighs {weight}g")
            else:
                weight_info.append(f"Weight for the {title} is not available")
        
        return ". ".join(weight_info) + "."
    
    def _get_multi_general_specs_response(self, products: List[Dict]) -> str:
        """Get general specs response for multiple products."""
        specs_info = []
        for product in products:
            title = product.get('title', 'Unknown ski')
            specs = []
            
            if product.get('waist_width_mm'):
                specs.append(f"waist width: {product['waist_width_mm']}mm")
            if product.get('price'):
                specs.append(f"price: {product['price']} SEK")
            if product.get('weight_grams') and not pd.isna(product['weight_grams']):
                specs.append(f"weight: {product['weight_grams']}g")
            
            if specs:
                specs_info.append(f"The {title}: {', '.join(specs)}")
            else:
                specs_info.append(f"Limited specification data available for the {title}")
        
        return ". ".join(specs_info) + "."

class LLMPromptGenerator:
    """Generates LLM prompts for property question responses."""
    
    @staticmethod
    def format_product_data(product: Dict) -> str:
        """Format complete product data for LLM prompt."""
        data_parts = []
        
        # Core product info
        data_parts.append(f"PRODUCT: {product.get('title', 'Unknown')}")
        data_parts.append(f"Brand: {product.get('brand', 'Unknown')}")
        
        # Technical specifications
        if product.get('waist_width_mm') and not pd.isna(product.get('waist_width_mm')):
            data_parts.append(f"Waist Width: {product.get('waist_width_mm')}mm")
        
        # Pricing info
        price = product.get('price')
        discounted_price = product.get('reapris')
        if discounted_price and not pd.isna(discounted_price) and price and not pd.isna(price) and discounted_price < price:
            data_parts.append(f"Price: {int(price)} SEK (usually), {int(discounted_price)} SEK (discounted)")
        elif price and not pd.isna(price):
            data_parts.append(f"Price: {int(price)} SEK")
        
        # Weight (if real data)
        weight = product.get('weight_grams')
        if weight and not pd.isna(weight) and DataValidator.is_real_data(weight, 'weight_grams'):
            data_parts.append(f"Weight: {weight}g")
        
        # Available lengths
        lengths = product.get('parsed_lengths', [])
        if lengths:
            data_parts.append(f"Available Lengths: {', '.join(map(str, lengths))}cm")
        
        # Twin-tip design
        twin_tip = product.get('twin_tip')
        if pd.notna(twin_tip):
            data_parts.append(f"Twin-tip: {'Yes' if twin_tip else 'No'}")
        
        # Category/tags
        if product.get('tags'):
            data_parts.append(f"Categories: {product.get('tags')}")
        
        # Flex rating (if available)
        if product.get('flex_rating'):
            data_parts.append(f"Flex Rating: {product.get('flex_rating')}")
        
        # Gender target
        if product.get('gender'):
            data_parts.append(f"Target: {product.get('gender')}")
        
        return "\n".join(data_parts)
    
    @staticmethod
    def generate_property_property_prompt(query: str, product: Dict) -> str:
        """Generate prompt for specific property questions."""
        product_data = LLMPromptGenerator.format_product_data(product)
        
        prompt = f"""You are an ai optimized search algorithm, you are an expert on skies and know all of the skies available, what seperates them and what they are useful for. Your goal is to help the user find exactly what they are looking for by asnwering queries. When you answer a query you will not do so like chat bot, meaning do not do it like you are having a conversation. You are a search algorithm and you should simply output the answer to the query followed by some reasoning if the query calls for it. For example, if the query is "is ski x or ski y better for carving" your answer should look something like "ski x is better since it is more narrow and heavier, making it more fit for carving and more stable in higher speeds". And if the query is something like "How wide is ski x" your answer should be "The X is ymm wide, making it suitable for z", meaning no explanation to where you have found it or any reasoning since the query did not call for any. ONLY ANSWER WITH DATA AVAILABLE, DO NOT SEARCH EXTERNALLY. All the data you have is in this prompt. Answer in the same language as the query is phrased in, use proper and gramatically correct phrasing. The aim of your answer is to give the most useful and efficent answer and explanation as possible. Do not use parantheses or other data like structures in your answer, if a ski is discounted phrase it like "x usually costs y but is now on sale and available for only zkr", This is the query and data:

query: {query}

data: {product_data}"""
        
        return prompt
    
    @staticmethod
    def generate_property_general_prompt(query: str, products: List[Dict]) -> str:
        """Generate prompt for general property questions (comparisons, suitability)."""
        if len(products) == 1:
            # Single product general question
            product_data = LLMPromptGenerator.format_product_data(products[0])
            prompt = f"""You are an expert ski equipment advisor providing accurate, helpful advice to skiers. Answer the user's question about this ski's suitability and performance.

USER QUESTION: {query}

PRODUCT DATA:
{product_data}

SKIING EXPERTISE:
- Waist width 70-85mm: Best for groomed runs, carving, beginners
- Waist width 85-100mm: All-mountain versatility, mixed conditions
- Waist width 100mm+: Powder, off-piste, deep snow flotation
- Lighter skis (<1500g): Better for touring, less fatigue
- Twin-tip design: Essential for park skiing, freestyle
- Narrower skis: Better edge hold on ice, responsive on groomers
- Wider skis: Better flotation in powder, stability in variable conditions

INSTRUCTIONS:
- Provide expert skiing advice based on the product specifications
- Consider the user's question context (beginner, off-piste, etc.)
- Be specific about why this ski would or wouldn't work for their needs
- Mention relevant specifications that affect performance
- Include the product name in your response
- Be honest about limitations

RESPONSE:"""
        
        else:
            # Comparison between multiple products
            products_data = []
            for i, product in enumerate(products, 1):
                products_data.append(f"PRODUCT {i}:")
                products_data.append(LLMPromptGenerator.format_product_data(product))
                products_data.append("")
            
            prompt = f"""You are an expert ski equipment advisor providing accurate, helpful advice to skiers. Compare these ski products and answer the user's question.

USER QUESTION: {query}

PRODUCTS TO COMPARE:
{chr(10).join(products_data)}

SKIING EXPERTISE:
- Waist width 70-85mm: Best for groomed runs, carving, beginners
- Waist width 85-100mm: All-mountain versatility, mixed conditions  
- Waist width 100mm+: Powder, off-piste, deep snow flotation
- Lighter skis (<1500g): Better for touring, less fatigue
- Twin-tip design: Essential for park skiing, freestyle
- Narrower skis: Better edge hold on ice, responsive on groomers
- Wider skis: Better flotation in powder, stability in variable conditions
- Price differences: Consider value proposition

INSTRUCTIONS:
- Compare the products directly based on the user's question
- If asking about "cheapest" or price, compare prices accurately
- If asking about skiing performance, explain which is better and why
- Use specific product names in your comparison
- Mention relevant specifications that affect the comparison
- Be definitive in your recommendation when there's a clear winner
- If they're similar, explain the trade-offs

RESPONSE:"""
        
        return prompt
    
    @staticmethod
    def generate_property_property_multi_prompt(query: str, products: List[Dict]) -> str:
        """Generate prompt for specific property questions about multiple products."""
        products_data = []
        for i, product in enumerate(products, 1):
            products_data.append(f"PRODUCT {i}:")
            products_data.append(LLMPromptGenerator.format_product_data(product))
            products_data.append("")
        
        prompt = f"""You are an ai optimized search algorithm, you are an expert on skies and know all of the skies available, what seperates them and what they are useful for. Your goal is to help the user find exactly what they are looking for by asnwering queries. When you answer a query you will not do so like chat bot, meaning do not do it like you are having a conversation. You are a search algorithm and you should simply output the answer to the query followed by some reasoning if the query calls for it. For example, if the query is "is ski x or ski y better for carving" your answer should look something like "ski x is better since it is more narrow and heavier, making it more fit for carving and more stable in higher speeds". And if the query is something like "How wide is ski x" your answer should be "The X is ymm wide, making it suitable for z", meaning no explanation to where you have found it or any reasoning since the query did not call for any. ONLY ANSWER WITH DATA AVAILABLE, DO NOT SEARCH EXTERNALLY. All the data you have is in this prompt. Answer in the same language as the query is phrased in, use proper and gramatically correct phrasing. The aim of your answer is to give the most useful and efficent answer and explanation as possible. Do not use parantheses or other data like structures in your answer, if a ski is discounted phrase it like "x usually costs y but is now on sale and available for only zkr", This is the query and data:

query: {query}

data: 
{chr(10).join(products_data)}"""
        
        return prompt

class LLMCaller:
    """Handles LLM API calls with error handling and fallbacks."""
    
    @staticmethod
    def call_gemini(prompt: str, max_tokens: int = 300) -> Optional[str]:
        """Call Gemini API with error handling."""
        # Get API key dynamically
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            logger.warning("Gemini API key not set - falling back to rule-based response")
            return None
        
        if not GEMINI_AVAILABLE:
            logger.warning("google-generativeai library not available - falling back to rule-based response")
            return None
        
        try:
            # Configure API key dynamically
            genai.configure(api_key=api_key)
            
            # Initialize the model
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.3,  # Lower temperature for more consistent responses
            )
            
            # Generate response
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if response.text:
                return response.text.strip()
            else:
                logger.warning("Empty response from Gemini API")
                return None
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return None
    
    @staticmethod
    def call_openai(prompt: str, max_tokens: int = 300) -> Optional[str]:
        """Legacy method name for compatibility - now calls Gemini."""
        return LLMCaller.call_gemini(prompt, max_tokens)

def main():
    """Main function for testing the fixed system."""
    try:
        handler = FixedOptimizedQueryHandler()
        
        # Test queries with the problematic cases
        test_queries = [
            "What are the specs of the Atomic Bent 110?",
            "Can I use the Stöckli Laser MX for off piste?",
            "Between the Line Pandora 99 and the Line Chronic 94, which has a lighter weight?",
            "Are the Völkl Mantra Junior twintip?",
            "Show me all-mountain skis under 5000 SEK"
        ]
        
        print("🎿 FIXED OPTIMIZED SKI QUERY SYSTEM TEST")
        print("=" * 70)
        print("🚨 CRITICAL FIX: No default/placeholder data will be shown as factual")
        print("=" * 70)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Query: {query}")
            print("-" * 70)
            
            result = handler.handle_query(query)
            
            print(f"Intent: {result.intent}")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Processing Time: {result.processing_time:.3f}s")
            print(f"Response:")
            print(result.response)
            
            if result.error_message:
                print(f"Error: {result.error_message}")
    
    except Exception as e:
        logger.error(f"System initialization failed: {e}")
        print(f"❌ Failed to initialize system: {e}")

if __name__ == "__main__":
    main() 