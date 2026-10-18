# Data dictionary

All source data are simulated. Root CSVs remain unchanged. Prepared exports remove only incomplete usage rows; review flags are separate.

| Table | Grain/key | Fields |
| --- | --- | --- |
| customers | One record per Customer_ID | Company: provider label; Join_Date and nullable Exit_Date: ISO dates; Monthly_Spend: positive amount, currency undocumented; Location: city; Team_Size: positive integer; Churned: supplied 0/1 status |
| companies | One record per Company | Base_Monthly_Price: amount, currency undocumented; Private_Office, Hot_Desk, Free_Coffee: binary amenities; Conference_Hours: allowance, period undocumented; Internet_Speed_Mbps: bandwidth; Flexibility_Score: synthetic score, rubric undocumented |
| usage_monthly | One record per customer/calendar month among complete rows | Customer_ID, Company; Month: source date within month, not consistently month-start; Days_Used: count; Meeting_Hours, Support_Tickets: quantities; Monthly_Revenue: amount, currency undocumented |
| survey | One survey per customer in supplied data; Customer_ID + Survey_Date key | Company, Survey_Date; Satisfaction_Score, Amenity_Rating, Price_Rating: 1-10 scores; NPS_Like: custom score ranging -5 to 6, not standard NPS |

Complete usage/survey IDs match customers; provider labels agree. Usage is on/after join and on/before recorded exit. Blank exits agree with Churned=0 and remain null dates. Post-exit surveys are retained for descriptive analysis, excluded from modelling. Survey dates extend beyond usage coverage.

Join usage to customers many-to-one. Aggregate to the required grain before combining fact tables; otherwise customer counts/revenue can multiply. Customer spend and usage revenue have different grains. Currency is unknown across cities in several countries, so do not add a currency symbol or interpret combined sums as comparable international revenue.

Source_Line in the quarantine export is the 1-based CSV line including header. Reason explains review/exclusion. Review flags have nullable columns for different issue types. Predictions contain only held-out customers. No unified extraction date, switching history, standard NPS, generation policy or feature-availability timeline can be reconstructed from these inputs.
