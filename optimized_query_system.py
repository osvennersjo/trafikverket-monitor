#!/usr/bin/env python3
"""
Optimized Ski Equipment Query System

This optimized version addresses the key issues identified in the diagnosis:
1. Data Quality and Preprocessing
2. Error Handling and Logging
3. Query Processing Improvements
4. Performance Optimizations
5. Better Testing and Validation
"""

import logging
import time
import pandas as pd
import re
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
import sys
import os

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

class DataValidator:
    """Validates and preprocesses data for better accuracy."""
    
    @staticmethod
    def validate_csv_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate the CSV data quality."""
        issues = []
        
        # Check for required columns
        required_cols = ['title', 'brand', 'price', 'waist_width_mm']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            issues.append(f"Missing required columns: {missing_cols}")
        
        # Check data completeness
        completeness = {}
        for col in df.columns:
            if col in df.select_dtypes(include=['object']).columns:
                non_empty = df[col].notna() & (df[col] != '') & (df[col] != 'unknown')
                completeness[col] = non_empty.sum() / len(df) * 100
            else:
                completeness[col] = df[col].notna().sum() / len(df) * 100
        
        # Report low completeness
        low_completeness = {k: v for k, v in completeness.items() if v < 70}
        if low_completeness:
            issues.append(f"Low data completeness: {low_completeness}")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def clean_product_data(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize product data."""
        df = df.copy()
        
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

