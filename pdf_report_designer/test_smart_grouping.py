#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test file for PDF Report Designer Smart Grouping Feature
This file demonstrates the intelligent field detection for totals calculation
"""

def test_meaningful_field_detection():
    """Test which fields should have totals calculated"""
    
    # Sample field definitions
    sample_fields = [
        {'name': 'amount_total', 'ttype': 'monetary', 'description': 'Total Amount'},
        {'name': 'product_qty', 'ttype': 'integer', 'description': 'Product Quantity'},
        {'name': 'unit_price', 'ttype': 'float', 'description': 'Unit Price'},
        {'name': 'customer_age', 'ttype': 'integer', 'description': 'Customer Age'},
        {'name': 'order_date', 'ttype': 'date', 'description': 'Order Date'},
        {'name': 'product_name', 'ttype': 'char', 'description': 'Product Name'},
        {'name': 'discount_amount', 'ttype': 'monetary', 'description': 'Discount Amount'},
        {'name': 'employee_id', 'ttype': 'integer', 'description': 'Employee ID'},
        {'name': 'revenue', 'ttype': 'monetary', 'description': 'Total Revenue'},
        {'name': 'tax_rate', 'ttype': 'float', 'description': 'Tax Rate Percentage'}
    ]
    
    # Keywords that indicate meaningful totals
    meaningful_keywords = [
        'amount', 'total', 'price', 'cost', 'value', 'quantity', 
        'qty', 'count', 'sum', 'balance', 'credit', 'debit',
        'revenue', 'income', 'expense', 'budget', 'target',
        'commission', 'discount', 'tax', 'fee', 'charge',
        'weight', 'volume', 'area', 'length', 'height',
        'score', 'rating', 'percentage', 'ratio'
    ]
    
    print("🧠 Testing Smart Field Detection for Totals")
    print("=" * 50)
    
    for field in sample_fields:
        field_name = field['name'].lower()
        field_description = field['description'].lower()
        field_type = field['ttype']
        
        # Check if field should have totals
        should_calculate_total = False
        
        if field_type in ['monetary', 'integer', 'float']:
            # Check field name and description for meaningful keywords
            for keyword in meaningful_keywords:
                if keyword in field_name or keyword in field_description:
                    should_calculate_total = True
                    break
        
        # Determine the result
        if should_calculate_total:
            result = "✅ WILL SUM"
            reason = "Contains meaningful keyword"
        else:
            if field_type not in ['monetary', 'integer', 'float']:
                result = "❌ WON'T SUM"
                reason = f"Not a numeric field (type: {field_type})"
            else:
                result = "❌ WON'T SUM"
                reason = "No meaningful keywords found"
        
        print(f"{field['name']:<20} | {field['description']:<25} | {result:<12} | {reason}")
    
    print("\n" + "=" * 50)
    print("✅ Smart field detection test completed!")
    return True

def test_grouping_with_smart_totals():
    """Test grouping logic with sample data"""
    
    # Sample grouped data
    grouped_data = {
        'Customer A': [
            {'amount_total': 50000, 'product_qty': 5, 'customer_age': 30},
            {'amount_total': 70000, 'product_qty': 7, 'customer_age': 35},
        ],
        'Customer B': [
            {'amount_total': 1435500, 'product_qty': 15, 'customer_age': 28},
            {'amount_total': 1617000, 'product_qty': 18, 'customer_age': 32},
        ]
    }
    
    print("\n📊 Testing Group Totals Calculation")
    print("=" * 50)
    
    for group_name, records in grouped_data.items():
        print(f"\nGroup: {group_name}")
        print("-" * 30)
        
        # Calculate totals for meaningful fields only
        meaningful_fields = ['amount_total', 'product_qty']  # customer_age excluded
        
        for field in meaningful_fields:
            total = sum(record[field] for record in records if record[field])
            print(f"  {field}: {total}")
        
        # Show excluded field
        print(f"  customer_age: [No total - not meaningful]")
    
    print("\n" + "=" * 50)
    print("✅ Group totals test completed!")
    return True

if __name__ == "__main__":
    test_meaningful_field_detection()
    test_grouping_with_smart_totals()
