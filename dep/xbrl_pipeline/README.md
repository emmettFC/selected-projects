# XBRL Ingest: 
## Leveraging the XBRL taxonomy to parse documents from the SEC EDGAR website at scale

![alt text](https://github.com/emmettFC/selected-projects/blob/master/xbrlIngest/assets/logos.png)

### Project Overview: 
In 2015 I was working for the applied analytics group at AlixPartners, a consulting firm based in NYC. For the annual company meeting, employees were offered the chance to compete in a data science competition, which asked participants to respond to one of three promts. Once of these prompts challenegd participants to develop a tool to predict EBITDA, as a component meant to improve the functionality of the Early Warning Model tool, which was used to identify distressed companies / potential clientele for the restructuring arm of the company. I chose to submit a solution to this promt, and formed a team with three of my colleagues to build out the project. Ultimately, we built a tool that leveraged the XBRL (extensible business reporting language) markup syntax in order to scrape and flatten 10-K and 10-Q documents from the SEC's EDGAR site. The idea was that rather than 1) pay for bloomberg or capital iq to get this information, or 2) design specific regular expressions processes to parse the format of individual companies fillings, we could build a generic proceedure that used this standard taxomony to evaluate all filings that were compliant with the markup syntax. Once this information was parsed and stored in a tabular structure -- initially in a SQL db -- it was then enriched via a set of other scraping utilities. In the first iteration of the project, we included:

  * Google trends data for available tickers
  * Yahoo finance price & volume data
  * Macroeconomic indicators 

In order to demonstrate the capability of the tool, we did some basic balance sheet analysis of the most recent submissions from companies in the phamaceutical industry, showing decompositon of asset funding by liability and equity. We presented this solution at the annual firm meeting in Orlando FL, and ultimately won first place. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/xbrlIngest/assets/summary-of-winning-submission.png)

The presentation we gave was video-taped, shakily and with sub-optimal sound quality, but I tracked it down and made a brief edit of it to include here if you'd like to check it out: 

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/BZLs1zgsR7g/0.jpg)](https://www.youtube.com/watch?v=BZLs1zgsR7g)

### Outcome & Ultimate deployment: 
We got requests from a few people at the firm to build out the prototype into a full software product. As a first step we attempted to validate the data against a subset of the Capital IQ data we got though our company subscription. We were able to reconcile the data to within 80%, though this was seen as insufficient for client deployment, and ultimately did not proceed with the project. 

I left the firm not long after this to join a subcontracting team at DARPA in Ballston Virginia. This group was a performer on several ongoing contracts including MEMEX, XDATA and QCR. We were doing some work for FinRA and FinCen, and had built a tool to identify fraudulent activity in a variety of spaces. Ultimately, this project found a second home as a component of this tool, and has since been deployed with agencies in the Federal Government. 

### Code: 
I have included the majority of the code used for this project in this repository. 

## Thanks for reading! 


