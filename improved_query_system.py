#!/usr/bin/env python3
"""
Improved query system with better intent classification for specific product queries
"""

import pandas as pd
import re
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QueryResult:
    """Structured query result with comprehensive information."""
    intent: str
    response: str
    confidence: float
    processing_time: float = 0.0
    data_sources: List[str] = field(default_factory=list)
    matched_products: List[Dict] = field(default_factory=list)
    error_message: Optional[str] = None

class DataValidator:
    """Enhanced data validation with default value detection."""
    
    DEFAULT_VALUES = {
        'turn_radius_m': [20.0],
        'weight_grams': [1140.0],
        'model_year': ['', None],
    }
    
    @staticmethod
    def validate_csv_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate CSV data quality and detect issues."""
        issues = []
        
        # Check for required columns
        required_cols = ['title', 'brand', 'waist_width_mm', 'price']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            issues.append(f"Missing required columns: {missing_cols}")
        
        # Check for default values
        for col, defaults in DataValidator.DEFAULT_VALUES.items():
            if col in df.columns:
                default_count = sum(df[col].isin(defaults))
                total_count = len(df)
                if default_count > total_count * 0.8:  # More than 80% are defaults
                    issues.append(f"Column '{col}' contains mostly default values ({default_count}/{total_count})")
        
        # Data completeness check
        completeness = {}
        for col in ['weight_grams', 'turn_radius_m']:
            if col in df.columns:
                non_null = df[col].notna().sum()
                completeness[col] = (non_null / len(df)) * 100
        
        low_completeness = {k: v for k, v in completeness.items() if v < 50}
        if low_completeness:
            issues.append(f"Low data completeness: {low_completeness}")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def clean_product_data(df: pd.DataFrame) -> pd.DataFrame:
        """Clean product data and remove default values."""
        df = df.copy()
        
        # Replace default values with NaN
        for col, defaults in DataValidator.DEFAULT_VALUES.items():
            if col in df.columns:
                logger.info(f"Replaced {defaults} with NaN in column '{col}' as these are default values")
                df[col] = df[col].replace(defaults, pd.NA)
        
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
        
        return df

class ImprovedProductMatcher:
    """Improved product matching with better brand and model detection."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.brand_patterns = self._build_brand_patterns()
        self.model_patterns = self._build_model_patterns()
        
    def _build_brand_patterns(self) -> Dict[str, List[str]]:
        """Build comprehensive brand pattern matching."""
        return {
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
            'blizzard': ['blizzard']
        }
    
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
            # Other common models
            r'rustler', r'laser', r'wailer', r'santa\s*ana', r'enforcer'
        ]
    
    def find_products(self, query: str, max_results: int = 10) -> List[Dict]:
        """Find products matching the query with improved search."""
        query_lower = query.lower()
        matches = []
        
        # Extract brands and models
        brands = self._extract_brands(query_lower)
        models = self._extract_models(query_lower)
        numbers = self._extract_numbers(query_lower)
        
        for idx, row in self.df.iterrows():
            score = self._calculate_match_score(row, query_lower, brands, models, numbers)
            if score > 0.2:  # Lower threshold for better recall
                product_dict = row.to_dict()
                product_dict['match_score'] = score
                matches.append(product_dict)
        
        # Sort by match score and return top results
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches[:max_results]
    
    def _extract_brands(self, query: str) -> List[str]:
        """Extract brand names from query."""
        brands = []
        for brand, patterns in self.brand_patterns.items():
            if any(pattern in query for pattern in patterns):
                brands.append(brand)
        return brands
    
    def _extract_models(self, query: str) -> List[str]:
        """Extract model names from query."""
        models = []
        for pattern in self.model_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                models.extend([m if isinstance(m, str) else m[0] for m in matches])
        return models
    
    def _extract_numbers(self, query: str) -> List[int]:
        """Extract numbers that might be model numbers or waist widths."""
        numbers = re.findall(r'\b(\d{2,3})\b', query)
        return [int(n) for n in numbers if 70 <= int(n) <= 130]  # Typical waist widths
    
    def _calculate_match_score(self, product: pd.Series, query: str, brands: List[str], models: List[str], numbers: List[int]) -> float:
        """Calculate improved match score for a product."""
        score = 0.0
        title = str(product.get('title', '')).lower()
        brand = str(product.get('brand', '')).lower()
        
        # Brand matching (high weight)
        if brands:
            for b in brands:
                if b in brand or b in title:
                    score += 0.5
                    break
        
        # Model matching (very high weight)
        if models:
            for m in models:
                if m in title:
                    score += 0.6
                    break
        
        # Number matching (waist width, etc.)
        if numbers:
            waist = product.get('waist_width_mm')
            if waist and not pd.isna(waist):
                for num in numbers:
                    if abs(waist - num) <= 2:  # Close match for waist width
                        score += 0.3
                        break
        
        # General word matching
        query_words = [w for w in query.split() if len(w) > 2]
        title_words = title.split()
        
        for q_word in query_words:
            for t_word in title_words:
                if q_word in t_word or t_word in q_word:
                    score += 0.1
        
        return min(score, 1.0)

