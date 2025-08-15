#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test file for PDF Report Designer Column Exclusion
This file demonstrates that only the first column (SL.No) is excluded from totals
"""

def test_column_exclusion():
    """Test that only the first column (SL.No) is excluded from totals"""
    
    # Simulate field order (as it would appear in the report)
    field_order = [
        "1",           # SL.No (first column - excluded from totals)
        "2",           # partner_id.name (second column - can have totals if numeric)
        "3",           # amount_total (third column - should have totals)
        "4",           # product_qty (fourth column - should have totals)
        "5"            # customer_name (fifth column - should not have totals)
    ]
    
    print("🧪 Testing Column Exclusion from Totals")
    print("=" * 60)
    
    # Simulate the logic from the code
    summary_row = ["TOTAL"]
    
    # Skip first field only (SL.No), include second field onwards
    for field_id in field_order[1:]:  # Start from index 1 (second column)
        field_name = f"field_{field_id}"
        
        # Simulate field types
        if field_id == "2":  # partner_id.name (group_by_field)
            field_type = "many2one"  # This won't have totals
            field_description = "Customer"
        elif field_id == "3":  # amount_total
            field_type = "monetary"
            field_description = "Total Amount"
        elif field_id == "4":  # product_qty
            field_type = "integer"
            field_description = "Product Quantity"
        elif field_id == "5":  # customer_name
            field_type = "char"
            field_description = "Customer Name"
        else:
            field_type = "unknown"
            field_description = "Unknown"
        
        print(f"Column {field_id}: {field_name}")
        print(f"  Type: {field_type}")
        print(f"  Description: {field_description}")
        
        # Check if this field should have totals
        should_calculate_total = False
        
        if field_type in ['monetary', 'integer', 'float']:
            meaningful_keywords = [
                'amount', 'total', 'price', 'cost', 'value', 'quantity', 
                'qty', 'count', 'sum', 'balance', 'credit', 'debit',
                'revenue', 'income', 'expense', 'budget', 'target',
                'commission', 'discount', 'tax', 'fee', 'charge',
                'weight', 'volume', 'area', 'length', 'height',
                'score', 'rating', 'percentage', 'ratio'
            ]
            
            # Check field name and description for meaningful keywords
            for keyword in meaningful_keywords:
                if keyword in field_name.lower() or keyword in field_description.lower():
                    should_calculate_total = True
                    break
        
        if should_calculate_total:
            result = "✅ WILL SUM"
            summary_row.append("150000")  # Example total
        else:
            result = "❌ WON'T SUM"
            summary_row.append("")
        
        print(f"  Result: {result}")
        print()
    
    print("📊 Final Summary Row:")
    print(f"  {summary_row}")
    
    print("\n" + "=" * 60)
    print("✅ Column exclusion test completed!")
    print("Note: Only the first column (SL.No) is excluded from totals")
    print("      Second column onwards can have totals if they are numeric fields")
    return True

def test_report_structure():
    """Test the expected report structure"""
    
    print("\n📋 Expected Report Structure")
    print("=" * 60)
    
    # Simulate report structure
    report_structure = [
        ["--- Customer ABC ---", "", "", "", ""],  # Group header
        ["1", "Customer ABC", "50000", "5", "John Doe"],  # Data row 1
        ["2", "Customer ABC", "70000", "7", "Jane Smith"],  # Data row 2
        ["TOTAL", "", "120000", "12", ""],  # Summary row
        ["", "", "", "", ""],  # Separator
        ["--- Customer XYZ ---", "", "", "", ""],  # Group header
        ["3", "Customer XYZ", "1435500", "15", "Bob Johnson"],  # Data row 1
        ["4", "Customer XYZ", "1617000", "18", "Alice Brown"],  # Data row 2
        ["TOTAL", "", "3046500", "33", ""],  # Summary row
    ]
    
    print("Column Headers: SL.No | Customer | Amount | Quantity | Name")
    print("-" * 60)
    
    for row in report_structure:
        if row[0].startswith("---"):
            print(f"GROUP: {row[0]}")
        elif row[0] == "TOTAL":
            print(f"TOTAL:  {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}")
        elif row[0] == "":
            print("--- Separator ---")
        else:
            print(f"DATA:   {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}")
    
    print("\n" + "=" * 60)
    print("✅ Report structure test completed!")
    print("Note: Second column (Customer) shows empty in TOTAL row")
    print("      Third and fourth columns show calculated totals")
    return True

if __name__ == "__main__":
    test_column_exclusion()
    test_report_structure()