class EnhancedProductMatcher:
    """Enhanced product matching with fuzzy search and validation."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.brand_patterns = self._build_brand_patterns()
        
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
            'fischer': ['fischer']
        }
        return patterns
    
    def find_products(self, query: str, max_results: int = 10) -> List[Dict]:
        """Find products matching the query with enhanced search."""
        query_lower = query.lower()
        matches = []
        
        # Extract potential product names and brands
        brands = self._extract_brands(query_lower)
        models = self._extract_models(query_lower)
        
        for idx, row in self.df.iterrows():
            score = self._calculate_match_score(row, query_lower, brands, models)
            if score > 0.3:  # Minimum threshold
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
        """Extract potential model names from query."""
        # Common ski model patterns
        model_patterns = [
            r'\b(mindbender|bent|enforcer|arv|edollo|declivity)\b',
            r'\b(pandora|chronic|sakana|reckoner)\b',
            r'\b(qst|laser|blaze|mantra)\b',
            r'\b(blacklight|kaizen|prodigy)\b'
        ]
        
        models = []
        for pattern in model_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            models.extend(matches)
        
        return models
    
    def _calculate_match_score(self, product: pd.Series, query: str, brands: List[str], models: List[str]) -> float:
        """Calculate match score for a product."""
        score = 0.0
        title = str(product.get('title', '')).lower()
        brand = str(product.get('brand', '')).lower()
        tags = str(product.get('tags', '')).lower()
        
        # Brand matching (high weight)
        if brands:
            if any(b in brand for b in brands):
                score += 0.4
            if any(b in title for b in brands):
                score += 0.3
        
        # Model matching (high weight)
        if models:
            if any(m in title for m in models):
                score += 0.4
        
        # General text matching
        query_words = query.split()
        title_words = title.split()
        
        common_words = set(query_words) & set(title_words)
        if common_words:
            score += 0.2 * (len(common_words) / len(query_words))
        
        # Tag matching
        if any(word in tags for word in query_words):
            score += 0.1
        
        return min(score, 1.0)

class OptimizedQueryHandler:
    """Optimized query handler with enhanced error handling and performance."""
    
    def __init__(self, data_file: str = 'alpingaraget_ai_optimized.csv'):
        """Initialize the optimized query handler."""
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
            
            # Clean data
            self.df = DataValidator.clean_product_data(self.df)
            
            # Initialize matcher
            self.matcher = EnhancedProductMatcher(self.df)
            
            logger.info(f"Successfully loaded {len(self.df)} products")
            
        except FileNotFoundError:
            logger.error(f"Data file not found: {self.data_file}")
            raise
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def handle_query(self, query: str) -> QueryResult:
        """Handle query with comprehensive error handling and logging."""
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
            
            # Classify intent with enhanced logic
            intent = self._classify_intent_enhanced(query)
            
            # Route to appropriate handler
            if intent == "search":
                result = self._handle_search_query(query)
            elif intent == "compare":
                result = self._handle_compare_query(query)
            elif intent == "describe":
                result = self._handle_describe_query(query)
            else:
                result = self._handle_general_query(query)
            
            result.processing_time = time.time() - start_time
            logger.info(f"Query processed successfully in {result.processing_time:.3f}s")
            
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
    
    def _classify_intent_enhanced(self, query: str) -> str:
        """Enhanced intent classification with better accuracy."""
        query_lower = query.lower()
        
        # Comparison indicators (enhanced)
        compare_patterns = [
            r'\b(compare|versus|vs|difference|better|worse)\b',
            r'\bbetween\s+.+\s+and\s+',
            r'\bwhich\s+(is|has|ski|one)',
            r'\b(lighter|heavier|wider|narrower|cheaper|expensive)\b'
        ]
        
        if any(re.search(pattern, query_lower) for pattern in compare_patterns):
            return "compare"
        
        # Search indicators
        search_patterns = [
            r'\b(show|find|search|list|recommend|suggest)\b',
            r'\bi\s+(want|need|am\s+looking\s+for)\b',
            r'\bdo\s+you\s+have\b'
        ]
        
        if any(re.search(pattern, query_lower) for pattern in search_patterns):
            return "search"
        
        # Describe indicators
        describe_patterns = [
            r'\b(can|will|is|are|does)\s+.+\s+(work|good|suitable)\b',
            r'\bhow\s+(stable|flexible|wide)\b',
            r'\bwhat\s+(are\s+the\s+specs|is\s+the\s+weight)\b'
        ]
        
        if any(re.search(pattern, query_lower) for pattern in describe_patterns):
            return "describe"
        
        return "general"
    
    def _handle_search_query(self, query: str) -> QueryResult:
        """Handle search queries with enhanced product matching."""
        products = self.matcher.find_products(query, max_results=5)
        
        if not products:
            return QueryResult(
                intent="search",
                response="I couldn't find any products matching your search criteria. Please try different keywords or be more specific.",
                confidence=0.2,
                processing_time=0,
                data_sources=["product_database"],
                matched_products=[]
            )
        
        # Format response
        response_parts = ["Here are the products I found matching your search:\n"]
        
        for i, product in enumerate(products, 1):
            title = product.get('title', 'Unknown')
            price = product.get('price', 'N/A')
            waist = product.get('waist_width_mm', 'N/A')
            
            response_parts.append(
                f"{i}. {title} - {price} SEK (Waist: {waist}mm)"
            )
        
        return QueryResult(
            intent="search",
            response="\n".join(response_parts),
            confidence=0.8,
            processing_time=0,
            data_sources=["product_database"],
            matched_products=products
        )
    
    def _handle_compare_query(self, query: str) -> QueryResult:
        """Handle comparison queries with enhanced logic."""
        products = self.matcher.find_products(query, max_results=5)
        
        if len(products) < 2:
            return QueryResult(
                intent="compare",
                response="I need at least two products to make a comparison. Please specify the exact ski models you'd like to compare.",
                confidence=0.3,
                processing_time=0,
                data_sources=["product_database"],
                matched_products=products
            )
        
        # Enhanced comparison logic
        comparison_result = self._generate_comparison(products[:2], query)
        
        return QueryResult(
            intent="compare",
            response=comparison_result,
            confidence=0.8,
            processing_time=0,
            data_sources=["product_database"],
            matched_products=products[:2]
        )
    
    def _generate_comparison(self, products: List[Dict], query: str) -> str:
        """Generate detailed product comparison."""
        p1, p2 = products[0], products[1]
        
        response_parts = [
            f"Comparing {p1.get('title', 'Product 1')} vs {p2.get('title', 'Product 2')}:\n"
        ]
        
        # Price comparison
        price1 = p1.get('price', 0) or 0
        price2 = p2.get('price', 0) or 0
        if price1 and price2:
            cheaper = p1 if price1 < price2 else p2
            response_parts.append(f"Price: {p1.get('title')} costs {price1} SEK, {p2.get('title')} costs {price2} SEK")
            response_parts.append(f"The {cheaper.get('title')} is cheaper by {abs(price1 - price2)} SEK.\n")
        
        # Waist width comparison
        width1 = p1.get('waist_width_mm', 0) or 0
        width2 = p2.get('waist_width_mm', 0) or 0
        if width1 and width2:
            wider = p1 if width1 > width2 else p2
            response_parts.append(f"Waist Width: {p1.get('title')} has {width1}mm, {p2.get('title')} has {width2}mm")
            response_parts.append(f"The {wider.get('title')} is wider, making it better for powder skiing.\n")
        
        # Weight comparison (if available)
        weight1 = p1.get('weight_grams', 0) or 0
        weight2 = p2.get('weight_grams', 0) or 0
        if weight1 and weight2:
            lighter = p1 if weight1 < weight2 else p2
            response_parts.append(f"Weight: {p1.get('title')} weighs {weight1}g, {p2.get('title')} weighs {weight2}g")
            response_parts.append(f"The {lighter.get('title')} is lighter by {abs(weight1 - weight2)}g.\n")
        
        # Length availability
        lengths1 = p1.get('parsed_lengths', [])
        lengths2 = p2.get('parsed_lengths', [])
        if lengths1 and lengths2:
            response_parts.append(f"Available lengths:")
            response_parts.append(f"- {p1.get('title')}: {', '.join(map(str, lengths1))}cm")
            response_parts.append(f"- {p2.get('title')}: {', '.join(map(str, lengths2))}cm")
        
        return "\n".join(response_parts)
    
    def _handle_describe_query(self, query: str) -> QueryResult:
        """Handle descriptive queries about specific products."""
        products = self.matcher.find_products(query, max_results=3)
        
        if not products:
            return QueryResult(
                intent="describe",
                response="I couldn't identify the specific product you're asking about. Please provide the exact ski model name.",
                confidence=0.2,
                processing_time=0,
                data_sources=["product_database"],
                matched_products=[]
            )
        
        product = products[0]
        description = self._generate_product_description(product, query)
        
        return QueryResult(
            intent="describe",
            response=description,
            confidence=0.8,
            processing_time=0,
            data_sources=["product_database"],
            matched_products=[product]
        )
    
    def _generate_product_description(self, product: Dict, query: str) -> str:
        """Generate detailed product description based on query context."""
        title = product.get('title', 'Unknown Product')
        waist = product.get('waist_width_mm', 'N/A')
        price = product.get('price', 'N/A')
        tags = product.get('tags', '')
        
        response_parts = [f"About the {title}:\n"]
        
        # Basic specs
        response_parts.append(f"• Waist width: {waist}mm")
        response_parts.append(f"• Price: {price} SEK")
        
        # Length information
        lengths = product.get('parsed_lengths', [])
        if lengths:
            response_parts.append(f"• Available lengths: {', '.join(map(str, lengths))}cm")
        
        # Context-specific information based on query
        query_lower = query.lower()
        
        if 'powder' in query_lower or 'off piste' in query_lower:
            if waist and isinstance(waist, (int, float)):
                if waist >= 100:
                    response_parts.append(f"\nFor powder skiing: Excellent choice! With {waist}mm waist width, this ski offers great flotation in deep snow.")
                elif waist >= 85:
                    response_parts.append(f"\nFor powder skiing: Good for light powder, but the {waist}mm waist might struggle in very deep snow.")
                else:
                    response_parts.append(f"\nFor powder skiing: Not recommended. The {waist}mm waist is too narrow for powder skiing.")
        
        if 'beginner' in query_lower:
            if 'beginner' in tags.lower() or 'intermediate' in tags.lower():
                response_parts.append(f"\nFor beginners: Yes, this ski is suitable for beginner to intermediate skiers.")
            else:
                response_parts.append(f"\nFor beginners: This appears to be an advanced ski and might be challenging for beginners.")
        
        if 'twin' in query_lower or 'twintip' in query_lower:
            twin_tip = product.get('twin_tip', False)
            response_parts.append(f"\nTwin-tip design: {'Yes' if twin_tip else 'No'}")
        
        return "\n".join(response_parts)
    
    def _handle_general_query(self, query: str) -> QueryResult:
        """Handle general skiing questions."""
        # This could be enhanced with a knowledge base
        return QueryResult(
            intent="general",
            response="I specialize in specific ski product information. For general skiing advice, please consult a ski instructor or refer to skiing guides.",
            confidence=0.5,
            processing_time=0,
            data_sources=["general_knowledge"]
        )

def main():
    """Main function for testing the optimized system."""
    try:
        handler = OptimizedQueryHandler()
        
        # Test queries
        test_queries = [
            "Can I use the Stöckli Laser MX for off piste?",
            "Between the Line Pandora 99 and the Line Chronic 94, which has a lighter weight?",
            "Are the Völkl Mantra Junior twintip?",
            "Show me all-mountain skis under 5000 SEK",
            "What are the specs of the Atomic Bent 110?"
        ]
        
        print("🎿 OPTIMIZED SKI QUERY SYSTEM TEST")
        print("=" * 60)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Query: {query}")
            print("-" * 60)
            
            result = handler.handle_query(query)
            
            print(f"Intent: {result.intent}")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Processing Time: {result.processing_time:.3f}s")
            print(f"Response: {result.response[:200]}{'...' if len(result.response) > 200 else ''}")
            
            if result.error_message:
                print(f"Error: {result.error_message}")
    
    except Exception as e:
        logger.error(f"System initialization failed: {e}")
        print(f"❌ Failed to initialize system: {e}")

if __name__ == "__main__":
    main() 