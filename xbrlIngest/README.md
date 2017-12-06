# XBRL Ingest: 
## Leveraging the XBRL taxonomy to parse documents from the SEC EDGAR website at scale

![alt text](https://github.com/emmettFC/selected-projects/blob/master/xbrlIngest/assets/logos.png)

### Project Overview: 
In 2015 I was working for the applied analytics group at AlixPartners, a consulting firm based in NYC. For the annual company meeting, employees were offered the chance to compete in a data science competition, which asked participants to respond to one of three promts. Once of these prompts challenegd participants to develop a tool to predict EBITDA, as a component meant to improve the functionality of the Early Warning Model tool, which was used to identify distressed companies / potential clientele for the restructuring arm of the company. I chose to submit a solution to this promt, and formed a team with three of my colleagues to build out the project. Ultimately, we built a tool that leveraged the XBRL (extensible business reporting language) markup syntax in order to scrape and flatten 10-K and 10-Q documents from the SEC's EDGAR site. The idea was that rather than 1) pay for bloomberg or capital iq to get this information, or 2) design specific regular expressions processes to parse the format of individual companies fillings, we could build a generic proceedure that used this standard taxomony to evaluate all filings that were compliant with the markup syntax. Once this information was parsed and stored in a tabular structure -- initially in a SQL db -- it was then enriched via a set of other scraping utilities. In the first iteration of the project, we included:

  * Google trends data for available tickers
  * Yahoo finance price & volume data
  * Macroeconomic indicators 

In order to demonstrate the capability of the tool, we did some basic balance sheet analysis of the most recent submissions from companies in the phamaceutical industry, showing decompositon of asset funding by liability and equity. We presented this solution at the annual firm meeting in Orlando FL, and ultimately won first place. 

  

### Presentation Video
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/BZLs1zgsR7g/0.jpg)](https://www.youtube.com/watch?v=BZLs1zgsR7g)

