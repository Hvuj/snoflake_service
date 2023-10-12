<h2>This service is for propagating click conversions</h2>

**<h3>Requirements:</h3>**

<u><h4>Env Variables:</h4></u>

1. PROJECT_ID - Default should be peppy-castle-368715
2. SECRET_ID - The secret name under secrets manager in PROJECT_ID

<u><h4>Request Variables:</h4></u>

1. customer_id - The customer on the Google Ads platform that the conversions belong to.
2. project_id - The Google Big Query Project ID of the project that we want to query.
3. dataset_id - The Google Big Query Dataset ID of the project that we want to query.
4. table_name - The Google Big Query Table Name of the project that we want to query.

<u><h4>Acceptable Values in query due to Google Ads API limitations:</h4></u>

1. <h5>value</h5> - The conversions Value
2. <h5>date</h5> - The conversions date. For daily usage It must look like this : timestamp(concat(cast(date(date) as string), ' 23:59:59+00:00')) as date.
   For hourly usage - please leave it as is just make sure to add the timezoe i.e. +00:00, +01:00 etc.
      Note! the +00:00 i.e. time zone is only necessary if it is not UTC.
3. <h5>email</h5> - The email address.
4. <h5>phone</h5> - The phone number.
5. <h5>order_id</h5> - The transaction ID of the transaction.
6. <h5>click_id</h5> - The click ID associated with Google Ads platform click conversion.
7. <h5>conversion_action_id - The Conversion ID of the conversion that belongs to the customer id on the Google Ads
   platform.</h5>

<B><h1>Super important!</h1></B>

<p>Uploaded conversions are reflected in reports for the impression date of the original click, not the date of the upload request or the date of the conversion_date_time of the ClickConversion.</p>
<p>It takes up to 3 hours for imported conversion statistics to appear in your Google Ads account for last-click attribution. For other search attribution models, it can take longer than 3 hours.</p>

<h3>Links to Docs</h3>

<a href="https://developers.google.com/google-ads/api/docs/conversions/upload-clicks">Google Ads click conversion
general docs</a>

<a href="https://developers.google.com/google-ads/api/reference/rpc/v12/ClickConversion#custom_variables">Google Ads
click conversion custom variables docs</a>

<a href="https://developers.google.com/google-ads/api/reference/rpc/v12/UserIdentifier">Google Ads
click conversion user identifier docs</a>

<a href="https://developers.google.com/google-ads/api/docs/conversions/upload-identifiers">Google Ads
click conversion user identifier docs example code</a>

<h3>Best practices</h3>
<a href="https://developers.google.com/google-ads/api/docs/best-practices/overview">Google Ads click conversion best
practices</a>
