// Create DataFolder as a required Text parameter first.

// Query: companies
let
    Source = Csv.Document(File.Contents(DataFolder & "\companies.csv"),[Delimiter=",", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"Company", type text}, {"Base_Monthly_Price", Int64.Type}, {"Private_Office", Int64.Type}, {"Hot_Desk", Int64.Type}, {"Conference_Hours", Int64.Type}, {"Free_Coffee", Int64.Type}, {"Internet_Speed_Mbps", Int64.Type}, {"Flexibility_Score", Int64.Type}}, "en-US")
in
    #"Changed Type"

// Query: customers
let
    Source = Csv.Document(File.Contents(DataFolder & "\customers.csv"),[Delimiter=",", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"Customer_ID", type text}, {"Company", type text}, {"Join_Date", type date}, {"Exit_Date", type date}, {"Monthly_Spend", Int64.Type}, {"Location", type text}, {"Team_Size", Int64.Type}, {"Churned", Int64.Type}}, "en-US")
in
    #"Changed Type"

// Query: survey
let
    Source = Csv.Document(File.Contents(DataFolder & "\survey.csv"),[Delimiter=",", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"Customer_ID", type text}, {"Company", type text}, {"Survey_Date", type date}, {"Satisfaction_Score", Int64.Type}, {"Amenity_Rating", Int64.Type}, {"Price_Rating", Int64.Type}, {"NPS_Like", Int64.Type}}, "en-US")
in
    #"Changed Type"

// Query: usage_monthly
let
    Source = Csv.Document(File.Contents(DataFolder & "\usage_monthly.csv"),[Delimiter=",", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"Customer_ID", type text}, {"Company", type text}, {"Month", type date}, {"Days_Used", Int64.Type}, {"Meeting_Hours", Int64.Type}, {"Support_Tickets", Int64.Type}, {"Monthly_Revenue", Int64.Type}}, "en-US")
in
    #"Changed Type"