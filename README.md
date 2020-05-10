# inflationswappricing
Pricing module for zero coupon inflation swaps in Python

A zero coupon inflation swap has one leg tied to a fixed rate and the other to a seasonally adjusted inflation series.  A net payment is made between an investor and a counterparty at maturity with not intermediate payments.  

This is a simple model which demonstrates the parts required and uses linear interpolation for computing discount factors and inflation curve projections.  No responsibility is taken for the accuracy of this model and is for demonstration purposes only.

Datafiles of the form,

curves.csv
tenor,rate,indexname
1y,2.37,UKRPI
2y,2.37,UKRPI
3y,2.4,UKRPI
4y,2.9,UKRPI
5y,3.18,UKRPI
....
1y,0.1,SONIA
2y,0.14,SONIA
3y,0.15,SONIA
4y,0.19,SONIA
5y,0.23,SONIA
....

fixings.csv
date,indexlevel
31/12/18,285.6
31/01/19,283.7
28/02/19,285.2
31/03/19,285.1
30/04/19,288.2
....

seasonality.csv
month,factor,month2
1,0.9924,Jan
2,1.003,Feb
3,1.004,Mar
4,1.003,Apr
....

swaps.csv
securityid,portfolio,effectivedate,maturitydate,notional,fixedrate,ccy,inflationindex,lagmonths,direction,counterparty
101,portfolio1,31/03/19,31/03/25,1000000,3.31,GBP,UKRPI,2,pay,bank1
....

securityid,date,notional,counterparty,fee,paymentdate
1000001, 31/12/2019, 100000,bank1,500,02/01/2020
....
