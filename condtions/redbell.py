from utility.redbell import date_conversion, yesterday_date_conversion


def generate_condition_data(sub_data, comp_data, adj_data, rental_data,sold1,sold2,sold3, list1, list2, list3):
    """
    Generate condition data dictionary based on extracted sections.
    """

    condition_data = {}

    # 1. Conditions from sub_data
    if sub_data:
        inspection_date = sub_data.get("InspectionDate")
        current_list_date=sub_data.get("CurrentListingDate")
        original_list_date=sub_data.get("OriginalListDateListing")
        last_list_date=sub_data.get("LastListDate")
        original_sold_date=sub_data.get("OriginalListDateSold")
        Hoa_fees_include_checkbox_values = sub_data.get("HOAFeesInclude", [])  
        # property_type = sub_data.get("PropertyType")
        # pool = sub_data.get("Pool")
        # year_built = sub_data.get("YearBuilt")

        if inspection_date:
            condition_data["InspectionDate"] = yesterday_date_conversion()
        if current_list_date:
            condition_data["CurrentListingDate"]=date_conversion(current_list_date)  
        if original_list_date:
            condition_data["OriginalListDateListing"]=date_conversion(original_list_date)
        if  last_list_date:
             condition_data["LastListDate"]=date_conversion(last_list_date) 
        if original_sold_date:
             condition_data["OriginalListDateSold"]=date_conversion(original_sold_date)              
    if list1:
        current_list1date=list1.get("CurrentListingDate")
        orginal_list1_date=list1.get("OriginalListDateListing") 
        if current_list1date:
            condition_data["current_list1date"]=date_conversion(current_list1date)
        if orginal_list1_date:
            condition_data["orginal_list1_date"]=date_conversion(orginal_list1_date)    
    if list2:
        current_list2date=list2.get("CurrentListingDate")
        orginal_list2_date=list2.get("OriginalListDateListing") 
        if current_list2date:
            condition_data["current_list2date"]=date_conversion(current_list2date)
        if orginal_list2_date:
            condition_data["orginal_list2_date"]=date_conversion(orginal_list2_date)     
    if list3:        
        current_list3date=list3.get("CurrentListingDate")  
        orginal_list3_date=list3.get("OriginalListDateListing")    
        if current_list3date:
            condition_data["current_list3date"]=date_conversion(current_list3date)        
        if orginal_list3_date:
            condition_data["orginal_list3_date"]=date_conversion(orginal_list3_date) 
    if  sold1:
        current_sold1date= sold1.get("CurrentListingDate")
        orginal_sold1_date= sold1.get("OriginalListDateListing") 
        sale_sold1_date=sold1.get("SaleDate")
        if current_sold1date:
            condition_data["current_sold1date"]=date_conversion(current_sold1date)
        if orginal_sold1_date:
            condition_data["orginal_sold1_date"]=date_conversion(orginal_sold1_date) 
        if sale_sold1_date:
            condition_data['sale_sold1_date']=date_conversion(sale_sold1_date)       
    if  sold2:
        current_sold2date= sold2.get("CurrentListingDate")
        orginal_sold2_date= sold2.get("OriginalListDateListing") 
        sale_sold2_date=sold2.get("SaleDate")
        if current_sold2date:
            condition_data["current_sold2date"]=date_conversion(current_sold2date)
        if orginal_sold2_date:
            condition_data["orginal_sold2_date"]=date_conversion(orginal_sold2_date) 
        if sale_sold2_date:
            condition_data['sale_sold2_date']=date_conversion(sale_sold2_date)        
    if  sold3:        
        current_sold3date= sold3.get("CurrentListingDate")  
        orginal_sold3_date= sold3.get("OriginalListDateListing")   
        sale_sold3_date=sold3.get("SaleDate") 
        if current_sold3date:
            condition_data["current_sold3date"]=date_conversion(current_sold3date)        
        if orginal_sold3_date:
            condition_data["orginal_sold3_date"]=date_conversion(orginal_sold3_date) 
        if sale_sold3_date:
            condition_data['sale_sold3_date']=date_conversion(sale_sold3_date)      
        # if property_type:
        #     condition_data["PropertyType"] = property_type
        # if pool and pool.lower() == "yes":
        #     condition_data["HasPool"] = True
        # else:
        #     condition_data["HasPool"] = False
        # if year_built:
        #     condition_data["YearBuilt"] = year_built

    # # 2. Conditions from comp_data
    # if comp_data:
    #     # Example: Get first comp details (like "List 1")
    #     first_comp_key = next(iter(comp_data), None)
    #     if first_comp_key:
    #         first_comp = comp_data[first_comp_key]
    #         condition = first_comp.get("Condition")
    #         sale_date = first_comp.get("SaleDate")
    #         original_list_date = first_comp.get("OriginalListDate")

    #         if condition:
    #             condition_data["FirstCompCondition"] = condition
    #         if sale_date:
    #             condition_data["FirstCompSaleDate"] = sale_date
    #         if original_list_date:
    #             condition_data["FirstCompOriginalListDate"] = original_list_date

    # # 3. Conditions from adj_data
    # if adj_data:
    #     # Example: suppose there's an AdjustmentFactor field
    #     adj_factor = adj_data.get("AdjustmentFactor")
    #     if adj_factor:
    #         condition_data["AdjustmentFactor"] = adj_factor

    # # 4. Conditions from rental_data
    # if rental_data:
    #     monthly_rent = rental_data.get("MonthlyRent")
    #     if monthly_rent:
    #         condition_data["MonthlyRent"] = monthly_rent

    return condition_data
