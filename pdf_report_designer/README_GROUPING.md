# PDF Report Designer - Grouping Feature

## Overview
This module now supports grouping data in PDF reports based on specified fields. When you set a `group_by_field`, the report will automatically group records and display summary totals for each group.

## How to Use Grouping

### 1. Configure the Report
- Set the **Model** (e.g., Sales Order)
- Set the **Group By Field** (e.g., `partner_id.name` for customer grouping)
- Select the **Fields** you want to display
- Set **Date Filter** if needed

### 2. Report Output Structure
When grouping is enabled, the report will display:

1. **Group Header Row**: Shows the group name (e.g., "Customer ABC")
2. **Data Rows**: All records belonging to that group
3. **Group Summary Row**: Shows "TOTAL" with calculated sums for monetary fields
4. **Separator Row**: Visual separation between groups

### 3. Example Output
```
--- Customer ABC ---
1   50000.0LE    50000.0LE
2   70000.0LE    70000.0LE
TOTAL    120000.0LE    120000.0LE

--- Customer XYZ ---
3   1435500.0LE    1435500.0LE
4   1617000.0LE    1617000.0LE
TOTAL    3052500.0LE    3052500.0LE
```

## Features

### Automatic Grouping
- Records are automatically grouped based on the `group_by_field`
- Each group is clearly separated with headers and totals

### Smart Totals
- **Group Totals**: All numeric fields (monetary, integer, float) are automatically summed for each group
- **Single Group Support**: Totals are shown even when there's only one group
- **Excluded Columns**: Only the first column (SL.No) is never included in totals
- **Included Columns**: Second column onwards can have totals if they are numeric fields
- **Currency Support**: Preserves currency symbols for monetary fields
- **Non-numeric fields show empty values in summary rows

### Field Detection Logic
The system automatically identifies meaningful fields by checking:
1. **Field Names**: Contains keywords like 'amount', 'price', 'quantity', 'total', etc.
2. **Field Descriptions**: Human-readable labels that indicate summable values
3. **Field Types**: Only numeric fields (monetary, integer, float) are considered

**Examples of fields that WILL have totals:**
- `amount_total` → ✅ Will sum
- `product_qty` → ✅ Will sum  
- `unit_price` → ✅ Will sum
- `discount_amount` → ✅ Will sum

**Examples of fields that WON'T have totals:**
- `customer_age` → ❌ Won't sum (not meaningful)
- `order_date` → ❌ Won't sum (date field)
- `product_name` → ❌ Won't sum (text field)
- `employee_id` → ❌ Won't sum (identifier)

### Visual Styling
- Group headers have gray background (`#f0f0f0`)
- Summary rows have blue background (`#e8f4fd`)
- Clear separation between groups

## Technical Details

### Data Structure
The grouping logic:
1. Maps records to groups using `record.mapped(group_by_field)`
2. Processes each group separately
3. Calculates totals for monetary fields
4. Adds special rows for headers, totals, and separators

### Template Changes
The XML template now handles:
- Group header rows (starting with "---")
- Summary rows (with "TOTAL")
- Separator rows (empty rows)
- Regular data rows

## Limitations
- Grouping only works when `group_by_field` is set
- Totals are only calculated for monetary fields
- Complex grouping (multiple fields) is not yet supported

## Future Enhancements
- Support for multiple grouping fields
- Custom aggregation functions (sum, average, count, etc.)
- Group-level subtotals and grand totals
- Custom formatting for group headers and totals
