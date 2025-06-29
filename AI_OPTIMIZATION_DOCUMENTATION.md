# AI-Optimized Ski Dataset Documentation

## Overview
This document describes the AI optimizations applied to the Alpingaraget ski dataset, converting it from Excel format to a machine learning-ready CSV format.

## 📊 Dataset Summary
- **Original**: 172 products × 12 features
- **Optimized**: 172 products × 22 features  
- **Data Completeness**: 94.6%
- **File Format**: UTF-8 encoded CSV
- **File Size**: 405 KB

## 🔄 Transformations Applied

### 1. Column Name Standardization
**Problem**: Original column names contained Swedish characters, colons, and special characters that are problematic for AI frameworks.

**Solution**: 
- Converted Swedish to English (e.g., `varumärke:` → `brand`)
- Removed special characters (colons, spaces)
- Applied snake_case convention
- Examples:
  - `titel:` → `title`
  - `Bredd:` → `waist_width_mm`
  - `Längd:` → `lengths_cm`
  - `kategori:` → `category`

### 2. Data Type Optimization
**Problem**: Mixed data types and inconsistent formatting.

**Solution**:
- **Numeric**: Converted width, price to proper numeric types
- **Boolean**: Converted `twintip` (1.0/0.0) to true boolean values
- **Text**: Standardized all text fields to string type
- **Categorical**: Created categorical encodings where appropriate

### 3. Feature Engineering
**Problem**: Important information was buried in unstructured text fields.

**New Features Created**:

#### Extracted from Tags:
- `weight_grams`: Extracted weight values (e.g., "1410g" → 1410.0)
- `turn_radius_m`: Extracted turn radius (e.g., "15m-radius" → 15.0)

#### Parsed from Lengths:
- `length_options`: Array of available lengths [165, 172, 179, 186]
- `min_length_cm`: Minimum available length (165)
- `max_length_cm`: Maximum available length (186)  
- `length_count`: Number of length options (4)

#### Derived from Model Names:
- `model_year`: Extracted year from product titles (where available)

#### Categorical Features:
- `width_category`: Categorized waist width
  - narrow: < 85mm
  - medium: 85-95mm  
  - wide: 95-105mm
  - very_wide: > 105mm
- `price_category`: Price range classification
  - budget: < 3000 SEK
  - mid_range: 3000-5000 SEK
  - premium: 5000-7000 SEK
  - luxury: > 7000 SEK
- `skiing_style`: Multi-label classification from tags/category
  - freestyle, freeride, allmountain, touring, racing

### 4. Missing Value Handling
**Strategy**: Domain-aware imputation

- **Numeric Features**: Filled with median values
  - `weight_grams`: 159 missing → filled with 1140g (median)
  - `turn_radius_m`: 168 missing → filled with 20m (median)
  - `waist_width_mm`: 1 missing → filled with 95mm (median)

- **Categorical Features**: Filled with 'unknown' label
  - Preserves information about missing data
  - Allows models to learn patterns from missingness

## 📈 Feature Breakdown

### Numeric Features (8):
- `waist_width_mm`: Ski waist width in millimeters
- `price`: Price in Swedish Kronor
- `reapris`: Sale price (if applicable)
- `weight_grams`: Ski weight in grams
- `turn_radius_m`: Turn radius in meters  
- `min_length_cm`: Shortest available length
- `max_length_cm`: Longest available length
- `length_count`: Number of length options

### Text Features (12):
- `title`: Product name
- `tags`: Semicolon-separated tags
- `brand`: Manufacturer name
- `category`: Product category
- `lengths_cm`: Available lengths (original format)
- `k_n`: Gender/target demographic
- `storlek_i_lager`: Stock sizes
- `length_options`: Parsed length array (as string)
- `width_category`: Width classification
- `price_category`: Price classification  
- `skiing_style`: Comma-separated skiing styles
- `unnamed_2`: Additional description field

### Boolean Features (1):
- `twin_tip`: Whether ski has twin-tip design

## 🤖 AI Readiness Features

### 1. Machine Learning Ready
- ✅ Consistent data types
- ✅ No special characters in column names
- ✅ Handled missing values appropriately
- ✅ Categorical variables properly encoded
- ✅ Numeric features in standard units

### 2. Natural Language Processing Ready
- ✅ UTF-8 encoding for international characters
- ✅ Structured text fields (`tags`, `skiing_style`)
- ✅ Clean product titles and descriptions
- ✅ Consistent terminology

### 3. Feature Engineering Ready
- ✅ Multi-level categorical features (narrow to very_wide)
- ✅ Extracted numeric features from text
- ✅ Derived features (min/max lengths)
- ✅ Multi-label classifications (skiing styles)

## 💡 Recommended AI Use Cases

### 1. Product Recommendation
```python
# Features: brand, category, waist_width_mm, price_category, skiing_style
# Target: User preferences/purchase history
```

### 2. Price Prediction
```python
# Features: brand, waist_width_mm, weight_grams, skiing_style, category
# Target: price
```

### 3. Performance Clustering
```python
# Features: waist_width_mm, weight_grams, turn_radius_m, skiing_style
# Method: K-means clustering to group similar skis
```

### 4. Search and Filtering
```python
# Use structured categories for faceted search:
# - width_category for waist width filtering
# - skiing_style for use case filtering  
# - price_category for budget filtering
```

### 5. Natural Language Query Processing
```python
# Use tags and descriptions for semantic search
# skiing_style for intent classification
# Numeric features for specification queries
```

## 🛠 Usage Examples

### Loading the Dataset
```python
import pandas as pd

# Load optimized dataset
df = pd.read_csv('alpingaraget_ai_optimized.csv')

# Basic info
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"Data types:\n{df.dtypes}")
```

### Feature Selection for ML
```python
# Numeric features for regression
numeric_features = [
    'waist_width_mm', 'weight_grams', 'turn_radius_m',
    'min_length_cm', 'max_length_cm', 'length_count'
]

# Categorical features for classification  
categorical_features = [
    'brand', 'category', 'width_category', 
    'price_category', 'skiing_style'
]

# Boolean features
boolean_features = ['twin_tip']
```

### Text Processing
```python
# Tags for feature extraction
df['tag_list'] = df['tags'].str.split(';')

# Skiing style for multi-label classification
df['style_list'] = df['skiing_style'].str.split(',')
```

## 📋 Data Quality Metrics

- **Completeness**: 94.6% (202 missing values out of 3,784 total cells)
- **Consistency**: Standardized formats across all fields
- **Accuracy**: Domain-validated categorical mappings
- **Validity**: All numeric values within expected ranges
- **Uniqueness**: 172 unique products, 26 brands, 15 categories

## 🔧 Maintenance Notes

### Updating the Dataset
1. Add new products to the Excel file
2. Run `optimize_for_ai.py` to regenerate the CSV
3. Verify data quality metrics remain consistent
4. Update documentation if new features are added

### Schema Evolution
- New numeric features should be added to the extraction functions
- New categorical mappings should be documented
- Version control recommended for schema changes

---

**Generated**: AI-optimized dataset for machine learning applications  
**Contact**: For questions about data structure or AI optimization process 