class ImprovedQueryHandler:
    """Improved query handler with better intent classification."""
    
    def __init__(self, data_file: str = 'alpingaraget_ai_optimized.csv'):
        """Initialize the improved query handler."""
        self.data_file = data_file
        self.df = None
        self.matcher = None
        self.load_data()
        
    def load_data(self) -> None:
        """Load and validate data with comprehensive error handling."""
        try:
            logger.info(f"Loading data from {self.data_file}")
            self.df = pd.read_csv(self.data_file)
            
            # Validate data quality
            is_valid, issues = DataValidator.validate_csv_data(self.df)
            if not is_valid:
                logger.warning(f"Data quality issues found: {issues}")
            
            # Clean data and remove default values
            self.df = DataValidator.clean_product_data(self.df)
            
            # Initialize matcher
            self.matcher = ImprovedProductMatcher(self.df)
            
            logger.info(f"Successfully loaded {len(self.df)} products")
            logger.info("IMPORTANT: Default/placeholder values have been removed")
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def handle_query(self, query: str) -> QueryResult:
        """Handle query with improved intent classification."""
        start_time = time.time()
        
        try:
            logger.info(f"Processing query: {query}")
            
            # Validate input
            if not query or len(query.strip()) < 3:
                return QueryResult(
                    intent="invalid",
                    response="Query too short or empty. Please provide a more detailed question.",
                    confidence=0.0,
                    processing_time=time.time() - start_time
                )
            
            # Improved intent classification
            intent, confidence = self._classify_intent_improved(query)
            
            # Route to appropriate handler
            if intent == "search" or intent == "describe":
                result = self._handle_product_query(query, intent)
            elif intent == "compare":
                result = self._handle_compare_query(query)
            else:
                result = self._handle_general_query(query)
            
            result.processing_time = time.time() - start_time
            logger.info(f"Query processed successfully in {result.processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query '{query}': {e}")
            return QueryResult(
                intent="error",
                response="I apologize, but I encountered an error while processing your query.",
                confidence=0.0,
                processing_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def _classify_intent_improved(self, query: str) -> Tuple[str, float]:
        """Improved intent classification that better detects product queries."""
        query_lower = query.lower()
        
        # Check for specific product mentions (high confidence indicators)
        brand_indicators = [
            'atomic', 'salomon', 'rossignol', 'k2', 'armada', 'völkl', 'volkl',
            'line', 'faction', 'dynafit', 'dps', 'nordica', 'stöckli', 'stockli',
            'fischer', 'head', 'blizzard'
        ]
        
        model_indicators = [
            'bent', 'qst', 'arv', 'pandora', 'chronic', 'prodigy', 'blaze',
            'mantra', 'laser', 'wailer', 'santa ana', 'enforcer', 'rustler'
        ]
        
        # If query mentions specific brand + model, it's likely a product query
        has_brand = any(brand in query_lower for brand in brand_indicators)
        has_model = any(model in query_lower for model in model_indicators)
        has_year = bool(re.search(r'\b(20\d{2}|2[4-5]/2[5-6])\b', query))
        
        # Comparison indicators
        compare_patterns = [
            r'\b(compare|versus|vs|between\s+.+\s+and)\b',
            r'\bwhich\s+(is|has|ski|one)\s+.*(wider|better|cheaper|expensive|lighter)',
            r'\b(wider|narrower|cheaper|expensive|lighter|heavier)\b.*:'
        ]
        
        is_comparison = any(re.search(pattern, query_lower) for pattern in compare_patterns)
        
        # Specific product question indicators
        product_question_patterns = [
            r'\bwhat.*\b(waist width|price|cost|specs|length|weight)\b',
            r'\bhow much.*\b(cost|price)\b',
            r'\bis.*\b(twin.?tip|good for|suitable)\b',
            r'\bwhich.*\b(length|options)\b.*offered',
            r'\bdoes.*\b(width|waist)\b.*put.*\b(category|medium|wide)\b'
        ]
        
        is_product_question = any(re.search(pattern, query_lower) for pattern in product_question_patterns)
        
        # Decision logic
        if is_comparison:
            return ("compare", 0.9)
        elif (has_brand and has_model) or (has_brand and has_year) or is_product_question:
            if is_product_question or any(word in query_lower for word in ['what', 'how much', 'is', 'does']):
                return ("describe", 0.8)
            else:
                return ("search", 0.8)
        elif has_brand or has_model:
            return ("search", 0.6)
        else:
            return ("general", 0.5)
    
    def _handle_product_query(self, query: str, intent: str) -> QueryResult:
        """Handle specific product queries (search/describe)."""
        products = self.matcher.find_products(query, max_results=5)
        
        if not products:
            return QueryResult(
                intent=intent,
                response="I couldn't find any products matching your query. Please check the product name and try again.",
                confidence=0.2,
                data_sources=["product_database"],
                matched_products=[]
            )
        
        # Get the best match
        best_match = products[0]
        
        if intent == "describe" and best_match['match_score'] > 0.5:
            # Provide detailed information about the specific product
            response = self._generate_product_description(best_match)
        else:
            # Show search results
            response = self._generate_search_results(products)
        
        return QueryResult(
            intent=intent,
            response=response,
            confidence=0.8,
            data_sources=["product_database"],
            matched_products=products
        )
    
    def _generate_product_description(self, product: Dict) -> str:
        """Generate detailed product description using only real data."""
        title = product.get('title', 'Unknown Product')
        
        response_parts = [f"About the {title}:"]
        
        # Waist width (most reliable data)
        waist = product.get('waist_width_mm')
        if waist and not pd.isna(waist):
            response_parts.append(f"• Waist width: {waist}mm")
        
        # Price
        price = product.get('price')
        if price and not pd.isna(price):
            response_parts.append(f"• Price: {price} SEK")
        
        # Lengths
        lengths = product.get('lengths_cm')
        if lengths and str(lengths) != 'nan':
            response_parts.append(f"• Available lengths: {lengths}")
        
        # Twin-tip info
        is_twin_tip = product.get('is_twin_tip')
        if not pd.isna(is_twin_tip):
            twin_tip_text = "Yes" if is_twin_tip else "No"
            response_parts.append(f"• Twin-tip: {twin_tip_text}")
        
        # Weight (only if real data)
        weight = product.get('weight_grams')
        if weight and not pd.isna(weight):
            response_parts.append(f"• Weight: {weight}g")
        else:
            response_parts.append("• Weight: Not available in our database")
        
        # Turn radius (only if real data)
        turn_radius = product.get('turn_radius_m')
        if turn_radius and not pd.isna(turn_radius):
            response_parts.append(f"• Turn radius: {turn_radius}m")
        else:
            response_parts.append("• Turn radius: Not specified in our database")
        
        return "\n".join(response_parts)
    
    def _generate_search_results(self, products: List[Dict]) -> str:
        """Generate search results display."""
        response_parts = ["Here are the products I found:\n"]
        
        for i, product in enumerate(products[:3], 1):
            title = product.get('title', 'Unknown')
            price = product.get('price', 'N/A')
            waist = product.get('waist_width_mm', 'N/A')
            
            response_parts.append(f"{i}. {title}")
            response_parts.append(f"   Price: {price} SEK | Waist: {waist}mm")
        
        return "\n".join(response_parts)
    
    def _handle_compare_query(self, query: str) -> QueryResult:
        """Handle comparison queries."""
        products = self.matcher.find_products(query, max_results=5)
        
        if len(products) < 2:
            return QueryResult(
                intent="compare",
                response="I need at least two products to make a comparison. Please specify the exact ski models you'd like to compare.",
                confidence=0.3,
                data_sources=["product_database"],
                matched_products=products
            )
        
        # Generate comparison
        comparison_result = self._generate_comparison(products[:2])
        
        return QueryResult(
            intent="compare",
            response=comparison_result,
            confidence=0.8,
            data_sources=["product_database"],
            matched_products=products[:2]
        )
    
    def _generate_comparison(self, products: List[Dict]) -> str:
        """Generate detailed product comparison."""
        p1, p2 = products[0], products[1]
        
        response_parts = [
            f"Comparing {p1.get('title', 'Product 1')} vs {p2.get('title', 'Product 2')}:\n"
        ]
        
        # Price comparison
        price1 = p1.get('price')
        price2 = p2.get('price')
        if price1 and price2 and not pd.isna(price1) and not pd.isna(price2):
            cheaper = p1 if price1 < price2 else p2
            response_parts.append(f"Price: {p1.get('title')} costs {price1} SEK, {p2.get('title')} costs {price2} SEK")
            response_parts.append(f"The {cheaper.get('title')} is cheaper by {abs(price1 - price2)} SEK.\n")
        
        # Waist width comparison
        width1 = p1.get('waist_width_mm')
        width2 = p2.get('waist_width_mm')
        if width1 and width2 and not pd.isna(width1) and not pd.isna(width2):
            wider = p1 if width1 > width2 else p2
            response_parts.append(f"Waist Width: {p1.get('title')} has {width1}mm, {p2.get('title')} has {width2}mm")
            response_parts.append(f"The {wider.get('title')} is wider, making it better for powder skiing.\n")
        
        # Length options
        lengths1 = p1.get('lengths_cm')
        lengths2 = p2.get('lengths_cm')
        if lengths1 and lengths2:
            response_parts.append("Available lengths:")
            response_parts.append(f"- {p1.get('title')}: {lengths1}")
            response_parts.append(f"- {p2.get('title')}: {lengths2}")
        
        # Note about missing data
        response_parts.append("\nWeight and turn radius specifications are not available in our database.")
        
        return "\n".join(response_parts)
    
    def _handle_general_query(self, query: str) -> QueryResult:
        """Handle general queries."""
        return QueryResult(
            intent="general",
            response="I specialize in specific ski product information from our database. Please ask about specific ski models, comparisons, or product specifications.",
            confidence=0.5,
            data_sources=[],
            matched_products=[]
        )

def test_improved_system():
    """Test the improved system with the specific queries."""
    print("🔧 TESTING IMPROVED QUERY SYSTEM")
    print("=" * 80)
    
    handler = ImprovedQueryHandler()
    
    queries = [
        "What's the waist width of the Faction Prodigy 4 24/25?",
        "How much does the DPS Wailer 112 RP 24/25 cost?",
        "What's the listed price for the Nordica Santa Ana 93 24/25?",
        "Is the Salomon QST Lux 92 Ti 24/25 a twin-tip ski?",
        "Which length options are offered for the Armada ARV 88 24/25?",
    ]
    
    for i, query in enumerate(queries[:5], 1):  # Test first 5
        print(f"\n{'='*60}")
        print(f"QUERY {i}: {query}")
        print('='*60)
        
        start_time = time.time()
        result = handler.handle_query(query)
        response_time = time.time() - start_time
        
        print(f"Intent: {result.intent}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Response Time: {response_time:.3f} seconds")
        print(f"Products Found: {len(result.matched_products)}")
        print(f"\nResponse:\n{result.response}")
        
        if result.matched_products:
            print(f"\nTop Match: {result.matched_products[0].get('title')} (Score: {result.matched_products[0].get('match_score', 0):.2f})")

if __name__ == "__main__":
    test_improved_system() 